"""Scene templates. A story file picks templates and fills their params; nothing here is story-specific.

Every template: fn(c, t, d, p, S)
  t = local time (s), d = scene duration, p = scene params (dict), S = story context (cast, habit colour...).
"""
import math, random
from .draw import *

SKIES = {
    'sunset': ('#f39a5b', '#b4527a', '#3b2b55'),
    'day': ('#ffd9a6', '#a6c6e2', '#6d98c9'),
    'dusk': ('#c46a5a', '#6b3b62', '#241a33'),
    'night': ('#2a2f55', '#161a33', '#0a0c1a'),
    'dawn': ('#ffcf9a', '#c99bb0', '#5a6a9a'),
}

CAMERAS = {
    'push': dict(z0=1.0, z1=1.06),
    'push_slow': dict(z0=1.02, z1=1.05),
    'close': dict(z0=1.12, z1=1.22),
    'pan_right': dict(z0=1.12, z1=1.15, px0=120, px1=-160),
    'pan_left': dict(z0=1.12, z1=1.15, px0=-120, px1=160),
    'still': dict(z0=1.0, z1=1.0),
}


def cam(c, t, d, p, default='push', fx=0.5, fy=0.55):
    spec = p.get('camera', default)
    cfg = dict(CAMERAS.get(spec, CAMERAS['push'])) if isinstance(spec, str) else dict(spec)
    u = ease_in_out(t / max(d, 0.01))
    z = lerp(cfg.get('z0', 1.0), cfg.get('z1', 1.06), u)
    cx, cy = W * cfg.get('fx', fx), H * cfg.get('fy', fy)
    c.translate(cx + lerp(cfg.get('px0', 0), cfg.get('px1', 0), u), cy + lerp(cfg.get('py0', 0), cfg.get('py1', 0), u))
    c.scale(z, z)
    c.translate(-cx, -cy)


def at_time(v, t, default=None):
    """v may be a value or a list of [t, value] keyframes (step)."""
    if isinstance(v, list) and v and isinstance(v[0], list):
        cur = v[0][1]
        for tk, val in v:
            if t >= tk:
                cur = val
        return cur
    return default if v is None else v


def walk_legs(ph, amp=24):
    s = math.sin(ph)
    return ((amp * s, amp * s - 14 * max(0, s)), (-amp * s, -amp * s - 14 * max(0, -s)))


def strum_arms(t, strum=True, speed=7.0):
    k = 14 * math.sin(t * speed) if strum else 0
    return ((-20, 60 + k), (60, 120))


def notes(c, t, x, y, n=4, colr='#ffe2a0', a=1.0, seed=1, spread=160):
    rnd = random.Random(seed)
    for i in range(n):
        ph = (t * 0.45 + i / n + rnd.random() * 0.3) % 1.0
        nx = x + rnd.uniform(-spread, spread) * 0.4 + math.sin(t * 2 + i) * 18 + ph * rnd.uniform(-60, 60)
        ny = y - ph * 260
        al = a * math.sin(ph * math.pi)
        s = rnd.uniform(0.8, 1.2)
        oval(c, nx, ny, 11 * s, 8 * s, colr, a=al)
        c.drawLine(nx + 10 * s, ny, nx + 10 * s, ny - 36 * s, paint(colr, al, stroke=3.5 * s))
        c.drawLine(nx + 10 * s, ny - 36 * s, nx + 22 * s, ny - 26 * s, paint(colr, al, stroke=3.5 * s))


# ---------------------------------------------------------------- characters doing things

def person_activity(c, x, y, t, ch, act='idle', expr='neutral', look=(0, 0), s=1.0, pose='stand', walk_ph=None, **kw):
    """Draw a character performing an activity. Returns anchors."""
    blink = blink_at(t, 3.4, (hash(ch.get('hoodie', '')) % 7) * 0.3)
    common = dict(look=tuple(look), blink=blink, pose=pose)
    common.update(kw)
    if walk_ph is not None:
        common.update(legs=walk_legs(walk_ph), bob=-abs(math.sin(walk_ph)) * 8)
    if act == 'guitar':
        return draw_person(c, x, y, s, ch, expr, t, prop='guitar', arms=strum_arms(t), **common)
    if act == 'guitar_still':
        return draw_person(c, x, y, s, ch, expr, t, prop='guitar', arms=strum_arms(t, False), **common)
    if act == 'sketch':
        k = math.sin(t * 9) * 6
        r = draw_person(c, x, y, s, ch, expr, t, arms=((-10, 160), (10 + k, -160 + k)), **common)
        draw_sketchbook(c, x, y - 225 * s * ch.get('height', 1), s * 0.95, t, 0.4 + 0.6 * ((t * 0.15) % 1))
        return r
    if act == 'talk':
        k = math.sin(t * 5.5)
        return draw_person(c, x, y, s, ch, expr, t, arms=((15 + 20 * k, -40 - 50 * max(0, k)), (-10, -5)), **common)
    if act == 'write':
        k = math.sin(t * 12) * 5
        r = draw_person(c, x, y, s, ch, expr, t, arms=((-10, 160), (10 + k, -155 + k)), **common)
        nx, ny = x, y - 225 * s * ch.get('height', 1)
        rrect(c, nx - 60 * s, ny - 70 * s, 120 * s, 140 * s, 6 * s, '#fbf6e8', INK, ow=4 * s)
        done = int(clamp01(kw.get('progress', (t * 0.35) % 1.2)) * 5)
        for i in range(5):
            ly = ny - 45 * s + i * 24 * s
            rrect(c, nx - 46 * s, ly - 7 * s, 14 * s, 14 * s, 3 * s, '#ffffff', INK, ow=2.5 * s)
            if i < done:
                c.drawLine(nx - 30 * s, ly, nx + (20 + (i * 13) % 25) * s, ly, paint('#3d5a80', stroke=4 * s))
        return r
    if act == 'camera':
        r = draw_person(c, x, y, s, ch, expr, t, arms=((-10, 160), (10, -160)), **common)
        ph = (t + (hash(ch.get('hoodie', '')) % 5) * 0.4) % 3.2
        draw_camera(c, x, y - 232 * s * ch.get('height', 1), 0.95 * s, max(0.0, 1 - ph / 0.35) if ph < 0.35 else 0.0)
        return r
    if act == 'book':
        r = draw_person(c, x, y, s, ch, expr, t, arms=((-10, 160), (10, -160)), **common)
        rrect(c, x - 70 * s, y - 280 * s, 140 * s, 95 * s, 6 * s, '#c8423b', INK, ow=4 * s)
        c.drawLine(x, y - 280 * s, x, y - 185 * s, paint(INK, stroke=3 * s))
        return r
    if act == 'ball':
        ph = (t * 1.6) % 1
        by = y - 160 * s - abs(math.sin(ph * math.pi)) * -140 * s
        hy_ = y - 230 * s
        bh = lerp(hy_, y - 30 * s, abs(math.sin(ph * math.pi)))
        r = draw_person(c, x, y, s, ch, expr, t, arms=((-20, -40), (40 - 20 * math.sin(ph * math.tau), 30)), **common)
        draw_ball(c, x + 70 * s, bh, 32 * s, t * 200)
        return r
    if act == 'phone':
        r = draw_person(c, x, y, s, ch, expr, t, arms=((-8, 168), (8, -168)), **common)
        draw_phone_small(c, x, y - 218 * s * ch.get('height', 1), 1.0 * s, kw.get('phone_col', '#8fb4ff'), 1.0, 0)
        return r
    if act == 'wave':
        w = math.sin(t * 7)
        return draw_person(c, x, y, s, ch, expr, t, arms=((10, 5), (150, 165 + 25 * w)), **common)
    if act == 'drum':
        return bucket_drummer(c, x, y, t, ch, expr, look, s)
    if act == 'sit':
        return draw_person(c, x, y, s, ch, expr, t, arms=((-10, 30), (10, -30)), **dict(common, pose='sit'))
    return draw_person(c, x, y, s, ch, expr, t, arms=kw.pop('arms', ((10, 5), (-10, -5))), **common)


