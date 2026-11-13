"""Render a species range map from scratch.

Nothing here is a screenshot. The range polygons were traced out of the
IUCN map and georeferenced back to Web Mercator; the land, borders and
labels are Natural Earth, which is public domain. That means the type,
the colours, the scale bar and the framing are all ours.
"""
import json, math, sys, os
import numpy as np

R = 6378137.0

def merc(lon, lat):
    lat = max(min(lat, 85.05), -85.05)
    return (math.radians(lon) * R,
            R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)))

def rings_of(geom):
    t, c = geom['type'], geom['coordinates']
    if t == 'Polygon':
        return [c]
    if t == 'MultiPolygon':
        return c
    return []

def build(slug, traced, geo, ne, out_w=1000.0, pad_frac=.07):
    g = geo[slug]
    x0, y0, mpp = g['x0'], g['y0'], g['mpp']

    # traced pixels -> web mercator
    shapes = []
    for s in traced['shapes']:
        pts = []
        for p in s['d'][1:-1].split('L'):
            px, py = p.split(',')
            pts.append((x0 + float(px) * mpp, y0 - float(py) * mpp))
        shapes.append({'band': s['band'], 'area': s['area'], 'pts': pts})

    xs = [p[0] for s in shapes for p in s['pts']]
    ys = [p[1] for s in shapes for p in s['pts']]
    bx0, bx1, by0, by1 = min(xs), max(xs), min(ys), max(ys)
    pad = max(bx1 - bx0, by1 - by0) * pad_frac
    bx0 -= pad; bx1 += pad; by0 -= pad; by1 += pad

    k = out_w / (bx1 - bx0)
    out_h = (by1 - by0) * k
    def T(X, Y):
        return ((X - bx0) * k, (by1 - Y) * k)

    mw, mh = bx1 - bx0, by1 - by0

    def path_of(geom, simplify):
        out = []
        for ring in rings_of(geom):
            for r in ring[:1]:
                pts, last = [], None
                for lon, lat in r:
                    X, Y = merc(lon, lat)
                    if not (bx0 - mw * .30 < X < bx1 + mw * .30
                            and by0 - mh * .30 < Y < by1 + mh * .30):
                        last = None
                        continue
                    x, y = T(X, Y)
                    p = (round(x), round(y))
                    if last is None or abs(p[0]-last[0]) + abs(p[1]-last[1]) > simplify:
                        pts.append(p); last = p
                if len(pts) > 6:
                    a2 = 0.0
                    for i2 in range(len(pts)):
                        xa, ya = pts[i2]; xb, yb = pts[(i2 + 1) % len(pts)]
                        a2 += xa * yb - xb * ya
                    # Skip specks. At this scale they are noise, not land.
                    if abs(a2) / 2 > (out_w * 0.9):
                        out.append('M' + 'L'.join(f'{a},{b}' for a, b in pts) + 'Z')
        return ''.join(out)

    land, labels = [], []
    for f in ne['features']:
        geom = f['geometry']
        if not geom:
            continue
        d = path_of(geom, 1.7)
        if not d:
            continue
        land.append(d)
        # label the country if a decent part of it is on screen
        best, barea = None, 0
        for ring in rings_of(geom):
            pr = [T(*merc(lon, lat)) for lon, lat in ring[0]]
            vis = [p for p in pr if -out_w*.04 < p[0] < out_w*1.04 and -out_h*.04 < p[1] < out_h*1.04]
            if len(vis) < 3:
                continue
            a = 0.0
            for i in range(len(pr)):
                x1c, y1c = pr[i]; x2c, y2c = pr[(i+1) % len(pr)]
                a += x1c*y2c - x2c*y1c
            a = abs(a) / 2
            if a > barea and len(vis) / len(pr) > .45:
                barea, best = a, (sum(p[0] for p in vis)/len(vis),
                                  sum(p[1] for p in vis)/len(vis))
        if best and barea > (out_w * out_h) * .0045:
            name = f['properties'].get('NAME') or ''
            labels.append((best[0], best[1], name, barea))

    labels.sort(key=lambda t: -t[3])
    # drop labels that would collide
    keep = []
    for x, y, name, a in labels:
        if all(abs(x-kx) > out_w*.085 or abs(y-ky) > out_h*.038 for kx, ky, _ in keep):
            keep.append((x, y, name))

    total = sum(s['area'] for s in shapes) or 1
    rng = []
    for s in sorted(shapes, key=lambda s: -s['area']):
        pts = [T(*p) for p in s['pts']]
        d = 'M' + 'L'.join(f'{round(a,1)},{round(b,1)}' for a, b in pts) + 'Z'
        rng.append({'band': s['band'], 'd': d,
                    'share': round(100.0 * s['area'] / total, 1)})

    # scale bar: a round number of km that lands near a fifth of the width
    m_per_unit = (bx1 - bx0) / out_w
    lat_mid = math.degrees(2*math.atan(math.exp(((by0+by1)/2)/R)) - math.pi/2)
    ground = m_per_unit * math.cos(math.radians(lat_mid))     # mercator -> ground
    target_km = ground * out_w * .2 / 1000.0
    nice = min([1,2,5,10,20,25,50,100,200,250,500,1000,2000,2500,5000],
               key=lambda v: abs(math.log(v / max(target_km, .001))))
    bar_units = nice * 1000.0 / ground

    return {'w': round(out_w), 'h': round(out_h), 'land': land,
            'labels': keep, 'shapes': rng,
            'scale': {'units': round(bar_units, 1), 'km': nice}}

if __name__ == '__main__':
    geo = json.load(open('georef.json'))
    ne = json.load(open('data/ne50.geojson'))
    os.makedirs('built', exist_ok=True)
    for slug in sys.argv[1:]:
        tr = json.load(open(f'traced/{slug}.json'))
        m = build(slug, tr, geo, ne)
        json.dump(m, open(f'built/{slug}.json', 'w'))
        print(f'{slug}: {m["w"]}x{m["h"]} land {len(m["land"])} labels {len(m["labels"])} '
              f'shapes {len(m["shapes"])} scale {m["scale"]["km"]}km')
