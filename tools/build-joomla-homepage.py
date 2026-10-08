import re, os
P = '/Users/irene/code/felidaefund.org/prototype'
OUT = '/Users/irene/code/felidaefund.org/joomla-homepage'
os.makedirs(OUT, exist_ok=True)

LINKS = {
 'learn-cats.html':'/learn/cats',
 'learn-ecosystems.html':'/learn/protecting-healthy-ecosystems',
 'learn-living-alongside.html':'/learn/living-alongside-wild-cats',
 'news.html':'/news',
 'news-ella-internship.html':'/news/volunteer-spotlights/ellas-internship-with-felidae',
 'news-roads-for-wildlife.html':'/news/how-america-is-redesigning-its-roads-for-wildlife',
 'news-wildlife-science.html':'/news/general/the-unexpected-social-ripple-of-local-wildlife-science',
 'project-bapp.html':'/projects/research/bay-area-puma-project',
 'project-bobcat.html':'/projects/research/bay-area-bobcat-project',
 'project-patagonia.html':'/projects/research/patagonia-cats-project',
 'project-pumalink.html':'/projects/research/pumalink',
 'projects.html':'/projects/research',
 'species-bobcat.html':'/learn/cats/bobcat',
 'species-mountain-lion.html':'/learn/cats/mountain-lion',
 'species-ocelot.html':'/learn/cats/ocelot',
 'species-snow-leopard.html':'/learn/cats/snow-leopard',
 'ways-to-donate.html':'/take-action/more-ways-to-help',
}
FRU = '#XSZEWCKT'          # Fundraise Up checkout, same anchor the live site uses
IMG = '/images/homepage/'  # where the assets get uploaded in Joomla media

# ── markup ───────────────────────────────────────────────────────────
src = open(f'{P}/index.html').read().splitlines(keepends=True)
html = ''.join(src[502:854])            # HERO .. end of CTA, no nav/footer/modal

html = re.sub(r'<!--.*?-->', '', html, flags=re.S)                  # strip comments (incl. the video block)
for proto, live in LINKS.items():
    html = html.replace(f'href="{proto}"', f'href="{live}"')
# donate buttons -> Fundraise Up; "Get Started" -> take action
html = html.replace('<a href="#" class="btn-gold" onclick="openDonate(event)">',
                    f'<a href="{FRU}" class="btn-gold">')
html = html.replace('<a href="#" class="btn-gold" style="margin-top:8px">',
                    '<a href="/take-action" class="btn-gold" style="margin-top:8px">')
html = re.sub(r'src="assets/', f'src="{IMG}', html)
# the two classes that collide with the live homepage CSS
html = re.sub(r'class="mission(?=[" ])', 'class="fx-mission', html)
html = re.sub(r'class="news(?=[" ])',    'class="fx-news', html)
# the template boxes plain <section>s at 1170px; full-width is its own escape hatch
html = re.sub(r'<section class="([^"]+)"', lambda m: f'<section class="{m.group(1)} full-width"', html)
html = re.sub(r'\n[ \t]*\n+', '\n', html)

assert 'openDonate' not in html and '.html"' not in html, 'unconverted link or donate handler left'
open(f'{OUT}/article.html','w').write(
  '<div class="fx-home">\n' + html.rstrip() + '\n</div>\n')

# ── css ──────────────────────────────────────────────────────────────
import scope_css as scope
tokens = open(f'{P}/tokens.css').read()
tokens = re.sub(r'/\* Alternate theme.*', '', tokens, flags=re.S).rstrip()   # theme picker is parked
base   = scope.scope_rules(open(f'{P}/base.css').read())
inline = scope.scope_rules(''.join(src[22:494]))
for css_name in ('base','inline'):
    pass
base   = base.replace(':root { --nav-h: 72px; }', '')      # hero does not use --nav-h
base   = re.sub(r'\.fx-home \.mission(?![\w-])', '.fx-home .fx-mission', base)
inline = re.sub(r'\.fx-home \.mission(?![\w-])', '.fx-home .fx-mission', inline)
base   = re.sub(r'\.fx-home \.news(?![\w-])', '.fx-home .fx-news', base)
inline = re.sub(r'\.fx-home \.news(?![\w-])', '.fx-home .fx-news', inline)

