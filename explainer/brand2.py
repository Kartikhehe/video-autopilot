"""Premium Gen-Z channel branding: dark canvases, aurora gradients, film grain, editorial type
(heavy grotesk + italic serif accent), minimal glowing logo marks. No mascots.

python3 -m explainer.brand2   ->  out/branding2/<n>_<slug>_banner.png (2560x1440), _avatar.png (800x800), sheet.jpg
"""
import math
import os

import numpy as np
import skia

from . import art as A

OUT = os.path.join(A.HERE, '..', 'out', 'branding2')
BW, BH = 2560, 1440
SAFE = (507, 508, 2053, 931)          # YouTube banner area visible on every device


# ------------------------------------------------------------------ helpers
def F(name, w, size):
    f = skia.Font(A.typeface(name, w), size)
    f.setEdging(skia.Font.Edging.kSubpixelAntiAlias)
    f.setSubpixel(True)
    return f


def width(s, name, w, size, track=0.0):
    return F(name, w, size).measureText(s) + track * size * max(0, len(s) - 1)


def draw_text(c, s, x, y, size, name='Unbounded', w=900, color='#ffffff', a=1.0, shader=None, align='left', track=0.0,
              glow_c=None, glow_r=0):
    f = F(name, w, size)
    tw = width(s, name, w, size, track)
    x0 = x - tw / 2 if align == 'center' else (x - tw if align == 'right' else x)

    def run(paint):
        if track:
            xx = x0
            for ch in s:
                c.drawString(ch, xx, y, f, paint)
                xx += f.measureText(ch) + track * size
        else:
            c.drawString(s, x0, y, f, paint)
    if glow_c:
        p = A.P(glow_c, 0.55 * a, blur=glow_r)
        run(p)
    p = A.P(color, a)
    if shader is not None:
        p.setShader(shader)
        p.setAlphaf(a)
    run(p)
    return tw


def aurora(c, blobs):
    for x, y, r, col, a in blobs:
        p = A.P(col, a, blur=r * 0.55)
        c.drawCircle(x, y, r, p)


def grain(c, w, h, amt=0.07, seed=1):
    rng = np.random.default_rng(seed)
    n = rng.integers(0, 256, (h, w), dtype=np.uint8)
    rgba = np.empty((h, w, 4), dtype=np.uint8)
    rgba[..., 0] = n
    rgba[..., 1] = n
    rgba[..., 2] = n
    rgba[..., 3] = 255
    img = skia.Image.fromarray(rgba, colorType=skia.ColorType.kRGBA_8888_ColorType)
    p = skia.Paint()
    p.setAlphaf(amt)
    p.setBlendMode(skia.BlendMode.kOverlay)
    c.drawImage(img, 0, 0, skia.SamplingOptions(), p)


def grid(c, w, h, step=80, a=0.045, col='#ffffff'):
    p = A.P(col, a, stroke=1.2)
    for x in range(0, w + 1, step):
        c.drawLine(x, 0, x, h, p)
    for y in range(0, h + 1, step):
        c.drawLine(0, y, w, y, p)


def vignette(c, w, h, a=0.55):
    p = skia.Paint()
    p.setShader(A.rad((w / 2, h / 2), max(w, h) * 0.72, ['#000000', '#000000', '#000000'], [0, 0.55, 1], alphas=[0, 0, a]))
    c.drawRect(skia.Rect(0, 0, w, h), p)


def orb(c, x, y, r, c1, c2):
    """Glossy 3D sphere: radial gradient + specular highlight + rim light."""
    p = skia.Paint(AntiAlias=True)
    p.setShader(A.rad((x - r * 0.35, y - r * 0.4), r * 1.5, [A.shade(c1, 0.35), c1, c2, '#05040a'], [0, 0.35, 0.8, 1]))
    c.drawCircle(x, y, r, p)
    A.glow(c, x - r * 0.38, y - r * 0.42, r * 0.38, '#ffffff', 0.55)
    c.drawArc(skia.Rect(x - r * 0.92, y - r * 0.92, x + r * 0.92, y + r * 0.92), 20, 110, False, A.P(A.shade(c1, 0.3), 0.35, stroke=r * 0.05))


