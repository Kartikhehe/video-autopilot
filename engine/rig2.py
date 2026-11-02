"""Character rig v2: semi-realistic 2D cartoon style (clean ink lines, cel shading, human proportions).

Drop-in replacement for draw.draw_person / draw_head / draw_hair: same arguments and return values,
so every template upgrades automatically. Light comes from the top-left; every part gets a cel shadow.

Character dict keys (all optional except skin/hoodie/pants/hair):
  skin, hoodie (= top colour), pants, shoe, hair, hair_style (spiky|messy|short|bun|long|curly|cap|beanie),
  top (tshirt|shirt|hoodie), bottom (pants|shorts), female (bool), glasses (bool), earrings (bool),
  cap (cap colour), stain (bool), height, eyes (iris colour)
"""
import math
import skia
from .draw import paint, mix, col, lerp, clamp01, oval, circle, rrect, INK, draw_guitar

LINE = '#1d1a1c'
LIGHT = (-0.62, -0.78)  # direction the light comes from (top-left)


def _shade(colr, k=0.22):
    return mix(colr, '#2a1a3a', k)


def _hi(colr, k=0.35):
    return mix(colr, '#ffffff', k)


def _skin_shade(skin):
    return mix(skin, '#9a4a3a', 0.28)


def _offset(path, dx, dy):
    p = skia.Path(path)
    p.offset(dx, dy)
    return p


def cel(c, path, base, ow, shade_k=0.22, depth=10.0, line=LINE, shade_col=None, hi=0.0):
    """Fill + cel shadow on the side away from the light + optional highlight + ink outline."""
    c.drawPath(path, paint(base))
    sh = skia.Op(path, _offset(path, LIGHT[0] * depth, LIGHT[1] * depth), skia.PathOp.kDifference_PathOp)
    if sh:
        c.drawPath(sh, paint(shade_col or _shade(base, shade_k)))
    if hi > 0:
        hl = skia.Op(path, _offset(path, -LIGHT[0] * depth * 0.5, -LIGHT[1] * depth * 0.5), skia.PathOp.kDifference_PathOp)
        if hl:
            c.drawPath(hl, paint(_hi(base, 0.45), hi))
    if ow:
        c.drawPath(path, paint(line, stroke=ow))


def stroke_limb(c, pts, w, base, ow, shade=True, line=LINE):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    c.drawPath(p, paint(line, stroke=w + ow * 2))
    c.drawPath(p, paint(base, stroke=w))
    if shade:
        # shadow strip along the side away from the light
        for (a, b) in zip(pts[:-1], pts[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1
            nx, ny = -dy / L, dx / L
            if nx * LIGHT[0] + ny * LIGHT[1] > 0:
                nx, ny = -nx, -ny
            o = w * 0.27
            q = skia.Path()
            q.moveTo(a[0] + nx * o, a[1] + ny * o)
            q.lineTo(b[0] + nx * o, b[1] + ny * o)
            c.drawPath(q, paint(_shade(base, 0.2), stroke=w * 0.38, cap='butt'))


def taper_path(pts, widths):
    """Union of tapered quads + round joints along a polyline (a smooth limb silhouette)."""
    out = None
    for i in range(len(pts) - 1):
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        wa, wb = widths[i] / 2, widths[i + 1] / 2
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        q = skia.Path()
        q.moveTo(ax + nx * wa, ay + ny * wa)
        q.lineTo(bx + nx * wb, by + ny * wb)
        q.lineTo(bx - nx * wb, by - ny * wb)
        q.lineTo(ax - nx * wa, ay - ny * wa)
        q.close()
        out = q if out is None else (skia.Op(out, q, skia.PathOp.kUnion_PathOp) or out)
    for (px, py), w in zip(pts, widths):
        j = skia.Path()
        j.addCircle(px, py, w / 2)
        out = skia.Op(out, j, skia.PathOp.kUnion_PathOp) or out
    return out


def limb2(c, pts, widths, base, ow, depth=6.0, shade_col=None):
    cel(c, taper_path(pts, widths), base, ow, depth=depth, shade_col=shade_col)


def arm_pts(sx, sy, a1, a2, s, l1=96, l2=88):
    ex = sx + math.sin(math.radians(a1)) * l1 * s
    ey = sy + math.cos(math.radians(a1)) * l1 * s
    hx = ex + math.sin(math.radians(a2)) * l2 * s
    hy = ey + math.cos(math.radians(a2)) * l2 * s
    return [(sx, sy), (ex, ey), (hx, hy)]


def draw_hand(c, x, y, ang, s, skin, side=1, kind='open', ow=4.0):
    """Hand at the wrist (x, y), pointing along ang (radians, 0 = down)."""
    c.save()
    c.translate(x, y)
    c.rotate(-math.degrees(ang))
    p = skia.Path()
    if kind == 'fist':
        p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-14 * s, -2 * s, 28 * s, 26 * s), 11 * s, 11 * s))
        cel(c, p, skin, ow, depth=4 * s, shade_col=_skin_shade(skin))
        for i in range(3):
            c.drawLine(-9 * s + i * 7 * s, 16 * s, -9 * s + i * 7 * s, 22 * s, paint(LINE, stroke=ow * 0.55))
    else:
        p.moveTo(-12 * s, 0)
        p.cubicTo(-15 * s, 12 * s, -13 * s, 26 * s, -6 * s, 32 * s)
        p.cubicTo(-1 * s, 35 * s, 7 * s, 34 * s, 11 * s, 28 * s)
        p.cubicTo(14 * s, 20 * s, 14 * s, 8 * s, 12 * s, 0)
        p.close()
        cel(c, p, skin, ow, depth=4 * s, shade_col=_skin_shade(skin))
        # thumb
        t = skia.Path()
        tx = -side * 12 * s
        t.moveTo(tx, 6 * s)
        t.cubicTo(tx - side * 9 * s, 10 * s, tx - side * 10 * s, 20 * s, tx - side * 4 * s, 22 * s)
        t.cubicTo(tx, 22 * s, tx + side * 2 * s, 16 * s, tx + side * 1 * s, 10 * s)
        c.drawPath(t, paint(skin))
        c.drawPath(t, paint(LINE, stroke=ow * 0.8))
        for i in (-1, 1):
            q = skia.Path()
            q.moveTo(i * 4 * s, 22 * s)
            q.lineTo(i * 4.5 * s, 31 * s)
            c.drawPath(q, paint(LINE, stroke=ow * 0.5))
    c.restore()


# ---------------------------------------------------------------- head

