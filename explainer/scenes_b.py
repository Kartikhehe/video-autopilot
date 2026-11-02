"""Scenes: chapter 3 (your brain's own bhang), chapter 4 (dark side), chapter 5 (so, is bhang bad?), ending."""
import math

import numpy as np
import skia

from .art import *  # noqa: F401,F403
from .scenes_a import bt, HOLI, info_pill, mini_person, traveller, info_card, glass as _g  # noqa: F401


# ------------------------------------------------------------------ neurons
def neuron_shape(c, x, y, r, h, t, seed=0, a=1.0, arms=6, reach=170, expr=None, look=(0, 0)):
    rng = np.random.default_rng(seed)
    tips = []
    for i in range(arms):
        an = i / arms * 6.28 + rng.random() * 0.6
        ln = reach * (0.7 + rng.random() * 0.6)
        pts = [(x, y)]
        for j in range(1, 5):
            k = j / 4
            pts.append((x + math.cos(an + 0.25 * math.sin(j + i + t * 0.4)) * ln * k,
                        y + math.sin(an + 0.25 * math.sin(j + i + t * 0.4)) * ln * k))
        c.drawPath(smooth_path(pts, closed=False), P(h, a, stroke=r * 0.32))
        tip = pts[-1]
        for sgn in (-1, 1):
            bx = tip[0] + math.cos(an + sgn * 0.6) * ln * 0.25
            by = tip[1] + math.sin(an + sgn * 0.6) * ln * 0.25
            line(c, [tip, (bx, by)], r * 0.14, h, a)
        tips.append(tip)
    pth = smooth_path(blob_pts(x, y, r, 7, 0.15, seed, t))
    glow(c, x, y, r * 3.2, h, 0.35 * a)
    shaded(c, pth, h, a)
    if expr:
        face(c, x, y, r * 0.95, expr, look, t, skin=h, eye_gap=0.38, eye_r=0.3)
    return tips


def s_neurons(c, t, d, p, b):
    bg_radial(c, (960, 540), '#22106a', '#06021a', 1300)
    particles(c, t, seed=81, n=70, h='#9fb8ff', a=0.35, size=(1.5, 4))
    zoom = 1.0 + 0.25 * eio(t / d)
    c.save()
    c.translate(960, 540)
    c.scale(zoom, zoom)
    c.translate(-960, -540)
    rng = np.random.default_rng(5)
    nodes = [(rng.random() * 2100 - 90, rng.random() * 1200 - 60) for _ in range(16)]
    nodes[0] = (960, 540)
    cols = ['#ff4fa3', '#7b5cff', '#2bd1ff', '#ffb02e']
    links = []
    for i, (x, y) in enumerate(nodes):
        ds = sorted(range(len(nodes)), key=lambda j: math.dist(nodes[i], nodes[j]))
        for j in ds[1:3]:
            if (j, i) not in links:
                links.append((i, j))
    for i, j in links:
        line(c, [nodes[i], nodes[j]], 5, '#5a4bd6', 0.35)
    for k, (i, j) in enumerate(links):
        ph = (t * 0.7 + k * 0.37) % 1.6
        if ph < 1:
            x = lerp(nodes[i][0], nodes[j][0], ph)
            y = lerp(nodes[i][1], nodes[j][1], ph)
            traveller(c, x, y, t, cols[k % 4], 0.7)
    for i, (x, y) in enumerate(nodes):
        neuron_shape(c, x, y, 34 if i else 70, cols[i % 4], t, seed=i, arms=6, reach=110 if i else 230,
                     expr='happy' if i == 0 else None, look=(0.2, -0.2))
    c.restore()


def scientist(c, x, y, s, t, look_as, expr='neutral', arms=('down', 'down'), look=(0, 0), blink_off=0.0):
    la = dict(look_as)
    la.setdefault('shirt', '#f4f2ff')
    info = person(c, x, y, s, la, expr=expr, t=t, arms=arms, look=look, blink_off=blink_off)
    hx, hy = info['head']
    r = info['r']
    for sgn in (-1, 1):
        c.drawCircle(hx + sgn * r * 0.36, hy - r * 0.05, r * 0.3, P('#2bd1ff', 0.9, stroke=r * 0.08))
    line(c, [(hx - r * 0.06, hy - r * 0.05), (hx + r * 0.06, hy - r * 0.05)], r * 0.07, '#2bd1ff')
    return info


def flask(c, x, y, s, liquid, t, a=1.0):
    body = smooth_path([(x - 20 * s, y - 120 * s), (x + 20 * s, y - 120 * s), (x + 22 * s, y - 60 * s), (x + 80 * s, y + 10 * s),
                        (x + 70 * s, y + 40 * s), (x - 70 * s, y + 40 * s), (x - 80 * s, y + 10 * s), (x - 22 * s, y - 60 * s)], k=0.25)
    c.drawPath(body, P('#d9f3ff', 0.3 * a))
    c.save()
    c.clipPath(body, doAntiAlias=True)
    c.drawRect(skia.Rect(x - 90 * s, y - 20 * s, x + 90 * s, y + 50 * s), P(liquid, a))
    for i in range(4):
        by = y + 30 * s - ((t * 50 + i * 30) % 60) * s
        circle(c, x - 30 * s + i * 20 * s, by, 6 * s, '#ffffff', 0.6 * a)
    c.restore()
    glow(c, x, y + 10 * s, 120 * s, liquid, 0.4 * a)


