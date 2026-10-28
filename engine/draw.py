"""Drawing engine: primitives, characters, props and backgrounds (skia, 1920x1080)."""
import math, os, random
import numpy as np
import skia

W, H = 1920, 1080
FPS = 30
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, 'fonts')

TF_HAND = skia.Typeface.MakeFromFile(os.path.join(FONT_DIR, 'PatrickHand-Regular.ttf'))
TF_UI = skia.Typeface.MakeFromFile(os.path.join(FONT_DIR, 'Baloo2.ttf'))
TF_BOLD = skia.Typeface.MakeFromFile(os.path.join(FONT_DIR, 'LuckiestGuy-Regular.ttf'))

INK = '#1b1820'

# ---------------------------------------------------------------- helpers

def hexc(h):
    h = h.lstrip('#')
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def col(h, a=1.0):
    r, g, b = hexc(h)
    return skia.ColorSetARGB(max(0, min(255, int(a * 255))), r, g, b)


def mix(h1, h2, t):
    a, b = hexc(h1), hexc(h2)
    t = max(0.0, min(1.0, t))
    return '#%02x%02x%02x' % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def paint(h=INK, a=1.0, stroke=None, blur=None, cap='round', shader=None):
    p = skia.Paint(AntiAlias=True)
    p.setColor(col(h, a))
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap if cap == 'round' else skia.Paint.kButt_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if shader is not None:
        p.setShader(shader)
        p.setAlphaf(a)
    return p


def clamp01(x):
    return max(0.0, min(1.0, x))


def ease(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp01(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ramp(t, a, b):
    """0 before a, 1 after b, eased between."""
    if b <= a:
        return 1.0 if t >= a else 0.0
    return ease((t - a) / (b - a))


def window(t, a, b, fade=0.4):
    return min(ramp(t, a, a + fade), 1 - ramp(t, b - fade, b))


def lerp(a, b, t):
    return a + (b - a) * t


def lin_grad(p0, p1, colors, pos=None):
    return skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)],
                                          [col(*c) if isinstance(c, tuple) else col(c) for c in colors], pos)


def rad_grad(center, r, colors, pos=None):
    return skia.GradientShader.MakeRadial(skia.Point(*center), r,
                                          [col(*c) if isinstance(c, tuple) else col(c) for c in colors], pos)


def rrect(c, x, y, w, h, r, fill, outline=INK, ow=5, a=1.0):
    rect = skia.Rect.MakeXYWH(x, y, w, h)
    c.drawRoundRect(rect, r, r, paint(fill, a))
    if outline:
        c.drawRoundRect(rect, r, r, paint(outline, a, stroke=ow))


def circle(c, x, y, r, fill, outline=INK, ow=5, a=1.0):
    c.drawCircle(x, y, r, paint(fill, a))
    if outline:
        c.drawCircle(x, y, r, paint(outline, a, stroke=ow))


def oval(c, x, y, rx, ry, fill, outline=None, ow=4, a=1.0):
    rect = skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y + ry)
    c.drawOval(rect, paint(fill, a))
    if outline:
        c.drawOval(rect, paint(outline, a, stroke=ow))


def glow(c, x, y, r, h, a=0.5):
    c.drawCircle(x, y, r, paint(shader=rad_grad((x, y), r, [(h, a), (h, a * 0.35), (h, 0)], [0, 0.4, 1])))


def limb(c, pts, w, fill, outline=INK, ow=5):
    path = skia.Path()
    path.moveTo(*pts[0])
    for p in pts[1:]:
        path.lineTo(*p)
    if outline:
        c.drawPath(path, paint(outline, stroke=w + ow * 2))
    c.drawPath(path, paint(fill, stroke=w))


