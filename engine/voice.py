"""Narration: Kokoro TTS (offline, natural voices) + automatic listening QA (Whisper) + caption timing.

Each scene may have `"narration": "One or more sentences."`. prepare() synthesizes every sentence, checks it
(speech recognition must match the script, no clipping, no strange pauses; otherwise it re-generates with a
slightly different speed), stretches the scene so the voice always fits, writes auto captions with
word timings, and returns the voice track that music.py mixes in (with ducking).
"""
import hashlib, json, math, os, re, subprocess, urllib.request
import numpy as np

SR_TTS = 24000
CACHE = os.path.expanduser('~/.cache')
KOKORO_DIR = os.path.join(CACHE, 'kokoro')
ASR_DIR = os.path.join(CACHE, 'asr', 'sherpa-onnx-whisper-base.en')
KOKORO_URL = 'https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/'
ASR_URL = 'https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-base.en.tar.bz2'

_tts = None
_asr = None
NAMES = set()


def ensure_models():
    os.makedirs(KOKORO_DIR, exist_ok=True)
    for f in ('kokoro-v1.0.onnx', 'voices-v1.0.bin'):
        p = os.path.join(KOKORO_DIR, f)
        if not os.path.exists(p) or os.path.getsize(p) < 1_000_000:
            urllib.request.urlretrieve(KOKORO_URL + f, p)
    if not os.path.exists(os.path.join(ASR_DIR, 'base.en-tokens.txt')):
        os.makedirs(os.path.dirname(ASR_DIR), exist_ok=True)
        tb = os.path.join(os.path.dirname(ASR_DIR), 'asr.tar.bz2')
        urllib.request.urlretrieve(ASR_URL, tb)
        subprocess.run(['tar', 'xjf', tb, '-C', os.path.dirname(ASR_DIR)], check=True)
        os.remove(tb)


def tts():
    global _tts
    if _tts is None:
        ensure_models()
        from kokoro_onnx import Kokoro
        _tts = Kokoro(os.path.join(KOKORO_DIR, 'kokoro-v1.0.onnx'), os.path.join(KOKORO_DIR, 'voices-v1.0.bin'))
    return _tts


def asr():
    global _asr
    if _asr is None:
        import sherpa_onnx
        a = ASR_DIR + '/'
        _asr = sherpa_onnx.OfflineRecognizer.from_whisper(
            encoder=a + 'base.en-encoder.int8.onnx', decoder=a + 'base.en-decoder.int8.onnx',
            tokens=a + 'base.en-tokens.txt', num_threads=4)
    return _asr


ONES = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen ' \
       'seventeen eighteen nineteen'.split()
TENS = 'x x twenty thirty forty fifty sixty seventy eighty ninety'.split()


def _num_words(n):
    n = int(n)
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + ('' if n % 10 == 0 else ' ' + ONES[n % 10])
    if n < 1000:
        return ONES[n // 100] + ' hundred' + ('' if n % 100 == 0 else ' ' + _num_words(n % 100))
    return str(n)


def norm_words(t):
    t = t.lower().replace('%', ' percent').replace('&', ' and ')
    t = re.sub(r'(\d+)', lambda m: ' ' + _num_words(m.group(1)) + ' ' if len(m.group(1)) <= 3 else m.group(1), t)
    t = re.sub(r"[^a-z0-9' ]", ' ', t)
    return [w.strip("'") for w in t.split() if w.strip("'")]


def wer(ref, hyp):
    r, h = norm_words(ref), norm_words(hyp)
    d = np.zeros((len(r) + 1, len(h) + 1), int)
    d[:, 0] = range(len(r) + 1)
    d[0, :] = range(len(h) + 1)
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            d[i, j] = min(d[i - 1, j] + 1, d[i, j - 1] + 1, d[i - 1, j - 1] + (r[i - 1] != h[j - 1]))
    return d[-1, -1] / max(1, len(r))


def clean_for_tts(t):
    """Spoken form: drop *highlight* marks, expand symbols the voice may stumble on."""
    t = t.replace('*', '').replace('"', '').replace('…', '...')
    t = re.sub(r'\ba\.m\.', 'A M', t, flags=re.I)
    t = re.sub(r'\bp\.m\.', 'P M', t, flags=re.I)
    t = t.replace('%', ' percent').replace('&', ' and ').replace(' vs ', ' versus ')
    return re.sub(r'\s+', ' ', t).strip()


def sentences(text):
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p for p in parts if p]