def bucket_drummer(c, x, y, t, ch, expr='happy', look=(0, 0), s=1.0, speed=6.0, amp=1.0):
    k = math.sin(t * speed) * amp
    rrect(c, x - 70 * s, y - 70 * s, 140 * s, 70 * s, 6 * s, '#7a5236', ow=5 * s)
    r = draw_person(c, x, y - 40 * s, s, ch, expr, t, pose='sit', arms=((-25 + 20 * k, 40 + 30 * k), (25 + 20 * k, -40 + 30 * k)),
                    look=tuple(look), blink=blink_at(t, 4.1, 1.3))
    bp = skia.Path()
    bx, by = x, y - 30 * s
    bp.moveTo(bx - 50 * s, by - 110 * s); bp.lineTo(bx + 50 * s, by - 110 * s)
    bp.lineTo(bx + 40 * s, by); bp.lineTo(bx - 40 * s, by); bp.close()
    c.drawPath(bp, paint('#3f7fb8')); c.drawPath(bp, paint(INK, stroke=5 * s))
    oval(c, bx, by - 110 * s, 50 * s, 12 * s, '#2e5f8c', INK, ow=4 * s)
    return r


def urge_from(c, t, d, u, x0, y0):
    """Draw the habit creature from a params dict: size, grow, x, y, eye, mouth, look, alpha, pop_at, whispers."""
    if not u:
        return
    size = u.get('size', 100)
    if 'grow' in u:
        size = lerp(size, u['grow'], ease_in_out(t / max(d, 0.01)))
    if 'appear_at' in u:
        size *= ease_out((t - u['appear_at']) / 1.5) if t > u['appear_at'] else 0
    x, y = u.get('x', x0), u.get('y', y0)
    a = u.get('alpha', 1.0)
    if 'fade_in_at' in u:
        a *= ramp(t, u['fade_in_at'], u['fade_in_at'] + 1.2)
    pop = u.get('pop_at')
    if pop is not None and t > pop:
        k = ramp(t, pop, pop + 0.8)
        rnd = random.Random(4)
        for i in range(26):
            ang = rnd.random() * math.tau
            dd = (t - pop) * rnd.uniform(60, 220)
            circle(c, x + math.cos(ang) * dd, y - size + math.sin(ang) * dd - (t - pop) * 40, rnd.uniform(3, 7),
                   URGE['say'], None, a=max(0, 0.8 - (t - pop) * 0.45))
        a *= 1 - k
    eye = u.get('eye', 1.0)
    if 5.9 < (t % 6.0) < 6.0:
        eye *= 0.1
    talking = any(tw <= t <= tw + 1.6 for tw, _ in u.get('whispers', []))
    mouth = u.get('mouth', 0.0) + (0.25 * abs(math.sin(t * 9)) if talking else 0)
    hand = u.get('hand')
    draw_urge(c, x, y, size, t, eye=eye, mouth=mouth, a=a, look=tuple(u.get('look', (-1, 0))),
              hand=tuple(hand) if hand else None)
    whispers = u.get('whispers', [])
    sx, sy = u.get('say_x', x + size * 0.9), u.get('say_y', y - size * 2.25)
    for i, (tw, s) in enumerate(whispers):
        nxt = whispers[i + 1][0] if i + 1 < len(whispers) else d
        if tw <= t < nxt:
            urge_say(c, s, min(max(sx, 260), W - 260), max(sy, 120), tw, t, u.get('say_size', 48), a=a * (1 - ramp(t, nxt - 0.3, nxt)))


# ---------------------------------------------------------------- backgrounds

def draw_park(c, t, sky='day', lights=1.0):
    s = SKIES.get(sky, SKIES['day'])
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=lin_grad((0, 0), (0, 820), [s[2], s[1], s[0]], [0, 0.55, 1])))
    if sky in ('night', 'dusk'):
        glow(c, 1500, 220, 160, '#cfd9ff', 0.35)
        circle(c, 1500, 220, 46, '#eef2ff', None)
    else:
        glow(c, 1450, 640, 520, '#ffcf8a', 0.4)
        circle(c, 1450, 640, 70, '#ffe2b0', None, a=0.9)
    for i, (hx, hr, colr) in enumerate([(300, 700, '#5c7a5a'), (1300, 800, '#4e6d50'), (1900, 600, '#58765a')]):
        c.drawCircle(hx, 1260, hr, paint(mix(colr, s[2], 0.35)))
    c.drawRect(skia.Rect.MakeLTRB(0, 820, W, H), paint(shader=lin_grad((0, 820), (0, H), ['#5f8f4e', '#3f6a38'])))
    c.drawLine(0, 822, W, 822, paint(INK, stroke=5))
    pth = skia.Path()
    pth.moveTo(760, H); pth.quadTo(900, 900, 1100, 822); pth.lineTo(1200, 822); pth.quadTo(1060, 920, 1000, H); pth.close()
    c.drawPath(pth, paint('#c9b48a'))
    for tx, ts in ((150, 1.0), (520, 0.8), (1600, 1.1)):
        c.drawRect(skia.Rect.MakeLTRB(tx - 18 * ts, 560, tx + 18 * ts, 830), paint('#5a3d2b'))
        for dx, dy, rr in ((0, -40, 120), (-80, 30, 90), (80, 30, 95)):
            circle(c, tx + dx * ts, 520 + dy * ts, rr * ts, '#3f7a45', INK, ow=5)
    # bench + lamp
    rrect(c, 1240, 740, 300, 22, 6, '#7a5236', ow=4)
    rrect(c, 1240, 690, 300, 22, 6, '#7a5236', ow=4)
    for lx in (1260, 1500):
        c.drawLine(lx, 762, lx, 830, paint('#3a2a20', stroke=10))
    c.drawLine(1700, 830, 1700, 420, paint('#2a2a30', stroke=12))
    if sky in ('night', 'dusk'):
        glow(c, 1700, 420, 200, '#ffd27a', 0.5 * lights)
    circle(c, 1700, 415, 22, '#ffe6a6' if sky in ('night', 'dusk') else '#d9d9d9', INK, ow=4)


def draw_street(c, t, sky='night', lights=1.0):
    s = SKIES.get(sky, SKIES['night'])
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=lin_grad((0, 0), (0, 820), [s[2], s[1], s[0]], [0, 0.55, 1])))
    rnd = random.Random(21)
    x = -40
    while x < W + 40:
        w = rnd.randint(260, 380)
        hgt = rnd.randint(260, 380)
        colr = rnd.choice(['#3b3550', '#43384f', '#353a52', '#4a3a45'])
        c.drawRect(skia.Rect.MakeLTRB(x, 840 - hgt, x + w - 20, 840), paint(colr))
        roof = skia.Path()
        roof.moveTo(x - 20, 840 - hgt); roof.lineTo(x + (w - 20) / 2, 840 - hgt - 110); roof.lineTo(x + w, 840 - hgt); roof.close()
        c.drawPath(roof, paint(mix(colr, '#000000', 0.3)))
        for wx in (x + 40, x + w - 120):
            on = rnd.random() < 0.6
            rrect(c, wx, 840 - hgt + 70, 60, 80, 4, '#ffd27a' if on and sky != 'day' else '#2a2a3a', INK, ow=3)
        x += w
    c.drawRect(skia.Rect.MakeLTRB(0, 840, W, 900), paint('#5a5560'))
    c.drawRect(skia.Rect.MakeLTRB(0, 900, W, H), paint('#2a2830'))
    for i in range(0, W, 220):
        c.drawRect(skia.Rect.MakeXYWH(i, 990, 120, 12), paint('#d9d2b8', 0.6))
    for lx in (300, 1100, 1800):
        c.drawLine(lx, 900, lx, 470, paint('#22222a', stroke=12))
        if sky != 'day':
            glow(c, lx, 470, 260, '#ffd27a', 0.45 * lights)
            c.drawPath(_cone(lx, 470), paint('#ffd27a', 0.06 * lights, blur=10))
        circle(c, lx, 465, 20, '#ffe6a6', INK, ow=4)


def _cone(x, y):
    p = skia.Path()
    p.moveTo(x - 10, y); p.lineTo(x + 10, y); p.lineTo(x + 160, 900); p.lineTo(x - 160, 900); p.close()
    return p