def chip(c, s, x, y, size=30, fg='#ffffff', border='#ffffff', bg='#ffffff', bg_a=0.06, a=1.0, name='SpaceGrotesk', w=700):
    tw = width(s, name, w, size)
    pw, ph = tw + size * 1.4, size * 1.9
    r = skia.RRect.MakeRectXY(skia.Rect(x, y - ph / 2, x + pw, y + ph / 2), ph / 2, ph / 2)
    c.drawRRect(r, A.P(bg, bg_a * a))
    c.drawRRect(r, A.P(border, 0.35 * a, stroke=2))
    draw_text(c, s, x + size * 0.7, y + size * 0.36, size, name, w, fg, a)
    return pw


def gstroke(p0, p1, cols, w):
    p = A.P('#ffffff', 1.0, stroke=w)
    p.setShader(A.lin(p0, p1, cols))
    return p


# ------------------------------------------------------------------ marks
def brain_top_paths(cx, cy, s):
    L = [(-14, -172), (-92, -176), (-166, -122), (-188, -28), (-172, 72), (-122, 150), (-44, 172), (-14, 146)]
    left = A.smooth_path([(cx + x * s, cy + y * s) for x, y in L], k=0.65)
    right = A.smooth_path([(cx - x * s, cy + y * s) for x, y in L], k=0.65)
    gyri = []
    for sg in (-1, 1):
        for pts in ([(-60, -120), (-110, -90), (-90, -40)], [(-150, -20), (-100, 10), (-140, 60)], [(-60, 20), (-80, 80), (-40, 110)]):
            gyri.append(A.smooth_path([(cx + sg * x * s, cy + y * s) for x, y in pts], closed=False, k=0.6))
    return left, right, gyri


def mark_glitch(c, cx, cy, s, cols=('#00f0ff', '#ff2bd6', '#ffffff')):
    """Brain line-mark with RGB split + horizontal slice displacement."""
    def draw(dx, col, a, blend=None):
        left, right, gyri = brain_top_paths(cx + dx, cy, s)
        p = A.P(col, a, stroke=22 * s)
        if blend:
            p.setBlendMode(blend)
        for path in [left, right] + gyri:
            c.drawPath(path, p)
    bands = [(-200, -120, 0), (-120, -70, 26), (-70, 10, 0), (10, 40, -34), (40, 120, 0), (120, 150, 18), (150, 220, 0)]
    for y0, y1, off in bands:
        c.save()
        c.clipRect(skia.Rect(cx - 400 * s, cy + y0 * s, cx + 400 * s, cy + y1 * s))
        draw(-12 * s + off * s, cols[0], 0.95, skia.BlendMode.kScreen)
        draw(12 * s + off * s, cols[1], 0.95, skia.BlendMode.kScreen)
        draw(off * s, cols[2], 1.0)
        c.restore()
    # scanline accents
    for y, w_, col in ((-95, 120, cols[0]), (25, 80, cols[1]), (135, 150, cols[0])):
        c.drawRect(skia.Rect(cx + 150 * s, cy + y * s, cx + (150 + w_) * s, cy + (y + 7) * s), A.P(col, 0.9))


