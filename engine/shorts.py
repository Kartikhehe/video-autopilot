"""Vertical YouTube Shorts (1080x1920) built from the same scene templates.

The 16:9 scene is scaled to fill the height and a 9:16 window follows the action (`focus`).
On top: a hook headline in the first seconds, big punchy captions (use *word* to highlight),
DAY labels, and a subscribe call-to-action at the end.
"""
import math
from .draw import *
from . import library as L

OW, OH = 1080, 1920
ZMIN = OH / H
SAFE_W = 900          # keep text clear of the right-hand like/comment buttons
CAPTION_Y = 1500      # below faces, above the bottom title/channel overlay

TEMPLATE_FOCUS = {
    'card': (960, 540), 'end_card': (960, 540), 'phone_feed': (960, 540), 'phone_chat': (960, 540), 'face': (960, 540),
    'mirror': (950, 540), 'desk': (990, 540), 'bedroom': (900, 540), 'hangout': (930, 540), 'stage': (1050, 540),
    'gallery': (1230, 540), 'sunrise': (970, 540), 'outro': (960, 540),
}


def active(sc, t):
    """(template, params, local_t, local_dur, label) of what's on screen; resolves montage shots."""
    p = sc.get('params', {})
    if sc['template'] != 'montage':
        return sc['template'], p, t, sc['duration'], p.get('label')
    shots = p['shots']
    scale = sc['duration'] / sum(s['dur'] for s in shots)
    acc = 0.0
    for s in shots:
        sd = s['dur'] * scale
        if t < acc + sd or s is shots[-1]:
            return s['template'], s.get('params', {}), t - acc, sd, s.get('label')
        acc += sd


def focus_for(sc, t):
    tpl, p, lt, ld, _ = active(sc, t)
    f = p.get('focus') or sc.get('focus') or TEMPLATE_FOCUS.get(tpl, (960, 540))
    if p.get('focus_to'):
        u = ease_in_out(lt / max(ld, 0.01))
        f = (lerp(f[0], p['focus_to'][0], u), lerp(f[1], p['focus_to'][1], u))
    z = ZMIN * p.get('zoom', sc.get('zoom', 1.0))
    hw, hh = OW / 2 / z, OH / 2 / z
    fx = min(max(f[0], hw), W - hw)
    fy = min(max(f[1], hh), H - hh)
    return fx, fy, z


def _words(s):
    out = []
    for w in s.split():
        hl = '*' in w
        out.append((w.replace('*', ''), hl))
    return out


def bold_block(c, s, cx, cy, size, hl_col, a=1.0, scale=1.0, max_w=SAFE_W):
    """Centered, wrapped, outlined bold text. *word* = highlighted."""
    if a <= 0:
        return
    f = font(TF_BOLD, size)
    space = f.measureText(' ')
    words = _words(s)
    lines, cur, cw = [], [], 0.0
    for w, hl in words:
        ww = f.measureText(w)
        if cur and cw + space + ww > max_w:
            lines.append((cur, cw))
            cur, cw = [], 0.0
        cw = cw + (space if cur else 0) + ww
        cur.append((w, hl, ww))
    if cur:
        lines.append((cur, cw))
    lh = size * 1.12
    top = cy - lh * (len(lines) - 1) / 2
    c.save()
    c.translate(cx, cy)
    c.scale(scale, scale)
    c.translate(-cx, -cy)
    for li, (ln, lw) in enumerate(lines):
        x = cx - lw / 2
        y = top + li * lh + size * 0.35
        for w, hl, ww in ln:
            c.drawString(w, x + 5, y + 8, f, paint('#000000', 0.55 * a, blur=8))
            c.drawString(w, x, y, f, paint('#000000', a, stroke=size * 0.2))
            c.drawString(w, x, y, f, paint(hl_col if hl else '#ffffff', a))
            x += ww + space
    c.restore()


def post_v(c, fi, vignette=0.5, grain=0.06):
    vp = paint(shader=rad_grad((OW / 2, OH / 2), OH * 0.62, [('#000000', 0), ('#000000', 0), ('#000000', vignette)], [0, 0.6, 1]))
    c.drawRect(skia.Rect.MakeWH(OW, OH), vp)
    from .draw import _grain
    gp = skia.Paint()
    gp.setAlphaf(grain)
    gp.setBlendMode(skia.BlendMode.kOverlay)
    c.drawImageRect(_grain[(fi // 2) % len(_grain)], skia.Rect.MakeWH(OW, OH), skia.SamplingOptions(skia.FilterMode.kLinear), gp)


def render_frame(c, gt, fi, S):
    sh = S['spec'].get('short', {})
    hl_col = sh.get('highlight_color', URGE['say'])
    tl = S['timeline']
    for sc in tl:
        t0, dur = sc['t0'], sc['duration']
        if not (t0 <= gt < t0 + dur or sc is tl[-1]):
            continue
        t = min(gt - t0, dur - 1e-3)
        fx, fy, z = focus_for(sc, t)
        c.save()
        c.translate(OW / 2, OH / 2)
        c.scale(z, z)
        c.translate(-fx, -fy)
        L.TEMPLATES[sc['template']](c, t, dur, sc.get('params', {}), S)
        c.restore()
        post_v(c, fi, 0.0 if sc['template'] in ('card', 'end_card') else 0.5)
        tpl, p, lt, ld, label = active(sc, t)
        if label:
            bold_block(c, label, OW / 2, 360, 84, hl_col, ramp(lt, 0.0, 0.25), 0.9 + 0.1 * ease_out(lt / 0.2))
        for (a0, a1, s) in sc.get('captions', []):
            if a0 - 0.05 <= t <= a1 + 0.05:
                a = window(t, a0, a1, 0.15)
                pop = 0.82 + 0.18 * ease_out((t - a0) / 0.18)
                bold_block(c, s, OW / 2, CAPTION_Y, sh.get('caption_size', 74), hl_col, a, pop)
        hook = sh.get('hook')
        if hook and gt < hook.get('until', 2.8):
            a = 1 - ramp(gt, hook.get('until', 2.8) - 0.25, hook.get('until', 2.8))
            pulse = 1 + 0.03 * math.sin(gt * 6)
            bold_block(c, hook['text'], OW / 2, hook.get('y', 470), hook.get('size', 96), hl_col, a, pulse)
        if sc is tl[-1] and sh.get('cta', True):
            k = ramp(t, dur - 2.6, dur - 2.3)
            if k > 0:
                cy = 1290
                pop = 1 + 0.08 * math.sin(clamp01((t - (dur - 2.3)) / 0.3) * math.pi)
                c.save(); c.translate(OW / 2, cy); c.scale(pop, pop)
                rrect(c, -230, -58, 460, 116, 58, '#e0322d', '#000000', ow=6, a=k)
                text(c, sh.get('cta_text', 'SUBSCRIBE'), 0, 20, 58, '#ffffff', a=k, tf=TF_BOLD, shadow=False)
                c.restore()
        fi_, fo_ = sc.get('fade_in', 0.12), sc.get('fade_out', 0.12)
        kk = 1.0
        if fi_ > 0 and sc is not tl[0]:
            kk = min(kk, ramp(t, 0, fi_))
        if fo_ > 0 and sc is not tl[-1]:
            kk = min(kk, 1 - ramp(t, dur - fo_, dur))
        if kk < 1:
            c.drawRect(skia.Rect.MakeWH(OW, OH), paint('#000000', 1 - kk))
        return sc
