import re, html, os, sys
LIVE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'live')
OUT  = '/Users/irene/code/felidaefund.org/prototype'
V    = '?v=14'

def txt(s): return html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',s))).strip()
def esc(s): return html.escape(s, quote=False)

def raw_main(s):
    i = s.find('<main id="main_content"')
    return '' if i < 0 else s[i:s.find('</main>', i)]

def main_block(s):
    i = s.find('<main id="main_content"')
    if i < 0: return ''
    seg = s[i:s.find('</main>', i)]
    # Joomla puts site-wide modules after the article but still inside
    # <main>: a volunteer promo, a newsletter block. They were being read
    # as body copy, so the same 1,000 characters landed at the bottom of
    # 80 pages, and on Photos & Videos the promo became the page lede.
    m = re.search(r'<(?:section|div)[^>]*\bafter-content\b', seg)
    if m: seg = seg[:m.start()]
    # the gallery-of-galleries widget: its card titles were leaking in as
    # headings followed by a "View Gallery" paragraph
    seg = re.sub(r'<div[^>]*\big-menu-grid\b.*?(?=<div class="after-content|\Z)', ' ', seg, flags=re.S)
    # the article listing is rendered as cards instead
    if 'blog-item' in seg:
        m2 = re.search(r'<div[^>]*\bcom-content-category-blog\b', seg)
        if m2: seg = seg[:m2.start()]
    # Joomla chrome that isn't body copy: hidden captions, scripts, nav, forms
    for pat in (r'<aside\b[^>]*>.*?</aside>',
                r'<div[^>]*\bigui-scope\b.*?<!--\s*/igallery\s*-->',
                r'<div[^>]*\big-gallery-wrapper\b.*?</ul>\s*</div>',
                r'<figcaption\b.*?</figcaption>', r'<script\b.*?</script>',
                r'<style\b.*?</style>', r'<nav\b.*?</nav>',
                r'<form\b.*?</form>', r'<button\b.*?</button>',
                r'<span class="visually-hidden">.*?</span>'):
        seg = re.sub(pat, ' ', seg, flags=re.S)
    return seg

NOISE = re.compile(r'^(show photo caption|home$|learn$|about us$|projects$|take action$)', re.I)
CREDIT = re.compile(r'(photo courtesy|copyright ©|used with permission|all rights reserved)', re.I)

# ── Inline links inside body copy ────────────────────────────────────
# The live pages carry ~380 links inside paragraphs and lists: PDF
# downloads, cross-references, outbound sources. Stripping tags to get
# clean text threw all of them away, so body copy said "Download the
# flyer here" with nothing to click. Keep them, and repoint the ones
# that have a prototype page.
LINKMAP = {
 "/projects/research/bay-area-puma-project":"project-bapp.html",
 "/projects/research/bay-area-bobcat-project":"project-bobcat.html",
 "/projects/research/pumalink":"project-pumalink.html",
 "/projects/research/wild-cat-health-project":"project-wildcat-health.html",
 "/projects/research/patagonia-cats-project":"project-patagonia.html",
 "/projects/research/tsavo-cheetah-project":"project-tsavo.html",
 "/projects/research/bhutan-wild-cat-health-project":"project-bhutan.html",
 "/projects/community/living-with-lions":"project-living-with-lions.html",
 "/projects/community/cat-aware":"project-cat-aware.html",
 "/projects/community/wilde-pod":"project-wilde-pod.html",
 "/projects/community/wilde-backyard":"project-wilde-backyard.html",
 "/projects/archive":"projects.html", "/projects/research":"projects.html",
 "/projects/community":"projects.html", "/projects":"projects.html",
 "/about/mission":"mission.html", "/about":"about.html", "/science":"science.html",
 "/news":"news.html", "/events":"events.html", "/kids":"kids.html", "/store":"store.html",
 "/learn/cats":"learn-cats.html",
 "/learn/protecting-healthy-ecosystems":"learn-ecosystems.html",
 "/learn/living-alongside-wild-cats":"learn-living-alongside.html",
 "/learn/safety-essentials-wild-cats":"learn-safety.html",
 "/learn/media":"learn-media.html",
 "/take-action/volunteer":"volunteer.html",
 "/take-action/spread-awareness":"spread-awareness.html",
 "/take-action/community-science":"community-science.html",
 "/take-action/more-ways-to-help":"ways-to-donate.html",
 "/take-action":"take-action.html",
}
SPECIES_SLUGS = set()   # filled in once species.json is loaded

def rewrite_href(h):
    """(href, is_external). Internal pages go local; assets stay on the
    live domain, same as the images."""
    h = html.unescape(h).strip().replace(' ', '%20')
    if h.startswith(('mailto:', 'tel:', '#')): return h, False
    for host in ('https://www.felidaefund.org', 'https://felidaefund.org', 'http://www.felidaefund.org'):
        if h.startswith(host): h = h[len(host):] or '/'
    if h.startswith('/'):
        path = h.split('?')[0].split('#')[0].rstrip('/') or '/'
        if path.startswith('/learn/cats/'):
            slug = path.rsplit('/', 1)[1]
            if slug in SPECIES_SLUGS: return f"species-{slug}.html", False
        if path in LINKMAP: return LINKMAP[path], False
        # assets (pdf, images, media) and anything without a prototype page
        return 'https://felidaefund.org' + h, True
    return h, True

KEEP = {'a', 'strong', 'em', 'b', 'i'}

