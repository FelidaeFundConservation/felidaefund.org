"""Work out what colour the legend patch must be to disappear into the map.

The basemap is rendered with  grayscale(1) contrast(.42) brightness(1.2)
at opacity .62 over --cream-200. Sample the real pixels just outside the
legend panel, push them through the same chain, and that is the fill.
"""
import json, glob, os
import numpy as np
from PIL import Image

BG = np.array([255, 248, 230], float)   # --cream-200
ALPHA, CONTRAST, BRIGHT = .62, .42, 1.2

def filtered(rgb):
    lum = (0.2126*rgb[0] + 0.7152*rgb[1] + 0.0722*rgb[2]) / 255.0
    lum = (lum - .5) * CONTRAST + .5
    lum = min(max(lum * BRIGHT, 0.0), 1.0) * 255.0
    v = np.array([lum, lum, lum])
    return ALPHA * v + (1 - ALPHA) * BG

done = 0
for f in sorted(glob.glob('traced/*.json')):
    d = json.load(open(f))
    lg = d.get('legend')
    if not lg:
        continue
    slug = os.path.basename(f)[:-5]
    src = f'maps/{slug}.jpg'
    if not os.path.exists(src):
        continue
    a = np.asarray(Image.open(src).convert('RGB')).astype(float)
    H, W = a.shape[:2]
    pad = 26
    y0, y1 = max(0, lg['y'] - pad), min(H, lg['y'] + lg['h'] + pad)
    x0, x1 = max(0, lg['x'] - pad), min(W, lg['x'] + lg['w'] + pad)
    ring = np.ones((y1 - y0, x1 - x0), bool)
    iy0, iy1 = lg['y'] - y0, lg['y'] + lg['h'] - y0
    ix0, ix1 = lg['x'] - x0, lg['x'] + lg['w'] - x0
    ring[max(0, iy0):max(0, iy1), max(0, ix0):max(0, ix1)] = False
    px = a[y0:y1, x0:x1][ring]
    med = np.median(px, axis=0)
    out = filtered(med)
    d['legendFill'] = '#%02x%02x%02x' % tuple(int(round(c)) for c in out)
    json.dump(d, open(f, 'w'))
    done += 1

print(f'{done} legend fills computed')
print('cheetah ->', json.load(open('traced/cheetah-map.json'))['legendFill'])
