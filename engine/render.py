"""CLI:  python3 -m engine.render stories/<file>.json  --check | --preview | --full

--check    validate the story file (durations, captions, metadata)
--preview  write out/<id>/preview.jpg (2 frames per scene) + thumbnails, for visual QA
--full     render out/<id>/video.mp4 (+ score, thumbnails, metadata.json)
"""
import argparse, json, os, subprocess, sys
from multiprocessing import Process

from .draw import W, H, FPS, skia, col
from . import story as ST
from . import thumbnail as TH
from .music import Score
from . import voice as VO
import numpy as np

ROOT = ST.ROOT


def resolve(path, need_voice=True):
    """Run narration (TTS + QA) and write out/<id>/story.resolved.json with voice-fitted durations + captions.
    Returns (resolved_path, voice_track@24k or None)."""
    with open(path) as f:
        spec = json.load(f)
    if not any(sc.get('narration') for sc in spec.get('scenes', [])):
        return path, None
    d = out_dir(spec)
    short = spec.get('format') == 'short'
    spec['_outro_seconds'] = ST.load_config().get('outro_seconds', 9)
    rspec, track, log = VO.prepare(spec, d, short)
    rspec['_source'] = os.path.relpath(path, ROOT)
    rp = os.path.join(d, 'story.resolved.json')
    with open(rp, 'w') as f:
        json.dump(rspec, f, indent=1, ensure_ascii=False)
    bad = [l for l in log if not l['ok']]
    print(f"voice: {len(log)} sentences, {len(bad)} below QA threshold" + ''.join(
        f"\n  CHECK: '{l['text']}' heard as '{l['heard']}' (wer {l['wer']})" for l in bad))
    np.save(os.path.join(d, 'voice_track.npy'), track)
    return rp, track


def out_dir(spec):
    d = os.path.join(ROOT, 'out', spec['id'])
    os.makedirs(d, exist_ok=True)
    return d


def _worker(path, f0, f1, out):
    spec, S = ST.load(path)
    ow, oh = S['out_w'], S['out_h']
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{ow}x{oh}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    surf = skia.Surface(ow, oh)
    c = surf.getCanvas()
    for fi in range(f0, f1):
        c.clear(col('#000000'))
        ST.render_frame(c, fi / FPS, fi, S)
        p.stdin.write(surf.makeImageSnapshot().tobytes())
    p.stdin.close()
    p.wait()


def loudnorm_filter(wav):
    """Two-pass EBU R128 to -14 LUFS in linear mode (constant gain, so no pumping on the voice)."""
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', wav, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json',
                        '-f', 'null', '-'], capture_output=True, text=True)
    try:
        j = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
        return ('loudnorm=I=-14:TP=-1.5:LRA=11:linear=true:measured_I={input_i}:measured_TP={input_tp}:'
                'measured_LRA={input_lra}:measured_thresh={input_thresh}:offset={target_offset},'
                'alimiter=limit=0.85:attack=4:release=80:level=false').format(**j)
    except Exception:
        return 'loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.85:attack=4:release=80:level=false'


def check(path):
    spec, S = ST.load(path)
    errs, warns = ST.validate(spec, S)
    for w in warns:
        print('WARN ', w)
    for e in errs:
        print('ERROR', e)
    print(f"duration {S['total']:.1f}s, scenes {len(S['timeline'])}, errors {len(errs)}, warnings {len(warns)}")
    return spec, S, errs


def thumbs(spec, S, d):
    if S.get('short'):
        # YouTube ignores API thumbnails on Shorts; this cover is for YouTube Studio (Content > Short > Thumbnail)
        TH.make_short_cover(S, os.path.join(d, 'thumbnail.png'))
        ct = spec.get('short', {}).get('cover_time', 1.0)
        surf = skia.Surface(S['out_w'], S['out_h'])
        c = surf.getCanvas()
        c.clear(col('#000000'))
        ST.render_frame(c, ct, int(ct * FPS), S)
        surf.makeImageSnapshot().save(os.path.join(d, 'cover_frame.png'), skia.kPNG)
        return
    th = spec.get('thumbnail', {})
    v = th.get('layout') if th.get('layout') in ('scene', 'hero') else th.get('variant', 'face')
    TH.make(S, os.path.join(d, 'thumbnail.png'), v)
    TH.make(S, os.path.join(d, 'thumbnail_alt.png'), 'split' if v != 'split' else 'face')


