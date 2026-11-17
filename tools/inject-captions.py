"""Carry the photo captions across from the live pages.

The live site hides them behind an asterisk button, so the credit is
there but nobody reads it. The photographers gave these images on the
understanding that they are credited, so the caption goes under the
picture where a caption belongs.
"""
import re, sys, html, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE = os.path.join(ROOT, 'tools', 'live')
PROTO = os.path.join(ROOT, 'prototype')

# .../101-200/cheetah-vjHrP78-4K-196-960.webp -> cheetah-vjHrP78-4K-196
STEM = re.compile(r'igallery/original/[^"\s]*?/([A-Za-z0-9._-]+?)(?:-\d+)?\.(?:webp|jpe?g|png)',
                  re.I)

def stem(url):
    m = STEM.search(url)
    if not m:
        return None
    s = m.group(1)
    # the size suffix is the trailing -NNN; the id before it stays
    return re.sub(r'-\d{2,4}$', '', s) if re.search(r'-\d{2,4}$', s) else s

# The live captions carry a few CMS artefacts. Clean them on the way in.
SELF = re.compile(r'<a href="/learn/cats/([a-z0-9-]+)"[^>]*>(.*?)</a>', re.S)

def tidy(cap, slug):
    # Joomla auto-links the species name in its own caption, so every page
    # links to itself. Keep the cross-references, drop the self-link.
    def link(m):
        to, text = m.group(1), m.group(2)
        return text if to == slug else '<a href="species-%s.html">%s</a>' % (to, text)
    cap = SELF.sub(link, cap)
    cap = cap.replace('http://creativecommons.org', 'https://creativecommons.org')
    # "copyright ©IngridVekemans" — the credit runs into the name.
    cap = cap.replace('\u00a9IngridVekemans', '\u00a9 Ingrid Vekemans')
    cap = re.sub(r'\u00a9(?=[A-Za-z])', '\u00a9 ', cap)
    return cap


def captions(live_html):
    """stem -> caption inner HTML, read out of the live figures."""
    out = {}
    for fig in re.findall(r'<figure\b.*?</figure>', live_html, re.S):
        cap = re.search(r'<figcaption[^>]*>(.*?)</figcaption>', fig, re.S)
        if not cap:
            continue
        t = cap.group(1).strip()
        t = re.sub(r'^<p[^>]*>|</p>$', '', t).strip()   # unwrap the single <p>
        t = re.sub(r'\s+', ' ', t)
        t = t.replace(' ', ' ').replace('&nbsp;', ' ')
        if not re.sub(r'<[^>]+>', '', t).strip():
            continue
        for u in re.findall(r'igallery/original/[^"\s,]+', fig):
            s = stem(u)
            if s:
                out.setdefault(s, t)
    return out

FIG = re.compile(r'<figure class="(page-hero[^"]*|prose-figure[^"]*)">(.*?)</figure>', re.S)

def inject(path, caps):
    src = open(path).read()
    added = []

    def one(m):
        cls, inner = m.group(1), m.group(2)
        if '<figcaption' in inner or 'rangemap' in cls:
            return m.group(0)
        u = re.search(r'src="([^"]+)"', inner)
        s = stem(u.group(1)) if u else None
        cap = caps.get(s)
        if not cap:
            return m.group(0)
        added.append(s)
        if cls.startswith('page-hero'):
            # The hero is full bleed, so its caption needs the page gutter.
            tail = ('\n      <figcaption class="container">'
                    + cap + '</figcaption>\n    ')
        else:
            tail = '<figcaption>' + cap + '</figcaption>'
        return '<figure class="%s">%s%s</figure>' % (cls, inner.rstrip(), tail)

    out = FIG.sub(one, src)
    if out != src:
        open(path, 'w').write(out)
    return added

if __name__ == '__main__':
    slugs = sys.argv[1:] or [os.path.basename(p)[len('species-'):-len('.html')]
                             for p in sorted(__import__('glob').glob(
                                 os.path.join(PROTO, 'species-*.html')))]
    tot = 0
    for slug in slugs:
        live = os.path.join(LIVE, 'learn__cats__%s.html' % slug)
        page = os.path.join(PROTO, 'species-%s.html' % slug)
        if not (os.path.exists(live) and os.path.exists(page)):
            print('skip %s (missing source)' % slug); continue
        caps = {k: tidy(v, slug) for k, v in captions(open(live).read()).items()}
        got = inject(page, caps)
        tot += len(got)
        print('%-30s %d caption(s) available, %d placed' % (slug, len(caps), len(got)))
    print('--- %d captions placed' % tot)