def inline_html(frag):
    """Escaped text with the whitelisted inline tags preserved."""
    out, pos = [], 0
    for m in re.finditer(r'<[^>]+>', frag):
        out.append(esc(html.unescape(frag[pos:m.start()])))
        tag = m.group(0); pos = m.end()
        name = re.match(r'</?\s*([a-zA-Z0-9]+)', tag)
        if not name or name.group(1).lower() not in KEEP: continue
        name = name.group(1).lower()
        if tag.startswith('</'):
            out.append(f'</{name}>')
        elif name == 'a':
            href = re.search(r'href="([^"]*)"', tag)
            if not href: continue
            url, ext = rewrite_href(href.group(1))
            out.append(f'<a href="{url}"' + (' target="_blank" rel="noopener"' if ext else '') + '>')
        else:
            out.append(f'<{name}>')
    out.append(esc(html.unescape(frag[pos:])))
    s = re.sub(r'\s+', ' ', ''.join(out)).strip()
    # drop links left empty or unbalanced by the tag filtering
    s = re.sub(r'<a [^>]*>\s*</a>', '', s)
    return s


def balanced(seg, start, tag):
    """End index of the tag opened at `start`, counting nested opens."""
    depth, i = 0, start
    pat = re.compile(rf'</?{tag}\b[^>]*>', re.I)
    while True:
        m = pat.search(seg, i)
        if not m: return len(seg)
        depth += -1 if m.group(0).startswith('</') else 1
        i = m.end()
        if depth == 0: return i

def list_html(markup, depth=0):
    """Render a ul/ol, keeping nested lists nested. The live pages use
    numbered lists with sub-points; flattening them lost the structure."""
    tag = 'ol' if re.match(r'\s*<ol', markup, re.I) else 'ul'
    inner = markup[markup.index('>') + 1: markup.rindex('</')]
    cls = ' class="prose-list"' if depth == 0 else ' class="prose-sublist"'
    rows, i = [], 0
    while True:
        m = re.compile(r'<li\b[^>]*>', re.I).search(inner, i)
        if not m: break
        end = balanced(inner, m.start(), 'li')
        li = inner[m.end(): inner.rindex('</li>', 0, end) if '</li>' in inner[:end] else end]
        nested = ''
        nm = re.compile(r'<(ul|ol)\b[^>]*>', re.I).search(li)
        if nm:
            ne = balanced(li, nm.start(), nm.group(1))
            nested = list_html(li[nm.start():ne], depth + 1)
            li = li[:nm.start()] + li[ne:]
        body = inline_html(li)
        if body or nested: rows.append(f'<li>{body}{nested}</li>')
        i = end
    if not rows: return ''
    return f'<{tag}{cls}>' + ''.join(rows) + f'</{tag}>'


def best_src(tag):
    """Largest variant offered by an <img>, from srcset or src."""
    cands = []
    ss = re.search(r'srcset="([^"]+)"', tag)
    if ss:
        for part in ss.group(1).split(','):
            bits = part.strip().split()
            if not bits: continue
            w = int(bits[1][:-1]) if len(bits) > 1 and bits[1].endswith('w') else 0
            cands.append((w, bits[0]))
    sr = re.search(r'src="([^"]+)"', tag)
    if sr:
        w = re.search(r'-(\d{2,4})\.(?:webp|jpg|jpeg|png)$', sr.group(1))
        cands.append((int(w.group(1)) if w else 1, sr.group(1)))
    cands = [(w, u) for w, u in cands if 'logo' not in u.lower() and not u.endswith('.svg')]
    if not cands: return None
    w, url = max(cands)
    if w <= 1:
        # no size in the filename or srcset: trust the tag, and only treat
        # it as an icon if it actually declares small dimensions
        attr = re.search(r'\bwidth="(\d+)"', tag)
        w = int(attr.group(1)) if attr else 1000
    if url.startswith('/'): url = 'https://felidaefund.org' + url.replace(' ', '%20')
    alt = re.search(r'alt="([^"]*)"', tag)
    return (url, html.unescape(alt.group(1)) if alt else '', w)

def photo_key(url):
    f = url.split('/')[-1]
    return re.sub(r'-\d{2,4}(?:-\d+-\d+)?(?:-c)?\.(?:webp|jpg|jpeg|png)$', '', f, flags=re.I)

def figure_html(url, alt, caption='', width=0):
    """A picture in the body flow.

    Small source images are held to their own size instead of being
    blown up across the column, and a YouTube still is turned back into
    a link to the video rather than posing as a photograph.
    """
    yt = re.search(r'img\.youtube\.com/vi/([A-Za-z0-9_-]{6,})/', url)
    cls = 'prose-figure'
    if width and width < 400: cls += ' prose-figure--small'
    if yt: cls += ' prose-figure--video'
    if yt and not caption: caption = 'Watch on YouTube'
    cap = f'<figcaption>{esc(caption)}</figcaption>' if caption else ''
    img = f'<img src="{url}" alt="{esc(alt)}" loading="lazy" />'
    if yt:
        img = (f'<a href="https://www.youtube.com/watch?v={yt.group(1)}" '
               f'target="_blank" rel="noopener">{img}</a>')
    return f'<figure class="{cls}">{img}{cap}</figure>' 