def mark_neural_w(c, cx, cy, s, c1='#c6ff3d', c2='#00e5ff'):
    pts = [(-210, -130), (-105, 130), (0, -30), (105, 130), (210, -130)]
    P_ = [(cx + x * s, cy + y * s) for x, y in pts]
    path = skia.Path()
    path.moveTo(*P_[0])
    for p in P_[1:]:
        path.lineTo(*p)
    A.glow(c, cx, cy, 330 * s, c1, 0.28)
    gp = gstroke((cx - 210 * s, cy), (cx + 210 * s, cy), [c1, c2], 30 * s)
    c.drawPath(path, gp)
    # dendrite ticks
    for (x, y), (dx, dy) in zip(P_, [(-1, -1), (0, 1), (0, -1), (0, 1), (1, -1)]):
        for k in (-1, 1):
            ang = math.atan2(dy, dx) + k * 0.6
            x2, y2 = x + math.cos(ang) * 70 * s, y + math.sin(ang) * 70 * s
            c.drawLine(x, y, x2, y2, gstroke((x, y), (x2, y2), [c1, c2], 10 * s))
            A.circle(c, x2, y2, 9 * s, c2)
    for i, (x, y) in enumerate(P_):
        A.glow(c, x, y, 70 * s, c1 if i % 2 == 0 else c2, 0.6)
        A.circle(c, x, y, 26 * s, '#0a0a0f')
        c.drawCircle(x, y, 26 * s, A.P(c1 if i % 2 == 0 else c2, 1, stroke=10 * s))


def mark_neuron(c, cx, cy, s, cols=('#ff4fd8', '#8b5cff', '#3de0ff')):
    A.glow(c, cx, cy, 380 * s, cols[1], 0.35)
    # dendrites
    rng = np.random.default_rng(4)
    for i, ang in enumerate([200, 235, 270, 305, 160]):
        a = math.radians(ang)
        ln = (150 + 30 * rng.random()) * s
        p0 = (cx + math.cos(a) * 80 * s, cy + math.sin(a) * 80 * s)
        p1 = (cx + math.cos(a) * ln * 1.4, cy + math.sin(a) * ln * 1.4)
        mid = (cx + math.cos(a + 0.25) * ln, cy + math.sin(a + 0.25) * ln)
        path = A.smooth_path([p0, mid, p1], closed=False)
        c.drawPath(path, gstroke(p0, p1, [cols[0], cols[1]], 16 * s))
        for k in (-1, 1):
            b = a + k * 0.5
            c.drawLine(p1[0], p1[1], p1[0] + math.cos(b) * 45 * s, p1[1] + math.sin(b) * 45 * s,
                       gstroke(p1, (p1[0] + 1, p1[1] + 1), [cols[1], cols[1]], 9 * s))
    # axon
    ax = A.smooth_path([(cx + 80 * s, cy + 10 * s), (cx + 190 * s, cy + 60 * s), (cx + 300 * s, cy + 20 * s), (cx + 390 * s, cy + 80 * s)],
                       closed=False)
    c.drawPath(ax, gstroke((cx, cy), (cx + 390 * s, cy), [cols[1], cols[2]], 16 * s))
    for k, (dx, dy) in enumerate([(30, -40), (55, 10), (25, 55)]):
        x2, y2 = cx + (390 + dx) * s, cy + (80 + dy) * s
        c.drawLine(cx + 390 * s, cy + 80 * s, x2, y2, gstroke((0, 0), (1, 1), [cols[2], cols[2]], 9 * s))
        A.glow(c, x2, y2, 40 * s, cols[2], 0.8)
        A.circle(c, x2, y2, 12 * s, '#ffffff')
    # soma ring
    c.drawCircle(cx, cy, 82 * s, gstroke((cx - 80 * s, cy - 80 * s), (cx + 80 * s, cy + 80 * s), [cols[0], cols[2]], 24 * s))
    A.glow(c, cx, cy, 70 * s, '#ffffff', 0.45)
    A.circle(c, cx, cy, 26 * s, '#ffffff')