def draw_place(c, t, place, sky, p):
    if place == 'park':
        draw_park(c, t, sky)
    elif place == 'street':
        draw_street(c, t, sky)
    else:
        poster = p.get('poster')
        draw_rooftop(c, t, SKIES.get(sky, SKIES['sunset']), lights=0.0 if sky == 'day' else 1.0,
                     poster=' '.join(poster[:1]) + ' ' if poster else None,
                     poster2=poster[1] if poster and len(poster) > 1 else '')


ROOM_LIGHT = {
    'night': dict(room=('#1d2336', '#131725'), moon=True),
    'dark': dict(room=('#1a1d2b', '#0e1018'), moon=True),
    'lamp': dict(room=('#262838', '#171826'), moon=True, lamp=0.9),
    'dawn': dict(room=('#4a5a86', '#2a3354'), moon=False),
    'day': dict(room=('#7a8fb8', '#5a6a94'), moon=False),
}


def room(c, t, light='night'):
    cfg = ROOM_LIGHT.get(light, ROOM_LIGHT['night'])
    draw_bedroom(c, t, moon=cfg['moon'], lamp=cfg.get('lamp', 0.0), room_col=cfg['room'])


# ---------------------------------------------------------------- templates

def t_card(c, t, d, p, S):
    c.clear(col('#000000'))
    a = window(t, 0.3, d - 0.1, 0.6)
    text(c, p['text'], W / 2, H / 2 + 20 - (40 if p.get('sub') else 0), p.get('size', 72), a=a)
    if p.get('sub'):
        text(c, p['sub'], W / 2, H / 2 + 70, 44, '#bdb6aa', a=window(t, 1.0, d - 0.1, 0.6))


