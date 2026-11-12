import json, sys, html

d = json.load(open(sys.argv[1]))
W, H, shapes = d['w'], d['h'], d['shapes']
total = sum(s['area'] for s in shapes)

LABEL = {'resident': 'Resident', 'possible': 'Possibly resident'}
out = []
for i, s in enumerate(shapes):
    share = 100.0 * s['area'] / total
    out.append(
        f'<path class="rp rp--{s["band"]}" d="{s["d"]}" '
        f'data-band="{s["band"]}" data-share="{share:.1f}" data-i="{i}"/>'
    )
print(f'{len(shapes)} shapes, total range area {total}px')
open(sys.argv[2], 'w').write('\n'.join(out))

counts = {}
for s in shapes:
    counts[s['band']] = counts.get(s['band'], 0) + 1
areas = {}
for s in shapes:
    areas[s['band']] = areas.get(s['band'], 0) + s['area']
meta = {
    'w': W, 'h': H, 'total': total,
    'counts': counts,
    'pct': {k: round(100.0 * v / total, 1) for k, v in areas.items()},
    'biggest': round(100.0 * shapes[0]['area'] / total, 1),
}
json.dump(meta, open(sys.argv[3], 'w'))
print(meta)
