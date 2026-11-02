"""Scenes: intro, chapter 1 (one plant, two lives), chapter 2 (the slow road).
Signature: scene(c, t, d, p, b) -> draws a full 1920x1080 frame. t = local time, d = shot length,
p = params, b = beat times (local start of each narrated sentence)."""
import math

import numpy as np
import skia

from .art import *  # noqa: F401,F403
from . import art as A


def bt(b, i, d=0.0):
    return b[i] if i < len(b) else d


HOLI = ['#ff3d8b', '#ffd23f', '#2bd17e', '#2bd1ff', '#9d5cff', '#ff7a1a']


# ------------------------------------------------------------------ festival
def powder_burst(c, x, y, t, t0, h, s=1.0, seed=0):
    k = t - t0
    if k < 0 or k > 4.5:
        return
    g = eout(k / 1.2)
    a = 1.0 - ramp(k, 2.2, 4.5)
    rng = np.random.default_rng(seed)
    for i in range(7):
        ang = rng.random() * 6.28
        dist = (40 + rng.random() * 120) * s * g
        r = (50 + rng.random() * 70) * s * (0.4 + 0.8 * g)
        blob(c, x + math.cos(ang) * dist, y + math.sin(ang) * dist * 0.7 - k * 18 * s, r, mix(h, '#ffffff', 0.12 * (i % 3)),
             0.75 * a, seed=seed + i, t=k, wob=0.18)
    for i in range(18):
        ang = rng.random() * 6.28
        sp = (150 + rng.random() * 300) * s
        circle(c, x + math.cos(ang) * sp * g, y + math.sin(ang) * sp * g + k * k * 30, (3 + rng.random() * 6) * s, h, a)


def skyline(c, base, colr, seed=2, t=0.0):
    rng = np.random.default_rng(seed)
    x = -60
    path = skia.Path()
    path.moveTo(-60, H)
    while x < W + 60:
        w = 110 + rng.random() * 160
        h = 160 + rng.random() * 220
        top = base - h
        path.lineTo(x, top)
        if rng.random() < 0.35:   # dome
            path.lineTo(x + w * 0.2, top)
            path.quadTo(x + w * 0.5, top - w * 0.55, x + w * 0.8, top)
        elif rng.random() < 0.5:  # chhatri
            path.lineTo(x + w * 0.3, top)
            path.lineTo(x + w * 0.5, top - 40)
            path.lineTo(x + w * 0.7, top)
        path.lineTo(x + w, top)
        x += w
    path.lineTo(W + 60, H)
    path.close()
    c.drawPath(path, P(colr))


def bunting(c, t, y=110, colors=HOLI, sag=60, a=1.0):
    n = 16
    for i in range(n):
        x0 = -40 + i * (W + 80) / n
        x1 = x0 + (W + 80) / n
        k0, k1 = i / n, (i + 1) / n
        y0 = y + sag * 4 * k0 * (1 - k0) + 4 * osc(t, 0.5, i)
        y1 = y + sag * 4 * k1 * (1 - k1) + 4 * osc(t, 0.5, i + 1)
        mx = (x0 + x1) / 2
        path = skia.Path()
        path.moveTo(x0 + 6, y0)
        path.lineTo(x1 - 6, y1)
        path.lineTo(mx + 6 * osc(t, 0.9, i), (y0 + y1) / 2 + 62)
        path.close()
        c.drawPath(path, P(colors[i % len(colors)], a))
    pts = [(-40 + i * (W + 80) / 40, y + sag * 4 * (i / 40) * (1 - i / 40) + 4 * osc(t, 0.5, i * 16 / 40)) for i in range(41)]
    line(c, pts, 3, '#2a0f45', a * 0.8)


def splat_person(c, x, y, s, look_as, seed, **kw):
    info = person(c, x, y, s, look_as, **kw)
    rng = np.random.default_rng(seed)
    hx, hy = info['head']
    for i in range(4):
        blob(c, x + (rng.random() - 0.5) * 80 * s, y - (120 + rng.random() * 150) * s, (12 + rng.random() * 16) * s,
             HOLI[(seed + i) % len(HOLI)], 0.85, seed=seed + i)
    blob(c, hx + (rng.random() - 0.5) * 50 * s, hy + 25 * s, 14 * s, HOLI[(seed + 2) % len(HOLI)], 0.7, seed=seed)
    return info


CROWD = [
    dict(skin='#d99a6c', hair='#22122e', style='short', shirt='#fff6ea', pants='#3a2f7a'),
    dict(skin='#8a5636', hair='#1a0f20', style='curly', shirt='#fff6ea', pants='#7b2d6b'),
    dict(skin='#f2c29b', hair='#3a1d10', style='long', shirt='#fff6ea', pants='#26407a'),
    dict(skin='#b77a50', hair='#160b1c', style='bun', shirt='#fff6ea', pants='#2a6b5b'),
    dict(skin='#c98b62', hair='#2b1a3a', style='spiky', shirt='#fff6ea', pants='#4a2f8a'),
    dict(skin='#ffd7b8', hair='#5a2a10', style='long', shirt='#fff6ea', pants='#8a2f4a'),
    dict(skin='#a9714a', hair='#120a18', style='cap', shirt='#fff6ea', pants='#2f3f8a'),
]


def holi(c, t, d, p, b):
    zoom = 1.0
    fx, fy = 960, 600
    if p.get('glass'):
        zoom = 1.0 + 0.55 * eio(t / 3.0)
        fx, fy = 1010, 640
    bg_grad(c, '#ff9a4d', '#5b1fa8', '#ff3d8b')
    glow(c, 1450, 360, 420, '#ffe08a', 0.55)
    circle(c, 1450, 360, 110, '#ffe7a8', 0.95)
    c.save()
    c.translate(fx, fy)
    c.scale(zoom, zoom)
    c.translate(-fx, -fy)
    skyline(c, 760, '#8a2f8f', seed=4)
    skyline(c, 820, '#5e1f7a', seed=9)
    bunting(c, t, 120)
    bunting(c, t + 1, 260, sag=40, colors=HOLI[::-1])
    for i, (bx, by, hc, t0) in enumerate([(380, 520, HOLI[0], 0.2), (1550, 480, HOLI[2], 0.9), (900, 430, HOLI[1], 1.7),
                                          (250, 650, HOLI[3], 2.6), (1300, 560, HOLI[4], 3.3), (700, 560, HOLI[5], 4.2),
                                          (1700, 640, HOLI[0], 5.0)]):
        powder_burst(c, bx, by, t, t0, hc, 1.3, seed=i * 7)
    xs = [180, 430, 690, 1240, 1500, 1760]
    for i, x in enumerate(xs):
        arms = [('dance', 'up'), ('up', 'dance'), ('hip', 'dance'), ('dance', 'wave'), ('up', 'up'), ('dance', 'hip')][i]
        splat_person(c, x, 1010 + (i % 2) * 25, 1.12, CROWD[i], i * 3, expr=['laugh', 'happy', 'laugh', 'happy', 'laugh', 'happy'][i],
                     t=t + i * 0.37, arms=arms, look=(0.3 if x < 960 else -0.3, -0.2), blink_off=i)
    # two friends in front, passing the glass
    a_info = splat_person(c, 900, 1080, 1.35, CROWD[6], 21, expr='happy', t=t, arms=('down', 'hold'), look=(0.6, 0))
    b_info = splat_person(c, 1150, 1080, 1.35, CROWD[2], 33, expr='curious' if t < 3 else 'happy', t=t + 0.4,
                          arms=('hold', 'down'), look=(-0.6, -0.1))
    if p.get('glass'):
        k = eio(ramp(t, 2.2, 3.6))
        ha, hb = a_info['hands'][1], b_info['hands'][-1]
        gx, gy = lerp(ha[0] + 20, hb[0] - 20, k), lerp(ha[1], hb[1], k) - 50 * math.sin(math.pi * k) + 40
        glass(c, gx, gy, 0.55, 0.78, t=t, glowc='#c8ffb0')
    c.restore()
    particles(c, t, seed=5, n=60, h='#fff3c4', a=0.5, size=(2, 5), speed=20)