def head_path(cx, cy, rx, ry):
    p = skia.Path()
    p.moveTo(cx, cy - ry)
    p.cubicTo(cx + 0.58 * rx, cy - ry, cx + rx, cy - 0.64 * ry, cx + rx, cy - 0.1 * ry)
    p.cubicTo(cx + rx, cy + 0.32 * ry, cx + 0.86 * rx, cy + 0.62 * ry, cx + 0.55 * rx, cy + 0.84 * ry)
    p.cubicTo(cx + 0.32 * rx, cy + 1.0 * ry, cx - 0.32 * rx, cy + 1.0 * ry, cx - 0.55 * rx, cy + 0.84 * ry)
    p.cubicTo(cx - 0.86 * rx, cy + 0.62 * ry, cx - rx, cy + 0.32 * ry, cx - rx, cy - 0.1 * ry)
    p.cubicTo(cx - rx, cy - 0.64 * ry, cx - 0.58 * rx, cy - ry, cx, cy - ry)
    p.close()
    return p


EXPR2 = {
    'neutral': dict(eye='open', brow=0, lift=0, mouth='line'),
    'happy': dict(eye='happy', brow=-6, lift=-4, mouth='grin', blush=1.0),
    'smile': dict(eye='open', brow=-3, lift=-2, mouth='smile', blush=0.5),
    'grin': dict(eye='happy', brow=-8, lift=-6, mouth='grin', blush=1.0),
    'laugh': dict(eye='happy', brow=-10, lift=-8, mouth='laugh', blush=1.0),
    'bored': dict(eye='lid', brow=2, lift=4, mouth='line'),
    'wow': dict(eye='wide', brow=-12, lift=-12, mouth='o'),
    'dazed': dict(eye='wide', brow=-6, lift=-8, mouth='smirk', blush=0.8),
    'tired': dict(eye='lid', brow=12, lift=2, mouth='flat_down', bags=1.0),
    'exhausted': dict(eye='bloodshot', brow=16, lift=-4, mouth='wobble', bags=1.0, sweat=True),
    'sad': dict(eye='sad', brow=18, lift=-2, mouth='frown', bags=0.6),
    'worried': dict(eye='wide', brow=16, lift=-8, mouth='wobble', bags=0.4),
    'determined': dict(eye='narrow', brow=-18, lift=4, mouth='line'),
    'angry': dict(eye='narrow', brow=-26, lift=8, mouth='teeth', vein=True),
    'rage': dict(eye='blank', brow=-28, lift=8, mouth='shout', shadow_band=True),
    'shout': dict(eye='narrow', brow=-22, lift=4, mouth='shout'),
    'shock': dict(eye='wide', brow=-14, lift=-16, mouth='shout_o'),
    'calm': dict(eye='closed', brow=-3, lift=0, mouth='smile'),
    'asleep': dict(eye='asleep', brow=0, lift=3, mouth='line'),
    'grit': dict(eye='narrow', brow=-24, lift=8, mouth='teeth'),
    'embarrassed': dict(eye='happy', brow=14, lift=-6, mouth='grin', blush=1.4, sweat=True),
    'smug': dict(eye='lid', brow=-8, lift=0, mouth='smirk'),
}


def _brow(c, x, y, side, tilt, s, colr, w):
    """Tapered brow: thick inner end, thin outer end. tilt>0 = inner end raised (sad)."""
    inner = (x - side * 0.0, y)
    t = math.radians(tilt)
    L = 34 * s
    ox, oy = x + side * L * math.cos(t), y + L * math.sin(t) * 1.0
    ix, iy = x - side * 4 * s, y - L * math.sin(t) * 0.3
    p = skia.Path()
    p.moveTo(ix, iy - w * 0.55)
    p.quadTo((ix + ox) / 2, (iy + oy) / 2 - w * 0.9, ox, oy - w * 0.1)
    p.quadTo((ix + ox) / 2, (iy + oy) / 2 + w * 0.15, ix, iy + w * 0.55)
    p.close()
    c.drawPath(p, paint(colr))
    c.drawPath(p, paint(LINE, stroke=w * 0.22))