def font(tf, size):
    f = skia.Font(tf, size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


def text(c, s, x, y, size=46, h='#f3ede2', a=1.0, tf=None, align='center', shadow=True,
         outline=None, ow=8, glow_col=None):
    f = font(tf or TF_HAND, size)
    w = f.measureText(s)
    if align == 'center':
        x -= w / 2
    elif align == 'right':
        x -= w
    if glow_col:
        c.drawString(s, x, y, f, paint(glow_col, a * 0.9, blur=size * 0.25))
    if shadow:
        c.drawString(s, x + 2, y + 3, f, paint('#000000', a * 0.6, blur=3))
    if outline:
        p = paint(outline, a, stroke=ow)
        c.drawString(s, x, y, f, p)
    c.drawString(s, x, y, f, paint(h, a))
    return w


def measure(s, size, tf=None):
    return font(tf or TF_HAND, size).measureText(s)


# ---------------------------------------------------------------- characters

KID = dict(skin='#e8bf98', hoodie='#e3a33e', hoodie_dark='#b97f25', pants='#33405e', shoe='#efe9e0',
           hair='#2a201c', hair_style='messy', height=1.0)
DEV = dict(skin='#a9714a', hoodie='#6f5aa8', hoodie_dark='#52417f', pants='#2c2f3a', shoe='#d64545',
           hair='#c8423b', hair_style='beanie', height=1.08)

EXPR = {
    #          brow_l, brow_r (tilt), brow_y, mouth, eye
    'neutral': dict(brow=0, brow_y=0, mouth='line', eye='dot'),
    'happy': dict(brow=-8, brow_y=-6, mouth='smile', eye='happy', blush=0.5),
    'smile': dict(brow=-4, brow_y=-3, mouth='smile', eye='dot', blush=0.3),
    'bored': dict(brow=0, brow_y=6, mouth='line', eye='lid'),
    'wow': dict(brow=-10, brow_y=-14, mouth='o', eye='wide'),
    'dazed': dict(brow=-6, brow_y=-8, mouth='smirk', eye='wide', blush=0.6),
    'tired': dict(brow=10, brow_y=4, mouth='flat_down', eye='lid', bags=1.0),
    'sad': dict(brow=16, brow_y=-2, mouth='frown', eye='dot', bags=0.7),
    'worried': dict(brow=14, brow_y=-6, mouth='wobble', eye='wide', bags=0.5),
    'determined': dict(brow=-16, brow_y=4, mouth='line', eye='dot'),
    'shock': dict(brow=-12, brow_y=-16, mouth='o', eye='wide'),
    'calm': dict(brow=-3, brow_y=0, mouth='smile', eye='closed'),
    'asleep': dict(brow=0, brow_y=4, mouth='line', eye='closed'),
}


def draw_hair(c, hx, hy, r, ch, t=0):
    if ch['hair_style'] == 'messy':
        p = skia.Path()
        rect = skia.Rect.MakeLTRB(hx - r * 1.02, hy - r * 1.02, hx + r * 1.02, hy + r * 1.02)
        p.arcTo(rect, 170, 200, True)
        # fringe back across forehead
        pts = [(0.92, -0.18), (0.62, -0.42), (0.42, -0.2), (0.12, -0.46), (-0.18, -0.24),
               (-0.42, -0.5), (-0.7, -0.28), (-1.0, -0.1)]
        prev = (hx + r * 1.0, hy - r * 0.15)
        for i, (px, py) in enumerate(pts):
            pt = (hx + px * r, hy + py * r)
            mid = ((prev[0] + pt[0]) / 2, (prev[1] + pt[1]) / 2 + (r * 0.08 if i % 2 else -r * 0.04))
            p.quadTo(mid[0], mid[1], pt[0], pt[1])
            prev = pt
        p.close()
        c.drawPath(p, paint(ch['hair']))
        c.drawPath(p, paint(INK, stroke=r * 0.06))
        # cowlick
        sw = math.sin(t * 2.2) * r * 0.04
        q = skia.Path()
        q.moveTo(hx - r * 0.1, hy - r * 0.98)
        q.quadTo(hx + r * 0.05 + sw, hy - r * 1.35, hx + r * 0.32 + sw, hy - r * 1.22)
        q.quadTo(hx + r * 0.1, hy - r * 1.15, hx + r * 0.12, hy - r * 0.96)
        q.close()
        c.drawPath(q, paint(ch['hair']))
        c.drawPath(q, paint(INK, stroke=r * 0.05))
    elif ch['hair_style'] in ('short', 'bun', 'long', 'curly', 'cap'):
        style = ch['hair_style']
        hc = ch['hair']
        if style == 'long':  # side locks behind the face line
            for sd in (-1, 1):
                lp_ = skia.Path()
                lp_.moveTo(hx + sd * r * 0.98, hy - r * 0.1)
                lp_.quadTo(hx + sd * r * 1.18, hy + r * 0.7, hx + sd * r * 0.9, hy + r * 1.15)
                lp_.lineTo(hx + sd * r * 0.62, hy + r * 1.05)
                lp_.quadTo(hx + sd * r * 0.86, hy + r * 0.5, hx + sd * r * 0.8, hy - r * 0.05)
                lp_.close()
                c.drawPath(lp_, paint(hc))
                c.drawPath(lp_, paint(INK, stroke=r * 0.05))
        if style == 'curly':
            for i in range(9):
                ang = math.radians(195 + i * 18.75)
                circle(c, hx + math.cos(ang) * r * 0.9, hy + math.sin(ang) * r * 0.9, r * 0.26, hc, INK, ow=r * 0.04)
            circle(c, hx, hy - r * 0.62, r * 0.42, hc, None)
            return
        p = skia.Path()
        rect = skia.Rect.MakeLTRB(hx - r * 1.02, hy - r * 1.02, hx + r * 1.02, hy + r * 1.02)
        p.arcTo(rect, 175, 190, True)
        p.quadTo(hx + r * 0.5, hy - r * 0.62, hx - r * 0.1, hy - r * 0.5)
        p.quadTo(hx - r * 0.6, hy - r * 0.42, hx - r * 1.0, hy - r * 0.05)
        p.close()
        c.drawPath(p, paint(hc))
        c.drawPath(p, paint(INK, stroke=r * 0.06))
        if style == 'bun':
            circle(c, hx + r * 0.1, hy - r * 1.18, r * 0.32, hc, INK, ow=r * 0.05)
        if style == 'cap':
            cc = ch.get('cap', '#2f6fd6')
            cp = skia.Path()
            cp.arcTo(skia.Rect.MakeLTRB(hx - r * 1.04, hy - r * 1.1, hx + r * 1.04, hy + r * 0.9), 180, 180, True)
            cp.close()
            c.drawPath(cp, paint(cc))
            c.drawPath(cp, paint(INK, stroke=r * 0.06))
            rrect(c, hx - r * 0.2, hy - r * 0.32, r * 1.45, r * 0.2, r * 0.1, mix(cc, '#000000', 0.25), ow=r * 0.05)
    elif ch['hair_style'] == 'beanie':
        p = skia.Path()
        rect = skia.Rect.MakeLTRB(hx - r * 1.04, hy - r * 1.08, hx + r * 1.04, hy + r * 1.0)
        p.arcTo(rect, 180, 180, True)
        p.lineTo(hx + r * 1.04, hy - r * 0.2)
        p.lineTo(hx - r * 1.04, hy - r * 0.2)
        p.close()
        c.drawPath(p, paint(ch['hair']))
        c.drawPath(p, paint(INK, stroke=r * 0.06))
        rrect(c, hx - r * 1.1, hy - r * 0.42, r * 2.2, r * 0.3, r * 0.14, mix(ch['hair'], '#000000', 0.25), ow=r * 0.06)
        circle(c, hx, hy - r * 1.12, r * 0.16, mix(ch['hair'], '#ffffff', 0.2), ow=r * 0.05)


def draw_face(c, hx, hy, r, expr='neutral', look=(0, 0), blink=0.0, bags=None, pupil_glow=None,
              tear=None, sweat=None, extra=None):
    e = dict(EXPR.get(expr, EXPR['neutral']))
    if extra:
        e.update(extra)
    lx, ly = look
    ex = r * 0.34
    ey = hy + r * 0.05 + ly * r * 0.08
    bags = e.get('bags', 0) if bags is None else bags
    if e.get('blush'):
        for s in (-1, 1):
            oval(c, hx + s * r * 0.55 + lx * r * 0.06, hy + r * 0.38, r * 0.16, r * 0.09, '#e46a6a', a=e['blush'] * 0.5)
    for s in (-1, 1):
        cx = hx + s * ex + lx * r * 0.12
        if bags > 0:
            arc = skia.Path()
            arc.addArc(skia.Rect.MakeLTRB(cx - r * 0.16, ey - r * 0.02, cx + r * 0.16, ey + r * 0.26), 20, 140)
            c.drawPath(arc, paint('#7a4f7e', 0.75 * bags, stroke=r * 0.05))
        eye = e['eye']
        bl = 1 - blink
        if eye == 'closed' or bl < 0.12:
            arc = skia.Path()
            if expr == 'calm' or e['eye'] == 'closed' and expr != 'asleep':
                arc.addArc(skia.Rect.MakeLTRB(cx - r * 0.12, ey - r * 0.1, cx + r * 0.12, ey + r * 0.1), 200, 140)
            else:
                arc.addArc(skia.Rect.MakeLTRB(cx - r * 0.12, ey - r * 0.12, cx + r * 0.12, ey + r * 0.06), 20, 140)
            c.drawPath(arc, paint(INK, stroke=r * 0.05))
        elif eye == 'happy':
            arc = skia.Path()
            arc.addArc(skia.Rect.MakeLTRB(cx - r * 0.12, ey - r * 0.06, cx + r * 0.12, ey + r * 0.16), 200, 140)
            c.drawPath(arc, paint(INK, stroke=r * 0.055))
        elif eye == 'wide':
            oval(c, cx, ey, r * 0.15, r * 0.17 * bl, '#fbf7f0', INK, ow=r * 0.03)
            pr = r * 0.075
            if pupil_glow:
                glow(c, cx + lx * r * 0.05, ey, r * 0.16, pupil_glow, 0.6)
            oval(c, cx + lx * r * 0.05, ey + ly * r * 0.03, pr, pr * bl, INK)
            circle(c, cx + lx * r * 0.05 + pr * 0.35, ey - pr * 0.35 * bl, pr * 0.3, '#ffffff', None)
        else:
            oval(c, cx, ey, r * 0.075, r * 0.1 * bl, INK)
            if pupil_glow:
                glow(c, cx, ey, r * 0.12, pupil_glow, 0.55)
            circle(c, cx + r * 0.025, ey - r * 0.035 * bl, r * 0.025, '#ffffff', None)
            if eye == 'lid':
                lid = skia.Path()
                lid.addRect(skia.Rect.MakeLTRB(cx - r * 0.12, ey - r * 0.16, cx + r * 0.12, ey - r * 0.005))
                c.save()
                c.clipRect(skia.Rect.MakeLTRB(cx - r * 0.13, ey - r * 0.2, cx + r * 0.13, ey + r * 0.2))
                c.drawPath(lid, paint(e.get('skin', '#e8bf98')))
                c.restore()
                c.drawLine(cx - r * 0.1, ey, cx + r * 0.1, ey, paint(INK, stroke=r * 0.04))
        # brows
        tilt = e['brow'] * s
        by = ey - r * 0.27 + e['brow_y'] * r * 0.01
        dx = math.cos(math.radians(tilt)) * r * 0.12
        dy = math.sin(math.radians(tilt)) * r * 0.12
        c.drawLine(cx - dx, by + dy * s * -1 if False else by - dy, cx + dx, by + dy, paint(INK, stroke=r * 0.05))
    # mouth
    mx, my = hx + lx * r * 0.1, hy + r * 0.48
    m = e['mouth']
    p = skia.Path()
    if m == 'smile':
        p.moveTo(mx - r * 0.18, my - r * 0.04)
        p.quadTo(mx, my + r * 0.16, mx + r * 0.18, my - r * 0.04)
        c.drawPath(p, paint(INK, stroke=r * 0.05))
    elif m == 'frown':
        p.moveTo(mx - r * 0.15, my + r * 0.08)
        p.quadTo(mx, my - r * 0.06, mx + r * 0.15, my + r * 0.08)
        c.drawPath(p, paint(INK, stroke=r * 0.05))
    elif m == 'o':
        oval(c, mx, my + r * 0.03, r * 0.07, r * 0.09, '#5a2a2a', INK, ow=r * 0.035)
    elif m == 'smirk':
        p.moveTo(mx - r * 0.12, my)
        p.quadTo(mx + r * 0.02, my + r * 0.08, mx + r * 0.16, my - r * 0.05)
        c.drawPath(p, paint(INK, stroke=r * 0.05))
    elif m == 'wobble':
        p.moveTo(mx - r * 0.15, my + r * 0.03)
        for i in range(1, 7):
            p.lineTo(mx - r * 0.15 + i * r * 0.05, my + r * 0.03 + (r * 0.025 if i % 2 else -r * 0.015))
        c.drawPath(p, paint(INK, stroke=r * 0.04))
    elif m == 'flat_down':
        p.moveTo(mx - r * 0.13, my + r * 0.04)
        p.quadTo(mx, my - r * 0.01, mx + r * 0.13, my + r * 0.04)
        c.drawPath(p, paint(INK, stroke=r * 0.05))
    else:
        c.drawLine(mx - r * 0.12, my, mx + r * 0.12, my, paint(INK, stroke=r * 0.05))
    if tear is not None:
        ty = ey + r * 0.15 + tear * r * 0.55
        a = 1 - clamp01((tear - 0.8) / 0.2)
        dp = skia.Path()
        tx = hx + ex + r * 0.05
        dp.moveTo(tx, ty - r * 0.09)
        dp.quadTo(tx + r * 0.07, ty + r * 0.02, tx, ty + r * 0.05)
        dp.quadTo(tx - r * 0.07, ty + r * 0.02, tx, ty - r * 0.09)
        c.drawPath(dp, paint('#8fd0ff', a))
    if sweat is not None:
        sx, sy = hx + r * 0.78, hy - r * 0.45 + sweat * r * 0.15
        dp = skia.Path()
        dp.moveTo(sx, sy - r * 0.12)
        dp.quadTo(sx + r * 0.09, sy + r * 0.03, sx, sy + r * 0.07)
        dp.quadTo(sx - r * 0.09, sy + r * 0.03, sx, sy - r * 0.12)
        c.drawPath(dp, paint('#bfe6ff'))
        c.drawPath(dp, paint(INK, stroke=r * 0.025))


def draw_head(c, hx, hy, r, ch, expr='neutral', t=0, **kw):
    circle(c, hx, hy, r, ch['skin'], ow=r * 0.065)
    kw.setdefault('extra', {})
    kw['extra'] = dict(kw['extra'], skin=ch['skin'])
    draw_face(c, hx, hy, r, expr, **kw)
    draw_hair(c, hx, hy, r, ch, t)


def arm_pts(sx, sy, a1, a2, s, l1=72, l2=66):
    ex = sx + math.sin(math.radians(a1)) * l1 * s
    ey = sy + math.cos(math.radians(a1)) * l1 * s
    hx = ex + math.sin(math.radians(a2)) * l2 * s
    hy = ey + math.cos(math.radians(a2)) * l2 * s
    return [(sx, sy), (ex, ey), (hx, hy)]


def draw_person(c, x, y, s=1.0, ch=KID, expr='neutral', t=0.0, pose='stand', arms=None, legs=None,
                look=(0, 0), blink=0.0, head_tilt=0.0, bob=0.0, prop=None, prop_t=0.0, face_kw=None,
                hand_items=None):
    """Feet anchored at (x, y). Returns dict of useful anchor points."""
    s = s * ch.get('height', 1.0)
    face_kw = face_kw or {}
    y = y + bob * s
    sitting = pose == 'sit'
    hip_y = y - (110 * s if not sitting else 118 * s)
    if sitting:
        hip_y = y - 118 * s
    # legs
    if legs is None:
        legs = ((0, 0), (0, 0))
    for side, (a1, a2) in zip((-1, 1), legs):
        hx0 = x + side * 24 * s
        if sitting:
            knee = (hx0 + side * 6 * s, hip_y + 4 * s)
            foot = (knee[0], y - 14 * s)
            pts = [(hx0, hip_y - 6 * s), (knee[0] + side * 2, knee[1]), foot]
            pts = [(hx0, hip_y - 8 * s), (hx0 + side * 4 * s, hip_y + 2 * s), foot]
        else:
            pts = arm_pts(hx0, hip_y, a1, a2, s, 56, 52)
        limb(c, pts, 30 * s, ch['pants'], ow=4.5 * s)
        fx, fy = pts[-1]
        oval(c, fx + side * 6 * s, fy + 2 * s, 24 * s, 12 * s, ch['shoe'], INK, ow=4.5 * s)
    # torso (hoodie)
    tx0, ty0 = x - 64 * s, hip_y - 160 * s
    rrect(c, tx0, ty0, 128 * s, 172 * s, 46 * s, ch['hoodie'], ow=5.5 * s)
    # pocket
    pk = skia.Path()
    pk.moveTo(x - 40 * s, hip_y - 22 * s)
    pk.lineTo(x - 30 * s, hip_y - 62 * s)
    pk.lineTo(x + 30 * s, hip_y - 62 * s)
    pk.lineTo(x + 40 * s, hip_y - 22 * s)
    c.drawPath(pk, paint(ch['hoodie_dark'], stroke=4 * s))
    # strings
    for sd in (-1, 1):
        c.drawLine(x + sd * 14 * s, ty0 + 14 * s, x + sd * 16 * s, ty0 + 52 * s, paint('#f4ecdf', stroke=4 * s))
    sh_y = ty0 + 38 * s
    head_c = (x + head_tilt * 0.4 * s, ty0 - 58 * s)
    hr = 74 * s
    # prop behind arms (guitar)
    if prop == 'guitar':
        draw_guitar(c, x + 8 * s, hip_y - 52 * s, s * 0.95, -28)
    if arms is None:
        arms = ((12, 6), (-12, -6))
    hands = []
    for side, (a1, a2) in zip((-1, 1), arms):
        pts = arm_pts(x + side * 56 * s, sh_y, a1 * side * -1 if False else a1, a2, s)
        limb(c, pts, 28 * s, ch['hoodie'], ow=5 * s)
        circle(c, pts[-1][0], pts[-1][1], 16 * s, ch['skin'], ow=4.5 * s)
        hands.append(pts[-1])
    if hand_items:
        for fn in hand_items:
            fn(c, hands)
    c.save()
    c.rotate(head_tilt, head_c[0], head_c[1] + hr)
    draw_head(c, head_c[0], head_c[1], hr, ch, expr, t, look=look, blink=blink, **face_kw)
    c.restore()
    return dict(head=head_c, hr=hr, hands=hands, hip=(x, hip_y))


def blink_at(t, period=3.7, offset=0.0):
    ph = (t + offset) % period
    return 1.0 if ph < 0.12 else 0.0


# ---------------------------------------------------------------- props

def draw_guitar(c, x, y, s=1.0, angle=-28, a=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(angle)
    wood = '#c8783b'
    # neck
    rrect(c, 40 * s, -12 * s, 230 * s, 24 * s, 6 * s, '#6b3f22', ow=4 * s)
    for i in range(1, 9):
        c.drawLine((60 + i * 22) * s, -11 * s, (60 + i * 22) * s, 11 * s, paint('#d9c6a0', 0.7, stroke=2 * s))
    rrect(c, 262 * s, -20 * s, 46 * s, 40 * s, 10 * s, '#4a2a17', ow=4 * s)
    body = skia.Path()
    body.addCircle(-58 * s, 0, 64 * s)
    body.addCircle(18 * s, 0, 50 * s)
    body.setFillType(skia.PathFillType.kWinding)
    merged = skia.Op(body, skia.Path.Rect(skia.Rect.MakeLTRB(-60 * s, -44 * s, 20 * s, 44 * s)), skia.PathOp.kUnion_PathOp)
    path = merged if merged else body
    c.drawPath(path, paint(wood))
    c.drawPath(path, paint(INK, stroke=5 * s))
    circle(c, 4 * s, 0, 20 * s, '#2a1a12', INK, ow=3 * s)
    rrect(c, -78 * s, -16 * s, 14 * s, 32 * s, 3 * s, '#3a2416', ow=3 * s)
    for i in range(-2, 3):
        c.drawLine(-70 * s, i * 5 * s, 300 * s, i * 4 * s, paint('#f2eada', 0.55, stroke=1.4 * s))
    c.restore()


def draw_laptop(c, x, y, s=1.0, screen='#8fb4ff', on=1.0, content=None, t=0.0):
    """Laptop seen from the front-side, base at (x, y)."""
    if on > 0:
        glow(c, x, y - 120 * s, 330 * s, screen, 0.3 * on)
    rrect(c, x - 150 * s, y - 210 * s, 300 * s, 190 * s, 12 * s, '#2a2b33', INK, ow=5 * s)
    rrect(c, x - 136 * s, y - 198 * s, 272 * s, 166 * s, 6 * s, mix('#0d0f16', screen, 0.85 * on), None)
    if content == 'work' and on > 0:
        for i in range(6):
            rrect(c, x - 120 * s, y - 186 * s + i * 24 * s, (180 - (i * 37) % 90) * s, 10 * s, 5 * s, '#33405e', None)
    elif content == 'feed' and on > 0:
        for i in range(3):
            rrect(c, x - 120 * s + i * 82 * s, y - 180 * s, 72 * s, 110 * s, 8 * s,
                  ['#5f4b8b', URGE['glow'], '#3d5a80'][i], None, a=0.85)
    elif content == 'game' and on > 0:
        c.drawRect(skia.Rect.MakeLTRB(x - 136 * s, y - 90 * s, x + 136 * s, y - 32 * s), paint('#2e7d4f'))
        for i in range(4):
            circle(c, x - 90 * s + i * 60 * s + math.sin(t * 3 + i) * 8 * s, y - 120 * s, 14 * s,
                   ['#ff5a5f', '#ffd36a', '#6ad1ff', '#b38bff'][i], INK, ow=3 * s)
    pb = skia.Path()
    pb.moveTo(x - 170 * s, y)
    pb.lineTo(x + 170 * s, y)
    pb.lineTo(x + 150 * s, y - 22 * s)
    pb.lineTo(x - 150 * s, y - 22 * s)
    pb.close()
    c.drawPath(pb, paint('#3a3b45'))
    c.drawPath(pb, paint(INK, stroke=5 * s))


def draw_ball(c, x, y, r, rot=0.0):
    circle(c, x, y, r, '#e8783a', INK, ow=r * 0.1)
    c.save()
    c.rotate(rot, x, y)
    c.drawLine(x - r, y, x + r, y, paint(INK, stroke=r * 0.07))
    c.drawLine(x, y - r, x, y + r, paint(INK, stroke=r * 0.07))
    arc = skia.Path()
    arc.addArc(skia.Rect.MakeLTRB(x - r * 1.5, y - r, x - r * 0.3, y + r), -60, 120)
    arc.addArc(skia.Rect.MakeLTRB(x + r * 0.3, y - r, x + r * 1.5, y + r), 120, 120)
    c.drawPath(arc, paint(INK, stroke=r * 0.07))
    c.restore()


def draw_camera(c, x, y, s=1.0, flash=0.0, body='#2a2b33'):
    """Small photo camera centred at (x, y). flash 0..1 fires the flash glow."""
    rrect(c, x - 62 * s, y - 38 * s, 124 * s, 76 * s, 12 * s, body, INK, ow=4 * s)
    rrect(c, x - 40 * s, y - 52 * s, 34 * s, 18 * s, 4 * s, body, INK, ow=3.5 * s)
    circle(c, x + 6 * s, y + 2 * s, 28 * s, '#3a3b45', INK, ow=4 * s)
    circle(c, x + 6 * s, y + 2 * s, 16 * s, '#1b2a44', None)
    circle(c, x + 11 * s, y - 4 * s, 5 * s, '#9fc2ff', None, a=0.8)
    rrect(c, x + 34 * s, y - 30 * s, 18 * s, 10 * s, 3 * s, '#e8e8ee', None)
    if flash > 0:
        glow(c, x + 43 * s, y - 25 * s, 260 * s * flash, '#ffffff', 0.7 * flash)
        circle(c, x + 43 * s, y - 25 * s, 10 * s, '#ffffff', None, a=flash)


def draw_sketchbook(c, x, y, s=1.0, t=0.0, progress=0.6):
    c.save()
    c.rotate(-8, x, y)
    rrect(c, x - 70 * s, y - 50 * s, 140 * s, 100 * s, 6 * s, '#f6f1e6', INK, ow=4 * s)
    p = skia.Path()
    n = int(10 * progress) + 1
    for i in range(n):
        px = x - 50 * s + i * 10 * s
        py = y + math.sin(i * 0.9) * 20 * s
        (p.moveTo if i == 0 else p.lineTo)(px, py)
    c.drawPath(p, paint('#3d5a80', stroke=3 * s))
    circle(c, x + 30 * s, y - 15 * s, 14 * s * progress, '#e9c46a', None, a=0.9)
    c.restore()


def draw_phone_small(c, x, y, s=1.0, glow_col='#7fb6ff', on=1.0, angle=-10):
    c.save()
    c.translate(x, y)
    c.rotate(angle)
    if on > 0:
        glow(c, 0, 0, 180 * s, glow_col, 0.28 * on)
    rrect(c, -20 * s, -36 * s, 40 * s, 72 * s, 8 * s, '#15151a', ow=3.5 * s)
    if on > 0:
        rrect(c, -15 * s, -30 * s, 30 * s, 60 * s, 4 * s, glow_col, None, a=0.9 * on)
    c.restore()


def draw_clock(c, x, y, s, hhmm, glowing=True):
    rrect(c, x, y, 150 * s, 66 * s, 12 * s, '#1a1a1f', '#3a3640', ow=4 * s)
    glow(c, x + 75 * s, y + 33 * s, 110 * s, '#ff3b30', 0.22)
    seven_seg(c, x + 18 * s, y + 13 * s, 26 * s, hhmm, '#ff4136')


SEG = {'0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd', '4': 'fgbc', '5': 'afgcd', '6': 'afgedc',
       '7': 'abc', '8': 'abcdefg', '9': 'abcdfg'}


def seven_seg(c, x, y, h, s, colr):
    w = h * 0.55
    p = paint(colr, stroke=h * 0.13, cap='round')
    cx = x
    for ch in s:
        if ch == ':':
            c.drawCircle(cx + w * 0.15, y + h * 0.3, h * 0.06, paint(colr))
            c.drawCircle(cx + w * 0.15, y + h * 0.75, h * 0.06, paint(colr))
            cx += w * 0.45
            continue
        segs = {'a': ((0, 0), (1, 0)), 'b': ((1, 0), (1, .5)), 'c': ((1, .5), (1, 1)), 'd': ((0, 1), (1, 1)),
                'e': ((0, .5), (0, 1)), 'f': ((0, 0), (0, .5)), 'g': ((0, .5), (1, .5))}
        for sg in SEG.get(ch, ''):
            (a0, b0), (a1, b1) = segs[sg]
            c.drawLine(cx + a0 * w, y + b0 * h * 1.2, cx + a1 * w, y + b1 * h * 1.2, p)
        cx += w * 1.45


URGE = dict(glow='#ff2e88', rim='#ff4f9a', eye='#ffd3e6', pupil='#7a0035', say='#ff6aa8', body=('#3a1748', '#1c0b26', '#0d0612'))


def set_urge_color(glow_hex):
    """Recolour the habit creature from one glow colour."""
    URGE.update(glow=glow_hex, rim=mix(glow_hex, '#ffffff', 0.15), eye=mix(glow_hex, '#ffffff', 0.8),
                pupil=mix(glow_hex, '#000000', 0.55), say=mix(glow_hex, '#ffffff', 0.3),
                body=(mix(glow_hex, '#120818', 0.78), mix(glow_hex, '#08040c', 0.88), '#07040a'))


def draw_urge(c, x, y, r, t, eye=1.0, mouth=0.0, a=1.0, look=(0, 0), hand=None):
    """The 'urge': a smoky violet blob with one magenta eye. (x, y) = bottom centre."""
    if r <= 1 or a <= 0:
        return
    U = URGE
    cy = y - r * 0.95
    c.drawCircle(x, cy, r * 2.0, paint(shader=rad_grad((x, cy), r * 2.0,
                 [(U['glow'], 0.30 * a), (U['pupil'], 0.12 * a), (U['pupil'], 0)], [0, 0.45, 1])))
    path = skia.Path()
    n = 72
    for i in range(n + 1):
        th = 2 * math.pi * i / n
        rr = r * (1 + 0.07 * math.sin(3 * th + t * 2.1) + 0.05 * math.sin(5 * th - t * 3.3)
                  + 0.03 * math.sin(9 * th + t * 5.0))
        px = x + math.cos(th) * rr
        py = cy + math.sin(th) * rr * 1.05
        if math.sin(th) > 0.55:  # flatten / drip at bottom
            py = min(py, y + 0.06 * r * math.sin(th * 7 + t * 4))
        if i == 0:
            path.moveTo(px, py)
        else:
            path.lineTo(px, py)
    path.close()
    c.drawPath(path, paint(U['rim'], 0.55 * a, blur=r * 0.08))
    c.drawPath(path, paint(shader=rad_grad((x - r * 0.25, cy - r * 0.35), r * 1.5,
                                           [(U['body'][0], a), (U['body'][1], a), (U['body'][2], a)], [0, 0.5, 1])))
    c.drawPath(path, paint(U['rim'], 0.5 * a, stroke=max(2, r * 0.03)))
    if hand is not None:  # a wispy arm reaching
        hx, hy = hand
        ap = skia.Path()
        ap.moveTo(x + r * 0.6, cy + r * 0.1)
        ap.quadTo(lerp(x + r * 0.6, hx, 0.5), min(cy, hy) - r * 0.3, hx, hy)
        c.drawPath(ap, paint(U['body'][1], a, stroke=r * 0.22))
        c.drawPath(ap, paint(U['rim'], 0.35 * a, stroke=r * 0.24, blur=r * 0.05))
    # eye
    ex, ey = x + look[0] * r * 0.15, cy - r * 0.15 + look[1] * r * 0.1
    eh = r * 0.32 * max(0.06, eye)
    glow(c, ex, ey, r * 0.7, U['glow'], 0.55 * a)
    oval(c, ex, ey, r * 0.34, eh, U['eye'], None, a=a)
    oval(c, ex + look[0] * r * 0.08, ey, r * 0.08, eh * 0.85, U['pupil'], None, a=a)
    if mouth > 0:
        mp = skia.Path()
        mp.moveTo(ex - r * 0.3, cy + r * 0.38)
        mp.quadTo(ex, cy + r * (0.38 + 0.3 * mouth), ex + r * 0.3, cy + r * 0.38)
        mp.quadTo(ex, cy + r * (0.38 + 0.12 * mouth), ex - r * 0.3, cy + r * 0.38)
        c.drawPath(mp, paint(U['rim'], a * 0.9))


def urge_say(c, s, x, y, t_in, t, size=50, a=1.0):
    """Magenta whisper text with a little shake and per-letter fade."""
    if t < t_in:
        return
    k = clamp01((t - t_in) / 0.6)
    jitter = math.sin(t * 37) * 1.2
    text(c, s, x + jitter, y, size, URGE['say'], a * k, glow_col=URGE['glow'], shadow=False)


# ---------------------------------------------------------------- backgrounds

_cache = {}


def city_layer(seed, n, ymin, ymax, colr, win_col, win_a, x0=-200, x1=2200):
    key = ('city', seed, n, ymin, ymax, colr, win_col, win_a)
    if key in _cache:
        return _cache[key]
    rnd = random.Random(seed)
    bld = []
    x = x0
    while x < x1:
        w = rnd.randint(90, 210)
        top = rnd.randint(ymin, ymax)
        wins = []
        for wy in range(top + 30, 900, 44):
            for wx in range(x + 16, x + w - 24, 34):
                if rnd.random() < 0.28:
                    wins.append((wx, wy, rnd.random()))
        bld.append((x, w, top, wins))
        x += w + rnd.randint(-10, 12)
    _cache[key] = bld
    return bld


def draw_city(c, t, sky=('#f39a5b', '#b4527a', '#3b2b55'), lights=1.0):
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=lin_grad((0, 0), (0, 820), list(reversed(sky)) if False else
                                                             [sky[2], sky[1], sky[0]], [0, 0.55, 1])))
    sun_y = 720
    glow(c, 1180, sun_y, 520, '#ffcf8a', 0.45)
    circle(c, 1180, sun_y, 70, '#ffd9a0', None, a=0.9)
    for layer, (seed, ymin, ymax, colr, wa) in enumerate([(3, 260, 520, '#4a2f55', 0.25), (9, 420, 640, '#2b1d38', 0.6)]):
        for (x, w, top, wins) in city_layer(seed, 0, ymin, ymax, colr, '#ffcf7a', wa):
            c.drawRect(skia.Rect.MakeLTRB(x, top, x + w, 900), paint(colr))
            for (wx, wy, r) in wins:
                on = lights * (0.6 + 0.4 * math.sin(t * 0.6 + r * 20)) if r > 0.15 else 0
                if on > 0:
                    c.drawRect(skia.Rect.MakeXYWH(wx, wy, 14, 20), paint('#ffd27a', wa * on))


