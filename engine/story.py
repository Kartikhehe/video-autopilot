"""Story file -> timeline, validation and per-frame rendering."""
import json, os
from .draw import *
from . import library as L

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HERO_DEFAULT = dict(KID)
FRIEND_DEFAULT = dict(DEV)
VALID_MOODS = {'warm', 'groove', 'calm', 'curious', 'rush', 'dark', 'tense', 'numb', 'sad', 'tender', 'hope',
               'triumph', 'silence'}


def load_config():
    with open(os.path.join(ROOT, 'config.json')) as f:
        return json.load(f)


def load(path):
    with open(path) as f:
        spec = json.load(f)
    cfg = load_config()
    cast = spec.get('cast', {})
    hero = dict(HERO_DEFAULT, **cast.get('hero', {}))
    friend = dict(FRIEND_DEFAULT, **cast.get('friend', {}))
    hero.setdefault('hoodie_dark', mix(hero['hoodie'], '#000000', 0.25))
    friend.setdefault('hoodie_dark', mix(friend['hoodie'], '#000000', 0.25))
    hero['hoodie_dark'] = cast.get('hero', {}).get('hoodie_dark', mix(hero['hoodie'], '#000000', 0.25))
    friend['hoodie_dark'] = cast.get('friend', {}).get('hoodie_dark', mix(friend['hoodie'], '#000000', 0.25))
    set_urge_color(cast.get('habit', {}).get('glow', '#ff2e88'))
    short = spec.get('format') == 'short'
    S = dict(hero=hero, friend=friend, config=cfg, spec=spec, short=short,
             out_w=1080 if short else W, out_h=1920 if short else H)
    scenes = list(spec['scenes'])
    if not short and not any(s['template'] == 'outro' for s in scenes):
        scenes.append(dict(template='outro', duration=cfg.get('outro_seconds', 9), mood='calm'))
    tl, t0 = [], 0.0
    for s in scenes:
        tl.append(dict(s, t0=t0))
        t0 += s['duration']
    S['timeline'] = tl
    S['total'] = t0
    return spec, S


def validate(spec, S):
    """Returns (errors, warnings). Errors must be fixed before rendering."""
    errs, warns = [], []
    cfg = S['config']
    total = S['total']
    if S.get('short'):
        lo, hi = cfg.get('short_min_seconds', 20), cfg.get('short_max_seconds', 59)
    else:
        lo, hi = cfg.get('min_seconds', 140), cfg.get('max_seconds', 178)
    if not lo <= total <= hi:
        errs.append(f'total duration {total:.1f}s outside {lo}-{hi}s')
    caps = 0
    for i, sc in enumerate(S['timeline']):
        name = f"scene {i} ({sc['template']})"
        if sc['template'] not in L.TEMPLATES:
            errs.append(f'{name}: unknown template')
            continue
        if sc.get('mood', 'calm') not in VALID_MOODS:
            errs.append(f"{name}: unknown mood {sc.get('mood')}")
        d = sc['duration']
        prev_end = -1
        for cap in sc.get('captions', []):
            a, b, s = cap
            caps += 1
            if b > d + 0.01 or a < 0:
                errs.append(f'{name}: caption "{s}" outside scene (0-{d})')
            if b - a < (1.2 if S.get('short') else 1.8):
                warns.append(f'{name}: caption "{s}" only {b - a:.1f}s on screen')
            if a < prev_end:
                errs.append(f'{name}: caption "{s}" overlaps previous caption')
            prev_end = b
            if not S.get('short') and measure(s, 50) > 1700:
                errs.append(f'{name}: caption too wide: "{s}"')
            if len(s.split()) > (8 if S.get('short') else 11):
                warns.append(f'{name}: caption has {len(s.split())} words (aim for <= 9): "{s}"')
        p = sc.get('params', {})
        if sc['template'] == 'montage':
            for sh in p.get('shots', []):
                if sh['template'] not in L.TEMPLATES or sh['template'] == 'montage':
                    errs.append(f"{name}: bad montage shot template {sh['template']}")
        if sc['template'] in ('card', 'end_card') and 'text' not in p:
            errs.append(f'{name}: needs params.text')
        for tw, s in p.get('urge', {}).get('whispers', []):
            if len(s) > 26:
                warns.append(f'{name}: whisper "{s}" is long (keep it under ~4 words)')
    if caps < (8 if S.get('short') else 25):
        warns.append(f'only {caps} captions; the reference rhythm is ~35-50')
    yt = spec.get('youtube', {})
    if not yt.get('title') or len(yt.get('title', '')) > 100:
        errs.append('youtube.title missing or over 100 chars')
    if len(yt.get('description', '')) > 4500:
        errs.append('youtube.description too long')
    if len(','.join(yt.get('tags', []))) > 480:
        errs.append('youtube.tags over 480 chars total')
    th = spec.get('thumbnail', {})
    if not th.get('words') or len(th['words']) > 4:
        errs.append('thumbnail.words must be 1-4 words')
    return errs, warns


def draw_caption(c, s, a, t_local):
    if a <= 0:
        return
    rise = (1 - ramp(t_local, 0, 0.35)) * 8
    w = measure(s, 50)
    c.drawRoundRect(skia.Rect.MakeXYWH(W / 2 - w / 2 - 30, 962 + rise, w + 60, 70), 30, 30, paint('#000000', 0.32 * a, blur=18))
    text(c, s, W / 2, 1012 + rise, 50, '#f6f0e4', a=a)


def render_frame(c, gt, fi, S):
    if S.get('short'):
        from . import shorts
        return shorts.render_frame(c, gt, fi, S)
    for sc in S['timeline']:
        t0, dur = sc['t0'], sc['duration']
        if t0 <= gt < t0 + dur or sc is S['timeline'][-1]:
            t = min(gt - t0, dur - 1e-3)
            c.save()
            L.TEMPLATES[sc['template']](c, t, dur, sc.get('params', {}), S)
            c.restore()
            post(c, fi, vignette=0.0 if sc['template'] in ('card', 'end_card') else 0.5, grain=0.07)
            for (a0, a1, s) in sc.get('captions', []):
                if a0 - 0.05 <= t <= a1 + 0.05:
                    draw_caption(c, s, window(t, a0, a1, 0.35), t - a0)
            fi_, fo_ = sc.get('fade_in', 0.35), sc.get('fade_out', 0.35)
            k = 1.0
            if fi_ > 0:
                k = min(k, ramp(t, 0, fi_))
            if fo_ > 0:
                k = min(k, 1 - ramp(t, dur - fo_, dur))
            if k < 1:
                c.drawRect(skia.Rect.MakeWH(W, H), paint('#000000', 1 - k))
            return sc
    return None


def chapters(S):
    out = []
    for sc in S['timeline']:
        if sc.get('chapter'):
            m, s = divmod(int(sc['t0']), 60)
            out.append(f'{m}:{s:02d} {sc["chapter"]}')
    if out and not out[0].startswith('0:00'):
        out[0] = '0:00 ' + out[0].split(' ', 1)[1]
    return out if len(out) >= 3 else []