NEUTRALISE = """
/* ── Undo the live site's rules where they reach into this markup ─────
   Checked against special-pages.css, template.css, digi-custom.css and
   content.min.css. Two template rules reach the new markup:

   1. .home section + section { margin-top: ... !important }
   2. * + :not(:first-child):not(main):not(.igui-lightbox)
          { margin-top: var(--space-s) }   <- template.css

   The second is the template's global flow spacing: it puts 24px on top
   of EVERY element that has a preceding sibling. The prototype assumes a
   margin:0 reset, so it has to be switched off inside .fx-home. The
   selector below mirrors the template's exactly, plus .fx-home, so it can
   only ever undo that one rule. The handful of margins the design does
   want back are restored at the end of this file, where equal specificity
   plus later source order lets them win.

   The two classes that collided outright (.mission, .news) are renamed
   .fx-mission / .fx-news in the article instead of being fought with
   !important, and every section carries the template's own full-width
   class so it is not boxed to 1170px. */
  .home .fx-home section + section { margin-top: 0 !important; }
  .fx-home * + :not(:first-child):not(main):not(.igui-lightbox) { margin-top: 0; }
"""


# ---- restore the margins the design does want, above the neutraliser ----
def _top_margin(decl):
    m = re.search(r'margin-top:\s*([^;}]+)', decl)
    if m: return m.group(1).strip()
    m = re.search(r'(?<![-\w])margin:\s*([^;}]+)', decl)
    if m: return m.group(1).split()[0].strip()
    return None

restores = []
for rule in re.findall(r'^\s*(\.fx-home[^{\n]*)\{([^}]*)\}', base + '\n' + inline, re.M):
    sel, decl = rule[0].strip().rstrip(','), rule[1]
    if '*' in sel or ':' in sel.split()[-1][:1]: pass
    val = _top_margin(decl)
    if not val or val in ('0', '0px') or 'auto' == val: continue
    if '*' in sel: continue
    restores.append((sel, val))
if restores:
    lines = ['', '/* \u2500\u2500 Margins the design wants, restored past the neutraliser above.',
             '   Same specificity as it, declared later, so these win. \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500 */']
    for sel, val in restores:
        lines.append(f'  {sel}:not(:first-child):not(main) {{ margin-top: {val}; }}')
    RESTORE = '\n'.join(lines) + '\n'
else:
    RESTORE = ''

RESTORE += """
/* \u2500\u2500 Hero height, allowing for Joomla's header \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
   The prototype's nav floats over the hero, so the hero is 100dvh. Joomla's
   header is sticky and sits in normal flow above the article, about 172px
   including its top offset. Left at 100dvh the hero runs 172px past the
   fold and takes its own buttons with it, which is exactly the donate CTA
   we are trying to make more prominent. homepage.js measures the real
   offset at runtime, since the header is shorter on narrow screens; the
   value here is the desktop fallback if the script does not run. */
  .fx-home .hero { height: calc(100dvh - var(--fx-hero-offset, 172px)); }
"""


open(f'{OUT}/homepage.css','w').write(f"""/* Felidae homepage — Joomla build.
   Generated from the prototype; every rule is scoped to .fx-home so
   nothing can reach Joomla's header, footer or any other page.
   Paste below the existing contents of digi-custom.css. */

/* ── Design tokens. No name clashes with the live site's 144 vars. ── */
{tokens}

/* ── Reset, type, buttons, utilities (was base.css) ───────────────── */
{base}
{NEUTRALISE}
/* ── Homepage sections (was the page's inline <style>) ───────────── */
{inline}
{RESTORE}
""")

# ── js ───────────────────────────────────────────────────────────────
counter = ''.join(src[860:889])
counter = re.sub(r'^\s{4}', '', counter, flags=re.M)
counter = counter.replace("document.querySelectorAll('[data-target]')",
                          "root.querySelectorAll('[data-target]')")