def mark_crack(c, cx, cy, s, c1='#ff7a1a', c2='#ff2e63', ink='#14061f'):
    """Squircle tile with a side-brain glyph split by a lightning crack."""
    r = 240 * s
    p = skia.Paint(AntiAlias=True)
    p.setShader(A.lin((cx - r, cy - r), (cx + r, cy + r), [c1, c2]))
    A.glow(c, cx, cy, 420 * s, c2, 0.35)
    c.drawRoundRect(skia.Rect(cx - r, cy - r, cx + r, cy + r), r * 0.42, r * 0.42, p)
    c.drawRoundRect(skia.Rect(cx - r, cy - r, cx + r, cy + r), r * 0.42, r * 0.42, A.P('#ffffff', 0.35, stroke=4 * s))
    bp = A.brain_path(cx, cy + 10 * s, 0.68 * s)
    c.drawPath(bp, A.P(ink, 1, stroke=24 * s))
    c.save()
    c.clipPath(bp, doAntiAlias=True)
    for pts in ([(-120, -60), (-60, -90), (0, -60)], [(30, -100), (90, -70), (130, -20)], [(-140, 30), (-80, 10), (-40, 50)],
                [(40, 20), (100, 40), (140, 10)]):
        c.drawPath(A.smooth_path([(cx + x * s, cy + y * s) for x, y in pts], closed=False), A.P(ink, 1, stroke=16 * s))
    c.restore()
    bolt = skia.Path()
    for i, (x, y) in enumerate([(20, -170), (-40, -10), (20, -10), (-30, 170), (80, -40), (20, -40), (70, -170)]):
        (bolt.moveTo if i == 0 else bolt.lineTo)(cx + x * s, cy + y * s)
    bolt.close()
    c.drawPath(bolt, A.P('#ffffff'))
    c.drawPath(bolt, A.P(ink, 1, stroke=10 * s))


# ------------------------------------------------------------------ options
OPTIONS = [
    dict(slug='mind_glitch', name='Mind Glitch', handle='@MindGlitch', tagline='why your brain does that.',
         bg='#06060c', blobs=[(260, 420, 520, '#00b8ff', 0.55), (2340, 1040, 560, '#ff2bd6', 0.55), (1280, 1500, 600, '#5b2bff', 0.35)],
         mark='glitch', words=[('MIND', 'Unbounded', 900, None), ('glitch', 'Instrument', 400, ('#00f0ff', '#ff2bd6'))],
         accent='#00f0ff', accent2='#ff2bd6', chips=['#dopamine', '#bhang', '#sleep', '#lust', '#caffeine', '#anxiety'],
         avatar_bg=('#140a2e', '#05040a')),
    dict(slug='wired_different', name='Wired Different', handle='@WiredDifferent', tagline='the science of why you can’t stop.',
         bg='#07080a', blobs=[(240, 1100, 560, '#7dff3d', 0.35), (2380, 380, 520, '#00e5ff', 0.4), (1300, -120, 500, '#2b6bff', 0.25)],
         mark='w', words=[('wired', 'Syne', 800, None), ('different.', 'Instrument', 400, ('#c6ff3d', '#00e5ff'))],
         accent='#c6ff3d', accent2='#00e5ff', chips=['habits', 'dopamine', 'addiction', 'focus', 'sleep', 'mind'],
         avatar_bg=('#0f1a12', '#040506')),
    dict(slug='neon_neuron', name='Neon Neuron', handle='@NeonNeuron', tagline='your brain, explained loudly.',
         bg='#08051a', blobs=[(300, 1000, 600, '#ff3dc8', 0.5), (2300, 420, 600, '#3de0ff', 0.4), (1280, -200, 560, '#7b3dff', 0.45)],
         mark='neuron', words=[('NEON', 'Unbounded', 900, ('#ff4fd8', '#8b5cff')), ('neuron', 'Instrument', 400, None)],
         accent='#ff4fd8', accent2='#3de0ff', chips=['brain', 'body', 'drugs', 'love', 'sleep', 'food'],
         avatar_bg=('#1a0b3a', '#06030f')),
    dict(slug='dimaag_kharab', name='Dimaag Kharab', handle='@DimaagKharab', tagline='science of things that mess with your head.',
         bg='#0b0610', blobs=[(260, 420, 560, '#ff7a1a', 0.45), (2320, 1060, 580, '#ff2e63', 0.45), (1300, 1550, 600, '#7b2bd1', 0.4)],
         mark='crack', words=[('dimaag', 'Bricolage', 800, None), ('kharab.', 'Instrument', 400, ('#ff9a3d', '#ff2e63'))],
         accent='#ff9a3d', accent2='#ff2e63', chips=['bhang', 'chai', 'reels', 'lust', 'exams', 'sleep'],
         deva='दिमाग़ ख़राब', avatar_bg=('#2a0a1a', '#07030a')),
]