def draw_face2(c, cx, cy, rx, ry, ch, expr='neutral', look=(0, 0), blink=0.0, bags=None, pupil_glow=None,
               tear=None, sweat=None, extra=None):
    e = dict(EXPR2.get(expr, EXPR2['neutral']))
    if extra:
        e.update({k: v for k, v in extra.items() if k not in ('skin',)})
    s = ry / 54.0
    lx, ly = look
    skin = ch['skin']
    ow = 3.4 * s
    if e.get('shadow_band'):
        band = skia.Path()
        band.addRect(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy - 0.02 * ry))
        c.save(); c.clipPath(head_path(cx, cy, rx, ry), skia.ClipOp.kIntersect, True)
        c.drawPath(band, paint(_skin_shade(skin)))
        c.restore()
    blush = e.get('blush', 0)
    ey = cy + 0.1 * ry + ly * 0.06 * ry
    for side in (-1, 1):
        ex = cx + side * 0.4 * rx + lx * 0.1 * rx
        if blush:
            oval(c, ex + side * 0.08 * rx, ey + 0.27 * ry, 0.2 * rx, 0.08 * ry, '#ff7a7a', a=0.22 * blush)
            for i in range(4):
                bx = ex - 0.12 * rx + i * 0.075 * rx
                c.drawLine(bx, ey + 0.31 * ry, bx + 0.05 * rx, ey + 0.22 * ry, paint('#d9535e', 0.65 * min(1, blush), stroke=1.8 * s))
        b = e.get('bags', 0) if bags is None else bags
        if b:
            arc = skia.Path()
            arc.addArc(skia.Rect.MakeLTRB(ex - 0.16 * rx, ey - 0.02 * ry, ex + 0.16 * rx, ey + 0.2 * ry), 25, 130)
            c.drawPath(arc, paint('#7a4f7e', 0.6 * b, stroke=2.6 * s))
        eye = e['eye']
        ew, eh = 0.185 * rx, 0.118 * ry
        if eye == 'wide':
            ew, eh = 0.19 * rx, 0.15 * ry
        bl = 1 - blink
        if eye in ('happy', 'closed', 'asleep') or bl < 0.15:
            a = skia.Path()
            if eye == 'happy':
                a.moveTo(ex - ew, ey + eh * 0.3); a.quadTo(ex, ey - eh * 1.4, ex + ew, ey + eh * 0.3)
            elif eye == 'asleep':
                a.moveTo(ex - ew, ey); a.quadTo(ex, ey + eh * 1.0, ex + ew, ey)
            else:
                a.moveTo(ex - ew, ey - eh * 0.1); a.quadTo(ex, ey + eh * 0.9, ex + ew, ey - eh * 0.1)
            c.drawPath(a, paint(LINE, stroke=3.6 * s))
            continue
        # almond eye
        top = 1.35 if eye != 'narrow' else 0.75
        bot = 0.95 if eye != 'narrow' else 0.7
        ep = skia.Path()
        ep.moveTo(ex - ew, ey)
        ep.cubicTo(ex - ew * 0.5, ey - eh * top * bl, ex + ew * 0.5, ey - eh * top * bl, ex + ew, ey - eh * 0.05)
        ep.cubicTo(ex + ew * 0.5, ey + eh * bot * bl, ex - ew * 0.5, ey + eh * bot * bl, ex - ew, ey)
        ep.close()
        white = '#ffffff' if eye != 'bloodshot' else '#fff1ee'
        c.drawPath(ep, paint(white))
        c.save()
        c.clipPath(ep, skia.ClipOp.kIntersect, True)
        if eye == 'bloodshot':
            for ang in (200, 230, 320, 345):
                a0 = math.radians(ang)
                c.drawLine(ex + math.cos(a0) * ew, ey + math.sin(a0) * eh, ex + math.cos(a0) * ew * 0.4,
                           ey + math.sin(a0) * eh * 0.4, paint('#e2453c', 0.8, stroke=1.2 * s))
        if eye != 'blank':
            ir = 0.098 * ry if eye not in ('wide', 'bloodshot') else 0.07 * ry
            ix, iy = ex + lx * 0.07 * rx + side * 0.01 * rx, ey + ly * 0.03 * ry + 0.01 * ry
            if pupil_glow:
                c.drawCircle(ix, iy, ir * 1.6, paint(pupil_glow, 0.7, blur=ir * 0.6))
            c.drawCircle(ix, iy, ir, paint(ch.get('eyes', '#3b2416')))
            c.drawCircle(ix, iy, ir * 0.55, paint('#120a08'))
            c.drawCircle(ix + ir * 0.35, iy - ir * 0.4, ir * 0.3, paint('#ffffff'))
            c.drawCircle(ix - ir * 0.35, iy + ir * 0.35, ir * 0.12, paint('#ffffff', 0.8))
        # lid shadow
        c.drawRect(skia.Rect.MakeLTRB(ex - ew, ey - eh * 2, ex + ew, ey - eh * (0.9 if eye != 'sad' else 0.4)),
                   paint(_skin_shade(skin), 0.25))
        if eye in ('lid', 'bloodshot') or eye == 'sad':
            lid = skia.Path()
            drop = 0.15 if eye == 'lid' else (0.55 if eye == 'sad' else 0.6)
            lid.addRect(skia.Rect.MakeLTRB(ex - ew * 1.2, ey - eh * 2, ex + ew * 1.2, ey - eh * drop))
            if eye == 'sad':
                lid = skia.Path()
                lid.moveTo(ex - ew * 1.2, ey - eh * 2); lid.lineTo(ex + ew * 1.2, ey - eh * 2)
                o, i_ = (ex + side * ew * 1.2), (ex - side * ew * 1.2)
                lid.lineTo(ex + ew * 1.2, ey - eh * (0.2 if side == 1 else 1.1))
                lid.lineTo(ex - ew * 1.2, ey - eh * (1.1 if side == 1 else 0.2))
                lid.close()
            c.drawPath(lid, paint(skin))
        c.restore()
        # upper lash line (thick) + flick
        ul = skia.Path()
        ul.moveTo(ex - ew * 1.02, ey + eh * 0.05)
        ul.cubicTo(ex - ew * 0.5, ey - eh * top * bl, ex + ew * 0.5, ey - eh * top * bl, ex + ew * 1.02, ey - eh * 0.05)
        c.drawPath(ul, paint(LINE, stroke=3.8 * s))
        fx = ex + side * ew * 1.02
        c.drawLine(fx, ey - eh * 0.05 * side, fx + side * 0.05 * rx, ey - eh * 0.45, paint(LINE, stroke=2.6 * s))
        if ch.get('female'):
            c.drawLine(fx - side * 0.02 * rx, ey - eh * 0.4, fx + side * 0.04 * rx, ey - eh * 0.95, paint(LINE, stroke=2.0 * s))
        lo = skia.Path()
        lo.moveTo(ex - ew * 0.6, ey + eh * 0.85 * bl)
        lo.quadTo(ex, ey + eh * 1.05 * bl, ex + ew * 0.7, ey + eh * 0.6 * bl)
        c.drawPath(lo, paint(LINE, 0.5, stroke=1.6 * s))
    # brows
    for side in (-1, 1):
        bx = cx + side * 0.27 * rx + lx * 0.1 * rx
        by = ey - 0.27 * ry + e.get('lift', 0) * s * 0.6
        tilt = e.get('brow', 0)
        _brow(c, bx, by, side, tilt * (1 if side == 1 else 1), s, mix(ch['hair'], '#000000', 0.25), 7.0 * s)
    if e.get('vein'):
        vx, vy = cx + 0.55 * rx, cy - 0.55 * ry
        for a in (0, 90, 180, 270):
            r_ = math.radians(a + 45)
            p = skia.Path()
            p.moveTo(vx + math.cos(r_) * 4 * s, vy + math.sin(r_) * 4 * s)
            p.quadTo(vx + math.cos(r_ + 0.6) * 11 * s, vy + math.sin(r_ + 0.6) * 11 * s, vx + math.cos(r_) * 14 * s, vy + math.sin(r_) * 14 * s)
            c.drawPath(p, paint('#e03a3a', stroke=3.2 * s))
    # nose
    nx = cx + lx * 0.12 * rx
    n = skia.Path()
    n.moveTo(nx + 0.03 * rx, cy + 0.26 * ry)
    n.quadTo(nx - 0.07 * rx, cy + 0.44 * ry, nx - 0.02 * rx, cy + 0.47 * ry)
    n.quadTo(nx + 0.04 * rx, cy + 0.49 * ry, nx + 0.08 * rx, cy + 0.45 * ry)
    c.drawPath(n, paint(LINE, 0.85, stroke=2.4 * s))
    oval(c, nx + 0.06 * rx, cy + 0.45 * ry, 0.06 * rx, 0.025 * ry, _skin_shade(skin), a=0.6)
    # mouth
    mx, my = cx + lx * 0.12 * rx, cy + 0.64 * ry
    m = e['mouth']
    lipc = '#c25560' if ch.get('female') else LINE
    if m == 'smile':
        p = skia.Path(); p.moveTo(mx - 0.2 * rx, my - 0.03 * ry); p.quadTo(mx, my + 0.11 * ry, mx + 0.2 * rx, my - 0.03 * ry)
        c.drawPath(p, paint(LINE, stroke=2.8 * s))
    elif m in ('grin', 'laugh'):
        w_, h_ = 0.3 * rx, (0.16 if m == 'grin' else 0.24) * ry
        p = skia.Path()
        p.moveTo(mx - w_, my - 0.05 * ry)
        p.quadTo(mx, my - 0.02 * ry, mx + w_, my - 0.05 * ry)
        p.quadTo(mx + w_ * 0.7, my + h_, mx, my + h_)
        p.quadTo(mx - w_ * 0.7, my + h_, mx - w_, my - 0.05 * ry)
        p.close()
        c.drawPath(p, paint('#7a1f2a' if m == 'laugh' else '#ffffff'))
        c.save(); c.clipPath(p, skia.ClipOp.kIntersect, True)
        if m == 'laugh':
            c.drawRect(skia.Rect.MakeLTRB(mx - w_, my - 0.06 * ry, mx + w_, my + 0.03 * ry), paint('#ffffff'))
            oval(c, mx, my + h_ * 0.95, w_ * 0.5, h_ * 0.4, '#e26a6a')
        else:
            c.drawLine(mx - w_, my + h_ * 0.42, mx + w_, my + h_ * 0.42, paint('#b9b4b8', stroke=1.6 * s))
        c.restore()
        c.drawPath(p, paint(LINE, stroke=2.8 * s))
    elif m in ('o', 'shout_o'):
        rr = 0.07 if m == 'o' else 0.12
        oval(c, mx, my + 0.04 * ry, rr * rx * 1.1, rr * ry * 1.3, '#6a1c26', LINE, ow=2.6 * s)
        if m == 'shout_o':
            oval(c, mx, my + 0.04 * ry + rr * ry * 0.7, rr * rx * 0.6, rr * ry * 0.4, '#d9606a')
    elif m == 'shout':
        w_, h_ = 0.28 * rx, 0.26 * ry
        p = skia.Path()
        p.moveTo(mx - w_, my - 0.02 * ry); p.lineTo(mx + w_, my - 0.04 * ry)
        p.quadTo(mx + w_ * 0.6, my + h_, mx, my + h_); p.quadTo(mx - w_ * 0.6, my + h_, mx - w_, my - 0.02 * ry); p.close()
        c.drawPath(p, paint('#6a1c26'))
        c.save(); c.clipPath(p, skia.ClipOp.kIntersect, True)
        c.drawRect(skia.Rect.MakeLTRB(mx - w_, my - 0.06 * ry, mx + w_, my + 0.04 * ry), paint('#ffffff'))
        oval(c, mx, my + h_ * 0.95, w_ * 0.55, h_ * 0.35, '#e05a64')
        c.restore()
        c.drawPath(p, paint(LINE, stroke=2.8 * s))
    elif m == 'teeth':
        p = skia.Path()
        p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(mx - 0.22 * rx, my - 0.04 * ry, mx + 0.22 * rx, my + 0.07 * ry), 4 * s, 4 * s))
        c.drawPath(p, paint('#ffffff'))
        c.drawLine(mx - 0.22 * rx, my + 0.015 * ry, mx + 0.22 * rx, my + 0.015 * ry, paint(LINE, stroke=1.6 * s))
        for i in range(-2, 3):
            c.drawLine(mx + i * 0.08 * rx, my - 0.04 * ry, mx + i * 0.08 * rx, my + 0.07 * ry, paint(LINE, 0.6, stroke=1.3 * s))
        c.drawPath(p, paint(LINE, stroke=2.6 * s))
    elif m == 'frown':
        p = skia.Path(); p.moveTo(mx - 0.16 * rx, my + 0.06 * ry); p.quadTo(mx, my - 0.05 * ry, mx + 0.16 * rx, my + 0.06 * ry)
        c.drawPath(p, paint(LINE, stroke=2.8 * s))
    elif m == 'wobble':
        p = skia.Path(); p.moveTo(mx - 0.16 * rx, my + 0.02 * ry)
        for i in range(1, 7):
            p.lineTo(mx - 0.16 * rx + i * 0.053 * rx, my + 0.02 * ry + (0.03 * ry if i % 2 else -0.012 * ry))
        c.drawPath(p, paint(LINE, stroke=2.4 * s))
    elif m == 'smirk':
        p = skia.Path(); p.moveTo(mx - 0.14 * rx, my + 0.01 * ry); p.quadTo(mx + 0.04 * rx, my + 0.07 * ry, mx + 0.18 * rx, my - 0.05 * ry)
        c.drawPath(p, paint(LINE, stroke=2.8 * s))
    elif m == 'flat_down':
        p = skia.Path(); p.moveTo(mx - 0.13 * rx, my + 0.03 * ry); p.quadTo(mx, my - 0.01 * ry, mx + 0.13 * rx, my + 0.03 * ry)
        c.drawPath(p, paint(LINE, stroke=2.6 * s))
    else:
        c.drawLine(mx - 0.12 * rx, my, mx + 0.12 * rx, my, paint(LINE, stroke=2.6 * s))
    if ch.get('female') and m in ('line', 'smile', 'frown', 'smirk', 'flat_down'):
        oval(c, mx, my + 0.05 * ry, 0.07 * rx, 0.02 * ry, lipc, a=0.45)
    # tears / sweat
    if tear is not None:
        ty = ey + 0.15 * ry + tear * 0.55 * ry
        a = 1 - clamp01((tear - 0.8) / 0.2)
        tx = cx + 0.45 * rx
        dp = skia.Path()
        dp.moveTo(tx, ty - 0.09 * ry); dp.quadTo(tx + 0.07 * rx, ty + 0.02 * ry, tx, ty + 0.05 * ry)
        dp.quadTo(tx - 0.07 * rx, ty + 0.02 * ry, tx, ty - 0.09 * ry)
        c.drawPath(dp, paint('#8fd0ff', a)); c.drawPath(dp, paint(LINE, a * 0.6, stroke=1.4 * s))
    sw = sweat if sweat is not None else (0.0 if e.get('sweat') else None)
    if sw is not None:
        sx, sy = cx + 0.85 * rx, cy - 0.35 * ry + sw * 0.1 * ry
        dp = skia.Path()
        dp.moveTo(sx, sy - 0.13 * ry); dp.quadTo(sx + 0.09 * rx, sy + 0.03 * ry, sx, sy + 0.07 * ry)
        dp.quadTo(sx - 0.09 * rx, sy + 0.03 * ry, sx, sy - 0.13 * ry)
        c.drawPath(dp, paint('#c4ecff')); c.drawPath(dp, paint(LINE, stroke=1.8 * s))
    if ch.get('glasses'):
        for side in (-1, 1):
            gx = cx + side * 0.4 * rx + lx * 0.1 * rx
            rrect(c, gx - 0.24 * rx, ey - 0.16 * ry, 0.48 * rx, 0.3 * ry, 0.1 * rx, '#ffffff', LINE, ow=3.0 * s, a=0.0)
            c.drawRoundRect(skia.Rect.MakeXYWH(gx - 0.24 * rx, ey - 0.16 * ry, 0.48 * rx, 0.3 * ry), 0.1 * rx, 0.1 * rx,
                            paint(LINE, stroke=3.0 * s))
        c.drawLine(cx - 0.16 * rx, ey - 0.04 * ry, cx + 0.16 * rx, ey - 0.04 * ry, paint(LINE, stroke=2.6 * s))