def blocks(seg, cap=80):
    """Ordered content blocks. Lists are scanned with balanced matching so
    a nested <ol> stays inside its parent instead of being re-read as a
    separate block."""
    out, i = [], 0
    opener = re.compile(r'<(h2|h3|p|ul|ol|figure|img)\b[^>]*>', re.I)
    while len(out) < cap:
        m = opener.search(seg, i)
        if not m: break
        kind = m.group(1).lower()
        if kind == 'img':
            i = m.end()
            got = best_src(m.group(0))
            if got and got[2] >= 200:
                out.append(('figure', figure_html(got[0], got[1], '', got[2])))
            continue
        stop = balanced(seg, m.start(), kind)
        whole = seg[m.start():stop]
        i = stop
        if kind == 'figure':
            im = re.search(r'<img[^>]+>', whole)
            got = best_src(im.group(0)) if im else None
            capm = re.search(r'<figcaption[^>]*>(.*?)</figcaption>', whole, re.S)
            caption = txt(capm.group(1)) if capm else ''
            if got and got[2] >= 200 and not CREDIT.search(caption):
                out.append(('figure', figure_html(got[0], got[1], caption, got[2])))
            continue
        if kind in ('ul', 'ol'):
            flat = [txt(li) for li in re.findall(r'<li[^>]*>(.*?)</li>', whole, re.S)]
            flat = [t for t in flat if t and not NOISE.match(t)]
            if not (1 < len(flat) <= 45): continue
            rendered = list_html(whole)
            if rendered: out.append(('list', {'html': rendered, 'items': flat}))
            continue
        inner = whole[whole.index('>') + 1: whole.rindex('</')] if '</' in whole else ''
        if kind == 'p' and '<img' in inner:
            for im in re.findall(r'<img[^>]+>', inner):
                got = best_src(im)
                if got and got[2] >= 200:
                    out.append(('figure', figure_html(got[0], got[1], '', got[2])))
            inner = re.sub(r'<img[^>]+>', ' ', inner)
        t = txt(inner)
        if not t or NOISE.match(t): continue
        has_link = '<a ' in inner
        if kind == 'p' and ((len(t) < 25 and not has_link) or len(t) > 900): continue
        if CREDIT.search(t): continue
        if kind in ('h2', 'h3') and (len(t) < 3 or len(t) > 90): continue
        out.append((kind, inline_html(inner)))
    ded, seen = [], set()
    for k, v in out:
        key = (k, v['html'] if k == 'list' else v)
        if key in seen: continue
        seen.add(key); ded.append((k, v))
    return ded

def drop_hero_dupe(bs, hero_url):
    """The hero already shows that picture at the top of the page."""
    if not hero_url: return bs
    key = photo_key(hero_url)
    out = []
    for k, v in bs:
        if k == 'figure':
            m = re.search(r'src="([^"]+)"', v)
            if m and photo_key(m.group(1)) == key: continue
        out.append((k, v))
    return out


def drop_orphan_headings(bs):
    """A heading with nothing under it. Happens when the content beneath
    it was a widget we render elsewhere (the Objectives list becomes the
    objective cards) or something the porter does not carry over."""
    rank = {'h2': 2, 'h3': 3, 'h4': 4}
    # removing one orphan can orphan the heading above it, so repeat
    # until nothing changes
    while True:
        out = []
        for i, (kind, val) in enumerate(bs):
            if kind in rank:
                has_body = False
                for k2, _ in bs[i+1:]:
                    if k2 in rank and rank[k2] <= rank[kind]: break
                    has_body = True; break
                if not has_body: continue
            out.append((kind, val))
        if len(out) == len(bs): return out
        bs = out


def hero_img(seg):
    """Biggest available variant of the first real photo in the region.

    Joomla serves a 256px thumbnail in src and the larger sizes in srcset,
    so taking src alone gives a thumbnail stretched across a 1280px hero.
    """
    for m in re.finditer(r'<(?:img|source)\b[^>]*>', seg):
        tag = m.group(0)
        cands = []
        ss = re.search(r'srcset="([^"]+)"', tag)
        if ss:
            for part in ss.group(1).split(','):
                bits = part.strip().split()
                if not bits: continue
                w = int(bits[1][:-1]) if len(bits) > 1 and bits[1].endswith('w') else 0
                cands.append((w, bits[0]))
        sr = re.search(r'src="([^"]+)"', tag)
        if sr:
            w = re.search(r'-(\d{2,4})\.(?:webp|jpg|jpeg|png)$', sr.group(1))
            cands.append((int(w.group(1)) if w else 1, sr.group(1)))
        cands = [(w, u) for w, u in cands
                 if 'logo' not in u.lower() and not u.endswith('.svg') and '/thumbs/' not in u]
        if not cands: continue
        w, src = max(cands)
        if w < 600: continue          # too small to carry a hero band
        if src.startswith('/'): src = 'https://felidaefund.org' + src
        alt = re.search(r'alt="([^"]*)"', tag)
        return src, (alt.group(1) if alt else '')
    return None, ''

# ── Image galleries ──────────────────────────────────────────────────
# Joomla renders galleries with the iGallery plugin: a widget div whose
# list items each hold a thumbnail, a link and a hidden caption. Read as
# prose that turns into a bullet list of alt text ("img 1584"), which is
# how the Bay Area Bobcat page ended up with a card full of filenames.
# Pull the pictures out as a real gallery and keep the widget out of the
# body copy.
def gallery_items(seg):
    """Pictures from an iGallery block.

    The widget ships each photo twice, at lightbox size and as a 130px
    thumbnail, so deduplicating on the URL alone put every picture in
    the grid twice: one sharp, one a thumbnail stretched to card width.
    Group by the photo's own name and keep the widest variant.
    """
    def name_and_width(url):
        f = url.split('/')[-1]
        m = re.search(r'^(.*?)-(\d+)-(\d+)-\d+(?:-c)?\.(?:webp|jpg|jpeg|png)$', f, re.I)
        if m: return m.group(1), int(m.group(2))
        return re.sub(r'\.(?:webp|jpg|jpeg|png)$', '', f, flags=re.I), 0

    best = {}
    for li in re.findall(r'<li[^>]*>(.*?)</li>', seg, re.S):
        if 'igallery' not in li: continue
        m = re.search(r'src="(/images/igallery/[^"]+)"', li)
        if not m: continue
        url = m.group(1)
        d = re.search(r'ig-lightbox-description-content"[^>]*>(.*?)</div>', li, re.S)
        cap = txt(d.group(1)) if d else ''
        alt = re.search(r'alt="([^"]*)"', li)
        alt = html.unescape(alt.group(1)) if alt else ''
        key, width = name_and_width(url)
        prev = best.get(key)
        if prev and prev[0] >= width: 
            # keep the wider file, but take a caption if this copy has one
            if cap and not prev[2]: best[key] = (prev[0], prev[1], cap, prev[3])
            continue
        best[key] = (width, 'https://felidaefund.org' + url, cap or (prev[2] if prev else ''),
                     alt or (prev[3] if prev else ''))
    return [(u, cap, alt) for _, (w, u, cap, alt) in best.items()]