def t_hangout(c, t, d, p, S):
    c.save()
    cam(c, t, d, p, 'pan_right')
    place, sky = p.get('place', 'rooftop'), p.get('sky', 'sunset')
    draw_place(c, t, place, sky, p)
    hero, friend = S['hero'], S['friend']
    hp, fp = p.get('hero', {'present': True}), p.get('friend', {'present': True})
    hi = ramp(t, p['hi5_at'], p['hi5_at'] + 0.4) if 'hi5_at' in p else 0
    for ex in p.get('extras', []):
        ch_ = dict(KID, **ex.get('look_as', {}))
        ch_.setdefault('hoodie_dark', mix(ch_['hoodie'], '#000000', 0.25))
        person_activity(c, ex['x'], ex.get('y', 900), t + ex['x'] * 0.01, ch_, ex.get('activity', 'idle'),
                        at_time(ex.get('expr', 'neutral'), t), tuple(ex.get('look', (0, 0))), s=ex.get('s', 0.95))
    if p.get('empty_seat'):
        rrect(c, 690, 830, 140, 70, 6, '#7a5236', ow=5)
    if fp.get('present', True):
        fx = fp.get('x', 1120)
        act = fp.get('activity', 'drum')
        if hi > 0:
            draw_person(c, fx, 900, 1.0, friend, 'happy', t, arms=((10, 5), (-120 * hi - 10, -150 * hi - 5)), look=(1, 0))
        else:
            person_activity(c, fx, 900, t, friend, act, at_time(fp.get('expr', 'happy'), t), fp.get('look', (-0.7, 0)))
    if hp.get('present', True):
        act = hp.get('activity', 'guitar')
        hx = hp.get('x', 760)
        walk_ph = None
        if act == 'walk_in':
            k = ease_in_out(t / hp.get('walk_dur', 3.0))
            hx = lerp(hp.get('from_x', 1660), hp.get('x', 1270), k)
            walk_ph = t * 9 if k < 1 else None
            act = 'idle'
        if hi > 0:
            r = draw_person(c, hx, 900, 1.0, hero, 'happy', t, arms=((120 * hi + 10, 150 * hi + 5), (-10, -5)), look=(1, 0))
        else:
            r = person_activity(c, hx, 900, t, hero, act, at_time(hp.get('expr', 'happy'), t), hp.get('look', (0.5, 0)), walk_ph=walk_ph,
                                face_kw=dict(bags=hp.get('bags', 0)) if hp.get('bags') else None)
        if act in ('guitar',) and not hp.get('no_notes'):
            notes(c, t, hx, 560, 5)
        if hp.get('distracted'):
            hx2, hy2 = r['head']
            a = ramp(t, hp.get('distracted_at', 1.0), hp.get('distracted_at', 1.0) + 0.6)
            for bx, by, br in ((hx2 + 70, hy2 - 110, 10), (hx2 + 110, hy2 - 160, 16)):
                circle(c, bx, by, br, '#f4f1ea', INK, ow=3, a=a)
            bx, by = hx2 + 230, hy2 - 300
            rrect(c, bx - 150, by - 90, 300, 180, 60, '#f4f1ea', INK, ow=4, a=a)
            for i in range(4):
                tx, ty = bx - 120 + (i % 2) * 125, by - 66 + (i // 2) * 70
                rrect(c, tx, ty, 115, 60, 10, ['#5f4b8b', '#b56576', '#3d5a80', URGE['glow']][i], None, a=a * 0.85)
        if 'urge' in p:
            u = dict(p['urge'])
            if u.get('on_shoulder'):
                hx2, hy2 = r['head']
                u.setdefault('x', hx2 - 115)
                u.setdefault('y', hy2 + 130)
                u.setdefault('size', 30)
                u.setdefault('say_x', hx2 - 240)
                u.setdefault('say_y', hy2 + 20)
            urge_from(c, t, d, u, 1400, 900)
    elif 'urge' in p:
        urge_from(c, t, d, p['urge'], 1400, 900)
    if 0 < t - p.get('hi5_at', -9) - 0.35 < 0.65:
        k = (t - p['hi5_at'] - 0.35) / 0.65
        cx_ = (hx + p.get('friend', {}).get('x', 1120)) / 2 if hp.get('present', True) else 1000
        for i in range(8):
            ang = i * math.pi / 4
            c.drawLine(cx_ + math.cos(ang) * (30 + 50 * k), 560 + math.sin(ang) * (30 + 50 * k),
                       cx_ + math.cos(ang) * (50 + 70 * k), 560 + math.sin(ang) * (50 + 70 * k), paint('#ffe2a0', 1 - k, stroke=5))
    c.restore()


def t_bedroom(c, t, d, p, S):
    hero = S['hero']
    c.save()
    pose = p.get('pose', 'lying_phone')
    cam(c, t, d, p, 'push', 0.42 if pose.startswith('lying') or pose in ('asleep', 'reach') else 0.5, 0.62)
    light = p.get('light', 'night')
    room(c, t, light)
    if p.get('corner_item'):
        if p.get('corner_glow'):
            glow(c, 1560, 760, 280, '#ffd29a', 0.25 + 0.1 * math.sin(t * 2))
        it = p['corner_item']
        if it == 'guitar':
            draw_guitar(c, 1560, 760, 1.0, -72)
        elif it == 'ball':
            draw_ball(c, 1560, 845, 36)
        elif it == 'camera':
            rrect(c, 1490, 846, 150, 34, 6, '#4a3a30', INK, ow=4)
            draw_camera(c, 1565, 806, 0.9)
        elif it == 'sketchbook':
            draw_sketchbook(c, 1560, 840, 1.0)
        elif it == 'shoes':
            for dx in (0, 70):
                oval(c, 1530 + dx, 862, 34, 16, '#efe9e0', INK, ow=4)
    draw_bed(c)
    draw_clock(c, 320, 668, 1, at_time(p.get('clock', '23:52'), t))
    if p.get('phone_far'):
        rrect(c, 1700, 856, 70, 22, 6, '#15151a', ow=3)
        c.drawLine(1770, 868, 1850, 868, paint('#cfcfd8', stroke=3))
    dg = p.get('drawer_glow', 0)
    if isinstance(dg, list):
        dg = 0.35 + 0.15 * math.sin(t * 4) + 0.6 * ramp(t, dg[0], dg[1])
    if dg:
        draw_drawer_light(c, dg)
    expr = at_time(p.get('expr', 'bored'), t)
    look = tuple(p.get('look', (0.5, -0.7)))
    fkw = dict(bags=p.get('bags')) if p.get('bags') is not None else {}
    sweat = math.sin(t * 2) if p.get('sweat') else None
    phone_col = p.get('phone_color', '#8fb4ff')
    if pose in ('lying_phone', 'lying_awake', 'asleep', 'reach'):
        on = 1.0 if pose == 'lying_phone' else 0.0
        if on:
            glow(c, 700, 650, 330, phone_col, 0.28)
        draw_head(c, 676, 654, 64, hero, 'asleep' if pose == 'asleep' and expr == 'bored' else expr, t, look=look,
                  blink=blink_at(t, 3.6), sweat=sweat, extra=fkw)
        draw_blanket(c, colr=p.get('blanket', '#3d4f86'))
        if on:
            draw_phone_small(c, 790, 610, 1.15, phone_col, 1.0, -18)
            circle(c, 772, 640, 15, hero['skin'], ow=4)
            circle(c, 808, 628, 15, hero['skin'], ow=4)
        if pose == 'reach' and t > p.get('reach_at', d * 0.6):
            k = ease_out((t - p.get('reach_at', d * 0.6)) / 0.9)
            limb(c, [(700, 712), (lerp(700, 560, k), 740), (lerp(700, 470, k), lerp(740, 790, k))], 26, hero['hoodie'], ow=5)
            circle(c, lerp(700, 470, k), lerp(740, 790, k), 15, hero['skin'], ow=4)
        if p.get('zzz'):
            for i in range(3):
                ph = (t * 0.5 + i / 3) % 1
                text(c, 'z', 760 + ph * 70 + i * 6, 590 - ph * 120, 34 + i * 8, '#cfd9ff', a=math.sin(ph * math.pi), shadow=False)
    elif pose in ('sitting', 'sitting_phone', 'sitting_activity'):
        draw_blanket(c, bump=0.5, colr=p.get('blanket', '#3d4f86'))
        act = 'sit'
        if pose == 'sitting_activity':
            act = p.get('activity', 'guitar')
        r = person_activity(c, 900, 900 if act == 'sit' else 880, t, hero, act, expr, look, pose='sit', face_kw=fkw or None)
        if pose == 'sitting_phone':
            hx, hy = r['hands'][0]
            glow(c, 900, 700, 300, phone_col, 0.3)
            draw_phone_small(c, 900, 760, 1.0, phone_col, 1.0, 0)
        if act == 'guitar':
            notes(c, t, 900, 560, 3, a=0.8)
    elif pose == 'standing':
        draw_blanket(c, bump=0.5, colr=p.get('blanket', '#3d4f86'))
        reach = 0.0
        if 'put_away' in p:
            a0, a1 = p['put_away']
            op = window(t, a0, a1, 0.5)
            rrect(c, 312, 812, 166 + 60 * op, 58, 6, '#34323d', '#55526a', ow=4)
            reach = window(t, a0, a1, 0.7)
        r = draw_person(c, p.get('x', 640), 900, 1.05, hero, expr, t, arms=((-35 - 25 * reach, -10 - 50 * reach), (-10, -5)),
                        look=look, blink=blink_at(t, 3.0, 0.4), face_kw=fkw or None)
        if 'put_away' in p and t < (p['put_away'][0] + p['put_away'][1]) / 2:
            hx, hy = r['hands'][0]
            draw_phone_small(c, hx - 4, hy + 4, 0.9, phone_col, 0.0, 10)
    else:  # empty
        draw_blanket(c, bump=0.2, colr=p.get('blanket', '#3d4f86'))
    if 'urge' in p:
        urge_from(c, t, d, p['urge'], 1150, 760)
    c.restore()
    if p.get('label') and not S.get('short'):
        text(c, p['label'], 90, 140, 64, '#f3ede2', tf=TF_BOLD, align='left', a=ramp(t, 0.05, 0.4))


_bg_cache = {}


def blurred_bg(S, sigma=18, dim=0.35):
    key = ('bed', S['hero']['hoodie'])
    if key not in _bg_cache:
        s = skia.Surface(W, H)
        cc = s.getCanvas()
        draw_bedroom(cc, 0)
        draw_bed(cc)
        draw_clock(cc, 320, 668, 1, '00:41')
        draw_blanket(cc)
        img = s.makeImageSnapshot()
        s2 = skia.Surface(W, H)
        c2 = s2.getCanvas()
        c2.drawImage(img, 0, 0, skia.SamplingOptions(), skia.Paint(ImageFilter=skia.ImageFilters.Blur(sigma, sigma)))
        c2.drawRect(skia.Rect.MakeWH(W, H), paint('#000000', dim))
        _bg_cache[key] = s2.makeImageSnapshot()
    return _bg_cache[key]


PH_W, PH_H = 500, 940


def phone_big(c, t, S, content, glow_col='#9ab8ff', glow_a=0.35, thumb=None):
    hero = S['hero']
    cx, cy = 960, 600
    c.save()
    c.translate(cx, cy)
    c.rotate(-3)
    glow(c, 0, 0, 760, glow_col, glow_a)
    rrect(c, -PH_W / 2, -PH_H / 2, PH_W, PH_H, 56, '#16161b', '#05050a', ow=8)
    sw, sh = PH_W - 40, PH_H - 60
    c.save()
    rect = skia.Rect.MakeXYWH(-sw / 2, -sh / 2, sw, sh)
    c.clipRRect(skia.RRect.MakeRectXY(rect, 40, 40), True)
    c.translate(-sw / 2, -sh / 2)
    content(c, t, sw, sh)
    c.restore()
    rrect(c, -60, -PH_H / 2 + 22, 120, 26, 13, '#0a0a0e', None)
    c.restore()
    sk = hero['skin']
    for side in (-1, 1):
        pth = skia.Path()
        bx = cx + side * 250
        pth.moveTo(bx + side * 160, H + 40)
        pth.cubicTo(bx + side * 140, 860, bx + side * 40, 760, bx - side * 10, 720)
        pth.cubicTo(bx - side * 40, 700, bx - side * 70, 760, bx - side * 50, 820)
        pth.cubicTo(bx - side * 40, 900, bx - side * 60, 1000, bx - side * 80, H + 40)
        pth.close()
        c.drawPath(pth, paint(sk)); c.drawPath(pth, paint(INK, stroke=6))
        sp = skia.Path()
        sp.moveTo(bx + side * 210, H + 40); sp.lineTo(bx + side * 170, 960); sp.lineTo(bx - side * 80, 990)
        sp.lineTo(bx - side * 110, H + 40); sp.close()
        c.drawPath(sp, paint(hero['hoodie'])); c.drawPath(sp, paint(INK, stroke=6))
    if thumb:
        tx, ty, press = thumb
        pth = skia.Path()
        pth.moveTo(cx + 420, H + 40)
        pth.cubicTo(cx + 380, 900, tx + 60, ty + 120, tx + 6, ty + 18)
        pth.cubicTo(tx - 30, ty - 20, tx - 50, ty + 30, tx - 30, ty + 70)
        pth.cubicTo(tx - 10, ty + 180, cx + 200, 960, cx + 230, H + 40)
        pth.close()
        c.drawPath(pth, paint(sk)); c.drawPath(pth, paint(INK, stroke=6))
        if press > 0:
            circle(c, tx - 10, ty + 10, 30 + 60 * press, '#ffffff', None, a=0.35 * (1 - press))


def status_bar(c, sw, hhmm):
    text(c, hhmm, 40, 44, 26, '#e8e8ee', tf=TF_UI, align='left', shadow=False)
    rrect(c, sw - 80, 26, 40, 18, 5, '#e8e8ee', None, a=0.8)


def t_phone_feed(c, t, d, p, S):
    c.drawImage(blurred_bg(S), 0, 0)
    tap = p.get('tap_at', d - 2.0)
    scroll = 1200 * ease_out(t / 3.4) + 140 * t
    scroll = min(scroll, 1690) if t > 3 else scroll
    pulse = ramp(t, tap - 2.4, tap - 1.8)
    press = clamp01((t - tap) / 0.4) if t > tap else 0
    flash = 0.6 * (1 - ramp(t, tap + 0.15, tap + 1.2)) if t > tap + 0.15 else 0
    tx = lerp(1180, 980, ease_in_out((t - (tap - 1.4)) / 1.3))
    ty = lerp(900, 640, ease_in_out((t - (tap - 1.4)) / 1.3))
    special = p.get('special_color', URGE['glow'])
    clock = p.get('clock', '00:07')

    def content(cc, tt, sw, sh):
        cc.drawRect(skia.Rect.MakeWH(sw, sh), paint('#111117'))
        y0 = 110 - scroll
        rnd = random.Random(11)
        pal = [('#3d5a80', '#98c1d9'), ('#5f4b8b', '#e69a8d'), ('#2a6f6f', '#e9c46a'), ('#6d597a', '#b56576'),
               ('#264653', '#f4a261'), ('#4a4e69', '#c9ada7')]
        for i in range(14):
            ty_ = y0 + i * 300
            sp = i == 6
            a_col, b_col = pal[i % len(pal)]
            if sp:
                a_col, b_col = mix(special, '#000000', 0.7), special
            if ty_ > sh + 20 or ty_ < -320:
                rnd.random(); rnd.random()
                continue
            rect = skia.Rect.MakeXYWH(24, ty_, sw - 48, 200)
            cc.save()
            cc.clipRRect(skia.RRect.MakeRectXY(rect, 18, 18), True)
            cc.drawRect(rect, paint(shader=lin_grad((24, ty_), (sw, ty_ + 200), [a_col, b_col])))
            for k in range(3):
                cc.drawCircle(60 + rnd.random() * (sw - 120), ty_ + 40 + rnd.random() * 120, 50 + rnd.random() * 40,
                              paint(b_col if k % 2 else a_col, 0.8, blur=26))
            cc.restore()
            if sp:
                pa = 0.5 + 0.5 * math.sin(tt * 9)
                cc.drawRoundRect(rect, 18, 18, paint(special, pulse * (0.4 + 0.6 * pa), stroke=6))
                glow(cc, sw / 2, ty_ + 100, 300, special, 0.35 * pulse)
            tri = skia.Path()
            tri.moveTo(sw / 2 - 18, ty_ + 76); tri.lineTo(sw / 2 + 26, ty_ + 100); tri.lineTo(sw / 2 - 18, ty_ + 124); tri.close()
            circle(cc, sw / 2 + 2, ty_ + 100, 42, '#000000', None, a=0.35)
            cc.drawPath(tri, paint('#ffffff', 0.9))
            rrect(cc, 24, ty_ + 216, sw * 0.62, 18, 9, '#3a3a44', None)
            rrect(cc, 24, ty_ + 246, sw * 0.38, 14, 7, '#2a2a33', None)
        cc.drawRect(skia.Rect.MakeWH(sw, 96), paint('#111117', 0.96))
        status_bar(cc, sw, clock)
        rrect(cc, 24, 58, sw - 48, 30, 15, '#24242c', None)
        if flash > 0:
            cc.drawRect(skia.Rect.MakeWH(sw, sh), paint(special, flash))
    phone_big(c, t, S, content, glow_col=special if t > tap else '#9ab8ff', glow_a=0.35 + 0.3 * flash, thumb=(tx, ty, press))


def t_phone_chat(c, t, d, p, S):
    c.drawImage(blurred_bg(S), 0, 0)
    msgs = p.get('messages', [])
    typing = p.get('typing')
    seen = p.get('seen_at')
    name = p.get('contact', 'Dev')
    av = p.get('avatar', 'friend')
    if isinstance(av, dict):
        avatar = dict(KID, **av)
    else:
        avatar = S['friend'] if av == 'friend' else S.get(av, S['friend'])
    clock = p.get('clock', '18:02')

    def content(cc, tt, sw, sh):
        cc.drawRect(skia.Rect.MakeWH(sw, sh), paint('#0f1016'))
        cc.drawRect(skia.Rect.MakeWH(sw, 150), paint('#171823'))
        status_bar(cc, sw, clock)
        cc.drawLine(30, 105, 46, 92, paint('#8fa0ff', stroke=5))
        cc.drawLine(30, 105, 46, 118, paint('#8fa0ff', stroke=5))
        draw_head(cc, 100, 106, 28, avatar, 'smile', tt, blink=blink_at(tt, 3.2))
        text(cc, name, 146, 116, 34, '#f0f0f5', tf=TF_UI, align='left', shadow=False)
        y = 190
        f = font(TF_UI, 28)
        for (ta, side, s) in msgs:
            if tt < ta:
                break
            k = ease_out((tt - ta) / 0.3)
            tw = f.measureText(s)
            bw, bh = min(tw + 44, sw - 40), 62
            bx = 22 if side == 'L' else sw - 22 - bw
            rrect(cc, bx, y + (1 - k) * 20, bw, bh, 26, '#2a2c3a' if side == 'L' else '#3b6cf6', None, a=k)
            cc.drawString(s, bx + 22, y + (1 - k) * 20 + 41, f, paint('#ffffff', k))
            y += bh + 16
        if typing and typing[0] <= tt < typing[1]:
            side = typing[2]
            bx = 22 if side == 'L' else sw - 22 - 110
            rrect(cc, bx, y, 110, 56, 26, '#2a2c3a' if side == 'L' else '#3b6cf6', None)
            for i in range(3):
                ph = math.sin(tt * 8 - i * 0.9)
                circle(cc, bx + 32 + i * 23, y + 28 - 4 * max(0, ph), 7, '#cfd3e6', None, a=0.6 + 0.4 * max(0, ph))
        if seen is not None and tt >= seen:
            text(cc, 'Seen', sw - 30, y + 6, 22, '#7d8193', tf=TF_UI, align='right', shadow=False, a=ramp(tt, seen, seen + .3))
        rrect(cc, 22, sh - 92, sw - 44, 60, 30, '#1d1e29', '#2c2e3d', ow=3)
        text(cc, 'message...', 52, sh - 52, 26, '#5d6175', tf=TF_UI, align='left', shadow=False)
    phone_big(c, t, S, content, glow_col=p.get('glow', '#9ab8ff'), glow_a=0.25)


def t_face(c, t, d, p, S):
    hero = S['hero']
    c.save()
    cam(c, t, d, p, 'push', 0.5, 0.42)
    bg = p.get('bg', 'bedroom')
    if bg == 'bedroom':
        c.drawImage(blurred_bg(S), 0, 0)
    elif bg == 'warm':
        c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=rad_grad((W / 2, H * 0.4), 1200, ['#5a3a2a', '#1a1014'])))
    else:
        c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=rad_grad((W / 2, H * 0.4), 1200, ['#1e2236', '#07080d'])))
    sw = math.sin(t * 0.7) * 6
    expr = at_time(p.get('expr', 'neutral'), t)
    tear_at = p.get('tear_at')
    fkw = dict(bags=p.get('bags', 0.0), tear=((t - tear_at) / 3.0) if tear_at is not None and t > tear_at else None,
               pupil_glow=p.get('pupil_glow'), sweat=math.sin(t * 2) if p.get('sweat') else None)
    r = draw_person(c, 960 + sw, 1560, 3.1, hero, expr, t, arms=((8, 4), (-8, -4)), look=tuple(p.get('look', (0, 0.3))),
                    blink=blink_at(t, 3.0, 0.7), face_kw=fkw)
    g = p.get('glow')
    if g:
        amt = p.get('glow_amt', 0.4) * (0.75 + 0.25 * math.sin(t * 5) if p.get('pulse') else 1) * ramp(t, 0, 0.8)
        gp = paint(shader=rad_grad((960, r['head'][1] + 200), 700, [(g, amt), (g, amt * 0.4), (g, 0)], [0, 0.5, 1]))
        gp.setBlendMode(skia.BlendMode.kScreen)
        c.drawRect(skia.Rect.MakeWH(W, H), gp)
    if p.get('sparkles'):
        hx, hy = r['head']
        rnd = random.Random(3)
        for i in range(18):
            ph = (t * 0.6 + rnd.random()) % 1
            ang = rnd.random() * math.tau
            dist = 260 + ph * 380
            sx, sy = hx + math.cos(ang) * dist, hy + math.sin(ang) * dist * 0.7
            a = math.sin(ph * math.pi) * ramp(t, 0.6, 1.4)
            sz = 6 + rnd.random() * 10
            colr = rnd.choice(['#ffd36a', URGE['say'], '#ffffff'])
            pth = skia.Path()
            for k in range(8):
                rr = sz if k % 2 == 0 else sz * 0.35
                th = k * math.pi / 4 + t
                (pth.moveTo if k == 0 else pth.lineTo)(sx + math.cos(th) * rr, sy + math.sin(th) * rr)
            pth.close()
            c.drawPath(pth, paint(colr, a))
    c.restore()


