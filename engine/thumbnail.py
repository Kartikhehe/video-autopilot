"""Thumbnails from the story's cast: 'face' (one big emotion + glowing device + habit) and 'split' (life vs. habit)."""
from .draw import *
import random
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
    if variant == 'scene':
        return make_scene(S, path, W, H)
    if variant == 'hero':
        return make_hero(S, path, W, H)
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


def make_vertical(S, path):
    """1080x1920 cover for Shorts: huge stacked words, exhausted face, glowing device, looming habit."""
    th = S['spec'].get('thumbnail', {})
    if th.get('layout') == 'scene':
        return make_scene(S, path, 1080, 1920)
    hero = S['hero']
    words = th.get('words', ['WHAT', 'IT', 'TAKES.'])
    hl = th.get('highlight', len(words) - 1)
    hl_col = th.get('highlight_color', URGE['say'])
    gcol = th.get('glow', URGE['glow'])
    OW, OH = 1080, 1920
    surf = skia.Surface(OW, OH)
    c = surf.getCanvas()
    c.drawRect(skia.Rect.MakeWH(OW, OH), paint(shader=lin_grad((0, 0), (0, OH), ['#05060b', '#101426', '#141a30'])))
    draw_urge(c, 760, 1430, 430, 2.0, eye=1.0, look=(-0.7, 0.5), mouth=1.0)
    rrect(c, -80, 1290, 900, 260, 130, '#7d8099', '#9a9db6', ow=10)
    hx, hy, r = 430, 1130, 290
    circle(c, hx, hy, r, hero['skin'], ow=14)
    exhausted_face(c, hx, hy, r, (1, 0.35), gcol)
    draw_hair(c, hx, hy, r, hero, 0.5)
    bl = skia.Path()
    bl.moveTo(-50, OH + 50); bl.lineTo(-50, 1450); bl.cubicTo(300, 1390, 650, 1430, 900, 1480)
    bl.cubicTo(1000, 1500, 1060, 1490, OW + 50, 1500); bl.lineTo(OW + 50, OH + 50); bl.close()
    c.drawPath(bl, paint('#26315c')); c.drawPath(bl, paint('#46578f', stroke=10))
    if th.get('device', 'phone') != 'none':
        _device(c, 820, 1330, 0.95, th.get('device', 'phone'), (mix(gcol, '#ffffff', 0.55), gcol), gcol)
    if th.get('device', 'phone') not in ('laptop', 'none'):
        for (x2, y2) in ((715, 1440), (935, 1390)):
            circle(c, x2, y2, 55, hero['skin'], ow=11)
    lp_ = paint(shader=rad_grad((760, 1300), 700, [(gcol, 0.5), (gcol, 0.0)]))
    lp_.setBlendMode(skia.BlendMode.kScreen)
    c.drawRect(skia.Rect.MakeWH(OW, OH), lp_)
    if th.get('badge'):
        bw = measure(th['badge'], 64, TF_BOLD) + 70
        c.save(); c.rotate(-6, 250, 760)
        rrect(c, 250 - bw / 2, 712, bw, 100, 22, '#111116', '#ff3b30', ow=6)
        text(c, th['badge'], 250, 787, 64, '#ff4136', tf=TF_BOLD, shadow=False, glow_col='#ff3b30')
        c.restore()
    vp = paint(shader=rad_grad((OW / 2, OH / 2), OH * 0.62, [('#000000', 0), ('#000000', 0), ('#000000', 0.45)], [0, 0.6, 1]))
    c.drawRect(skia.Rect.MakeWH(OW, OH), vp)
    # stacked title, auto-sized to the width
    size = 175
    f = font(TF_BOLD, size)
    lines, cur = [], []
    for i, w in enumerate(words):
        test = ' '.join(x for x, _ in cur + [(w, i)])
        if cur and f.measureText(test) > OW - 110:
            lines.append(cur)
            cur = []
        cur.append((w, i))
    lines.append(cur)
    widest = max(f.measureText(' '.join(w for w, _ in ln)) for ln in lines)
    if widest > OW - 110:
        size *= (OW - 110) / widest
        f = font(TF_BOLD, size)
    y = 300
    for ln in lines:
        lw = f.measureText(' '.join(w for w, _ in ln))
        x = OW / 2 - lw / 2
        for w, i in ln:
            c.drawString(w, x + 8, y + 12, f, paint('#000000', 0.75, blur=10))
            c.drawString(w, x, y, f, paint('#000000', stroke=size * 0.17))
            c.drawString(w, x, y, f, paint(hl_col if i == hl else '#ffffff'))
            x += f.measureText(w + ' ')
        y += size * 1.05
    img = surf.makeImageSnapshot()
    img.save(path, skia.kPNG)
    s2 = skia.Surface(270, 480)
    s2.getCanvas().drawImageRect(img, skia.Rect.MakeWH(270, 480), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    s2.makeImageSnapshot().save(path.replace('.png', '_small.png'), skia.kPNG)


def _stack(c, words, hl, y, size, hl_col, colors=None, strike=(), max_w=980, cx=540):
    """Stacked, outlined, auto-wrapped title. colors: per-word overrides; strike: word indexes crossed out in red."""
    f = font(TF_BOLD, size)
    lines, cur = [], []
    for i, w in enumerate(words):
        if cur and f.measureText(' '.join(x for x, _ in cur + [(w, i)])) > max_w:
            lines.append(cur)
            cur = []
        cur.append((w, i))
    lines.append(cur)
    widest = max(f.measureText(' '.join(w for w, _ in ln)) for ln in lines)
    if widest > max_w:
        size *= max_w / widest
        f = font(TF_BOLD, size)
    for ln in lines:
        x = cx - f.measureText(' '.join(w for w, _ in ln)) / 2
        for w, i in ln:
            colr = (colors or {}).get(str(i)) or (hl_col if i == hl else '#ffffff')
            c.drawString(w, x + 8, y + 12, f, paint('#000000', 0.75, blur=10))
            c.drawString(w, x, y, f, paint('#000000', stroke=size * 0.17))
            c.drawString(w, x, y, f, paint(colr))
            wd = f.measureText(w)
            if i in strike:
                c.drawLine(x - 14, y - size * 0.28, x + wd + 14, y - size * 0.40, paint('#000000', stroke=size * 0.12))
                c.drawLine(x - 10, y - size * 0.28, x + wd + 10, y - size * 0.40, paint('#ff2d2d', stroke=size * 0.065))
            x += f.measureText(w + ' ')
        y += size * 1.05
    return y


def _arrow(c, x0, y0, x1, y1, colr='#ff2d2d', w=34):
    """Fat hand-drawn style arrow with a dark outline."""
    ang = math.atan2(y1 - y0, x1 - x0)
    mx, my = (x0 + x1) / 2 - math.sin(ang) * 60, (y0 + y1) / 2 + math.cos(ang) * 60
    hx, hy = x1 - math.cos(ang) * w * 1.6, y1 - math.sin(ang) * w * 1.6
    body = skia.Path()
    body.moveTo(x0, y0); body.quadTo(mx, my, hx, hy)
    head = skia.Path()
    for k, (dx, dy) in enumerate(((math.cos(ang) * w * 1.9, math.sin(ang) * w * 1.9),
                                  (-math.sin(ang) * w * 1.5, math.cos(ang) * w * 1.5),
                                  (math.sin(ang) * w * 1.5, -math.cos(ang) * w * 1.5))):
        (head.moveTo if k == 0 else head.lineTo)(hx + dx, hy + dy)
    head.close()
    bp = paint('#000000', stroke=w + 18); bp.setStrokeCap(skia.Paint.kRound_Cap)
    c.drawPath(body, bp); c.drawPath(head, paint('#000000', stroke=18))
    fp = paint(colr, stroke=w); fp.setStrokeCap(skia.Paint.kRound_Cap)
    c.drawPath(body, fp); c.drawPath(head, paint(colr))


def make_scene(S, path, OW, OH):
    """Cover built from a real frame of the story (so every video looks different) + bold overlays.
    Works for Shorts (1080x1920) and long videos (1920x1080).

    thumbnail: {"layout": "scene",
      "scene": {"index": 3, "t": 1.0, "zoom": 1.3, "focus": [x, y], "params": {...overrides}}
               (or {"template": "desk", "t": 1.0, "params": {...}} for a scene that isn't in the story),
      "tint": "#hex", "shade": ["top", "left"], "words": [...], "highlight": i, "colors": {"0": "#hex"}, "strike": [i],
      "title_x": cx, "title_y": 260, "title_size": 170, "title_w": 980,
      "big": {"text": "+60%", "x": 540, "y": 1500, "size": 300, "color": "#hex", "rotate": -6, "sub": "..."},
      "arrows": [[x0, y0, x1, y1]], "rings": [[x, y, r]], "badge": "...", "badge_pos": [x, y]}
    Coordinates are in output pixels.
    """
    from . import shorts as SH
    th = S['spec'].get('thumbnail', {})
    if th.get('panels'):
        return _finish(S, th, path, OW, OH, _panels(S, th, OW, OH))
    sc_cfg = th.get('scene', {})
    if 'template' in sc_cfg:
        sc = dict(template=sc_cfg['template'], duration=sc_cfg.get('duration', 6.0), params={})
    else:
        sc = dict(S['timeline'][sc_cfg.get('index', 0)])
    prm = dict(sc.get('params', {}))
    prm.update(sc_cfg.get('params', {}))
    for k in ('focus', 'zoom'):
        if k in sc_cfg:
            prm[k] = sc_cfg[k]
    prm.pop('focus_to', None)
    sc['params'] = prm
    t = sc_cfg.get('t', 1.0)
    vertical = OH > OW
    surf = skia.Surface(OW, OH)
    c = surf.getCanvas()
    c.clear(col('#000000'))
    if vertical:
        fx, fy, z = SH.focus_for(sc, t)
    else:
        z = prm.get('zoom', 1.0)
        f = prm.get('focus', (W / 2, H / 2))
        fx = min(max(f[0], W / 2 / z), W - W / 2 / z)
        fy = min(max(f[1], H / 2 / z), H - H / 2 / z)
    c.save(); c.translate(OW / 2, OH / 2); c.scale(z, z); c.translate(-fx, -fy)
    L.TEMPLATES[sc['template']](c, t, sc['duration'], prm, S)
    c.restore()
    return _finish(S, th, path, OW, OH, surf)


def _scene_surface(S, sc_cfg, OW, OH, cx, cy, base_z):
    """Render one story scene (index or inline template) into a full OWxOH surface, focus at (cx, cy)."""
    if 'template' in sc_cfg:
        sc = dict(template=sc_cfg['template'], duration=sc_cfg.get('duration', 6.0), params={})
    else:
        sc = dict(S['timeline'][sc_cfg.get('index', 0)])
    prm = dict(sc.get('params', {}))
    prm.update(sc_cfg.get('params', {}))
    prm.pop('focus_to', None)
    z = base_z * sc_cfg.get('zoom', 1.0)
    f = sc_cfg.get('focus', prm.get('focus', (W / 2, H / 2)))
    surf = skia.Surface(OW, OH)
    c = surf.getCanvas()
    c.clear(col('#000000'))
    c.save(); c.translate(cx, cy); c.scale(z, z); c.translate(-f[0], -f[1])
    L.TEMPLATES[sc['template']](c, sc_cfg.get('t', 1.0), sc['duration'], prm, S)
    c.restore()
    if sc_cfg.get('tint'):
        tp = paint(sc_cfg['tint'], 0.3); tp.setBlendMode(skia.BlendMode.kMultiply)
        c.drawRect(skia.Rect.MakeWH(OW, OH), tp)
    return surf


def _mark(c, x, y, r, ok):
    circle(c, x, y, r, '#2fbf5a' if ok else '#e8302a', '#000000', ow=r * 0.16)
    pp = paint('#ffffff', stroke=r * 0.26); pp.setStrokeCap(skia.Paint.kRound_Cap)
    if ok:
        pth = skia.Path(); pth.moveTo(x - r * 0.45, y + r * 0.02); pth.lineTo(x - r * 0.1, y + r * 0.38); pth.lineTo(x + r * 0.5, y - r * 0.35)
        c.drawPath(pth, pp)
    else:
        c.drawLine(x - r * 0.38, y - r * 0.38, x + r * 0.38, y + r * 0.38, pp)
        c.drawLine(x + r * 0.38, y - r * 0.38, x - r * 0.38, y + r * 0.38, pp)


def _panels(S, th, OW, OH):
    """Two scenes split by a slanted white divider: left/right for 16:9, top/bottom for Shorts (before vs. after)."""
    vertical = OH > OW
    pn = th['panels']
    slant = th.get('slant', 60)
    out = skia.Surface(OW, OH)
    c = out.getCanvas()
    for i, p in enumerate(pn[:2]):
        if vertical:
            cx, cy, bz = OW / 2, OH * (0.25 if i == 0 else 0.75), (OH / 2) / H
        else:
            cx, cy, bz = OW * (0.25 if i == 0 else 0.75), OH / 2, OH / H
        img = _scene_surface(S, p.get('scene', {}), OW, OH, cx, cy, bz).makeImageSnapshot()
        clip = skia.Path()
        if vertical:
            m = OH / 2
            if i == 0:
                clip.moveTo(0, 0); clip.lineTo(OW, 0); clip.lineTo(OW, m - slant); clip.lineTo(0, m + slant)
            else:
                clip.moveTo(0, m + slant); clip.lineTo(OW, m - slant); clip.lineTo(OW, OH); clip.lineTo(0, OH)
        else:
            m = OW / 2
            if i == 0:
                clip.moveTo(0, 0); clip.lineTo(m + slant, 0); clip.lineTo(m - slant, OH); clip.lineTo(0, OH)
            else:
                clip.moveTo(m + slant, 0); clip.lineTo(OW, 0); clip.lineTo(OW, OH); clip.lineTo(m - slant, OH)
        clip.close()
        c.save(); c.clipPath(clip, skia.ClipOp.kIntersect, True); c.drawImage(img, 0, 0); c.restore()
    if vertical:
        a0, a1 = (0, OH / 2 + slant), (OW, OH / 2 - slant)
    else:
        a0, a1 = (OW / 2 + slant, 0), (OW / 2 - slant, OH)
    c.drawLine(*a0, *a1, paint('#000000', stroke=26))
    c.drawLine(*a0, *a1, paint(th.get('divider', '#ffffff'), stroke=14))
    # labels with a check / cross
    for i, p in enumerate(pn[:2]):
        if not p.get('label'):
            continue
        lx, ly = p.get('label_pos') or ((OW / 2, OH * (0.43 if i == 0 else 0.93)) if vertical else
                                        (OW * (0.25 if i == 0 else 0.75), OH - 90))
        ls = p.get('label_size', 64 if vertical else 60)
        lw = measure(p['label'], ls, TF_BOLD) + 60 + (ls * 1.3 if 'ok' in p else 0)
        rrect(c, lx - lw / 2, ly - ls * 0.95, lw, ls * 1.45, ls * 0.35, p.get('label_bg', '#111116'), '#000000', ow=6)
        tx = lx + (ls * 0.65 if 'ok' in p else 0)
        text(c, p['label'], tx, ly + ls * 0.05, ls, p.get('label_color', '#ffffff'), tf=TF_BOLD, shadow=False)
        if 'ok' in p:
            _mark(c, lx - lw / 2 + ls * 0.75, ly - ls * 0.25, ls * 0.55, p['ok'])
    return out


def _finish(S, th, path, OW, OH, surf):
    vertical = OH > OW
    c = surf.getCanvas()
    if th.get('tint'):
        tp = paint(th['tint'], 0.28); tp.setBlendMode(skia.BlendMode.kMultiply)
        c.drawRect(skia.Rect.MakeWH(OW, OH), tp)
    # darken behind the text so it always reads
    tx = th.get('title_x', OW / 2)
    shade = th.get('shade')
    if shade is None:
        shade = [] if th.get('panels') else (['top', 'bottom'] if vertical else
                                             ['top', 'left' if tx < OW * 0.45 else 'right' if tx > OW * 0.55 else 'top'])
    for side in shade:
        k = 0.4 * (OH if side in ('top', 'bottom') else OW)
        r = {'top': (0, 0, OW, k), 'bottom': (0, OH - k, OW, k), 'left': (0, 0, k, OH), 'right': (OW - k, 0, k, OH)}[side]
        p0, p1 = {'top': ((0, 0), (0, k)), 'bottom': ((0, OH), (0, OH - k)), 'left': ((0, 0), (k, 0)), 'right': ((OW, 0), (OW - k, 0))}[side]
        c.drawRect(skia.Rect.MakeXYWH(*r), paint(shader=lin_grad(p0, p1, [('#000000', 0.82), ('#000000', 0.0)])))
    hl_col = th.get('highlight_color', URGE['say'])
    for (x, y, r) in th.get('rings', []):
        c.drawCircle(x, y, r, paint('#000000', stroke=30))
        c.drawCircle(x, y, r, paint('#ff2d2d', stroke=16))
    for a in th.get('arrows', []):
        _arrow(c, *a)
    big = th.get('big')
    if big:
        bxc, by = big.get('x', OW / 2), big.get('y', OH * 0.78)
        c.save(); c.rotate(big.get('rotate', -5), bxc, by)
        bs = big.get('size', 300)
        blines = big['text'].split('\n')
        f = font(TF_BOLD, bs)
        while max(f.measureText(ln) for ln in blines) > big.get('max_w', OW - 80):
            bs *= 0.92; f = font(TF_BOLD, bs)
        colr = big.get('color', hl_col)
        for ln in blines:
            bx = bxc - f.measureText(ln) / 2
            c.drawString(ln, bx, by, f, paint(colr, 0.85, blur=bs * 0.18))
            c.drawString(ln, bx + 10, by + 14, f, paint('#000000', 0.8, blur=8))
            c.drawString(ln, bx, by, f, paint('#000000', stroke=bs * 0.16))
            c.drawString(ln, bx, by, f, paint(colr))
            by += bs * 1.0
        by -= bs * 1.0
        if big.get('sub'):
            text(c, big['sub'], bxc, by + bs * 0.42 + big.get('sub_size', 70) * 0.4, big.get('sub_size', 70), '#ffffff', tf=TF_BOLD,
                 outline='#000000', ow=14, shadow=True)
        c.restore()
    words = th.get('words', [])
    if words:
        ty, tsz = th.get('title_y', 270 if vertical else 200), th.get('title_size', 170 if vertical else 150)
        tw = th.get('title_w', OW - 100 if vertical else OW * 0.5)
        if th.get('band'):
            c.save(); c.rotate(-3, tx, ty)
            rrect(c, tx - tw / 2 - 40, ty - tsz * 1.0, tw + 80, tsz * 1.05 * (1 + (len(words) > 2)) + 40, 26, th['band'], '#000000', ow=10)
            c.restore()
        _stack(c, words, th.get('highlight', -1), ty, tsz, hl_col, th.get('colors'), tuple(th.get('strike', [])), tw, tx)
    if th.get('badge'):
        bx, by = th.get('badge_pos', [OW / 2, OH - 160])
        bw = measure(th['badge'], 66, TF_BOLD) + 80
        c.save(); c.rotate(-4, bx, by)
        rrect(c, bx - bw / 2, by - 62, bw, 110, 24, '#ff2d2d', '#000000', ow=8)
        text(c, th['badge'], bx, by + 18, 66, '#ffffff', tf=TF_BOLD, shadow=False)
        c.restore()
    img = surf.makeImageSnapshot()
    img.save(path, skia.kPNG)
    sw, sh = (270, 480) if vertical else (320, 180)
    s2 = skia.Surface(sw, sh)
    s2.getCanvas().drawImageRect(img, skia.Rect.MakeWH(sw, sh), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    s2.makeImageSnapshot().save(path.replace('.png', '_small.png'), skia.kPNG)


def _heart(c, x, y, r, colr, a=1.0):
    p = skia.Path()
    p.moveTo(x, y + r * 0.9)
    p.cubicTo(x - r * 1.6, y - r * 0.2, x - r * 0.8, y - r * 1.3, x, y - r * 0.45)
    p.cubicTo(x + r * 0.8, y - r * 1.3, x + r * 1.6, y - r * 0.2, x, y + r * 0.9)
    c.drawPath(p, paint(colr, a))
    c.drawPath(p, paint('#000000', a, stroke=r * 0.14))


def _drop(c, x, y, r, a=1.0):
    p = skia.Path()
    p.moveTo(x, y - r * 1.4); p.quadTo(x + r, y + r * 0.1, x, y + r * 0.8); p.quadTo(x - r, y + r * 0.1, x, y - r * 1.4)
    c.drawPath(p, paint('#d6efff', a))
    c.drawPath(p, paint('#000000', a, stroke=r * 0.22))
    circle(c, x - r * 0.25, y - r * 0.1, r * 0.22, '#ffffff', None, a=a)


def make_hero(S, path, OW=W, OH=H):
    """Big, lit, expressive close-up of the hero with one bold word (the channel's 'film poster' style).

    thumbnail: {"layout": "hero", "bg": "bedroom|rain", "expr": "tired", "look": [x, y], "bags": 1, "glow": "#ff4f8b",
                "light_dir": [x, y], "prop": "phone|fists|none", "particles": "hearts|sweat|none", "hero_x": 900,
                "words": ["DOPAMINE."], "highlight": -1, "highlight_color": "#hex", "title_rotate": -3}
    """
    th = S['spec'].get('thumbnail', {})
    g = th.get('glow', '#ff4f8b')
    ldir = th.get('light_dir', (0.8, 0.4))
    hero = dict(S['hero'], shade=dict(dir=ldir, rim=g, amt=0.42, rim_a=0.9))
    surf = skia.Surface(OW, OH)
    c = surf.getCanvas()
    bg = th.get('bg', 'bedroom')
    hx, hy, sc = th.get('hero_x', OW * 0.45), th.get('hero_y', OH * 0.57), th.get('scale', 3.8)
    rnd = random.Random(5)
    if bg == 'rain':
        c.drawRect(skia.Rect.MakeWH(OW, OH), paint(shader=lin_grad((0, 0), (0, OH), ['#0b1424', '#1a2a44', '#0d1626'])))
        for _ in range(16):
            bx, by, br = rnd.uniform(0, OW), rnd.uniform(OH * 0.2, OH * 0.7), rnd.uniform(30, 90)
            glow(c, bx, by, br * 2.2, rnd.choice(['#ffcf7a', '#9fc4ff', '#ffe6b0']), 0.35)
        c.drawRect(skia.Rect.MakeXYWH(0, OH * 0.78, OW, OH * 0.22), paint(shader=lin_grad((0, OH * 0.78), (0, OH), ['#0e1a2e', '#060b14'])))
    else:
        c.drawRect(skia.Rect.MakeWH(OW, OH), paint(shader=rad_grad((OW * 0.6, OH * 0.45), OW * 0.8, ['#1c1830', '#0a0912', '#040407'])))
        rrect(c, hx - 560, hy + 40, 600, 300, 140, '#1b2038', '#2b3254', ow=10)       # pillow
        rrect(c, hx + 120, hy - 20, 520, 280, 140, '#171b30', '#262c48', ow=10)
    feet_y = hy + 328 * sc * hero.get('height', 1.0)
    r = draw_person(c, hx, feet_y, sc, hero, th.get('expr', 'tired'), 1.0, look=tuple(th.get('look', (0.6, 0.4))),
                    arms=((6, 3), (-6, -3)), face_kw=dict(bags=th.get('bags', 1.0), pupil_glow=th.get('eye_glow')))
    hcx, hcy = r['head']
    hr = r['hr']
    prop = th.get('prop', 'phone')
    if bg == 'bedroom':                                                               # blanket over the shoulders
        bl = skia.Path()
        bl.moveTo(-50, OH + 50); bl.lineTo(-50, hy + hr * 1.35)
        bl.cubicTo(OW * 0.25, hy + hr * 1.05, OW * 0.55, hy + hr * 1.45, OW * 0.8, hy + hr * 1.2)
        bl.cubicTo(OW * 0.9, hy + hr * 1.1, OW, hy + hr * 1.25, OW + 50, hy + hr * 1.2); bl.lineTo(OW + 50, OH + 50); bl.close()
        c.drawPath(bl, paint(shader=lin_grad((0, hy + hr), (0, OH), ['#2c3561', '#141a33'])))
        c.drawPath(bl, paint('#000000', stroke=10))
    px, py = hcx + hr * 1.2, hcy + hr * 0.78
    if prop == 'phone':
        c.save(); c.rotate(-14, px, py)
        rrect(c, px - 95, py - 175, 190, 350, 34, '#14141c', '#000000', ow=10)
        rrect(c, px - 80, py - 158, 160, 316, 24, mix(g, '#ffffff', 0.35), None)
        c.drawRect(skia.Rect.MakeXYWH(px - 80, py - 158, 160, 316), paint(shader=lin_grad((px, py - 158), (px, py + 158), [(mix(g, '#ffffff', 0.6), 1), (g, 1)]), a=0.9))
        c.restore()
        for k, (dx, dy, rr) in enumerate(((62, 135, 60), (-72, 110, 52))):                # fingers / hand
            circle(c, px + dx, py + dy, rr, hero['skin'], '#000000', ow=9)
    elif prop == 'fists':                                                              # running arms, pumping
        shy = hcy + hr * 1.5
        for side, (fx, fy) in ((-1, (hcx - hr * 1.3, hcy + hr * 0.7)), (1, (hcx + hr * 1.55, hcy + hr * 1.3))):
            sx_ = hcx + side * hr * 0.95
            ex_, ey_ = (sx_ + fx) / 2 + side * hr * 0.45, (shy + fy) / 2 + hr * 0.35
            limb(c, [(sx_, shy), (ex_, ey_), (fx, fy)], hr * 0.42, hero['hoodie'], ow=10)
            circle(c, fx, fy, hr * 0.33, hero['skin'], '#000000', ow=10)
            for k in range(3):
                c.drawLine(fx - hr * 0.16 + k * hr * 0.15, fy - hr * 0.24, fx - hr * 0.16 + k * hr * 0.15, fy - hr * 0.04,
                           paint('#000000', 0.7, stroke=6))
            for k in range(3):
                c.drawLine(fx + side * hr * 0.45, fy - hr * 0.25 + k * hr * 0.22, fx + side * hr * 0.85, fy - hr * 0.25 + k * hr * 0.22,
                           paint('#ffffff', 0.55, stroke=8))
        for k, (dx, dy, rr) in enumerate(((0.55, 0.62, 0.16), (0.8, 0.5, 0.2), (1.08, 0.36, 0.25))):   # cold breath
            oval(c, hcx + dx * hr, hcy + dy * hr, rr * hr, rr * hr * 0.7, '#e8f2ff', a=0.32 - k * 0.07)
    # coloured light from the light source onto the scene
    lsx, lsy = (px, py) if prop == 'phone' else (hcx + ldir[0] * hr * 3, hcy + ldir[1] * hr * 3)
    lp_ = paint(shader=rad_grad((lsx, lsy), OW * 0.55, [(g, 0.55), (g, 0.18), (g, 0.0)], [0, 0.35, 1]))
    lp_.setBlendMode(skia.BlendMode.kScreen)
    c.drawRect(skia.Rect.MakeWH(OW, OH), lp_)
    parts = th.get('particles', 'none')
    if parts == 'hearts':                                     # a glowing stream of rewards from the phone into the head
        p0, p2 = (px + 20, py - hr * 0.75), (hcx + hr * 0.1, hcy - hr * 1.05)
        p1 = (px + hr * 1.6, hcy - hr * 1.9)
        def qb(u):
            return ((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0],
                    (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1])
        rib = skia.Path(); rib.moveTo(*p0); rib.quadTo(*p1, *p2)
        for w_, a_ in ((90, 0.18), (46, 0.35), (16, 0.9)):
            c.drawPath(rib, paint(g if w_ > 20 else mix(g, '#ffffff', 0.6), a_, stroke=w_, blur=w_ * 0.4))
        for i in range(16):
            u = (i + 0.5) / 16
            x, y = qb(u)
            x += 60 * math.sin(i * 2.3); y += 50 * math.cos(i * 1.7)
            glow(c, x, y, 80, g, 0.5)
            if i % 4 == 2:
                lbl = ['+1', '99+', '3', '+5', '12'][i % 5]
                bw = measure(lbl, 44, TF_BOLD) + 40
                rrect(c, x - bw / 2, y - 34, bw, 64, 32, '#ff3045', '#000000', ow=6)
                text(c, lbl, x, y + 14, 44, '#ffffff', tf=TF_BOLD, shadow=False)
            else:
                _heart(c, x, y, 30 + 12 * math.sin(i * 2.1) + 10 * (1 - u), rnd.choice([g, mix(g, '#ffffff', 0.4), '#ff3b6b']))
    elif parts == 'sweat':
        for (dx, dy, rr) in ((-0.55, -0.55, 0.11), (0.62, -0.42, 0.1), (-0.8, 0.05, 0.09), (0.86, 0.1, 0.12),
                             (0.2, -0.82, 0.08), (-0.3, -0.85, 0.07), (0.7, 0.55, 0.08)):
            _drop(c, hcx + dx * hr, hcy + dy * hr, rr * hr)
    if th.get('rain', bg == 'rain'):
        for _ in range(260):
            x, y = rnd.uniform(-100, OW), rnd.uniform(-60, OH)
            c.drawLine(x, y, x + 10, y + 56, paint('#cfe0ff', rnd.uniform(0.25, 0.6), stroke=rnd.uniform(2, 4)))
    vp = paint(shader=rad_grad((OW / 2, OH * 0.55), OW * 0.7, [('#000000', 0), ('#000000', 0), ('#000000', 0.6)], [0, 0.55, 1]))
    c.drawRect(skia.Rect.MakeWH(OW, OH), vp)
    words = th.get('words', [])
    if words:
        tsz = th.get('title_size', 210)
        f = font(TF_BOLD, tsz)
        txt = ' '.join(words)
        while f.measureText(txt) > OW - 140:
            tsz *= 0.94; f = font(TF_BOLD, tsz)
        ty = th.get('title_y', tsz * 0.95)
        c.save(); c.rotate(th.get('title_rotate', 0), OW / 2, ty)
        x = OW / 2 - f.measureText(txt) / 2
        hl, hlc = th.get('highlight', -1), th.get('highlight_color', g)
        for i, w in enumerate(words):
            c.drawString(w, x + 10, ty + 16, f, paint('#000000', 0.8, blur=12))
            c.drawString(w, x, ty, f, paint('#000000', stroke=tsz * 0.2))
            c.drawString(w, x, ty, f, paint(hlc if i == hl else th.get('title_color', '#ffffff')))
            x += f.measureText(w + ' ')
        c.restore()
    img = surf.makeImageSnapshot()
    img.save(path, skia.kPNG)
    s2 = skia.Surface(320, 180)
    s2.getCanvas().drawImageRect(img, skia.Rect.MakeWH(320, 180), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    s2.makeImageSnapshot().save(path.replace('.png', '_small.png'), skia.kPNG)
