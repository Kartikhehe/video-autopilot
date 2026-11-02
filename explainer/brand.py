"""Channel branding options: banners (2560x1440, text inside YouTube's 1546x423 safe area) and
profile photos (800x800, read as a small circle).

    python3 -m explainer.brand            # all options + comparison sheet -> out/branding/
"""
import math
import os

import numpy as np
import skia

from explainer import art as A

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'out', 'branding')
BW, BH = 2560, 1440
SAFE = ((BW - 1546) / 2, (BH - 423) / 2, (BW + 1546) / 2, (BH + 423) / 2)   # x0, y0, x1, y1
DEVA_FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'branding', 'Baloo2-800.ttf')


# ------------------------------------------------------------------ helpers
def bg(c, w, h, stops, angle=(0.0, 0.0, 1.0, 1.0)):
    p = skia.Paint()
    p.setShader(A.lin((angle[0] * w, angle[1] * h), (angle[2] * w, angle[3] * h), stops))
    c.drawRect(skia.Rect(0, 0, w, h), p)


def bokeh(c, w, h, seed, colors, n=18, a=0.22, rmin=60, rmax=260, avoid=None):
    rng = np.random.default_rng(seed)
    for i in range(n):
        x, y = rng.random() * w, rng.random() * h
        r = rmin + rng.random() * (rmax - rmin)
        A.glow(c, x, y, r, colors[i % len(colors)], a)


def sparkles(c, w, h, seed, n=70, col='#ffffff', a=0.5, avoid=None):
    rng = np.random.default_rng(seed)
    for i in range(n):
        x, y = rng.random() * w, rng.random() * h
        r = 2 + rng.random() * 5
        if avoid and avoid[0] - 40 < x < avoid[2] + 40 and avoid[1] - 40 < y < avoid[3] + 40:
            r *= 0.6
        aa = a * (0.4 + 0.6 * rng.random())
        if rng.random() < 0.22:
            A.line(c, [(x - r * 2.2, y), (x + r * 2.2, y)], r * 0.7, col, aa)
            A.line(c, [(x, y - r * 2.2), (x, y + r * 2.2)], r * 0.7, col, aa)
        else:
            A.circle(c, x, y, r, col, aa)


def deva_text(c, s, x, y, size, h='#ffffff', align='left', shadow=0.35):
    """Devanagari needs shaping: HarfBuzz -> glyph run. Returns width."""
    try:
        import uharfbuzz as hb
        data = open(DEVA_FONT, 'rb').read()
        face = hb.Face(data)
        f = hb.Font(face)
        buf = hb.Buffer()
        buf.add_str(s)
        buf.guess_segment_properties()
        hb.shape(f, buf, {})
        sc = size / face.upem
        gl, pos, xx = [], [], 0.0
        for inf, p in zip(buf.glyph_infos, buf.glyph_positions):
            gl.append(inf.codepoint)
            pos.append(skia.Point(xx + p.x_offset * sc, -p.y_offset * sc))
            xx += p.x_advance * sc
        font = skia.Font(skia.Typeface.MakeFromFile(DEVA_FONT), size)
        b = skia.TextBlobBuilder()
        b.allocRunPos(font, gl, pos)
        blob = b.make()
        w = xx
    except Exception:
        font = skia.Font(skia.Typeface.MakeFromFile(DEVA_FONT), size)
        blob = skia.TextBlob(s, font)
        w = font.measureText(s)
    x0 = x - w / 2 if align == 'center' else x
    if shadow:
        c.drawTextBlob(blob, x0, y + size * 0.05, A.P('#12062e', shadow))
    c.drawTextBlob(blob, x0, y, A.P(h))
    return w


def fit(s, max_w, size, weight=900, name='Montserrat'):
    w = A.measure(s, size, weight, name)
    return size if w <= max_w else size * max_w / w


