"""Sound: synthesized music score (mood per shot, bar-aligned), procedural SFX, voice polish, ducking, loudness."""
import math
import os
import subprocess

import numpy as np
from scipy import signal

from . import voice

SR = 48000
BPM = 96
BEAT = 60 / BPM
BAR = 4 * BEAT
RNG = np.random.default_rng(3)


def mf(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, fc, order=2):
    sos = signal.butter(order, min(fc, SR * 0.45) / (SR / 2), 'low', output='sos')
    return signal.sosfilt(sos, x)


def hp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), 'high')
    return signal.lfilter(b, a, x)


def bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), min(hi, SR * 0.45) / (SR / 2)], 'band')
    return signal.lfilter(b, a, x)


def env(n, a=0.01, r=0.2, hold=None):
    e = np.ones(n)
    na = max(1, int(a * SR))
    e[:na] = np.linspace(0, 1, na)
    nr = max(1, int(r * SR))
    if nr < n:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def add(buf, t, sig, gain=1.0, pan=0.0):
    i = int(t * SR)
    if sig.ndim == 1:
        l, r = math.cos((pan + 1) * math.pi / 4) * 1.414, math.sin((pan + 1) * math.pi / 4) * 1.414
        sig = np.stack([sig * l, sig * r], 1)
    if i < 0:
        sig = sig[-i:]
        i = 0
    j = min(len(buf), i + len(sig))
    if j > i:
        buf[i:j] += sig[:j - i] * gain


# ------------------------------------------------------------------ instruments
def pad(notes, dur, bright=2200, wob=0.0):
    n = int((dur + 1.2) * SR)
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    for m in notes:
        for ch, det in ((0, -0.06), (1, 0.06)):
            f0 = mf(m + det) * (1 + wob * 0.006 * np.sin(2 * math.pi * 0.5 * t))
            ph = 2 * math.pi * np.cumsum(f0) / SR
            s = np.zeros(n)
            for k in range(1, 7):
                if f0[0] * k > bright * 1.8:
                    break
                s += np.sin(ph * k + RNG.random() * 6) / k ** 1.3
            out[:, ch] += s
    e = env(n, 0.5, 1.4)
    out *= e[:, None] / max(1, len(notes))
    for ch in range(2):
        out[:, ch] = lp(out[:, ch], bright)
    return out