def passages(sents, max_chars=220):
    """Group sentences into flowing passages so the voice keeps a natural rhythm across them."""
    out, cur = [], ''
    for st in sents:
        if cur and len(cur) + 1 + len(st) > max_chars:
            out.append(cur)
            cur = st
        else:
            cur = (cur + ' ' + st).strip()
    if cur:
        out.append(cur)
    return out


def _process(x):
    """Trim silence, gentle high-pass, 10 ms fades, level to a fixed RMS. Returns float32 mono @24k."""
    from scipy.signal import butter, sosfilt
    env = np.convolve(np.abs(x), np.ones(240) / 240, 'same')
    thr = 0.02 * (env.max() + 1e-9)
    idx = np.where(env > thr)[0]
    if len(idx):
        a = max(0, idx[0] - int(0.03 * SR_TTS))
        b = min(len(x), idx[-1] + int(0.08 * SR_TTS))
        x = x[a:b]
    x = sosfilt(butter(2, 75, 'high', fs=SR_TTS, output='sos'), x)
    f = int(0.01 * SR_TTS)
    x[:f] *= np.linspace(0, 1, f)
    x[-f:] *= np.linspace(1, 0, f)
    voiced = x[np.abs(x) > 0.01]
    rms = np.sqrt((voiced ** 2).mean()) if len(voiced) else 1.0
    x = x * (0.1 / (rms + 1e-9))             # ~ -20 dBFS speech RMS
    pk = np.max(np.abs(x))
    if pk > 0.89:
        x = x * (0.89 / pk)
    return x.astype(np.float32)


def _longest_pause(x):
    env = np.convolve(np.abs(x), np.ones(480) / 480, 'same')
    q = env < 0.012 * env.max()
    best = cur = 0
    for v in q:
        cur = cur + 1 if v else 0
        best = max(best, cur)
    return best / SR_TTS


def synth_checked(text, voice, speed, cache_dir, log):
    """One sentence -> audio, verified by speech recognition. Retries with small speed changes."""
    spoken = clean_for_tts(text)
    key = hashlib.sha1(f'{voice}|{speed}|{spoken}'.encode()).hexdigest()[:16]
    cp = os.path.join(cache_dir, key + '.npy')
    if os.path.exists(cp):
        mp = cp.replace('.npy', '.json')
        if os.path.exists(mp):
            with open(mp) as f:
                log.append(json.load(f))
        return np.load(cp)
    lang = 'en-gb' if voice.startswith('b') else 'en-us'
    best = None
    for attempt, sp in enumerate((speed, speed * 0.96, speed * 1.04, speed * 0.92)):
        raw, sr = tts().create(spoken, voice=voice, speed=sp, lang=lang)
        x = _process(np.asarray(raw, dtype=np.float32))
        st = asr().create_stream()
        st.accept_waveform(SR_TTS, x)
        asr().decode_stream(st)
        hyp = st.result.text.strip()
        w = wer(spoken, hyp)
        if w > 0.15:   # proper names (Rohan, Arjun...) are often spelled differently by the recognizer
            names = {m.lower() for m in re.findall(r"(?<![.!?]\s)(?<!^)\b([A-Z][a-z]+)", spoken)} | set(NAMES)
            ref2 = ' '.join(x_ for x_ in spoken.split() if re.sub(r'[^a-z]', '', x_.lower()) not in names)
            hyp2 = ' '.join(x_ for x_ in hyp.split() if not any(abs(len(x_) - len(n)) <= 2 and x_.lower()[:2] == n[:2]
                                                               for n in names))
            w = min(w, wer(ref2, hyp2))
        pause = _longest_pause(x)
        dur_per_word = len(x) / SR_TTS / max(1, len(norm_words(spoken)))
        ok = w <= 0.15 and pause < 0.9 and 0.16 < dur_per_word < 0.75
        score = w + max(0, pause - 0.9) + (0 if 0.16 < dur_per_word < 0.75 else 1)
        if best is None or score < best[0]:
            best = (score, x, w, hyp, sp)
        if ok:
            break
    score, x, w, hyp, sp = best
    log.append(dict(text=spoken, heard=hyp, wer=round(w, 3), speed=round(sp, 3), seconds=round(len(x) / SR_TTS, 2),
                    ok=bool(score <= 0.15)))
    np.save(cp, x)
    with open(cp.replace('.npy', '.json'), 'w') as f:
        json.dump(log[-1], f)
    return x


