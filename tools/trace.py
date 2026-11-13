"""Trace the coloured range bands out of an IUCN map screenshot into SVG paths."""
import sys, json
import numpy as np
from PIL import Image
from scipy import ndimage

BANDS = {                      # legend colour -> band key
    'resident': (219, 162, 49),
    'possible': (159, 105, 129),
}
TOL = {'resident': 46, 'possible': 40}
MIN_AREA = 120        # below this it is JPEG fringing, not a range

def mask_for(a, rgb, tol):
    d = np.abs(a - np.array(rgb)).sum(axis=2)
    m = d < tol * 2.2
    m = ndimage.binary_closing(m, np.ones((3, 3)), iterations=2)
    m = ndimage.binary_opening(m, np.ones((2, 2)))
    return m

NBR = [(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]

def trace(mask, img=None, rgb=None):
    """Moore boundary following. Returns the outer ring of each blob."""
    lab, n = ndimage.label(mask, np.ones((3,3)))
    rings = []
    for i in range(1, n + 1):
        blob = lab == i
        area = int(blob.sum())
        if area < MIN_AREA:
            continue
        # Purity test. A real range region is solidly its legend colour.
        # Text, labels and legend keys are smears of several colours, so
        # their mean sits well away from it.
        if img is not None:
            mean = img[blob].mean(axis=0)
            if np.abs(mean - np.array(rgb)).sum() > 95:
                continue
        ys, xs = np.nonzero(blob)
        y0, x0 = ys.min(), xs[ys == ys.min()].min()
        H, W = blob.shape
        inside = lambda y, x: 0 <= y < H and 0 <= x < W and blob[y, x]

        ring, cur, bdir = [], (y0, x0), 6
        guard = 0
        while True:
            ring.append(cur)
            found = False
            for k in range(8):
                d = (bdir + 5 + k) % 8          # back up, then sweep clockwise
                dy, dx = NBR[d]
                ny, nx = cur[0] + dy, cur[1] + dx
                if inside(ny, nx):
                    cur, bdir, found = (ny, nx), d, True
                    break
            guard += 1
            if not found or guard > 400000:
                break
            if cur == (y0, x0) and len(ring) > 2:
                break
        if len(ring) > 7:
            rings.append((area, ring))
    return rings

def dp(pts, eps):
    """Douglas-Peucker."""
    if len(pts) < 3:
        return pts
    a, b = np.array(pts[0], float), np.array(pts[-1], float)
    ab = b - a
    nrm = np.hypot(*ab)
    P = np.array(pts, float)
    if nrm == 0:
        d = np.hypot(*(P - a).T)
    else:
        rel = P - a
        d = np.abs(ab[0] * rel[:, 1] - ab[1] * rel[:, 0]) / nrm
    i = int(d.argmax())
    if d[i] > eps:
        return dp(pts[:i+1], eps)[:-1] + dp(pts[i:], eps)
    return [pts[0], pts[-1]]

def legend_box(a):
    """The legend is a white panel. Everything inside it is a key, not a
    range, so it is masked out before tracing."""
    white = (a[:, :, 0] > 238) & (a[:, :, 1] > 238) & (a[:, :, 2] > 238)
    white = ndimage.binary_closing(white, np.ones((5, 5)))
    lab, n = ndimage.label(white)
    if not n:
        return None
    sizes = np.bincount(lab.ravel())
    sizes[0] = 0
    H, W = white.shape
    best = None
    for i in np.argsort(sizes)[::-1][:6]:
        if sizes[i] < 4000:
            break
        ys, xs = np.nonzero(lab == i)
        y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
        bw, bh = x1 - x0 + 1, y1 - y0 + 1
        if bw < 60 or bh < 30 or bw > W * .62 or bh > H * .4:
            continue
        if sizes[i] / float(bw * bh) < .55:      # must actually be a filled box
            continue
        best = (y0, y1, x0, x1)
        break
    return best


def main(src, out, eps=1.4):
    im = Image.open(src).convert('RGB')
    a = np.asarray(im).astype(int)
    W, H = im.size
    box = legend_box(a)
    shapes = []
    for key, rgb in BANDS.items():
        m = mask_for(a, rgb, TOL[key])
        if box:
            y0, y1, x0, x1 = box
            m[max(0, y0 - 4):y1 + 5, max(0, x0 - 4):x1 + 5] = False
        for area, ring in trace(m, a, rgb):
            simp = dp(ring, eps)
            if len(simp) < 4:
                continue
            ys, xs = zip(*simp)
            d = 'M' + 'L'.join(f'{x},{y}' for y, x in simp) + 'Z'
            shapes.append({'band': key, 'area': area, 'd': d})
    shapes.sort(key=lambda s: -s['area'])
    out_d = {'w': W, 'h': H, 'shapes': shapes}
    if box:
        y0, y1, x0, x1 = box
        # A little bleed so the panel's drop shadow goes with it.
        out_d['legend'] = {'x': int(x0) - 5, 'y': int(y0) - 5,
                           'w': int(x1 - x0) + 11, 'h': int(y1 - y0) + 11}
    json.dump(out_d, open(out, 'w'))
    tot = {}
    for s in shapes:
        tot[s['band']] = tot.get(s['band'], 0) + 1
    print(f'{src}: {len(shapes)} shapes {tot}, canvas {W}x{H}')

if __name__ == '__main__':
    sys.setrecursionlimit(100000)
    main(sys.argv[1], sys.argv[2])