def s_lab(c, t, d, p, b):
    bg_grad(c, '#2b1f8a', '#13093d')
    particles(c, t, seed=91, n=40, a=0.3)
    # lab back wall shelves
    for i in range(3):
        rrect(c, 120, 200 + i * 170, 520, 18, 9, '#3f2fa8')
        for j in range(4):
            flask(c, 190 + j * 120, 190 + i * 170, 0.45, HOLI[(i + j) % 6], t + i + j)
    rrect(c, 1590, 110, 260, 110, 24, '#ffffff', 0.95)
    text(c, '1992', 1720, 168, 54, '#2b1f8a', weight=900, shadow=0)
    text(c, 'JERUSALEM', 1720, 202, 26, '#7a6ad0', weight=800, shadow=0)
    t1, t2 = bt(b, 1, 6), bt(b, 2, 9)
    scientist(c, 820, 1010, 1.15, t, dict(skin='#f2c29b', hair='#6a4a3a', style='short'),
              expr='curious' if t < 2.5 else 'happy', arms=('down', 'point'), look=(0.6, -0.4))
    scientist(c, 1460, 1010, 1.15, t, dict(skin='#d99a6c', hair='#2b1a3a', style='curly'),
              expr='happy' if t < 2.5 else 'laugh', arms=('point', 'down'), look=(-0.6, -0.4), blink_off=1.2)
    rrect(c, 700, 800, 900, 50, 16, '#8a7ad8')
    rrect(c, 740, 850, 820, 230, 10, '#5a4ab0')
    flask(c, 1140, 760, 1.1, '#ff5fae', t)
    k = eout(ramp(t, 1.0, 3.2))
    if k > 0:
        my = lerp(640, 420, k)
        molecule(c, 1140, my + 8 * osc(t, 0.6), 1.5 * k, 'ana', t, glow_a=0.6)
    ka = pop(t, t1 + 0.6)
    if ka > 0:
        c.drawRect(skia.Rect(0, 0, W, H), P('#0a0420', 0.5 * clamp01(ka)))
        glow(c, 960, 420, 520, '#ffd23f', 0.5 * clamp01(ka))
        text(c, 'आनंद', 960, 470, 220 * ka + 1, '#ffe14d', clamp01(ka), shadow=0.5)
        text(c, 'ĀNANDA = BLISS', 960, 600, 70 * ka + 1, '#ffffff', clamp01(ka), weight=900)
    kb = pop(t, t2 + 0.1)
    if kb > 0:
        rrect(c, 960 - 520 * kb, 700, 1040 * kb, 150, 75, '#ff5fae', clamp01(kb))
        text(c, 'ANANDAMIDE', 960, 800, 96 * kb + 1, '#ffffff', clamp01(kb), weight=900)
        for i in range(10):
            an = i / 10 * 6.28 + t
            circle(c, 960 + math.cos(an) * 640, 775 + math.sin(an) * 140, 8, '#ffe14d', clamp01(kb))


# ------------------------------------------------------------------ synapse
def receptor(c, x, y, s, h='#ffb02e', occupied=None, t=0.0, flip=False, a=1.0):
    sg = -1 if flip else 1
    path = skia.Path()
    path.moveTo(x - 30 * s, y)
    path.lineTo(x - 30 * s, y + sg * 40 * s)
    path.lineTo(x - 12 * s, y + sg * 40 * s)
    path.lineTo(x - 12 * s, y + sg * 18 * s)
    path.quadTo(x, y + sg * 6 * s, x + 12 * s, y + sg * 18 * s)
    path.lineTo(x + 12 * s, y + sg * 40 * s)
    path.lineTo(x + 30 * s, y + sg * 40 * s)
    path.lineTo(x + 30 * s, y)
    path.close()
    c.drawPath(path, P(h, a))
    if occupied:
        circle(c, x, y + sg * 30 * s, 13 * s, occupied, a)
        glow(c, x, y + sg * 30 * s, 40 * s, occupied, 0.6 * a)


def s_synapse(c, t, d, p, b):
    flood = p.get('flood')
    bg_radial(c, (960, 540), '#3a1d8f' if not flood else '#1d4a3a', '#0c0628', 1200)
    particles(c, t, seed=101, n=40, a=0.25)
    # presynaptic terminal (top), postsynaptic (bottom)
    top = smooth_path([(560, -50), (1360, -50), (1400, 200), (1300, 380), (960, 430), (620, 380), (520, 200)], k=0.5)
    shaded(c, top, '#7b5cff', dark=-0.25)
    bot = smooth_path([(380, 1130), (380, 760), (700, 690), (960, 670), (1220, 690), (1540, 760), (1540, 1130)], k=0.5)
    shaded(c, bot, '#ff4fa3', dark=-0.22)
    t1, t2 = bt(b, 1, 3), bt(b, 2, 7)
    calm = 0.0
    if not flood:
        calm = ramp(t, t2 + 1.4, t2 + 2.6)
        dazed = 0.0
    else:
        dazed = ramp(t, t2 + 0.6, t2 + 2.0)
    # receptors on top terminal (CB1, pointing down)
    nrec = 7 if not flood else 9
    rec_x = [960 + (i - (nrec - 1) / 2) * 95 for i in range(nrec)]
    rec_y = [425 - 0.0028 * (x - 960) ** 2 for x in rec_x]
    for i, (rx, ry) in enumerate(zip(rec_x, rec_y)):
        occ = None
        if not flood and i in (2, 4) and t > t2 + 0.9:
            occ = '#ff5fae'
        if flood and t > t2 + 0.3 + i * 0.12:
            occ = '#3ee07f'
        receptor(c, rx, ry, 1.5, '#ffb02e', occupied=occ, t=t, flip=False)
    # signals (neurotransmitter dots) raining down
    rate = (1.0 - 0.75 * calm - 0.9 * dazed)
    for i in range(26):
        ph = (t * 0.9 * (0.6 + rate) + i * 0.137) % 1.0
        if (i % 4) / 4 > rate + 0.05:
            continue
        x = 700 + (i * 97) % 520
        y = lerp(440, 680, ph)
        circle(c, x, y, 9, '#5fd4ff', 0.9)
    # faces
    shout = not flood and t < t2 + 1.6
    face(c, 960, 230, 125, 'shock' if shout else ('calm' if not flood else ('dazed' if dazed > 0.3 else 'curious')),
         (0, 0.4), t, skin='#7b5cff', eye_gap=0.45)
    face(c, 960, 890, 135, 'think' if t < t1 else 'happy', (0, -0.4), t, skin='#ff4fa3', eye_gap=0.45)
    if shout:
        for i in range(3):
            r = 60 + ((t * 120 + i * 40) % 120)
            c.drawArc(skia.Rect(1100 - r, 190 - r, 1100 + r, 190 + r), -30, 60, False, P('#ffffff', 0.5, stroke=6))
    if not flood:
        # anandamide going backwards
        for i in range(2):
            k = eio(ramp(t, t1 + 1.6 + i * 0.4, t2 + 0.9))
            if k > 0:
                tx, ty = rec_x[(2, 4)[i]], rec_y[(2, 4)[i]] + 30
                x, y = lerp(900 + i * 120, tx, k), lerp(700, ty, k)
                if k < 1:
                    molecule(c, x, y, 0.8, 'ana', t, glow_a=0.7)
        ka = ramp(t, t1 + 1.6, t1 + 2.1)
        label(c, 'ANANDAMIDE', 1500, 560, 1020, 600, a=ka * (1 - ramp(t, t2 + 1.5, t2 + 2)), size=36)
        kc = pop(t, t2 + 1.4)
        if kc > 0:
            rrect(c, 1260, 620, 380, 110, 55, '#ffffff', clamp01(kc))
            text(c, 'calm down.', 1450, 692, 56 * kc + 1, '#d1366b', clamp01(kc), weight=900, shadow=0)
    else:
        kl = ramp(t, 0.6, 1.2)
        label(c, 'CB1 RECEPTOR', 1560, 300, rec_x[-1] + 10, rec_y[-1] + 20, a=kl * (1 - ramp(t, bt(b, 1) + 0.5, bt(b, 1) + 1)), size=36)
        if t > bt(b, 1):
            n = 34
            for i in range(n):
                rng = np.random.default_rng(i)
                sx, sy = (-80 if i % 2 else 2000), 500 + rng.random() * 160
                k = eio(ramp(t, bt(b, 1) + i * 0.05, t2 + 0.6 + i * 0.03))
                tx = rec_x[i % nrec] + (rng.random() - 0.5) * 60 * (i >= nrec)
                ty = rec_y[i % nrec] + 40 + (rng.random() * 80) * (i >= nrec)
                x, y = lerp(sx, tx, k), lerp(sy, ty, k) + 10 * osc(t, 0.8, i)
                if i < nrec and k >= 1:
                    continue
                molecule(c, x, y, 0.5, 'thc', t + i, glow_a=0.3)
            kt = ramp(t, bt(b, 1) + 0.6, bt(b, 1) + 1.1)
            label(c, 'THC', 300, 300, 200, 560, a=kt, size=40, bg='#0f5c36')
        if t > t2:
            kx = pop(t, t2 + 0.8)
            rrect(c, 1360, 560, 420, 120, 60, '#3ee07f', clamp01(kx))
            text(c, 'ALL BRAKES ON', 1570, 640, 46 * kx + 1, '#0b3b22', clamp01(kx), weight=900, shadow=0)