def draw_mark(c, o, cx, cy, s):
    {'glitch': mark_glitch, 'w': mark_neural_w, 'neuron': mark_neuron, 'crack': mark_crack}[o['mark']](c, cx, cy, s)


def wordmark(c, o, x, y, size):
    """Two-part wordmark: heavy grotesk + italic serif accent. Returns total width."""
    xx = x
    for i, (s, fam, w, grad) in enumerate(o['words']):
        sz = size * (1.22 if fam == 'Instrument' else 1.0)
        tw = width(s, fam, w, sz)
        sh = A.lin((xx, y - sz), (xx + tw, y), list(grad)) if grad else None
        draw_text(c, s, xx, y, sz, fam, w, '#ffffff', shader=sh)
        xx += tw + size * (0.22 if i == 0 else 0)
    return xx - x


def wordmark_width(o, size):
    tot = 0
    for i, (s, fam, w, grad) in enumerate(o['words']):
        sz = size * (1.22 if fam == 'Instrument' else 1.0)
        tot += width(s, fam, w, sz) + (size * 0.22 if i == 0 else 0)
    return tot


def banner(o):
    s = skia.Surface(BW, BH)
    c = s.getCanvas()
    c.clear(A.col(o['bg']))
    aurora(c, o['blobs'])
    grid(c, BW, BH)
    # side decor in the desktop strip (outside the mobile-safe box)
    sx0, sy0, sx1, sy1 = SAFE
    # orbs sit at the edges of the strip, chips in clean columns that never touch them
    orb(c, 150, 600, 95, o['accent2'], A.shade(o['accent2'], -0.6))
    orb(c, 2420, 830, 80, o['accent'], A.shade(o['accent'], -0.6))
    orb(c, 2300, 480, 34, o['accent2'], A.shade(o['accent2'], -0.6))
    orb(c, 300, 960, 28, o['accent'], A.shade(o['accent'], -0.6))
    lefts = [(70, 760), (190, 860), (280, 670)]
    rights = [(2110, 600), (2160, 700), (2100, 800)]
    for i, tag in enumerate(o['chips']):
        x, y = (lefts if i % 2 == 0 else rights)[i // 2]
        chip(c, tag, x, y, 28, border=o['accent'] if i % 3 == 0 else '#ffffff')
    # centre lockup
    msz = 1.05 if o['mark'] != 'crack' else 0.78
    size = 150
    ww = wordmark_width(o, size)
    while ww + 420 > (sx1 - sx0) - 40:
        size -= 6
        ww = wordmark_width(o, size)
    total = 380 + ww
    x0 = (BW - total) / 2
    cy = 690
    if o['mark'] == 'neuron':
        draw_mark(c, o, x0 + 120, cy + 10, 0.5)
    else:
        draw_mark(c, o, x0 + 170, cy + 10, 0.62 * msz)
    wordmark(c, o, x0 + 400, cy + size * 0.38, size)
    ty = cy + size * 0.38 + 80
    draw_text(c, o['tagline'], x0 + 404, ty, 46, 'SpaceGrotesk', 500, '#ffffff', 0.82)
    if o.get('deva'):
        A.deva(c, o['deva'], x0 + 404, cy - size * 0.62, 48, h=o['accent'], a=0.95, align='left', shadow=0)
    # meta row
    meta = 'NEW EPISODE EVERY WEEK'
    draw_text(c, '●', sx0 + 40, 885, 22, 'SpaceGrotesk', 700, o['accent'], 1)
    draw_text(c, meta, sx0 + 74, 885, 24, 'SpaceGrotesk', 700, '#ffffff', 0.7, track=0.12)
    draw_text(c, 'BRAIN · BODY · HABITS', sx1 - 40, 885, 24, 'SpaceGrotesk', 700, '#ffffff', 0.7, align='right', track=0.12)
    draw_text(c, 'EST. 2026', sx1 - 40, 560, 24, 'SpaceGrotesk', 700, '#ffffff', 0.55, align='right', track=0.12)
    draw_text(c, o['handle'].upper(), sx0 + 40, 560, 24, 'SpaceGrotesk', 700, '#ffffff', 0.55, track=0.12)
    vignette(c, BW, BH, 0.5)
    grain(c, BW, BH, 0.09, seed=2)
    return s.makeImageSnapshot()


def avatar(o):
    N = 800
    s = skia.Surface(N, N)
    c = s.getCanvas()
    p = skia.Paint()
    p.setShader(A.rad((N / 2, N * 0.42), N * 0.75, list(o['avatar_bg'])))
    c.drawRect(skia.Rect(0, 0, N, N), p)
    aurora(c, [(140, 140, 260, o['accent2'], 0.45), (680, 680, 280, o['accent'], 0.4)])
    sc = {'glitch': 1.25, 'w': 1.25, 'neuron': 0.95, 'crack': 1.12}[o['mark']]
    dx = -115 * sc if o['mark'] == 'neuron' else 0
    draw_mark(c, o, N / 2 + dx, N / 2 + 10, sc)
    c.drawCircle(N / 2, N / 2, N / 2 - 30, A.P('#ffffff', 0.1, stroke=3))
    grain(c, N, N, 0.08, seed=5)
    return s.makeImageSnapshot()


def sheet(items):
    cw, ch = 1100, 619
    pad = 40
    s = skia.Surface(pad + 2 * (cw + 420 + pad), pad + 2 * (ch + 140))
    c = s.getCanvas()
    c.clear(A.col('#0b0b10'))
    samp = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)
    for i, (o, ban, av) in enumerate(items):
        col, row = i % 2, i // 2
        x = pad + col * (cw + 420 + pad)
        y = pad + row * (ch + 140) + 70
        draw_text(c, f'{i + 1}. {o["name"]}', x, y - 26, 40, 'Unbounded', 700, '#ffffff')
        draw_text(c, o['handle'] + '  ·  ' + o['tagline'], x + 520, y - 28, 24, 'SpaceGrotesk', 500, '#ffffff', 0.6)
        c.drawImageRect(ban, skia.Rect(x, y, x + cw, y + ch), samp)
        # safe area outline (scaled)
        k = cw / BW
        c.drawRect(skia.Rect(x + SAFE[0] * k, y + SAFE[1] * k, x + SAFE[2] * k, y + SAFE[3] * k), A.P('#ffffff', 0.35, stroke=2))
        # avatar circle big + small
        ax, ay, r = x + cw + 210, y + 200, 170
        c.save()
        path = skia.Path()
        path.addCircle(ax, ay, r)
        c.clipPath(path, doAntiAlias=True)
        c.drawImageRect(av, skia.Rect(ax - r, ay - r, ax + r, ay + r), samp)
        c.restore()
        for j, rr in enumerate((44, 20)):
            bx, by = ax - 60 + j * 110, y + 470
            c.save()
            path = skia.Path()
            path.addCircle(bx, by, rr)
            c.clipPath(path, doAntiAlias=True)
            c.drawImageRect(av, skia.Rect(bx - rr, by - rr, bx + rr, by + rr), samp)
            c.restore()
        draw_text(c, 'avatar  ·  small sizes', ax, y + 560, 22, 'SpaceGrotesk', 500, '#ffffff', 0.5, align='center')
    return s.makeImageSnapshot()


def main():
    os.makedirs(OUT, exist_ok=True)
    items = []
    for i, o in enumerate(OPTIONS):
        ban, av = banner(o), avatar(o)
        ban.save(os.path.join(OUT, f'{i + 1}_{o["slug"]}_banner.png'), skia.kPNG)
        av.save(os.path.join(OUT, f'{i + 1}_{o["slug"]}_avatar.png'), skia.kPNG)
        items.append((o, ban, av))
    sheet(items).save(os.path.join(OUT, 'sheet.jpg'), skia.kJPEG, 90)
    print('->', OUT)


if __name__ == '__main__':
    main()
