"""Render a narrated explainer episode.

python3 -m explainer.render explainer/episodes/<ep>.json --preview      # contact sheet of 2 frames per shot
python3 -m explainer.render explainer/episodes/<ep>.json --shot 12      # 6 frames of one shot
python3 -m explainer.render explainer/episodes/<ep>.json --full         # video.mp4 + subtitles.srt + metadata
"""
import argparse
import json
import os
import subprocess
import sys
from multiprocessing import Process

import numpy as np
import skia

from . import art as A
from . import voice
from .scenes_a import SCENES as SA
from .scenes_b import SCENES as SB

SCENES = {**SA, **SB}
ROOT = voice.ROOT
TR = 0.5            # crossfade length
IRIS = 0.65         # iris wipe into chapter cards
NO_PUSH = {'chapter', 'title', 'outro', 'end_card'}


def load(path):
    ep = json.load(open(path))
    shots, track, total = voice.build(ep)
    return ep, shots, track, total


def out_dir(ep):
    d = os.path.join(ROOT, 'out', ep['id'])
    os.makedirs(d, exist_ok=True)
    return d


def draw_shot(c, sh, t):
    c.save()
    if sh['scene'] not in NO_PUSH:
        z = 1.0 + 0.045 * A.eio(t / max(sh['dur'], 0.1))
        c.translate(960, 540)
        c.scale(z, z)
        c.translate(-960, -540)
    SCENES[sh['scene']](c, t, sh['dur'], sh.get('p', {}), sh['beats'])
    c.restore()
    if sh.get('cite'):
        A.cite(c, sh['cite'], A.ramp(t, 0.8, 1.3) * (1 - A.ramp(t, sh['dur'] - 0.4, sh['dur'])))


def vignette(c):
    p = skia.Paint()
    p.setShader(A.rad((960, 540), 1150, ['#000000', '#000000', '#000000'], [0, 0.6, 1], alphas=[0, 0, 0.42]))
    c.drawRect(skia.Rect(0, 0, A.W, A.H), p)


def find(shots, T):
    for i, sh in enumerate(shots):
        if T < sh['start'] + sh['dur']:
            return i
    return len(shots) - 1


def render_frame(c, T, shots):
    i = find(shots, T)
    sh = shots[i]
    t = T - sh['start']
    c.clear(A.col('#000000'))
    if i > 0 and t < (IRIS if sh['scene'] == 'chapter' else TR):
        prev = shots[i - 1]
        draw_shot(c, prev, prev['dur'] + t)
        if sh['scene'] == 'chapter':
            k = A.eio(t / IRIS)
            path = skia.Path()
            path.addCircle(960, 540, 1150 * k)
            c.save()
            c.clipPath(path, doAntiAlias=True)
            draw_shot(c, sh, t)
            c.restore()
            c.drawCircle(960, 540, 1150 * k, A.P('#ffffff', 0.8 * (1 - k), stroke=26))
        else:
            k = A.ease(t / TR)
            c.saveLayerAlpha(None, int(255 * k))
            draw_shot(c, sh, t)
            c.restore()
    else:
        draw_shot(c, sh, t)
    vignette(c)


def snap(T, shots):
    s = skia.Surface(A.W, A.H)
    render_frame(s.getCanvas(), T, shots)
    return s.makeImageSnapshot()