def rangoli(c, x, y, r, t, a=1.0, colors=('#ff3d8b', '#ffd23f', '#2bd17e', '#2bd1ff', '#9d5cff')):
    for ring in range(4):
        rr = r * (1 - ring * 0.22)
        n = 8 + ring * 4
        hcol = colors[ring % len(colors)]
        for i in range(n):
            an = i / n * 2 * math.pi + t * 0.1 * (1 if ring % 2 else -1)
            px, py = x + math.cos(an) * rr * 0.78, y + math.sin(an) * rr * 0.78
            c.save()
            c.translate(px, py)
            c.rotate(math.degrees(an) + 90)
            path = smooth_path([(0, -rr * 0.2), (rr * 0.08, 0), (0, rr * 0.2), (-rr * 0.08, 0)], k=0.8)
            c.drawPath(path, P(hcol, a))
            c.restore()
    circle(c, x, y, r * 0.18, colors[1], a)


def s_glass(c, t, d, p, b):
    bg_radial(c, (960, 560), '#2f7a4f', '#160a3d', 1100)
    rangoli(c, 960, 560, 470 * back(ramp(t, bt(b, 2), bt(b, 2) + 0.9)), t, a=0.85)
    bokeh(c, t, seed=8, colors=('#7dff6a', '#ffd23f', '#ff4fa3'), a=0.2)
    for i in range(3):
        k = eout(ramp(t, bt(b, 1) + i * 0.25, bt(b, 1) + 1.3 + i * 0.25))
        if k > 0:
            lx = [560, 1360, 1250][i]
            ly = [460, 380, 760][i]
            leaf(c, lerp(960, lx, k), lerp(560, ly + 10 * osc(t, 0.4, i), k), 0.8 * k, ang=[-30, 25, 140][i] + 8 * osc(t, 0.3, i),
                 h=['#2bd17e', '#45e08c', '#1fb36a'][i], a=k)
    s = 2.1 * back(ramp(t, 0.0, 0.7))
    glass(c, 960, 800 + 6 * osc(t, 0.5), s, 0.82, t=t, glowc='#b8ff9c')
    k = pop(t, bt(b, 0) + 0.3)
    text(c, 'BHANG', 960, 230, 150 * k + 1, '#ffffff', a=clamp01(k), weight=900, shadow=0.5, track=0.05)
    text(c, 'भांग', 960, 335, 84 * k + 1, '#c8ffb0', a=clamp01(k), name='Baloo2', weight=800, shadow=0.4)
    particles(c, t, seed=2, n=45, h='#e8ffd8', a=0.45)


def s_shop(c, t, d, p, b):
    bg_grad(c, '#2a1a6e', '#ff6f91', '#7b3fa8')
    skyline(c, 700, '#3f1f78', seed=13)
    c.drawRect(skia.Rect(0, 900, W, H), P('#3b2366'))
    # shop body
    rrect(c, 520, 300, 880, 620, 26, '#ffcf5a')
    rrect(c, 520, 300, 880, 40, 20, '#ffe08a')
    # sign board
    k = pop(t, 0.5, 0.6)
    c.save()
    c.translate(960, 360)
    c.scale(k, k)
    rrect(c, -380, -70, 760, 150, 22, '#1fa35c')
    rrect(c, -366, -56, 732, 122, 16, '#2bd17e')
    text(c, 'सरकारी भांग की दुकान', 0, 2, 64, '#ffffff', name='Baloo2', weight=800, shadow=0.35)
    text(c, 'GOVT. LICENSED BHANG SHOP', 0, 52, 30, '#0b3b22', weight=800, shadow=0)
    c.restore()
    # awning
    for i in range(10):
        x0 = 500 + i * 92
        path = skia.Path()
        path.moveTo(x0, 450)
        path.lineTo(x0 + 92, 450)
        path.lineTo(x0 + 92, 520)
        path.quadTo(x0 + 46, 560, x0, 520)
        path.close()
        c.drawPath(path, P('#ff3d6e' if i % 2 else '#fff3e6'))
    # window + shopkeeper + counter
    rrect(c, 600, 560, 720, 300, 20, '#4a2a7a')
    glow(c, 960, 700, 420, '#ffd27a', 0.45)
    person(c, 960, 990, 1.25, dict(skin='#b77a50', hair='#1a0f20', style='short', shirt='#ff8a3d'), expr='happy',
           t=t, arms=('wave' if t % 3 < 1.6 else 'down', 'down'), look=(0, 0.1))
    rrect(c, 560, 800, 800, 300, 18, '#9a4b2a')
    rrect(c, 560, 800, 800, 26, 13, '#c06a3c')
    for i in range(5):
        glass(c, 640 + i * 160, 830, 0.36, 0.75, t=t + i, garnish=False)
    # licensed stamp
    k2 = pop(t, 1.9, 0.5)
    if k2 > 0:
        c.save()
        c.translate(1430, 640)
        c.rotate(-12)
        c.scale(2.2 - 1.2 * k2, 2.2 - 1.2 * k2)
        a = clamp01(k2)
        rrect(c, -150, -55, 300, 110, 18, '#ffffff', a)
        rrect(c, -138, -43, 276, 86, 12, '#2bd17e', a)
        text(c, 'LICENSED', 0, 16, 46, '#ffffff', a, weight=900, shadow=0)
        c.restore()
    for i in range(14):
        x = 120 + i * 130
        circle(c, x, 280 + 18 * math.sin(i * 0.9), 9, HOLI[i % 6], 0.9)
        glow(c, x, 280 + 18 * math.sin(i * 0.9), 40, HOLI[i % 6], 0.35 + 0.15 * osc(t, 1.2, i))


def room(c, t, wob=0.0, hue=0.0):
    top = mix('#3b2a8a', '#ff3dd1', hue)
    bot = mix('#1d1150', '#2bd1ff', hue * 0.6)
    bg_grad(c, top, bot)
    # floor
    path = skia.Path()
    path.moveTo(0, 820)
    for i in range(21):
        x = i * W / 20
        path.lineTo(x, 820 + wob * 30 * osc(t * 0.8 + i * 0.3, 0.7))
    path.lineTo(W, H)
    path.lineTo(0, H)
    path.close()
    c.drawPath(path, P(mix('#2a1760', '#9d2bd1', hue)))
    # window
    c.save()
    c.translate(420, 360)
    c.rotate(wob * 8 * osc(t, 0.3))
    rrect(c, -170, -150, 340, 300, 20, '#160b3d')
    rrect(c, -150, -130, 300, 260, 12, mix('#3a2fa8', '#ff9a4d', hue))
    circle(c, 60, -40, 40, '#fff3c4')
    line(c, [(0, -130), (0, 130)], 10, '#160b3d')
    line(c, [(-150, 0), (150, 0)], 10, '#160b3d')
    c.restore()


