"""Swap a species page's static distribution map for the live component.

The map is drawn from scratch: land, borders, labels and scale bar come
from Natural Earth (public domain), and the range shapes were traced out
of the IUCN map and georeferenced back onto it. No screenshot is used,
so the type, colour and framing are all ours.
"""
import json, re, sys, os, html

LABEL = {'resident': 'Resident', 'possible': 'Possibly resident'}


def build(slug, data_dir):
    m = json.load(open(os.path.join(data_dir, 'maps', f'{slug}-map.json')))
    W, H = m['w'], m['h']
    counts = {}
    for s in m['shapes']:
        counts[s['band']] = counts.get(s['band'], 0) + 1
    res, pos = counts.get('resident', 0), counts.get('possible', 0)

    land = '\n'.join(f'                  <path d="{d}"/>' for d in m['land'])
    rng = '\n'.join(
        f'                  <path class="rp rp--{s["band"]}" d="{s["d"]}" '
        f'data-band="{s["band"]}" data-share="{s["share"]}"/>'
        for s in m['shapes'])
    labels = '\n'.join(
        f'                  <text x="{x:.0f}" y="{y:.0f}">{html.escape(n)}</text>'
        for x, y, n in m['labels'])

    bw = m['scale']['units']
    bx, by = W * .035, H - H * .045
    scale = (f'                  <line x1="{bx:.0f}" y1="{by:.0f}" x2="{bx+bw:.0f}" y2="{by:.0f}"/>\n'
             f'                  <line x1="{bx:.0f}" y1="{by-5:.0f}" x2="{bx:.0f}" y2="{by+5:.0f}"/>\n'
             f'                  <line x1="{bx+bw:.0f}" y1="{by-5:.0f}" x2="{bx+bw:.0f}" y2="{by+5:.0f}"/>\n'
             f'                  <text x="{bx:.0f}" y="{by-10:.0f}">{m["scale"]["km"]:,} km</text>')

    bar = []
    if res:
        bar.append('<button type="button" class="rmtoggle" data-band="resident" aria-pressed="true">'
                   f'<span class="sw sw--resident"></span>Resident <span class="rmtoggle__n">{res}</span></button>')
    if pos:
        bar.append('<button type="button" class="rmtoggle" data-band="possible" aria-pressed="true">'
                   f'<span class="sw sw--possible"></span>Possibly resident <span class="rmtoggle__n">{pos}</span></button>')

    frag = f'''<figure class="prose-figure rangemap">
            <div class="rangemap__head">
              <div class="rangemap__bar">{''.join(bar)}</div>
              <p class="rangemap__readout" role="status" aria-live="polite"><span class="rangemap__hint"><span class="hint-hover">Hover an area to see its share of the range.</span><span class="hint-touch">Tap an area to see its share of the range.</span></span></p>
            </div>
            <div class="rangemap__stage">
              <svg class="rangemap__svg" viewBox="0 0 {W} {H}" role="img" aria-label="Range map: {res} resident and {pos} possibly resident populations.">
                <g class="rm-land">
{land}
                </g>
                <g class="rm-range">
{rng}
                </g>
                <g class="rm-labels" aria-hidden="true">
{labels}
                </g>
                <g class="rm-scale" aria-hidden="true">
{scale}
                </g>
              </svg>
            </div>
          </figure>'''
    return frag, res + pos


def inject(page, slug, data_dir, ver):
    s = open(page).read()
    pat = re.compile(r'<figure class="prose-figure"><img src="[^"]*' + re.escape(slug)
                     + r'-map-960\.webp"[^>]*/></figure>')
    m = pat.search(s)
    if not m:
        print(f'  no static map figure in {os.path.basename(page)}')
        return 0
    frag, n = build(slug, data_dir)
    s = s[:m.start()] + frag + s[m.end():]
    if 'rangemap.css' not in s:
        s = s.replace('<link rel="stylesheet" href="page.css?v=',
                      f'<link rel="stylesheet" href="rangemap.css?v={ver}" />\n  '
                      '<link rel="stylesheet" href="page.css?v=', 1)
    if 'components/rangemap.js' not in s:
        s = s.replace('<script src="components/page.js?v=',
                      f'<script src="components/rangemap.js?v={ver}" defer></script>\n  '
                      '<script src="components/page.js?v=', 1)
    open(page, 'w').write(s)
    print(f'  {os.path.basename(page)}: {n} populations')
    return n


if __name__ == '__main__':
    page, slug, data_dir, ver = sys.argv[1:5]
    inject(page, slug, data_dir, ver)