def draw_rooftop(c, t, sky=('#f39a5b', '#b4527a', '#3b2b55'), lights=1.0, poster='OPEN MIC', poster2='SAT 8PM'):
    draw_city(c, t, sky, lights)
    # water tank
    c.drawRect(skia.Rect.MakeLTRB(160, 520, 340, 720), paint('#5a3f3a'))
    c.drawRect(skia.Rect.MakeLTRB(160, 520, 340, 720), paint(INK, stroke=5))
    for i in range(5):
        c.drawLine(160, 550 + i * 36, 340, 550 + i * 36, paint('#3e2b29', stroke=4))
    tp = skia.Path()
    tp.moveTo(150, 522)
    tp.lineTo(250, 470)
    tp.lineTo(350, 522)
    tp.close()
    c.drawPath(tp, paint('#4a3230'))
    c.drawPath(tp, paint(INK, stroke=5))
    for lx in (180, 320):
        c.drawLine(lx, 720, lx - 10, 860, paint('#3a2a2a', stroke=10))
    # stair door box
    rrect(c, 1500, 440, 340, 440, 6, '#6a5160', ow=6)
    rrect(c, 1600, 560, 130, 320, 6, '#3d2e3a', ow=5)
    circle(c, 1712, 730, 8, '#d9b86a', ow=3)
    glow(c, 1665, 520, 120, '#ffd27a', 0.35 * lights)
    circle(c, 1665, 520, 14, '#ffe2a0', ow=3)
    if poster:
        c.save()
        c.rotate(3, 1560, 620)
        rrect(c, 1520, 600, 74, 104, 4, '#f2e6c9', ow=3)
        text(c, poster.split()[0], 1557, 638, 22, '#c8423b', shadow=False, tf=TF_BOLD)
        text(c, poster.split()[-1], 1557, 662, 22, '#c8423b', shadow=False, tf=TF_BOLD)
        text(c, poster2, 1557, 690, 18, '#2a2a2a', shadow=False)
        c.restore()
    # string lights
    p = skia.Path()
    p.moveTo(-20, 300)
    p.quadTo(700, 470, 1520, 330)
    c.drawPath(p, paint('#20161f', stroke=3))
    for i in range(1, 24):
        u = i / 24
        bx = (1 - u) ** 2 * -20 + 2 * (1 - u) * u * 700 + u * u * 1520
        by = (1 - u) ** 2 * 300 + 2 * (1 - u) * u * 470 + u * u * 330 + 14
        fl = 0.75 + 0.25 * math.sin(t * 3 + i * 1.7)
        glow(c, bx, by, 36, '#ffcf6a', 0.45 * fl * lights)
        circle(c, bx, by, 7, '#ffe6a6', None, a=0.95 * lights + 0.05)
    # floor
    c.drawRect(skia.Rect.MakeLTRB(0, 860, W, H), paint(shader=lin_grad((0, 860), (0, H), ['#4b3a44', '#2e232c'])))
    c.drawLine(0, 862, W, 862, paint(INK, stroke=6))
    for i in range(0, W, 160):
        c.drawLine(i, 880, i - 60, H, paint('#3e2f39', stroke=3))


