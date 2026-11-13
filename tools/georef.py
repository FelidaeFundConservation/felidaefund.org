"""Work out what patch of the world each IUCN screenshot shows.

The screenshots come out of a Leaflet/Esri viewer, so they are Web
Mercator with no rotation. That leaves three unknowns: metres per pixel,
and the mercator x/y of the top-left corner. Fit them by matching the
screenshot's own land/water split against a world coastline.
"""
import json, math, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

R = 6378137.0
EXT = math.pi * R                      # 20037508.34
OCEAN = np.array([178, 227, 253])
G = 4096                               # global raster size

def merc(lon, lat):
    lat = max(min(lat, 85.05), -85.05)
    return (math.radians(lon) * R,
            R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)))

def world_land(geojson):
    im = Image.new('1', (G, G), 0)
    dr = ImageDraw.Draw(im)
    k = G / (2 * EXT)
    d = json.load(open(geojson))
    for f in d['features']:
        g = f['geometry']
        if not g:
            continue
        polys = ([g['coordinates']] if g['type'] == 'Polygon'
                 else g['coordinates'] if g['type'] == 'MultiPolygon' else [])
        for poly in polys:
            for ring in poly[:1]:                     # outer ring is enough
                pts = []
                for lon, lat in ring:
                    x, y = merc(lon, lat)
                    pts.append(((x + EXT) * k, (EXT - y) * k))
                if len(pts) > 2:
                    dr.polygon(pts, fill=1)
    return np.asarray(im, bool)

def ocean_mask(path, size):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    m = np.abs(a - OCEAN).sum(axis=2) < 70
    m = ndimage.binary_closing(m, np.ones((5, 5)))
    im = Image.fromarray((~m).astype(np.uint8) * 255)   # land = white
    im = im.resize((size, size), Image.BILINEAR)
    return np.asarray(im) > 127, a.shape[1], a.shape[0]

def _iou(land, target, mpp, cx, cy, W, H, n):
    k = G / (2 * EXT)
    hw, hh = mpp * W / 2.0, mpp * H / 2.0
    gx = ((cx - hw + (np.arange(n) + .5) * (2 * hw / n)) + EXT) * k
    gy = (EXT - (cy + hh - (np.arange(n) + .5) * (2 * hh / n))) * k
    s = land[np.ix_(np.clip(gy.astype(int), 0, G - 1),
                    np.clip(gx.astype(int), 0, G - 1))]
    u = np.count_nonzero(s | target)
    return (np.count_nonzero(s & target) / u) if u else 0.0


def fit(slug, land, verbose=False):
    """Coarse sweep, then refine the best few. One sweep alone lands in a
    false optimum: for the cheetah map it settled over south-east Asia at
    IoU .63 while the true fit over Africa scores .86."""
    t_c, W, H = ocean_mask(f'maps/{slug}.jpg', 96)
    t_f, _, _ = ocean_mask(f'maps/{slug}.jpg', 192)

    cand = []
    for mpp in np.geomspace(2200., 42000., 20):
        for cx in np.linspace(-EXT * .62, EXT * .62, 33):
            for cy in np.linspace(-EXT * .34, EXT * .58, 27):
                cand.append((_iou(land, t_c, mpp, cx, cy, W, H, 96), mpp, cx, cy))
    cand.sort(reverse=True)
    starts = cand[:28]
    if verbose:
        print(f'  coarse best {starts[0][0]:.3f}')

    best = (0, 0, 0, 0)
    for _, mpp, cx, cy in starts:
        sm, sx, sy = .30, 1.6e6, 1.6e6
        cur = (_iou(land, t_f, mpp, cx, cy, W, H, 192), mpp, cx, cy)
        for _ in range(6):
            trial = []
            for m in np.linspace(cur[1] * (1 - sm), cur[1] * (1 + sm), 7):
                for x in np.linspace(cur[2] - sx, cur[2] + sx, 7):
                    for y in np.linspace(cur[3] - sy, cur[3] + sy, 7):
                        trial.append((_iou(land, t_f, m, x, y, W, H, 192), m, x, y))
            trial.sort(reverse=True)
            if trial[0][0] > cur[0]:
                cur = trial[0]
            sm, sx, sy = sm * .45, sx * .45, sy * .45
        if cur[0] > best[0]:
            best = cur
    iou, mpp, cx, cy = best
    if verbose:
        print(f'  refined {iou:.3f} mpp {mpp:.0f} centre ({cx:.0f},{cy:.0f})')
    return {'iou': round(float(iou), 4), 'mpp': float(mpp),
            'x0': float(cx - mpp * W / 2), 'y0': float(cy + mpp * H / 2),
            'w': W, 'h': H}


if __name__ == '__main__':
    import os
    if os.path.exists('world_land.npy'):
        land = np.load('world_land.npy')
    else:
        land = world_land('data/ne.geojson')
        np.save('world_land.npy', land)
    print('world raster', land.shape)
    out = {}
    if os.path.exists('georef.json'):
        out = json.load(open('georef.json'))
    for slug in sys.argv[1:]:
        r = fit(slug, land, verbose=True)
        print(slug, 'IoU', r['iou'])
        out[slug] = r
        json.dump(out, open('georef.json', 'w'), indent=1)
