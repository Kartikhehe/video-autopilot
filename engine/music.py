"""Original score + sound design synthesised per story (no samples => no Content ID claims).

Each scene has a `mood`; sound effects are derived automatically from scene params
(chat messages, urge whispers, taps, cheers...) plus any explicit `sfx` list.
"""
import wave
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt

SR = 44100

BASE_CH = {
    'C': [48, 55, 60, 64, 67, 72], 'G': [43, 50, 55, 59, 62, 67], 'Am': [45, 52, 57, 60, 64, 69],
    'F': [41, 48, 53, 57, 60, 65], 'Dm': [50, 57, 62, 65, 69], 'E': [40, 47, 52, 56, 59, 64],
    'Em': [40, 47, 52, 55, 59, 64], 'Fmaj7': [41, 48, 52, 57, 60, 64],
}
MAJ_PENTA = [0, 2, 4, 7, 9]
MIN_SCALE = [0, 2, 3, 5, 7, 8, 10]

MOOD_LEVEL = dict(warm=-20, groove=-19.5, calm=-23, curious=-21, rush=-20, dark=-21.5, tense=-18.5, numb=-24,
                  sad=-22, tender=-22, hope=-21, triumph=-18, silence=-30)


def mf(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, 'low', fs=SR, output='sos'), x)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], 'band', fs=SR, output='sos'), x)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, 'high', fs=SR, output='sos'), x)