# ---------------------------------------------------------------- hair

def _spiky_top(cx, cy, rx, ry, n=9, a0=196, a1=344, r_in=1.08, r_out=1.3, seed=0):
    pts = []
    for i in range(n * 2 + 1):
        a = math.radians(a0 + (a1 - a0) * i / (n * 2))
        rr = r_out if i % 2 == 1 else r_in
        jitter = 1 + 0.06 * math.sin(i * 2.3 + seed)
        pts.append((cx + math.cos(a) * rx * rr * jitter, cy - 0.12 * ry + math.sin(a) * ry * rr * jitter))
    return pts


def _fringe(cx, cy, rx, ry, style):
    """Points along the fringe edge from right temple back to left temple."""
    if style in ('spiky', 'messy'):
        return [(1.02, -0.05), (0.85, -0.32), (0.7, -0.18), (0.5, -0.5), (0.3, -0.28), (0.12, -0.56), (-0.1, -0.34),
                (-0.32, -0.6), (-0.52, -0.36), (-0.72, -0.52), (-0.9, -0.2), (-1.02, -0.05)]
    if style == 'short':
        return [(1.02, -0.1), (0.8, -0.42), (0.45, -0.5), (0.2, -0.38), (-0.15, -0.56), (-0.5, -0.5), (-0.85, -0.3), (-1.02, -0.1)]
    return [(1.02, -0.05), (0.75, -0.45), (0.3, -0.62), (0.02, -0.5), (-0.3, -0.62), (-0.75, -0.45), (-1.02, -0.05)]