def gallery_html(items, heading="Photos & videos"):
    if len(items) < 3: return ''
    cells = []
    for n, (url, cap, alt) in enumerate(items[:18]):
        d = f' reveal-delay-{n % 4}' if n % 4 else ''
        caption = f'\n            <figcaption>{esc(cap)}</figcaption>' if cap else ''
        cells.append(f"""          <figure class="shot reveal{d}">
            <img src="{url}" alt="{esc(alt or cap or heading)}" loading="lazy" />{caption}
          </figure>""")
    return f"""
    <section class="gallery-section">
      <div class="container">
        <p class="section-label reveal">Gallery</p>
        <h2 class="section-title reveal">{esc(heading)}</h2>
        <div class="shot-grid">
{chr(10).join(cells)}
        </div>
      </div>
    </section>
"""


def gallery_menu(seg):
    """The other iGallery shape: cards linking to sub-galleries, each with
    a cover image, a title and an item count. Photos & Videos and Science
    use this; the sub-galleries themselves are not ported, so the cards
    link to the live site."""
    out = []
    # the markup wraps attributes across lines, so slice between each
    # card marker rather than matching a fixed tag shape
    marks = [m.start() for m in re.finditer(r'ig-menu-grid-link', seg)]
    blocks = [seg[a:b] for a, b in zip(marks, marks[1:] + [min(len(seg), marks[-1] + 1600)])] if marks else []
    for blk in blocks:
        img = re.search(r'src="([^"]+)"', blk)
        title = re.search(r'class="h4 title">(.*?)</h2>', blk, re.S)
        count = re.search(r'class="details h5">(.*?)</div>', blk, re.S)
        href = re.search(r'<a href="([^"]+)"', blk)
        if not (img and title): continue
        url = img.group(1)
        if url.startswith('/'): url = 'https://felidaefund.org' + url
        link = href.group(1) if href else ''
        if link.startswith('/'): link = 'https://felidaefund.org' + link
        out.append((url, txt(title.group(1)), txt(count.group(1)) if count else '', link))
    return out

def gallery_menu_html(items, heading="Photo galleries"):
    if not items: return ''
    cells = []
    for n, (url, title, count, link) in enumerate(items):
        d = f' reveal-delay-{n % 4}' if n % 4 else ''
        meta = f'<p class="rel-card__label">{esc(count)}</p>' if count else ''
        cells.append(f"""          <a class="rel-card reveal{d}" href="{link}" target="_blank" rel="noopener">
            <div class="rel-card__media"><img src="{url}" alt="{esc(title)}" loading="lazy" /></div>
            <div class="rel-card__body">
              {meta}
              <h3>{esc(title)}</h3>
            </div>
          </a>""")
    return f"""
    <section class="gallery-section">
      <div class="container">
        <p class="section-label reveal">Galleries</p>
        <h2 class="section-title reveal">{esc(heading)}</h2>
        <div class="rel-grid">
{chr(10).join(cells)}
        </div>
      </div>
    </section>
"""


# ── Article listings ─────────────────────────────────────────────────
# The News page is a Joomla category blog: each item is a card with a
# title, date, image, standfirst and a Read More button. Read as prose
# it produced a run of headings followed by the word "Read More".
def article_items(seg):
    marks = [m.start() for m in re.finditer(r'class="[^"]*blog-item[^"]*"', seg)]
    if not marks: return []
    blocks = [seg[a:b] for a, b in zip(marks, marks[1:] + [len(seg)])]
    out = []
    for blk in blocks:
        t = re.search(r'<h2[^>]*>(.*?)</h2>', blk, re.S)
        if not t: continue
        href = re.search(r'<a[^>]+href="([^"]+)"', t.group(1)) or re.search(r'readmore.*?href="([^"]+)"', blk, re.S)
        date = re.search(r'publication-date"[^>]*>(.*?)</span>', blk, re.S)
        img  = re.search(r'newsflash-image.*?<img[^>]+src="([^"]+)"', blk, re.S)
        prev = re.search(r'preview-text"[^>]*>\s*<p>(.*?)</p>', blk, re.S)
        url, _ = rewrite_href(href.group(1)) if href else ('', False)
        cover = img.group(1) if img else ''
        if cover.startswith('/'): cover = 'https://felidaefund.org' + cover.replace(' ', '%20')
        out.append((url, txt(t.group(1)), txt(date.group(1)) if date else '',
                    txt(prev.group(1)) if prev else '', cover))
    return out

def article_list_html(items, heading="Latest stories"):
    if len(items) < 2: return ''
    cells = []
    for n, (url, title, date, standfirst, cover) in enumerate(items):
        d = f' reveal-delay-{n % 3}' if n % 3 else ''
        ext = ' target="_blank" rel="noopener"' if url.startswith('http') else ''
        media = (f'<div class="rel-card__media"><img src="{cover}" alt="" loading="lazy" /></div>'
                 if cover else '')
        meta = f'<p class="rel-card__label">{esc(date)}</p>' if date else ''
        body = f'<p>{esc(standfirst)}</p>' if standfirst else ''
        cells.append(f"""          <a class="rel-card reveal{d}" href="{url or '#'}"{ext}>
            {media}
            <div class="rel-card__body">
              {meta}
              <h3>{esc(title)}</h3>
              {body}
            </div>
          </a>""")
    return f"""
    <section class="gallery-section">
      <div class="container">
        <p class="section-label reveal">Newsroom</p>
        <h2 class="section-title reveal">{esc(heading)}</h2>
        <div class="rel-grid">
{chr(10).join(cells)}
        </div>
      </div>
    </section>
"""


