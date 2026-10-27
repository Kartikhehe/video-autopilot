"""Thumbnails from the story's cast: 'face' (one big emotion + glowing device + habit) and 'split' (life vs. habit)."""
from .draw import *
from . import library as L


def exhausted_face(c, hx, hy, r, look=(1, 0.35), glow_col='#ff9a4d'):
    lx, ly = look
    for s in (-1, 1):
        ex, ey = hx + s * r * 0.36, hy + r * 0.04
        for k, a in ((0, 0.9), (1, 0.45)):
            arc = skia.Path()
            arc.addArc(skia.Rect.MakeLTRB(ex - r * 0.2, ey - r * 0.02 + k * r * 0.06, ex + r * 0.2, ey + r * 0.3 + k * r * 0.06), 25, 130)
            c.drawPath(arc, paint('#6e3f73', a, stroke=r * 0.045))
        oval(c, ex, ey, r * 0.2, r * 0.215, '#ff7b6e', a=0.6)
        oval(c, ex, ey, r * 0.165, r * 0.18, '#fffaf2', INK, ow=r * 0.03)
        for ang in (200, 230, 320, 345, 150):
            a0 = math.radians(ang)
            c.drawLine(ex + math.cos(a0) * r * 0.16, ey + math.sin(a0) * r * 0.17,
                       ex + math.cos(a0 + 0.15) * r * 0.09, ey + math.sin(a0 + 0.15) * r * 0.1, paint('#e2453c', 0.8, stroke=r * 0.012))
        px, py = ex + lx * r * 0.07, ey + ly * r * 0.06
        glow(c, px, py, r * 0.09, glow_col, 0.7)
        circle(c, px, py, r * 0.045, INK, None)
        circle(c, px + r * 0.015, py - r * 0.015, r * 0.014, '#ffffff', None)
        bx, by = ex, ey - r * 0.3
        c.drawLine(bx - s * r * 0.15, by - r * 0.08, bx + s * r * 0.13, by + r * 0.03, paint(INK, stroke=r * 0.055))
    mp = skia.Path()
    mx, my = hx + lx * r * 0.06, hy + r * 0.5
    mp.moveTo(mx - r * 0.12, my + r * 0.05)
    mp.quadTo(mx, my - r * 0.07, mx + r * 0.12, my + r * 0.05)
    mp.quadTo(mx, my, mx - r * 0.12, my + r * 0.05)
    c.drawPath(mp, paint('#5a2a2a'))
    c.drawPath(mp, paint(INK, stroke=r * 0.03))
    for (sx, sy, sz) in ((0.82, -0.38, 1.0), (-0.86, -0.1, 0.7)):
        dx, dy, rr = hx + sx * r, hy + sy * r, r * 0.11 * sz
        dp = skia.Path()
        dp.moveTo(dx, dy - rr * 1.3); dp.quadTo(dx + rr, dy + rr * 0.2, dx, dy + rr * 0.8); dp.quadTo(dx - rr, dy + rr * 0.2, dx, dy - rr * 1.3)
        c.drawPath(dp, paint('#bfe6ff')); c.drawPath(dp, paint(INK, stroke=r * 0.02))


def title(c, words, highlight, y, size, hl_col):
    f = font(TF_BOLD, size)
    gap = size * 0.25
    widths = [f.measureText(w) for w in words]
    total = sum(widths) + gap * (len(words) - 1)
    if total > W - 120:
        size = size * (W - 120) / total
        return title(c, words, highlight, y, size, hl_col)
    x = W / 2 - total / 2
    for i, (w, wd) in enumerate(zip(words, widths)):
        c.drawString(w, x + 8, y + 12, f, paint('#000000', 0.75, blur=10))
        c.drawString(w, x, y, f, paint('#000000', stroke=size * 0.17))
        c.drawString(w, x, y, f, paint(hl_col if i == highlight else '#ffffff'))
        x += wd + gap


def _device(c, x, y, s, device, scr=('#ffd08a', '#ff5a5f'), glow_col='#ff8a3d'):
    c.save(); c.translate(x, y); c.rotate(-12)
    glow(c, 0, 0, 600 * s, glow_col, 0.6)
    if device == 'laptop':
        c.rotate(12)
        draw_laptop(c, 0, 160 * s, 1.6 * s, scr[1], 1.0, 'feed')
    else:
        rrect(c, -110 * s, -200 * s, 220 * s, 400 * s, 32 * s, '#0f0f13', '#000000', ow=10 * s)
        c.drawRoundRect(skia.Rect.MakeXYWH(-92 * s, -180 * s, 184 * s, 360 * s), 20 * s, 20 * s,
                        paint(shader=lin_grad((0, -180 * s), (0, 180 * s), list(scr))))
    c.restore()


