import glob, os, sys, json, traceback
sys.setrecursionlimit(100000)
import trace as T

rows, failed = [], []
for f in sorted(glob.glob('maps/*.jpg')):
    slug = os.path.basename(f)[:-4]
    try:
        T.main(f, f'traced/{slug}.json')
        d = json.load(open(f'traced/{slug}.json'))
        c = {}
        for s in d['shapes']:
            c[s['band']] = c.get(s['band'], 0) + 1
        rows.append((slug, len(d['shapes']), c.get('resident', 0), c.get('possible', 0),
                     sum(len(s['d']) for s in d['shapes'])))
    except Exception as e:
        failed.append((slug, repr(e)[:90]))

print(f'\n{"species":34} {"shapes":>7} {"res":>5} {"poss":>5} {"path KB":>8}')
for slug, n, r, p, ch in rows:
    print(f'{slug[:34]:34} {n:7} {r:5} {p:5} {ch/1024:8.1f}')
print(f'\nsucceeded {len(rows)} / {len(rows)+len(failed)}')
for s, e in failed:
    print('  FAILED', s, e)
tot = sum(r[1] for r in rows)
kb = sum(r[4] for r in rows)/1024
print(f'total shapes {tot}, total path data {kb:.0f}KB')