def s_party(c, t, d, p, b):
    t2 = bt(b, 2, d * 0.6)
    w = eio(ramp(t, t2, t2 + 2.0))
    room(c, t, wob=w, hue=w * (0.6 + 0.4 * osc(t, 0.25)))
    # clock
    hrs = 7.0 + 0.4 * t / d + (6.0 * eio(ramp(t, t2, t2 + 2.2)))
    c.save()
    c.translate(1420, 330)
    c.rotate(w * 12 * osc(t, 0.4))
    c.scale(1 + w * 0.12 * osc(t, 0.9), 1 - w * 0.12 * osc(t, 0.9))
    clock(c, 0, 0, 120, hrs)
    c.restore()
    k = ramp(t, t2, t2 + 1.5)
    text(c, 'HOURS LATER...', 1420, 520, 46, '#ffe14d', a=k * (1 - ramp(t, t2 + 3, t2 + 4)), weight=900)
    # couch
    rrect(c, 640, 680, 640, 220, 60, '#ff5f8f')
    rrect(c, 600, 760, 720, 170, 60, '#e03d75')
    rrect(c, 560, 700, 110, 230, 50, '#ff5f8f')
    rrect(c, 1250, 700, 110, 230, 50, '#ff5f8f')
    # drinking phases
    t1 = bt(b, 1, 2)
    drink1 = win(t, t1 + 0.2, t1 + 1.3, 0.3)
    drink2 = win(t, t1 + 2.3, t1 + 3.2, 0.3)
    arms = ('down', 'drink' if (drink1 > 0.5 or drink2 > 0.5) else 'hold')
    expr = 'neutral' if t < t1 + 1.3 else ('bored' if t < t2 else ('high' if t < t2 + 3 else 'dazed'))
    info = person(c, 960, 905, 1.35, dict(skin='#d99a6c', hair='#22122e', style='spiky', shirt='#2bd1ff', pants='#3a2f7a'),
                  expr=expr, t=t, arms=arms, sit=True, look=(0.2 if t < t2 else 0.6 * osc(t, 0.5), -0.1),
                  lean=w * 0.3 * osc(t, 0.35))
    hx, hy = info['hands'][1]
    n_glass = 1 if t < t1 + 2.2 else 2
    fill = 0.8 - 0.6 * ramp(t, t1 + 0.3, t1 + 1.3) if n_glass == 1 else 0.8 - 0.6 * ramp(t, t1 + 2.4, t1 + 3.2)
    glass(c, hx + 6, hy + 70, 0.42, fill, t=t)
    # empty glass on the floor
    if t > t1 + 2.0:
        glass(c, 1380, 980, 0.42, 0.05, t=t, garnish=False)
    # "..." bubble
    kb = win(t, t1 + 1.4, t1 + 2.3, 0.25)
    if kb > 0:
        hx2, hy2 = info['head']
        rrect(c, hx2 + 70, hy2 - 170, 150, 80, 40, '#ffffff', kb)
        for i in range(3):
            circle(c, hx2 + 110 + i * 35, hy2 - 130, 9, '#3a1d8f', kb)
    # weird world bits
    if w > 0:
        for i in range(9):
            an = t * 0.6 + i * 0.7
            x, y = 960 + math.cos(an) * (500 + 80 * osc(t, 0.3, i)), 520 + math.sin(an * 1.3) * 300
            sz = 34 + 10 * osc(t, 1.1, i)
            ellipse(c, x, y, sz, sz * 0.7, '#ffffff', w * 0.9)
            circle(c, x + 6 * osc(t, 0.7, i), y, sz * 0.38, '#2a1640', w)
        for i in range(30):
            an = i / 30 * 6.28 + t
            r = 300 + 40 * osc(t, 0.5, i)
            circle(c, 960 + math.cos(an) * r * 1.6, 500 + math.sin(an) * r, 6, HOLI[i % 6], w * 0.8)


def s_brain_q(c, t, d, p, b):
    bg_radial(c, (960, 520), '#4a2bb0', '#120838', 1200)
    particles(c, t, seed=9, n=50, a=0.4)
    t1 = bt(b, 1, d * 0.6)
    expr = 'curious' if t < t1 + 0.9 else 'shock'
    jump = pop(t, t1 + 0.7, 0.35)
    shake = 8 * osc(t, 9) * win(t, t1 + 0.8, t1 + 1.6, 0.1)
    brain(c, 900 + shake, 540, 1.45, t, expr=expr, look=(-0.3, -0.4) if t < t1 + 0.8 else (0.8, 0.2), face_r=105)
    for i in range(5):
        an = t * 0.7 + i * 1.256
        k = pop(t, 0.3 + i * 0.25)
        x, y = 900 + math.cos(an) * 520, 470 + math.sin(an) * 300
        text(c, '?', x, y + 30, 110 * k + 1, ['#ffe14d', '#2bd1ff', '#ff4fa3', '#7cf2c4', '#ffffff'][i], a=clamp01(k), weight=900)
    if t > t1:
        gx = lerp(1700, 1380, eout(ramp(t, t1, t1 + 0.6)))
        gy = 760 - 120 * jump
        if p.get('prop') == 'phone':
            phone(c, gx, gy - 150, 0.62, t, glow_c='#ff3d8b', ang=-8)
            for s in (-1, 1):
                eye(c, gx + s * 30 - 10, gy - 190, 20, look=(-0.8, 0), lid=0.45 * (1 - jump), lid_col='#2a1450', red=0)
        else:
            glass(c, gx, gy, 0.75, 0.8, t=t, glowc='#9cff7a')
            # sneaky eyes on the glass
            for s in (-1, 1):
                eye(c, gx + s * 28, gy - 120, 20, look=(-0.8, 0), lid=0.45 * (1 - jump), lid_col='#cfe8b0', red=0)
        if jump > 0.2:
            text(c, 'BOO!', gx + 20, gy - 250, 90 * clamp01(jump), '#ffe14d', weight=900)


def s_title(c, t, d, p, b):
    bg_radial(c, (960, 600), '#ff4fa3', '#2a0f6e', 1300)
    c.save()
    c.translate(960, 640)
    c.rotate(t * 6)
    for i in range(18):
        path = skia.Path()
        path.moveTo(0, 0)
        a0, a1 = math.radians(i * 20), math.radians(i * 20 + 9)
        path.lineTo(math.cos(a0) * 1600, math.sin(a0) * 1600)
        path.lineTo(math.cos(a1) * 1600, math.sin(a1) * 1600)
        path.close()
        c.drawPath(path, P('#ffffff', 0.07))
    c.restore()
    k = back(ramp(t, 0.0, 0.8))
    ph = p.get('prop') == 'phone'
    if ph:
        phone(c, 960, 760, 1.25 * k, t, glow_c='#ff3d8b')
    else:
        glass(c, 960, 1040, 2.6 * k, 0.86, t=t, glowc='#c8ffb0', garnish=False)
    c.save()
    c.translate(960, 780)
    c.scale(0.62 * k, 0.62 * k)
    if ph:
        c.translate(0, -330)
        c.scale(0.8, 0.8)
    brain(c, 0, 0, 1.0, t, expr='dazed' if ph else 'high', look=(0, 0.6) if ph else (0.2, -0.3), stem=False)
    c.restore()
    for i in range(12):
        an = i / 12 * 6.28 + t * 0.5
        if ph:
            heart_icon(c, 960 + math.cos(an) * 700, 560 + math.sin(an) * 330, 26, ['#ff3d6e', '#ffd23f', '#ff9ad5'][i % 3], 0.8)
        else:
            leaf(c, 960 + math.cos(an) * 700, 560 + math.sin(an) * 330, 0.28, ang=math.degrees(an) + 90, a=0.75)
    w1 = pop(t, 0.35)
    w2 = pop(t, 0.7)
    text(c, p.get('l1', 'WHAT BHANG REALLY DOES'), 960, 170, 104 * w1 + 1, '#ffffff', clamp01(w1), weight=900, shadow=0.55)
    text(c, p.get('l2', 'TO YOUR BRAIN'), 960, 300, 128 * w2 + 1, '#ffe14d', clamp01(w2), weight=900, shadow=0.55)