def preview(path):
    path, _ = resolve(path)
    spec, S, errs = check(path)
    d = out_dir(spec)
    frames = []
    for i, sc in enumerate(S['timeline']):
        for frac in (0.3, 0.75):
            gt = sc['t0'] + sc['duration'] * frac
            surf = skia.Surface(S['out_w'], S['out_h'])
            c = surf.getCanvas()
            c.clear(col('#000000'))
            ST.render_frame(c, gt, int(gt * FPS), S)
            fp = os.path.join(d, f'prev_{i:02d}_{int(frac * 100)}.png')
            surf.makeImageSnapshot().save(fp, skia.kPNG)
            frames.append(fp)
    cols = 8 if S.get('short') else 4
    tile = '270:480' if S.get('short') else '480:270'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-pattern_type', 'glob', '-i', os.path.join(d, 'prev_*.png'),
                    '-vf', f'scale={tile},tile={cols}x{(len(frames) + cols - 1) // cols}:padding=6:color=0x222222',
                    '-frames:v', '1', os.path.join(d, 'preview.jpg')], check=True)
    for fp in frames:
        os.remove(fp)
    thumbs(spec, S, d)
    print('preview:', os.path.join(d, 'preview.jpg'))


def full(path, workers=4):
    src = path
    path, track = resolve(path)
    spec, S, errs = check(path)
    if errs:
        sys.exit('fix errors first')
    d = out_dir(spec)
    nf = int(round(S['total'] * FPS))
    bounds = [nf * i // workers for i in range(workers + 1)]
    segs = [os.path.join(d, f'seg{i}.mp4') for i in range(workers)]
    mus = spec.get('music', {})
    Score(S['total'], mus.get('key', 0), mus.get('tempo', 96), mus.get('seed', 1)).render(S['timeline'], os.path.join(d, 'score.wav'),
                                                                                         short=bool(S.get('short')), voice=track)
    print('score done, rendering frames...', flush=True)
    ps = [Process(target=_worker, args=(path, bounds[i], bounds[i + 1], segs[i])) for i in range(workers)]
    [p.start() for p in ps]
    [p.join() for p in ps]
    if any(p.exitcode for p in ps):
        sys.exit('a render worker failed')
    lst = os.path.join(d, 'segs.txt')
    with open(lst, 'w') as f:
        f.writelines(f"file '{s}'\n" for s in segs)
    af = loudnorm_filter(os.path.join(d, 'score.wav'))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-i', os.path.join(d, 'score.wav'),
                    '-c:v', 'copy', '-af', af, '-ar', '48000', '-c:a', 'aac', '-b:a', '192k',
                    '-shortest', '-movflags', '+faststart', os.path.join(d, 'video.mp4')], check=True)
    for s in segs + [lst]:
        os.remove(s)
    thumbs(spec, S, d)
    yt = spec['youtube']
    cfg = S['config']
    desc = yt['description'].rstrip()
    ch = [] if S.get('short') else ST.chapters(S)
    if ch:
        desc += '\n\n⏱️ Chapters\n' + '\n'.join(ch)
    if cfg.get('description_footer'):
        desc += '\n\n' + cfg['description_footer']
    meta = dict(title=yt['title'], description=desc, tags=yt.get('tags', []), categoryId=str(cfg.get('category_id', '27')),
                privacyStatus=cfg.get('privacy', 'public'), madeForKids=False, defaultLanguage=cfg.get('language', 'en'),
                video=os.path.join(d, 'video.mp4'), thumbnail=os.path.join(d, 'thumbnail.png'), story=os.path.relpath(src, ROOT),
                topic=spec.get('topic'), id=spec['id'], kind='short' if S.get('short') else 'long',
                comment=yt.get('comment'))
    with open(os.path.join(d, 'metadata.json'), 'w') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    # QA sheet of the finished video
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(d, 'video.mp4'), '-vf',
                    'fps=1/2,scale=216:-1,tile=10x3:padding=4' if S.get('short') else 'fps=1/4,scale=384:-1,tile=6x8:padding=4', '-frames:v', '1', os.path.join(d, 'final_sheet.jpg')])
    print('done:', os.path.join(d, 'video.mp4'))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('story')
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--check', action='store_true')
    g.add_argument('--preview', action='store_true')
    g.add_argument('--full', action='store_true')
    ap.add_argument('--workers', type=int, default=os.cpu_count() or 4)
    a = ap.parse_args()
    if a.check:
        sys.exit(1 if check(resolve(a.story)[0])[2] else 0)
    elif a.preview:
        preview(a.story)
    else:
        full(a.story, a.workers)
