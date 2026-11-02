"""Flat-vector drawing kit for the explainer channel: vivid gradients, soft glows, two-tone shading,
no outlines, round friendly characters. Everything draws into a 1920x1080 skia canvas."""
import math
import os

import numpy as np
import skia

W, H, FPS = 1920, 1080, 30
HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, 'fonts')

# ------------------------------------------------------------------ fonts
_tf_cache = {}


def typeface(name='Montserrat', weight=800):
    """Static instances live in fonts/<Name>-<weight>.ttf; nearest available weight is used."""
    k = (name, weight)
    if k not in _tf_cache:
        if name == 'Baloo2':
            path = os.path.join(FD, 'Baloo2.ttf')
        else:
            ws = sorted(int(f.split('-')[1][:-4]) for f in os.listdir(FD) if f.startswith(name + '-'))
            w = min(ws, key=lambda x: abs(x - weight))
            path = os.path.join(FD, f'{name}-{w}.ttf')
        _tf_cache[k] = skia.Typeface.MakeFromFile(path)
    return _tf_cache[k]


def font(size, name='Montserrat', weight=800):
    f = skia.Font(typeface(name, weight), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    f.setSubpixel(True)
    return f


# ------------------------------------------------------------------ colour + math
def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def col(h, a=1.0):
    if isinstance(h, int):
        return h
    r, g, b = rgb(h)
    return skia.Color(r, g, b, int(255 * max(0, min(1, a))))


def mix(h1, h2, t):
    a, b = rgb(h1), rgb(h2)
    t = max(0.0, min(1.0, t))
    return '#%02x%02x%02x' % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def shade(h, k):
    """k<0 darker (towards deep purple, not grey), k>0 lighter."""
    return mix(h, '#1a0b3d', -k) if k < 0 else mix(h, '#ffffff', k)


def clamp01(x):
    return max(0.0, min(1.0, x))


def lerp(a, b, t):
    return a + (b - a) * t


def ease(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def eio(x):
    x = clamp01(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def eout(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def back(x, s=1.9):
    """ease-out with overshoot: pops in."""
    x = clamp01(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def ramp(t, a, b):
    return clamp01((t - a) / (b - a)) if b > a else float(t >= a)


def pop(t, a, dur=0.45):
    return back(ramp(t, a, a + dur))


def win(t, a, b, f=0.35):
    return clamp01(min((t - a) / f, (b - t) / f)) if b > a else 0.0


def osc(t, f=1.0, ph=0.0):
    return math.sin(2 * math.pi * f * t + ph)


# ------------------------------------------------------------------ paints
def P(h='#ffffff', a=1.0, stroke=None, cap='round', shader=None, blur=None):
    p = skia.Paint(AntiAlias=True)
    p.setColor(col(h, a))
    if shader is not None:
        p.setShader(shader)
        p.setAlphaf(a)
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(dict(round=skia.Paint.kRound_Cap, butt=skia.Paint.kButt_Cap, square=skia.Paint.kSquare_Cap)[cap])
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def lin(p0, p1, colors, pos=None):
    return skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)], [col(c) for c in colors], pos)


def rad(center, r, colors, pos=None, alphas=None):
    cs = [col(c, alphas[i] if alphas else 1.0) for i, c in enumerate(colors)]
    return skia.GradientShader.MakeRadial(skia.Point(*center), max(r, 0.1), cs, pos)


# ------------------------------------------------------------------ primitives
def circle(c, x, y, r, h, a=1.0):
    if r > 0 and a > 0:
        c.drawCircle(x, y, r, P(h, a))


def ellipse(c, x, y, rx, ry, h, a=1.0):
    if a > 0:
        c.drawOval(skia.Rect(x - rx, y - ry, x + rx, y + ry), P(h, a))


def rrect(c, x, y, w, h, r, fill, a=1.0, paint=None):
    c.drawRoundRect(skia.Rect(x, y, x + w, y + h), r, r, paint or P(fill, a))


def line(c, pts, w, h, a=1.0, cap='round'):
    path = skia.Path()
    path.moveTo(*pts[0])
    for p in pts[1:]:
        path.lineTo(*p)
    c.drawPath(path, P(h, a, stroke=w, cap=cap))


def glow(c, x, y, r, h, a=0.5):
    if a <= 0 or r <= 0:
        return
    p = skia.Paint(AntiAlias=True)
    p.setShader(rad((x, y), r, [h, h, h], [0, 0.35, 1], alphas=[a, a * 0.45, 0]))
    c.drawCircle(x, y, r, p)


def smooth_path(pts, closed=True, k=0.5):
    """Catmull-Rom spline through points -> skia path."""
    n = len(pts)
    path = skia.Path()
    path.moveTo(*pts[0])
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 3, p1[1] + (p2[1] - p0[1]) * k / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 3, p2[1] - (p3[1] - p1[1]) * k / 3)
        path.cubicTo(*c1, *c2, *p2)
    if closed:
        path.close()
    return path


def blob_pts(x, y, r, n=9, wob=0.12, seed=0, t=0.0, sx=1.0, sy=1.0):
    rng = np.random.default_rng(seed)
    ph = rng.random(n) * 6.28
    amp = rng.random(n)
    pts = []
    for i in range(n):
        a = i / n * 2 * math.pi
        rr = r * (1 + wob * (amp[i] - 0.5) * 2 + 0.04 * math.sin(t * 1.3 + ph[i]))
        pts.append((x + math.cos(a) * rr * sx, y + math.sin(a) * rr * sy))
    return pts


def blob(c, x, y, r, h, a=1.0, n=9, wob=0.12, seed=0, t=0.0, sx=1.0, sy=1.0):
    path = smooth_path(blob_pts(x, y, r, n, wob, seed, t, sx, sy))
    c.drawPath(path, P(h, a))
    return path


def shaded(c, path, h, a=1.0, dark=-0.28, light=0.22, off=(0.16, 0.2), size=None, hl=True):
    """Fill a path with two-tone shading: dark crescent bottom-right, soft highlight top-left."""
    b = path.computeTightBounds()
    sz = size or max(b.width(), b.height())
    c.drawPath(path, P(h, a))
    c.save()
    c.clipPath(path, doAntiAlias=True)
    sh = skia.Path(path)
    sh.offset(-off[0] * sz, -off[1] * sz)
    d = skia.Op(path, sh, skia.PathOp.kDifference_PathOp)
    if d is not None:
        c.drawPath(d, P(shade(h, dark), a))
    if hl:
        cx, cy = b.left() + b.width() * 0.3, b.top() + b.height() * 0.28
        glow(c, cx, cy, sz * 0.35, shade(h, light + 0.35), 0.35 * a)
    c.restore()


def shaded_circle(c, x, y, r, h, a=1.0, dark=-0.28):
    path = skia.Path()
    path.addCircle(x, y, r)
    shaded(c, path, h, a, dark=dark)


# ------------------------------------------------------------------ text
def text(c, s, x, y, size=60, h='#ffffff', a=1.0, weight=800, name='Montserrat', align='center', shadow=0.35,
         track=0.0, outline=None):
    if a <= 0 or not s:
        return 0
    if any('\u0900' <= ch <= '\u097f' for ch in s):
        return deva(c, s, x, y, size, h, a, align, shadow)
    f = font(size, name, weight)
    w = f.measureText(s) + track * size * (len(s) - 1)
    x0 = x - w / 2 if align == 'center' else (x - w if align == 'right' else x)

    def draw(paint, dx=0, dy=0):
        if track:
            xx = x0
            for ch in s:
                c.drawString(ch, xx + dx, y + dy, f, paint)
                xx += f.measureText(ch) + track * size
        else:
            c.drawString(s, x0 + dx, y + dy, f, paint)
    if shadow:
        draw(P('#12062e', a * shadow), 0, size * 0.06)
    if outline:
        draw(P(outline[0], a, stroke=outline[1]))
    draw(P(h, a))
    return w


DEVA_FONT = os.path.join(HERE, 'branding', 'Baloo2-800.ttf')
_deva = {}


def deva(c, s, x, y, size, h='#ffffff', a=1.0, align='center', shadow=0.35):
    """Devanagari needs shaping (HarfBuzz) to place matras correctly. Returns width."""
    key = (s, size)
    if key not in _deva:
        tf = skia.Typeface.MakeFromFile(DEVA_FONT)
        fnt = skia.Font(tf, size)
        try:
            import uharfbuzz as hb
            face = hb.Face(open(DEVA_FONT, 'rb').read())
            buf = hb.Buffer()
            buf.add_str(s)
            buf.guess_segment_properties()
            hb.shape(hb.Font(face), buf, {})
            sc = size / face.upem
            gl, pos, xx = [], [], 0.0
            for inf, p in zip(buf.glyph_infos, buf.glyph_positions):
                gl.append(inf.codepoint)
                pos.append(skia.Point(xx + p.x_offset * sc, -p.y_offset * sc))
                xx += p.x_advance * sc
            bb = skia.TextBlobBuilder()
            bb.allocRunPos(fnt, gl, pos)
            _deva[key] = (bb.make(), xx)
        except Exception:
            _deva[key] = (skia.TextBlob(s, fnt), fnt.measureText(s))
    blob_, w = _deva[key]
    x0 = x - w / 2 if align == 'center' else (x - w if align == 'right' else x)
    if shadow:
        c.drawTextBlob(blob_, x0, y + size * 0.05, P('#12062e', a * shadow))
    c.drawTextBlob(blob_, x0, y, P(h, a))
    return w


def measure(s, size, weight=800, name='Montserrat'):
    return font(size, name, weight).measureText(s)


def label(c, s, x, y, tx, ty, a=1.0, size=34, h='#ffffff', bg='#1b0f45'):
    """Kurzgesagt-ish pointer label: small dot on target, line, pill with text."""
    if a <= 0:
        return
    k = ease(a)
    ex, ey = lerp(tx, x, k), lerp(ty, y, k)
    circle(c, tx, ty, 7, h, a)
    line(c, [(tx, ty), (ex, ey)], 3.5, h, a)
    w = measure(s, size, 700) + size * 1.1
    hh = size * 1.55
    rrect(c, ex - w / 2, ey - hh / 2, w, hh, hh / 2, bg, a * 0.88)
    text(c, s, ex, ey + size * 0.36, size, h, a, weight=700, shadow=0)


def cite(c, s, a=1.0):
    """Small source tag, bottom-right, like a citation sticker."""
    if a <= 0 or not s:
        return
    size = 21
    s = 'SOURCE: ' + s
    w = measure(s, size, 600) + 34
    x, y = W - w - 36, H - 70
    rrect(c, x, y, w, 38, 10, '#0e0828', a * 0.72)
    circle(c, x + 15, y + 19, 4.5, '#7cf2c4', a)
    text(c, s, x + 27, y + 26, size, '#e9e3ff', a * 0.95, weight=600, align='left', shadow=0)


# ------------------------------------------------------------------ backgrounds
def bg_grad(c, top, bottom, mid=None):
    p = skia.Paint()
    cols = [top, mid, bottom] if mid else [top, bottom]
    p.setShader(lin((0, 0), (0, H), cols))
    c.drawRect(skia.Rect(0, 0, W, H), p)


def bg_radial(c, center, inner, outer, r=1300):
    p = skia.Paint()
    p.setShader(rad(center, r, [inner, outer]))
    c.drawRect(skia.Rect(0, 0, W, H), p)


def particles(c, t, seed=1, n=40, h='#ffffff', a=0.35, size=(2, 6), speed=12, plus=0.25, area=(0, 0, W, H)):
    rng = np.random.default_rng(seed)
    x0, y0, x1, y1 = area
    for i in range(n):
        x = x0 + rng.random() * (x1 - x0)
        y = y0 + rng.random() * (y1 - y0)
        r = size[0] + rng.random() * (size[1] - size[0])
        sp = speed * (0.4 + rng.random())
        ph = rng.random() * 6.28
        yy = y0 + ((y - t * sp - y0) % (y1 - y0))
        xx = x + 8 * math.sin(t * 0.5 + ph)
        tw = 0.55 + 0.45 * math.sin(t * 1.7 + ph * 3)
        if rng.random() < plus:
            line(c, [(xx - r * 1.6, yy), (xx + r * 1.6, yy)], r * 0.6, h, a * tw)
            line(c, [(xx, yy - r * 1.6), (xx, yy + r * 1.6)], r * 0.6, h, a * tw)
        else:
            circle(c, xx, yy, r, h, a * tw)


def bokeh(c, t, seed=3, n=14, colors=('#ff4fa3', '#7b5cff', '#2bd1ff'), a=0.18, rmin=30, rmax=120):
    rng = np.random.default_rng(seed)
    for i in range(n):
        x, y = rng.random() * W, rng.random() * H
        r = rmin + rng.random() * (rmax - rmin)
        ph = rng.random() * 6.28
        h = colors[i % len(colors)]
        glow(c, x + 30 * math.sin(t * 0.21 + ph), y + 20 * math.cos(t * 0.17 + ph), r, h, a)


# ------------------------------------------------------------------ faces + people
SKINS = ['#f2c29b', '#d99a6c', '#b77a50', '#8a5636', '#ffd7b8', '#c98b62']


def eye(c, x, y, r, look=(0, 0), lid=0.0, blink=0.0, white='#ffffff', pupil='#1d1238', pr=0.48, lid_col='#e8b48f',
        red=0.0, lower_lid=0.0, sparkle=True):
    ry = r * (1 - blink * 0.92)
    wcol = mix(white, '#ff9cb0', red * 0.6)
    ellipse(c, x, y, r * 0.86, ry, wcol)
    c.save()
    pth = skia.Path()
    pth.addOval(skia.Rect(x - r * 0.86, y - ry, x + r * 0.86, y + ry))
    c.clipPath(pth, doAntiAlias=True)
    px, py = x + look[0] * r * 0.38, y + look[1] * r * 0.38
    circle(c, px, py, r * pr, pupil)
    if sparkle:
        circle(c, px - r * pr * 0.35, py - r * pr * 0.4, r * pr * 0.32, '#ffffff', 0.95)
    lidk = max(lid, blink)
    if lidk > 0:
        c.drawRect(skia.Rect(x - r, y - r - 2, x + r, y - r + 2 * r * lidk), P(lid_col))
    if lower_lid > 0:
        c.drawRect(skia.Rect(x - r, y + r - 2 * r * lower_lid, x + r, y + r + 2), P(lid_col))
    c.restore()


def blink_k(t, period=3.9, off=0.0):
    ph = (t + off) % period
    return clamp01(1 - abs(ph - 0.08) / 0.08) if ph < 0.16 else 0.0


def mouth(c, x, y, r, kind='smile', h='#3a1230', tongue='#ff6b8a', a=1.0, open_=0.0):
    w = r * 0.42
    if kind == 'smile':
        path = skia.Path()
        path.moveTo(x - w, y)
        path.quadTo(x, y + w * 0.9, x + w, y)
        c.drawPath(path, P(h, a, stroke=r * 0.075))
    elif kind in ('grin', 'laugh'):
        k = 0.9 if kind == 'grin' else 1.25
        path = skia.Path()
        path.moveTo(x - w, y - w * 0.1)
        path.quadTo(x, y - w * 0.05, x + w, y - w * 0.1)
        path.quadTo(x + w * 0.9, y + w * k, x, y + w * k)
        path.quadTo(x - w * 0.9, y + w * k, x - w, y - w * 0.1)
        path.close()
        c.drawPath(path, P(h, a))
        c.save()
        c.clipPath(path, doAntiAlias=True)
        ellipse(c, x, y + w * k, w * 0.6, w * 0.45, tongue, a)
        c.drawRect(skia.Rect(x - w, y - w * 0.3, x + w, y + w * 0.12), P('#ffffff', a))
        c.restore()
    elif kind == 'o':
        ellipse(c, x, y + w * 0.25, w * 0.32 * (1 + open_), w * 0.42 * (1 + open_), h, a)
    elif kind == 'flat':
        line(c, [(x - w * 0.6, y + w * 0.2), (x + w * 0.6, y + w * 0.2)], r * 0.07, h, a)
    elif kind == 'frown':
        path = skia.Path()
        path.moveTo(x - w * 0.7, y + w * 0.45)
        path.quadTo(x, y - w * 0.15, x + w * 0.7, y + w * 0.45)
        c.drawPath(path, P(h, a, stroke=r * 0.075))
    elif kind == 'wavy':
        pts = [(x - w * 0.8 + i * w * 0.2, y + w * 0.25 + (w * 0.12 if i % 2 else -w * 0.12)) for i in range(9)]
        line(c, pts, r * 0.065, h, a)
    elif kind == 'scream':
        ellipse(c, x, y + w * 0.4, w * 0.5, w * 0.7, h, a)
        ellipse(c, x, y + w * 0.75, w * 0.32, w * 0.25, tongue, a)


EXPR = {
    # brow (angle, raise), lid, mouth, look default, extras
    'neutral': dict(brow=(0, 0), lid=0.12, mouth='smile'),
    'happy': dict(brow=(0, 0.15), lid=0.0, mouth='grin'),
    'laugh': dict(brow=(0, 0.25), lid=0.35, mouth='laugh', blush=1),
    'high': dict(brow=(-0.1, 0.05), lid=0.5, mouth='grin', red=1, blush=1),
    'bored': dict(brow=(0, -0.05), lid=0.45, mouth='flat'),
    'curious': dict(brow=(0.15, 0.2), lid=0.0, mouth='o'),
    'shock': dict(brow=(0, 0.45), lid=0.0, mouth='scream', small_pupil=True),
    'scared': dict(brow=(-0.3, 0.3), lid=0.0, mouth='wavy', small_pupil=True, sweat=1),
    'sick': dict(brow=(-0.25, 0.1), lid=0.35, mouth='wavy', red=0.6, green=1),
    'sad': dict(brow=(-0.35, 0.1), lid=0.3, mouth='frown'),
    'think': dict(brow=(0.25, 0.1), lid=0.15, mouth='flat'),
    'dazed': dict(brow=(-0.15, 0.1), lid=0.55, mouth='o', red=1),
    'calm': dict(brow=(0, 0.05), lid=0.4, mouth='smile'),
    'talk': dict(brow=(0, 0.12), lid=0.05, mouth='grin'),
}


def face(c, x, y, r, expr='neutral', look=(0, 0), t=0.0, skin='#f2c29b', blink_off=0.0, eye_gap=0.36, eye_r=0.27,
         ink='#2a1640'):
    e = EXPR.get(expr, EXPR['neutral'])
    bl = blink_k(t, 3.7, blink_off)
    lid_col = shade(skin, -0.08)
    ex = r * eye_gap
    ey = y - r * 0.05
    er = r * eye_r
    pr = 0.34 if e.get('small_pupil') else 0.48
    for s in (-1, 1):
        eye(c, x + s * ex, ey, er, look, lid=e['lid'], blink=bl, pr=pr, lid_col=lid_col, red=e.get('red', 0))
        ang, rise = e['brow']
        bx, by = x + s * ex, ey - er * (1.25 + rise * 1.5)
        dy = s * ang * er * 0.5
        line(c, [(bx - er * 0.75, by + dy), (bx + er * 0.75, by - dy)], r * 0.085, ink)
    if e.get('blush'):
        for s in (-1, 1):
            glow(c, x + s * r * 0.55, y + r * 0.28, r * 0.25, '#ff5a8a', 0.55)
    if e.get('green'):
        glow(c, x, y + r * 0.2, r * 0.9, '#7dff6a', 0.22)
    mouth(c, x + look[0] * r * 0.08, y + r * 0.38, r, e['mouth'])
    if e.get('sweat'):
        dy = (t * 40) % 30
        sw = smooth_path([(x + r * 0.85, y - r * 0.55 + dy), (x + r * 0.95, y - r * 0.3 + dy),
                          (x + r * 0.85, y - r * 0.22 + dy), (x + r * 0.76, y - r * 0.3 + dy)])
        c.drawPath(sw, P('#9fe6ff', 0.9))


def hair(c, x, y, r, style, h, back=False):
    if style == 'long' and back:
        path = smooth_path([(x - r * 1.05, y - r * 0.1), (x - r * 1.0, y - r * 0.9), (x, y - r * 1.15),
                            (x + r * 1.0, y - r * 0.9), (x + r * 1.05, y - r * 0.1), (x + r * 1.1, y + r * 1.3),
                            (x, y + r * 1.25), (x - r * 1.1, y + r * 1.3)])
        c.drawPath(path, P(shade(h, -0.15)))
        return
    if style == 'bun' and back:
        circle(c, x + r * 0.15, y - r * 1.12, r * 0.42, h)
        return
    if back:
        return
    if style in ('short', 'long', 'bun'):
        path = skia.Path()
        path.moveTo(x - r * 1.02, y - r * 0.05)
        path.cubicTo(x - r * 1.1, y - r * 1.25, x + r * 1.1, y - r * 1.3, x + r * 1.03, y - r * 0.1)
        path.cubicTo(x + r * 0.8, y - r * 0.55, x + r * 0.2, y - r * 0.45, x - r * 0.15, y - r * 0.75)
        path.cubicTo(x - r * 0.4, y - r * 0.45, x - r * 0.8, y - r * 0.5, x - r * 1.02, y - r * 0.05)
        path.close()
        c.drawPath(path, P(h))
        glow(c, x - r * 0.35, y - r * 0.85, r * 0.35, shade(h, 0.4), 0.35)
    elif style == 'curly':
        for i in range(9):
            a = math.pi * (1.05 + i / 8 * 0.9)
            circle(c, x + math.cos(a) * r * 0.95, y - r * 0.15 + math.sin(a) * r * 0.95, r * 0.36, h)
        circle(c, x, y - r * 0.8, r * 0.45, h)
    elif style == 'spiky':
        pts = []
        for i in range(11):
            a = math.pi * (1.0 + i / 10)
            rr = r * (1.25 if i % 2 else 0.98)
            pts.append((x + math.cos(a) * rr, y - r * 0.1 + math.sin(a) * rr))
        pts += [(x + r * 0.9, y - r * 0.2), (x - r * 0.9, y - r * 0.2)]
        c.drawPath(smooth_path(pts, k=0.15), P(h))
    elif style == 'cap':
        path = skia.Path()
        path.addArc(skia.Rect(x - r * 1.02, y - r * 1.05, x + r * 1.02, y + r * 0.95), 180, 180)
        path.close()
        c.drawPath(path, P(h))
        rrect(c, x - r * 0.1, y - r * 0.2, r * 1.5, r * 0.22, r * 0.11, shade(h, -0.2))


def person(c, x, y, s=1.0, look_as=None, expr='neutral', look=(0, 0), t=0.0, arms=('down', 'down'), hold=None,
           bob=1.0, sit=False, blink_off=0.0, lean=0.0, body_h=None):
    """x,y = feet centre. Returns dict with hand positions + head pos."""
    L = dict(skin='#f2c29b', hair='#2b1a3a', style='short', shirt='#ff6f59', pants='#3a2f7a', shoe='#ffffff')
    if look_as:
        L.update(look_as)
    r = 62 * s
    by = y - (16 * s) * max(0, osc(t, 0.6)) * bob * 0.3
    leg = 0 if sit else 95 * s
    torso_h = body_h or 150 * s
    hip_y = by - leg
    sh_y = hip_y - torso_h
    hx = x + lean * 40 * s
    hy = sh_y - r * 0.9
    # legs
    if not sit:
        for sx in (-1, 1):
            line(c, [(x + sx * 22 * s, hip_y), (x + sx * 26 * s, by - 10 * s)], 34 * s, L['pants'])
            ellipse(c, x + sx * 32 * s, by - 6 * s, 26 * s, 13 * s, L['shoe'])
    else:
        for sx in (-1, 1):
            line(c, [(x + sx * 22 * s, hip_y), (x + sx * 22 * s + 60 * s, hip_y + 4 * s),
                     (x + sx * 22 * s + 62 * s, hip_y + 70 * s)], 34 * s, L['pants'])
    hair(c, hx, hy, r, L['style'], L['hair'], back=True)
    # torso
    tor = skia.Path()
    tor.moveTo(x - 56 * s, hip_y + 4 * s)
    tor.cubicTo(x - 60 * s, sh_y + 40 * s, x - 52 * s, sh_y, x - 30 * s + lean * 30 * s, sh_y)
    tor.lineTo(x + 30 * s + lean * 30 * s, sh_y)
    tor.cubicTo(x + 52 * s, sh_y, x + 60 * s, sh_y + 40 * s, x + 56 * s, hip_y + 4 * s)
    tor.close()
    shaded(c, tor, L['shirt'], dark=-0.22, off=(0.25, 0.0))
    # arms
    hands = {}
    poses = {
        'down': [(0.2, 0.45), (0.25, 1.0)], 'wave': [(0.55, -0.35), (0.6, -1.0)], 'up': [(0.3, -0.6), (0.35, -1.25)],
        'hold': [(0.35, 0.35), (0.05, 0.25)], 'drink': [(0.3, 0.3), (0.0, -0.45)], 'hip': [(0.55, 0.35), (0.3, 0.65)],
        'point': [(0.6, 0.0), (1.25, -0.15)], 'face': [(0.3, 0.25), (0.05, -0.55)], 'shrug': [(0.6, 0.15), (0.9, -0.2)],
        'dance': [(0.55, -0.2 + 0.25 * osc(t, 1.6)), (0.75, -0.75 + 0.3 * osc(t, 1.6))],
        'stomach': [(0.35, 0.4), (0.05, 0.55)],
    }
    for side, pose in zip((-1, 1), arms):
        sx0, sy0 = hx - lean * 40 * s + side * 46 * s + lean * 30 * s, sh_y + 22 * s
        pts = poses.get(pose, poses['down'])
        e = (sx0 + side * pts[0][0] * 100 * s, sy0 + pts[0][1] * 100 * s)
        hnd = (sx0 + side * pts[1][0] * 100 * s, sy0 + pts[1][1] * 100 * s)
        line(c, [(sx0, sy0), e, hnd], 30 * s, shade(L['shirt'], -0.1))
        circle(c, hnd[0], hnd[1], 19 * s, L['skin'])
        hands[side] = hnd
    # neck + head
    rrect(c, hx - 16 * s, hy + r * 0.6, 32 * s, 40 * s, 10 * s, shade(L['skin'], -0.12))
    head = skia.Path()
    head.addOval(skia.Rect(hx - r, hy - r * 1.02, hx + r, hy + r * 0.98))
    shaded(c, head, L['skin'], dark=-0.16, off=(0.18, 0.12))
    for sx in (-1, 1):
        ellipse(c, hx + sx * r * 0.98, hy + r * 0.05, r * 0.16, r * 0.22, shade(L['skin'], -0.08))
    face(c, hx + look[0] * r * 0.12, hy + look[1] * r * 0.08, r, expr, look, t, L['skin'], blink_off)
    hair(c, hx, hy, r, L['style'], L['hair'])
    return dict(hands=hands, head=(hx, hy), r=r)


# ------------------------------------------------------------------ objects
def glass(c, x, y, s=1.0, fill=0.8, liquid='#cfe8b0', t=0.0, garnish=True, a=1.0, glowc=None):
    """Tall tumbler of thandai/bhang. x,y = bottom centre."""
    if glowc:
        glow(c, x, y - 130 * s, 260 * s, glowc, 0.35 * a)
    top_w, bot_w, h = 92 * s, 70 * s, 250 * s
    body = skia.Path()
    body.moveTo(x - top_w, y - h)
    body.lineTo(x + top_w, y - h)
    body.lineTo(x + bot_w, y - 10 * s)
    body.quadTo(x + bot_w, y, x + bot_w - 12 * s, y)
    body.lineTo(x - bot_w + 12 * s, y)
    body.quadTo(x - bot_w, y, x - bot_w, y - 10 * s)
    body.close()
    c.drawPath(body, P('#d9f3ff', 0.28 * a))
    if fill > 0:
        ly = y - h * fill * 0.92 - 6 * s + 3 * s * osc(t, 0.8)
        c.save()
        c.clipPath(body, doAntiAlias=True)
        liq = skia.Paint(AntiAlias=True)
        liq.setShader(lin((0, ly), (0, y), [shade(liquid, 0.15), liquid, shade(liquid, -0.12)]))
        liq.setAlphaf(a)
        wave = skia.Path()
        wave.moveTo(x - top_w - 5, ly)
        for i in range(13):
            xx = x - top_w + i * (2 * top_w / 12)
            wave.lineTo(xx, ly + 4 * s * osc(t * 0.9 + i * 0.1, 1.0))
        wave.lineTo(x + top_w + 5, y + 5)
        wave.lineTo(x - top_w - 5, y + 5)
        wave.close()
        c.drawPath(wave, liq)
        ellipse(c, x, ly, top_w * 0.95, 9 * s, shade(liquid, 0.3), a)
        # little bubbles
        for i in range(6):
            bx = x - 40 * s + (i * 23 * s) % (80 * s)
            byy = y - ((t * 30 * s + i * 37 * s) % (h * fill * 0.85))
            circle(c, bx, byy, 4 * s, '#ffffff', 0.35 * a)
        if garnish:
            for i, (gx, gc) in enumerate([(-35, '#d9a066'), (0, '#7bc96f'), (30, '#ff9fb5'), (55, '#d9a066')]):
                ellipse(c, x + gx * s, ly - 2 * s + 2 * s * osc(t, 0.9, i), 12 * s, 6 * s, gc, a)
        c.restore()
    # glass rim + reflection
    line(c, [(x - top_w, y - h), (x + top_w, y - h)], 5 * s, '#ffffff', 0.55 * a)
    line(c, [(x - top_w * 0.72, y - h * 0.9), (x - bot_w * 0.78, y - h * 0.12)], 9 * s, '#ffffff', 0.32 * a)
    line(c, [(x - top_w * 0.55, y - h * 0.9), (x - top_w * 0.5, y - h * 0.75)], 6 * s, '#ffffff', 0.25 * a)


def leaf(c, x, y, s=1.0, ang=0.0, h='#2bd17e', a=1.0, n=7, spread=1.0):
    """Stylised cannabis leaf: n slim serrated leaflets fanning upward from (x,y)."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    line(c, [(0, 0), (0, 60 * s)], 7 * s, shade(h, -0.25), a)
    for i in range(n):
        k = (i - (n - 1) / 2) / ((n - 1) / 2)
        an = k * 82 * spread
        ln = (200 - 120 * abs(k) ** 1.4) * s
        wd = ln * 0.13
        c.save()
        c.rotate(an)
        pts = [(0, 0)]
        steps = 8
        for j in range(1, steps + 1):
            yy = -ln * j / steps
            ww = wd * math.sin(math.pi * j / (steps + 0.3)) * (1.15 if j % 2 else 0.85)
            pts.append((ww, yy))
        pts.append((0, -ln * 1.04))
        for j in range(steps, 0, -1):
            yy = -ln * j / steps
            ww = wd * math.sin(math.pi * j / (steps + 0.3)) * (1.15 if j % 2 else 0.85)
            pts.append((-ww, yy))
        path = smooth_path(pts, k=0.35)
        c.drawPath(path, P(h, a))
        c.save()
        c.clipPath(path, doAntiAlias=True)
        c.drawRect(skia.Rect(0, -ln * 1.1, wd * 2, 0), P(shade(h, -0.18), a))
        c.restore()
        line(c, [(0, -6 * s), (0, -ln * 0.92)], 2.4 * s, shade(h, 0.35), a * 0.7)
        c.restore()
    c.restore()


def molecule(c, x, y, s=1.0, kind='thc', t=0.0, a=1.0, rot=0.0, glow_a=0.35):
    pal = dict(thc=('#3ee07f', '#1f9d5a', '#c8ffd9'), ohthc=('#ffc53d', '#ff7a1a', '#fff1b8'),
               ana=('#ff5fae', '#b82d7a', '#ffd1e8'), nt=('#5fd4ff', '#2b7bd6', '#d6f6ff'))[kind]
    rng = np.random.default_rng({'thc': 1, 'ohthc': 2, 'ana': 3, 'nt': 4}[kind])
    n = {'thc': 6, 'ohthc': 7, 'ana': 6, 'nt': 3}[kind]
    pts = []
    ang = rot + t * 0.4
    for i in range(n):
        a_ = ang + i * 2 * math.pi / n * (0.85 if kind == 'ana' else 1) + rng.random() * 0.4
        rr = (28 + 14 * (i % 2)) * s
        if kind == 'ana':
            pts.append((x - 70 * s + i * 28 * s, y + (12 if i % 2 else -12) * s + 4 * s * osc(t, 0.8, i)))
        else:
            pts.append((x + math.cos(a_) * rr, y + math.sin(a_) * rr))
    if glow_a:
        glow(c, x, y, 75 * s, pal[0], glow_a * a)
    for i in range(len(pts) - 1 + (0 if kind == 'ana' else 1)):
        p0, p1 = pts[i], pts[(i + 1) % len(pts)]
        line(c, [p0, p1], 8 * s, pal[2], a * 0.85)
    if kind == 'ohthc':
        ox, oy = pts[0][0] + 24 * s, pts[0][1] - 20 * s
        line(c, [pts[0], (ox, oy)], 8 * s, pal[2], a * 0.85)
        circle(c, ox, oy, 13 * s, '#ff3d5a', a)
    for i, (px, py) in enumerate(pts):
        rr = (15 if i % 2 else 12) * s
        circle(c, px, py, rr, pal[i % 2], a)
        circle(c, px - rr * 0.3, py - rr * 0.35, rr * 0.3, '#ffffff', a * 0.6)


def clock(c, x, y, r, hours, h='#ffffff', face_c='#2a1a5e', a=1.0, ticks=True):
    circle(c, x, y + r * 0.08, r * 1.04, '#120734', a * 0.4)
    circle(c, x, y, r, face_c, a)
    circle(c, x, y, r * 0.86, shade(face_c, 0.08), a)
    if ticks:
        for i in range(12):
            an = i / 12 * 2 * math.pi
            line(c, [(x + math.sin(an) * r * 0.72, y - math.cos(an) * r * 0.72),
                     (x + math.sin(an) * r * 0.8, y - math.cos(an) * r * 0.8)], r * 0.05, h, a * 0.8)
    ha = hours / 12 * 2 * math.pi
    ma = (hours % 1) * 2 * math.pi
    line(c, [(x, y), (x + math.sin(ha) * r * 0.45, y - math.cos(ha) * r * 0.45)], r * 0.09, h, a)
    line(c, [(x, y), (x + math.sin(ma) * r * 0.68, y - math.cos(ma) * r * 0.68)], r * 0.06, '#ff5fae', a)
    circle(c, x, y, r * 0.07, h, a)


BRAIN_PINK = '#ff7eb6'


def brain_path(x, y, s):
    pts = [(-230, 40), (-250, -40), (-215, -120), (-140, -175), (-40, -200), (60, -195), (150, -165), (215, -105),
           (245, -20), (235, 50), (190, 95), (120, 105), (40, 95), (-40, 110), (-120, 105), (-195, 85)]
    return smooth_path([(x + px * s, y + py * s) for px, py in pts], k=0.6)


def brain(c, x, y, s=1.0, t=0.0, h=BRAIN_PINK, expr=None, look=(0, 0), a=1.0, stem=True, glow_c=None, glow_a=0.0,
          regions=None, face_r=120):
    """Side-view cartoon brain facing left (frontal lobe at -x). regions: dict name->alpha to highlight."""
    regions = regions or {}
    RC = {'hippo': '#ffe14d', 'amyg': '#ff3d6e', 'cereb': '#4fd8ff', 'basal': '#4fd8ff', 'stem': '#4dffb8',
          'smell': '#ffc53d'}
    if glow_c and glow_a > 0:
        glow(c, x, y - 40 * s, 420 * s, glow_c, glow_a)
    st = cb = None
    if stem:
        st = smooth_path([(x + 30 * s, y + 80 * s), (x + 95 * s, y + 85 * s), (x + 85 * s, y + 160 * s),
                          (x + 75 * s, y + 262 * s), (x + 30 * s, y + 264 * s), (x + 35 * s, y + 160 * s)], k=0.4)
        shaded(c, st, mix(shade(h, -0.12), RC['stem'], 0.85 * regions.get('stem', 0)), a, dark=-0.2)
        cb = smooth_path([(x + 85 * s, y + 80 * s), (x + 200 * s, y + 55 * s), (x + 240 * s, y + 110 * s),
                          (x + 190 * s, y + 175 * s), (x + 110 * s, y + 165 * s)], k=0.6)
        shaded(c, cb, mix(shade(h, -0.05), RC['cereb'], 0.85 * regions.get('cereb', 0)), a, dark=-0.22)
        c.save()
        c.clipPath(cb, doAntiAlias=True)
        for i in range(5):
            yy = y + (70 + i * 22) * s
            line(c, [(x + 90 * s, yy + 12 * s), (x + 165 * s, yy - 8 * s), (x + 250 * s, yy + 10 * s)], 4 * s,
                 shade(h, -0.3), a * 0.6)
        c.restore()
    bp = brain_path(x, y, s)
    shaded(c, bp, h, a, dark=-0.22, off=(0.06, 0.1))
    c.save()
    c.clipPath(bp, doAntiAlias=True)
    rng = np.random.default_rng(11)
    for i in range(14):
        cx = x + (-190 + (i % 5) * 95 + rng.random() * 30) * s
        cy = y + (-140 + (i // 5) * 85 + rng.random() * 25) * s
        pts = [(cx + (j * 22 - 40) * s, cy + 18 * s * math.sin(j * 1.7 + i)) for j in range(5)]
        c.drawPath(smooth_path(pts, closed=False), P(shade(h, -0.3), a * 0.6, stroke=6 * s))
    # inner regions (seen "through" the cortex)
    inner = {'hippo': [(-60, 20), (-15, 2), (40, 12), (62, 38), (20, 30), (-35, 42)],
             'amyg': [(-95, 35), (-70, 22), (-52, 40), (-68, 60), (-92, 56)],
             'basal': [(-55, -55), (0, -78), (45, -50), (20, -20), (-35, -22)],
             'smell': [(-235, 70), (-180, 62), (-150, 78), (-185, 90), (-232, 88)]}
    for k, pts in inner.items():
        al = regions.get(k, 0)
        if al > 0:
            pp = [(x + px * s, y + py * s) for px, py in pts]
            cx = sum(p[0] for p in pp) / len(pp)
            cy = sum(p[1] for p in pp) / len(pp)
            glow(c, cx, cy, 150 * s, RC[k], 0.5 * al * a)
            path = smooth_path(pp)
            c.drawPath(path, P(RC[k], al * a))
            glow(c, cx - 8 * s, cy - 6 * s, 30 * s, '#ffffff', 0.5 * al * a)
    c.restore()
    for k in ('cereb', 'stem'):
        al = regions.get(k, 0)
        if al > 0:
            cx, cy = (x + 165 * s, y + 115 * s) if k == 'cereb' else (x + 60 * s, y + 200 * s)
            glow(c, cx, cy, 190 * s, RC[k], 0.35 * al * a)
    if expr:
        face(c, x - 10 * s, y - 50 * s, face_r * s, expr, look, t, skin=h, eye_gap=0.5, eye_r=0.3)