def s_chapter(c, t, d, p, b):
    c1, c2 = p.get('c1', '#ff4fa3'), p.get('c2', '#3a1d8f')
    bg_grad(c, c1, c2)
    for i in range(7):
        x = (i * 330 + t * 120) % (W + 400) - 200
        c.save()
        c.translate(x, 540)
        c.rotate(25)
        c.drawRect(skia.Rect(-60, -900, 60, 900), P('#ffffff', 0.06))
        c.restore()
    bokeh(c, t, seed=p.get('n', 1) * 5, colors=('#ffffff', c1), a=0.15)
    k = pop(t, 0.15, 0.55)
    circle(c, 960, 420, 120 * k, '#ffffff', 0.95)
    text(c, str(p.get('n', 1)), 960, 420 + 48 * k, 140 * k + 1, c2, weight=900, shadow=0)
    k2 = pop(t, 0.45, 0.55)
    text(c, p.get('text', ''), 960, 690, 112 * k2 + 1, '#ffffff', clamp01(k2), weight=900, shadow=0.45)
    w = measure(p.get('text', ''), 112, 900) * eout(ramp(t, 0.7, 1.3))
    rrect(c, 960 - w / 2, 730, w, 12, 6, '#ffffff', 0.8)


# ------------------------------------------------------------------ chapter 1
def bud(c, x, y, s, t, glow_a=0.0, seed=0):
    if glow_a > 0:
        glow(c, x, y, 140 * s, '#ffb02e', 0.6 * glow_a)
    rng = np.random.default_rng(seed)
    for i in range(9):
        bx, by = x + (rng.random() - 0.5) * 50 * s, y + (rng.random() - 0.5) * 90 * s
        blob(c, bx, by, (26 + rng.random() * 12) * s, ['#7ad65a', '#5fbf4a', '#9be36b'][i % 3], seed=seed + i, wob=0.2)
    for i in range(10):
        bx, by = x + (rng.random() - 0.5) * 60 * s, y + (rng.random() - 0.5) * 100 * s
        an = rng.random() * 6.28
        line(c, [(bx, by), (bx + math.cos(an) * 16 * s, by + math.sin(an) * 16 * s)], 4 * s, '#ff9a3d')
    for i in range(14):   # resin sparkles
        bx, by = x + (rng.random() - 0.5) * 70 * s, y + (rng.random() - 0.5) * 110 * s
        circle(c, bx, by, 3.2 * s, '#ffffff', 0.7 * (0.5 + 0.5 * osc(t, 1.4, i)))


def plant(c, x, y, s, t, flowers=0.0, leaves=0.0):
    sway = 2 * osc(t, 0.25)
    c.save()
    c.translate(x, y)
    c.rotate(sway)
    line(c, [(0, 0), (4, -300 * s), (0, -620 * s)], 16 * s, '#2a8f4f')
    for i, (yy, sc) in enumerate([(-150, 1.0), (-300, 0.85), (-440, 0.7)]):
        for sd in (-1, 1):
            if leaves > 0:
                glow(c, sd * 170 * s * sc, yy * s - 60 * s, 200 * s * sc, '#7dff6a', 0.45 * leaves)
            leaf(c, sd * 20 * s, yy * s, 0.95 * s * sc, ang=sd * 62 + 3 * osc(t, 0.4, i), h=mix('#2bd17e', '#6dff9a', leaves * 0.5))
    for (bx, by, bs) in [(0, -660, 1.25), (-70, -470, 0.9), (75, -360, 0.85), (-80, -230, 0.75)]:
        bud(c, bx * s, by * s, bs * s, t, flowers, seed=int(abs(bx) + abs(by)))
    c.restore()


def info_card(c, x, y, w, h, title, sub, colr, a, stamp=None, stamp_col='#ff3d5a', t=0.0, stamp_k=0.0):
    if a <= 0:
        return
    c.save()
    c.translate(x + w / 2, y + h / 2)
    k = back(clamp01(a))
    c.scale(k, k)
    rrect(c, -w / 2, -h / 2 + 10, w, h, 30, '#12062e', 0.35 * a)
    rrect(c, -w / 2, -h / 2, w, h, 30, '#ffffff', a)
    rrect(c, -w / 2, -h / 2, w, 18, 9, colr, a)
    ts = min(76, 76 * (w - 70) / max(measure(title, 76, 900), 1))
    text(c, title, 0, -h / 2 + 110, ts, '#1b0f45', a, weight=900, shadow=0)
    text(c, sub, 0, -h / 2 + 170, 34, '#5a4b8a', a, weight=700, shadow=0)
    if stamp and stamp_k > 0:
        sk = back(stamp_k)
        c.save()
        c.translate(0, h / 2 - 85)
        c.rotate(-8)
        c.scale(1.8 - 0.8 * sk, 1.8 - 0.8 * sk)
        sw = measure(stamp, 46, 900) + 50
        rrect(c, -sw / 2, -40, sw, 80, 14, stamp_col, clamp01(stamp_k))
        text(c, stamp, 0, 17, 46, '#ffffff', clamp01(stamp_k), weight=900, shadow=0)
        c.restore()
    c.restore()


def sil_batta(c, x, y, s, t, a=1.0, paste=0.0):
    rrect(c, x - 220 * s, y - 30 * s, 440 * s, 70 * s, 30 * s, '#8a8aa8', a)
    rrect(c, x - 220 * s, y - 30 * s, 440 * s, 22 * s, 11 * s, '#b0b0c8', a)
    if paste > 0:
        blob(c, x, y - 34 * s, 90 * s * paste, '#5fbf4a', a, seed=4, t=t, sx=1.6, sy=0.45)
    rx = x + 110 * s * osc(t, 0.9)
    rrect(c, rx - 45 * s, y - 120 * s, 90 * s, 90 * s, 40 * s, '#9a9ab8', a)
    rrect(c, rx - 45 * s, y - 120 * s, 90 * s, 30 * s, 15 * s, '#c0c0d8', a)