def pill(c, s, x, y, size, fg, bg_, weight=700, name='Montserrat', align='left'):
    w = A.measure(s, size, weight, name) + size * 1.2
    hh = size * 1.65
    x0 = x if align == 'left' else x - w / 2
    A.rrect(c, x0, y - hh / 2, w, hh, hh / 2, bg_)
    A.text(c, s, x0 + w / 2, y + size * 0.36, size, fg, weight=weight, name=name, shadow=0)
    return w


def branch(c, x, y, ang, length, w, h, depth, rng, a=1.0):
    """Tapered, gently curving dendrite with forks."""
    pts = [(x, y)]
    bend = (rng.random() - 0.5) * 0.6
    steps = 10
    for i in range(1, steps + 1):
        k = i / steps
        an = ang + bend * k
        pts.append((pts[-1][0] + math.cos(an) * length / steps, pts[-1][1] + math.sin(an) * length / steps))
    for i in range(steps):
        ww = w * (1 - i / steps * 0.75)
        A.line(c, [pts[i], pts[i + 1]], ww, h, a)
    end = pts[-1]
    if depth > 0:
        for s_ in (-1, 1):
            branch(c, end[0], end[1], ang + bend + s_ * (0.45 + rng.random() * 0.25), length * 0.55, w * 0.3, h,
                   depth - 1, rng, a)
    else:
        A.circle(c, end[0], end[1], w * 0.32, A.shade(h, 0.3), a)


def star4(c, x, y, r, h, a=1.0):
    pts = []
    for i in range(8):
        an = i * math.pi / 4 - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.32
        pts.append((x + math.cos(an) * rr, y + math.sin(an) * rr))
    c.drawPath(A.smooth_path(pts, k=0.12), A.P(h, a))


def planet(c, x, y, r, h, ring=None, a=1.0):
    A.glow(c, x, y, r * 1.8, h, 0.35 * a)
    if ring:
        c.save()
        c.translate(x, y)
        c.rotate(-18)
        rect = skia.Rect(-r * 1.75, -r * 0.42, r * 1.75, r * 0.42)
        p = skia.Path()
        p.addArc(rect, 180, 180)
        c.drawPath(p, A.P(ring, a * 0.9, stroke=r * 0.09))
        c.restore()
    body = skia.Path()
    body.addCircle(x, y, r)
    A.shaded(c, body, h, a, dark=-0.3, off=(0.18, 0.18))
    rng = np.random.default_rng(int(r))
    c.save()
    c.clipPath(body, doAntiAlias=True)
    for i in range(4):
        A.ellipse(c, x + (rng.random() - 0.5) * r * 1.2, y + (rng.random() - 0.5) * r * 1.2, r * (0.12 + rng.random() * 0.12),
                  r * 0.08, A.shade(h, -0.15), a * 0.7)
    c.restore()
    if ring:
        c.save()
        c.translate(x, y)
        c.rotate(-18)
        p = skia.Path()
        p.addArc(skia.Rect(-r * 1.75, -r * 0.42, r * 1.75, r * 0.42), 0, 180)
        c.drawPath(p, A.P(ring, a, stroke=r * 0.09))
        c.restore()


def mini_neuron(c, x, y, s, h, rng):
    for k in range(5):
        an = k * 2 * math.pi / 5 + rng.random() * 0.5
        branch(c, x + math.cos(an) * 30 * s, y + math.sin(an) * 30 * s, an, 55 * s, 12 * s, h, 1, rng)
    A.shaded_circle(c, x, y, 42 * s, h)
    A.circle(c, x, y - 2 * s, 20 * s, '#ffffff')
    A.circle(c, x + 3 * s, y, 11 * s, '#2a0b3d')


def mini_brain(c, x, y, s, h=None):
    A.brain(c, x, y, s * 0.28, stem=False)
    for sx in (-1, 1):
        A.circle(c, x + sx * 18 * s, y - 14 * s, 11 * s, '#ffffff')
        A.circle(c, x + sx * 18 * s + 2 * s, y - 12 * s, 6 * s, '#2a0b3d')
    A.mouth(c, x, y + 4 * s, 40 * s, 'smile', h='#5a0a3a')


