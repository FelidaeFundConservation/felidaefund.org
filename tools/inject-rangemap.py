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
    counts, shares = {}, {}
    for s in m['shapes']:
        counts[s['band']] = counts.get(s['band'], 0) + 1
        shares[s['band']] = shares.get(s['band'], 0.0) + s['share']
    res, pos = counts.get('resident', 0), counts.get('possible', 0)
    # Share of mapped range, not a count of shapes. The count is an
    # artifact of the tracing threshold and moved between 23 and 37 for
    # the cheetah as the filters changed; the area barely shifts.
    res_pc = round(shares.get('resident', 0))
    pos_pc = round(shares.get('possible', 0))

    land = '\n'.join(f'                  <path d="{d}"/>' for d in m['land'])
    rng = '\n'.join(
        f'                  <path class="rp rp--{s["band"]}" d="{s["d"]}" '
        f'data-band="{s["band"]}" data-share="{s["share"]}"/>'
        for s in m['shapes'])
    labels = '\n'.join(
        f'                  <text x="{x:.0f}" y="{y:.0f}">{html.escape(n)}</text>'
        for x, y, n in m['labels'])

    # Kilometres per viewBox unit, so the scale bar can be redrawn in the
    # frame at whatever zoom the reader is on.
    km_per_unit = m['scale']['km'] / m['scale']['units']

    bar = []
    if res:
        bar.append('<button type="button" class="rmtoggle" data-band="resident" aria-pressed="true">'
                   f'<span class="sw sw--resident"></span>Resident <span class="rmtoggle__n">{res_pc}%</span></button>')
    if pos:
        bar.append('<button type="button" class="rmtoggle" data-band="possible" aria-pressed="true">'
                   f'<span class="sw sw--possible"></span>Possibly resident <span class="rmtoggle__n">{pos_pc}%</span></button>')

    frag = f'''<figure class="prose-figure rangemap">
            <div class="rangemap__head">
              <div class="rangemap__bar">{''.join(bar)}</div>
              <p class="rangemap__readout" role="status" aria-live="polite"><span class="rangemap__hint"><span class="hint-hover">Hover an area to see its share of the range.</span><span class="hint-touch">Tap an area to see its share of the range.</span></span></p>
            </div>
            <div class="rangemap__frame" style="--rm-ar: {W} / {H}">
              <div class="rangemap__stage" tabindex="0" role="group" aria-label="Range map, {res} resident and {pos} possibly resident areas. Drag to move it, arrow keys to pan, plus and minus to zoom.">
                <svg class="rangemap__svg" viewBox="0 0 {W} {H}" data-base="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Range map: {res} resident and {pos} possibly resident populations.">
                <g class="rm-land">
{land}
                </g>
                <g class="rm-range">
{rng}
                </g>
                <g class="rm-labels" aria-hidden="true">
{labels}
                </g>
              </svg>
              </div>
              <p class="rangemap__cue" aria-hidden="true"><span class="rangemap__cue-pill">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v18M3 12h18"/><path d="m9 6 3-3 3 3M9 18l3 3 3-3M6 9l-3 3 3 3M18 9l3 3-3 3"/></svg>
                  Drag to explore the distribution</span></p>
              <div class="rangemap__scale" aria-hidden="true" data-kmpu="{km_per_unit:.6f}">
                <span class="rangemap__scale-bar"></span><span class="rangemap__scale-label"></span>
              </div>
              <div class="rangemap__zoom">
                <button type="button" class="rmzoom" data-zoom="in" aria-label="Zoom in">+</button>
                <button type="button" class="rmzoom" data-zoom="out" aria-label="Zoom out">&minus;</button>
                <button type="button" class="rmzoom rmzoom--reset" data-zoom="reset" aria-label="Reset the view">Reset</button>
              </div>
            </div>
          </figure>'''
    return frag, res + pos


CREDIT = re.compile(
    r'[ \t]*<p><em>(Distribution map courtesy of(?:(?!</em>).)*)</em></p>\n?', re.I | re.S)


def inject(page, slug, data_dir, ver):
    s = open(page, encoding='utf-8').read()
    pat = re.compile(r'<figure class="prose-figure"><img src="[^"]*' + re.escape(slug)
                     + r'-map-960\.webp"[^>]*/></figure>')
    m = pat.search(s)
    if not m:
        print(f'  no static map figure in {os.path.basename(page)}')
        return 0
    frag, n = build(slug, data_dir)

    # The IUCN credit was a paragraph of body prose sitting above the map.
    # It belongs to the map, so it moves inside the figure as a caption.
    credit = CREDIT.search(s)
    if credit:
        line = credit.group(1).strip()
        frag = frag.replace('</figure>',
                            f'              <figcaption class="rangemap__credit">{line}</figcaption>\n            </figure>')

    s = s[:m.start()] + frag + s[m.end():]
    if credit:
        s = CREDIT.sub('', s, count=1)
    if 'rangemap.css' not in s:
        s = s.replace('<link rel="stylesheet" href="page.css?v=',
                      f'<link rel="stylesheet" href="rangemap.css?v={ver}" />\n  '
                      '<link rel="stylesheet" href="page.css?v=', 1)
    if 'components/rangemap.js' not in s:
        s = s.replace('<script src="components/page.js?v=',
                      f'<script src="components/rangemap.js?v={ver}" defer></script>\n  '
                      '<script src="components/page.js?v=', 1)
    open(page, 'w', encoding='utf-8').write(s)
    print(f'  {os.path.basename(page)}: {n} populations')
    return n


if __name__ == '__main__':
    page, slug, data_dir, ver = sys.argv[1:5]
    inject(page, slug, data_dir, ver)