def head(title, accent, extra_css=True):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{esc(title)} — Felidae Conservation Fund</title>
  <link rel="icon" type="image/svg+xml" href="https://felidaefund.org/templates/genesis4/images/favicon.svg" />
  <link rel="alternate icon" href="https://felidaefund.org/favicon.ico" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;500;600;700;800&family=Literata:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400;1,600&display=swap" rel="stylesheet" />

  <link rel="stylesheet" href="tokens.css{V}" />
  <link rel="stylesheet" href="base.css{V}" />
  <link rel="stylesheet" href="components.css{V}" />
  <link rel="stylesheet" href="page.css{V}" />

  <script src="components/site-nav.js{V}"></script>
  <script src="components/site-footer.js{V}"></script>
  <script src="components/site-donate.js{V}"></script>
  <script src="components/page.js{V}" defer></script>
</head>

<body style="--page-accent: var(--project-{accent})" data-ported="joomla">

  <site-nav></site-nav>

  <main>'''

TAIL = '''  </main>

  <site-footer></site-footer>
  <site-donate></site-donate>
</body>
</html>
'''

def support(title, body):
    return f'''
    <section class="support">
      <div class="container support__inner">
        <div class="reveal">
          <h2>{esc(title)}</h2>
          <p>{esc(body)}</p>
        </div>
        <a href="#" class="btn-gold reveal reveal-delay-1" onclick="openDonate(event)">Donate</a>
      </div>
    </section>
'''

def prose_html(bs, indent='          '):
    out = []
    for k, v in bs:
        if k in ('list', 'figure'):
            out.append(indent + (v['html'] if k == 'list' else v))
        elif k in ('h2','h3'):
            out.append(indent + f'<{k}>{v}</{k}>')
        else:
            out.append(indent + f'<p>{v}</p>')
    return '\n'.join(out)

# ── Page register ────────────────────────────────────────────────────
# path -> (out file, title, section label, breadcrumb parent, accent token)
CONTENT = [
 ("about",            "about.html",            "About Us",                    "About",       None,            "bapp"),
 ("about/mission",    "mission.html",          "Our Mission",                 "About",       ("About Us","about.html"), "bapp"),
 ("science",          "science.html",          "Science & Research",          "Science",     None,            "health"),
 ("news",             "news.html",             "News",                        "Newsroom",    None,            "argentina"),
 ("events",           "events.html",           "Events",                      "Get Involved",    None,            "argentina"),
 ("learn/cats",       "learn-cats.html",       "Wild Cats Around the World",  "Learn",       None,            "tsavo"),
 ("learn/protecting-healthy-ecosystems", "learn-ecosystems.html", "Protecting Healthy Ecosystems", "Learn", None, "lwl"),
 ("learn/living-alongside-wild-cats",    "learn-living-alongside.html", "Living Alongside Wild Cats", "Learn", None, "lwl"),
 ("learn/safety-essentials-wild-cats",   "learn-safety.html", "Safety Essentials", "Learn", None, "tsavo"),
 ("learn/media",      "learn-media.html",      "Photos & Videos",             "Learn",       None,            "patagonia"),
 ("kids",             "kids.html",             "Kids Area",                   "Learn",       None,            "cat-aware"),
 ("take-action",      "take-action.html",      "Take Action Today",           "Get Involved",None,            "wilde"),
 ("take-action/volunteer",        "volunteer.html",        "Volunteer",          "Get Involved", ("Take Action","take-action.html"), "wilde"),
 ("take-action/spread-awareness", "spread-awareness.html", "Spread Awareness",   "Get Involved", ("Take Action","take-action.html"), "wilde"),
 ("take-action/community-science","community-science.html","Community Scientist","Get Involved", ("Take Action","take-action.html"), "pumalink"),
 ("take-action/more-ways-to-help","ways-to-donate.html",   "Ways to Donate",     "Get Involved", ("Take Action","take-action.html"), "bapp"),
 ("store",            "store.html",            "Store",                       "Get Involved", None,           "argentina"),
]

# ── Form call-to-actions ─────────────────────────────────────────────
# Daniel's IA puts a form on two pages: "Apply as a Volunteer" and the
# "Event Inquiry Form". A static page cannot receive a submission, so
# these link out to a Google Form instead.
#
# TO ENABLE: paste the Google Form URL next to the page. A page with an
# empty URL renders no button, so nothing ever ships pointing at a dead
# link. The live Joomla forms ask for first name, last name and email.
FORMS = {
  "volunteer.html":     ("Apply as a volunteer", ""),
  "host-an-event.html": ("Send an event inquiry", ""),
}

def form_cta(outfile):
    label, url = FORMS.get(outfile, (None, None))
    if not url: return ''
    return f"""
    <section class="form-cta">
      <div class="container">
        <a href="{url}" class="btn-primary" target="_blank" rel="noopener">{esc(label)}</a>
        <p>Opens a form in a new tab.</p>
      </div>
    </section>
"""


# ── Breadcrumbs ──────────────────────────────────────────────────────
# The live site builds its trail from the URL path, so /science reads
# "Home > Science & Research" even though the menu files it under Learn.
# People navigate the menu, so the menu section is the middle crumb.
# Learn has no landing page, so that crumb is text rather than a link.
SECTIONS = {
  "Projects":     "projects.html",
  "Learn":        None,
  "Get Involved": "take-action.html",
}
SECTION_OF = {
  # Learn
  "mission.html":"Learn", "about.html":"Learn", "who-we-are.html":"Learn",
  "partners-supporters.html":"Learn", "science.html":"Learn",
  "innovative-approach.html":"Learn", "news.html":"Learn",
  "learn-cats.html":"Learn", "learn-ecosystems.html":"Learn",
  "learn-living-alongside.html":"Learn", "learn-safety.html":"Learn",
  "learn-media.html":"Learn", "kids.html":"Learn",
  # Get Involved
  "take-action.html":"Get Involved", "volunteer.html":"Get Involved",
  "spread-awareness.html":"Get Involved", "community-science.html":"Get Involved",
  "events.html":"Get Involved", "ways-to-donate.html":"Get Involved",
  "store.html":"Get Involved", "careers.html":"Get Involved",
  "host-an-event.html":"Get Involved",
  # Projects
  "projects.html":"Projects", "past-projects.html":"Projects",
  # contact-us, privacy and site-map sit in the footer, under no section
}

def section_of(outfile):
    if outfile.startswith(("project-",)): return "Projects"
    if outfile.startswith(("species-","kids-","news-")): return "Learn"
    return SECTION_OF.get(outfile)

def crumb_chain(outfile, parent):
    """[(label, href or None), ...] for everything above the current page."""
    chain = []
    sec = section_of(outfile)
    if sec:
        href = SECTIONS[sec]
        if href == outfile: return []          # the section landing page itself
        chain.append((sec, href))
    # "Get Involved" already points at take-action.html, so a Take Action
    # parent would repeat the same destination twice in one trail
    if parent and parent[1] != outfile and parent[1] != SECTIONS.get(sec):
        chain.append(parent)
    return chain


def crumbs(chain, current):
    rows = ['          <a href="index.html">Home</a>']
    for label, href in chain:
        rows.append('          <span aria-hidden="true">/</span>')
        rows.append(f'          <a href="{href}">{esc(label)}</a>' if href
                    else f'          <span class="crumb-section">{esc(label)}</span>')
    rows.append('          <span aria-hidden="true">/</span>')
    rows.append(f'          <span>{esc(current)}</span>')
    return '\n'.join(rows)

def build_content(src, outfile, title, section, parent, accent):
    s = open(os.path.join(LIVE, src.replace('/','__') + '.html'), encoding='utf-8', errors='replace').read()
    seg = main_block(s)
    bs = blocks(seg)
    # first long paragraph becomes the lede
    lede, rest = '', bs
    for i,(k,v) in enumerate(bs):
        if k == 'p' and len(txt(v)) > 60:
            lede = v; rest = bs[:i] + bs[i+1:]; break
    img, alt = hero_img(seg)
    hero = ''
    if img:
        hero = f'''
    <figure class="page-hero reveal">
      <img src="{img}" alt="{esc(alt) or esc(title)}" />
    </figure>