def t_mirror(c, t, d, p, S):
    hero = S['hero']
    c.save()
    cam(c, t, d, p, 'push', 0.5, 0.45)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(p.get('wall', '#2f454c')))
    for x in range(0, W, 90):
        c.drawLine(x, 0, x, H, paint(mix(p.get('wall', '#2f454c'), '#000000', 0.2), stroke=4))
    for y in range(0, H, 90):
        c.drawLine(0, y, W, y, paint(mix(p.get('wall', '#2f454c'), '#000000', 0.2), stroke=4))
    glow(c, 200, 200, 700, '#dfe9ff', 0.18)
    mx, my, mw, mh = 560, 110, 800, 660
    rrect(c, mx - 18, my - 18, mw + 36, mh + 36, 30, '#c9c2b4', INK, ow=6)
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(mx, my, mw, mh), 18, 18), True)
    c.drawRect(skia.Rect.MakeXYWH(mx, my, mw, mh), paint('#3c5560'))
    if p.get('urge_at') is not None:
        ua = ramp(t, p['urge_at'], p['urge_at'] + 1.6)
        draw_urge(c, 1230, my + mh + 40, p.get('urge_size', 260), t, eye=ua, a=ua, look=(-0.8, 0.4))
    draw_person(c, 950, 1150, 2.0, hero, at_time(p.get('expr', 'tired'), t), t, arms=((6, 3), (-6, -3)), look=(0, 0.1),
                blink=blink_at(t, 3.1), face_kw=dict(bags=p.get('bags', 1.0)))
    c.drawRect(skia.Rect.MakeXYWH(mx, my, mw, mh), paint('#a9c4d6', 0.12))
    c.restore()
    rrect(c, 300, 820, 1320, 300, 20, '#d8d2c4', INK, ow=6)
    oval(c, 960, 860, 220, 34, '#9fa9ad', INK, ow=5)
    rrect(c, 940, 770, 40, 70, 10, '#b8c0c4', INK, ow=5)
    rrect(c, 900, 760, 120, 26, 12, '#b8c0c4', INK, ow=5)
    c.restore()