def s_plant(c, t, d, p, b):
    bg_grad(c, '#173a6b', '#0d1a3d', '#12305a')
    bokeh(c, t, seed=21, colors=('#2bd17e', '#2bd1ff'), a=0.18)
    particles(c, t, seed=4, n=35, a=0.3)
    c.drawRect(skia.Rect(0, 930, W, H), P('#0a1430'))
    focus = p.get('focus', 'flowers')
    if focus == 'flowers':
        fl = ramp(t, bt(b, 2), bt(b, 2) + 0.6)
        lv = 0.0
    else:
        fl = 0.0
        lv = ramp(t, bt(b, 0), bt(b, 0) + 0.6)
    plant(c, 560, 960, 1.05, t, flowers=fl, leaves=lv)
    if focus == 'flowers':
        k = ramp(t, bt(b, 2) + 0.2, bt(b, 2) + 0.8)
        label(c, 'FLOWERS + RESIN', 900, 200, 600, 270, a=k)
        info_card(c, 1080, 300, 660, 470, 'GANJA · CHARAS', 'India\'s narcotics law (NDPS), 1985', '#ff3d5a', k,
                  stamp='ILLEGAL', t=t, stamp_k=ramp(t, bt(b, 2) + 2.6, bt(b, 2) + 3.1))
        if t < bt(b, 2):
            k0 = pop(t, bt(b, 1) + 0.3)
            text(c, 'ONE PLANT', 1400, 460, 110 * k0 + 1, '#ffffff', clamp01(k0), weight=900)
            text(c, 'TWO LIVES', 1400, 590, 110 * pop(t, bt(b, 1) + 0.9) + 1, '#2bd17e', clamp01(pop(t, bt(b, 1) + 0.9)), weight=900)
    else:
        k = ramp(t, bt(b, 0) + 0.3, bt(b, 0) + 0.9)
        label(c, 'LEAVES + SEEDS', 920, 180, 760, 600, a=k)
        k2 = ramp(t, bt(b, 1), bt(b, 1) + 0.6)
        info_card(c, 1080, 270, 660, 470, 'BHANG', 'Leaves + seeds, ground to a paste', '#2bd17e', k2,
                  stamp='UP TO EACH STATE', stamp_col='#ffb02e', t=t, stamp_k=ramp(t, bt(b, 1) + 2.4, bt(b, 1) + 2.9))
        sil_batta(c, 1410, 900, 0.9, t, a=k2, paste=ramp(t, bt(b, 1), bt(b, 1) + 3))


def s_scroll(c, t, d, p, b):
    bg_radial(c, (960, 540), '#ff9a3d', '#5a1a5e', 1200)
    particles(c, t, seed=31, n=40, h='#ffe8b0', a=0.45)
    k = eio(ramp(t, 0.2, 1.6))
    w = 1300 * k
    rrect(c, 960 - w / 2, 300, w, 520, 20, '#ffe8b8')
    c.save()
    c.clipRect(skia.Rect(960 - w / 2, 300, 960 + w / 2, 820))
    rrect(c, 960 - w / 2, 300, w, 520, 20, '#ffe8b8')
    for i in range(6):   # "ancient text" squiggle lines
        y = 370 + i * 30
        pts = [(350 + j * 30, y + 5 * math.sin(j * 1.9 + i)) for j in range(41)]
        line(c, pts, 5, '#c98a4a', 0.45)
    text(c, 'ATHARVA VEDA', 960, 590, 64, '#7a2a1a', weight=900, shadow=0)
    text(c, 'अथर्ववेद', 960, 650, 44, '#b05a2a', name='Baloo2', weight=800, shadow=0)
    c.restore()
    for sx in (-1, 1):
        x = 960 + sx * w / 2
        rrect(c, x - 30, 270, 60, 580, 30, '#a0522d')
        rrect(c, x - 30, 270, 60, 30, 15, '#c0703d')
    t1 = bt(b, 1, 3)
    icons = ['#ffb02e', '#ff4fa3', '#2bd1ff', '#9d5cff', '#2bd17e']
    for i in range(5):
        kk = pop(t, t1 + 1.6 + i * 0.25)
        x = 560 + i * 200
        y = 860 + 10 * osc(t, 0.5, i)
        if kk <= 0:
            continue
        sel = i == 4
        hl = ramp(t, t1 + 3.6, t1 + 4.2) if sel else 0
        glow(c, x, y, 140, '#7dff6a', 0.6 * hl)
        circle(c, x, y, 80 * kk, '#ffffff')
        circle(c, x, y, 70 * kk, icons[i] if not sel else mix('#ffffff', '#2bd17e', 0.3))
        if sel:
            leaf(c, x, y + 40 * kk, 0.32 * kk, h='#1f9d5a')
        else:
            blob(c, x, y, 34 * kk, '#ffffff', 0.85, seed=i)
            line(c, [(x, y + 34 * kk), (x, y + 56 * kk)], 6, '#ffffff', 0.85)
    if t > t1 + 4.0:
        kk = pop(t, t1 + 4.0)
        text(c, 'RELIEVES ANXIETY', 1420, 1010 - 0, 44 * kk + 1, '#ffffff', clamp01(kk), weight=900)
        line(c, [(1420, 960), (1420, 940), (1330, 930)], 5, '#ffffff', clamp01(kk) * 0.0)


def top_hat(c, x, y, r, h='#1d1238'):
    rrect(c, x - r * 0.95, y - r * 0.72, r * 1.9, r * 0.16, r * 0.08, h)
    rrect(c, x - r * 0.62, y - r * 1.75, r * 1.24, r * 1.08, r * 0.1, h)
    rrect(c, x - r * 0.62, y - r * 0.95, r * 1.24, r * 0.16, 0, '#ff3d6e')


def mustache(c, x, y, r, h='#3a2010'):
    for s in (-1, 1):
        path = smooth_path([(x, y), (x + s * r * 0.45, y - r * 0.08), (x + s * r * 0.62, y + r * 0.06),
                            (x + s * r * 0.4, y + r * 0.12), (x + s * r * 0.08, y + r * 0.1)], k=0.6)
        c.drawPath(path, P(h))


