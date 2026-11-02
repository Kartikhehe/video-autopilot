"""Narration: Kokoro TTS (offline) per sentence, cached, plus the episode timeline built from it.

Model files: /opt/tts/kokoro-v1.0.onnx + voices-v1.0.bin (see explainer/README.md to download).
"""
import hashlib
import json
import os
import re

import numpy as np

SR = 24000
MODEL_DIR = os.environ.get('KOKORO_DIR', '/opt/tts')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE = os.path.join(ROOT, 'out', '_tts_cache')

LEAD_IN = 0.45          # silence before the first sentence of a shot
GAP = 0.32              # between sentences
GAP_DOTS = 0.75         # after a sentence that ends with "..."
PAD = 0.55              # default tail after the last sentence

_k = None


def kokoro():
    global _k
    if _k is None:
        from kokoro_onnx import Kokoro
        _k = Kokoro(os.path.join(MODEL_DIR, 'kokoro-v1.0.onnx'), os.path.join(MODEL_DIR, 'voices-v1.0.bin'))
    return _k


def tts_text(s, ep):
    for a, b in ep.get('tts_fix', {}).items():
        s = re.sub(r'(?<![A-Za-z])' + re.escape(a) + r'(?![A-Za-z])', b, s)
    return s


def trim(x, thr=0.006):
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0:
        return x[:0]
    a, b = max(0, idx[0] - int(0.02 * SR)), min(len(x), idx[-1] + int(0.06 * SR))
    return x[a:b]


def synth(sentence, ep):
    voice, speed = ep.get('voice', 'af_heart'), ep.get('speed', 1.0)
    text = tts_text(sentence, ep)
    key = hashlib.sha1(json.dumps([text, voice, speed, ep.get('ipa_fix', {})]).encode()).hexdigest()[:16]
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, key + '.npy')
    if os.path.exists(path):
        return np.load(path)
    k = kokoro()
    ph = k.tokenizer.phonemize(text, 'en-us')
    for a, b in ep.get('ipa_fix', {}).items():
        ph = ph.replace(a, b)
    audio, sr = k.create(ph, voice=voice, speed=speed, is_phonemes=True)
    assert sr == SR
    audio = trim(np.asarray(audio, dtype=np.float32))
    np.save(path, audio)
    return audio


def build(ep):
    """Returns (shots, voice_track). Each shot gets start, dur, beats (sentence starts, local s), sents."""
    shots, clips = [], []
    t = 0.0
    for sh in ep['shots']:
        sh = dict(sh)
        sh.setdefault('p', {})
        beats, ends = [], []
        lt = LEAD_IN if sh['say'] else 0.0
        for s in sh['say']:
            a = synth(s, ep)
            beats.append(lt)
            clips.append((t + lt, a))
            lt += len(a) / SR
            ends.append(lt)
            lt += GAP_DOTS if s.rstrip().endswith('...') else GAP
        if sh['say']:
            lt = ends[-1] + sh.get('pad', PAD)
        dur = max(lt, sh.get('hold', 0.0))
        sh.update(start=t, dur=dur, beats=beats, ends=ends)
        shots.append(sh)
        t += dur
    total = t
    track = np.zeros(int((total + 1) * SR), dtype=np.float32)
    for t0, a in clips:
        i = int(t0 * SR)
        track[i:i + len(a)] += a
    return shots, track, total


def srt(shots, path):
    """Subtitles from the sentence timings (each sentence = one cue, long ones split)."""
    def ts(x):
        h, m = int(x // 3600), int(x % 3600 // 60)
        return f'{h:02d}:{m:02d}:{x % 60:06.3f}'.replace('.', ',')
    n, out = 1, []
    for sh in shots:
        for s, b, e in zip(sh['say'], sh['beats'], sh['ends']):
            words = s.split()
            parts = [s] if len(words) <= 14 else [' '.join(words[:len(words) // 2]), ' '.join(words[len(words) // 2:])]
            span = (e - b) / len(parts)
            for k, ptxt in enumerate(parts):
                a0 = sh['start'] + b + k * span
                out.append(f'{n}\n{ts(a0)} --> {ts(a0 + span)}\n{ptxt}\n')
                n += 1
    with open(path, 'w') as f:
        f.write('\n'.join(out))
