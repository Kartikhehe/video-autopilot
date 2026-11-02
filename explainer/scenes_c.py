"""Scenes for episode 2 (what porn does to your brain). Non-explicit by design: phones show abstract tiles,
hearts and play buttons; people are always clothed; animals are cute."""
import math

import numpy as np
import skia

from .art import *  # noqa: F401,F403
from .scenes_a import bt, HOLI, info_pill, mini_person, traveller, info_card, room, graph_axes
from .scenes_b import mouse_char, neuron_shape, heart as big_heart

HEARTS = ['#ff3d6e', '#ff9ad5', '#ffd23f', '#ff7a1a']


def stars(c, t, n=80, seed=3, a=0.8):
    rng = np.random.default_rng(seed)
    for i in range(n):
        x, y = rng.random() * W, rng.random() * H * 0.6
        circle(c, x, y, 1.5 + rng.random() * 2.5, '#ffffff', a * (0.4 + 0.6 * abs(math.sin(t * 0.8 + i))))


def fire(c, x, y, s, t):
    glow(c, x, y - 60 * s, 420 * s, '#ff9a3d', 0.55)
    for i, (hc, sc) in enumerate([('#ff3d2e', 1.0), ('#ff9a1a', 0.72), ('#ffe14d', 0.45)]):
        pts = []
        for j in range(9):
            an = math.pi * (1 + j / 8)
            r = 90 * s * sc
            fl = 1 + 0.25 * math.sin(t * 7 + j * 1.3 + i)
            pts.append((x + math.cos(an) * r, y + math.sin(an) * r * (1.9 if j == 4 else 1.2) * fl))
        pts.append((x + 60 * s * sc, y + 20 * s))
        pts.append((x - 60 * s * sc, y + 20 * s))
        c.drawPath(smooth_path(pts, k=0.5), P(hc))
    for k in (-1, 1):
        rrect(c, x - 110 * s, y + 5 * s, 220 * s, 34 * s, 17 * s, '#7a3a1f')


CAVE = [dict(skin='#b77a50', hair='#2b1a10', style='long', shirt='#c98a4a', pants='#7a4a2a', shoe='#5a3a20'),
        dict(skin='#8a5636', hair='#120a08', style='curly', shirt='#a0622d', pants='#5a3a20', shoe='#5a3a20'),
        dict(skin='#d99a6c', hair='#3a1d10', style='short', shirt='#b8743a', pants='#6a3f1f', shoe='#5a3a20')]