def _word_times(text, dur):
    """Approximate per-word timings inside one sentence (weighted by length, pauses at punctuation)."""
    words = text.split()
    wts = []
    for w in words:
        base = len(re.sub(r'[^A-Za-z0-9]', '', w)) + 2.5
        if re.search(r'[,;:]$', w):
            base += 3
        if re.search(r'[.!?]$', w):
            base += 4
        wts.append(base)
    tot = sum(wts)
    out, t = [], 0.0
    for w, k in zip(words, wts):
        d = dur * k / tot
        out.append([round(t, 3), round(t + d * 0.92, 3), w])
        t += d
    return out


def chunk_words(words, max_words, max_chars):
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        txt = ' '.join(x[2] for x in cur)
        if len(cur) >= max_words or len(txt) >= max_chars or re.search(r'[.!?,;:]$', w[2]):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return chunks


def prepare(spec, out_dir, short=False):
    """Synthesize narration, stretch scenes, add captions. Returns (resolved_spec, voice_track@24k or None, qa)."""
    if not any(sc.get('narration') for sc in spec['scenes']):
        return spec, None, []
    cfg_voice = spec.get('voice', {})
    voice = cfg_voice.get('name', 'af_heart')
    speed = cfg_voice.get('speed', 1.03 if short else 0.98)
    gap = cfg_voice.get('gap', 0.22 if short else 0.32)
    NAMES.update(n.lower() for n in spec.get('voice', {}).get('names', []))
    for txt in [sc.get('narration', '') for sc in spec['scenes']]:
        for n in re.findall(r'\b([A-Z][a-z]{2,})\b', txt if isinstance(txt, str) else ' '.join(txt)):
            if n.lower() not in ('the', 'and', 'but', 'so', 'then', 'ever', 'just', 'your', 'you', 'nothing', 'tired', 'sunday',
                                 'monday', 'after', 'here', 'what', 'when', 'within', 'everyone', 'nobody', 'not', 'because',
                                 'psychologists', 'it', 'in', 'his', 'her', 'one', 'day', 'by', 'across', 'meanwhile'):
                NAMES.add(n.lower())
    cache = os.path.join(out_dir, 'voice_cache')
    os.makedirs(cache, exist_ok=True)
    log = []
    clips = []          # (scene index, offset within scene, audio)
    spec = json.loads(json.dumps(spec))
    for i, sc in enumerate(spec['scenes']):
        nar = sc.get('narration')
        if not nar:
            continue
        lead = sc.get('voice_at', 0.25 if i else 0.15)
        t = lead
        words = []
        for sent in passages(nar if isinstance(nar, list) else sentences(nar)):
            x = synth_checked(sent, voice, speed, cache, log)
            d = len(x) / SR_TTS
            clips.append((i, t, x))
            for a, b, w in _word_times(sent, d):
                words.append([round(t + a, 3), round(t + b, 3), w])
            t += d + gap
        need = t - gap + sc.get('tail', 0.45 if short else 0.6)
        if sc.get('duration', 0) < need:
            sc['duration'] = round(need, 2)
        if sc.get('captions_mode') != 'manual' and sc.get('template') not in ('card', 'end_card'):
            mw, mc = (4, 22) if short else (10, 60)
            caps = []
            for ch in chunk_words(words, mw, mc):
                a, b = ch[0][0], ch[-1][1]
                caps.append([round(a, 2), round(max(b, a + 0.35), 2), ' '.join(w[2] for w in ch)])
            for k in range(len(caps) - 1):            # hold each chunk until the next one starts
                caps[k][1] = round(max(caps[k][1], caps[k + 1][0] - 0.02), 2)
            sc['captions'] = caps
            sc['_words'] = words
    # global track
    t0s, acc = [], 0.0
    for sc in spec['scenes']:
        t0s.append(acc)
        acc += sc['duration']
    total = acc + (0 if short else spec.get('_outro_seconds', 9))
    track = np.zeros(int((total + 1) * SR_TTS), np.float32)
    for i, off, x in clips:
        a = int((t0s[i] + off) * SR_TTS)
        track[a:a + len(x)] += x[:max(0, len(track) - a)]
    with open(os.path.join(out_dir, 'voice_qa.json'), 'w') as f:
        json.dump(log, f, indent=1)
    return spec, track, log
