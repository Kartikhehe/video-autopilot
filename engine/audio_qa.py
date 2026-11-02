"""python3 -m engine.audio_qa out/<id>   -> checks the FINAL mix of video.mp4 and writes audio_qa.json

Checks: loudness (-14 LUFS ±1.5), true peak, clipping, clicks/jumps, voice-over-music clarity
(speech recognition on the finished audio must match the narration), music level under the voice.
Exit 0 = pass, 1 = fail (the playbook re-renders or fixes the story before uploading).
"""
import json, os, re, subprocess, sys
import numpy as np


def _audio(video, sr=16000):
    """Returns (mono mix for analysis, stereo peak per sample) without an ffmpeg downmix that could sum channels."""
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', video, '-ac', '2', '-ar', str(sr), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    st = np.frombuffer(raw, np.float32).reshape(-1, 2)
    return st.mean(1), np.abs(st).max(1)


def loudness(video):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', video, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    i = re.findall(r'I:\s+(-?[\d.]+) LUFS', r)
    tp = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r)
    return float(i[-1]) if i else None, float(tp[-1]) if tp else None


def main(d):
    from . import voice as VO
    video = os.path.join(d, 'video.mp4')
    spec = json.load(open(os.path.join(d, 'story.resolved.json'))) if os.path.exists(os.path.join(d, 'story.resolved.json')) else None
    rep, problems = {}, []
    lufs, tp = loudness(video)
    rep.update(lufs=lufs, true_peak=tp)
    if lufs is None or abs(lufs + 14) > 1.5:
        problems.append(f'loudness {lufs} LUFS (want -14)')
    if tp is not None and tp > -0.5:
        problems.append(f'true peak {tp} dBFS too hot')
    x, peak = _audio(video)
    clip = float(np.mean(peak > 0.995))
    rep['clipped_fraction'] = clip
    if clip > 1e-4:
        problems.append(f'clipping in {clip * 100:.3f}% of samples')
    # clicks: sample-to-sample jumps far above the local level
    dx = np.abs(np.diff(x))
    loc = np.convolve(np.abs(x), np.ones(400) / 400, 'same')[1:] + 1e-3
    clicks = int(np.sum(dx > 12 * loc + 0.25))
    rep['clicks'] = clicks
    if clicks > 3:
        problems.append(f'{clicks} click-like jumps')
    # abrupt level changes (music cutting in/out): 100 ms RMS jumping > 12 dB between neighbours
    blk = 1600
    rms = np.array([np.sqrt(np.mean(x[i:i + blk] ** 2)) + 1e-5 for i in range(0, len(x) - blk, blk)])
    db = 20 * np.log10(rms)
    jumps = int(np.sum(np.abs(np.diff(db)) > 12))
    rep['abrupt_level_jumps'] = jumps
    if spec and any(sc.get('narration') for sc in spec['scenes']):
        vt = np.load(os.path.join(d, 'voice_track.npy')) if os.path.exists(os.path.join(d, 'voice_track.npy')) else None
        if vt is not None:
            from scipy.signal import resample_poly
            v16 = resample_poly(vt.astype(np.float64), 2, 3)[:len(x)]
            speech = np.zeros(len(x), bool)
            env = np.convolve(np.abs(v16), np.ones(800) / 800, 'same')
            speech[:len(env)] = env > 0.01
            mus = x[~speech]
            sp = x[speech]
            rep['level_speech_dbfs'] = float(round(20 * np.log10(np.sqrt(np.mean(sp ** 2)) + 1e-9), 1)) if len(sp) else None
            rep['level_gaps_dbfs'] = float(round(20 * np.log10(np.sqrt(np.mean(mus ** 2)) + 1e-9), 1)) if len(mus) else None
        # recognise the finished mix in 25 s windows and compare with the narration
        ref = ' '.join((sc['narration'] if isinstance(sc['narration'], str) else ' '.join(sc['narration']))
                       for sc in spec['scenes'] if sc.get('narration'))
        hyp = []
        for a in range(0, len(x), 16000 * 25):
            st = VO.asr().create_stream()
            st.accept_waveform(16000, x[a:a + 16000 * 25].copy())
            VO.asr().decode_stream(st)
            hyp.append(st.result.text)
        heard = ' '.join(hyp)
        w = VO.wer(VO.clean_for_tts(ref), heard)
        rep.update(final_mix_wer=float(round(w, 3)), heard=heard[:600])
        if w > 0.18:
            problems.append(f'voice not clear over the music (word error {w:.0%})')
    rep['problems'] = problems
    rep['pass'] = not problems
    with open(os.path.join(d, 'audio_qa.json'), 'w') as f:
        json.dump(rep, f, indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k != 'heard'}, indent=1))
    return 0 if not problems else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