'''
    body = prose_html(drop_orphan_headings(drop_hero_dupe(rest, img)))
    html_out = head(title, accent) + f'''
    <header class="page-head">
      <div class="container">
        <nav class="crumbs" aria-label="Breadcrumb">
{crumbs(crumb_chain(outfile, parent), title)}
        </nav>
        <p class="page-eyebrow">{esc(section)}</p>
        <h1 class="page-title">{esc(title)}</h1>
        {f'<p class="page-lede">{lede}</p>' if lede else ''}
      </div>
    </header>
{hero}
    <section class="page-body">
      <div class="container">
        <div class="prose reveal">
{body}
        </div>
      </div>
    </section>
''' + gallery_html(gallery_items(raw_main(s))) + gallery_menu_html(gallery_menu(raw_main(s))) + article_list_html(article_items(raw_main(s))) + form_cta(outfile) + support("Support the work behind this page",
              "Felidae is a 501(c)(3) nonprofit. Gifts fund field research, community science and habitat protection.") + TAIL
    open(os.path.join(OUT, outfile), 'w').write(html_out)
    return outfile, len(bs), bool(img)



# ── Project logos ────────────────────────────────────────────────────
# Each project has its own identity lockup. The porter skipped them
# because hero_img() filters out anything with "logo" in the filename.
# Seven of the eleven projects have one; the other four have no logo on
# the live site, and the fact box simply omits it.
FF_IMG = "https://felidaefund.org/images/logos/projects/"
PROJECT_LOGOS = {
  "project-bapp.html":               FF_IMG + "bapp/logo_bapp-01.png",
  "project-bobcat.html":             FF_IMG + "bay-bobcats/logo_babp-01.png",
  "project-tsavo.html":              FF_IMG + "tsavo/logo_tsavo-03.png",
  "project-cat-aware.html":          FF_IMG + "cat-aware/logo_ca-01.png",
  "project-living-with-lions.html":  FF_IMG + "living-with-lions/logo_lwl-03.png",
  "project-wilde-pod.html":          FF_IMG + "wilde-pod/wilde-pod.png",
  "project-wilde-backyard.html":     FF_IMG + "wilde-backyard/wilde-backyard.png",
}

def project_logo(outfile, title):
    url = PROJECT_LOGOS.get(outfile)
    if not url: return ''
    return (f'\n          <img class="factbox__logo" src="{url}" '
            f'alt="{esc(title)} logo" loading="lazy" />')


# ── Project pages ────────────────────────────────────────────────────
PROJECTS = [
 ("projects/research/bay-area-bobcat-project","project-bobcat.html","Bay Area Bobcat Project","babp","Field research"),
 ("projects/research/pumalink","project-pumalink.html","Diablo PumaLink Project","pumalink","Field research"),
 ("projects/research/wild-cat-health-project","project-wildcat-health.html","Wild Cat Health Project","health","Field research"),
 ("projects/research/patagonia-cats-project","project-patagonia.html","Patagonia Wild Cats Project","patagonia","Field research"),
 ("projects/research/tsavo-cheetah-project","project-tsavo.html","Tsavo Cheetah Project","tsavo","Field research"),
 ("projects/research/bhutan-wild-cat-health-project","project-bhutan.html","Bhutan Wild Cat Health Project","bhutan","Field research"),
 ("projects/community/living-with-lions","project-living-with-lions.html","Living with Lions","lwl","Community program"),
 ("projects/community/cat-aware","project-cat-aware.html","CAT Aware","cat-aware","Community program"),
 ("projects/community/wilde-pod","project-wilde-pod.html","Wilde Pod","wilde","Community program"),
 ("projects/community/wilde-backyard","project-wilde-backyard.html","Wilde Backyard","wilde","Community program"),
]
META_KEYS = ("Focus Species","Location","Project Status","Project Start","Project Website")

def project_meta(seg):
    meta = {}
    for li in re.findall(r'<li[^>]*>(.*?)</li>', seg, re.S):
        t = txt(li).replace('\xa0',' ')
        for k in META_KEYS:
            if t.lower().startswith(k.lower()+":"):
                meta[k] = t.split(":",1)[1].strip()
    return meta

def objectives(bs):
    """Objective cards, but only from the section under an "Objectives"
    heading. Pairing any h3 with any list pulled "Conservation goals"
    out of Outcomes on the Bay Area Bobcat page and stranded it in a
    card of its own."""
    start = None
    for i, (k, v) in enumerate(bs):
        if k == 'h2' and re.match(r'objectives?\b', txt(v), re.I):
            start = i + 1; break
    if start is None: return [], None
    end = len(bs)
    for j in range(start, len(bs)):
        if bs[j][0] == 'h2': end = j; break
    section, cards = bs[start:end], []
    for i in range(len(section) - 1):
        if section[i][0] == 'h3' and section[i+1][0] == 'list':
            cards.append((section[i][1], section[i+1][1]['items']))
    return (cards, (start - 1, end)) if cards else ([], None)

def build_project(src, outfile, title, accent, kind):
    s = open(os.path.join(LIVE, src.replace('/','__') + '.html'), encoding='utf-8', errors='replace').read()
    seg = main_block(s)
    meta, bs = project_meta(seg), blocks(seg, cap=90)
    cards, span = objectives(bs)
    if span: bs = bs[:span[0]] + bs[span[1]:]   # the section now lives in the cards
    paras = [(k, v) for k, v in bs if k in ('p', 'h2', 'h3', 'list', 'figure')]
    lede, rest = '', paras
    for i,(k,v) in enumerate(paras):
        if k == 'p' and len(txt(v)) > 60:
            lede = re.sub(r'^(Research|Community Program)\s+', '', v)
            rest = paras[:i] + paras[i+1:]; break
    rest = [b for b in rest
            if b[0] != 'p' or len(txt(b[1])) > 40 or '<a ' in b[1]][:24]
    img, alt = hero_img(seg)

    fact_rows = []
    for k, label in (("Focus Species","Focus species"),("Location","Location"),
                     ("Project Status","Project status"),("Project Start","Started"),
                     ("Project Website","Project website")):
        if k not in meta: continue
        v = meta[k]
        if k == "Project Status":
            cls = 'status-pill status-pill--future' if 'future' in v.lower() else 'status-pill'
            v = f'<span class="{cls}">{esc(v)}</span>'
        elif k == "Project Website":
            u = v if v.startswith('http') else 'https://'+v
            v = f'<a href="{u}" target="_blank" rel="noopener">{esc(v.replace("http://","").replace("https://","").rstrip("/"))}</a>'
        else:
            v = esc(v)
        fact_rows.append(f'            <dt>{label}</dt>\n            <dd>{v}</dd>')
    facts = '\n'.join(fact_rows)

    obj = ''
    if cards:
        cols = []
        for n,(h,items) in enumerate(cards):
            lis = '\n'.join(f'              <li>{i}</li>' for i in items)
            d = f' reveal-delay-{n}' if n else ''
            cols.append(f'''          <article class="obj-card reveal{d}">
            <h3>{h}</h3>
            <ul>
{lis}
            </ul>
          </article>''')
        obj = f'''
    <section class="objectives">
      <div class="container">
        <p class="section-label reveal">Objectives</p>
        <h2 class="section-title reveal">What this project sets out to do</h2>
        <div class="obj-grid">
{chr(10).join(cols)}
        </div>
      </div>
    </section>
