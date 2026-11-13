"""Build the previous/next species navigation.

The live site has it on all 40 pages; the port to the prototype dropped
it. Order is alphabetical, which is how the index is ordered, so moving
through the pages matches moving along the grid. Thumbnails are reused
from the index, which already carries a working URL per species (the
autosized cache serves a different maximum width for each one).
"""
import json, os, re, sys

CARD = re.compile(
    r'<a class="species-card[^"]*" href="(species-[a-z0-9-]+\.html)">\s*'
    r'<div class="species-card__media">\s*<img src="([^"]+)"[^>]*alt="([^"]+)"',
    re.S)


def read_index(proto):
    s = open(os.path.join(proto, 'learn-cats.html'), encoding='utf-8').read()
    out = []
    for href, thumb, name in CARD.findall(s):
        out.append({'href': href, 'thumb': thumb, 'name': name})
    return out


def frag(prev, nxt):
    def side(item, kind, label, arrow):
        if not item:
            return f'<span class="spnav__slot spnav__slot--empty" aria-hidden="true"></span>'
        order = ('__media', '__text') if kind == 'prev' else ('__text', '__media')
        media = (f'<span class="spnav__media"><img src="{item["thumb"]}" alt="" '
                 f'loading="lazy" width="256" height="256" /></span>')
        text = (f'<span class="spnav__text"><span class="spnav__label">{arrow} {label}</span>'
                f'<span class="spnav__name">{item["name"]}</span></span>')
        inner = media + text if kind == 'prev' else text + media
        return (f'<a class="spnav__slot spnav__slot--{kind}" href="{item["href"]}" '
                f'rel="{kind}">{inner}</a>')

    return ('''      <nav class="spnav" aria-label="More species">
        <div class="container">
          <div class="spnav__inner">
            '''
            + side(prev, 'prev', 'Previous', '&larr;') + '\n            '
            + side(nxt, 'next', 'Next', '&rarr;')
            + '''
          </div>
        </div>
      </nav>
''')


def inject(proto, only=None):
    items = read_index(proto)
    by_href = {i['href']: n for n, i in enumerate(items)}
    done = 0
    for n, it in enumerate(items):
        if only and it['href'] != only:
            continue
        path = os.path.join(proto, it['href'])
        if not os.path.exists(path):
            continue
        s = open(path, encoding='utf-8').read()
        block = frag(items[n - 1] if n > 0 else None,
                     items[n + 1] if n + 1 < len(items) else None)
        s = re.sub(r'    <nav class="spnav".*?</nav>\n', '', s, flags=re.S)
        anchor = '    <section class="support">'
        if anchor not in s:
            anchor = '  </main>'
        s = s.replace(anchor, block + anchor, 1)
        open(path, 'w', encoding='utf-8').write(s)
        done += 1
    print(f'{done} page(s) given prev/next, from {len(items)} species')


if __name__ == '__main__':
    inject(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