def s_commission(c, t, d, p, b):
    bg_grad(c, '#1d6b6b', '#0c2a40', '#145060')
    particles(c, t, seed=17, n=30, h='#ffe8b0', a=0.3)
    # wall frame w/ year
    rrect(c, 760, 90, 400, 150, 18, '#d9a14a')
    rrect(c, 776, 106, 368, 118, 12, '#2a1a10')
    text(c, '1893-94', 960, 190, 76, '#ffd27a', weight=900, shadow=0)
    # officials behind table
    officials = [(700, '#f2c29b', '#2a6b8a'), (960, '#ffd7b8', '#8a2f4a'), (1220, '#e8b48f', '#3a2f7a')]
    for i, (x, sk, sh) in enumerate(officials):
        info = person(c, x, 830, 1.05, dict(skin=sk, hair='#e8e0d0', style='short', shirt=sh),
                      expr='think' if t < bt(b, 1) + 3 else 'happy', t=t + i, arms=('down', 'down'), look=(-0.5, 0.2),
                      blink_off=i * 1.3)
        hx, hy = info['head']
        top_hat(c, hx, hy, info['r'])
        mustache(c, hx, hy + info['r'] * 0.33, info['r'])
    # table + papers
    rrect(c, 480, 700, 960, 60, 16, '#a0522d')
    rrect(c, 520, 760, 880, 260, 10, '#7a3a1f')
    pile = int(2 + 22 * ramp(t, 0.5, bt(b, 1) + 3))
    for i in range(pile):
        rrect(c, 1270 + (i % 3) * 3, 690 - i * 9, 150, 10, 3, '#fff6e0' if i % 2 else '#f0e4c8')
    # witnesses queue
    k = ramp(t, bt(b, 1), bt(b, 1) + 3)
    for i in range(6):
        x = -100 + ((t * 70 + i * 120) % 520)
        person(c, x, 1060, 0.62, dict(skin=SKINS[i % 6], hair='#22122e', style=['short', 'long', 'bun'][i % 3],
                                       shirt=HOLI[i % 6]), expr='neutral', t=t * 2 + i, arms=('down', 'down'), look=(1, 0))
    n = int(1000 * eout(k)) + (0 if k < 1 else 0)
    if k > 0:
        rrect(c, 70, 300, 360, 150, 24, '#ffffff', 0.95)
        text(c, f'{n:,}' + ('+' if k >= 1 else ''), 250, 395, 84, '#1d6b6b', weight=900, shadow=0)
        text(c, 'WITNESSES', 250, 432, 28, '#5a4b8a', weight=800, shadow=0)
    ks = ramp(t, bt(b, 1) + 3.2, bt(b, 1) + 3.7)
    if ks > 0:
        c.save()
        c.translate(1600, 470)
        c.rotate(8)
        sk = back(ks)
        c.scale(1.8 - 0.8 * sk, 1.8 - 0.8 * sk)
        rrect(c, -230, -90, 460, 180, 20, '#2bd17e', clamp01(ks))
        text(c, 'MODERATE USE:', 0, -20, 44, '#ffffff', clamp01(ks), weight=900, shadow=0)
        text(c, 'NO SERIOUS HARM', 0, 40, 44, '#ffffff', clamp01(ks), weight=900, shadow=0)
        c.restore()
    kh = ramp(t, bt(b, 2), bt(b, 2) + 0.5)
    if kh > 0:
        c.drawRect(skia.Rect(0, 0, W, H), P('#0c0628', 0.45 * kh))
        info = person(c, 1640 + 200 * (1 - eout(kh)), 1090, 1.3, dict(skin='#b77a50', hair='#22122e', style='bun', shirt='#ffd23f'),
                      expr='think', t=t, arms=('down', 'point'), look=(-0.8, 0))
        hx, hy = info['hands'][1]
        circle(c, hx - 60, hy - 60, 70, '#bde8ff', 0.35 * kh)
        c.drawCircle(hx - 60, hy - 60, 70, P('#ffffff', kh, stroke=12))
        line(c, [(hx - 10, hy - 10), (hx + 30, hy + 30)], 18, '#ffffff', kh)
        kq = pop(t, bt(b, 2) + 0.8)
        text(c, 'NEUTRAL?', 1600, 300, 90 * kq + 1, '#ffe14d', clamp01(kq), weight=900)


def mini_person(c, x, y, s, colr, a=1.0, head='#ffd7b8'):
    circle(c, x, y - 52 * s, 20 * s, head, a)
    path = skia.Path()
    path.addRoundRect(skia.Rect(x - 24 * s, y - 30 * s, x + 24 * s, y + 20 * s), 18 * s, 18 * s)
    c.drawPath(path, P(colr, a))


def s_people_grid(c, t, d, p, b):
    dark = p.get('dark')
    if dark:
        bg_radial(c, (960, 400), '#3a1d8f', '#0c0628', 1200)
    else:
        bg_radial(c, (960, 400), '#1f7a5c', '#0f1a40', 1200)
    particles(c, t, seed=41, n=30, a=0.3)
    colr = p.get('color', '#2bd17e')
    cols, rows = 26, 7
    for j in range(rows):
        for i in range(cols):
            idx = j * cols + i
            k = pop(t, 0.2 + (i + j) * 0.03, 0.4)
            if k <= 0:
                continue
            x = 960 + (i - (cols - 1) / 2) * 66
            y = 580 + j * 70 + 4 * osc(t, 0.7, idx * 0.3)
            hl = (idx * 37) % 50 == 0
            mini_person(c, x, y, 0.9 * k, colr if hl else '#5a4b8a', 0.95, head=SKINS[idx % 6])
            if hl:
                glow(c, x, y - 20, 50, colr, 0.4)
    k = pop(t, 0.6, 0.6)
    text(c, p.get('big', ''), 960, 300, 190 * k + 1, colr, clamp01(k), weight=900, shadow=0.5)
    k2 = ramp(t, 1.0, 1.5)
    text(c, p.get('sub', ''), 960, 390, 48, '#ffffff', k2, weight=700)


# ------------------------------------------------------------------ chapter 2: body
ORG = dict(mouth=(960, 300), throat=(960, 420), stomach=(1060, 620), gut=(960, 790), liver=(850, 610),
           heart=(1000, 500), brain=(960, 165), lungL=(860, 470), lungR=(1080, 470))


def body_diagram(c, t, lit=None, a=1.0):
    lit = lit or {}
    # silhouette
    sil = skia.Path()
    sil.addCircle(960, 190, 150)
    c.drawPath(sil, P('#ffffff', 0.12 * a))
    rrect(c, 920, 320, 80, 80, 20, '#ffffff', 0.12 * a)
    tor = smooth_path([(700, 420), (1220, 420), (1250, 650), (1180, 960), (740, 960), (670, 650)], k=0.5)
    c.drawPath(tor, P('#ffffff', 0.12 * a))
    # brain
    c.save()
    c.translate(960, 190)
    c.scale(0.42, 0.42)
    brain(c, 0, 0, 1.0, t, stem=False, glow_c='#ffe14d', glow_a=0.8 * lit.get('brain', 0))
    c.restore()
    # lungs
    for sx, key in ((-1, 'lungL'), (1, 'lungR')):
        x, y = ORG[key]
        pth = smooth_path([(x - 60 * (sx < 0) - 10, y - 90), (x + 50 * (sx > 0) + 10, y - 80), (x + 70 * sx, y + 60),
                           (x + 20 * sx, y + 110), (x - 40 * sx, y + 60)], k=0.6)
        shaded(c, pth, mix('#ff8fb3', '#ffffff', 0.3 * lit.get('lungs', 0)), a)
    # heart
    hx, hy = ORG['heart']
    beat = 1 + 0.08 * max(0, osc(t, 1.3))
    blob(c, hx, hy, 50 * beat, '#ff3d5a', a, seed=3, wob=0.08)
    # throat
    line(c, [ORG['mouth'], ORG['throat'], (1000, 540), ORG['stomach']], 26, '#ff9a8a', a * 0.9)
    # stomach
    sx_, sy_ = ORG['stomach']
    sp = smooth_path([(sx_ - 70, sy_ - 70), (sx_ + 40, sy_ - 90), (sx_ + 110, sy_ - 10), (sx_ + 60, sy_ + 80),
                      (sx_ - 60, sy_ + 70), (sx_ - 40, sy_)], k=0.6)
    shaded(c, sp, mix('#ff7a9a', '#ffe14d', 0.5 * lit.get('stomach', 0)), a)
    # liver
    lx, ly = ORG['liver']
    lp = smooth_path([(lx - 140, ly - 50), (lx + 60, ly - 70), (lx + 110, ly - 30), (lx + 20, ly + 50), (lx - 120, ly + 40)], k=0.6)
    shaded(c, lp, mix('#b8325a', '#ff9a3d', 0.6 * lit.get('liver', 0)), a)
    if lit.get('liver', 0) > 0:
        glow(c, lx, ly, 200, '#ffb02e', 0.5 * lit['liver'])
    # gut coil
    gx, gy = ORG['gut']
    pts = []
    for i in range(60):
        an = i / 60 * 6.28 * 3
        rr = 110 - i * 1.3
        pts.append((gx + math.cos(an) * rr * 1.4, gy + math.sin(an) * rr * 0.75))
    c.drawPath(smooth_path(pts, closed=False), P(mix('#ff9ab8', '#ffe14d', 0.5 * lit.get('gut', 0)), a, stroke=30))
    c.drawPath(smooth_path(pts, closed=False), P('#ffc2d6', a * 0.5, stroke=8))
    return pts