def s_cave(c, t, d, p, b):
    bg_grad(c, '#0e1a4a', '#3a1d5e', '#1d2a6b')
    stars(c, t)
    circle(c, 1550, 220, 70, '#fff3c4')
    # hills
    c.drawPath(smooth_path([(-100, 700), (300, 520), (700, 640), (1100, 500), (1500, 620), (2000, 520), (2100, 1200), (-100, 1200)], k=0.5),
               P('#2a1d55'))
    c.drawRect(skia.Rect(0, 860, W, H), P('#24183f'))
    fire(c, 960, 900, 1.0, t)
    t1 = bt(b, 1, 4)
    # one hopeful walker crossing the hills, then everybody chats at the fire
    kx = ramp(t, 0.3, t1)
    person(c, lerp(-150, 700, eio(kx)), 930, 0.9, CAVE[2], expr='curious' if kx < 1 else 'happy', t=t * 2.4 * (1 - kx) + t,
           arms=('down', 'wave' if kx >= 1 else 'down'), look=(1, 0))
    person(c, 1240, 940, 0.95, CAVE[0], expr='happy' if t > t1 + 1 else 'neutral', t=t + 1, arms=('down', 'down'), look=(-1, 0))
    person(c, 1450, 950, 0.9, CAVE[1], expr='laugh' if t > t1 + 2.5 else 'neutral', t=t + 2, arms=('hip', 'down'), look=(-1, 0))
    labels = [('WALK', t1 + 0.1), ('TALK', t1 + 0.6), ('RISK REJECTION', t1 + 1.2), ('GET LUCKY (SOMETIMES)', t1 + 2.6)]
    for i, (s_, tw) in enumerate(labels):
        k = pop(t, tw)
        if k > 0:
            info_pill(c, 380 + (i % 2) * 520 if i < 3 else 960, 180 + (i // 2) * 150 if i < 3 else 470, s_, '',
                      ['#ffb02e', '#2bd1ff', '#ff3d6e', '#7cf2c4'][i], k)
    for i in range(20):
        ph = (t * 0.6 + i * 0.13) % 1
        circle(c, 960 + 60 * math.sin(i * 2 + t), 840 - ph * 380, 4 * (1 - ph), '#ffd27a', 1 - ph)


def s_pocket(c, t, d, p, b):
    room(c, t, 0.0, 0.0)
    clock(c, 1500, 260, 90, 1.0 + t / d * 0.6)
    # bed + person lying with phone
    rrect(c, 300, 760, 1300, 160, 40, '#3d4f86')
    rrect(c, 300, 700, 260, 90, 40, '#e8e0ff')
    info = person(c, 700, 980, 1.0, dict(skin='#d99a6c', hair='#22122e', style='short', shirt='#ff6f59'),
                  expr='curious' if t < bt(b, 1, 3) else 'dazed', t=t, arms=('hold', 'hold'), look=(0.6, -0.5), sit=True)
    k = back(ramp(t, 0.3, 1.0))
    phone(c, 1100, 540, 1.2 * k, t, glow_c='#ff3d8b', scroll=1.6, ang=6)
    for i in range(14):
        ph = (t * 0.35 + i * 0.071) % 1
        x = 1100 + (i - 7) * 50 + 30 * math.sin(i)
        y = 300 - ph * 300
        heart_icon(c, x, y, 16 + 8 * (i % 3), HEARTS[i % 4], (1 - ph) * k)
    t1 = bt(b, 1, 3)
    for i, w_ in enumerate(['FREE', 'PRIVATE', 'ONE TAP AWAY']):
        kk = pop(t, t1 + 0.1 + i * 0.6)
        if kk > 0:
            info_pill(c, 1600, 520 + i * 150, w_, '', ['#2bd17e', '#7b5cff', '#ff3d6e'][i], kk)


def s_flat_life(c, t, d, p, b):
    t1, t2 = bt(b, 1, 3), bt(b, 2, 6)
    gray = ramp(t, t2 + 0.3, t2 + 2.5)
    top, bot = mix('#ffb02e', '#6a6a7a', gray), mix('#d1366b', '#3a3a4a', gray)
    bg_grad(c, top, bot)
    # friends waving outside the window / a bike / guitar: colourful life that fades
    for i, (x, colr) in enumerate([(300, '#2bd17e'), (1620, '#2bd1ff')]):
        person(c, x, 1000, 1.0, dict(skin=SKINS[i * 2], hair='#22122e', style=['bun', 'curly'][i], shirt=mix(colr, '#8a8a9a', gray)),
               expr='happy' if gray < 0.5 else 'sad', t=t + i, arms=('wave', 'down') if i == 0 else ('down', 'wave'),
               look=(1 if i == 0 else -1, 0))
    a_fade = 1 - 0.75 * gray
    c.saveLayerAlpha(None, int(255 * a_fade))
    for i in range(10):
        ph = (t * 0.2 + i * 0.1) % 1
        circle(c, 200 + i * 170, 200 + 40 * math.sin(t + i), 14, HOLI[i % 6], 0.8)
    c.restore()
    # couch + person + phone
    rrect(c, 640, 700, 640, 220, 60, mix('#7b5cff', '#5a5a6a', gray))
    rrect(c, 600, 780, 720, 150, 60, mix('#5a3fd1', '#4a4a5a', gray))
    person(c, 960, 905, 1.25, dict(skin='#f2c29b', hair='#5a2a10', style='long', shirt=mix('#ff6f59', '#7a7a8a', gray)),
           expr='neutral' if t < t1 else ('bored' if gray < 0.5 else 'dazed'), t=t, arms=('hold', 'hold'), look=(0.3, 0.5), sit=True)
    phone(c, 1000, 700, 0.35, t, glow_c='#ff3d8b', scroll=1.5)
    if t > t1:
        hrs = 20 + 5 * eio(ramp(t, t1, d))
        clock(c, 1600, 260, 95, hrs % 12)
        kt = ramp(t, t1 + 0.4, t1 + 1)
        text(c, 'HOURS DISAPPEAR', 1600, 440, 46, '#ffffff', kt, weight=900)
    if gray > 0:
        text(c, 'FLAT.', 300, 260, 130 * back(gray) + 1, '#ffffff', gray, weight=900)


# ------------------------------------------------------------------ chapter 1
def dopa(c, x, y, s=1.0, a=1.0, t=0.0):
    glow(c, x, y, 40 * s, '#ffd23f', 0.6 * a)
    circle(c, x, y, 13 * s, '#ffd23f', a)
    circle(c, x - 4 * s, y - 4 * s, 4 * s, '#ffffff', 0.8 * a)


def s_dopamine(c, t, d, p, b):
    bg_radial(c, (960, 520), '#5a2a9e', '#140838', 1200)
    particles(c, t, seed=301, n=40, a=0.3)
    neuron_shape(c, 700, 520, 90, '#ff4fa3', t, seed=4, reach=260, expr='happy', look=(0.6, 0))
    neuron_shape(c, 1350, 560, 70, '#7b5cff', t, seed=9, reach=220, expr='curious', look=(-0.6, 0))
    for i in range(26):
        ph = (t * 0.5 + i * 0.039) % 1
        x = lerp(820, 1260, ph)
        y = 540 + 90 * math.sin(i * 1.7) * math.sin(ph * math.pi)
        dopa(c, x, y, 1.0, 1.0 - 0.5 * ph)
    k = pop(t, 0.8)
    text(c, 'DOPAMINE', 960, 220, 120 * k + 1, '#ffd23f', clamp01(k), weight=900)
    t1, t2 = bt(b, 1, 4), bt(b, 2, 6)
    k1 = pop(t, t1 + 0.2)
    if k1 > 0:
        info_pill(c, 960, 880, '"THE PLEASURE CHEMICAL"', '', '#ff3d6e', k1)
    k2 = ramp(t, t2 + 0.2, t2 + 0.6)
    if k2 > 0:
        w = 640 * k2
        line(c, [(960 - 320, 880), (960 - 320 + w, 880)], 14, '#ff3d6e')
        kq = pop(t, t2 + 0.6)
        text(c, 'NOT QUITE.', 960, 1010, 70 * kq + 1, '#ffffff', clamp01(kq), weight=900)


def sugar(c, x, y, s=1.0, a=1.0):
    rrect(c, x - 40 * s, y - 40 * s, 80 * s, 80 * s, 10 * s, '#ffffff', a)
    rrect(c, x - 40 * s, y - 40 * s, 80 * s, 22 * s, 10 * s, '#f0ecff', a)
    for i in range(5):
        circle(c, x - 22 * s + i * 11 * s, y + (i % 2) * 12 * s, 3 * s, '#d8d0f0', a)


def meter(c, x, y, w, val, colr, label_, a=1.0):
    text(c, label_, x, y - 18, 30, '#ffffff', a, weight=900, align='left', shadow=0.3)
    rrect(c, x, y, w, 34, 17, '#ffffff', 0.25 * a)
    rrect(c, x, y, max(34, w * clamp01(val)), 34, 17, colr, a)


def s_rats_sugar(c, t, d, p, b):
    mode = p.get('mode', 'low')
    bg_grad(c, '#ffb02e' if mode == 'low' else '#ff7a1a', '#b8326a')
    particles(c, t, seed=311, n=40, h='#fff3c4', a=0.4)
    c.drawRect(skia.Rect(0, 840, W, H), P('#7a2a5a'))
    if mode == 'low':
        # sugar on a high ledge; rat would have to climb. It tastes some (happy) but doesn't go for more.
        rrect(c, 1300, 520, 420, 40, 20, '#5a1a4a')
        for i in range(3):
            sugar(c, 1400 + i * 100, 470, 1.0)
        t1 = bt(b, 1, 5)
        taste = win(t, 1.5, t1, 0.4)
        sugar(c, 800, 800, 0.6)
        mouse_char(c, 560, 780, 1.15, t, h='#d6cff2', expr='happy', look=(1, 0.3) if t < t1 else (0.8, -0.8))
        if taste > 0:
            for i in range(3):
                heart_icon(c, 700 + i * 40, 560 - 30 * osc(t, 0.8, i), 18, '#ff3d6e', taste)
            info_pill(c, 760, 330, 'LIKING: YES', 'still enjoys sugar', '#2bd17e', taste)
        if t > t1:
            kk = ramp(t, t1, t1 + 0.5)
            info_pill(c, 1500, 330, 'WANTING: NO', "won't go get more", '#ff3d6e', kk)
            text(c, 'zzz', 760, 600 - 20 * osc(t, 0.5), 50, '#ffffff', kk, weight=900)
        meter(c, 120, 980, 420, 0.08, '#ffd23f', 'DOPAMINE', ramp(t, 0.3, 0.8))
    else:
        # boosted dopamine: frantic running, same smile
        for i in range(6):
            sugar(c, 1350 + (i % 3) * 90, 800 - (i // 3) * 85, 0.9)
        run = t * 4
        x = 900 + 300 * math.sin(run * 0.5)
        mouse_char(c, x, 780 + 12 * abs(math.sin(run * 3)), 1.15, t * 3, h='#d6cff2', look=(1 if math.cos(run * 0.5) > 0 else -1, 0))
        for i in range(4):
            line(c, [(x - 260 - i * 40, 720 + i * 25), (x - 180 - i * 40, 720 + i * 25)], 8, '#ffffff', 0.6)
        info_pill(c, 600, 300, 'WANTING: WAY UP', '', '#ffd23f', ramp(t, 1.5, 2.0))
        info_pill(c, 1300, 300, 'LIKING: SAME', '', '#2bd1ff', ramp(t, 3.5, 4.0))
        meter(c, 120, 980, 420, 0.95, '#ffd23f', 'DOPAMINE', ramp(t, 0.3, 0.8))


def s_spotlight(c, t, d, p, b):
    bg_grad(c, '#1a0b4a', '#0a0420')
    # spotlight beam
    k = eout(ramp(t, 0.4, 1.4))
    beam = skia.Path()
    beam.moveTo(860, -20)
    beam.lineTo(1060, -20)
    beam.lineTo(1260 + 0 * k, 980)
    beam.lineTo(660, 980)
    beam.close()
    pnt = skia.Paint(AntiAlias=True)
    pnt.setShader(lin((0, 0), (0, 980), ['#fff3c4', '#ffd23f']))
    pnt.setAlphaf(0.28 * k)
    c.drawPath(beam, pnt)
    ellipse(c, 960, 980, 320, 50, '#ffd23f', 0.35 * k)
    phone(c, 960, 640, 0.9, t, glow_c='#ffd23f', scroll=1.2)
    # brain watching from the side, hypnotised
    brain(c, 380, 560, 0.75, t, expr='dazed', look=(1, 0.3))
    t1 = bt(b, 1, 4)
    kk = pop(t, t1)
    if kk > 0:
        c.save()
        c.translate(1500, 360)
        c.rotate(-6 + 3 * osc(t, 2))
        text(c, 'THIS!', 0, 0, 130 * kk + 1, '#ffd23f', clamp01(kk), weight=900)
        text(c, 'MORE!', 0, 140, 110 * pop(t, t1 + 0.6) + 1, '#ff3d6e', clamp01(pop(t, t1 + 0.6)), weight=900)
        c.restore()
    for i in range(10):
        dopa(c, 960 + math.cos(t + i) * 360, 600 + math.sin(t * 1.3 + i) * 260, 1.2, 0.8 * k)


# ------------------------------------------------------------------ chapter 2: birds
def egg(c, x, y, s, h='#e8dcc0', spots='#6a5a3a', a=1.0, rot=0.0, bold=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    path = skia.Path()
    path.addOval(skia.Rect(-40 * s, -55 * s, 40 * s, 45 * s))
    shaded(c, path, h, a, dark=-0.18)
    rng = np.random.default_rng(int(s * 10) + 3)
    for i in range(7):
        circle(c, (rng.random() - 0.5) * 55 * s, (rng.random() - 0.5) * 70 * s, (4 + 5 * rng.random() + 6 * bold) * s, spots, a * 0.9)
    c.restore()


def bird(c, x, y, s, t, expr='happy', look=(1, 0), flap=0.0, sit=False):
    """Original chubby shorebird: black back, white belly, long orange beak, pink legs."""
    if not sit:
        for sg in (-1, 1):
            line(c, [(x + sg * 22 * s, y + 60 * s), (x + sg * 26 * s, y + 140 * s)], 7 * s, '#ff8fb3')
    body = smooth_path([(x - 120 * s, y - 10 * s), (x - 40 * s, y - 80 * s), (x + 70 * s, y - 70 * s), (x + 110 * s, y),
                        (x + 50 * s, y + 70 * s), (x - 70 * s, y + 60 * s)], k=0.6)
    shaded(c, body, '#2a2440')
    belly = smooth_path([(x - 60 * s, y + 10 * s), (x + 20 * s, y - 10 * s), (x + 95 * s, y + 10 * s), (x + 40 * s, y + 65 * s),
                         (x - 50 * s, y + 55 * s)], k=0.6)
    c.drawPath(belly, P('#f4f2ff'))
    # wing
    c.save()
    c.translate(x - 10 * s, y - 10 * s)
    c.rotate(-20 * flap * osc(t, 3))
    wing = smooth_path([(0, 0), (-90 * s, -20 * s), (-110 * s, 30 * s), (-30 * s, 40 * s)], k=0.5)
    c.drawPath(wing, P('#3a3458'))
    c.restore()
    # head
    hx, hy = x + 80 * s, y - 90 * s
    circle(c, hx, hy, 52 * s, '#2a2440')
    sg = 1 if look[0] >= 0 else -1
    beak = skia.Path()
    beak.moveTo(hx + sg * 35 * s, hy - 6 * s)
    beak.lineTo(hx + sg * 140 * s, hy + 6 * s)
    beak.lineTo(hx + sg * 35 * s, hy + 16 * s)
    beak.close()
    c.drawPath(beak, P('#ff7a1a'))
    eye(c, hx + sg * 12 * s, hy - 12 * s, 17 * s, look=look, lid=0.0 if expr != 'dazed' else 0.5, lid_col='#2a2440', white='#ffffff')
    circle(c, hx + sg * 12 * s, hy - 12 * s, 19 * s, '#ff3d2e', 0.0)


def nest(c, x, y, s):
    ellipse(c, x, y, 150 * s, 40 * s, '#8a5a2a')
    for i in range(12):
        an = i / 12 * math.pi
        line(c, [(x - 150 * s + i * 25 * s, y - 10 * s), (x - 120 * s + i * 25 * s, y + 25 * s)], 5 * s, '#c08a4a', 0.8)


def s_birds(c, t, d, p, b):
    stage = p.get('stage', 'offer')
    bg_grad(c, '#7cf2e8', '#2b7bd6', '#4fc8e0')
    for i in range(4):
        x = (i * 600 + t * 30) % 2400 - 200
        blob(c, x, 160 + i * 40, 70, '#ffffff', 0.8, seed=i, sx=2.2, sy=0.8)
    c.drawRect(skia.Rect(0, 860, W, H), P('#f2d39a'))
    for i in range(18):
        circle(c, (i * 113) % W, 900 + (i * 37) % 160, 6, '#e0b878')
    t1 = bt(b, 1, 3)
    if stage == 'offer':
        nest(c, 640, 860, 1.2)
        for i in range(3):
            egg(c, 560 + i * 80, 820, 0.8)
        bird(c, 560, 700, 1.1, t, look=(1, 0.3) if t < t1 else (1, 0))
        # scientist hand / brush painting a bigger egg
        k = ramp(t, t1, t1 + 1.0)
        if k > 0:
            sz = 0.8 + 1.0 * eout(k)
            egg(c, 1300, 860 - 45 * sz, sz, h=mix('#e8dcc0', '#bfe0ff', k), spots=mix('#6a5a3a', '#1d1238', k), bold=k)
            ang = 20 * osc(t, 1.5)
            c.save()
            c.translate(1450, 600)
            c.rotate(ang)
            rrect(c, -10, -160, 20, 180, 10, '#c0703d')
            rrect(c, -14, 10, 28, 40, 8, '#2a1640')
            c.restore()
            person(c, 1680, 1150, 1.4, dict(skin='#f2c29b', hair='#e8e0d0', style='short', shirt='#f4f2ff'), expr='happy', t=t,
                   arms=('point', 'down'), look=(-0.8, 0))
            info_pill(c, 1300, 240, 'BIGGER. BOLDER.', '', '#ffd23f', ramp(t, t1 + 1.2, t1 + 1.7))
        k0 = pop(t, 0.6)
        info_pill(c, 380, 230, '1950s', 'NIKO TINBERGEN', '#2bd1ff', k0 * (1 - ramp(t, t1 + 1.0, t1 + 1.4)))
    else:
        # bird abandons real eggs, sits (and slides) on a giant egg
        nest(c, 400, 860, 1.0)
        for i in range(3):
            egg(c, 330 + i * 70, 830, 0.7)
        if t > t1 + 0.5:
            glow(c, 400, 800, 160, '#ff3d6e', 0.25)
            text(c, 'ignored...', 400, 700, 44, '#1d1238', ramp(t, t1 + 0.5, t1 + 1.0), weight=800, shadow=0)
        egg(c, 1150, 760, 2.6, h='#bfe0ff', spots='#1d1238', bold=1.0)
        slide = (t * 0.45) % 1.0
        on = slide < 0.7
        bx = 1150 + (0 if on else 220 * eio((slide - 0.7) / 0.3))
        by = 520 + (0 if on else 260 * eio((slide - 0.7) / 0.3) ** 2)
        bird(c, bx - 40, by, 1.0, t, look=(-1, 0.4), flap=1.0 if not on else 0.2, sit=True)
        k = pop(t, 0.5)
        text(c, 'THE FAKE WINS', 1150, 200, 100 * k + 1, '#ffffff', clamp01(k), weight=900)


def s_super_card(c, t, d, p, b):
    bg_radial(c, (960, 560), '#2b7bd6', '#0e1a4a', 1200)
    particles(c, t, seed=331, n=40, a=0.3)
    t1, t2 = bt(b, 1, 4), bt(b, 2, 9)
    if t < t2:
        # rule: bigger + brighter = better
        egg(c, 600, 640, 1.2)
        text(c, '<', 840, 680, 140, '#ffffff', 1, weight=900)
        egg(c, 1200, 640 - 20, 2.4, h='#bfe0ff', spots='#1d1238', bold=1.0)
        k = pop(t, 0.4)
        text(c, 'BIGGER + BRIGHTER = BETTER', 960, 220, 72 * k + 1, '#ffd23f', clamp01(k), weight=900)
        if t > t1:
            kk = ramp(t, t1, t1 + 0.4)
            info_pill(c, 520, 930, 'NATURE: IT WORKS', '', '#2bd17e', kk)
            info_pill(c, 1400, 930, 'PAINTBRUSH: OOPS', '', '#ff3d6e', ramp(t, t1 + 2.0, t1 + 2.4))
    else:
        k = pop(t, t2 + 0.1)
        text(c, 'SUPERNORMAL', 960, 400, 150 * k + 1, '#ffffff', clamp01(k), weight=900)
        text(c, 'STIMULUS', 960, 560, 150 * pop(t, t2 + 0.4) + 1, '#ffd23f', clamp01(pop(t, t2 + 0.4)), weight=900)
        text(c, 'an exaggerated version of what we are built to chase', 960, 680, 42, '#ffffff', ramp(t, t2 + 1.5, t2 + 2.2), weight=700)
        for i in range(8):
            an = i / 8 * 6.28 + t * 0.4
            egg(c, 960 + math.cos(an) * 760, 520 + math.sin(an) * 420, 0.6 + 0.3 * (i % 2), h='#bfe0ff', spots='#1d1238', bold=1,
                rot=math.degrees(an))


def s_phone_egg(c, t, d, p, b):
    bg_radial(c, (960, 560), '#b8326a', '#1a0838', 1200)
    k = back(ramp(t, 0.2, 1.0))
    c.save()
    c.translate(960, 600)
    c.scale(1 + 0.03 * osc(t, 1.2), 1 + 0.03 * osc(t, 1.2))
    c.translate(-960, -600)
    phone(c, 960, 600, 1.35 * k, t, glow_c='#ff3d8b', scroll=1.4)
    c.restore()
    bird(c, 350, 760, 0.9, t, expr='dazed', look=(1, -0.4))
    brain(c, 1600, 560, 0.5, t, expr='dazed', look=(-1, 0.2))
    t1 = bt(b, 1, 5)
    items = ['ENDLESS NOVELTY', 'PERFECT-LOOKING', 'ZERO REJECTION', 'ON DEMAND']
    for i, s_ in enumerate(items):
        kk = pop(t, t1 + 0.1 + i * 0.85)
        if kk > 0:
            x = 420 if i % 2 == 0 else 1500
            y = 200 if i < 2 else 960
            info_pill(c, x, y, s_, '', HEARTS[i], kk)


# ------------------------------------------------------------------ chapter 3
def s_coolidge(c, t, d, p, b):
    bg_grad(c, '#ff9ad5', '#7b2bd1')
    particles(c, t, seed=341, n=40, a=0.35)
    c.drawRect(skia.Rect(0, 840, W, H), P('#5a1a8a'))
    t1, t2 = bt(b, 1, 2), bt(b, 2, 9)
    newk = ramp(t, t1 + 4.5, t1 + 5.5)
    perk = ramp(t, t1 + 5.6, t1 + 6.1)
    # male rat: bored (yawning) then perks up
    mouse_char(c, 600, 780, 1.2, t, h='#c9c3e6', expr='dazed' if perk < 0.5 else 'happy', look=(1, 0.5) if perk < 0.5 else (1, -0.2),
               sniff=perk)
    if perk < 0.5 and t > t1 + 1:
        text(c, 'meh.', 700, 520, 56, '#ffffff', ramp(t, t1 + 1, t1 + 1.5), weight=900)
    # first female rat walks away bored
    mouse_char(c, lerp(1000, 1300, ramp(t, t1, t1 + 3)), 790, 1.0, t, h='#e6c3d6', look=(1, 0))
    # new rat arrives with sparkles
    if newk > 0:
        x = lerp(2200, 1200, eout(newk))
        glow(c, x, 760, 220, '#ffd23f', 0.5 * newk)
        mouse_char(c, x, 790, 1.0, t, h='#ffd6a8', look=(-1, 0))
        text(c, 'NEW!', x, 560, 70 * newk + 1, '#ffd23f', newk, weight=900)
    if perk > 0:
        for i in range(6):
            ph = (t * 0.6 + i * 0.17) % 1
            heart_icon(c, 640 + (i - 3) * 50, 600 - ph * 260, 22, HEARTS[i % 4], perk * (1 - ph))
    kk = pop(t, t2 + 0.2)
    if kk > 0:
        info_pill(c, 960, 220, 'THE COOLIDGE EFFECT', 'novelty revives interest', '#ffd23f', kk)


def s_tabs(c, t, d, p, b):
    bg_grad(c, '#1d1150', '#0a0420')
    t1 = bt(b, 1, 3)
    n = int(1 + 30 * eio(ramp(t, t1, d)))
    rng = np.random.default_rng(7)
    for i in range(n):
        x = 160 + rng.random() * 1400
        y = 140 + rng.random() * 660
        w, h = 360, 230
        k = pop(t, t1 + i * (d - t1) / 32)
        if k <= 0:
            continue
        c.save()
        c.translate(x + w / 2, y + h / 2)
        c.scale(k, k)
        rrect(c, -w / 2, -h / 2, w, h, 18, '#f4f2ff')
        rrect(c, -w / 2, -h / 2, w, 40, 18, HOLI[i % 6])
        for j in range(3):
            circle(c, -w / 2 + 24 + j * 22, -h / 2 + 20, 7, '#ffffff', 0.8)
        pp = skia.Paint(AntiAlias=True)
        pp.setShader(lin((0, -h / 2 + 50), (0, h / 2 - 10), ['#ff3d8b', '#9d5cff']))
        c.drawRoundRect(skia.Rect(-w / 2 + 12, -h / 2 + 52, w / 2 - 12, h / 2 - 12), 12, 12, pp)
        tri = skia.Path()
        tri.moveTo(-18, -10)
        tri.lineTo(-18, 40)
        tri.lineTo(26, 15)
        tri.close()
        c.drawPath(tri, P('#ffffff', 0.9))
        c.restore()
        # dopamine spark for every new tab
        if 0 < t - (t1 + i * (d - t1) / 32) < 0.6:
            dopa(c, x + w / 2, y - 20, 2.0, 1 - (t - (t1 + i * (d - t1) / 32)) / 0.6)
    if t < t1 + 0.5:
        k = pop(t, 0.3)
        brain(c, 960, 520, 1.1, t, expr='curious', look=(0.4, -0.2), glow_c='#ffd23f', glow_a=0.4 * k)
        text(c, 'NEW = DOPAMINE', 960, 960, 80 * k + 1, '#ffd23f', clamp01(k), weight=900)
    else:
        rrect(c, 1540, 900, 340, 120, 30, '#ffffff', 0.95)
        text(c, f'{n} TABS', 1710, 980, 64, '#1b0f45', weight=900, shadow=0)


def s_habituation(c, t, d, p, b):
    bg_grad(c, '#3a1a7a', '#120838')
    particles(c, t, seed=351, n=30, a=0.25)
    x0, y0, w, h = 220, 860, 1100, 560
    line(c, [(x0, y0 - h), (x0, y0), (x0 + w, y0)], 6, '#ffffff')
    text(c, 'EXCITEMENT', x0 - 20, y0 - h - 20, 32, '#ffffff', weight=800, align='left', shadow=0)
    text(c, 'SAME THING, AGAIN AND AGAIN →', x0 + w / 2, y0 + 60, 32, '#ffffff', weight=800, shadow=0)
    t1, t2 = bt(b, 1, 3), bt(b, 2, 6)
    nbars = int(8 * ramp(t, 0.4, t2))
    for i in range(nbars):
        v = 0.95 * (0.72 ** i)
        bh = h * v
        k = eout(ramp(t, 0.4 + i * (t2 - 0.4) / 8, 0.8 + i * (t2 - 0.4) / 8))
        x = x0 + 40 + i * 130
        rrect(c, x, y0 - bh * k, 90, bh * k + 2, 16, mix('#ffd23f', '#7a6ad0', i / 7))
    if t > t2:
        kk = pop(t, t2 + 0.2)
        # staircase on the right
        for i, s_ in enumerate(['MORE TABS', 'MORE EXTREME', 'MORE TIME']):
            k2 = pop(t, t2 + 0.5 + i * 1.0)
            if k2 > 0:
                x, y = 1340 + i * 90, 800 - i * 220
                rrect(c, x, y, 380, 120, 20, ['#ff7a1a', '#ff3d6e', '#b8326a'][i], clamp01(k2))
                text(c, s_, x + 190, y + 74, 36 * k2 + 1, '#ffffff', clamp01(k2), weight=900, shadow=0)
        text(c, 'for some people:', 1580, 150, 40, '#ffffff', clamp01(kk), weight=800)


def s_scan(c, t, d, p, b):
    bg_radial(c, (640, 520), '#14507a', '#081a33', 1200)
    particles(c, t, seed=361, n=40, a=0.3)
    k = ramp(t, 1.0, 1.8)
    brain(c, 640, 470, 1.4, t, regions={'basal': k * (0.85 + 0.15 * osc(t, 1.2))})
    label(c, 'CAUDATE (REWARD SYSTEM)', 640, 990, 640, 420, a=ramp(t, 1.4, 1.9), size=36)
    # scanner ring
    c.drawCircle(640, 470, 470 + 10 * osc(t, 0.5), P('#4fd8ff', 0.5, stroke=10))
    ky = pop(t, 0.5)
    if ky > 0:
        info_pill(c, 1480, 220, '2014 · 64 MEN', 'brain scans', '#4fd8ff', ky)
    t1 = bt(b, 1, 9)
    kc = ramp(t, 5.0, 5.6)
    if kc > 0:
        rrect(c, 1180, 380, 600, 160, 30, '#ffffff', kc)
        text(c, 'MORE HOURS / WEEK', 1480, 450, 44, '#1b0f45', kc, weight=900, shadow=0)
        text(c, '↔ SMALLER CAUDATE', 1480, 510, 44, '#d1366b', kc, weight=900, shadow=0)
    if t > t1:
        ka = ramp(t, t1 + 0.6, t1 + 1.1)
        # cause/effect arrows both ways
        for i, (txt, y) in enumerate([('PORN → BRAIN?', 700), ('BRAIN → PORN?', 860)]):
            kk = ramp(t, t1 + 1.5 + i * 1.8, t1 + 2.0 + i * 1.8)
            info_pill(c, 1480, y, txt, '', ['#ffd23f', '#ff3d6e'][i], kk)
        text(c, 'CORRELATION ONLY', 1480, 1010, 40, '#ffffff', ka, weight=900)


# ------------------------------------------------------------------ chapter 4
def s_who_file(c, t, d, p, b):
    bg_grad(c, '#2a1a6e', '#0e0628')
    particles(c, t, seed=371, n=30, a=0.25)
    t1, t2, t3 = bt(b, 1, 4), bt(b, 2, 10), bt(b, 3, 15)
    if t < t1:
        # two scientists arguing
        k = pop(t, 0.3)
        for i, (x, ex, col_) in enumerate([(640, 'think', '#2bd1ff'), (1280, 'curious', '#ff7a1a')]):
            person(c, x, 1000, 1.3, dict(skin=SKINS[i * 3], hair='#22122e', style=['short', 'bun'][i], shirt='#f4f2ff'),
                   expr=ex, t=t, arms=('point', 'down') if i == 0 else ('down', 'point'), look=(1 - 2 * i, 0))
            rrect(c, x - 140 + (1 - 2 * i) * 60, 260, 280, 110, 55, '#ffffff', clamp01(k))
            text(c, ['ADDICTION!', 'NOT SO FAST!'][i], x + (1 - 2 * i) * 60, 330, 40, col_, clamp01(k), weight=900, shadow=0)
        return
    # ICD book + cabinet
    kb = pop(t, t1)
    c.save()
    c.translate(520, 560)
    c.scale(clamp01(kb), clamp01(kb))
    rrect(c, -220, -280, 440, 560, 26, '#2bd1ff')
    rrect(c, -200, -260, 30, 520, 10, '#1f8ab0')
    text(c, 'ICD-11', 20, -120, 90, '#ffffff', weight=900, shadow=0.3)
    text(c, 'WHO · 2019', 20, -50, 40, '#0b3b5a', weight=900, shadow=0)
    circle(c, 20, 110, 90, '#ffffff', 0.9)
    text(c, 'WHO', 20, 132, 60, '#1f8ab0', weight=900, shadow=0)
    c.restore()
    # file card
    kf = ramp(t, t1 + 0.8, t1 + 1.4)
    drawers = [('ADDICTIONS', '#ff3d6e'), ('IMPULSE CONTROL', '#2bd17e')]
    for i, (name, colr) in enumerate(drawers):
        y = 340 + i * 260
        rrect(c, 1180, y, 600, 220, 24, '#4a3a9a')
        rrect(c, 1210, y + 30, 540, 160, 18, '#5a4ab0')
        rrect(c, 1290, y + 80, 380, 60, 30, colr)
        text(c, name, 1480, y + 120, 32, '#ffffff', weight=900, shadow=0)
    fy = 560
    fx = 900
    if t > t3:
        km = eio(ramp(t, t3 + 1.2, t3 + 2.6))
        fx, fy = lerp(900, 1480, km), lerp(560, 620 + 70, km)
    if kf > 0 and not (t > t3 + 2.6):
        c.save()
        c.translate(fx, fy)
        c.rotate(-6)
        c.scale(back(kf), back(kf))
        rrect(c, -260, -110, 520, 220, 18, '#ffe9a8')
        rrect(c, -260, -150, 200, 60, 14, '#ffe9a8')
        text(c, 'COMPULSIVE SEXUAL', 0, -20, 38, '#3a1d10', weight=900, shadow=0)
        text(c, 'BEHAVIOUR DISORDER', 0, 30, 38, '#3a1d10', weight=900, shadow=0)
        text(c, '6C72', 0, 80, 30, '#8a5a2a', weight=800, shadow=0)
        c.restore()
    if t > t2:
        kd = ramp(t, t2, t2 + 0.5) * (1 - ramp(t, t3 - 0.2, t3 + 0.2))
        info_pill(c, 960, 960, "CAN'T CONTROL URGES + REAL HARM", '', '#ff7a1a', kd)
    if t > t3 + 2.4:
        kk = pop(t, t3 + 2.4)
        line(c, [(1790, 690), (1815, 718), (1860, 660)], 16, '#2bd17e', clamp01(kk))
        text(c, '(for now)', 1480, 1000, 44, '#ffffff', clamp01(kk), weight=800)


def s_pct(c, t, d, p, b):
    bg_radial(c, (960, 500), '#3a1d8f', '#0c0628', 1200)
    particles(c, t, seed=381, n=30, a=0.25)
    for gi, (x0, n_hl, colr, name) in enumerate([(220, 10, '#2bd1ff', 'MEN'), (1060, 7, '#ff4fa3', 'WOMEN')]):
        for i in range(100):
            r, cidx = divmod(i, 10)
            x = x0 + cidx * 66 + 40
            y = 330 + r * 62
            k = pop(t, 0.3 + gi * 0.3 + i * 0.008, 0.35)
            hl = i < n_hl and t > 2.0 + gi * 1.2
            if k > 0:
                mini_person(c, x, y + 30, 0.95 * k, colr if hl else '#5a4b8a', 1.0, head=SKINS[i % 6])
        kk = pop(t, 2.0 + gi * 1.2)
        text(c, f'~{n_hl}%', x0 + 340, 250, 110 * kk + 1, colr, clamp01(kk), weight=900)
        text(c, name, x0 + 340, 1000, 52, '#ffffff', ramp(t, 0.5, 1.0), weight=900)
    text(c, 'distress about controlling sexual urges', 960, 1060, 34, '#e9e3ff', ramp(t, 3.5, 4.2), weight=700)


def s_shame(c, t, d, p, b):
    t1, t2, t3 = bt(b, 1, 2), bt(b, 2, 9), bt(b, 3, 12)
    bg_grad(c, '#3a1d6e', '#0e0628')
    particles(c, t, seed=391, n=30, a=0.25)
    # balance-ish two sliders
    k1 = ramp(t, t1 + 0.5, t1 + 1.0)
    if k1 > 0:
        meter(c, 1080, 360, 700, 0.35, '#2bd1ff', 'HOW MUCH THEY WATCH', k1)
        k2 = ramp(t, t2, t2 + 0.5)
        meter(c, 1080, 520, 700, 0.35 + 0.55 * eio(ramp(t, t2 + 0.3, t2 + 1.8)), '#ff3d6e', 'HOW WRONG THEY THINK IT IS', k2)
        info_pill(c, 1430, 760, 'FEELING "ADDICTED"', 'linked to both', '#ffd23f', ramp(t, t2 + 1.8, t2 + 2.3))
    # person with shame cloud growing
    cloud = 0.4 + 0.9 * eio(ramp(t, t2, t3 + 2))
    person(c, 560, 1000, 1.35, dict(skin='#b77a50', hair='#160b1c', style='spiky', shirt='#7b5cff'),
           expr='sad' if t > t2 else 'neutral', t=t, arms=('face', 'down') if t > t3 else ('down', 'down'), look=(0, 0.4))
    blob(c, 560, 330, 150 * cloud, '#2a2440', 0.9, seed=3, t=t, sx=1.5, sy=0.8)
    for i in range(3):
        blob(c, 460 + i * 100, 330 + 40 * cloud, 60 * cloud, '#2a2440', 0.9, seed=i, t=t)
    text(c, 'SHAME', 560, 345, 56 * cloud, '#ff9ab8', clamp01(cloud), weight=900, shadow=0)
    if t > t3:
        # loop arrow
        kl = ramp(t, t3 + 0.6, t3 + 1.4)
        path = skia.Path()
        path.addArc(skia.Rect(260, 520, 860, 760), 200, 320 * kl)
        c.drawPath(path, P('#ff3d6e', 0.8, stroke=14))
        text(c, 'THE LOOP', 560, 860, 50, '#ff3d6e', kl, weight=900)


def s_mixed(c, t, d, p, b):
    bg_grad(c, '#2a1050', '#0c0628')
    particles(c, t, seed=401, n=30, a=0.25)
    t1, t2 = bt(b, 1, 3), bt(b, 2, 7)
    k0 = pop(t, 0.3)
    text(c, 'SCARY HEADLINES?', 960, 200, 90 * k0 + 1, '#ffffff', clamp01(k0), weight=900)
    for i, (x, title_, tt, flat) in enumerate([(520, 'HOW OFTEN THEY WATCH', t1 + 1.6, True), (1400, 'FEELING OUT OF CONTROL', t2 + 0.3, False)]):
        k = ramp(t, tt - 0.5, tt)
        if k <= 0:
            continue
        rrect(c, x - 380, 320, 760, 560, 30, '#ffffff', 0.08 * k)
        text(c, title_, x, 400, 40, '#ffffff', k, weight=900)
        x0, y0, w, h = x - 300, 820, 600, 340
        line(c, [(x0, y0 - h), (x0, y0), (x0 + w, y0)], 5, '#ffffff', k)
        rng = np.random.default_rng(i)
        for j in range(26):
            px = rng.random()
            py = (0.45 + (rng.random() - 0.5) * 0.6) if flat else (0.15 + 0.7 * px + (rng.random() - 0.5) * 0.25)
            kk = ramp(t, tt + j * 0.03, tt + 0.2 + j * 0.03)
            circle(c, x0 + 20 + px * (w - 40), y0 - py * h, 9, '#2bd1ff' if flat else '#ff3d6e', kk)
        kl = ramp(t, tt + 1.0, tt + 1.6)
        if flat:
            line(c, [(x0 + 20, y0 - 0.45 * h), (x0 + 20 + (w - 40) * kl, y0 - 0.45 * h)], 6, '#2bd1ff', 0.8)
            text(c, 'NO CLEAR LINK', x, 950, 46, '#2bd1ff', kl, weight=900)
        else:
            line(c, [(x0 + 20, y0 - 0.15 * h), (x0 + 20 + (w - 40) * kl, y0 - (0.15 + 0.7 * kl) * h)], 6, '#ff3d6e', 0.8)
            text(c, 'CONNECTED', x, 950, 46, '#ff3d6e', kl, weight=900)


def s_teen12(c, t, d, p, b):
    bg_grad(c, '#ff9a4d', '#7b2bd1', '#d1366b')
    particles(c, t, seed=411, n=40, h='#fff3c4', a=0.4)
    t1 = bt(b, 1, 3)
    # birthday cake with "12"
    k = back(ramp(t, t1, t1 + 0.7))
    c.save()
    c.translate(700, 760)
    c.scale(clamp01(k) + 0.0001, clamp01(k) + 0.0001)
    rrect(c, -260, -60, 520, 220, 30, '#ff7eb6')
    rrect(c, -220, -220, 440, 180, 30, '#ffd6e8')
    for i in range(7):
        circle(c, -200 + i * 66, -60, 26, '#ffffff')
    for i, ch in enumerate('12'):
        rrect(c, -80 + i * 110, -400, 70, 180, 20, '#2bd1ff')
        text(c, ch, -45 + i * 110, -290, 120, '#ffffff', weight=900, shadow=0.3)
        fy = -430 + 6 * osc(t, 5, i)
        glow(c, -45 + i * 110, fy, 60, '#ffd23f', 0.7)
        ellipse(c, -45 + i * 110, fy, 16, 26, '#ffb02e')
    c.restore()
    phone(c, 1350, 560, 0.85, t, glow_c='#ff3d8b', scroll=1.0, ang=8)
    kk = ramp(t, t1 + 0.9, t1 + 1.4)
    text(c, 'AVERAGE AGE OF FIRST EXPOSURE', 960, 150, 54, '#ffffff', kk, weight=900)
    if t < t1:
        k0 = pop(t, 0.4)
        info_pill(c, 960, 500, 'HOW EARLY?', '', '#ffd23f', k0)


# ------------------------------------------------------------------ chapter 5
def junk_food(c, x, y, s):
    rrect(c, x - 60 * s, y - 90 * s, 120 * s, 160 * s, 20 * s, '#ff3d2e')
    rrect(c, x - 60 * s, y - 90 * s, 120 * s, 40 * s, 20 * s, '#ffd23f')
    for i in range(5):
        rrect(c, x - 50 * s + i * 22 * s, y - 150 * s, 14 * s, 80 * s, 6 * s, '#ffd23f')
    text(c, 'M', x, y + 20 * s, 60 * s, '#ffd23f', weight=900, shadow=0)


def s_not_evil(c, t, d, p, b):
    bg_grad(c, '#ffd23f', '#d1366b', '#ff8a3d')
    particles(c, t, seed=421, n=40, a=0.4)
    t1, t2 = bt(b, 1, 3), bt(b, 2, 7)
    k = pop(t, 0.3)
    ph_x = 960 if t < t1 else lerp(960, 1400, eio(ramp(t, t1, t1 + 0.8)))
    phone(c, ph_x, 600, 1.0 * clamp01(k), t, glow_c='#ff3d8b')
    fall = ramp(t, t1 - 1.6, t1 - 0.6)
    for sg in (-1, 1):
        hx = ph_x + sg * 100 + sg * 200 * fall
        hy = 320 + 700 * fall ** 2
        path = skia.Path()
        path.moveTo(hx - 34, hy + 20)
        path.quadTo(hx + sg * 10, hy - 50, hx + sg * 40, hy - 90)
        path.quadTo(hx + sg * 20, hy - 20, hx + 34, hy + 20)
        path.close()
        c.drawPath(path, P('#e0203a', clamp01(k)))
    if t < t1:
        text(c, 'PURE EVIL?', 960, 170, 110 * k + 1, '#ffffff', clamp01(k), weight=900)
        kk = pop(t, t1 - 1.4)
        if kk > 0:
            text(c, 'NOT EXACTLY.', 960, 1000, 80 * kk + 1, '#1b0f45', clamp01(kk), weight=900, shadow=0)
        return
    # same family: junk food + endless feed
    ka = pop(t, t1 + 0.3)
    c.save()
    c.translate(520, 640)
    c.scale(clamp01(ka) * 1.5, clamp01(ka) * 1.5)
    junk_food(c, 0, 0, 1.0)
    c.restore()
    phone(c, 960, 620, 0.7 * clamp01(pop(t, t1 + 0.8)), t * 2, glow_c='#2bd1ff', scroll=2.5)
    if t > t2:
        kk = ramp(t, t2, t2 + 0.6)
        text(c, 'ENGINEERED TO BE', 960, 160, 70, '#ffffff', kk, weight=900)
        text(c, '"MORE THAN NATURE"', 960, 250, 70, '#1b0f45', kk, weight=900, shadow=0)
        egg(c, 1720, 860, 1.6 * clamp01(kk), h='#bfe0ff', spots='#1d1238', bold=1)


def s_signs(c, t, d, p, b):
    bg_grad(c, '#2bd1c4', '#1d3a8f')
    particles(c, t, seed=431, n=40, a=0.35)
    k = pop(t, 0.3)
    rrect(c, 420, 140, 1080, 800, 40, '#ffffff', clamp01(k))
    rrect(c, 420, 140, 1080, 130, 40, '#ffd23f', clamp01(k))
    text(c, 'WARNING SIGNS', 960, 230, 76, '#1b0f45', clamp01(k), weight=900, shadow=0)
    items = ["Tried to cut down. Can't.", 'Eats time meant for other things.', 'Feel worse after, not better.']
    for i, s_ in enumerate(items):
        tt = bt(b, i + 1, 2 + i * 2)
        kk = ramp(t, tt, tt + 0.4)
        y = 400 + i * 180
        rrect(c, 500, y - 50, 80, 80, 18, '#f0ecff', clamp01(k))
        if kk > 0:
            line(c, [(515, y - 10), (538, y + 15), (575, y - 35)], 14, '#ff3d6e', kk)
        text(c, s_, 620, y + 12, 50, '#1b0f45', kk, weight=800, align='left', shadow=0)


def s_tips(c, t, d, p, b):
    bt1, bt2, bt3, bt4 = bt(b, 1, 3), bt(b, 2, 6), bt(b, 3, 9), bt(b, 4, 12)
    if t < bt2:
        room(c, t, 0, 0)
        # bedroom door, phone charging outside
        rrect(c, 1240, 300, 280, 560, 16, '#5a3a8a')
        circle(c, 1480, 590, 14, '#ffd23f')
        rrect(c, 1540, 700, 300, 40, 12, '#8a6ad0')
        k = ramp(t, bt1, bt1 + 1.0)
        px = lerp(900, 1690, eio(k))
        phone(c, px, 620 - 80 * math.sin(math.pi * k), 0.3, t, glow_c='#2bd1ff')
        if k >= 1:
            line(c, [(1690, 700), (1690, 740), (1800, 740), (1800, 860)], 6, '#ffffff', 0.8)
        person(c, 700, 1000, 1.2, dict(skin='#d99a6c', hair='#22122e', style='short', shirt='#ff6f59'), expr='calm' if k >= 1 else 'neutral',
               t=t, arms=('down', 'point' if 0 < k < 1 else 'down'), look=(1, 0))
        info_pill(c, 600, 200, 'PHONE OUT OF THE BEDROOM', '', '#2bd1ff', ramp(t, bt1 + 0.3, bt1 + 0.8))
        return
    if t < bt3:
        bg_grad(c, '#7b2bd1', '#1d1150')
        person(c, 960, 1000, 1.3, dict(skin='#b77a50', hair='#160b1c', style='bun', shirt='#2bd17e'), expr='think', t=t,
               arms=('face', 'down'), look=(0, -0.6))
        for i, (s_, colr) in enumerate([('BOREDOM', '#ffd23f'), ('STRESS', '#ff3d6e'), ('LONELINESS', '#2bd1ff')]):
            kk = pop(t, bt2 + 0.8 + i * 0.6)
            an = math.pi * (1.15 + i * 0.35)
            x, y = 960 + math.cos(an) * 520, 460 + math.sin(an) * 280
            if kk > 0:
                blob(c, x, y, 130 * clamp01(kk), '#ffffff', 0.95, seed=i, t=t, sx=1.7, sy=0.8)
                text(c, s_, x, y + 16, 46 * kk + 1, colr, clamp01(kk), weight=900, shadow=0)
        text(c, 'NOTICE YOUR TRIGGERS', 960, 140, 72, '#ffffff', ramp(t, bt2, bt2 + 0.5), weight=900)
        return
    bg_grad(c, '#ffb02e', '#d1366b')
    particles(c, t, seed=441, n=40, h='#fff3c4', a=0.4)
    if t < bt4:
        # swap habit: phone → walk / call friend / gym
        k = ramp(t, bt3, bt3 + 0.6)
        phone(c, 400, 560, 0.6 * (1 - eio(ramp(t, bt3 + 0.8, bt3 + 1.6))), t, glow_c='#ff3d8b')
        text(c, '→', 700, 600, 130, '#ffffff', k, weight=900)
        opts = [('GO FOR A WALK', '#2bd17e'), ('CALL A FRIEND', '#2bd1ff'), ('MOVE YOUR BODY', '#7b5cff')]
        for i, (s_, colr) in enumerate(opts):
            info_pill(c, 1250, 330 + i * 200, s_, '', colr, ramp(t, bt3 + 0.5 + i * 0.5, bt3 + 1.0 + i * 0.5))
        text(c, 'REPLACE, DON\'T JUST FIGHT', 960, 140, 70, '#ffffff', k, weight=900)
        return
    # drop the shame: cloud pops, person lighter
    pk = ramp(t, bt4 + 0.4, bt4 + 1.2)
    person(c, 960, 1000, 1.4, dict(skin='#b77a50', hair='#160b1c', style='spiky', shirt='#7b5cff'),
           expr='sad' if pk < 0.5 else 'happy', t=t, arms=('down', 'down') if pk < 0.5 else ('up', 'up'), look=(0, -0.3))
    if pk < 1:
        blob(c, 960, 330, 150 * (1 - pk) + 1, '#2a2440', 0.9 * (1 - pk), seed=3, t=t, sx=1.5, sy=0.8)
        text(c, 'SHAME', 960, 345, 56 * (1 - pk) + 1, '#ff9ab8', 1 - pk, weight=900, shadow=0)
    else:
        for i in range(10):
            an = i / 10 * 6.28 + t
            circle(c, 960 + math.cos(an) * 260, 330 + math.sin(an) * 130, 10, '#ffffff', 0.8)
    text(c, 'DROP THE SHAME', 960, 140, 80, '#ffffff', ramp(t, bt4, bt4 + 0.5), weight=900)


def s_real(c, t, d, p, b):
    bg_grad(c, '#ff9a4d', '#7b2bd1', '#ff5f8f')
    glow(c, 960, 520, 520, '#ffe08a', 0.6)
    circle(c, 960, 520, 140, '#ffe7a8')
    c.drawPath(smooth_path([(-100, 760), (400, 680), (900, 740), (1400, 660), (2000, 720), (2100, 1200), (-100, 1200)], k=0.5),
               P('#5b1fa8'))
    c.drawRect(skia.Rect(0, 900, W, H), P('#3a1470'))
    # bench
    rrect(c, 620, 790, 680, 34, 14, '#a0522d')
    rrect(c, 620, 700, 680, 30, 14, '#a0522d')
    for x in (660, 1240):
        rrect(c, x, 820, 24, 100, 8, '#7a3a1f')
    t1 = bt(b, 1, 4)
    laugh = t > 1.5
    person(c, 820, 900, 1.15, dict(skin='#d99a6c', hair='#22122e', style='short', shirt='#ff6f59'), expr='laugh' if laugh else 'happy',
           t=t, arms=('down', 'down'), look=(1, 0), sit=True)
    person(c, 1100, 900, 1.15, dict(skin='#f2c29b', hair='#5a2a10', style='long', shirt='#2bd1ff'), expr='happy' if not laugh else 'laugh',
           t=t + 1, arms=('down', 'down'), look=(-1, 0), sit=True, blink_off=1.3)
    # phone face down on bench
    rrect(c, 950, 760, 80, 30, 8, '#1b1030')
    for i in range(8):
        ph = (t * 0.35 + i * 0.125) % 1
        heart_icon(c, 960 + (i - 4) * 40, 600 - ph * 300, 18, HEARTS[i % 4], (1 - ph) * ramp(t, t1, t1 + 1))
    particles(c, t, seed=451, n=40, h='#fff3c4', a=0.45)


SCENES = dict(cave=s_cave, pocket=s_pocket, flat_life=s_flat_life, dopamine=s_dopamine, rats_sugar=s_rats_sugar,
              spotlight=s_spotlight, birds=s_birds, super_card=s_super_card, phone_egg=s_phone_egg, coolidge=s_coolidge,
              tabs=s_tabs, habituation=s_habituation, scan=s_scan, who_file=s_who_file, pct=s_pct, shame=s_shame,
              mixed=s_mixed, teen12=s_teen12, not_evil=s_not_evil, signs=s_signs, tips=s_tips, real=s_real)