def t_desk(c, t, d, p, S):
    """Hero at a desk with a laptop. screen: work|feed|game|dark."""
    hero = S['hero']
    c.save()
    cam(c, t, d, p, 'push', 0.5, 0.55)
    room(c, t, p.get('light', 'lamp'))
    # wall clock + sticky note
    circle(c, 600, 240, 70, '#e9e4d8', INK, ow=6)
    ang = (t * 6) % 360
    c.drawLine(600, 240, 600 + 40 * math.sin(math.radians(ang)), 240 - 40 * math.cos(math.radians(ang)), paint(INK, stroke=5))
    c.drawLine(600, 240, 625, 225, paint(INK, stroke=7))
    if p.get('note'):
        c.save(); c.rotate(4, 1180, 300)
        rrect(c, 1100, 230, 170, 150, 4, '#ffe066', INK, ow=4)
        text(c, p['note'], 1185, 320, 38, '#c8423b', shadow=False, tf=TF_BOLD)
        c.restore()
    pose = p.get('pose', 'staring')
    expr = at_time(p.get('expr', 'neutral'), t)
    fkw = dict(bags=p.get('bags', 0.0))
    tilt = -14 if pose == 'head_down' else 0
    if pose == 'typing':
        k = math.sin(t * 14) * 4
        arms = ((40, 80 + k), (75, 95 - k))
    elif pose == 'head_down':
        arms = ((-50, -100), (50, 100))
    else:
        arms = ((30, 70), (70, 90))
    draw_person(c, 800, 960 + (40 if pose == 'head_down' else 0), 1.1, hero, expr, t, pose='sit', arms=arms, look=(0.8, 0.5),
                blink=blink_at(t, 3.2), head_tilt=tilt, face_kw=fkw)
    # desk in front
    rrect(c, 380, 820, 1160, 60, 10, '#7a5236', INK, ow=6)
    c.drawRect(skia.Rect.MakeLTRB(420, 880, 460, H), paint('#5a3a26'))
    c.drawRect(skia.Rect.MakeLTRB(1460, 880, 1500, H), paint('#5a3a26'))
    if p.get('papers'):
        for i in range(int(p['papers'])):
            rrect(c, 520 + i * 6, 800 - i * 14, 160, 16, 3, '#f2efe6', INK, ow=3)
    screen = p.get('screen', 'work')
    col_ = {'work': '#9ab8ff', 'feed': URGE['glow'], 'game': '#7fe0a0', 'dark': '#222222'}.get(screen, '#9ab8ff')
    c.save()
    c.translate(0, 0)
    draw_laptop(c, 1180, 840, 1.1, col_, 0.0 if screen == 'dark' else 1.0, screen, t)
    c.restore()
    if 'urge' in p:
        urge_from(c, t, d, p['urge'], 1520, 820)
    c.restore()
    if p.get('label') and not S.get('short'):
        text(c, p['label'], 90, 140, 64, '#f3ede2', tf=TF_BOLD, align='left', a=ramp(t, 0.05, 0.4))


def t_montage(c, t, d, p, S):
    shots = p['shots']
    total = sum(s['dur'] for s in shots)
    scale = d / total
    acc = 0.0
    for s in shots:
        sd = s['dur'] * scale
        if t < acc + sd or s is shots[-1]:
            lt = t - acc
            sp = dict(s.get('params', {}))
            if s.get('label'):
                sp['label'] = s['label']
            TEMPLATES[s['template']](c, lt, sd, sp, S)
            if s.get('label') and s['template'] not in ('bedroom', 'desk') and not S.get('short'):
                text(c, s['label'], 90, 140, 64, '#f3ede2', tf=TF_BOLD, align='left', a=ramp(lt, 0.05, 0.4))
            if lt < 0.12 and acc > 0:
                c.drawRect(skia.Rect.MakeWH(W, H), paint('#000000', 1 - lt / 0.12))
            return
        acc += sd


def crowd(c, t, cheer_at=None, colors=('#0d0a10', '#070509')):
    rnd = random.Random(8)
    for row, (yb, sc, colr) in enumerate([(1040, 1.0, colors[0]), (1110, 1.25, colors[1])]):
        x = -40 + row * 60
        while x < W + 80:
            boost = 1 + (ramp(t, cheer_at, cheer_at + 0.8) if cheer_at is not None else 0)
            bob = math.sin(t * (2.2 + rnd.random()) + x) * 6 * boost
            sz = rnd.uniform(0.85, 1.15) * sc
            hy = yb - 150 * sz + bob
            rrect(c, x - 70 * sz, hy + 60 * sz, 140 * sz, 200 * sz, 60 * sz, colr, None)
            circle(c, x, hy, 52 * sz, colr, None)
            c.drawCircle(x, hy, 52 * sz, paint('#ffd9a0', 0.12, stroke=3))
            if cheer_at is not None and t > cheer_at and rnd.random() < 0.4:
                ah = ramp(t, cheer_at + rnd.random() * 0.4, cheer_at + 0.6)
                limb(c, [(x + 50 * sz, hy + 90 * sz), (x + 80 * sz, hy + 90 * sz - 120 * sz * ah)], 26 * sz, colr, None)
            x += rnd.uniform(150, 210) * sc