def hair_front_path(cx, cy, rx, ry, style):
    p = skia.Path()
    if style in ('spiky', 'messy'):
        pts = [(-1.06, -0.05), (-1.28, -0.42), (-1.0, -0.52), (-1.16, -0.92), (-0.74, -0.92), (-0.72, -1.32),
               (-0.34, -1.1), (-0.06, -1.48), (0.2, -1.14), (0.56, -1.4), (0.66, -1.04), (1.16, -1.06), (0.98, -0.64),
               (1.3, -0.44), (1.06, -0.05)]
        if style == 'messy':
            pts = [(a, b * 0.92 + 0.02) for a, b in pts]
        top = [(cx + a * rx, cy + b * ry) for a, b in pts]
    else:
        top = []
        for i in range(25):
            a = math.radians(192 + 156 * i / 24)
            top.append((cx + math.cos(a) * rx * 1.1, cy - 0.08 * ry + math.sin(a) * ry * 1.12))
    p.moveTo(cx - rx * 1.03, cy + 0.05 * ry)
    for q in top:
        p.lineTo(*q)
    p.lineTo(cx + rx * 1.03, cy + 0.05 * ry)
    fr = _fringe(cx, cy, rx, ry, style)
    prev = (cx + rx * 1.03, cy + 0.05 * ry)
    for (fx, fy) in fr:
        pt = (cx + fx * rx, cy + fy * ry)
        p.quadTo((prev[0] + pt[0]) / 2, (prev[1] + pt[1]) / 2 + 0.05 * ry, pt[0], pt[1])
        prev = pt
    p.close()
    return p


def draw_back_hair(c, cx, cy, rx, ry, ch, s):
    st = ch.get('hair_style', 'spiky')
    hc = ch['hair']
    if st == 'long':
        p = skia.Path()
        p.moveTo(cx - rx * 1.08, cy - 0.3 * ry)
        p.cubicTo(cx - rx * 1.3, cy + 0.6 * ry, cx - rx * 1.25, cy + 1.6 * ry, cx - rx * 0.95, cy + 2.0 * ry)
        p.lineTo(cx + rx * 0.95, cy + 2.0 * ry)
        p.cubicTo(cx + rx * 1.25, cy + 1.6 * ry, cx + rx * 1.3, cy + 0.6 * ry, cx + rx * 1.08, cy - 0.3 * ry)
        p.close()
        cel(c, p, _shade(hc, 0.12), 3.6 * s, depth=8 * s)
    if st == 'bun':
        bp = skia.Path()
        bp.addOval(skia.Rect.MakeLTRB(cx - 0.45 * rx, cy - 1.62 * ry, cx + 0.45 * rx, cy - 0.85 * ry))
        cel(c, bp, hc, 3.6 * s, depth=6 * s, hi=0.6)


def draw_hair2(c, cx, cy, rx, ry, ch, t=0):
    s = ry / 54.0
    st = ch.get('hair_style', 'spiky')
    hc = ch['hair']
    ow = 3.6 * s
    if st == 'curly':
        mass = skia.Path()
        mass.addOval(skia.Rect.MakeLTRB(cx - 1.02 * rx, cy - 1.2 * ry, cx + 1.02 * rx, cy - 0.05 * ry))
        for i in range(12):
            a = math.radians(178 + i * 16.5)
            lobe = skia.Path()
            lobe.addCircle(cx + math.cos(a) * rx * 0.96, cy - 0.32 * ry + math.sin(a) * ry * 0.92, 0.27 * rx)
            mass = skia.Op(mass, lobe, skia.PathOp.kUnion_PathOp) or mass
        for i in range(5):  # fringe curls
            lobe = skia.Path()
            lobe.addCircle(cx + (-0.6 + i * 0.3) * rx, cy - 0.42 * ry + (0.05 if i % 2 else 0) * ry, 0.2 * rx)
            mass = skia.Op(mass, lobe, skia.PathOp.kUnion_PathOp) or mass
        cel(c, mass, hc, ow, depth=8 * s)
        c.save(); c.clipPath(mass, skia.ClipOp.kIntersect, True)
        for i in range(7):
            a = math.radians(200 + i * 22)
            arc = skia.Path()
            ax, ay = cx + math.cos(a) * rx * 0.62, cy - 0.55 * ry + math.sin(a) * ry * 0.45
            arc.addArc(skia.Rect.MakeLTRB(ax - 0.14 * rx, ay - 0.12 * ry, ax + 0.14 * rx, ay + 0.12 * ry), 200, 140)
            c.drawPath(arc, paint(_hi(hc, 0.3), 0.9, stroke=2.4 * s))
        c.restore()
        return
    if st in ('cap', 'beanie'):
        # a little hair below the hat
        sides = skia.Path()
        for side in (-1, 1):
            sides.moveTo(cx + side * rx * 1.02, cy - 0.35 * ry)
            sides.lineTo(cx + side * rx * 1.04, cy + 0.15 * ry)
            sides.lineTo(cx + side * rx * 0.82, cy - 0.12 * ry)
            sides.lineTo(cx + side * rx * 0.75, cy - 0.38 * ry)
            sides.close()
        cel(c, sides, hc, ow, depth=4 * s)
        hat = ch.get('cap', '#2f6fd6') if st == 'cap' else hc
        dome = skia.Path()
        dome.arcTo(skia.Rect.MakeLTRB(cx - rx * 1.1, cy - ry * 1.22, cx + rx * 1.1, cy + ry * 0.5), 180, 180, True)
        dome.close()
        cel(c, dome, hat, ow, depth=10 * s, hi=0.5)
        if st == 'cap':
            brim = skia.Path()
            brim.moveTo(cx - rx * 0.95, cy - 0.32 * ry)
            brim.quadTo(cx, cy - 0.12 * ry, cx + rx * 1.55, cy - 0.3 * ry)
            brim.quadTo(cx + rx * 1.4, cy - 0.48 * ry, cx + rx * 0.95, cy - 0.42 * ry)
            brim.close()
            cel(c, brim, _shade(hat, 0.12), ow, depth=5 * s)
            c.drawLine(cx, cy - 1.2 * ry, cx, cy - 0.4 * ry, paint(_shade(hat, 0.3), stroke=2 * s))
            circle(c, cx, cy - 1.2 * ry, 0.06 * rx, _shade(hat, 0.2), LINE, ow=2 * s)
        else:
            band = skia.Path()
            band.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(cx - rx * 1.14, cy - 0.5 * ry, cx + rx * 1.14, cy - 0.2 * ry), 10 * s, 10 * s))
            cel(c, band, _shade(hat, 0.15), ow, depth=4 * s)
            for i in range(-5, 6):
                c.drawLine(cx + i * rx * 0.19, cy - 0.47 * ry, cx + i * rx * 0.19, cy - 0.24 * ry, paint(_shade(hat, 0.35), stroke=2 * s))
            pp = skia.Path(); pp.addCircle(cx, cy - 1.25 * ry, 0.2 * rx)
            cel(c, pp, _hi(hat, 0.2), ow, depth=3 * s)
        return
    p = hair_front_path(cx, cy, rx, ry, 'spiky' if st == 'messy' else st)
    cel(c, p, hc, ow, depth=9 * s)
    # glossy highlight streak
    hl = skia.Path()
    hl.moveTo(cx - rx * 0.62, cy - 0.74 * ry)
    hl.quadTo(cx - rx * 0.15, cy - 1.02 * ry, cx + rx * 0.4, cy - 0.86 * ry)
    hl.quadTo(cx - rx * 0.1, cy - 0.9 * ry, cx - rx * 0.62, cy - 0.66 * ry)
    hl.close()
    c.save(); c.clipPath(p, skia.ClipOp.kIntersect, True)
    c.drawPath(hl, paint(_hi(hc, 0.32), 0.9))
    c.restore()
    # a few strand lines
    for (a, b, q) in (((-0.3, -0.95), (-0.1, -0.55), (-0.15, -0.8)), ((0.25, -0.98), (0.35, -0.6), (0.38, -0.82))):
        sp = skia.Path()
        sp.moveTo(cx + a[0] * rx, cy + a[1] * ry)
        sp.quadTo(cx + q[0] * rx, cy + q[1] * ry, cx + b[0] * rx, cy + b[1] * ry)
        c.drawPath(sp, paint(LINE, 0.55, stroke=1.8 * s))


