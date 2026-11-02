"""Thumbnail options for the bhang episode (1280x720 PNGs + a phone-size comparison sheet).
python3 -m explainer.thumbs"""
import math
import os

import skia

from . import art as A
from .scenes_a import powder_burst, HOLI, rangoli

OUT = os.path.join(A.HERE, '..', 'out', 'bhang-brain')


def title(c, words, y=150, size=168, colors=('#ffffff',)):
    s = ' '.join(words)
    w = A.measure(s, size, 900)
    if w > 1800:
        size *= 1800 / w
    x = 960 - A.measure(s, size, 900) / 2
    for i, wd in enumerate(words):
        A.text(c, wd, x, y, size, colors[i % len(colors)], weight=900, align='left', shadow=0.6,
               outline=('#12062e', 18))
        A.text(c, wd, x, y, size, colors[i % len(colors)], weight=900, align='left', shadow=0)
        x += A.measure(wd + ' ', size, 900)


def thumb_a(c):
    """BHANG BRAIN: brain mascot soaking in a giant glowing glass."""
    A.bg_radial(c, (960, 700), '#2f9a5a', '#1a0840', 1200)
    c.save()
    c.translate(960, 700)
    for i in range(20):
        path = skia.Path()
        a0, a1 = math.radians(i * 18), math.radians(i * 18 + 8)
        path.moveTo(0, 0)
        path.lineTo(math.cos(a0) * 1500, math.sin(a0) * 1500)
        path.lineTo(math.cos(a1) * 1500, math.sin(a1) * 1500)
        path.close()
        c.drawPath(path, A.P('#ffffff', 0.07))
    c.restore()
    for i, (x, y, an) in enumerate([(260, 520, -35), (1660, 560, 30), (330, 900, -120), (1600, 930, 120)]):
        A.leaf(c, x, y, 0.75, ang=an, h=['#2bd17e', '#45e08c'][i % 2])
    A.glass(c, 960, 1110, 2.9, 0.86, t=0.3, glowc='#c8ffb0', garnish=False)
    c.save()
    c.translate(960, 760)
    c.scale(0.95, 0.95)
    A.brain(c, 0, 0, 1.0, 0.0, expr='high', look=(0.25, -0.25), stem=False, glow_c='#7dff6a', glow_a=0.5)
    c.restore()
    for i in range(14):
        an = i / 14 * 6.28
        A.circle(c, 960 + math.cos(an) * 520, 760 + math.sin(an) * 280, 9, '#ffffff', 0.7)
    title(c, ['BHANG', 'BRAIN'], 205, 190, ('#ffffff', '#7dff6a'))


def thumb_b(c):
    """HOLY HIGH?: Holi colour explosion around one glowing glass."""
    A.bg_grad(c, '#ff9a4d', '#4a1a9a', '#ff3d8b')
    for i, (x, y, h, t0) in enumerate([(300, 640, HOLI[0], -1.2), (1620, 640, HOLI[2], -1.0), (520, 980, HOLI[1], -1.3),
                                       (1420, 990, HOLI[4], -1.1), (960, 500, HOLI[3], -1.4)]):
        powder_burst(c, x, y, 0, t0, h, 2.0, seed=i * 5)
    rangoli(c, 960, 760, 360, 0.0, a=0.9)
    A.glow(c, 960, 760, 420, '#ffffff', 0.4)
    A.glass(c, 960, 1060, 2.2, 0.84, t=0.5, glowc='#c8ffb0')
    for s in (-1, 1):
        A.eye(c, 960 + s * 70, 760, 46, look=(0.3, -0.3), lid=0.5, lid_col='#d8efc0', red=1)
    A.mouth(c, 960, 860, 150, 'grin')
    title(c, ['HOLY', 'HIGH?'], 205, 200, ('#ffffff', '#ffe14d'))


def thumb_c(c):
    """THE 2ND GLASS: the delayed double-dose trap."""
    A.bg_radial(c, (960, 600), '#5a1a8f', '#12041c', 1200)
    for i in range(5):
        r = 200 + i * 170
        c.drawCircle(1350, 640, r, A.P('#ff3d6e', 0.09, stroke=40))
    A.glass(c, 480, 1000, 1.7, 0.1, t=0.0, garnish=False)
    A.glass(c, 840, 1000, 1.7, 0.85, t=0.0, glowc='#ff3d6e')
    A.text(c, '+1', 840, 520, 120, '#ff3d6e', weight=900, outline=('#12062e', 14))
    A.text(c, '+1', 840, 520, 120, '#ff3d6e', weight=900, shadow=0)
    A.person(c, 1450, 1400, 2.6, dict(skin='#d99a6c', hair='#22122e', style='spiky', shirt='#2bd1ff'), expr='dazed',
             t=0.0, look=(-0.5, 0.2))
    A.clock(c, 1700, 400, 115, 3.6)
    title(c, ['THE', '2ND GLASS'], 205, 180, ('#ffffff', '#ff3d6e'))


def main():
    os.makedirs(OUT, exist_ok=True)
    imgs = []
    for name, fn in (('A_bhang_brain', thumb_a), ('B_holy_high', thumb_b), ('C_second_glass', thumb_c)):
        s = skia.Surface(1920, 1080)
        c = s.getCanvas()
        fn(c)
        img = s.makeImageSnapshot()
        small = skia.Surface(1280, 720)
        small.getCanvas().drawImageRect(img, skia.Rect(0, 0, 1280, 720), skia.SamplingOptions(skia.FilterMode.kLinear))
        p = os.path.join(OUT, f'thumbnail_{name}.png')
        small.makeImageSnapshot().save(p, skia.kPNG)
        imgs.append((img, name))
    # sheet: big + phone size
    s = skia.Surface(3 * 640 + 40, 360 + 40 + 120)
    c = s.getCanvas()
    c.clear(A.col('#0f0f12'))
    for i, (img, name) in enumerate(imgs):
        x = 10 + i * 650
        c.drawImageRect(img, skia.Rect(x, 10, x + 640, 370), skia.SamplingOptions(skia.FilterMode.kLinear))
        c.drawImageRect(img, skia.Rect(x, 390, x + 196, 500), skia.SamplingOptions(skia.FilterMode.kLinear))
        A.text(c, name.split('_', 1)[0] + ' (phone size)', x + 210, 450, 22, '#ffffff', weight=700, align='left', shadow=0)
    s.makeImageSnapshot().save(os.path.join(OUT, 'thumbnails_sheet.jpg'), skia.kJPEG, 90)
    print('thumbnails ->', OUT)


if __name__ == '__main__':
    main()