def t_stage(c, t, d, p, S):
    hero, friend = S['hero'], S['friend']
    c.save()
    cam(c, t, d, p, 'push', 0.5, 0.5)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=lin_grad((0, 0), (0, H), ['#140f16', '#24161e'])))
    for y in range(40, 760, 54):
        off = 0 if (y // 54) % 2 else 60
        for x in range(-60 + off, W, 120):
            rrect(c, x, y, 112, 46, 4, '#1d151c', None)
    for i in range(30):
        bx, by = 40 + i * 64, 90 + 30 * math.sin(i * 0.7)
        glow(c, bx, by, 30, '#ffcf6a', 0.4 * (0.7 + 0.3 * math.sin(t * 3 + i)))
        circle(c, bx, by, 5, '#ffe6a6', None)
    if p.get('banner'):
        rrect(c, 660, 150, 600, 90, 10, '#c8423b', INK, ow=5)
        text(c, p['banner'], 960, 212, 52, '#fff3d6', tf=TF_BOLD, shadow=False)
    rrect(c, 260, 780, 1400, 90, 6, '#3a2620', INK, ow=6)
    sp = skia.Path()
    sp.moveTo(860, -40); sp.lineTo(1060, -40); sp.lineTo(1340, 830); sp.lineTo(580, 830); sp.close()
    c.drawPath(sp, paint(shader=lin_grad((960, 0), (960, 830), [('#fff3d6', 0.04), ('#fff3d6', 0.22)]), blur=10))
    oval(c, 960, 800, 420, 50, '#fff3d6', a=0.25)
    act = p.get('activity', 'guitar')
    if p.get('friend', True):
        rrect(c, 1180, 650, 120, 150, 8, '#a26a3c', INK, ow=5)
        circle(c, 1240, 725, 26, '#3a2416', INK, ow=4)
        k = math.sin(t * 7.0)
        draw_person(c, 1240, 690, 0.95, friend, 'happy', t, pose='sit',
                    arms=((-5 + 15 * k, 40 + 25 * k), (5 - 15 * k, -40 - 25 * k)), look=(-0.6, 0), blink=blink_at(t, 3.0))
    if act == 'guitar':
        rrect(c, 830, 690, 120, 18, 8, '#5a3a2a', INK, ow=4)
        c.drawLine(850, 700, 840, 790, paint('#5a3a2a', stroke=10))
        c.drawLine(930, 700, 940, 790, paint('#5a3a2a', stroke=10))
        c.drawLine(700, 790, 700, 560, paint('#2a2a2e', stroke=8))
        c.drawLine(700, 560, 780, 520, paint('#2a2a2e', stroke=7))
        oval(c, 790, 515, 16, 22, '#3a3a40', INK, ow=3)
        person_activity(c, 890, 760, t, hero, 'guitar', 'calm' if t < d * 0.6 else 'happy', (0, 0), s=0.95, pose='sit')
        notes(c, t, 900, 380, 6, seed=5, spread=400)
    else:  # speech / award / sing: hero standing at mic
        c.drawLine(900, 790, 900, 560, paint('#2a2a2e', stroke=8))
        oval(c, 900, 545, 18, 24, '#3a3a40', INK, ow=3)
        person_activity(c, 960, 790, t, hero, 'wave' if t > d * 0.6 else 'idle', 'happy', (0, 0), s=1.0)
    crowd(c, t, p.get('cheer_at'))
    c.restore()


def t_gallery(c, t, d, p, S):
    """Payoff for creative goals: hero next to their framed work, people admiring."""
    hero, friend = S['hero'], S['friend']
    c.save()
    cam(c, t, d, p, 'push', 0.5, 0.5)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=lin_grad((0, 0), (0, H), ['#efe6d6', '#d9cdb8'])))
    c.drawRect(skia.Rect.MakeLTRB(0, 860, W, H), paint('#8a6a4a'))
    c.drawLine(0, 860, W, 860, paint(INK, stroke=5))
    rnd = random.Random(p.get('seed', 3))
    for (fx, fy, fw, fh) in ((200, 260, 260, 200), (1460, 240, 280, 220)):
        rrect(c, fx, fy, fw, fh, 4, '#3a2a20', INK, ow=6)
        c.drawRect(skia.Rect.MakeXYWH(fx + 16, fy + 16, fw - 32, fh - 32), paint(rnd.choice(['#9cc3e6', '#e9c46a', '#b56576'])))
    # the hero's piece, spotlit
    glow(c, 960, 380, 420, '#fff3d6', 0.5)
    rrect(c, 760, 180, 400, 320, 6, '#c9a14a', INK, ow=8)
    c.drawRect(skia.Rect.MakeXYWH(790, 210, 340, 260), paint(shader=lin_grad((790, 210), (1130, 470), ['#3b2b55', '#f39a5b'])))
    circle(c, 1040, 300, 40, '#ffe2a0', None)
    c.drawRect(skia.Rect.MakeXYWH(790, 380, 340, 90), paint('#2b1d38'))
    rrect(c, 900, 520, 120, 40, 4, '#f6f1e6', INK, ow=3)
    text(c, p.get('plaque', 'by me'), 960, 548, 22, '#2a2a2a', shadow=False)
    person_activity(c, 1230, 870, t, hero, 'wave' if t > d * 0.5 else 'idle', 'happy', (-0.5, 0))
    if p.get('friend', True):
        person_activity(c, 640, 870, t, friend, 'idle', 'happy', (0.6, 0))
    crowd(c, t, p.get('cheer_at'), colors=('#5a4a44', '#3a2e2a'))
    c.restore()


def t_sunrise(c, t, d, p, S):
    hero, friend = S['hero'], S['friend']
    c.save()
    cam(c, t, d, p, 'push_slow', 0.5, 0.6)
    k = ease_out(t / d)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=lin_grad((0, 0), (0, 860), ['#3a4a86', mix('#c99bb0', '#ffcf9a', k), '#ffd9a6'],
                                                         [0, 0.6, 1])))
    sy = lerp(900, 640, k)
    glow(c, 960, sy, 700, '#ffd9a0', 0.55)
    circle(c, 960, sy, 110, '#ffe6b8', None)
    c.drawCircle(500, 1500, 900, paint('#3a4a5e'))
    c.drawCircle(1500, 1560, 1000, paint('#2f3d50'))
    c.drawRect(skia.Rect.MakeLTRB(0, 900, W, H), paint('#28354a'))
    person_activity(c, 860, 900, t, hero, p.get('activity', 'sit'), 'calm', (0.3, -0.3), pose='sit')
    if p.get('friend', False):
        person_activity(c, 1080, 900, t, friend, 'sit', 'smile', (-0.3, -0.3), pose='sit')
    c.restore()


def t_end_card(c, t, d, p, S):
    c.clear(col('#07060a'))
    a = window(t, 0.3, d - 0.1, 0.7)
    if p.get('sprout', True):
        g = ease_out((t - 0.2) / 2.2)
        stem = skia.Path()
        stem.moveTo(960, 760); stem.quadTo(950, 760 - 60 * g, 962, 760 - 120 * g)
        c.drawPath(stem, paint('#7cc46a', a, stroke=7))
        for side in (-1, 1):
            lk = ease_out((t - 1.0) / 1.2)
            if lk > 0:
                lp_ = skia.Path()
                bx, by = 962, 760 - 115 * g
                lp_.moveTo(bx, by)
                lp_.quadTo(bx + side * 40 * lk, by - 45 * lk, bx + side * 70 * lk, by - 20 * lk)
                lp_.quadTo(bx + side * 30 * lk, by + 4 * lk, bx, by)
                c.drawPath(lp_, paint('#8fd47a', a))
        oval(c, 960, 768, 90, 14, '#3a2a20', a=a)
    text(c, p['text'], W / 2, 470, p.get('size', 84), '#f3ede2', a=a)