def draw_bedroom(c, t, moon=True, lamp=0.0, room_col=('#1d2336', '#131725')):
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=lin_grad((0, 0), (0, 880), [room_col[1], room_col[0]])))
    # window
    wx, wy, ww, wh = 1360, 150, 330, 300
    rrect(c, wx, wy, ww, wh, 8, '#0b1430', '#4b5470', ow=8)
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(wx, wy, ww, wh))
    rnd = random.Random(5)
    for i in range(26):
        sx, sy = wx + rnd.random() * ww, wy + rnd.random() * wh
        tw = 0.5 + 0.5 * math.sin(t * 2 + i)
        circle(c, sx, sy, 1.6 + rnd.random() * 1.5, '#dfe8ff', None, a=0.4 + 0.5 * tw)
    if moon:
        glow(c, wx + 240, wy + 80, 120, '#cfd9ff', 0.35)
        circle(c, wx + 240, wy + 80, 34, '#e9eeff', None)
        circle(c, wx + 256, wy + 70, 30, '#0b1430', None)
    c.restore()
    c.drawLine(wx + ww / 2, wy, wx + ww / 2, wy + wh, paint('#4b5470', stroke=8))
    c.drawLine(wx, wy + wh / 2, wx + ww, wy + wh / 2, paint('#4b5470', stroke=8))
    # moonlight patch
    mp = skia.Path()
    mp.moveTo(wx, wy + wh)
    mp.lineTo(wx + ww, wy + wh)
    mp.lineTo(wx + ww - 260, 880)
    mp.lineTo(wx - 380, 880)
    mp.close()
    c.drawPath(mp, paint('#9fb3ff', 0.05, blur=20))
    # poster
    c.save()
    c.rotate(-2, 300, 300)
    rrect(c, 180, 200, 170, 230, 4, '#2c3550', '#47506c', ow=4)
    circle(c, 265, 290, 50, '#3c4a6e', None)
    draw_guitar(c, 265, 300, 0.32, -55)
    c.restore()
    # floor
    c.drawRect(skia.Rect.MakeLTRB(0, 880, W, H), paint('#0f121b'))
    c.drawLine(0, 880, W, 880, paint('#2a3044', stroke=5))
    # nightstand + clock drawn by scene (needs time); bed
    rrect(c, 300, 740, 190, 140, 10, '#2b2a33', '#45434f', ow=5)
    c.drawLine(310, 806, 480, 806, paint('#45434f', stroke=4))
    circle(c, 395, 776, 6, '#6b6878', None)
    circle(c, 395, 840, 6, '#6b6878', None)
    if lamp > 0:
        glow(c, 395, 700, 360, '#ffbf6a', 0.3 * lamp)


