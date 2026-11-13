"""Swap a species page's static distribution map for the live component."""
import json, re, sys, os

def build(slug, data_dir):
    d = json.load(open(os.path.join(data_dir, f'{slug}-map.json')))
    shapes = sorted(d['shapes'], key=lambda s: -s['area'])
    total = sum(s['area'] for s in shapes) or 1
    counts = {}
    for s in shapes:
        counts[s['band']] = counts.get(s['band'], 0) + 1
    paths = '\n'.join(
        f'              <path class="rp rp--{s["band"]}" d="{s["d"]}" '
        f'data-band="{s["band"]}" data-share="{100.0*s["area"]/total:.1f}"/>'
        for s in shapes)

    # Crop to the range itself. The IUCN viewer frames every species in the
    # same square, so most maps carry dead ocean on two sides; a narrow
    # range like the snow leopard's wastes most of the frame. Cropping to
    # the data makes the map wider than it is tall wherever the range is.
    xs, ys = [], []
    for sh in shapes:
        for pt in sh['d'][1:-1].split('L'):
            x, y = pt.split(',')
            xs.append(float(x)); ys.append(float(y))
    pad = max(d['w'], d['h']) * .025
    vx0 = max(0, min(xs) - pad); vy0 = max(0, min(ys) - pad)
    vx1 = min(d['w'], max(xs) + pad); vy1 = min(d['h'], max(ys) + pad)
    vb = f'{vx0:.0f} {vy0:.0f} {vx1-vx0:.0f} {vy1-vy0:.0f}'
    res, pos = counts.get('resident', 0), counts.get('possible', 0)
    # IUCN's own legend is covered: the toggles above the map replace it,
    # and two legends saying the same thing in different styles is noise.
    lg = d.get('legend')
    fill = d.get('legendFill', '#ddd9d0')
    mask = ('' if not lg else
            f'\n                <rect class="rp-mask" x="{lg["x"]}" y="{lg["y"]}" '
            f'width="{lg["w"]}" height="{lg["h"]}" rx="3" fill="{fill}"/>')
    bar = []
    if res:
        bar.append('<button type="button" class="rmtoggle" data-band="resident" aria-pressed="true">'
                   f'<span class="sw sw--resident"></span>Resident <span class="rmtoggle__n">{res}</span></button>')
    if pos:
        bar.append('<button type="button" class="rmtoggle" data-band="possible" aria-pressed="true">'
                   f'<span class="sw sw--possible"></span>Possibly resident <span class="rmtoggle__n">{pos}</span></button>')
    return f'''<figure class="prose-figure rangemap">
            <div class="rangemap__bar">{''.join(bar)}</div>
            <p class="rangemap__readout" role="status" aria-live="polite"><span class="rangemap__hint"><span class="hint-hover">Point at a population.</span><span class="hint-touch">Tap a population.</span></span></p>
            <div class="rangemap__stage">
              <svg class="rangemap__svg" viewBox="{vb}" role="img" aria-label="Range map: {res} resident and {pos} possibly resident populations.">
                <image class="rangemap__base" href="https://felidaefund.org/media/cache/autosized/images/static/{slug}-map-960.webp" x="0" y="0" width="{d['w']}" height="{d['h']}" preserveAspectRatio="none"/>{mask}
{paths}
              </svg>
            </div>
          </figure>''', res + pos

def inject(page, slug, data_dir, ver):
    s = open(page).read()
    pat = re.compile(r'<figure class="prose-figure"><img src="[^"]*' + re.escape(slug)
                     + r'-map-960\.webp"[^>]*/></figure>')
    m = pat.search(s)
    if not m:
        print(f'  no static map figure found in {os.path.basename(page)}')
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
