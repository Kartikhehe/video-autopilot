"""python3 -m engine.rethumb <story.json> [--out out/<id>/thumbnail.png]

Re-renders just the thumbnail of a story (long or Short) without rendering the video. Also accepts a
thumbnail-only spec (id, cast, thumbnail with an inline "scene": {"template": ...}) for videos whose story
file is gone. Set it on YouTube with: python3 -m youtube.set_thumbnail <video_id> <png>
"""
import argparse, os
from . import story as ST, thumbnail as TH
from .draw import W, H

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('story')
    ap.add_argument('--out')
    a = ap.parse_args()
    spec, S = ST.load(a.story)
    out = a.out or os.path.join(ROOT, 'out', spec['id'], 'thumbnail.png')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    th = spec.get('thumbnail', {})
    if S.get('short'):
        TH.make_vertical(S, out)
    elif th.get('layout') == 'scene':
        TH.make_scene(S, out, W, H)
    else:
        TH.make(S, out, th.get('variant', 'face'))
    print(out)


if __name__ == '__main__':
    main()