def draw_head2(c, cx, cy, ry, ch, expr='neutral', t=0, look=(0, 0), blink=0.0, neck=True, back=True, **kw):
    s = ry / 54.0
    rx = ry * 0.84
    skin = ch['skin']
    ow = 3.8 * s
    if back:
        draw_back_hair(c, cx, cy, rx, ry, ch, s)
    if neck:
        n = skia.Path()
        n.addRect(skia.Rect.MakeLTRB(cx - 0.36 * rx, cy + 0.6 * ry, cx + 0.36 * rx, cy + 1.32 * ry))
        c.drawPath(n, paint(_skin_shade(skin)))
        c.drawLine(cx - 0.36 * rx, cy + 0.6 * ry, cx - 0.36 * rx, cy + 1.3 * ry, paint(LINE, stroke=ow * 0.85))
        c.drawLine(cx + 0.36 * rx, cy + 0.6 * ry, cx + 0.36 * rx, cy + 1.3 * ry, paint(LINE, stroke=ow * 0.85))
    for side in (-1, 1):
        ep = skia.Path()
        ep.addOval(skia.Rect.MakeLTRB(cx + side * 0.97 * rx - 0.16 * rx, cy - 0.12 * ry, cx + side * 0.97 * rx + 0.16 * rx, cy + 0.3 * ry))
        cel(c, ep, skin, ow * 0.9, depth=3 * s, shade_col=_skin_shade(skin))
        c.drawLine(cx + side * 0.96 * rx, cy - 0.02 * ry, cx + side * 1.0 * rx, cy + 0.16 * ry, paint(LINE, 0.6, stroke=1.6 * s))
        if ch.get('earrings'):
            circle(c, cx + side * 0.97 * rx, cy + 0.36 * ry, 0.05 * rx, '#ffd36a', LINE, ow=1.6 * s)
    hp = head_path(cx, cy, rx, ry)
    cel(c, hp, skin, ow, depth=8 * s, shade_col=_skin_shade(skin))
    # hair shadow on the forehead
    st = ch.get('hair_style', 'spiky')
    if st not in ('curly', 'cap', 'beanie'):
        fp = hair_front_path(cx, cy, rx, ry, 'spiky' if st == 'messy' else st)
        c.save(); c.clipPath(hp, skia.ClipOp.kIntersect, True)
        c.drawPath(_offset(fp, 0.04 * rx, 0.09 * ry), paint(_skin_shade(skin), 0.9))
        c.restore()
    elif st in ('cap', 'beanie'):
        c.save(); c.clipPath(hp, skia.ClipOp.kIntersect, True)
        c.drawRect(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy - 0.24 * ry), paint(_skin_shade(skin), 0.9))
        c.restore()
    face_kw = {k: v for k, v in kw.items() if k in ('bags', 'pupil_glow', 'tear', 'sweat', 'extra')}
    draw_face2(c, cx, cy, rx, ry, ch, expr, look=look, blink=blink, **face_kw)
    draw_hair2(c, cx, cy, rx, ry, ch, t)


# ---------------------------------------------------------------- body

def _torso_path(x, y_sh, y_hem, s, wide=1.0):
    w_sh, w_ws, w_hm = 62 * s * wide, 50 * s * wide, 55 * s * wide
    p = skia.Path()
    p.moveTo(x - w_sh + 10 * s, y_sh - 8 * s)
    p.quadTo(x, y_sh - 16 * s, x + w_sh - 10 * s, y_sh - 8 * s)
    p.quadTo(x + w_sh + 2 * s, y_sh - 4 * s, x + w_sh, y_sh + 22 * s)
    p.cubicTo(x + w_sh - 6 * s, (y_sh + y_hem) / 2, x + w_ws, y_hem - 30 * s, x + w_hm, y_hem)
    p.quadTo(x, y_hem + 8 * s, x - w_hm, y_hem)
    p.cubicTo(x - w_ws, y_hem - 30 * s, x - w_sh + 6 * s, (y_sh + y_hem) / 2, x - w_sh, y_sh + 22 * s)
    p.quadTo(x - w_sh - 2 * s, y_sh - 4 * s, x - w_sh + 10 * s, y_sh - 8 * s)
    p.close()
    return p