def draw_bed(c, blanket='#3a4a7a', with_body=False):
    # headboard
    rrect(c, 540, 580, 46, 300, 14, '#3a3747', '#55526a', ow=5)
    # frame
    rrect(c, 560, 760, 760, 70, 14, '#34313f', '#55526a', ow=5)
    for lx in (580, 1290):
        c.drawRect(skia.Rect.MakeLTRB(lx, 830, lx + 18, 880), paint('#2a2833'))
    # mattress
    rrect(c, 580, 712, 730, 60, 20, '#5d5f74', '#6e7088', ow=4)
    # pillow
    rrect(c, 595, 676, 170, 52, 26, '#8b8ea6', '#a2a5bb', ow=4)


def draw_blanket(c, colr='#3d4f86', bump=1.0, x0=700, x1=1320, top=700):
    p = skia.Path()
    p.moveTo(x0, 780)
    p.lineTo(x0, top + 10)
    p.cubicTo(x0 + 120, top - 40 * bump, x0 + 330, top - 30 * bump, x0 + 420, top - 5 * bump)
    p.cubicTo(x0 + 500, top + 10, x1 - 60, top - 10 * bump, x1, top + 20)
    p.lineTo(x1 + 10, 800)
    p.quadTo((x0 + x1) / 2, 815, x0, 780)
    p.close()
    c.drawPath(p, paint(colr))
    c.drawPath(p, paint(mix(colr, '#ffffff', 0.25), stroke=5))
    c.drawLine(x0 + 40, top + 14, x0 + 60, 790, paint(mix(colr, '#000000', 0.3), 0.6, stroke=4))