# ------------------------------------------------------------------ brain map
def s_brain_map(c, t, d, p, b):
    reg = p.get('region', 'hippo')
    pal = dict(hippo=('#3a1d8f', '#0e0730'), cereb=('#14507a', '#081a33'), amyg=('#6b1240', '#1d0718'),
               stem=('#0f5c4a', '#06201c'))[reg]
    bg_radial(c, (700, 520), pal[0], pal[1], 1300)
    particles(c, t, seed=111, n=40, a=0.3)
    key = {'hippo': 'hippo', 'cereb': 'cereb', 'amyg': 'amyg', 'stem': 'stem'}[reg]
    t0 = bt(b, 1, 1.0) if reg in ('hippo', 'stem') else 0.4
    k = ramp(t, t0, t0 + 0.8)
    regions = {key: k * (0.85 + 0.15 * osc(t, 1.2))}
    if reg == 'cereb':
        regions['basal'] = regions['cereb']
    expr = dict(hippo='dazed', cereb='dazed', amyg='calm' if t < bt(b, 1, 4) else 'scared', stem='calm')[reg]
    if reg == 'hippo' and t < bt(b, 1, 1):
        expr = 'curious'
    wob = 6 * osc(t, 0.6) if reg == 'cereb' else 0
    c.save()
    c.translate(640, 470)
    c.rotate(wob)
    c.translate(-640, -470)
    brain(c, 640, 470, 1.55, t, expr=None, regions=regions)
    c.restore()
    names = dict(hippo='HIPPOCAMPUS', cereb='CEREBELLUM + BASAL GANGLIA', amyg='AMYGDALA', stem='BRAINSTEM')
    anchors = dict(hippo=(625, 505), cereb=(895, 650), amyg=(530, 540), stem=(730, 780))
    lx, ly = anchors[reg]
    label(c, names[reg], 640, 990 if reg != 'stem' else 1000, lx, ly, a=ramp(t, t0 + 0.3, t0 + 0.8), size=38)
    if reg == 'hippo' and t < t0:
        kk = pop(t, 0.6)
        text(c, 'LOCATION', 1440, 470, 110 * kk + 1, '#ffffff', clamp01(kk), weight=900)
        text(c, 'MATTERS', 1440, 600, 110 * kk + 1, '#ffe14d', clamp01(kk), weight=900)
    x0, y0 = 1440, 520
    if reg == 'hippo' and t > t0 + 0.3:
        kb = pop(t, t0 + 0.3)
        info = person(c, x0, 1010, 1.3, dict(skin='#d99a6c', hair='#22122e', style='spiky', shirt='#2bd1ff'),
                      expr='talk' if t < bt(b, 2, 5) + 1.5 else 'dazed', t=t, arms=('down', 'shrug' if t > bt(b, 2, 5) + 1.2 else 'down'),
                      look=(-0.3, -0.4))
        rrect(c, x0 - 330, 170, 660, 170, 85, '#ffffff', clamp01(kb))
        msg = 'so I was saying...'
        n = len(msg)
        tt = bt(b, 2, 5)
        shown = int(n * ramp(t, t0 + 0.4, tt + 0.3))
        fade = ramp(t, tt + 0.6, tt + 2.2)
        s1 = msg[:shown]
        text(c, s1, x0, 275, 58, '#1b0f45', clamp01(kb) * (1 - ramp(fade, 0, 0.45)), weight=800, shadow=0)
        if fade > 0:
            for i in range(12):
                rng = np.random.default_rng(i)
                circle(c, x0 - 250 + i * 45, 260 - fade * (60 + rng.random() * 140), 8 * (1 - fade) + 1, '#ffffff', 1 - fade)
            text(c, '...wait, what?', x0, 275, 58, '#d1366b', ramp(fade, 0.55, 1.0), weight=900, shadow=0)
    if reg == 'cereb':
        kb = pop(t, 0.7)
        # clumsy walker on a tightrope
        rope_y = 760
        line(c, [(1150, rope_y), (1780, rope_y)], 8, '#ffffff', clamp01(kb))
        tilt = 18 * osc(t, 0.7)
        c.save()
        c.translate(1465, rope_y)
        c.rotate(tilt)
        person(c, 0, 0, 1.1, dict(skin='#f2c29b', hair='#5a2a10', style='long', shirt='#ffd23f'), expr='scared', t=t,
               arms=('up', 'up'), look=(0.4 * osc(t, 0.5), -0.2))
        c.restore()
        text(c, 'CLUMSY + SLOW', 1465, 900, 64 * kb + 1, '#4fd8ff', clamp01(kb), weight=900)
    if reg == 'amyg':
        t1 = bt(b, 1, 4)
        kb = pop(t, 0.6)
        flip = ramp(t, t1, t1 + 0.6)
        glow(c, x0, 520, 360, mix('#4dffb8', '#ff3d6e', flip), 0.4 * clamp01(kb))
        person(c, x0, 1000, 1.4, dict(skin='#b77a50', hair='#160b1c', style='bun', shirt=mix('#2bd17e', '#9d5cff', flip)),
               expr='calm' if flip < 0.5 else 'scared', t=t, arms=('down', 'down') if flip < 0.5 else ('face', 'face'),
               look=(0.6 * osc(t, 1.4) * flip, 0))
        if flip > 0:
            for i in range(6):
                an = i / 6 * 6.28 + t * 0.8
                x, y = x0 + math.cos(an) * 330, 540 + math.sin(an) * 250
                ellipse(c, x, y, 34, 22, '#ffffff', flip)
                circle(c, x - 6, y, 10, '#2a1640', flip)
        text(c, 'CALM' if flip < 0.5 else 'ANXIOUS?!', x0, 230, 90 * kb + 1, '#4dffb8' if flip < 0.5 else '#ff3d6e',
             clamp01(kb), weight=900)
    if reg == 'stem':
        kb = pop(t, t0 + 0.5)
        breath = 1 + 0.08 * osc(t, 0.25)
        for sg in (-1, 1):
            pth = smooth_path([(x0 + sg * 20, 380), (x0 + sg * 150 * breath, 420), (x0 + sg * 190 * breath, 640),
                               (x0 + sg * 110, 720), (x0 + sg * 40, 640)], k=0.6)
            c.save()
            c.translate(x0, 550)
            c.scale(clamp01(kb), clamp01(kb))
            c.translate(-x0, -550)
            shaded(c, pth, '#ff8fb3')
            c.restore()
        line(c, [(x0, 300), (x0, 450)], 26 * clamp01(kb), '#ff8fb3')
        kc = pop(t, bt(b, 2, 4) + 0.3)
        if kc > 0:
            rrect(c, x0 - 300, 780, 600, 140, 30, '#ffffff', clamp01(kc))
            text(c, 'FEW CB1 HERE', x0, 845, 50, '#0f5c4a', clamp01(kc), weight=900, shadow=0)
            text(c, 'breathing keeps going', x0, 893, 32, '#4a7a6a', clamp01(kc), weight=800, shadow=0)
        text(c, 'BREATHING', x0, 260, 70 * kb + 1, '#4dffb8', clamp01(kb), weight=900)