def path_pos(pts, k):
    k = clamp01(k)
    segs = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total = sum(segs)
    target = k * total
    for i, sl in enumerate(segs):
        if target <= sl or i == len(segs) - 1:
            u = target / sl if sl else 0
            return (lerp(pts[i][0], pts[i + 1][0], u), lerp(pts[i][1], pts[i + 1][1], u))
        target -= sl
    return pts[-1]


def traveller(c, x, y, t, h='#7dff6a', s=1.0):
    glow(c, x, y, 70 * s, h, 0.7)
    circle(c, x, y, 16 * s, h)
    circle(c, x - 5 * s, y - 5 * s, 6 * s, '#ffffff', 0.8)


def s_body(c, t, d, p, b):
    bg_radial(c, (960, 540), '#3a1d8f', '#100630', 1200)
    particles(c, t, seed=51, n=40, a=0.3)
    stage = p.get('stage', 'compare')
    if stage == 'compare':
        k1 = ramp(t, 0.6, 2.4)
        lit = dict(lungs=win(t, 0.6, 2.6), brain=ramp(t, 2.0, 2.5) * (1 - ramp(t, bt(b, 1) - 0.3, bt(b, 1))))
        body_diagram(c, t, lit)
        if 0 < k1 < 1:
            path = [(700, 300), ORG['lungL'], ORG['heart'], (960, 360), ORG['brain']]
            x, y = path_pos(path, eio(k1))
            traveller(c, x, y, t, '#bdbdff')
        ka = ramp(t, 0.5, 1.0) * (1 - ramp(t, bt(b, 1) - 0.3, bt(b, 1)))
        info_pill(c, 420, 260, 'SMOKED', 'MINUTES', '#bdbdff', ka)
        k2 = ramp(t, bt(b, 1) + 0.3, d + 2)
        if t > bt(b, 1):
            gk = pop(t, bt(b, 1))
            glass(c, 1340, 360, 0.55 * gk, 0.7, t=t)
            path = [(1300, 260), ORG['mouth'], ORG['throat'], (1000, 540), ORG['stomach']]
            x, y = path_pos(path, eio(k2))
            traveller(c, x, y, t)
            info_pill(c, 1500, 260, 'DRANK', 'A LONG TRIP...', '#7dff6a', ramp(t, bt(b, 1) + 0.4, bt(b, 1) + 0.9))
    else:
        k = ramp(t, 0.2, bt(b, 1) + 0.2)
        lit = dict(stomach=win(t, 0.2, 2.8, 0.5), gut=win(t, 1.6, bt(b, 1) + 0.5, 0.5), liver=ramp(t, bt(b, 1) + 0.3, bt(b, 1) + 1.0))
        pts = body_diagram(c, t, lit)
        route = [ORG['stomach'], (1000, 690)] + pts[::-1][::3] + [(880, 700), ORG['liver']]
        x, y = path_pos(route, eio(ramp(t, 0.3, bt(b, 1) + 0.9)))
        traveller(c, x, y, t)
        info_pill(c, 1500, 640, 'STOMACH + GUT', '', '#ff7a9a', ramp(t, 0.5, 1.0) * (1 - ramp(t, bt(b, 1), bt(b, 1) + 0.4)))
        kl = ramp(t, bt(b, 1) + 0.6, bt(b, 1) + 1.1)
        label(c, 'LIVER', 420, 480, 760, 600, a=kl, size=40)
        info_pill(c, 1500, 640, 'CHEMICAL', 'PROCESSING PLANT', '#ffb02e', kl)


def info_pill(c, x, y, title, sub, colr, a):
    if a <= 0:
        return
    k = back(a)
    c.save()
    c.translate(x, y)
    c.scale(k, k)
    w = max(measure(title, 54, 900), measure(sub, 34, 800)) + 80
    h = 150 if sub else 100
    rrect(c, -w / 2, -h / 2, w, h, 30, '#ffffff', clamp01(a))
    rrect(c, -w / 2, -h / 2, 16, h, 8, colr, clamp01(a))
    text(c, title, 0, -h / 2 + 68, 54, '#1b0f45', clamp01(a), weight=900, shadow=0)
    if sub:
        text(c, sub, 0, -h / 2 + 118, 34, '#6a5aa0', clamp01(a), weight=800, shadow=0)
    c.restore()


def liver_char(c, x, y, s, t, expr='happy'):
    lp = smooth_path([(x - 260 * s, y - 60 * s), (x + 100 * s, y - 130 * s), (x + 230 * s, y - 70 * s),
                      (x + 150 * s, y + 90 * s), (x - 60 * s, y + 130 * s), (x - 240 * s, y + 60 * s)], k=0.6)
    glow(c, x, y, 380 * s, '#ff9a3d', 0.35)
    shaded(c, lp, '#c8325e')
    face(c, x - 10 * s, y - 5 * s, 105 * s, expr, (0.2, 0), t, skin='#c8325e', eye_gap=0.5)
    # hard hat
    path = skia.Path()
    path.addArc(skia.Rect(x - 120 * s, y - 210 * s, x + 100 * s, y - 20 * s), 180, 180)
    path.close()
    c.save()
    c.translate(0, -10 * s)
    c.drawPath(path, P('#ffd23f'))
    c.restore()
    rrect(c, x - 140 * s, y - 130 * s, 260 * s, 26 * s, 13 * s, '#ffb02e')


def s_liver(c, t, d, p, b):
    bg_grad(c, '#ff9a4d', '#5b1fa8', '#d1366b')
    particles(c, t, seed=61, n=40, h='#fff3c4', a=0.4)
    # conveyor
    rrect(c, -40, 780, 2000, 60, 30, '#2a1050')
    for i in range(22):
        x = (i * 95 - t * 160) % 2000 - 40
        circle(c, x, 810, 16, '#4a2a7a')
    liver_char(c, 960, 560, 1.15, t, expr='happy' if t < bt(b, 1) else 'laugh')
    # machine sparkle around liver
    for i in range(6):
        an = t * 2 + i
        circle(c, 960 + math.cos(an) * 330, 560 + math.sin(an) * 200, 6, '#ffe14d', 0.7)
    # molecules along the belt
    for i in range(10):
        x = (i * 260 + t * 160) % 2300 - 200
        if x < 700:
            molecule(c, x, 735, 0.9, 'thc', t + i, glow_a=0.4)
        elif x > 1220:
            molecule(c, x, 735, 1.0, 'ohthc', t + i, glow_a=0.7)
    k1 = ramp(t, bt(b, 0) + 1.8, bt(b, 0) + 2.3)
    label(c, 'THC', 250, 560, 380, 720, a=k1, size=44)
    k2 = ramp(t, bt(b, 1), bt(b, 1) + 0.5)
    label(c, '11-HYDROXY-THC', 1560, 560, 1530, 720, a=k2, size=44, bg='#7a2a00')
    if t > bt(b, 1) + 1.5:
        kk = pop(t, bt(b, 1) + 1.5)
        rrect(c, 1450, 300, 330, 90, 45, '#ffe14d', clamp01(kk))
        text(c, 'BRAIN VIP', 1615, 360, 46 * kk + 1, '#5a1a00', clamp01(kk), weight=900, shadow=0)