def pluck(m, dur=0.9, bright=1.0, decay=5.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = mf(m)
    s = np.sin(2 * math.pi * f * t) + 0.35 * bright * np.sin(2 * math.pi * 2 * f * t) * np.exp(-t * 9) \
        + 0.15 * bright * np.sin(2 * math.pi * 3.01 * f * t) * np.exp(-t * 14)
    return s * np.exp(-t * decay) * env(n, 0.003, 0.05)


def bell(m, dur=1.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = mf(m)
    mod = np.sin(2 * math.pi * f * 3.5 * t) * 2.0 * np.exp(-t * 3)
    return np.sin(2 * math.pi * f * t + mod) * np.exp(-t * 2.6) * env(n, 0.002, 0.1)


def piano(m, dur=1.6, vel=0.7):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = mf(m)
    s = np.zeros(n)
    for k in range(1, 7):
        s += np.sin(2 * math.pi * f * k * t * (1 + 0.0004 * k * k)) / k ** 1.5 * np.exp(-t * (1.5 + k * 0.9))
    return s * vel * env(n, 0.004, 0.2)


def bass(m, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * math.pi * mf(m) * t) + 0.25 * np.sin(2 * math.pi * mf(m) * 2 * t)
    return np.tanh(1.6 * s) * env(n, 0.01, 0.12) * np.exp(-t * 1.2)


def kick(g=1.0):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 28)
    return np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * g


def snare():
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    return (bp(RNG.normal(0, 1, n), 900, 6000) * 0.7 + 0.3 * np.sin(2 * math.pi * 190 * t)) * np.exp(-t * 18)


def hat():
    n = int(0.05 * SR)
    return hp(RNG.normal(0, 1, n), 7000) * np.exp(-np.arange(n) / SR * 80)


PROG = {
    'bright': [[0, 4, 7], [7, 11, 14], [9, 12, 16], [5, 9, 12]],
    'wonder': [[0, 4, 7, 11], [5, 9, 12, 16], [4, 7, 11, 14], [7, 11, 14, 16]],
    'weird': [[0, 3, 7], [-2, 2, 5], [5, 8, 12], [7, 11, 14]],
    'dark': [[0, 3, 7], [-2, 2, 5], [3, 7, 10], [-5, -2, 2]],
}
FAM = dict(bright='bright', groove='bright', hit='bright', warm='bright', wonder='wonder', weird='weird', dark='dark')


def render_music(moods_per_bar, nbars, root):
    total = nbars * BAR + 3
    buf = np.zeros((int(total * SR), 2))
    for bi in range(nbars):
        mood = moods_per_bar[bi]
        fam = FAM.get(mood, 'bright')
        ch = PROG[fam][bi % 4]
        t0 = bi * BAR
        base = root + 12
        bright = dict(bright=2600, groove=3000, hit=3200, warm=1800, wonder=2400, weird=1700, dark=900).get(mood, 2200)
        add(buf, t0, pad([base + n for n in ch] + [base + ch[0] - 12], BAR, bright, wob=1.0 if mood == 'weird' else 0.0),
            dict(dark=0.55, warm=0.5, wonder=0.55).get(mood, 0.45))
        # bass
        if mood in ('groove', 'hit', 'bright'):
            for k, (bt, ln) in enumerate([(0, 0.9), (1.5, 0.45), (2, 0.9), (3.5, 0.45)]):
                add(buf, t0 + bt * BEAT, bass(root - 12 + ch[0], ln * BEAT * 1.6), 0.32)
        elif mood in ('wonder', 'warm'):
            add(buf, t0, bass(root - 12 + ch[0], BAR), 0.25)
        elif mood == 'weird':
            for bt in (0, 1.5, 2.5):
                add(buf, t0 + bt * BEAT, bass(root - 12 + ch[0], BEAT), 0.28)
        elif mood == 'dark':
            add(buf, t0, bass(root - 24 + ch[0] + 12, BAR) * 0.9, 0.35)
        # melodic layer
        if mood in ('bright', 'groove', 'hit'):
            pat = [0, 1, 2, 1, 3, 2, 1, 2]
            notes = [base + 12 + n for n in ch] + [base + 24 + ch[0]]
            for k in range(8):
                add(buf, t0 + k * BEAT / 2, pluck(notes[pat[k] % len(notes)], 0.6), 0.14, pan=0.35 * (1 if k % 2 else -1))
        elif mood == 'wonder':
            for k in range(8):
                if k % 2 == 0 or RNG.random() < 0.4:
                    m = base + 24 + ch[(k * 3) % len(ch)]
                    add(buf, t0 + k * BEAT / 2, bell(m, 1.4), 0.06, pan=RNG.uniform(-0.6, 0.6))
        elif mood == 'weird':
            for k in range(4):
                m = base + 12 + ch[(k * 2) % len(ch)]
                n = int(BEAT * 1.4 * SR)
                t = np.arange(n) / SR
                f = mf(m) * (1 + 0.03 * np.sin(2 * math.pi * 5.5 * t))
                s = np.sin(2 * math.pi * np.cumsum(f) / SR) * env(n, 0.05, 0.3)
                add(buf, t0 + k * BEAT, s, 0.07, pan=0.5 * math.sin(k))
        elif mood == 'warm':
            for k, m in enumerate([ch[0], ch[1], ch[2], ch[1]]):
                add(buf, t0 + k * BEAT, piano(base + 12 + m, 1.8), 0.16, pan=-0.2 + 0.13 * k)
        elif mood == 'dark':
            n = int(BAR * SR)
            t = np.arange(n) / SR
            s = np.sin(2 * math.pi * mf(base + 24 + ch[2]) * t) * env(n, 1.0, 1.0) * (0.5 + 0.5 * np.sin(2 * math.pi * 0.25 * t))
            add(buf, t0, s, 0.03)
        # drums
        if mood in ('groove', 'hit'):
            for k in range(4):
                if k in (0, 2):
                    add(buf, t0 + k * BEAT, kick(), 0.5)
                else:
                    add(buf, t0 + k * BEAT, snare(), 0.13)
            for k in range(8):
                add(buf, t0 + k * BEAT / 2, hat(), 0.06 if k % 2 else 0.035, pan=0.3)
        elif mood == 'bright':
            for k in range(4):
                add(buf, t0 + k * BEAT, kick(0.8) if k in (0, 2) else hat() * 2, 0.32 if k in (0, 2) else 0.05)
        elif mood == 'weird':
            add(buf, t0, kick(0.7), 0.35)
            add(buf, t0 + 2.5 * BEAT, kick(0.6), 0.3)
            for k in range(8):
                add(buf, t0 + k * BEAT / 2 + 0.03 * (k % 2), hat(), 0.03, pan=-0.4)
        elif mood == 'dark':
            add(buf, t0, kick(0.9), 0.4)
            add(buf, t0 + 0.32, kick(0.7), 0.3)
            add(buf, t0 + 2 * BEAT, kick(0.9), 0.4)
            add(buf, t0 + 2 * BEAT + 0.32, kick(0.7), 0.3)
    return buf


# ------------------------------------------------------------------ sfx
def noise(n):
    return RNG.normal(0, 1, n)


def sweep_noise(dur, f0, f1, a=0.05, r=0.3):
    n = int(dur * SR)
    x = noise(n)
    out = np.zeros(n)
    steps = 24
    for k in range(steps):
        i0, i1 = n * k // steps, n * (k + 1) // steps
        fc = f0 * (f1 / f0) ** (k / steps)
        seg = bp(x[max(0, i0 - 2000):i1], fc * 0.6, fc * 1.6)
        out[i0:i1] = seg[-(i1 - i0):]
    return out * env(n, a, r) * np.hanning(n) ** 0.3


def tone(dur, f0, f1=None, decay=8, harm=0.3):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 if f1 is None else f0 * (f1 / f0) ** (t / dur)
    ph = 2 * math.pi * np.cumsum(np.full(n, f) if np.isscalar(f) else f) / SR
    return (np.sin(ph) + harm * np.sin(2 * ph)) * np.exp(-t * decay) * env(n, 0.003, 0.03)


def make_sfx(name):
    if name == 'whoosh':
        return sweep_noise(0.55, 400, 3500, 0.2, 0.3) * 0.9
    if name == 'whoosh_dn':
        return sweep_noise(0.6, 3000, 300, 0.05, 0.4) * 0.9
    if name == 'riser':
        return sweep_noise(1.6, 300, 6000, 1.4, 0.1) * 0.8
    if name == 'pop':
        return tone(0.12, 900, 380, 30, 0.2) * 0.8
    if name == 'pop_hi':
        return tone(0.1, 1400, 700, 35, 0.2) * 0.6
    if name == 'ding':
        a, b2 = bell(91, 1.4), bell(98, 1.4)
        return (a + 0.5 * b2) * 0.3
    if name == 'chime':
        out = np.zeros(int(1.8 * SR))
        for k, m in enumerate([86, 90, 93, 98]):
            s = bell(m, 1.2)
            i = int(k * 0.08 * SR)
            out[i:i + len(s)] += s[:len(out) - i] * 0.3
        return out
    if name == 'sparkle':
        out = np.zeros(int(0.9 * SR))
        for k in range(9):
            s = tone(0.3, RNG.uniform(2500, 6000), None, 18, 0.0) * 0.25
            i = int(RNG.uniform(0, 0.55) * SR)
            out[i:i + len(s)] += s
        return out
    if name == 'gulp':
        out = np.zeros(int(0.5 * SR))
        for k in range(2):
            s = tone(0.14, 260, 140, 18, 0.4) * 0.8 + lp(noise(int(0.14 * SR)), 600) * 0.2 * np.exp(-np.arange(int(0.14 * SR)) / SR * 20)
            i = int(k * 0.22 * SR)
            out[i:i + len(s)] += s
        return out
    if name == 'tick':
        n = int(0.03 * SR)
        return hp(noise(n), 3000) * np.exp(-np.arange(n) / SR * 300) * 0.5 + tone(0.03, 2400, None, 120, 0)[:n] * 0.3
    if name == 'impact':
        n = int(1.6 * SR)
        t = np.arange(n) / SR
        k = np.sin(2 * math.pi * np.cumsum(38 + 90 * np.exp(-t * 12)) / SR) * np.exp(-t * 3)
        return k + lp(noise(n), 1800) * np.exp(-t * 6) * 0.5
    if name == 'stamp':
        n = int(0.35 * SR)
        t = np.arange(n) / SR
        return np.sin(2 * math.pi * 90 * t) * np.exp(-t * 22) + lp(noise(n), 2500) * np.exp(-t * 35) * 0.6
    if name == 'heartbeat':
        out = np.zeros(int(0.7 * SR))
        for k, g in ((0, 1.0), (0.24, 0.7)):
            n = int(0.18 * SR)
            t = np.arange(n) / SR
            s = np.sin(2 * math.pi * 55 * t) * np.exp(-t * 25) * g
            i = int(k * SR)
            out[i:i + n] += s
        return lp(out, 300) * 1.6
    if name == 'squeak':
        n = int(0.16 * SR)
        t = np.arange(n) / SR
        f = 2100 + 500 * t / 0.16 + 120 * np.sin(2 * math.pi * 30 * t)
        return np.sin(2 * math.pi * np.cumsum(f) / SR) * env(n, 0.01, 0.05) * 0.35
    if name == 'bubble':
        return tone(0.09, 300, 1000, 20, 0) * 0.6
    if name == 'boing':
        n = int(0.6 * SR)
        t = np.arange(n) / SR
        f = 180 * (1 + 0.5 * np.sin(2 * math.pi * 9 * t) * np.exp(-t * 4))
        return np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-t * 5) * 0.7
    if name == 'click':
        return tone(0.04, 1800, 900, 80, 0) * 0.7
    if name == 'bell':
        return (bell(93, 1.5) + bell(100, 1.5) * 0.6) * 0.3
    if name == 'beep':
        return tone(0.12, 1000, None, 4, 0) * env(int(0.12 * SR), 0.005, 0.03) * 0.25
    if name == 'poof':
        n = int(0.6 * SR)
        return lp(noise(n), 900) * np.exp(-np.arange(n) / SR * 7) * env(n, 0.02, 0.2) * 0.8
    if name == 'crunch':
        out = np.zeros(int(0.3 * SR))
        for k in range(4):
            n = int(0.03 * SR)
            i = int(k * 0.07 * SR)
            out[i:i + n] += bp(noise(n), 1500, 5000) * np.exp(-np.arange(n) / SR * 120)
        return out * 0.6
    if name == 'sniff':
        n = int(0.12 * SR)
        return bp(noise(n), 2000, 7000) * env(n, 0.02, 0.06) * 0.25
    if name == 'crowd':
        n = int(6.0 * SR)
        t = np.arange(n) / SR
        x = np.zeros(n)
        for k in range(10):
            am = 0.5 + 0.5 * np.sin(2 * math.pi * RNG.uniform(0.3, 1.2) * t + RNG.random() * 6)
            x += bp(noise(n), RNG.uniform(300, 600), RNG.uniform(1200, 2500)) * am
        return x * env(n, 0.6, 1.0) * 0.12
    if name == 'wobble':
        n = int(1.2 * SR)
        t = np.arange(n) / SR
        f = 300 * (1 + 0.4 * np.sin(2 * math.pi * 3 * t)) * (1 - 0.4 * t / 1.2)
        return np.sin(2 * math.pi * np.cumsum(f) / SR) * env(n, 0.05, 0.4) * 0.35
    raise KeyError(name)


