import re, html, os, sys
LIVE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'live')
OUT  = '/Users/irene/code/felidaefund.org/prototype'
V    = '?v=10'

def txt(s): return html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',s))).strip()
def esc(s): return html.escape(s, quote=False)

def main_block(s):
    i = s.find('<main id="main_content"')
    if i < 0: return ''
    seg = s[i:s.find('</main>', i)]
    # Joomla chrome that isn't body copy: hidden captions, scripts, nav, forms
    for pat in (r'<figcaption\b.*?</figcaption>', r'<script\b.*?</script>',
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


def blocks(seg, cap=80):
    """Ordered (kind, payload) content blocks from the Joomla main region."""
    out = []
    for m in re.finditer(r'<(h2|h3|p|ul|ol)\b[^>]*>(.*?)</\1>', seg, re.S):
        kind, inner = m.group(1), m.group(2)
        if kind in ('ul','ol'):
            raw = re.findall(r'<li[^>]*>(.*?)</li>', inner, re.S)
            items = [(txt(li), inline_html(li)) for li in raw]
            items = [h for t, h in items if 3 < len(t) < 220 and not NOISE.match(t)]
            if 1 < len(items) <= 12: out.append(('ul', items))
        else:
            t = txt(inner)
            if not t or NOISE.match(t): continue
            has_link = '<a ' in inner
            if kind == 'p' and ((len(t) < 25 and not has_link) or len(t) > 900): continue
            if CREDIT.search(t): continue
            if kind in ('h2','h3') and (len(t) < 3 or len(t) > 90): continue
            out.append((kind, inline_html(inner)))
        if len(out) >= cap: break
    # collapse duplicate consecutive headings
    ded, seen = [], set()
    for k, v in out:
        key = (k, v if isinstance(v, str) else tuple(v))
        if key in seen: continue
        seen.add(key); ded.append((k, v))
    return ded

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

def head(title, accent, extra_css=True):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{esc(title)} — Felidae Conservation Fund</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;500;600;700;800&family=Literata:ital,wght@0,300;0,400;0,500;1,300;1,400&display=swap" rel="stylesheet" />

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
        if k == 'ul':
            out.append(indent + '<ul class="prose-list">')
            out += [indent + f'  <li>{i}</li>' for i in v]
            out.append(indent + '</ul>')
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
 ("science",          "science.html",          "Science & Research",          "Our Work",    None,            "health"),
 ("news",             "news.html",             "News",                        "Newsroom",    None,            "argentina"),
 ("events",           "events.html",           "Events",                      "Newsroom",    None,            "argentina"),
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

def crumbs(parent, current):
    rows = ['          <a href="index.html">Home</a>', '          <span aria-hidden="true">/</span>']
    if parent:
        rows += [f'          <a href="{parent[1]}">{esc(parent[0])}</a>', '          <span aria-hidden="true">/</span>']
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
    body = prose_html(rest)
    html_out = head(title, accent) + f'''
    <header class="page-head">
      <div class="container">
        <nav class="crumbs" aria-label="Breadcrumb">
{crumbs(parent, title)}
        </nav>
        <p class="page-eyebrow">{esc(section)}</p>
        <h1 class="page-title">{esc(title)}</h1>
        <p class="page-lede">{lede}</p>
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
''' + support("Support the work behind this page",
              "Felidae is a 501(c)(3) nonprofit. Gifts fund field research, community science and habitat protection.") + TAIL
    open(os.path.join(OUT, outfile), 'w').write(html_out)
    return outfile, len(bs), bool(img)



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
    """h3 followed by a list -> an objective card."""
    cards, i = [], 0
    while i < len(bs):
        if bs[i][0] == 'h3' and i+1 < len(bs) and bs[i+1][0] == 'ul':
            cards.append((bs[i][1], bs[i+1][1])); i += 2
        else: i += 1
    return cards[:3]

def build_project(src, outfile, title, accent, kind):
    s = open(os.path.join(LIVE, src.replace('/','__') + '.html'), encoding='utf-8', errors='replace').read()
    seg = main_block(s)
    meta, bs = project_meta(seg), blocks(seg, cap=90)
    cards = objectives(bs)
    used = {c[0] for c in cards}
    paras = [(k,v) for k,v in bs if k == 'p' or (k in ('h2','h3') and v not in used)]
    lede, rest = '', paras
    for i,(k,v) in enumerate(paras):
        if k == 'p' and len(txt(v)) > 60:
            lede = re.sub(r'^(Research|Community Program)\s+', '', v)
            rest = paras[:i] + paras[i+1:]; break
    rest = [b for b in rest if b[0] != 'p' or len(txt(b[1])) > 40 or '<a ' in b[1]][:24]
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
            <h3>{esc(h)}</h3>
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
        <p class="page-lede">{lede}</p>
      </div>
    </header>
{hero}
    <section class="page-body">
      <div class="container page-grid">
        <div class="prose reveal">
{prose_html(rest)}
        </div>
        <aside class="factbox reveal reveal-delay-1" aria-label="Project details">
          <h2>Project details</h2>
          <dl>
{facts}
          </dl>
          <a href="#" class="btn-primary" onclick="openDonate(event)">Support this project</a>
        </aside>
      </div>
    </section>
{obj}
    <section class="related">
      <div class="container">
        <p class="section-label reveal">More projects</p>
        <h2 class="section-title reveal">Other places we work</h2>
        <p style="margin-top:24px"><a href="projects.html" class="btn-outline">See all eleven projects</a></p>
      </div>
    </section>
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
          <a href="index.html">Home</a>
          <span aria-hidden="true">/</span>
          <span>Wild Cats</span>
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