class Score:
    def __init__(self, total, key=0, tempo=96, seed=1):
        self.N = int(total * SR) + SR
        self.total = total
        self.music = np.zeros((self.N, 2))
        self.sfx = np.zeros((self.N, 2))
        self.key = key
        self.beat = 60.0 / tempo
        self.rng = np.random.default_rng(seed)
        self.CH = {k: [m + key for m in v] for k, v in BASE_CH.items()}

    # ------------------------------------------------ primitives
    def add(self, buf, t, sig, gain=1.0, pan=0.0):
        i = int(t * SR)
        if i >= len(buf) or i + len(sig) <= 0:
            return
        if sig.ndim == 1:
            l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
            sig = np.stack([sig * l * 1.414, sig * r * 1.414], 1)
        j = min(len(buf), i + len(sig))
        buf[max(i, 0):j] += sig[max(0, -i):j - i] * gain

    def piano(self, m, dur=3.0, vel=0.6):
        f0 = mf(m)
        n = int((dur + 1.2) * SR)
        t = np.arange(n) / SR
        out = np.zeros(n)
        for k in range(1, 10):
            fk = f0 * k * np.sqrt(1 + 0.0003 * k * k)
            if fk > 12000:
                break
            amp = (1 / k ** 1.25) * (1 if k < 3 else 0.7)
            dec = 1.2 + 0.9 * k + f0 / 300
            out += amp * np.exp(-t * dec / (1 + vel)) * np.sin(2 * np.pi * fk * t + self.rng.random() * 6)
        ham = self.rng.normal(0, 1, int(0.01 * SR)) * np.linspace(1, 0, int(0.01 * SR)) * 0.15
        out[:len(ham)] += lp(ham, 3000)
        off = int(dur * SR)
        out[off:] *= np.exp(-np.arange(n - off) / (0.25 * SR))
        out[:int(0.003 * SR)] *= np.linspace(0, 1, int(0.003 * SR))
        return lp(out, 2500 + vel * 4000) * vel

    def ks(self, m, dur=2.5, bright=0.5, decay=0.996):
        f = mf(m)
        Np = int(SR / f)
        n = int(dur * SR)
        y = np.zeros(n + Np + 1)
        y[:Np] = lp(self.rng.uniform(-1, 1, Np), 1500 + bright * 5000, 1)
        i = Np
        while i < n:
            j = min(n, i + Np)
            if i - Np - 1 >= 0:
                y[i:j] = 0.5 * (y[i - Np:j - Np] + y[i - Np - 1:j - Np - 1]) * decay
            else:
                y[i:j] = y[i - Np:j - Np] * decay
            i = j
        out = y[:n]
        out = out * 0.6 + bp(out, 90, 5000, 1) * 0.6
        out[-int(0.08 * SR):] *= np.linspace(1, 0, int(0.08 * SR))
        return out

    def strum(self, t, chord, gain=0.2, down=True, dur=2.0, detune=0.0, pan=-0.15):
        notes = self.CH[chord] if down else list(reversed(self.CH[chord]))
        for i, m in enumerate(notes):
            self.add(self.music, t + i * 0.014 + self.rng.random() * 0.004, self.ks(m + 12 + detune, dur), gain, pan + 0.05 * i)

    def pick(self, t, chord, gain=0.15, step=0.3, pattern=(0, 3, 4, 5, 4, 3)):
        notes = self.CH[chord]
        for k, idx in enumerate(pattern):
            self.add(self.music, t + k * step, self.ks(notes[min(idx, len(notes) - 1)] + 12, 2.0, 0.4), gain, -0.2)

    def pad(self, t, chord, dur, gain=0.06, cutoff=1400, attack=1.2):
        n = int((dur + 1.5) * SR)
        tt = np.arange(n) / SR
        out = np.zeros(n)
        for m in self.CH[chord][1:5]:
            for det in (-0.08, 0.0, 0.07):
                out += 2 * ((tt * mf(m) * 2 ** (det / 12) + self.rng.random()) % 1.0) - 1
        out = lp(out, cutoff, 2) * np.minimum(1, tt / attack) * np.clip((dur + 1.5 - tt) / 1.5, 0, 1) / 12
        self.add(self.music, t, np.stack([out, np.roll(out, 900)], 1), gain)

    def drone(self, t, dur, m=33, gain=0.1, dark=280):
        n = int(dur * SR)
        tt = np.arange(n) / SR
        f = mf(m + self.key)
        out = np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 1.5 * tt + 1) + 0.3 * (2 * ((tt * f * 1.003) % 1) - 1)
        out = lp(out, dark) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.2 * tt))
        out *= np.minimum(1, tt / 1.5) * np.clip((dur - tt) / 1.5, 0, 1)
        self.add(self.music, t, out, gain)

    def note(self, t, m, dur, gain=0.15, vel=0.45, pan=0.15):
        self.add(self.music, t, self.piano(m, dur, vel), gain, pan)

    def melody(self, t, dur, chord_seq, step, minor=False, gain=0.12, vel=0.42, density=0.7, octave=72):
        """Random-walk melody on the scale, landing on chord tones on downbeats."""
        scale = MIN_SCALE if minor else MAJ_PENTA
        base = octave + self.key - (3 if minor else 0)
        deg = 2
        n = int(dur / step)
        for i in range(n):
            if self.rng.random() > density:
                continue
            deg = int(np.clip(deg + self.rng.choice([-2, -1, -1, 0, 1, 1, 2]), 0, len(scale) * 2 - 1))
            m = base + scale[deg % len(scale)] + 12 * (deg // len(scale))
            if i % 4 == 0 and chord_seq:
                ch = self.CH[chord_seq[(i // 4) % len(chord_seq)]]
                cands = [x + 12 * k for x in ch for k in (0, 1, 2) if abs(x + 12 * k - m) < 6]
                if cands:
                    m = min(cands, key=lambda x: abs(x - m))
            self.note(t + i * step, m, step * 1.6, gain, vel)

    # ------------------------------------------------ sfx
    def heartbeat(self, t, gain=0.4):
        for dt, g in ((0, 1.0), (0.26, 0.7)):
            n = int(0.22 * SR)
            tt = np.arange(n) / SR
            s = np.sin(2 * np.pi * np.cumsum(55 * np.exp(-tt * 6)) / SR) * np.exp(-tt * 18)
            self.add(self.sfx, t + dt, s, gain * g)

    def boom(self, t, gain=0.7):
        n = int(3.0 * SR)
        tt = np.arange(n) / SR
        s = np.sin(2 * np.pi * np.cumsum(80 * np.exp(-tt * 1.2) + 30) / SR) * np.exp(-tt * 1.4)
        s += lp(self.rng.normal(0, 1, n), 400) * np.exp(-tt * 4) * 0.4
        self.add(self.sfx, t, s, gain)

    def whisper(self, t, dur=1.2, gain=0.22, pan=0.3):
        n = int(dur * SR)
        tt = np.arange(n) / SR
        syl = 0.5 + 0.5 * np.sin(2 * np.pi * (3.2 + self.rng.random()) * tt) ** 2
        s = bp(self.rng.normal(0, 1, n), 1200, 5200) * syl * np.sin(np.pi * tt / dur) ** 0.7
        s = s + lp(np.sin(2 * np.pi * 70 * tt + 3 * np.sin(2 * np.pi * 9 * tt)) * 0.35, 300) * np.sin(np.pi * tt / dur)
        self.add(self.sfx, t, s, gain, pan)

    def bucket(self, t, gain=0.3, pan=0.25):
        n = int(0.3 * SR)
        tt = np.arange(n) / SR
        s = np.sin(2 * np.pi * np.cumsum(140 * np.exp(-tt * 14) + 70) / SR) * np.exp(-tt * 16)
        s += bp(self.rng.normal(0, 1, n), 250, 900) * np.exp(-tt * 40) * 0.5
        self.add(self.sfx, t, s, gain, pan)

    def slap(self, t, gain=0.2, pan=0.25):
        n = int(0.12 * SR)
        self.add(self.sfx, t, hp(self.rng.normal(0, 1, n), 1500) * np.exp(-np.arange(n) / SR * 45), gain, pan)

    def click(self, t, gain=0.15):
        n = int(0.02 * SR)
        self.add(self.sfx, t, hp(self.rng.normal(0, 1, n), 2500) * np.exp(-np.arange(n) / (0.003 * SR)), gain)

    def blip(self, t, f0=660, f1=990, gain=0.16):
        n = int(0.25 * SR)
        tt = np.arange(n) / SR
        self.add(self.sfx, t, np.sin(2 * np.pi * np.cumsum(np.where(tt < 0.07, f0, f1)) / SR) * np.exp(-tt * 14), gain)

    def whoosh(self, t, dur=0.4, gain=0.14, up=True):
        n = int(dur * SR)
        tt = np.arange(n) / SR
        e = (tt / dur) ** 2 if up else (1 - tt / dur) ** 2
        self.add(self.sfx, t, bp(self.rng.normal(0, 1, n), 600, 6000) * e * np.sin(np.pi * tt / dur) ** 0.3, gain)

    def bell(self, t, gain=0.12):
        n = int(1.8 * SR)
        tt = np.arange(n) / SR
        f = mf(91)
        s = sum(a * np.sin(2 * np.pi * f * r * tt) * np.exp(-tt * d) for a, r, d in ((1, 1, 3), (0.5, 2.76, 6), (0.3, 5.4, 9)))
        self.add(self.sfx, t, s, gain)

    def sparkle(self, t, dur, density=8, gain=0.06):
        for _ in range(int(dur * density)):
            self.add(self.sfx, t + self.rng.random() * dur, self.piano(int(self.rng.choice([84, 86, 88, 91, 93, 96])), 0.4, 0.3),
                     gain, self.rng.uniform(-0.7, 0.7))

    def tick(self, t):
        self.click(t, 0.08)

    def crowd(self, t, dur, gain=0.3):
        n = int(dur * SR)
        tt = np.arange(n) / SR
        s = bp(self.rng.normal(0, 1, n), 400, 3500) * np.minimum(1, tt / 0.6) * np.clip((dur - tt) / 1.5, 0, 1)
        self.add(self.sfx, t, np.stack([s, np.roll(s, 1200)], 1), gain * 0.5)
        for _ in range(int(dur * 25)):
            self.slap(t + 0.3 + self.rng.random() * max(0.1, dur - 1.5), 0.06 * self.rng.random() + 0.03, self.rng.uniform(-0.8, 0.8))

    def drawer(self, t, slam=False):
        n = int(0.4 * SR)
        tt = np.arange(n) / SR
        self.add(self.sfx, t, bp(self.rng.normal(0, 1, n), 200, 1500) * np.sin(np.pi * tt / 0.4) * 0.5, 0.22)
        if slam:
            self.bucket(t + 0.35, 0.35, 0)

    # ------------------------------------------------ moods
    def mood(self, name, t0, d, scene):
        b = self.beat
        p = scene.get('params', {})
        if name == 'silence':
            return
        if name in ('warm', 'groove', 'triumph'):
            bt = b * (0.92 if name == 'groove' else 1.0)
            prog = ['C', 'G', 'Am', 'F']
            bars = int(np.ceil(d / (4 * bt)))
            perc = name != 'warm' or scene['template'] in ('hangout', 'stage')
            for bar in range(bars):
                ch = prog[bar % 4]
                st = t0 + bar * 4 * bt
                pattern = ((0, 1), (1, 1), (1.5, 0), (2.5, 0), (3, 1)) + (((3.5, 0),) if name == 'triumph' else ())
                for k, (off, down) in enumerate(pattern):
                    if st + off * bt < t0 + d - 0.3:
                        self.strum(st + off * bt, ch, 0.16 if k else 0.2, bool(down), 1.7)
                if perc:
                    for q in range(4):
                        if st + q * bt < t0 + d - 0.2:
                            self.bucket(st + q * bt, 0.3 if q % 2 == 0 else 0.2)
                            if q % 2:
                                self.slap(st + q * bt, 0.14)
                self.note(st, self.CH[ch][0], 4 * bt, 0.15, 0.5)
                if name == 'triumph':
                    self.pad(st, ch, 4 * bt, 0.04, 1800, 0.3)
            self.melody(t0 + 4 * bt if name == 'warm' else t0, d - 4 * bt if name == 'warm' else d, prog, bt,
                        gain=0.11 if name != 'triumph' else 0.13, density=0.55 if name == 'warm' else 0.75)
        elif name == 'calm':
            for i, ch in enumerate(['Am', 'F', 'C', 'G']):
                if i * 3.5 < d:
                    self._arp(t0 + i * 3.5, ch, 0.44, min(8, int((d - i * 3.5) / 0.44)), 0.13)
            self.pad(t0, 'Am', d, 0.04)
        elif name == 'curious':
            self.drone(t0, d + 0.5, 33, 0.07)
            self.pad(t0, 'Dm', d, 0.04, 900)
            self.melody(t0 + 0.4, d - 0.6, None, 0.7, minor=True, gain=0.08, vel=0.35, density=0.45, octave=81)
        elif name == 'rush':
            self.pad(t0, 'Fmaj7', d, 0.10, 3500, 0.4)
            self.sparkle(t0 + 0.3, d - 0.6, 9, 0.07)
            for k in range(int(d / 1.05)):
                self.heartbeat(t0 + 0.6 + k * 1.05, 0.28)
        elif name == 'dark':
            self.drone(t0, d + 0.5, 31, 0.10, 220)
            self.pad(t0, 'Am', d, 0.04, 800)
            self.melody(t0 + 0.4, d - 0.6, None, 0.6, minor=True, gain=0.1, vel=0.35, density=0.4, octave=72)
        elif name == 'tense':
            self.drone(t0, d + 0.5, 29, 0.13, 240)
            self.pad(t0, 'Dm', d, 0.05, 700)
            n = int(d / 0.5)
            for k in range(n):
                self.heartbeat(t0 + 0.2 + k * (0.62 - 0.2 * k / max(n, 1)), 0.22 + 0.15 * k / max(n, 1))
        elif name == 'numb':
            self.pad(t0, 'Em', d, 0.05, 700)
            for k in range(int(d)):
                self.tick(t0 + 0.3 + k)
            self.melody(t0 + 0.8, d - 1, None, 0.65, minor=True, gain=0.07, vel=0.3, density=0.35)
        elif name == 'sad':
            prog = ['Am', 'F', 'C', 'G']
            for i in range(int(np.ceil(d / 2.0))):
                self.note(t0 + i * 2.0, self.CH[prog[i % 4]][0], 2.2, 0.14, 0.4)
            self.melody(t0 + 0.2, d - 0.4, prog, 0.5, minor=True, gain=0.16, vel=0.4, density=0.75, octave=69)
        elif name == 'tender':
            prog = ['F', 'C', 'G', 'Am']
            for i in range(int(np.ceil(d / 2.0))):
                self.pick(t0 + i * 2.0, prog[i % 4], 0.13, 0.33)
                self.note(t0 + i * 2.0, self.CH[prog[i % 4]][0], 2.0, 0.12, 0.4)
        elif name == 'hope':
            prog = ['Am', 'F', 'C', 'G']
            for i in range(int(np.ceil(d / 2.0))):
                ch = prog[i % 4]
                self.pick(t0 + i * 2.0, ch, 0.14, 0.3)
                self.note(t0 + i * 2.0, self.CH[ch][0], 2.0, 0.13, 0.45)
            self.pad(t0, 'Fmaj7', d, 0.06, 2000)
            self.melody(t0 + d * 0.4, d * 0.6, prog, 0.5, gain=0.1, density=0.6)

    def _arp(self, t, chord, step, n, gain):
        notes = self.CH[chord][1:]
        seq = notes + notes[-2:0:-1]
        for i in range(max(0, n)):
            self.note(t + i * step, seq[i % len(seq)], step * 2.2, gain, 0.45, 0.1 * ((i % 3) - 1))

    # ------------------------------------------------ automatic sfx from scene params
    def auto_sfx(self, sc):
        t0, d, tpl, p = sc['t0'], sc['duration'], sc['template'], sc.get('params', {})
        def urge_sfx(u, base, dur):
            for tw, _ in u.get('whispers', []):
                self.whisper(base + tw, 1.3, 0.2)
            if u.get('size', 0) >= 150 and sc.get('mood') not in ('tense',):
                for k in range(int(dur / 1.2)):
                    self.heartbeat(base + 0.3 + k * 1.2, 0.18)
            if 'pop_at' in u:
                self.sparkle(base + u['pop_at'], 1.2, 10, 0.06)
                self.blip(base + u['pop_at'], 1200, 1800, 0.1)
        if tpl == 'phone_feed':
            tap = p.get('tap_at', d - 2.0)
            for k in range(int((tap - 0.8) / 0.35)):
                self.click(t0 + 0.3 + k * 0.35, 0.05)
            self.heartbeat(t0 + tap - 2.0, 0.3)
            self.click(t0 + tap + 0.05, 0.3)
            self.whoosh(t0 + tap + 0.3, 1.4, 0.22)
        if tpl == 'phone_chat':
            for ta, side, _ in p.get('messages', []):
                (self.blip if side == 'L' else self.whoosh)(t0 + ta)
            if p.get('typing'):
                a, b_, _ = p['typing']
                for k in range(int((b_ - a) / 0.2)):
                    self.click(t0 + a + k * 0.2, 0.04)
        if 'urge' in p:
            urge_sfx(p['urge'], t0, d)
        if tpl == 'montage':
            total = sum(s['dur'] for s in p['shots'])
            acc = 0.0
            for i, sh in enumerate(p['shots']):
                sd = sh['dur'] * d / total
                if 'urge' in sh.get('params', {}):
                    urge_sfx(sh['params']['urge'], t0 + acc, sd)
                if i and sc.get('mood') in ('dark', 'tense'):
                    self.boom(t0 + acc, 0.3)
                acc += sd
        if tpl in ('stage', 'gallery') and p.get('cheer_at') is not None:
            self.crowd(t0 + p['cheer_at'], max(1.5, d - p['cheer_at']), 0.35)
        if tpl == 'hangout':
            if 'hi5_at' in p:
                self.slap(t0 + p['hi5_at'] + 0.35, 0.5, 0)
                self.slap(t0 + p['hi5_at'] + 0.37, 0.4, 0)
            if p.get('hero', {}).get('activity') == 'walk_in':
                for k in range(int(p['hero'].get('walk_dur', 3.0) / 0.35)):
                    self.click(t0 + 0.2 + k * 0.35, 0.05)
        if tpl == 'bedroom':
            if 'put_away' in p:
                self.drawer(t0 + p['put_away'][0] + 0.3)
                self.drawer(t0 + p['put_away'][1] - 0.3, slam=True)
            if p.get('pose') == 'reach':
                self.drawer(t0 + p.get('reach_at', d * 0.6) + 0.4)
                self.boom(t0 + p.get('reach_at', d * 0.6) + 0.6, 0.7)
        if tpl == 'card':
            for k in range(int(d / 0.8)):
                self.tick(t0 + 0.2 + k * 0.8)
        if tpl == 'outro':
            for tc in (2.5, 3.7, 4.9, 6.3):
                self.click(t0 + tc, 0.25)
            self.blip(t0 + 2.55, 990, 1480, 0.12)
            self.bell(t0 + 5.7)
        for ts, name in sc.get('sfx', []):
            fn = getattr(self, name, None)
            if fn:
                fn(t0 + ts)

    # ------------------------------------------------ mix
    def render(self, timeline, path):
        for sc in timeline:
            self.mood(sc.get('mood', 'calm'), sc['t0'], sc['duration'], sc)
            self.auto_sfx(sc)
        rng = np.random.default_rng(1)
        n = int(2.4 * SR)
        tt = np.arange(n) / SR
        ir = rng.normal(0, 1, (n, 2)) * np.exp(-tt * 3.0)[:, None]
        ir = np.stack([lp(ir[:, 0], 6000), lp(ir[:, 1], 6000)], 1)
        ir /= np.sqrt((ir ** 2).sum(0))
        wet = np.stack([fftconvolve(self.music[:, k], ir[:, k])[:self.N] for k in range(2)], 1)
        swet = np.stack([fftconvolve(self.sfx[:, k], ir[:, k])[:self.N] for k in range(2)], 1)
        mix = self.music * 0.8 + wet * 0.55 + self.sfx * 0.9 + swet * 0.2
        mix = hp(mix.T, 28).T
        ref = np.sqrt((mix ** 2).mean()) + 1e-9
        gains = np.ones(len(mix))
        for sc in timeline:
            a, b = int(sc['t0'] * SR), int((sc['t0'] + sc['duration']) * SR)
            seg = mix[a:b]
            if len(seg) == 0 or sc.get('mood') == 'silence':
                continue
            cur = 20 * np.log10(np.sqrt((seg ** 2).mean()) / ref + 1e-9)
            gains[a:b] = 10 ** ((MOOD_LEVEL.get(sc.get('mood', 'calm'), -21) + 20 - cur) / 20)
        gains = np.clip(gains, 0.1, 6.0)
        k = int(0.5 * SR)
        gains = np.convolve(np.pad(gains, (k, k), mode='edge'), np.ones(2 * k + 1) / (2 * k + 1), 'same')[k:-k]
        mix *= gains[:, None]
        n_end = int(self.total * SR)
        fo = int(2.5 * SR)
        mix[n_end - fo:n_end] *= np.linspace(1, 0, fo)[:, None]
        mix = mix[:n_end]
        mix /= np.max(np.abs(mix)) + 1e-9
        mix = np.tanh(mix * 1.6) / np.tanh(1.6) * 0.89
        with wave.open(path, 'wb') as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((mix * 32767).astype(np.int16).tobytes())
