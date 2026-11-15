"""Give each species page a contents rail beside the article.

The pages run six sections deep with no way to see the shape of them or
jump about. This lists the h2s in a sticky column and marks the one being
read.
"""
import glob, os, re, sys, html, unicodedata

OPEN = '<section class="page-body">\n      <div class="container">\n        <div class="prose reveal">'
H2 = re.compile(r'<h2(?P<attrs>[^>]*)>(?P<text>.*?)</h2>', re.S)
EMPTY = re.compile(r'\n *<div class="container" hidden>\n *<div>\s*</div>\n *</div>')


def slug(t):
    t = unicodedata.normalize('NFKD', t).replace(' ', ' ')
    t = re.sub(r'<[^>]+>', '', t)
    t = html.unescape(t)
    t = re.sub(r'[^a-zA-Z0-9]+', '-', t).strip('-').lower()
    return t or 'section'


def run(proto, only=None):
    n = 0
    for f in sorted(glob.glob(os.path.join(proto, 'species-*.html'))):
        if only and os.path.basename(f) != only:
            continue
        s = open(f, encoding='utf-8').read()
        if 'class="toc"' in s or OPEN not in s:
            continue
        start = s.index(OPEN)
        end = s.index('\n      </div>', start)
        body = s[start:end]

        items, used = [], set()
        def tag(m):
            if 'id=' in m.group('attrs'):
                return m.group(0)
            raw = m.group('text')
            sid = slug(raw)
            i = 2
            while sid in used:
                sid, i = f'{slug(raw)}-{i}', i + 1
            used.add(sid)
            label = html.unescape(re.sub(r'<[^>]+>', '', raw)).replace(' ', ' ').strip()
            items.append((sid, html.escape(label)))
            return f'<h2 id="{sid}"{m.group("attrs")}>{raw}</h2>'

        body = H2.sub(tag, body)
        if len(items) < 3:
            continue

        links = '\n'.join(
            f'              <li><a href="#{i}">{t}</a></li>' for i, t in items)
        nav = ('        <nav class="toc" aria-label="On this page">\n'
               '          <p class="toc__label">Contents</p>\n'
               '          <ul class="toc__list">\n' + links + '\n'
               '          </ul>\n'
               '        </nav>\n')

        body = body.replace(
            '<div class="container">\n        <div class="prose reveal">',
            '<div class="container page-body__grid">\n' + nav + '        <div class="prose reveal">', 1)

        s = s[:start] + body + s[end:]
        s = EMPTY.sub('', s)
        open(f, 'w', encoding='utf-8').write(s)
        n += 1
    print(f'{n} page(s) given a contents rail')


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