'''
    hero = f'''
    <figure class="page-hero reveal">
      <img src="{img}" alt="{esc(alt) or esc(title)}" />
    </figure>
''' if img else ''

    out = head(title, accent) + f'''
    <header class="page-head">
      <div class="container">
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="index.html">Home</a>
          <span aria-hidden="true">/</span>
          <a href="projects.html">Projects</a>
          <span aria-hidden="true">/</span>
          <span>{esc(title)}</span>
        </nav>
        <p class="page-eyebrow">{esc(kind)}</p>
        <h1 class="page-title">{esc(title)}</h1>
        {f'<p class="page-lede">{lede}</p>' if lede else ''}
      </div>
    </header>
{hero}
    <section class="page-body">
      <div class="container page-grid">
        <div class="prose reveal">
{prose_html(drop_orphan_headings(drop_hero_dupe(rest, img)))}
        </div>
        <aside class="factbox reveal reveal-delay-1" aria-label="Project details">{project_logo(outfile, title)}
          <h2>Project details</h2>
          <dl>
{facts}
          </dl>
          <a href="#" class="btn-primary" onclick="openDonate(event)">Support this project</a>
        </aside>
      </div>
    </section>
{obj}
{gallery_html(gallery_items(raw_main(s)))}
''' + support("Fund this project",
              "Camera traps, collar batteries and lab work are what turn field hours into protection.") + TAIL
    open(os.path.join(OUT, outfile), 'w').write(out)
    return outfile, len(rest), len(cards), len(meta)

EXTRA = [
 ("learn/cats/bobcat",       "species-bobcat.html",   "Bobcat",        "Wild Cat Species", ("Wild Cats","learn-cats.html"), "babp"),
 ("learn/cats/mountain-lion","species-mountain-lion.html","Mountain Lion","Wild Cat Species", ("Wild Cats","learn-cats.html"), "bapp"),
 ("learn/cats/ocelot",       "species-ocelot.html",   "Ocelot",        "Wild Cat Species", ("Wild Cats","learn-cats.html"), "argentina"),
 ("learn/cats/snow-leopard", "species-snow-leopard.html","Snow Leopard","Wild Cat Species", ("Wild Cats","learn-cats.html"), "bhutan"),
 ("news/general/the-unexpected-social-ripple-of-local-wildlife-science","news-wildlife-science.html",
   "The Unexpected Social Ripple of Local Wildlife Science","News",("News","news.html"),"health"),
 ("news/how-america-is-redesigning-its-roads-for-wildlife","news-roads-for-wildlife.html",
   "How America Is Redesigning Its Roads for Wildlife","News",("News","news.html"),"pumalink"),
 ("news/volunteer-spotlights/ellas-internship-with-felidae","news-ella-internship.html",
   "Ella's Internship with Felidae","News",("News","news.html"),"lwl"),
]

# ── Species: 40 detail pages + the gallery index ─────────────────────
import json
SPECIES = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'species.json')))
SPECIES_SLUGS.update(SPECIES)
ACCENTS = ["bapp","tsavo","patagonia","lwl","babp","argentina","pumalink","bhutan","health","wilde"]
# The live gallery ships a different max size per species; use what exists.
THUMBS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'thumbs.json')))
def thumb(slug):
    return f"https://felidaefund.org/media/cache/autosized/images/species/thumbs/{slug}-{THUMBS.get(slug, 50)}.webp"

def build_species():
    made = []
    for n, (slug, sp) in enumerate(sorted(SPECIES.items())):
        accent = ACCENTS[n % len(ACCENTS)]
        out = f"species-{slug}.html"
        made.append(build_content(f"learn/cats/{slug}", out, sp["common"], "Wild Cat Species",
                                  ("Wild Cats","learn-cats.html"), accent))
    return made

def build_species_index():
    cards = []
    for n, (slug, sp) in enumerate(sorted(SPECIES.items(), key=lambda x: x[1]["common"])):
        d = f' reveal-delay-{n%4}' if n % 4 else ''
        cards.append(f'''          <a class="species-card reveal{d}" href="species-{slug}.html">
            <div class="species-card__media">
              <img src="{thumb(slug)}" alt="{esc(sp['common'])}" loading="lazy" width="256" height="256" />
            </div>
            <h3>{esc(sp['common'])}</h3>
            <p>{esc(sp['sci'])}</p>
          </a>''')
    out = head("Wild Cats Around the World", "tsavo") + f'''
    <header class="page-head">
      <div class="container">
        <nav class="crumbs" aria-label="Breadcrumb">
{crumbs(crumb_chain('learn-cats.html', None), 'Wild Cats')}
        </nav>
        <p class="page-eyebrow">Learn</p>
        <h1 class="page-title">Wild cats around the world</h1>
        <p class="page-lede">
          There are {len(SPECIES)} species in the Felidae family, from the seven-pound black-footed cat
          to the tiger. Roughly 40 percent of them are threatened and in decline.
        </p>
      </div>
    </header>

    <section class="page-body">
      <div class="container">
        <div class="species-grid">
{chr(10).join(cards)}
        </div>
      </div>
    </section>