counter = re.sub(r'^[ \t]+(const counterObserver)', r'  \1', counter, flags=re.M)
open(f'{OUT}/homepage.js','w').write(
"""// Felidae homepage — counters and scroll reveal.
// No libraries. Both effects degrade safely: without this file the
// numbers show their final values and the sections simply appear.
(function () {
  'use strict';
  var root = document.querySelector('.fx-home');
  if (!root) return;

  if (!('IntersectionObserver' in window)) {           // very old browser
    root.querySelectorAll('.reveal').forEach(function (el) { el.classList.add('visible'); });
    root.querySelectorAll('[data-target]').forEach(function (el) {
      el.textContent = el.dataset.format === 'M'
        ? (el.dataset.target / 1000000).toFixed(1) + 'M'
        : (+el.dataset.target).toLocaleString();
    });
    return;
  }

""" + re.sub(r'^', '  ', counter.strip(), flags=re.M) + """

  // The hero fills whatever the Joomla header leaves. Its own height does not
  // affect its top, so this is safe to read at any scroll position.
  var setHeroOffset = function () {
    var hero = root.querySelector('.hero');
    if (!hero) return;
    var top = Math.round(hero.getBoundingClientRect().top + window.scrollY);
    document.documentElement.style.setProperty('--fx-hero-offset', top + 'px');
  };
  setHeroOffset();
  window.addEventListener('resize', setHeroOffset);

  var revealObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('visible'); revealObserver.unobserve(e.target); }
    });
  }, { threshold: 0.12 });
  root.querySelectorAll('.reveal').forEach(function (el) { revealObserver.observe(el); });
})();
""")

# ── review harness: the Joomla cascade, reproduced, so the article can be
#    checked before anyone pastes it into the live site ────────────────
B = 'https://felidaefund.org/templates/genesis4/css/'
HERE = os.path.dirname(os.path.abspath(__file__))
# The live site's real header and footer, saved from felidaefund.org so the
# preview shows the page in its actual chrome. These ship as-is on Joomla;
# the decision was to keep them. Refresh with --chrome.
chrome_hdr = open(os.path.join(HERE, 'joomla-header.html')).read()
chrome_ftr = open(os.path.join(HERE, 'joomla-footer.html')).read()
harness_art = open(f'{OUT}/article.html').read().replace('src="/images/homepage/', 'src="assets/')
preview = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Homepage — Joomla build preview</title>
<link rel="icon" type="image/svg+xml" href="https://felidaefund.org/templates/genesis4/images/favicon.svg" />
<link href="https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;500;600;700;800&family=Literata:ital,wght@0,300;0,400;0,500;1,300;1,400&display=swap" rel="stylesheet">
<!-- The live site's four stylesheets, in the live order, so this page shows
     exactly what the article will look like once it is pasted into Joomla.
     The header and footer are the live site's real ones, kept as agreed.
     The homepage CSS and JS are inlined so this page is self-contained and
     works from Vercel, the local server, or straight off disk. -->
<link rel="stylesheet" href="@B@special-pages.css?1">
<link rel="stylesheet" href="https://felidaefund.org/media/plg_system_jcepro/site/css/content.min.css">
<link rel="stylesheet" href="@B@template.css?1.3">
<link rel="stylesheet" href="@B@digi-custom.css">
<style>
@CSS@
</style>
</head>
<body class="option-com_content view-article no-layout no-task itemid-101  path-home">
@HEADER@
<main><article class="home item-page">
@ART@
</article></main>
@FOOTER@
<script>
@JS@
</script>
</body></html>
""".replace('@B@', B).replace('@ART@', harness_art) \
    .replace('@CSS@', open(f'{OUT}/homepage.css').read()) \
    .replace('@JS@',  open(f'{OUT}/homepage.js').read()) \
    .replace('@HEADER@', chrome_hdr).replace('@FOOTER@', chrome_ftr)
open(f'{P}/joomla-preview.html','w').write(preview)
print('joomla-preview.html -> prototype/')
print('article.html', len(open(f'{OUT}/article.html').read()), 'bytes')
print('homepage.css', len(open(f'{OUT}/homepage.css').read()), 'bytes')
print('homepage.js ', len(open(f'{OUT}/homepage.js').read()), 'bytes')