_cache = {}


def sfx(name):
    if name not in _cache:
        s = make_sfx(name)
        m = np.max(np.abs(s)) or 1
        _cache[name] = s / m
    return _cache[name]


def cues(sh):
    """SFX cue list (local time, name, gain) per shot, matching the animation timings in scenes_*.py."""
    sc, b, d, p = sh['scene'], sh['beats'], sh['dur'], sh.get('p', {})

    def B(i, dflt=0.0):
        return b[i] if i < len(b) else dflt
    c = []
    if sc == 'holi':
        c += [(0, 'crowd', 0.5)] + [(t, 'poof', 0.35) for t in (0.2, 0.9, 1.7, 2.6, 3.3, 4.2, 5.0) if t < d]
        if p.get('glass'):
            c += [(2.2, 'whoosh', 0.3), (3.5, 'pop', 0.3)]
    elif sc == 'glass':
        c += [(B(0) + 0.3, 'pop', 0.5), (B(1), 'sparkle', 0.5), (B(2), 'chime', 0.4), (B(2) + 0.1, 'whoosh', 0.3)]
    elif sc == 'shop':
        c += [(0.5, 'pop', 0.5), (1.9, 'stamp', 0.6), (1.95, 'ding', 0.3)]
    elif sc == 'party_clock':
        c += [(B(1) + 0.35, 'gulp', 0.6), (B(1) + 2.4, 'gulp', 0.6), (B(2), 'wobble', 0.6)]
        c += [(B(2) + k * 0.11, 'tick', 0.25) for k in range(20)]
    elif sc == 'brain_q':
        c += [(0.3 + i * 0.25, 'pop_hi', 0.3) for i in range(5)] + [(B(1) + 0.7, 'boing', 0.5), (B(1) + 0.75, 'pop', 0.5)]
    elif sc == 'title':
        c += [(0.0, 'impact', 0.8), (0.35, 'pop', 0.5), (0.7, 'pop', 0.5), (0.5, 'sparkle', 0.4)]
    elif sc == 'chapter':
        c += [(0.0, 'whoosh', 0.5), (0.15, 'pop', 0.5), (0.45, 'ding', 0.4)]
    elif sc == 'plant':
        if p.get('focus') == 'flowers':
            c += [(B(1) + 0.3, 'pop', 0.4), (B(1) + 0.9, 'pop', 0.4), (B(2) + 0.2, 'whoosh', 0.3), (B(2) + 2.6, 'stamp', 0.6)]
        else:
            c += [(B(0) + 0.3, 'sparkle', 0.4), (B(1), 'whoosh', 0.3), (B(1) + 2.4, 'stamp', 0.6)]
    elif sc == 'scroll':
        c += [(0.2, 'whoosh', 0.4)] + [(B(1) + 1.6 + i * 0.25, 'pop_hi', 0.35) for i in range(5)] + [(B(1) + 3.6, 'chime', 0.35)]
    elif sc == 'commission':
        c += [(B(1) + k * 0.12, 'tick', 0.22) for k in range(25)] + [(B(1) + 3.2, 'stamp', 0.7), (B(2), 'whoosh_dn', 0.4),
                                                                      (B(2) + 0.8, 'boing', 0.3)]
    elif sc == 'people_grid':
        c += [(0.25, 'sparkle', 0.4), (0.6, 'pop', 0.5)]
    elif sc == 'body':
        if p.get('stage') == 'compare':
            c += [(0.6, 'whoosh', 0.5), (2.3, 'ding', 0.3), (B(1), 'gulp', 0.5), (B(1) + 0.5, 'bubble', 0.3)]
        else:
            c += [(0.6, 'bubble', 0.3), (1.0, 'bubble', 0.25), (1.6, 'bubble', 0.3), (B(1) + 0.6, 'ding', 0.35)]
    elif sc == 'liver':
        c += [(B(0) + 1.8, 'pop', 0.4), (B(1), 'pop', 0.4), (B(1) + 1.5, 'sparkle', 0.5)]
    elif sc == 'timeline':
        c += [(0.4, 'pop', 0.4), (B(1) + 1.2, 'ding', 0.3), (B(2) + 0.4, 'ding', 0.3)]
    elif sc == 'second_glass':
        c += [(B(1) + 0.3, 'pop', 0.4), (B(2), 'gulp', 0.6), (B(3) - 0.6, 'riser', 0.45), (B(3) + 0.9, 'impact', 0.5)]
    elif sc == 'neurons':
        c += [(t, 'pop_hi', 0.15) for t in np.arange(0.5, d, 0.9)]
    elif sc == 'lab':
        c += [(1.0, 'bubble', 0.3), (1.3, 'bubble', 0.3), (1.8, 'sparkle', 0.4), (B(1) + 0.6, 'chime', 0.45), (B(2) + 0.1, 'pop', 0.5)]
    elif sc == 'synapse':
        if not p.get('flood'):
            c += [(B(1) + 1.6, 'whoosh', 0.25), (B(2) + 0.9, 'click', 0.4), (B(2) + 1.4, 'ding', 0.35)]
        else:
            c += [(0.6, 'pop', 0.3), (B(1), 'whoosh', 0.4), (B(1) + 0.6, 'pop', 0.3), (B(2) + 0.3, 'whoosh', 0.4),
                  (B(2) + 0.8, 'stamp', 0.6)]
    elif sc == 'brain_map':
        reg = p.get('region')
        t0 = B(1, 1.0) if reg in ('hippo', 'stem') else 0.4
        c += [(t0, 'sparkle', 0.35), (t0 + 0.3, 'pop', 0.3)]
        if reg == 'hippo':
            c += [(B(2) + 0.6, 'whoosh_dn', 0.4)]
        if reg == 'cereb':
            c += [(1.2, 'wobble', 0.35)]
        if reg == 'amyg':
            c += [(B(1, 4), 'heartbeat', 0.6), (B(1, 4) + 0.8, 'heartbeat', 0.6), (B(1, 4) + 1.5, 'heartbeat', 0.6)]
        if reg == 'stem':
            c += [(B(2, 4) + 0.3, 'ding', 0.35)]
    elif sc == 'mouse':
        c += [(0.6, 'squeak', 0.5), (0.5, 'pop', 0.3)] + [(B(1) + 0.6 + k * 0.35, 'sniff', 0.5) for k in range(5)]
        c += [(B(1) + 2.6 + k * 0.4, 'crunch', 0.4) for k in range(int(max(0, B(2) - B(1) - 2.6) / 0.4))]
        c += [(B(2) + 0.6, 'pop', 0.5), (B(2) + 1.0, 'squeak', 0.4)]
    elif sc == 'panic':
        t = 0.3
        while t < B(2, d) - 0.2:
            c.append((t, 'heartbeat', 0.55))
            rate = 1.0 + 1.8 * min(1, max(0, (t - B(1)) / 2))
            t += 1.0 / rate
        c += [(B(1) + 1.6, 'pop', 0.4), (B(1) + 3.0, 'pop', 0.4), (B(1) + 3.9, 'pop', 0.4), (B(2) - 0.2, 'whoosh', 0.4)]
        c += [(t, 'beep', 0.4) for t in np.arange(B(2) + 0.4, d + 0.4, 0.75)]
    elif sc == 'loop':
        c += [(0.4 + i * 0.09, 'tick', 0.2) for i in range(28)] + [(B(1), 'whoosh', 0.3), (B(1) + 2.2, 'stamp', 0.5),
                                                                   (B(2), 'pop', 0.4)]
    elif sc == 'teen':
        c += [(t, 'tick', 0.3) for t in np.arange(0.8, d, 0.6)] + [(B(1, 3), 'pop', 0.3)]
    elif sc == 'bars':
        c += [(0.6, 'whoosh', 0.3), (3.2, 'whoosh', 0.35), (B(1) + 0.4, 'whoosh', 0.45), (B(1) + 1.6, 'pop', 0.4),
              (B(2) + 0.4, 'stamp', 0.6)]
    elif sc == 'balance':
        c += [(0.3, 'pop', 0.5), (B(1) - 1.6, 'boing', 0.5), (B(1) - 1.4, 'pop', 0.4), (B(1), 'whoosh', 0.35)]
        c += [(B(1) + 2.0 + i * 0.12, 'tick', 0.25) for i in range(12)] + [(B(1) + 3.6, 'stamp', 0.5)]
    elif sc == 'hidden':
        c += [(0.3, 'pop', 0.4), (0.5, 'wobble', 0.4), (B(1), 'whoosh', 0.3), (B(1) + 1.5, 'pop', 0.4)]
        c += [(t, 'tick', 0.18) for t in np.arange(B(1), d, 0.5)]
    elif sc == 'bliss':
        c += [(B(1), 'whoosh_dn', 0.3), (B(2), 'chime', 0.45), (B(2) + 0.3, 'sparkle', 0.4), (B(3) - 0.2, 'whoosh', 0.3),
              (B(3) + 0.4, 'pop', 0.4), (B(3) + 0.8, 'whoosh', 0.4), (B(3) + 0.9, 'boing', 0.3)]
    elif sc == 'end_card':
        c += [(0.4, 'chime', 0.45)]
    elif sc == 'outro':
        c += [(B(0, 0.5) + 1.6, 'pop', 0.5), (B(0, 0.5) + 2.65, 'click', 0.6), (B(0, 0.5) + 2.9, 'bell', 0.5)]
    elif sc == 'cave':
        c += [(0.3, 'crowd', 0.15)] + [(B(1) + 0.1 + i * 0.6, 'pop', 0.35) for i in range(3)] + [(B(1) + 2.6, 'ding', 0.3)]
    elif sc == 'pocket':
        c += [(0.3, 'whoosh', 0.3), (0.6, 'sparkle', 0.4)] + [(B(1) + 0.1 + i * 0.6, 'pop', 0.35) for i in range(3)]
    elif sc == 'flat_life':
        c += [(B(1), 'tick', 0.2), (B(2) + 0.3, 'whoosh_dn', 0.4), (B(2) + 1.5, 'stamp', 0.4)]
    elif sc == 'dopamine':
        c += [(0.8, 'pop', 0.45), (1.0, 'sparkle', 0.4), (B(1) + 0.2, 'pop', 0.4), (B(2) + 0.2, 'whoosh', 0.35), (B(2) + 0.6, 'boing', 0.35)]
    elif sc == 'rats_sugar':
        if p.get('mode') == 'low':
            c += [(0.6, 'squeak', 0.4), (1.5, 'sparkle', 0.35), (B(1), 'pop', 0.4), (B(1) + 0.3, 'boing', 0.3)]
        else:
            c += [(t, 'squeak', 0.25) for t in np.arange(0.4, d, 0.9)] + [(1.5, 'pop', 0.4), (3.5, 'pop', 0.4)]
    elif sc == 'spotlight':
        c += [(0.4, 'whoosh', 0.4), (B(1), 'impact', 0.35), (B(1) + 0.6, 'pop', 0.45)]
    elif sc == 'birds':
        if p.get('stage') == 'offer':
            c += [(0.6, 'pop', 0.4), (B(1), 'sparkle', 0.4), (B(1) + 1.2, 'pop', 0.4)]
        else:
            c += [(0.5, 'pop', 0.4)] + [(t, 'boing', 0.25) for t in np.arange(1.55, d, 2.22)]
    elif sc == 'super_card':
        c += [(0.4, 'pop', 0.45), (B(1), 'ding', 0.3), (B(1) + 2.0, 'boing', 0.3), (B(2) + 0.1, 'impact', 0.4), (B(2) + 0.4, 'sparkle', 0.4)]
    elif sc == 'phone_egg':
        c += [(0.2, 'whoosh', 0.4)] + [(B(1) + 0.1 + i * 0.85, 'pop', 0.4) for i in range(4)]
    elif sc == 'coolidge':
        c += [(0.5, 'squeak', 0.3), (B(1) + 4.5, 'sparkle', 0.45), (B(1) + 5.6, 'squeak', 0.45), (B(1) + 5.8, 'boing', 0.35),
              (B(2) + 0.2, 'ding', 0.35)]
    elif sc == 'tabs':
        c += [(0.3, 'pop', 0.4)] + [(B(1) + i * (d - B(1)) / 32, 'pop_hi', 0.22) for i in range(30)]
    elif sc == 'habituation':
        c += [(0.4 + i * (B(2) - 0.4) / 8, 'pop', 0.3 * 0.8 ** i) for i in range(8)] + [(B(2) + 0.5 + i, 'stamp', 0.35) for i in range(3)]
    elif sc == 'scan':
        c += [(0.5, 'pop', 0.4), (1.0, 'sparkle', 0.35), (5.0, 'ding', 0.3), (B(1) + 1.5, 'pop', 0.35), (B(1) + 3.3, 'pop', 0.35)]
    elif sc == 'who_file':
        c += [(0.3, 'pop', 0.35), (B(1), 'whoosh', 0.4), (B(1) + 0.8, 'pop', 0.4), (B(2), 'pop', 0.3), (B(3) + 1.2, 'whoosh', 0.35),
              (B(3) + 2.4, 'stamp', 0.5)]
    elif sc == 'pct':
        c += [(0.3, 'sparkle', 0.35), (2.0, 'pop', 0.45), (3.2, 'pop', 0.45)]
    elif sc == 'shame':
        c += [(B(1) + 0.5, 'pop', 0.3), (B(2), 'whoosh_dn', 0.35), (B(2) + 1.8, 'ding', 0.3), (B(3) + 0.6, 'whoosh', 0.3)]
    elif sc == 'mixed':
        c += [(0.3, 'pop', 0.4), (B(1) + 1.1, 'whoosh', 0.3), (B(1) + 2.6, 'ding', 0.25), (B(2) - 0.2, 'whoosh', 0.3), (B(2) + 1.3, 'ding', 0.3)]
    elif sc == 'teen12':
        c += [(0.4, 'pop', 0.4), (B(1), 'pop', 0.45), (B(1) + 0.3, 'chime', 0.35)]
    elif sc == 'not_evil':
        c += [(0.3, 'pop', 0.5), (B(1) - 1.6, 'boing', 0.5), (B(1) - 1.4, 'pop', 0.4), (B(1) + 0.3, 'pop', 0.4), (B(1) + 0.8, 'pop', 0.4),
              (B(2), 'whoosh', 0.35)]
    elif sc == 'signs':
        c += [(0.3, 'pop', 0.45)] + [(B(i), 'click', 0.5) for i in (1, 2, 3)]
    elif sc == 'tips':
        c += [(B(1), 'whoosh', 0.35), (B(1) + 1.0, 'click', 0.4), (B(2), 'whoosh', 0.35)] + [(B(2) + 0.8 + i * 0.6, 'pop', 0.4) for i in range(3)]
        c += [(B(3), 'whoosh', 0.35)] + [(B(3) + 0.5 + i * 0.5, 'pop', 0.35) for i in range(3)] + [(B(4) + 0.4, 'whoosh', 0.3),
                                                                                                  (B(4) + 1.2, 'chime', 0.4)]
    elif sc == 'real':
        c += [(1.5, 'sparkle', 0.3), (B(1), 'chime', 0.35)]
    return c