def qmark(c, x, y, s, h, rot=0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    A.glow(c, 0, -30 * s, 110 * s, h, 0.35)
    A.text(c, '?', 0, 0, 150 * s, h, weight=900, shadow=0.25)
    c.restore()


def edge_art(c, o):
    """Decor for the parts of the banner only TVs/desktops show; nothing inside the safe area."""
    n = o['n']
    rng = np.random.default_rng(n * 13)
    p1, p2 = o['planets']
    planet(c, 170, 230, 230, p1, ring=o['accent'])
    planet(c, BW - 140, BH - 170, 300, p2)
    A.glow(c, BW - 300, 160, 200, o['accent'], 0.35)
    spots = [(330, 1170), (120, 760), (430, 560), (2170, 300), (2440, 650), (2150, 980), (1050, 160), (1500, 1280),
             (760, 1300), (1900, 120), (650, 250), (2330, 900)]
    for i, (x, y) in enumerate(spots):
        s_ = 0.75 + rng.random() * 0.6
        col_ = o['bokeh'][i % len(o['bokeh'])]
        kind = o['icons'][i % len(o['icons'])]
        if kind == 'neuron':
            mini_neuron(c, x, y, s_, col_, rng)
        elif kind == 'brain':
            mini_brain(c, x, y, s_ * 1.4)
        elif kind == 'q':
            qmark(c, x, y + 50 * s_, s_, col_, rot=(rng.random() - 0.5) * 40)
        elif kind == 'star':
            A.glow(c, x, y, 70 * s_, col_, 0.5)
            star4(c, x, y, 38 * s_, '#ffffff')
        elif kind == 'bubble':
            A.glow(c, x, y, 90 * s_, col_, 0.45)
            A.circle(c, x, y, 46 * s_, col_, 0.85)
            A.circle(c, x - 15 * s_, y - 16 * s_, 12 * s_, '#ffffff', 0.8)
            c.drawCircle(x, y, 58 * s_, A.P('#ffffff', 0.5, stroke=4 * s_))
        elif kind == 'mol':
            A.molecule(c, x, y, 1.6 * s_, ['ana', 'nt', 'ohthc'][i % 3], t=rng.random() * 5, a=0.9)


# ------------------------------------------------------------------ mascots (x, y = centre, s = scale ~ 1 => ~400 px)
def m_neuron(c, x, y, s=1.0, t=0.6):
    pink, deep = '#ff4fa3', '#c2187a'
    A.glow(c, x, y, 420 * s, '#ff4fa3', 0.55)
    A.glow(c, x, y, 250 * s, '#ffd1ec', 0.35)
    rng = np.random.default_rng(4)
    # axon: long tail down-right with myelin beads
    ax = [(x + 60 * s, y + 70 * s), (x + 170 * s, y + 160 * s), (x + 260 * s, y + 190 * s), (x + 350 * s, y + 175 * s)]
    path = A.smooth_path(ax, closed=False)
    c.drawPath(path, A.P(deep, 1, stroke=26 * s))
    for i, (bx, by) in enumerate([(x + 150 * s, y + 140 * s), (x + 230 * s, y + 184 * s)]):
        c.save()
        c.translate(bx, by)
        c.rotate(30 - i * 18)
        A.rrect(c, -34 * s, -20 * s, 68 * s, 40 * s, 20 * s, '#5fe3ff')
        A.rrect(c, -26 * s, -14 * s, 30 * s, 10 * s, 5 * s, '#d8f8ff', 0.8)
        c.restore()
    for k in (-1, 0, 1):
        tx, ty = x + 350 * s + 40 * s, y + 175 * s + k * 34 * s
        A.line(c, [(x + 350 * s, y + 175 * s), (tx, ty)], 10 * s, deep)
        A.circle(c, tx, ty, 14 * s, '#ffd23f')
        A.glow(c, tx, ty, 40 * s, '#ffd23f', 0.6)
    # dendrites
    for ang in (-2.6, -1.95, -1.25, -0.55, 2.35, 3.05, 1.7):
        branch(c, x + math.cos(ang) * 110 * s, y + math.sin(ang) * 110 * s, ang, 140 * s, 30 * s, pink, 2, rng)
    body = A.smooth_path(A.blob_pts(x, y, 150 * s, n=8, wob=0.08, seed=5))
    A.shaded(c, body, pink, dark=-0.22, off=(0.1, 0.14))
    # one big eye
    A.circle(c, x, y - 12 * s, 84 * s, '#ffffff')
    A.circle(c, x + 10 * s, y - 6 * s, 50 * s, '#2a0b3d')
    A.circle(c, x + 12 * s, y - 4 * s, 30 * s, '#7a2bff')
    A.circle(c, x + 10 * s, y - 6 * s, 18 * s, '#12051f')
    A.circle(c, x - 8 * s, y - 28 * s, 16 * s, '#ffffff')
    A.circle(c, x + 26 * s, y + 12 * s, 7 * s, '#ffffff', 0.8)
    # lid arc + lashes for charm
    p = skia.Path()
    p.addArc(skia.Rect(x - 92 * s, y - 104 * s, x + 92 * s, y + 80 * s), 200, 140)
    c.drawPath(p, A.P('#7a0f4f', 1, stroke=10 * s))
    # smile + blush
    m = skia.Path()
    m.moveTo(x - 38 * s, y + 92 * s)
    m.quadTo(x, y + 128 * s, x + 38 * s, y + 92 * s)
    c.drawPath(m, A.P('#5a0a3a', 1, stroke=11 * s))
    for sx in (-1, 1):
        A.glow(c, x + sx * 98 * s, y + 70 * s, 34 * s, '#ff2f6e', 0.6)


def m_brain(c, x, y, s=1.0, t=0.3, wave=True):
    """Cheerful brain buddy with little arms."""
    A.glow(c, x, y, 430 * s, '#ffb02e', 0.45)
    # arms behind
    if wave:
        A.line(c, [(x - 190 * s, y + 60 * s), (x - 265 * s, y - 10 * s), (x - 290 * s, y - 110 * s)], 44 * s, '#e05a94')
        A.circle(c, x - 292 * s, y - 122 * s, 36 * s, '#ff8cc0')
        for k in (-1, 0, 1):
            A.circle(c, x - 292 * s + k * 22 * s, y - 158 * s + abs(k) * 8 * s, 13 * s, '#ff8cc0')
    A.line(c, [(x + 200 * s, y + 70 * s), (x + 270 * s, y + 130 * s)], 44 * s, '#e05a94')
    A.circle(c, x + 280 * s, y + 140 * s, 36 * s, '#ff8cc0')
    for sx in (-1, 1):
        A.line(c, [(x + sx * 70 * s, y + 140 * s), (x + sx * 80 * s, y + 215 * s)], 40 * s, '#e05a94')
        A.ellipse(c, x + sx * 92 * s, y + 225 * s, 46 * s, 22 * s, '#ffd23f')
    A.brain(c, x - 10 * s, y + 40 * s, s * 1.0, t=t, expr=None, stem=False)
    # custom friendly face (bigger eyes than default)
    fx, fy = x + 5 * s, y - 10 * s
    for sx in (-1, 1):
        A.ellipse(c, fx + sx * 62 * s, fy, 38 * s, 44 * s, '#ffffff')
        A.circle(c, fx + sx * 62 * s + 8 * s, fy + 6 * s, 24 * s, '#2a0b3d')
        A.circle(c, fx + sx * 62 * s - 2 * s, fy - 6 * s, 9 * s, '#ffffff')
        A.line(c, [(fx + sx * 62 * s - 24 * s, fy - 66 * s + (sx * -4) * s), (fx + sx * 62 * s + 22 * s, fy - 72 * s)],
               9 * s, '#7a1747')
        A.glow(c, fx + sx * 108 * s, fy + 56 * s, 30 * s, '#ff2f6e', 0.55)
    A.mouth(c, fx, fy + 62 * s, 130 * s, 'grin', h='#5a0a3a')


def m_bowl(c, x, y, s=1.0, t=0.4):
    """Brain Snacks: a bite-sized brain sitting in a bowl."""
    A.glow(c, x, y, 430 * s, '#2bd1ff', 0.4)
    A.glow(c, x, y - 60 * s, 260 * s, '#ff7eb6', 0.35)
    # steam / sparkle swirls
    for i, dx in enumerate((-90, 0, 90)):
        pts = [(x + dx * s, y - 210 * s), (x + (dx + 22) * s, y - 260 * s), (x + (dx - 14) * s, y - 305 * s),
               (x + (dx + 12) * s, y - 350 * s)]
        c.drawPath(A.smooth_path(pts, closed=False), A.P('#ffffff', 0.55, stroke=12 * s))
    # spoon behind
    c.save()
    c.translate(x + 175 * s, y - 40 * s)
    c.rotate(28)
    A.rrect(c, -12 * s, -170 * s, 24 * s, 200 * s, 12 * s, '#d8e6ff')
    A.ellipse(c, 0, -190 * s, 46 * s, 62 * s, '#eef4ff')
    A.ellipse(c, -10 * s, -200 * s, 18 * s, 30 * s, '#ffffff', 0.8)
    c.restore()
    # brain sitting in the bowl
    A.brain(c, x - 5 * s, y - 30 * s, s * 0.78, t=t, stem=False)
    fx, fy = x + 2 * s, y - 90 * s
    for sx in (-1, 1):
        A.ellipse(c, fx + sx * 48 * s, fy, 30 * s, 34 * s, '#ffffff')
        A.circle(c, fx + sx * 48 * s + 5 * s, fy + 6 * s, 19 * s, '#2a0b3d')
        A.circle(c, fx + sx * 48 * s - 3 * s, fy - 4 * s, 7 * s, '#ffffff')
        A.glow(c, fx + sx * 90 * s, fy + 42 * s, 24 * s, '#ff2f6e', 0.55)
    A.mouth(c, fx, fy + 46 * s, 100 * s, 'grin', h='#5a0a3a')
    # bowl
    bowl = skia.Path()
    bowl.moveTo(x - 270 * s, y + 10 * s)
    bowl.lineTo(x + 270 * s, y + 10 * s)
    bowl.cubicTo(x + 260 * s, y + 200 * s, x + 140 * s, y + 250 * s, x, y + 250 * s)
    bowl.cubicTo(x - 140 * s, y + 250 * s, x - 260 * s, y + 200 * s, x - 270 * s, y + 10 * s)
    bowl.close()
    A.shaded(c, bowl, '#18b4c9', dark=-0.25, off=(0.14, 0.0))
    A.rrect(c, x - 285 * s, y - 8 * s, 570 * s, 36 * s, 18 * s, '#5fe3ff')
    A.rrect(c, x - 90 * s, y + 245 * s, 180 * s, 30 * s, 14 * s, '#0f7f99')
    # bowl pattern: little dots
    for i in range(5):
        A.circle(c, x + (-160 + i * 80) * s, y + (95 + 18 * (i % 2)) * s, 13 * s, '#ffd23f')


def m_blob(c, x, y, s=1.0, t=0.2):
    """Tiny Big Questions: round curious blob with a question-mark antenna."""
    yel, teal = '#ffd23f', '#2bd1c4'
    A.glow(c, x, y, 430 * s, '#7b5cff', 0.5)
    # antenna: question mark
    qx, qy = x + 10 * s, y - 330 * s
    q = skia.Path()
    q.moveTo(qx - 55 * s, qy - 10 * s)
    q.cubicTo(qx - 55 * s, qy - 90 * s, qx + 75 * s, qy - 95 * s, qx + 65 * s, qy - 15 * s)
    q.cubicTo(qx + 60 * s, qy + 30 * s, qx, qy + 35 * s, qx, qy + 90 * s)
    q.lineTo(qx, qy + 165 * s)
    c.drawPath(q, A.P('#ffffff', 1, stroke=22 * s))
    A.glow(c, qx - 55 * s, qy - 10 * s, 60 * s, '#ffffff', 0.5)
    A.circle(c, qx - 55 * s, qy - 10 * s, 20 * s, '#ff4fa3')
    A.glow(c, qx - 55 * s, qy - 10 * s, 70 * s, '#ff4fa3', 0.6)
    # feet
    for sx in (-1, 1):
        A.ellipse(c, x + sx * 85 * s, y + 205 * s, 62 * s, 30 * s, A.shade(teal, -0.2))
    body = A.smooth_path(A.blob_pts(x, y, 215 * s, n=10, wob=0.03, seed=2, sy=0.96))
    A.shaded(c, body, yel, dark=-0.2, off=(0.12, 0.12))
    # little arms
    A.line(c, [(x - 200 * s, y + 40 * s), (x - 265 * s, y - 30 * s)], 34 * s, A.shade(yel, -0.12))
    A.line(c, [(x + 200 * s, y + 40 * s), (x + 258 * s, y + 95 * s)], 34 * s, A.shade(yel, -0.12))
    # eyes
    for sx in (-1, 1):
        ex, ey = x + sx * 72 * s, y - 30 * s
        A.ellipse(c, ex, ey, 54 * s, 62 * s, '#ffffff')
        A.circle(c, ex + 12 * s, ey - 10 * s, 34 * s, '#22113f')
        A.circle(c, ex + 12 * s, ey - 10 * s, 18 * s, teal)
        A.circle(c, ex + 12 * s, ey - 10 * s, 10 * s, '#22113f')
        A.circle(c, ex - 2 * s, ey - 26 * s, 12 * s, '#ffffff')
        A.line(c, [(ex - 32 * s, ey - 88 * s - sx * 6 * s), (ex + 30 * s, ey - 96 * s + sx * 6 * s)], 11 * s, '#7a4a00')
        A.glow(c, x + sx * 135 * s, y + 55 * s, 38 * s, '#ff5a8a', 0.6)
    A.mouth(c, x + 6 * s, y + 70 * s, 120 * s, 'o', h='#4a1a2a', open_=0.5)


# ------------------------------------------------------------------ options
OPTIONS = [
    dict(n=1, slug='neon_neuron', name='Neon Neuron', tag='Your brain, explained loudly.', mascot=m_neuron, ban_scale=0.62,
         bg=['#1a0b4a', '#4b1590', '#c21f7a'], bokeh=['#ff4fa3', '#7b5cff', '#2bd1ff'], name_col='#ffffff',
         accent='#ff4fa3', pill='NEW VIDEOS EVERY WEEK', pill_bg='#ff4fa3', pill_fg='#ffffff',
         planets=('#7b5cff', '#ff4fa3'), icons=('neuron', 'star', 'mol'),
         av_bg=['#2a0f6b', '#7a1a8c'], av_scale=1.18, av_off=(-40, -10)),
    dict(n=2, slug='andar_ki_baat', name='Andar Ki Baat', deva='अंदर की बात', tag="What's really happening inside you.",
         mascot=m_brain, ban_scale=0.66, bg=['#3b1070', '#d1366b', '#ffb02e'], bokeh=['#ffd23f', '#ff4fa3', '#7b5cff'],
         name_col='#ffffff', accent='#ffd23f', pill='SCIENCE • BODY • MIND', pill_bg='#ffd23f', pill_fg='#3b1070',
         planets=('#ff4fa3', '#ffd23f'), icons=('brain', 'star', 'mol'),
         av_bg=['#5a1a8c', '#ff6a4d'], av_scale=1.12, av_off=(10, 50)),
    dict(n=3, slug='brain_snacks', name='Brain Snacks', tag='Big science. Bite-sized.', mascot=m_bowl, ban_scale=0.68,
         bg=['#0d2a6b', '#1f6fd1', '#2bd1c4'], bokeh=['#ffd23f', '#ff7eb6', '#7cf2c4'], name_col='#ffffff',
         accent='#ffd23f', pill='FRESH EXPLAINERS SERVED WEEKLY', pill_bg='#ffd23f', pill_fg='#0d2a6b',
         planets=('#ffd23f', '#ff7eb6'), icons=('bubble', 'star', 'mol', 'bubble'),
         av_bg=['#123a8c', '#2bb5c4'], av_scale=0.98, av_off=(0, 10)),
    dict(n=4, slug='tiny_big_questions', name='Tiny Big Questions', tag='Curious about everything.', mascot=m_blob, ban_scale=0.6,
         bg=['#140a40', '#3a1d8f', '#2bd1c4'], bokeh=['#ffd23f', '#2bd1c4', '#ff4fa3'], name_col='#ffffff',
         accent='#ffd23f', pill='ASK WEIRD. LEARN WEIRDER.', pill_bg='#2bd1c4', pill_fg='#140a40',
         planets=('#2bd1c4', '#ff4fa3'), icons=('q', 'star', 'q', 'mol'),
         av_bg=['#2a1580', '#7b2bd1'], av_scale=0.92, av_off=(0, 95)),
]


def banner(o):
    surf = skia.Surface(BW, BH)
    c = surf.getCanvas()
    bg(c, BW, BH, o['bg'], (0.0, 0.0, 1.0, 1.0))
    bokeh(c, BW, BH, o['n'] * 7, o['bokeh'], n=22, a=0.25)
    edge_art(c, o)
    sparkles(c, BW, BH, o['n'] * 3, n=110, avoid=SAFE)
    # soft band behind safe area for legibility
    x0, y0, x1, y1 = SAFE
    A.glow(c, (x0 + x1) / 2, (y0 + y1) / 2, 1100, '#0c0428', 0.35)
    # mascot on the left of safe area
    mx, my = x0 + 250, (y0 + y1) / 2 + 10
    o['mascot'](c, mx, my, o.get('ban_scale', 0.6))
    # text block
    tx = x0 + 540
    max_w = x1 - tx - 20
    if o.get('deva'):
        deva_text(c, o['deva'], tx, y0 + 175, 150, '#ffffff')
        ns = fit(o['name'].upper(), max_w, 72, 900)
        A.text(c, o['name'].upper(), tx, y0 + 262, ns, o['accent'], weight=900, align='left', track=0.06)
        A.text(c, o['tag'], tx, y0 + 330, fit(o['tag'], max_w, 46, 700), '#ffffff', weight=700, align='left',
               name='Nunito')
        pill(c, o['pill'], tx, y0 + 392, 28, o['pill_fg'], o['pill_bg'])
    else:
        ns = fit(o['name'], max_w, 150, 900)
        A.text(c, o['name'], tx, y0 + 190, ns, o['name_col'], weight=900, align='left', name='Montserrat')
        # accent underline
        A.rrect(c, tx + 4, y0 + 222, 160, 14, 7, o['accent'])
        A.text(c, o['tag'], tx, y0 + 305, fit(o['tag'], max_w, 58, 800), '#ffffff', weight=800, align='left',
               name='Nunito')
        pill(c, o['pill'], tx, y0 + 378, 30, o['pill_fg'], o['pill_bg'])
    return surf.makeImageSnapshot()


def avatar(o):
    S = 800
    surf = skia.Surface(S, S)
    c = surf.getCanvas()
    p = skia.Paint()
    p.setShader(A.rad((S * 0.5, S * 0.42), S * 0.75, o['av_bg']))
    c.drawRect(skia.Rect(0, 0, S, S), p)
    bokeh(c, S, S, o['n'] * 11, o['bokeh'], n=7, a=0.22, rmin=40, rmax=140)
    sparkles(c, S, S, o['n'] * 5, n=26, a=0.55)
    ox, oy = o['av_off']
    o['mascot'](c, S / 2 + ox, S / 2 + oy, o['av_scale'])
    return surf.makeImageSnapshot()


def sheet(items):
    BWs, BHs = 1280, 720
    AV = 330
    pad = 50
    W_ = pad * 3 + BWs + AV + 40
    rowh = BHs + 120
    H_ = pad + rowh * len(items) + 20
    surf = skia.Surface(W_, H_)
    c = surf.getCanvas()
    c.clear(A.col('#120a2e'))
    for i, (o, b, a) in enumerate(items):
        y = pad + i * rowh
        A.text(c, f"OPTION {o['n']}:  {o['name']}" + f"  -  {o['tag']}",
               pad, y + 40, 36, '#ffffff', weight=800, align='left', shadow=0)
        y += 70
        c.drawImageRect(b, skia.Rect(pad, y, pad + BWs, y + BHs), skia.SamplingOptions(skia.FilterMode.kLinear))
        sx, sy = BWs / BW, BHs / BH
        r = skia.Rect(pad + SAFE[0] * sx, y + SAFE[1] * sy, pad + SAFE[2] * sx, y + SAFE[3] * sy)
        dash = A.P('#ffffff', 0.55, stroke=2)
        dash.setPathEffect(skia.DashPathEffect.Make([10, 8], 0))
        c.drawRect(r, dash)
        A.text(c, 'mobile-safe area', r.left() + 8, r.bottom() + 24, 18, '#ffffff', 0.7, weight=600, align='left', shadow=0)
        ax, ay = pad * 2 + BWs + 20, y + (BHs - AV) / 2
        c.save()
        path = skia.Path()
        path.addCircle(ax + AV / 2, ay + AV / 2, AV / 2)
        c.clipPath(path, doAntiAlias=True)
        c.drawImageRect(a, skia.Rect(ax, ay, ax + AV, ay + AV), skia.SamplingOptions(skia.FilterMode.kLinear))
        c.restore()
        # tiny version, as seen next to a comment
        c.save()
        sm = 64
        path = skia.Path()
        path.addCircle(ax + AV / 2, ay + AV + 70 + sm / 2, sm / 2)
        c.clipPath(path, doAntiAlias=True)
        c.drawImageRect(a, skia.Rect(ax + AV / 2 - sm / 2, ay + AV + 70, ax + AV / 2 + sm / 2, ay + AV + 70 + sm),
                        skia.SamplingOptions(skia.FilterMode.kLinear))
        c.restore()
        A.text(c, 'avatar', ax + AV / 2, ay - 18, 22, '#ffffff', 0.8, weight=600, shadow=0)
        A.text(c, 'at comment size', ax + AV / 2, ay + AV + 160, 18, '#ffffff', 0.7, weight=600, shadow=0)
    return surf.makeImageSnapshot()


def main():
    os.makedirs(OUT, exist_ok=True)
    items = []
    for o in OPTIONS:
        b, a = banner(o), avatar(o)
        b.save(os.path.join(OUT, f"option{o['n']}_{o['slug']}_banner.png"))
        a.save(os.path.join(OUT, f"option{o['n']}_{o['slug']}_avatar.png"))
        items.append((o, b, a))
        print('wrote option', o['n'], o['name'])
    sh = sheet(items)
    sh.save(os.path.join(OUT, 'branding_sheet.jpg'), skia.kJPEG, 90)
    print('sheet', os.path.join(OUT, 'branding_sheet.jpg'))


if __name__ == '__main__':
    main()