''' + support("Every species here depends on habitat",
              "Felidae funds the field research and community work that keeps that habitat intact.") + TAIL
    open(os.path.join(OUT, "learn-cats.html"), 'w').write(out)
    return len(cards)

# Pages that exist on the live site but nothing in the main nav points at,
# so the first pass missed them. Reachable from the footer, from links in
# body copy, or by URL.
CONTENT += [
 ("projects/archive", "past-projects.html", "Past Projects", "Our Work",
    ("Projects","projects.html"), "bapp"),
 ("science/innovative-wild-cat-conservation", "innovative-approach.html",
    "Our Innovative Approach", "Science", ("Science & Research","science.html"), "health"),
 ("take-action/host-an-event", "host-an-event.html", "Host an Event", "Get Involved",
    ("Take Action","take-action.html"), "wilde"),
 ("careers", "careers.html", "Career Opportunities", "Get Involved",
    ("Take Action","take-action.html"), "pumalink"),
 ("about/who-we-are", "who-we-are.html", "Who We Are", "About",
    ("About Us","about.html"), "bapp"),
 ("about/partners-supporters", "partners-supporters.html", "Partners & Supporters", "About",
    ("About Us","about.html"), "argentina"),
 ("kids/fun-facts", "kids-fun-facts.html", "Fun Facts", "Learn",
    ("Kids Area","kids.html"), "cat-aware"),
 ("kids/ask-a-wild-cat", "kids-ask-a-wild-cat.html", "Ask a Wild Cat", "Learn",
    ("Kids Area","kids.html"), "cat-aware"),
 ("kids/how-to-help", "kids-how-to-help.html", "How Can Kids Help?", "Learn",
    ("Kids Area","kids.html"), "lwl"),
 ("contact-us", "contact-us.html", "Contact Us", "Get in Touch", None, "bapp"),
 ("privacy", "privacy.html", "Privacy Policy", "Legal", None, "health"),
 ("site-map", "site-map.html", "Site Map", "Navigate", None, "tsavo"),
]

LINKMAP.update({
 "/projects/archive":"past-projects.html",
 "/science/innovative-wild-cat-conservation":"innovative-approach.html",
 "/take-action/host-an-event":"host-an-event.html",
 "/careers":"careers.html",
 "/about/who-we-are":"who-we-are.html",
 "/about/partners-supporters":"partners-supporters.html",
 "/kids/fun-facts":"kids-fun-facts.html",
 "/kids/ask-a-wild-cat":"kids-ask-a-wild-cat.html",
 "/kids/how-to-help":"kids-how-to-help.html",
 "/contact-us":"contact-us.html",
 "/privacy":"privacy.html",
 "/site-map":"site-map.html",
})

if __name__ == '__main__':
    for row in CONTENT:
        print("  %-28s blocks=%-3s hero=%s" % build_content(*row))
    print()
    for row in EXTRA:
        print("  %-28s blocks=%-3s hero=%s" % build_content(*row))
    print()
    for row in PROJECTS:
        print("  %-28s paras=%-3s objcards=%-2s meta=%s" % build_project(*row))
    print()
    print("  species pages:", len(build_species()))
    print("  species index cards:", build_species_index())