# ------------------------------------------------------------------ mouse
def mouse_char(c, x, y, s, t, h='#c9c3e6', expr='happy', belly=1.0, sniff=0.0, look=(1, 0)):
    tail = [(x - 120 * s, y + 20 * s), (x - 200 * s, y - 10 * s + 10 * s * osc(t, 0.8)), (x - 260 * s, y + 30 * s)]
    c.drawPath(smooth_path(tail, closed=False), P('#ff9ab8', stroke=10 * s))
    body = smooth_path(blob_pts(x, y, 115 * s, 8, 0.05, 3, t, sx=1.15 * belly, sy=0.85 * belly))
    shaded(c, body, h)
    hx, hy = x + 110 * s, y - 60 * s + 4 * s * osc(t, 3 * sniff + 0.01)
    for sg in (-1, 1):
        circle(c, hx - 30 * s + sg * 45 * s, hy - 70 * s, 42 * s, h)
        circle(c, hx - 30 * s + sg * 45 * s, hy - 70 * s, 26 * s, '#ffb3c8')
    head = smooth_path([(hx - 70 * s, hy - 40 * s), (hx + 20 * s, hy - 50 * s), (hx + 95 * s, hy + 5 * s), (hx + 20 * s, hy + 50 * s),
                        (hx - 70 * s, hy + 40 * s)], k=0.6)
    shaded(c, head, h)
    nose_r = 14 * s * (1 + 0.6 * sniff * max(0, osc(t, 4)))
    circle(c, hx + 95 * s, hy + 2 * s, nose_r, '#ff5f8f')
    for sg in (-1, 1):
        line(c, [(hx + 80 * s, hy + 10 * s), (hx + 140 * s, hy + 10 * s + sg * 20 * s)], 2.5 * s, '#ffffff', 0.8)
    eye(c, hx + 20 * s, hy - 12 * s, 17 * s, look=look, lid=0.0 if expr != 'dazed' else 0.5, lid_col=h)