def draw_drawer_light(c, amt):
    if amt > 0:
        glow(c, 395, 806, 300 * (0.5 + amt), '#ff4f9a', 0.45 * amt)
        c.drawRect(skia.Rect.MakeLTRB(312, 800, 478, 812), paint('#ffb3d1', 0.9 * amt))


# ---------------------------------------------------------------- post effects

_rng = np.random.default_rng(7)
_grain = []
for _i in range(8):
    g = (_rng.normal(128, 40, (H // 2, W // 2))).clip(0, 255).astype(np.uint8)
    rgba = np.dstack([g, g, g, np.full_like(g, 255)])
    _grain.append(skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType))


def post(c, frame_idx, vignette=0.55, grain=0.06):
    vp = paint(shader=rad_grad((W / 2, H / 2), W * 0.72, [('#000000', 0), ('#000000', 0), ('#000000', vignette)],
                               [0, 0.55, 1]))
    c.drawRect(skia.Rect.MakeWH(W, H), vp)
    if grain:
        gp = skia.Paint()
        gp.setAlphaf(grain)
        gp.setBlendMode(skia.BlendMode.kOverlay)
        c.drawImageRect(_grain[(frame_idx // 2) % len(_grain)], skia.Rect.MakeWH(W, H),
                        skia.SamplingOptions(skia.FilterMode.kLinear), gp)