# ------------------------------------------------------------------ voice polish + mix
def polish_voice(v24):
    v = signal.resample_poly(v24, 2, 1)
    v = hp(v, 75)
    # gentle presence + warmth
    v = v + 0.18 * bp(v, 2500, 6000) + 0.1 * lp(v, 250)
    # soft compression
    e = np.sqrt(np.abs(lp(v ** 2, 8)) + 1e-9)
    g = np.minimum(1.0, (0.12 / np.maximum(e, 1e-4)) ** 0.35)
    v = v * g
    # short room
    n = int(0.35 * SR)
    ir = RNG.normal(0, 1, n) * np.exp(-np.arange(n) / SR * 18)
    ir = lp(ir, 4000)
    wet = signal.fftconvolve(v, ir)[:len(v)]
    v = v + 0.035 * wet / (np.max(np.abs(wet)) / max(np.max(np.abs(v)), 1e-6) + 1e-9)
    return v / (np.max(np.abs(v)) + 1e-9) * 0.9


def mix(ep, shots, vtrack, total, out_path):
    n = int((total + 1) * SR)
    v = polish_voice(vtrack)
    v = np.pad(v, (0, max(0, n - len(v))))[:n]
    # music: mood per bar
    nbars = int(math.ceil(total / BAR)) + 1
    moods = []
    for bi in range(nbars):
        tm = bi * BAR + BAR * 0.5
        m = shots[-1].get('mood', 'warm')
        for sh in shots:
            if sh['start'] <= tm < sh['start'] + sh['dur']:
                m = sh.get('mood', 'warm')
                break
        moods.append(m)
    music = render_music(moods, nbars, ep.get('music', {}).get('root', 50))[:n]
    music = np.pad(music, ((0, max(0, n - len(music))), (0, 0)))
    music /= np.max(np.abs(music)) + 1e-9
    # fade the music in/out
    music[:int(1.0 * SR)] *= np.linspace(0, 1, int(1.0 * SR))[:, None]
    tail = int(3.0 * SR)
    music[int(total * SR) - tail:int(total * SR)] *= np.linspace(1, 0, tail)[:, None]
    music[int(total * SR):] = 0
    # ducking under the voice
    ve = np.sqrt(np.abs(lp(v ** 2, 3)) + 1e-9)
    ve = ve / (np.max(ve) + 1e-9)
    duck = 1.0 - 0.6 * np.clip(ve * 3.0, 0, 1)
    duck = lp(lp(duck, 0.8), 0.8)
    music *= (0.19 * duck)[:, None]
    # sfx
    fx = np.zeros((n, 2))
    for i, sh in enumerate(shots):
        if i > 0 and sh['scene'] != 'chapter':
            add(fx, sh['start'] - 0.3, sfx('whoosh'), 0.12)
        for t, name, g in cues(sh):
            if t < sh['dur'] + 0.5:
                pan = float(np.clip(RNG.normal(0, 0.25), -0.6, 0.6))
                add(fx, sh['start'] + t, sfx(name), g * 0.32, pan=pan)
    out = music + fx + np.stack([v, v], 1) * 0.8
    out /= np.max(np.abs(out)) + 1e-9
    import soundfile as sf
    raw = out_path.replace('.wav', '_raw.wav')
    sf.write(raw, (out * 0.89).astype(np.float32), SR)
    import json as _j
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=20:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True)
    js = r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1]
    m = _j.loads(js)
    gain = -14.0 - float(m['input_i'])
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af',
                    f'volume={gain:.2f}dB,alimiter=limit=0.72:attack=2:release=60:level=disabled', '-ar', str(SR), out_path],
                   check=True)
    os.remove(raw)
    # also keep stems for QA
    return out_path