def s_mouse(c, t, d, p, b):
    bg_grad(c, '#ffb02e', '#d1366b')
    particles(c, t, seed=121, n=40, h='#fff3c4', a=0.45)
    c.drawRect(skia.Rect(0, 820, W, H), P('#8a2f5a'))
    t1, t2 = bt(b, 1, 2), bt(b, 2, 6)
    # food pile
    pile = 1 - 0.7 * ramp(t, t1 + 2.5, t2)
    for i in range(int(14 * pile) + 1):
        x = 1350 + (i % 5) * 50 - (i // 5) * 25
        y = 820 - (i // 5) * 40
        ellipse(c, x, y, 34, 24, '#ffd23f')
        circle(c, x - 8, y - 5, 6, '#e0a020')
    # smell waves
    ks = ramp(t, t1 + 0.6, t1 + 1.2)
    for i in range(5):
        ph = (t * 0.8 + i * 0.2) % 1
        x = lerp(1300, 780, ph)
        pts = [(x + j * 12, 600 + 30 * math.sin(j * 0.6 + t * 3 + i)) for j in range(12)]
        line(c, pts, 8, '#ffffff', ks * (1 - ph) * 0.9)
    belly = 1 + 0.35 * ramp(t, t1 + 2.5, t2 + 1)
    glow(c, 620, 700, 330, '#3ee07f', 0.45 * ramp(t, 0.3, 1))
    mouse_char(c, 620, 740, 1.2, t, h='#d6cff2', belly=belly, sniff=ks)
    mouse_char(c, 240, 760, 0.8, t + 1, h='#bdb4e6', sniff=0.0)
    k0 = pop(t, 0.5)
    rrect(c, 520, 380, 200, 76, 38, '#3ee07f', clamp01(k0))
    text(c, '+THC', 620, 436, 50 * k0 + 1, '#0b3b22', clamp01(k0), weight=900, shadow=0)
    kn = pop(t, t2 + 0.6)
    if kn > 0:
        c.save()
        c.translate(1000, 240)
        c.rotate(-4)
        rrect(c, -380, -80, 760, 160, 40, '#ffffff', clamp01(kn))
        text(c, 'MUNCHIES = NOSE?', 0, 26, 72 * kn + 1, '#d1366b', clamp01(kn), weight=900, shadow=0)
        c.restore()
        label(c, 'SMELL ↑', 900, 470, 790, 620, a=ramp(t, t2 + 0.8, t2 + 1.3), size=36)


# ------------------------------------------------------------------ chapter 4
def ecg(c, x0, y0, w, t, speed, h='#ff3d6e', a=1.0, amp=80):
    pts = []
    for i in range(160):
        x = x0 + i * w / 160
        ph = ((i / 160) * speed * 3 - t * speed) % 1.0
        y = y0
        if 0.40 < ph < 0.44:
            y -= amp * math.sin((ph - 0.40) / 0.04 * math.pi)
        elif 0.44 < ph < 0.47:
            y += amp * 0.35 * math.sin((ph - 0.44) / 0.03 * math.pi)
        pts.append((x, y))
    line(c, pts, 6, h, a)


def heart(c, x, y, s, h='#ff3d5a', a=1.0):
    path = skia.Path()
    path.moveTo(x, y + 60 * s)
    path.cubicTo(x - 110 * s, y - 10 * s, x - 60 * s, y - 90 * s, x, y - 40 * s)
    path.cubicTo(x + 60 * s, y - 90 * s, x + 110 * s, y - 10 * s, x, y + 60 * s)
    path.close()
    glow(c, x, y, 150 * s, h, 0.5 * a)
    shaded(c, path, h, a)


def s_panic(c, t, d, p, b):
    t1, t2 = bt(b, 1, 3), bt(b, 2, 9)
    hosp = ramp(t, t2 - 0.2, t2 + 0.4)
    if hosp < 1:
        bg_radial(c, (960, 540), '#6b1240', '#12041c', 1200)
        for i in range(5):
            r = ((t * 220 + i * 260) % 1300)
            c.drawCircle(960, 540, r, P('#ff3d6e', 0.12 * (1 - r / 1300), stroke=30))
        rate = 1.0 + 1.8 * ramp(t, t1, t1 + 2)
        beat = 1 + 0.18 * max(0, osc(t, rate)) ** 4
        heart(c, 1500, 360, 1.3 * beat)
        ecg(c, 1180, 620, 640, t, rate)
        person(c, 700, 1180, 2.1, dict(skin='#d99a6c', hair='#22122e', style='spiky', shirt='#2bd1ff'),
               expr='neutral' if t < t1 else ('sick' if t < t1 + 3.5 else 'scared'), t=t, arms=('face', 'stomach') if t > t1 + 2 else ('down', 'down'),
               look=(0.4 * osc(t, 1.7), 0))
        words = [('RACING HEART', t1 + 1.6), ('NAUSEA', t1 + 3.0), ('PANIC', t1 + 3.9)]
        for i, (w_, tw) in enumerate(words):
            k = pop(t, tw)
            text(c, w_, 1500, 780 + i * 80, 58 * k + 1, ['#ff3d6e', '#7dff6a', '#ffe14d'][i], clamp01(k), weight=900)
        if t < t1:
            k = pop(t, 0.5)
            text(c, 'NOT DEADLY', 1450, 860, 86 * k + 1, '#ffffff', clamp01(k), weight=900)
            text(c, '≠ HARMLESS', 1450, 960, 86 * pop(t, 1.3) + 1, '#ff3d6e', clamp01(pop(t, 1.3)), weight=900)
    if hosp > 0:
        c.saveLayerAlpha(None, int(255 * hosp))
        bg_grad(c, '#2a6b8a', '#0e2a40')
        rrect(c, 120, 140, 420, 300, 20, '#1b3a55')
        ecg(c, 150, 300, 360, t, 2.6, h='#4dffb8', amp=60)
        rrect(c, 1500, 160, 20, 600, 10, '#c0d6e8')
        rrect(c, 1440, 160, 140, 180, 30, '#bde8ff')
        line(c, [(1510, 340), (1510, 500), (1300, 620)], 5, '#bde8ff')
        rrect(c, 420, 640, 1100, 90, 30, '#f4f2ff')
        rrect(c, 380, 720, 1180, 70, 20, '#7a8ab0')
        for x in (440, 1500):
            rrect(c, x - 15, 790, 30, 200, 10, '#5a6a90')
        person(c, 680, 700, 1.1, dict(skin='#d99a6c', hair='#22122e', style='spiky', shirt='#bde8ff'), expr='scared', t=t,
               arms=('down', 'down'), look=(0.6, -0.2), sit=True)
        rrect(c, 820, 600, 640, 120, 50, '#9ab8ff')
        c.restore()


def s_loop(c, t, d, p, b):
    bg_radial(c, (960, 540), '#3a1d6e', '#0e0628', 1200)
    particles(c, t, seed=131, n=30, a=0.25)
    t1, t2 = bt(b, 1, 4), bt(b, 2, 10)
    ka = 1 - ramp(t, t1 - 0.3, t1 + 0.2)
    if ka > 0:
        rrect(c, 460, 170, 1000, 760, 30, '#ffffff', ka)
        rrect(c, 460, 170, 1000, 110, 30, '#9d5cff', ka)
        text(c, 'EVERY DAY', 960, 250, 60, '#ffffff', ka, weight=900, shadow=0)
        for i in range(28):
            x, y = 540 + (i % 7) * 140, 340 + (i // 7) * 145
            rrect(c, x - 55, y - 10, 110, 125, 14, '#f0ecff', ka)
            k = ramp(t, 0.4 + i * 0.09, 0.6 + i * 0.09)
            if k > 0:
                c.save()
                c.translate(x, y + 105)
                c.scale(0.24 * back(k), 0.24 * back(k))
                _g(c, 0, 0, 1.0, 0.8, t=t, garnish=False)
                c.restore()
    kb = ramp(t, t1, t1 + 0.4)
    if kb > 0:
        for i in range(10):
            x = 960 + (i - 4.5) * 150
            hl = i in (1, 4, 7)
            k = pop(t, t1 + 0.2 + i * 0.07)
            mini_person(c, x, 640, 2.4 * k, '#ff3d6e' if (hl and t > t1 + 2.2) else '#7a6ad0', clamp01(kb), head=SKINS[i % 6])
            if hl and t > t1 + 2.2:
                glow(c, x, 580, 120, '#ff3d6e', 0.4)
        kk = pop(t, t1 + 2.2)
        text(c, '3 IN 10', 960, 330, 170 * kk + 1, '#ff3d6e', clamp01(kk), weight=900)
        text(c, 'people who use cannabis have some level of cannabis use disorder', 960, 860, 38, '#ffffff',
             ramp(t, t1 + 2.6, t1 + 3.1), weight=700)
        kc = ramp(t, t2, t2 + 0.5)
        if kc > 0:
            rrect(c, 520, 920, 880, 100, 50, '#ffe14d', kc)
            text(c, 'START YOUNG + USE OFTEN = HIGHER RISK', 960, 985, 38, '#3a1d10', kc, weight=900, shadow=0)


def s_teen(c, t, d, p, b):
    bg_grad(c, '#ffb02e', '#7a2a8c', '#d1366b')
    particles(c, t, seed=141, n=40, h='#fff3c4', a=0.4)
    brain(c, 900, 520, 1.5, t, expr='curious', look=(0.4, -0.3))
    # scaffolding
    for x in (480, 1320):
        line(c, [(x, 160), (x, 1000)], 14, '#ffd23f')
    for y in (300, 520, 740):
        line(c, [(470, y), (1330, y)], 12, '#ffd23f', 0.9)
    # crane
    line(c, [(1580, 1000), (1580, 120), (1100, 120)], 22, '#ff8a3d')
    line(c, [(1250, 120), (1250, 260 + 20 * osc(t, 0.4))], 4, '#ffffff')
    rrect(c, 1215, 260 + 20 * osc(t, 0.4), 70, 40, 8, '#2bd1ff')
    # wires being laid
    k = ramp(t, 0.6, d - 0.5)
    rng = np.random.default_rng(7)
    nodes = [(650 + rng.random() * 520, 330 + rng.random() * 320) for _ in range(9)]
    nshow = int(k * 8)
    for i in range(nshow):
        line(c, [nodes[i], nodes[i + 1]], 7, '#ffe14d', 0.9)
        glow(c, nodes[i + 1][0], nodes[i + 1][1], 40, '#ffe14d', 0.6)
    # sign
    c.save()
    c.translate(400, 900)
    c.rotate(-6)
    rrect(c, -260, -70, 520, 140, 20, '#ffd23f')
    for i in range(6):
        c.save()
        c.clipRect(skia.Rect(-260, -70, 260, -40))
        c.drawRect(skia.Rect(-280 + i * 100, -70, -230 + i * 100, -40), P('#1b0f45'))
        c.restore()
    text(c, 'UNDER CONSTRUCTION', 0, 40, 40, '#1b0f45', weight=900, shadow=0)
    c.restore()
    kb = ramp(t, bt(b, 1, 3), bt(b, 1, 3) + 0.6)
    label(c, 'BRAIN\'S OWN CANNABIS SYSTEM', 1450, 700, nodes[4][0], nodes[4][1], a=kb, size=34)
    text(c, 'TEEN BRAIN', 1500, 920, 90, '#ffffff', ramp(t, 0.3, 0.8), weight=900)


def s_bars(c, t, d, p, b):
    bg_grad(c, '#2a1050', '#0c0628')
    particles(c, t, seed=151, n=30, a=0.25)
    t1, t2 = bt(b, 1, 6), bt(b, 2, 10)
    x0, y0 = 360, 900
    bars = [('NEVER', 1.0, '#7a6ad0', 0.6), ('DAILY', 3.2, '#ff7a1a', 3.2), ('DAILY + HIGH POTENCY', 4.8, '#ff3d6e', t1 + 0.4)]
    line(c, [(x0 - 30, y0), (x0 + 1300, y0)], 6, '#ffffff')
    for i, (name, v, colr, tt) in enumerate(bars):
        k = eout(ramp(t, tt, tt + 1.4))
        x = x0 + 80 + i * 420
        h = 120 * v * k
        rrect(c, x, y0 - h, 260, h + 2, 22, colr)
        rrect(c, x, y0 - h, 70, h + 2, 22, shade(colr, 0.2))
        if k > 0:
            text(c, f'~{v:.0f}x' if v > 1 else '1x', x + 130, y0 - h - 30, 74, colr, clamp01(k * 2), weight=900)
        text(c, name, x + 130, y0 + 60, 32 if len(name) < 12 else 26, '#ffffff', ramp(t, tt, tt + 0.4), weight=800)
    text(c, 'ODDS OF A PSYCHOTIC DISORDER', 960, 140, 56, '#ffffff', ramp(t, 0.2, 0.7), weight=900)
    kl = pop(t, t2 + 0.4)
    if kl > 0:
        c.save()
        c.translate(1560, 300)
        c.rotate(-5)
        rrect(c, -280, -70, 560, 140, 30, '#ffffff', clamp01(kl))
        text(c, 'LINK ≠ PROOF', 0, 24, 62 * kl + 1, '#1b0f45', clamp01(kl), weight=900, shadow=0)
        c.restore()


# ------------------------------------------------------------------ chapter 5
def s_balance(c, t, d, p, b):
    bg_grad(c, '#ffd23f', '#d1366b', '#ff8a3d')
    particles(c, t, seed=161, n=40, h='#ffffff', a=0.4)
    t1 = bt(b, 1, 3)
    if t < t1:
        k = pop(t, 0.3)
        glow(c, 960, 620, 400, '#ff3d6e', 0.4)
        _g(c, 960, 860, 1.6 * k, 0.8, t=t, glowc='#c8ffb0')
        horns = 1 - ramp(t, t1 - 1.6, t1 - 1.2)
        fall = ramp(t, t1 - 1.6, t1)
        for sg in (-1, 1):
            hx = 960 + sg * 110 + sg * 200 * fall
            hy = 420 - 10 + 600 * fall ** 2
            path = skia.Path()
            path.moveTo(hx - 34, hy + 20)
            path.quadTo(hx + sg * 10, hy - 50, hx + sg * 40, hy - 90)
            path.quadTo(hx + sg * 20, hy - 20, hx + 34, hy + 20)
            path.close()
            c.drawPath(path, P('#e0203a', clamp01(k)))
        text(c, 'EVIL?', 960, 200, 130 * k + 1, '#ffffff', clamp01(k), weight=900)
        kk = pop(t, t1 - 1.4)
        if kk > 0:
            text(c, 'NOT EXACTLY.', 960, 330, 80 * kk + 1, '#1b0f45', clamp01(kk), weight=900, shadow=0)
        return
    k = ramp(t, t1, t1 + 0.6)
    tilt = -14 * eio(ramp(t, t1 + 3.5, t1 + 5.0))
    rrect(c, 940, 360, 40, 560, 20, '#3a1d6e')
    rrect(c, 760, 900, 400, 50, 25, '#3a1d6e')
    c.save()
    c.translate(960, 360)
    c.rotate(-tilt)
    rrect(c, -620, -16, 1240, 32, 16, '#5a2a9e')
    for sg in (-1, 1):
        px = sg * 580
        dy = 0
        line(c, [(px, 0), (px - 120, 260), (px + 120, 260), (px, 0)], 5, '#ffffff', k)
        c.save()
        c.translate(px, 260)
        c.rotate(tilt)
        ellipse(c, 0, 0, 200, 30, '#5a2a9e', k)
        if sg < 0:
            _g(c, 0, -10, 0.55, 0.8, t=t)
            for i in range(5):
                circle(c, -120 + i * 60, -40 - 20 * osc(t, 0.6, i), 16, HOLI[i], k)
        else:
            for i in range(12):
                gx = -150 + (i % 6) * 60
                gy = -10 - (i // 6) * 140
                if t > t1 + 2.0 + i * 0.12:
                    _g(c, gx, gy, 0.4, 0.8, t=t + i, garnish=False)
        c.restore()
    c.restore()
    text(c, 'ONCE, AT HOLI', 380, 820, 56, '#1b0f45', ramp(t, t1 + 0.4, t1 + 0.9), weight=900, shadow=0)
    text(c, 'EVERY DAY, TO FEEL OKAY', 1440, 1000, 44, '#1b0f45',
         ramp(t, t1 + 1.8, t1 + 2.3), weight=900, shadow=0)


def snail(c, x, y, s, t, letter=True):
    body = smooth_path([(x - 120 * s, y), (x + 140 * s, y - 5 * s), (x + 170 * s, y - 50 * s), (x + 130 * s, y - 70 * s),
                        (x + 100 * s, y - 20 * s), (x - 100 * s, y - 20 * s)], k=0.4)
    c.drawPath(body, P('#ffcf8a'))
    for sg in (0, 1):
        line(c, [(x + 140 * s, y - 60 * s), (x + 150 * s + sg * 30 * s, y - 120 * s)], 6 * s, '#ffcf8a')
        circle(c, x + 150 * s + sg * 30 * s, y - 122 * s, 9 * s, '#2a1640')
    shell = skia.Path()
    shell.addCircle(x, y - 80 * s, 85 * s)
    shaded(c, shell, '#ff7a9a')
    pts = [(x + math.cos(a) * a * 9 * s, y - 80 * s + math.sin(a) * a * 9 * s) for a in np.linspace(0, 9, 40)]
    c.drawPath(smooth_path(pts, closed=False), P('#c8325e', stroke=7 * s))
    if letter:
        c.save()
        c.translate(x + 10 * s, y - 190 * s)
        c.rotate(-8)
        rrect(c, -90 * s, -55 * s, 180 * s, 110 * s, 10 * s, '#ffffff')
        line(c, [(-90 * s, -55 * s), (0, 5 * s), (90 * s, -55 * s)], 5 * s, '#d0c8f0')
        text(c, 'TOO MUCH!', 0, 40 * s, 26 * s, '#d1366b', weight=900, shadow=0)
        c.restore()


def s_hidden(c, t, d, p, b):
    bg_grad(c, '#ff8a3d', '#7a2a8c', '#d1366b')
    particles(c, t, seed=171, n=40, h='#fff3c4', a=0.4)
    t1 = bt(b, 1, 3)
    # glass with mystery strength meter
    _g(c, 520, 860, 1.4, 0.8, t=t, glowc='#c8ffb0')
    k = pop(t, 0.3)
    text(c, '?', 520, 600, 220 * k + 1, '#ffffff', clamp01(k), weight=900)
    cx, cy = 520, 300
    c.drawArc(skia.Rect(cx - 170, cy - 170, cx + 170, cy + 170), 180, 180, False, P('#ffffff', 0.9, stroke=26))
    c.drawArc(skia.Rect(cx - 170, cy - 170, cx + 170, cy + 170), 300, 60, False, P('#ff3d6e', 0.9, stroke=26))
    ang = math.radians(180 + 90 + 80 * math.sin(t * 2.3) * math.cos(t * 0.9))
    line(c, [(cx, cy), (cx + math.cos(ang) * 150, cy + math.sin(ang) * 150)], 12, '#1b0f45')
    circle(c, cx, cy, 20, '#1b0f45')
    text(c, 'STRENGTH?', cx, cy + 90, 46, '#ffffff', weight=900)
    if t > t1:
        kk = ramp(t, t1, t1 + 0.4)
        clock(c, 1500, 300, 120, 3 + 4 * eio(ramp(t, t1, d)), a=kk)
        sx = lerp(950, 1350, ramp(t, t1, d + 1))
        snail(c, sx, 900, 1.2, t)
        brain(c, 1700, 700, 0.55, t, expr='curious' if t < d - 1.5 else 'shock', look=(-0.8, 0.3))
        text(c, 'HOURS TOO LATE', 1300, 530, 60, '#ffe14d', ramp(t, t1 + 1.5, t1 + 2), weight=900)


def key_ring(c, x, y, s, t, a=1.0):
    c.drawCircle(x, y, 40 * s, P('#ffd23f', a, stroke=10 * s))
    for i, an in enumerate((60, 100, 140)):
        c.save()
        c.translate(x, y)
        c.rotate(an + 6 * osc(t, 1.2, i))
        circle(c, 0, 75 * s, 26 * s, '#ffd23f', a)
        circle(c, 0, 75 * s, 10 * s, '#7a4a00', a)
        rrect(c, -8 * s, 95 * s, 16 * s, 90 * s, 6 * s, '#ffd23f', a)
        rrect(c, 0, 150 * s, 22 * s, 12 * s, 3 * s, '#ffd23f', a)
        rrect(c, 0, 170 * s, 16 * s, 12 * s, 3 * s, '#ffd23f', a)
        c.restore()
    glow(c, x, y + 80 * s, 160 * s, '#ffd23f', 0.4 * a)


def leaf_thief(c, x, y, s, t):
    leaf(c, x, y, 0.9 * s, h='#2bd17e')
    face(c, x, y - 120 * s, 55 * s, 'happy', (-0.6, 0), t, skin='#2bd17e', eye_gap=0.45)
    for sg in (-1, 1):
        line(c, [(x + sg * 20 * s, y + 50 * s), (x + sg * 35 * s + 20 * s * osc(t, 3, sg), y + 140 * s)], 12 * s, '#1f9d5a')


def s_bliss(c, t, d, p, b):
    t1, t2, t3 = bt(b, 1, 3), bt(b, 2, 5), bt(b, 3, 8)
    warm = ramp(t, t2, t2 + 1.5)
    bg_radial(c, (960, 520), mix('#5b1fa8', '#ffb02e', warm), mix('#140838', '#7a1a4a', warm), 1300)
    particles(c, t, seed=181, n=60, h='#ffe8a8', a=0.5)
    # plant fading on the left at "never in the plant"
    kp = win(t, t1 - 0.2, t2 + 0.4, 0.4)
    if kp > 0:
        leaf(c, 420, 760, 1.2, h='#2bd17e', a=kp)
        c.drawPath(smooth_path([(270, 500), (570, 800), (570, 800)], closed=False), P('#ff3d6e', kp, stroke=18))
        line(c, [(280, 500), (570, 800)], 18, '#ff3d6e', kp)
        line(c, [(570, 500), (280, 800)], 18, '#ff3d6e', kp)
    brain(c, 980, 500, 1.35, t, expr='calm' if t < t3 + 0.8 else 'shock', look=(0.3, -0.2) if t < t3 + 0.8 else (-0.8, 0.3),
          glow_c='#ffd23f', glow_a=0.25 + 0.5 * warm, h=mix('#ff7eb6', '#ffb0c8', warm))
    for i in range(10):
        if t > t2 + i * 0.15:
            an = i / 10 * 6.28 + t * 0.35
            molecule(c, 980 + math.cos(an) * 520, 520 + math.sin(an) * 340, 0.6, 'ana', t + i, glow_a=0.5)
    # keys
    if t3 > 0:
        steal = eio(ramp(t, t3 + 0.8, t3 + 2.4))
        kx, ky = lerp(1240, 1900, steal), lerp(830, 760, steal)
        key_ring(c, kx, ky, 0.9, t, a=ramp(t, 0.5, 1.2))
        if t > t3 - 0.2:
            tx = lerp(2100, 1360, eout(ramp(t, t3 - 0.2, t3 + 0.8))) + 660 * steal
            leaf_thief(c, tx, 860, 1.0, t)
        if t > t3 + 0.4:
            kk = pop(t, t3 + 0.4)
            text(c, 'JUST BORROWING!', 1500, 560, 52 * kk + 1, '#2bd17e', clamp01(kk) * (1 - steal), weight=900)


def s_end_card(c, t, d, p, b):
    bg_radial(c, (960, 540), '#3a1d8f', '#0a0420', 1200)
    particles(c, t, seed=191, n=70, h='#ffe8a8', a=0.5)
    k = ramp(t, 0.3, 1.2)
    glow(c, 960, 400, 300, '#ffd23f', 0.5 * k)
    c.save()
    c.translate(960, 420)
    c.scale(0.55 * back(k), 0.55 * back(k))
    brain(c, 0, 0, 1.0, t, expr='calm', glow_c='#ffd23f', glow_a=0.6)
    c.restore()
    text(c, p.get('text', ''), 960, 820, 84, '#ffffff', ramp(t, 0.8, 1.6), weight=900)


def s_outro(c, t, d, p, b):
    bg_grad(c, '#ff4fa3', '#3a1d8f')
    bokeh(c, t, seed=201, colors=('#ffffff', '#ffd23f', '#2bd1ff'), a=0.18)
    particles(c, t, seed=202, n=50, a=0.4)
    k = back(ramp(t, 0.1, 0.8))
    c.save()
    c.translate(700, 520)
    c.scale(0.9 * k, 0.9 * k)
    c.rotate(4 * osc(t, 0.5))
    brain(c, 0, 0, 1.0, t, expr='happy', look=(0.6, 0.1))
    c.restore()
    # waving arm
    line(c, [(860, 560), (980, 470 + 30 * osc(t, 1.6)), (1010, 380 + 50 * osc(t, 1.6))], 24, '#ff7eb6')
    circle(c, 1010, 380 + 50 * osc(t, 1.6), 26, '#ff7eb6')
    kb = pop(t, bt(b, 0, 0.5) + 1.6)
    press = win(t, bt(b, 0, 0.5) + 2.6, bt(b, 0, 0.5) + 2.9, 0.1)
    sub = t > bt(b, 0, 0.5) + 2.75
    c.save()
    c.translate(1400, 520)
    c.scale(clamp01(kb) * (1 - 0.08 * press), clamp01(kb) * (1 - 0.08 * press))
    rrect(c, -260, -70, 520, 140, 70, '#7a7a8a' if sub else '#ff2e4d')
    text(c, 'SUBSCRIBED' if sub else 'SUBSCRIBE', 0, 20, 58, '#ffffff', weight=900, shadow=0.2)
    c.restore()
    if sub:
        kk = pop(t, bt(b, 0, 0.5) + 2.9)
        c.save()
        c.translate(1720, 520)
        c.rotate(15 * osc(t, 3) * (1 - ramp(t, bt(b, 0, 0.5) + 3, bt(b, 0, 0.5) + 4.5)))
        circle(c, 0, 0, 70 * kk, '#ffffff')
        rrect(c, -30 * kk, -32 * kk, 60 * kk, 56 * kk, 26 * kk, '#ffb02e')
        rrect(c, -40 * kk, 16 * kk, 80 * kk, 12 * kk, 6 * kk, '#ffb02e')
        circle(c, 0, 36 * kk, 9 * kk, '#ffb02e')
        c.restore()
    # cursor
    ck = ramp(t, bt(b, 0, 0.5) + 1.9, bt(b, 0, 0.5) + 2.6)
    if 0 < ck and t < bt(b, 0, 0.5) + 4:
        cx, cy = lerp(1800, 1440, eio(ck)), lerp(950, 560, eio(ck))
        path = skia.Path()
        path.moveTo(cx, cy)
        path.lineTo(cx, cy + 70)
        path.lineTo(cx + 18, cy + 54)
        path.lineTo(cx + 34, cy + 86)
        path.lineTo(cx + 46, cy + 80)
        path.lineTo(cx + 30, cy + 48)
        path.lineTo(cx + 52, cy + 46)
        path.close()
        c.drawPath(path, P('#ffffff'))
        c.drawPath(path, P('#1b0f45', stroke=4))


SCENES = dict(neurons=s_neurons, lab=s_lab, synapse=s_synapse, brain_map=s_brain_map, mouse=s_mouse, panic=s_panic,
              loop=s_loop, teen=s_teen, bars=s_bars, balance=s_balance, hidden=s_hidden, bliss=s_bliss,
              end_card=s_end_card, outro=s_outro)