def sheet(images, path, cols=6, w=480):
    h = int(w * 9 / 16)
    rows = (len(images) + cols - 1) // cols
    s = skia.Surface(cols * w, rows * h)
    c = s.getCanvas()
    c.clear(A.col('#000000'))
    for k, (img, cap) in enumerate(images):
        x, y = (k % cols) * w, (k // cols) * h
        c.drawImageRect(img, skia.Rect(x, y, x + w - 3, y + h - 3), skia.SamplingOptions(skia.FilterMode.kLinear))
        A.text(c, cap, x + 8, y + 26, 22, '#ffffff', weight=800, align='left', shadow=0.9)
    s.makeImageSnapshot().save(path, skia.kJPEG, 88)


def preview(path, only=None):
    ep, shots, track, total = load(path)
    d = out_dir(ep)
    imgs = []
    for i, sh in enumerate(shots):
        if only is not None and i not in only:
            continue
        fr = [0.35, 0.75] if only is None else [0.08, 0.25, 0.42, 0.58, 0.75, 0.92]
        for f in fr:
            T = sh['start'] + sh['dur'] * f
            imgs.append((snap(T, shots), f'{i} {sh["scene"]} {T:.1f}s'))
    name = 'preview.jpg' if only is None else f'shot_{"_".join(map(str, only))}.jpg'
    for k in range(0, len(imgs), 36):
        sheet(imgs[k:k + 36], os.path.join(d, name.replace('.jpg', f'_{k // 36}.jpg')), cols=6)
    print('total', round(total, 1), 's ->', d)


def _worker(path, f0, f1, out):
    ep, shots, track, total = load(path)
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{A.W}x{A.H}', '-r', str(A.FPS),
           '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-tune', 'animation', '-pix_fmt', 'yuv420p', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    surf = skia.Surface(A.W, A.H)
    c = surf.getCanvas()
    for fi in range(f0, f1):
        try:
            render_frame(c, fi / A.FPS, shots)
        except Exception as e:      # never lose a whole segment to one bad frame; keep the previous frame
            print(f'frame {fi} failed: {e!r}', file=sys.stderr, flush=True)
        p.stdin.write(surf.makeImageSnapshot().tobytes())
    p.stdin.close()
    p.wait()


def chapters(shots):
    out = []
    for sh in shots:
        if sh.get('chapter'):
            s = int(sh['start']) if out else 0
            out.append(f'{s // 60}:{s % 60:02d} {sh["chapter"]}')
    return out


def write_meta(ep, shots, d):
    yt = ep.get('youtube', {})
    desc = yt.get('description', '').rstrip()
    ch = chapters(shots)
    if ch:
        parts = desc.split('\n\n📚 Sources', 1)
        desc = parts[0] + '\n\n⏱️ Chapters\n' + '\n'.join(ch) + ('\n\n📚 Sources' + parts[1] if len(parts) > 1 else '')
    meta = dict(title=yt.get('title', ep['title']), description=desc, tags=yt.get('tags', []), categoryId='27',
                privacyStatus='private', madeForKids=False, defaultLanguage='en', video=os.path.join(d, 'video.mp4'),
                thumbnail=os.path.join(d, 'thumbnail_A_bhang_brain.png'), captions=os.path.join(d, 'subtitles.srt'),
                id=ep['id'], kind='long', comment=yt.get('comment'))
    with open(os.path.join(d, 'metadata.json'), 'w') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    with open(os.path.join(d, 'description.txt'), 'w') as f:
        f.write(desc + '\n')


def full(path, workers=4):
    from . import audio
    ep, shots, track, total = load(path)
    d = out_dir(ep)
    audio.mix(ep, shots, track, total, os.path.join(d, 'audio.wav'))
    print('audio done, rendering frames...', flush=True)
    nf = int(round(total * A.FPS))
    bounds = [nf * i // workers for i in range(workers + 1)]
    segs = [os.path.join(d, f'seg{i}.mp4') for i in range(workers)]
    ps = [Process(target=_worker, args=(path, bounds[i], bounds[i + 1], segs[i])) for i in range(workers)]
    [p.start() for p in ps]
    [p.join() for p in ps]
    if any(p.exitcode for p in ps):
        sys.exit('a render worker failed')
    lst = os.path.join(d, 'segs.txt')
    with open(lst, 'w') as f:
        f.writelines(f"file '{s}'\n" for s in segs)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-i', os.path.join(d, 'audio.wav'),
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest', '-movflags', '+faststart',
                    os.path.join(d, 'video.mp4')], check=True)
    for s in segs + [lst]:
        os.remove(s)
    voice.srt(shots, os.path.join(d, 'subtitles.srt'))
    write_meta(ep, shots, d)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(d, 'video.mp4'), '-vf',
                    'fps=1/6,scale=320:-1,tile=8x8:padding=4', '-frames:v', '1', os.path.join(d, 'final_sheet.jpg')])
    print('done:', os.path.join(d, 'video.mp4'), round(total, 1), 's')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('episode')
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--preview', action='store_true')
    g.add_argument('--shot', type=str, help='comma-separated shot indexes')
    g.add_argument('--full', action='store_true')
    ap.add_argument('--workers', type=int, default=os.cpu_count() or 4)
    a = ap.parse_args()
    if a.preview:
        preview(a.episode)
    elif a.shot:
        preview(a.episode, [int(x) for x in a.shot.split(',')])
    else:
        full(a.episode, a.workers)