def graph_axes(c, x0, y0, w, h, a=1.0, hours=4):
    line(c, [(x0, y0 - h), (x0, y0), (x0 + w, y0)], 6, '#ffffff', a)
    for i in range(hours + 1):
        x = x0 + w * i / hours
        line(c, [(x, y0), (x, y0 + 16)], 5, '#ffffff', a)
        text(c, f'{i}h', x, y0 + 62, 36, '#ffffff', a, weight=800, shadow=0)
    text(c, 'EFFECT', x0 - 30, y0 - h - 20, 32, '#ffffff', a, weight=800, align='left', shadow=0)


def effect_curve(hrs, onset=0.75, peak=2.2, height=1.0):
    if hrs < 0:
        return 0.0
    rise = 1 / (1 + math.exp(-(hrs - onset * 1.25) * 3.2))
    fall = math.exp(-max(0, hrs - peak) * 0.55)
    return height * rise * fall


def s_timeline(c, t, d, p, b):
    bg_grad(c, '#2a1a7a', '#120838')
    particles(c, t, seed=71, n=30, a=0.3)
    x0, y0, w, h = 260, 880, 1450, 560
    graph_axes(c, x0, y0, w, h)
    k = ramp(t, bt(b, 1) - 0.4, d - 0.5)
    hrs_max = 4 * eio(k)
    # bands
    kb1 = ramp(t, bt(b, 1) + 1.2, bt(b, 1) + 1.8)
    if kb1 > 0:
        c.drawRect(skia.Rect(x0 + w * 0.5 / 4, y0 - h, x0 + w * 1.0 / 4, y0), P('#2bd1ff', 0.22 * kb1))
        text(c, '30-60 MIN', x0 + w * 0.75 / 4, y0 - h - 30, 34, '#2bd1ff', kb1, weight=900)
        text(c, 'FIRST EFFECTS', x0 + w * 0.75 / 4, y0 - h + 10, 26, '#ffffff', kb1, weight=800)
    kb2 = ramp(t, bt(b, 2) + 0.4, bt(b, 2) + 1.0)
    if kb2 > 0:
        c.drawRect(skia.Rect(x0 + w * 1.5 / 4, y0 - h, x0 + w * 3.0 / 4, y0), P('#ffb02e', 0.22 * kb2))
        text(c, '1.5-3 HOURS', x0 + w * 2.25 / 4, y0 - h - 30, 34, '#ffb02e', kb2, weight=900)
        text(c, 'PEAK', x0 + w * 2.25 / 4, y0 - h + 10, 26, '#ffffff', kb2, weight=800)
    pts = []
    for i in range(121):
        hr = 4 * i / 120
        if hr > hrs_max:
            break
        pts.append((x0 + w * hr / 4, y0 - h * 0.82 * effect_curve(hr)))
    if len(pts) > 1:
        line(c, pts, 10, '#7dff6a')
        traveller(c, pts[-1][0], pts[-1][1], t)
    gk = pop(t, 0.4)
    glass(c, x0 + 10, y0 - 40, 0.4 * gk, 0.8, t=t)
    kt = pop(t, 0.5)
    text(c, 'EATEN OR DRUNK', 960, 150, 72 * kt + 1, '#ffffff', clamp01(kt), weight=900)


def s_second_glass(c, t, d, p, b):
    bg_grad(c, '#3a1a7a', '#140838')
    x0, y0, w, h = 220, 880, 1250, 560
    graph_axes(c, x0, y0, w, h)
    t1, t2, t3 = bt(b, 1, 2), bt(b, 2, 4), bt(b, 3, 6)
    m40 = 40 / 60
    # first curve up to 40 min
    k = ramp(t, 0.3, t1 + 1.0)
    pts = [(x0 + w * hr / 4, y0 - h * 0.6 * effect_curve(hr)) for hr in np.linspace(0, m40 * k, 30)]
    line(c, pts, 10, '#7dff6a')
    if t > t1:
        xm = x0 + w * m40 / 4
        line(c, [(xm, y0), (xm, y0 - h)], 4, '#ffffff', 0.5 * ramp(t, t1, t1 + 0.4))
        text(c, '40 MIN', xm, y0 - h - 20, 34, '#ffffff', ramp(t, t1, t1 + 0.4), weight=900)
        info_pill(c, xm + 230, y0 - 200, '"NOTHING..."', '', '#7dff6a', ramp(t, t1 + 0.3, t1 + 0.8) * (1 - ramp(t, t2, t2 + 0.3)))
    if t > t2:
        gk = pop(t, t2)
        xm = x0 + w * m40 / 4
        glass(c, xm, y0 - 40, 0.4 * gk, 0.8, t=t)
        text(c, '+1 GLASS', xm, y0 - 300, 50 * gk + 1, '#ffe14d', clamp01(gk), weight=900)
    if t > t3 - 0.2:
        k3 = eio(ramp(t, t3 - 0.2, t3 + 2.2))
        ptsA, ptsB = [], []
        for hr in np.linspace(0, 4 * k3, 80):
            e1 = effect_curve(hr)
            e2 = effect_curve(hr - m40)
            ptsA.append((x0 + w * hr / 4, y0 - h * 0.6 * e1))
            ptsB.append((x0 + w * hr / 4, y0 - h * 0.6 * (e1 + e2)))
        line(c, ptsA, 6, '#7dff6a', 0.4)
        line(c, ptsB, 12, '#ff3d6e')
        traveller(c, ptsB[-1][0], ptsB[-1][1], t, '#ff3d6e')
        kz = ramp(t, t3 + 0.8, t3 + 1.3)
        c.drawRect(skia.Rect(x0, y0 - h - 140, x0 + w, y0 - h * 0.85), P('#ff3d6e', 0.18 * kz))
        text(c, 'TOO MUCH', x0 + w - 20, y0 - h - 60, 46, '#ff3d6e', kz, weight=900, align='right')
    # reaction face
    expr = 'bored' if t < t3 + 0.6 else 'dazed'
    glow(c, 1700, 640, 330, '#ff3d6e' if expr == 'dazed' else '#7b5cff', 0.35)
    person(c, 1700, 1260, 1.5, dict(skin='#d99a6c', hair='#22122e', style='spiky', shirt='#2bd1ff'), expr=expr, t=t,
           arms=('down', 'down'), look=(-0.6, -0.3) if expr == 'bored' else (0.5 * osc(t, 0.7), 0))


SCENES = dict(holi=holi, glass=s_glass, shop=s_shop, party_clock=s_party, brain_q=s_brain_q, title=s_title,
              chapter=s_chapter, plant=s_plant, scroll=s_scroll, commission=s_commission, people_grid=s_people_grid,
              body=s_body, liver=s_liver, timeline=s_timeline, second_glass=s_second_glass)