def _draw_top(c, x, y_sh, y_hem, s, ch, ow):
    top = ch.get('top', 'tshirt')
    base = ch.get('hoodie', '#e3a33e')
    tp = _torso_path(x, y_sh, y_hem, s)
    cel(c, tp, base, ow, depth=14 * s)
    # folds
    for (a, b, q) in (((-34, 60), (8, 92), (-10, 84)), ((22, 40), (42, 70), (36, 52)), ((-40, 100), (-10, 112), (-28, 110))):
        f = skia.Path()
        f.moveTo(x + a[0] * s, y_sh + a[1] * s)
        f.quadTo(x + q[0] * s, y_sh + q[1] * s, x + b[0] * s, y_sh + b[1] * s)
        c.drawPath(f, paint(_shade(base, 0.35), 0.8, stroke=2.2 * s))
    if top == 'shirt':
        c.drawLine(x, y_sh - 2 * s, x, y_hem, paint(_shade(base, 0.3), stroke=2.4 * s))
        for i in range(4):
            circle(c, x + 5 * s, y_sh + 22 * s + i * 30 * s, 2.6 * s, '#f6f3ee', LINE, ow=1.2 * s)
        pk = skia.Path(); pk.addRect(skia.Rect.MakeXYWH(x - 44 * s, y_sh + 26 * s, 26 * s, 24 * s))
        c.drawPath(pk, paint(LINE, 0.8, stroke=2.0 * s))
        for side in (-1, 1):
            cp = skia.Path()
            cp.moveTo(x, y_sh + 10 * s); cp.lineTo(x + side * 26 * s, y_sh - 12 * s); cp.lineTo(x + side * 6 * s, y_sh - 14 * s)
            cp.close()
            cel(c, cp, _hi(base, 0.15), ow * 0.9, depth=3 * s)
    elif top == 'hoodie':
        hood = skia.Path()
        hood.moveTo(x - 46 * s, y_sh - 6 * s)
        hood.quadTo(x, y_sh + 22 * s, x + 46 * s, y_sh - 6 * s)
        hood.quadTo(x, y_sh - 2 * s, x - 46 * s, y_sh - 6 * s)
        cel(c, hood, _shade(base, 0.1), ow * 0.9, depth=4 * s)
        for sd in (-1, 1):
            c.drawLine(x + sd * 12 * s, y_sh + 8 * s, x + sd * 14 * s, y_sh + 52 * s, paint('#f4ecdf', stroke=3.2 * s))
            circle(c, x + sd * 14 * s, y_sh + 54 * s, 3.4 * s, '#f4ecdf', LINE, ow=1.4 * s)
        pk = skia.Path()
        pk.moveTo(x - 40 * s, y_hem - 8 * s); pk.lineTo(x - 30 * s, y_hem - 46 * s)
        pk.lineTo(x + 30 * s, y_hem - 46 * s); pk.lineTo(x + 40 * s, y_hem - 8 * s)
        c.drawPath(pk, paint(_shade(base, 0.38), stroke=2.4 * s))
    else:  # tshirt crew neck
        nk = skia.Path()
        nk.moveTo(x - 26 * s, y_sh - 12 * s)
        nk.quadTo(x, y_sh + 14 * s, x + 26 * s, y_sh - 12 * s)
        c.drawPath(nk, paint(_shade(base, 0.25), stroke=5 * s))
        c.drawPath(nk, paint(LINE, stroke=2.4 * s))
    if ch.get('stain'):
        st = skia.Path()
        sx, sy = x + 16 * s, y_sh + 60 * s
        for i in range(14):
            a_ = i / 14 * math.tau
            rr = (24 + 7 * math.sin(i * 2.7) + 5 * math.cos(i * 4.1)) * s
            (st.moveTo if i == 0 else st.lineTo)(sx + math.cos(a_) * rr, sy + math.sin(a_) * rr * 0.85)
        st.close()
        c.drawPath(st, paint('#6a3e1e', 0.85))
        circle(c, sx + 32 * s, sy + 28 * s, 6 * s, '#6a3e1e', None, a=0.85)


def _sneaker(c, fx, fy, s, side, ch, ow):
    sh = skia.Path()
    sh.moveTo(fx - 18 * s + side * 4 * s, fy + 10 * s)
    sh.quadTo(fx - 22 * s + side * 4 * s, fy - 10 * s, fx - 4 * s + side * 4 * s, fy - 12 * s)
    sh.quadTo(fx + 18 * s + side * 8 * s, fy - 10 * s, fx + 24 * s + side * 8 * s, fy + 6 * s)
    sh.quadTo(fx + 24 * s + side * 8 * s, fy + 12 * s, fx + 16 * s + side * 8 * s, fy + 12 * s)
    sh.lineTo(fx - 14 * s + side * 4 * s, fy + 12 * s)
    sh.close()
    cel(c, sh, ch.get('shoe', '#efe9e0'), ow, depth=4 * s)
    c.drawLine(fx - 18 * s + side * 4 * s, fy + 5 * s, fx + 24 * s + side * 8 * s, fy + 5 * s, paint(LINE, stroke=2.2 * s))
    for i in range(2):
        c.drawLine(fx - 6 * s + side * 4 * s + i * 7 * s, fy - 8 * s, fx - 2 * s + side * 4 * s + i * 7 * s, fy - 3 * s,
                   paint(LINE, 0.6, stroke=1.6 * s))


def draw_legs(c, x, hip_y, legs_pts, s, ch, ow, bottom='pants'):
    """legs_pts: [(hip, knee, ankle) left, (hip, knee, ankle) right]. Pants drawn as one garment."""
    pc = ch.get('pants', '#33405e')
    skin = ch['skin']
    for side, (hp, kn, an) in zip((-1, 1), legs_pts):
        _sneaker(c, an[0], an[1], s, side, ch, ow)
    if bottom == 'shorts':
        for side, (hp, kn, an) in zip((-1, 1), legs_pts):
            limb2(c, [kn, an], [24 * s, 19 * s], skin, ow, depth=4 * s, shade_col=_skin_shade(skin))
    garment = skia.Path()
    garment.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x - 56 * s, hip_y - 14 * s, x + 56 * s, hip_y + 34 * s), 12 * s, 12 * s))
    for side, (hp, kn, an) in zip((-1, 1), legs_pts):
        if bottom == 'shorts':
            mid = (lerp(hp[0], kn[0], 0.9), lerp(hp[1], kn[1], 0.9))
            lp = taper_path([hp, mid], [50 * s, 44 * s])
        else:
            lp = taper_path([hp, kn, (an[0], an[1] - 8 * s)], [46 * s, 36 * s, 32 * s])
        garment = skia.Op(garment, lp, skia.PathOp.kUnion_PathOp) or garment
    cel(c, garment, pc, ow, depth=10 * s)
    # crotch + knee folds + waistband
    c.drawLine(x, hip_y + 6 * s, x, hip_y + 34 * s, paint(LINE, 0.7, stroke=2 * s))
    c.drawLine(x - 54 * s, hip_y - 4 * s, x + 54 * s, hip_y - 4 * s, paint(_shade(pc, 0.35), stroke=3 * s))
    if bottom != 'shorts':
        for side, (hp, kn, an) in zip((-1, 1), legs_pts):
            c.drawLine(kn[0] - 10 * s, kn[1] - 4 * s, kn[0] + 4 * s, kn[1] + 4 * s, paint(_shade(pc, 0.4), stroke=2 * s))