def make(S, path, variant='face'):
    th = S['spec'].get('thumbnail', {})
    hero = S['hero']
    words = th.get('words', ['WHAT', 'IT', 'TAKES.'])
    hl = th.get('highlight', 1)
    hl_col = th.get('highlight_color', '#ff3d6e')
    device = th.get('device', 'phone')
    gcol = th.get('glow', '#ff8a3d')
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    if variant == 'split':
        left = skia.Path()
        left.moveTo(0, 0); left.lineTo(1010, 0); left.lineTo(910, H); left.lineTo(0, H); left.close()
        c.save(); c.clipPath(left, True)
        c.save(); c.translate(-330, -200); c.scale(1.35, 1.35)
        sl = th.get('split_left', {})
        L.draw_place(c, 1.0, sl.get('place', 'rooftop'), sl.get('sky', 'sunset'), {})
        L.person_activity(c, 760, 900, 0.3, hero, sl.get('activity', 'guitar'), 'happy', (0, 0), s=1.15)
        c.restore(); c.restore()
        right = skia.Path()
        right.moveTo(1010, 0); right.lineTo(W, 0); right.lineTo(W, H); right.lineTo(910, H); right.close()
        c.save(); c.clipPath(right, True)
        c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=lin_grad((0, 0), (0, H), ['#06070d', '#141a30'])))
        draw_urge(c, 1580, 860, 330, 2.0, eye=1.0, look=(-0.8, 0.5), mouth=1.0)
        rrect(c, 980, 820, 700, 200, 100, '#7d8099', '#9a9db6', ow=10)
        hx, hy, r = 1250, 700, 210
        circle(c, hx, hy, r, hero['skin'], ow=11)
        exhausted_face(c, hx, hy, r, (0.6, 0.6), gcol)
        draw_hair(c, hx, hy, r, hero, 0.5)
        bl = skia.Path()
        bl.moveTo(900, H + 50); bl.lineTo(900, 960); bl.cubicTo(1200, 900, 1500, 940, W + 50, 960); bl.lineTo(W + 50, H + 50); bl.close()
        c.drawPath(bl, paint('#26315c')); c.drawPath(bl, paint('#46578f', stroke=10))
        _device(c, 1460, 900, 0.72, device, (mix(gcol, '#ffffff', 0.55), gcol), gcol)
        lp_ = paint(shader=rad_grad((1400, 860), 520, [(gcol, 0.45), (gcol, 0.0)]))
        lp_.setBlendMode(skia.BlendMode.kScreen)
        c.drawRect(skia.Rect.MakeWH(W, H), lp_)
        c.restore()
        c.drawLine(1010, 0, 910, H, paint('#000000', stroke=34))
        c.drawLine(1010, 0, 910, H, paint('#ffffff', stroke=16))
        post(c, 0, vignette=0.4, grain=0.03)
        title(c, words, hl, 200, 180, hl_col)
    else:
        c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=lin_grad((0, 0), (0, H), ['#06070d', '#121628'])))
        draw_urge(c, 1450, 1080, 430, 2.0, eye=1.0, look=(-0.6, 0.6), mouth=1.0)
        rrect(c, 150, 760, 1050, 260, 130, '#7d8099', '#9a9db6', ow=10)
        hx, hy, r = 680, 610, 300
        circle(c, hx, hy, r, hero['skin'], ow=14)
        exhausted_face(c, hx, hy, r, (1, 0.35), gcol)
        draw_hair(c, hx, hy, r, hero, 0.5)
        bl = skia.Path()
        bl.moveTo(-50, H + 50); bl.lineTo(-50, 930); bl.cubicTo(400, 860, 800, 900, 1100, 950)
        bl.cubicTo(1400, 1000, 1700, 960, W + 50, 990); bl.lineTo(W + 50, H + 50); bl.close()
        c.drawPath(bl, paint('#26315c')); c.drawPath(bl, paint('#46578f', stroke=10))
        _device(c, 1120, 770, 1.0, device, (mix(gcol, '#ffffff', 0.55), gcol), gcol)
        if device != 'laptop':
            for (x2, y2) in ((1010, 880), (1245, 830)):
                circle(c, x2, y2, 58, hero['skin'], ow=11)
        lp_ = paint(shader=rad_grad((1000, 760), 720, [(gcol, 0.5), (gcol, 0.0)]))
        lp_.setBlendMode(skia.BlendMode.kScreen)
        c.drawRect(skia.Rect.MakeWH(W, H), lp_)
        post(c, 0, vignette=0.45, grain=0.03)
        title(c, words, hl, 215, 190, hl_col)
    img = surf.makeImageSnapshot()
    for (w, h, p) in ((1280, 720, path), (320, 180, path.replace('.png', '_small.png'))):
        s2 = skia.Surface(w, h)
        s2.getCanvas().drawImageRect(img, skia.Rect.MakeWH(w, h), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
        s2.makeImageSnapshot().save(p, skia.kPNG)