def t_outro(c, t, d, p, S):
    hero = S['hero']
    cfg = S.get('config', {})
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=rad_grad((W / 2, H * 0.75), 1100, ['#2a1c22', '#120d12'])))
    a = ramp(t, 0.2, 0.8)
    text(c, cfg.get('outro_line', 'If this helped, like, share & subscribe.'), W / 2, 230, 64, '#f3ede2', a=a)
    if cfg.get('channel_name'):
        text(c, cfg['channel_name'], W / 2, 310, 40, '#bdb6aa', a=a)
    bx, by = W / 2, 380
    liked, subbed = t > 2.6, t > 5.0
    lx = bx - 420
    rrect(c, lx, by, 230, 86, 43, '#3b6cf6' if liked else '#2b2b33', None, a=a)
    _thumb_icon(c, lx + 62, by + 43, '#ffffff', a)
    text(c, 'LIKE', lx + 150, by + 56, 38, '#ffffff', tf=TF_UI, a=a, shadow=False)
    sx = bx - 160
    rrect(c, sx, by, 250, 86, 43, '#2b2b33' if t < 3.8 else '#3a3a46', None, a=a)
    _share_icon(c, sx + 62, by + 43, '#ffffff', a)
    text(c, 'SHARE', sx + 160, by + 56, 38, '#ffffff', tf=TF_UI, a=a, shadow=False)
    ux = bx + 120
    pop = 1 + 0.08 * math.sin(clamp01((t - 5.0) / 0.3) * math.pi)
    c.save(); c.translate(ux + 150, by + 43); c.scale(pop, pop)
    rrect(c, -150, -43, 300, 86, 43, '#e0322d' if not subbed else '#3a3a46', None, a=a)
    text(c, 'SUBSCRIBED' if subbed else 'SUBSCRIBE', 0, 13, 36, '#ffffff', tf=TF_UI, a=a, shadow=False)
    c.restore()
    if t > 5.6:
        _bell_icon(c, ux + 340, by + 43, '#ffd36a', a * ramp(t, 5.6, 6.0), math.sin(t * 18) * 14 * (1 - ramp(t, 6.0, 7.0)))
    pts = [(0.0, (1500, 900)), (1.8, (lx + 120, by + 50)), (3.2, (sx + 130, by + 50)), (4.4, (ux + 150, by + 50)),
           (5.8, (ux + 340, by + 50)), (d, (ux + 360, by + 140))]
    cx_, cy_ = pts[-1][1]
    for i in range(len(pts) - 1):
        (t0, p0), (t1, p1) = pts[i], pts[i + 1]
        if t0 <= t <= t1:
            u = ease_in_out((t - t0) / max(0.01, t1 - t0 - 0.4))
            cx_, cy_ = lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u)
            break
    click = any(abs(t - tc) < 0.12 for tc in (2.5, 3.7, 4.9, 6.3))
    _cursor(c, cx_, cy_, 0.85 if click else 1.0, a)
    person_activity(c, W / 2, 1110, t, hero, 'wave', 'happy', (0, -0.2), s=1.25)


def _thumb_icon(c, x, y, colr, a):
    rrect(c, x - 24, y - 6, 12, 30, 3, colr, None, a=a)
    p = skia.Path()
    p.moveTo(x - 8, y - 4); p.lineTo(x + 2, y - 26); p.quadTo(x + 12, y - 26, x + 10, y - 12); p.lineTo(x + 26, y - 10)
    p.quadTo(x + 32, y - 6, x + 28, y + 2); p.lineTo(x + 22, y + 22); p.quadTo(x + 20, y + 26, x + 14, y + 26)
    p.lineTo(x - 8, y + 26); p.close()
    c.drawPath(p, paint(colr, a))


def _share_icon(c, x, y, colr, a):
    p = skia.Path()
    p.moveTo(x + 22, y - 6); p.lineTo(x + 2, y - 26); p.lineTo(x + 2, y - 15); p.quadTo(x - 26, y - 10, x - 26, y + 24)
    p.quadTo(x - 14, y + 2, x + 2, y + 3); p.lineTo(x + 2, y + 14); p.close()
    c.drawPath(p, paint(colr, a))


def _bell_icon(c, x, y, colr, a, wiggle=0):
    c.save(); c.rotate(wiggle, x, y - 30)
    p = skia.Path()
    p.moveTo(x - 26, y + 16); p.quadTo(x - 22, y - 30, x, y - 32); p.quadTo(x + 22, y - 30, x + 26, y + 16); p.close()
    c.drawPath(p, paint(colr, a))
    circle(c, x, y + 22, 7, colr, None, a=a)
    c.restore()


def _cursor(c, x, y, s, a):
    p = skia.Path()
    p.moveTo(x, y); p.lineTo(x, y + 46 * s); p.lineTo(x + 12 * s, y + 35 * s); p.lineTo(x + 22 * s, y + 56 * s)
    p.lineTo(x + 30 * s, y + 52 * s); p.lineTo(x + 20 * s, y + 32 * s); p.lineTo(x + 36 * s, y + 32 * s); p.close()
    c.drawPath(p, paint('#ffffff', a)); c.drawPath(p, paint('#000000', a, stroke=3))


def draw_thoughts(c, t, thoughts):
    """Thought bubbles: [{"t": 0.5, "until": 3, "x": 900, "y": 300, "text": "...", "to": [x, y], "size": 34}]"""
    for th in thoughts:
        if not (th.get('t', 0) <= t <= th.get('until', 999)):
            continue
        k = ease_out((t - th.get('t', 0)) / 0.25) * (1 - ramp(t, th.get('until', 999) - 0.2, th.get('until', 999)))
        size = th.get('size', 34)
        w = measure(th['text'], size) + 48
        h = size * 1.6
        x, y = th['x'], th['y']
        c.save()
        c.translate(x, y); c.scale(0.6 + 0.4 * k, 0.6 + 0.4 * k); c.translate(-x, -y)
        if th.get('to'):
            tx, ty = th['to']
            for i, rr in enumerate((12, 8)):
                u = 0.45 + 0.25 * i
                circle(c, lerp(x, tx, u), lerp(y + h / 2, ty, u), rr, '#f8f5ee', INK, ow=3, a=k)
        rrect(c, x - w / 2, y - h / 2, w, h, h / 2, th.get('fill', '#f8f5ee'), INK, ow=4, a=k)
        text(c, th['text'], x, y + size * 0.35, size, th.get('color', '#2a2630'), a=k, shadow=False)
        c.restore()


def draw_spotlight(c, t, sp):
    """Darken everything except a cone of light on x: {"x": 760, "from": 0, "dim": 0.6}"""
    a = sp.get('dim', 0.62) * ramp(t, sp.get('from', 0), sp.get('from', 0) + 0.4)
    if a <= 0:
        return
    x = sp['x']
    cone = skia.Path()
    cone.moveTo(x - 50, -60); cone.lineTo(x + 50, -60); cone.lineTo(x + 190, 960); cone.lineTo(x - 190, 960); cone.close()
    full = skia.Path()
    full.addRect(skia.Rect.MakeLTRB(-400, -400, W + 400, H + 400))
    dark = skia.Op(full, cone, skia.PathOp.kDifference_PathOp)
    c.drawPath(dark, paint('#05040a', a, blur=14))
    c.drawPath(cone, paint('#fff3d6', 0.12 * a / 0.62, blur=10))
    oval(c, x, 905, 190, 30, '#fff3d6', a=0.25 * a / 0.62)


def _wrap(fn):
    def run(c, t, d, p, S):
        if S.get('short') and p.get('camera', 'pan') in ('pan', 'pan_right', 'pan_left'):
            p = dict(p, camera='push')  # sideways pans push characters out of the 9:16 window
        if p.get('pov') == 'friend':
            S = dict(S, hero=S['friend'], friend=S['hero'])
        hero_patch = p.get('hero_patch')
        if hero_patch:
            S = dict(S, hero=dict(S['hero'], **hero_patch))
        fn(c, t, d, p, S)
        if p.get('spotlight'):
            c.save()
            cam(c, t, d, p, 'push')
            draw_spotlight(c, t, p['spotlight'])
            c.restore()
        if p.get('thoughts'):
            c.save()
            cam(c, t, d, p, 'push')
            draw_thoughts(c, t, p['thoughts'])
            c.restore()
    run.__name__ = fn.__name__
    return run


TEMPLATES = {
    'card': t_card, 'hangout': t_hangout, 'bedroom': t_bedroom, 'phone_feed': t_phone_feed, 'phone_chat': t_phone_chat,
    'face': t_face, 'mirror': t_mirror, 'desk': t_desk, 'montage': t_montage, 'stage': t_stage, 'gallery': t_gallery,
    'sunrise': t_sunrise, 'end_card': t_end_card, 'outro': t_outro,
}
TEMPLATES = {k: _wrap(v) for k, v in TEMPLATES.items()}