def draw_person(c, x, y, s=1.0, ch=None, expr='neutral', t=0.0, pose='stand', arms=None, legs=None,
                look=(0, 0), blink=0.0, head_tilt=0.0, bob=0.0, prop=None, prop_t=0.0, face_kw=None,
                hand_items=None, shadow=True, hands_kind='open', prop_fn=None):
    """Feet anchored at (x, y). Returns anchors: head, hr, hands, hip, shoulders."""
    from .draw import KID
    ch = ch or KID
    s = s * ch.get('height', 1.0)
    face_kw = face_kw or {}
    y = y + bob * s
    ow = 4.2 * s
    sitting = pose == 'sit'
    bottom = ch.get('bottom', 'pants')
    if shadow:
        oval(c, x, y + 4 * s, 78 * s, 13 * s, '#000000', a=0.18)
    if sitting:
        hip_y = y - 128 * s
        y_sh = hip_y - 128 * s
    else:
        hip_y = y - 212 * s
        y_sh = hip_y - 118 * s
    # legs
    if legs is None:
        legs = ((0, 0), (0, 0))
    lp = []
    for side, (a1, a2) in zip((-1, 1), legs):
        hx0 = x + side * 26 * s
        if sitting:
            lp.append(((hx0, hip_y + 4 * s), (hx0 + side * 8 * s, hip_y + 30 * s), (hx0 + side * 8 * s, y - 16 * s)))
        else:
            pts = arm_pts(hx0, hip_y + 4 * s, a1, a2, s, 98, 92)
            lp.append(tuple(pts))
    draw_legs(c, x, hip_y, lp, s, ch, ow, bottom)
    head_c = (x + head_tilt * 0.5 * s, y_sh - 76 * s)
    draw_back_hair(c, head_c[0], head_c[1], 54 * s * 0.84, 54 * s, ch, s)
    # torso
    hem = hip_y + 8 * s
    if prop == 'guitar':
        pass
    _draw_top(c, x, y_sh, hem, s, ch, ow)
    if bottom != 'shorts' or True:
        belt = skia.Path()
        belt.addRect(skia.Rect.MakeLTRB(x - 52 * s, hem - 4 * s, x + 52 * s, hem + 4 * s))
    head_c = (x + head_tilt * 0.5 * s, y_sh - 76 * s)
    hr = 54 * s
    if prop == 'guitar':
        draw_guitar(c, x + 10 * s, hip_y - 30 * s, s * 1.15, -28)
    # arms
    if arms is None:
        arms = ((10, 4), (-10, -4))
    hands = []
    hand_geo = []
    sleeve_len = {'hoodie': 1.0, 'shirt': 0.5, 'tshirt': 0.45}.get(ch.get('top', 'tshirt'), 0.45)
    base = ch.get('hoodie', '#e3a33e')
    for side, (a1, a2) in zip((-1, 1), arms):
        sh_pt = (x + side * 56 * s, y_sh + 10 * s)
        pts = arm_pts(sh_pt[0], sh_pt[1], a1, a2, s)
        (sx, sy), (ex, ey), (wx, wy) = pts
        if sleeve_len >= 1.0:
            limb2(c, pts, [34 * s, 28 * s, 24 * s], base, ow, depth=7 * s)
            cuff = (lerp(ex, wx, 0.84), lerp(ey, wy, 0.84))
            limb2(c, [cuff, (wx, wy)], [25 * s, 25 * s], _shade(base, 0.12), ow * 0.9, depth=3 * s)
        else:
            limb2(c, pts, [24 * s, 21 * s, 17 * s], ch['skin'], ow, depth=5 * s, shade_col=_skin_shade(ch['skin']))
            u = sleeve_len + 0.2
            se = (lerp(sx, ex, u), lerp(sy, ey, u))
            dx, dy = se[0] - sx, se[1] - sy
            L = math.hypot(dx, dy) or 1
            nx, ny = -dy / L, dx / L
            w1 = 23 * s
            e1 = (se[0] + nx * w1, se[1] + ny * w1)
            e2 = (se[0] - nx * w1, se[1] - ny * w1)
            outer, inner = (e1, e2) if side * (e1[0] - e2[0]) > 0 else (e2, e1)
            sl = skia.Path()
            sl.moveTo(x + side * 34 * s, y_sh - 12 * s)                    # collar side of the shoulder seam
            sl.quadTo(x + side * 58 * s, y_sh - 12 * s, sx + side * 10 * s, sy - 4 * s)   # shoulder curve
            sl.lineTo(*outer)
            sl.quadTo(se[0] + dx / L * 5 * s, se[1] + dy / L * 5 * s, *inner)            # slightly curved hem
            sl.lineTo(x + side * 46 * s, y_sh + 44 * s)                    # armpit
            sl.close()
            cel(c, sl, base, ow, depth=8 * s)
            hm = skia.Path()
            hm.moveTo(lerp(outer[0], se[0], 0.2) - dx / L * 7 * s, lerp(outer[1], se[1], 0.2) - dy / L * 7 * s)
            hm.lineTo(lerp(inner[0], se[0], 0.2) - dx / L * 7 * s, lerp(inner[1], se[1], 0.2) - dy / L * 7 * s)
            c.drawPath(hm, paint(_shade(base, 0.35), stroke=2 * s))
        ang = math.atan2(wx - ex, wy - ey)
        draw_hand(c, wx, wy, ang, s, ch['skin'], side, hands_kind, ow * 0.9)
        hands.append((wx + math.sin(ang) * 16 * s, wy + math.cos(ang) * 16 * s))
        hand_geo.append((wx, wy, ang, side))
    if hand_items:
        for fn in hand_items:
            fn(c, hands)
    if prop_fn:
        prop_fn(c, hands)
        for (wx, wy, ang, side) in hand_geo:      # fingers wrap over the held object
            draw_hand(c, wx, wy, ang, s, ch['skin'], side, 'fist' if hands_kind == 'fist' else 'open', ow * 0.9)
    c.save()
    c.rotate(head_tilt, head_c[0], head_c[1] + hr)
    fk = dict(face_kw)
    draw_head2(c, head_c[0], head_c[1], hr, ch, expr, t, look=look, blink=blink, back=False, **fk)
    c.restore()
    return dict(head=head_c, hr=hr, hands=hands, hip=(x, hip_y), shoulders=y_sh)


def draw_head(c, hx, hy, r, ch, expr='neutral', t=0, **kw):
    """Head-only drawing (beds, avatars). r ≈ old circle radius."""
    draw_head2(c, hx, hy + r * 0.05, r * 0.95, ch, expr, t, neck=kw.pop('neck', False), **kw)


def draw_hair(c, hx, hy, r, ch, t=0):
    draw_hair2(c, hx, hy, r * 0.84, r, ch, t)
