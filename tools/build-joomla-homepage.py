import re, os
P = '/Users/irene/code/felidaefund.org/prototype'
OUT = '/Users/irene/code/felidaefund.org/joomla-homepage'
os.makedirs(OUT, exist_ok=True)


def between(lines, start_pred, end_pred, label):
    """Slice the prototype by landmarks, never by line number. Editing
    index.html used to shift every hardcoded offset, which silently handed
    the build the wrong block: the day the hairline rule was added, the
    counter script came out truncated and every section below the hero
    stayed invisible."""
    a = next((i for i, l in enumerate(lines) if start_pred(l)), None)
    b = next((i for i, l in enumerate(lines) if i > (a or 0) and end_pred(l)), None)
    if a is None or b is None:
        raise SystemExit(f'build: could not locate {label} in index.html')
    return lines[a + 1:b]

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
# Fundraise Up. The live homepage does not use the #XSZEWCKT element id that
# the interior pages use: it uses the form-and-UTM form, which is what feeds
# per-placement attribution in Fundraise Up's reporting. Matching it keeps
# Zara's homepage conversion numbers continuous.
#   donate_row_home  - the existing homepage donate row, kept so the history
#                      stays comparable
#   donate_hero_home - new, the hero CTA, so the two can be told apart
FRU_CTA  = '#?utm_content=donate_row_home&form=donate'
FRU_HERO = '#?utm_content=donate_hero_home&form=donate'
IMG = '/images/homepage/'  # where the assets get uploaded in Joomla media

# ── markup ───────────────────────────────────────────────────────────
src = open(f'{P}/index.html').read().splitlines(keepends=True)
html = ''.join(between(src, lambda l: '<site-nav>' in l,
                            lambda l: '<site-footer>' in l, 'page content'))

html = re.sub(r'<!--.*?-->', '', html, flags=re.S)                  # strip comments (incl. the video block)
for proto, live in LINKS.items():
    html = html.replace(f'href="{proto}"', f'href="{live}"')
# donate buttons -> Fundraise Up; "Get Started" -> take action
# the hero button first (it is the one followed by a newline + "Donate Now"),
# then the CTA panel button, so the two get different attribution
html = html.replace('<a href="#" class="btn-gold" onclick="openDonate(event)">\n          Donate Now',
                    f'<a href="{FRU_HERO}" class="btn-gold">\n          Donate Now', 1)
html = html.replace('<a href="#" class="btn-gold" onclick="openDonate(event)">Donate Now</a>',
                    f'<a href="{FRU_CTA}" class="btn-gold">Donate Now</a>')
html = html.replace('<a href="#" class="btn-gold" style="margin-top:8px">',
                    '<a href="/take-action" class="btn-gold" style="margin-top:8px">')
# Joomla's media manager on this server rejects .webp: its type detection
# fails regardless of the Legal Extensions / MIME settings, while plain
# JPEG uploads fine. So the upload set is built as JPEG and the article
# points at .jpg. The prototype keeps its .webp originals, which are
# smaller and serve fine from Vercel.
html = re.sub(r'src="assets/([^"]+)\.webp"', rf'src="{IMG}\1.jpg"', html)
html = re.sub(r'src="assets/', f'src="{IMG}', html)
# Joomla's media manager flattens on upload, so the badges landed beside the
# photos rather than in a badges/ subfolder. Point at where they actually are.
html = html.replace(f'{IMG}badges/', IMG)
# the two classes that collide with the live homepage CSS
html = re.sub(r'class="mission(?=[" ])', 'class="fx-mission', html)
html = re.sub(r'class="news(?=[" ])',    'class="fx-news', html)
# the template boxes plain <section>s at 1170px; full-width is its own escape hatch
html = re.sub(r'<section class="([^"]+)"', lambda m: f'<section class="{m.group(1)} full-width"', html)
html = re.sub(r'\n[ \t]*\n+', '\n', html)

assert 'openDonate' not in html and '.html"' not in html, 'unconverted link or donate handler left'
assert html.count('form=donate') == 2, f'expected 2 donate links, got {html.count("form=donate")}'
# Section order. Zara's note from the Oct 2026 review: the impact numbers
# come first, then the mission, so the page leads with evidence rather
# than with a statement about ourselves.
def move_section(doc, mover, before):
    # Lift one top-level <section class="X ..."> and re-insert it ahead of
    # another. The sections are siblings and never nest, so a non-greedy
    # match to the next </section> is safe.
    pat = re.compile(r'\n?[ \t]*<section class="' + mover + r'\b.*?</section>', re.S)
    m = pat.search(doc)
    if not m: raise SystemExit(f'section {mover} not found')
    block = m.group(0)
    doc = doc[:m.start()] + doc[m.end():]
    anchor = re.search(r'\n?[ \t]*<section class="' + before + r'\b', doc)
    if not anchor: raise SystemExit(f'section {before} not found')
    return doc[:anchor.start()] + '\n' + block.strip('\n') + doc[anchor.start():]

html = move_section(html, 'impact', 'fx-mission')
order = re.findall(r'<section class="([a-z-]+)', html)
print('  section order:', ' -> '.join(order))

ARTICLE_HTML = '<div class="fx-home">\n' + html.rstrip() + '\n</div>\n'
open(f'{OUT}/article.html','w').write(ARTICLE_HTML)

# ── upload set: every image the article needs, in a format Joomla accepts ──
import subprocess, shutil
IMGDIR = os.path.join(OUT, 'images')
if os.path.isdir(IMGDIR): shutil.rmtree(IMGDIR)
os.makedirs(os.path.join(IMGDIR, 'badges'), exist_ok=True)
wanted = sorted(set(re.findall(r'src="/images/homepage/([^"]+)"', open(f'{OUT}/article.html').read())))
converted = kept = 0
for rel in wanted:
    dest = os.path.join(IMGDIR, rel)
    # badges live in assets/badges/ but upload flat, so look in both
    cands = [os.path.join(P, 'assets', rel), os.path.join(P, 'assets', 'badges', rel)]
    src_jpg = next((c for c in cands if os.path.exists(c)), cands[0])
    src_webp = next((os.path.splitext(c)[0] + '.webp' for c in cands
                     if os.path.exists(os.path.splitext(c)[0] + '.webp')),
                    os.path.splitext(cands[0])[0] + '.webp')
    if os.path.exists(src_jpg):
        shutil.copy2(src_jpg, dest); kept += 1
    elif os.path.exists(src_webp):
        subprocess.run(['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', '90',
                        src_webp, '--out', dest], capture_output=True, check=True)
        converted += 1
    else:
        raise SystemExit(f'missing source for {rel}')
total = sum(os.path.getsize(os.path.join(r, f))
            for r, _, fs in os.walk(IMGDIR) for f in fs)
print(f'images/      {len(wanted)} files ({converted} converted from webp, {kept} copied), '
      f'{total/1024/1024:.1f} MB')

# ── css ──────────────────────────────────────────────────────────────
import scope_css as scope
tokens = open(f'{P}/tokens.css').read()
tokens = re.sub(r'/\* Alternate theme.*', '', tokens, flags=re.S).rstrip()   # theme picker is parked
base   = scope.scope_rules(open(f'{P}/base.css').read())
inline = scope.scope_rules(''.join(between(src, lambda l: '<style>' in l,
                                                lambda l: '</style>' in l, 'inline <style>')))
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
/* \u2500\u2500 Hosting this page as a Joomla module \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
   The homepage ships as a Custom HTML module in the `after-content`
   position. Three things there get in the way:

     section.after-content   capped at 1170px
     .after-content-inner    display:flex, capped at 1098px, so the module
                             becomes one column beside any other module
     .mod-custom             padding-right 48px and margin-right 72px,
                             which pushes the whole page off-centre
     section.after-content   picks up a 24px top margin from the global flow
                             spacing, showing as a brown band above the hero
     article.item-page       still renders Joomla's title header
                             (section.intro) and an empty details box
                             (section.default) above the module

   Every rule below is guarded by :has(.fx-home), so it applies only where
   this homepage is actually present and stops applying by itself if the
   module is removed. The two that reset padding and margin are guarded on
   the module itself, not the page: any other module sharing the position
   keeps its own spacing. :has() is supported by every
   current browser; in an old one the page is narrow but not broken. */
  body:has(.fx-home) section.after-content,
  body:has(.fx-home) .after-content-inner {
    display: block; max-width: none; width: 100%; padding: 0; margin: 0; }
  /* The same flow spacing reaches the siblings outside .fx-home too, where
     the 24px shows as a dark band of page background between the CTAs, the
     newsletter and the footer. The footer repeats their :not() chain
     because a plain `footer` loses the specificity tie. */
  body:has(.fx-home) section.bottom,
  body:has(.fx-home) footer:not(:first-child):not(main) { margin-top: 0; }
  /* The social icons are mask images painted with a background colour, and
     several rules compete for it: gold in one state, --light-brown in
     another. The dark one was winning here, so the icons rendered dark
     brown on a dark footer: present and clickable, but invisible. Pinned
     to the site's own --gold, which is what the live footer shows. No new
     colour: hsl(var(--gold)) is the template's own token. */
  body:has(.fx-home) footer nav[aria-label="Social Media Icons"] a span.icon {
    background-color: hsl(var(--gold)) !important; }
  body:has(.fx-home) footer nav[aria-label="Social Media Icons"] a:hover span.icon {
    background-color: hsl(var(--light-brown)) !important; }
  .after-content-inner > .moduletable:has(.fx-home),
  .after-content-inner .mod-custom:has(.fx-home) {
    width: 100%; max-width: none; padding: 0; margin: 0; }
  body:has(.fx-home) article.item-page > section.intro,
  body:has(.fx-home) article.item-page > section.default { display: none; }

  /* special-pages.css and template.css both carry
         h1, .h1 { text-transform: uppercase }
     and the prototype never declares text-transform on the hero title, so
     there was nothing to override it and Joomla shouted the headline.
     Daniel's design is title case. */
  .fx-home h1 { text-transform: none; }
"""

RESTORE += """
/* \u2500\u2500 Newsletter \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
   The signup is a Convert Forms form in a Joomla module. Its markup is
   generated by the extension and its submission is wired to Convert Forms,
   so this restyles it and changes nothing structural: same three fields,
   same handler, same form id. Replacing the markup would keep the look and
   silently break the signup.

   Values are taken from .newsletter in the prototype's components.css, not
   invented. The one thing CSS cannot do is reduce three fields to one as
   the prototype has: First Name and Last Name are required, and hiding a
   required field blocks submission.

   The !important marks are not decoration. template.css sets the input
   background and border with !important of its own, and digi-custom.css
   already does the same to .cf-btn, so a plain rule loses to both.

   :not(#_) is stranger and needs explaining. template.css styles text
   inputs with

       form input[type="text"]:not(#jform_com_fields_screenshot), ...

   and an id inside :not() counts towards specificity, which is what
   decides between two !important rules. That selector therefore carries
   id-level weight, while the entry for email in the same list does not,
   which is why email picked up this styling and the name fields did not.
   :not(#_) matches everything (no element has that id) and lends this rule
   the same id-level weight, so it wins by class count. Lifting the whole
   file's specificity would be worse: it would break the ordering between
   these rules and the prototype's own.

   Guarded by body:has(.fx-home), so for now this only applies on the new
   homepage. Removing that guard from these rules makes it site-wide. */
  /* The cream runs the full width of the band, as the prototype does, so it
     reads as a section rather than a card floating on brown. The tint goes
     on section.bottom; .bottom-inner keeps its own max-width, so the text
     stays aligned with every other section on the page. */
  body:has(.fx-home) section.bottom {
    background: var(--gold-100);
    border-top: 1px solid rgba(var(--gold-rgb),.3);
    color: var(--espresso-900);
    padding: 80px 0; }
  body:has(.fx-home) .moduletable.newsletter {
    background: transparent;
    border-top: none;
    color: var(--espresso-900);
    padding: 0; }
  body:has(.fx-home) .moduletable.newsletter h3 {
    font-family: var(--font-display); font-weight: 700;
    font-size: clamp(22px, 2.5vw, 32px); line-height: 1.15;
    color: var(--espresso-900); max-width: 480px; }
  body:has(.fx-home) .moduletable.newsletter .cf-control-group,
  body:has(.fx-home) .moduletable.newsletter .cf-label,
  body:has(.fx-home) .moduletable.newsletter span {
    color: var(--brown-800); }
  body:has(.fx-home) .moduletable.newsletter .cf-input:not(#_) {
    padding: 14px 18px !important;
    font-family: var(--font-body); font-size: 15px;
    background: var(--white) !important; color: var(--espresso-900) !important;
    border: 1.5px solid rgba(var(--brown-rgb),.25) !important;
    border-radius: var(--r-sm) !important; outline: none;
    transition: border-color .2s; }
  body:has(.fx-home) .moduletable.newsletter .cf-input::placeholder {
    color: var(--brown-300); }
  body:has(.fx-home) .moduletable.newsletter .cf-input:not(#_):focus {
    border-color: var(--brown-700) !important; }
  body:has(.fx-home) .moduletable.newsletter .cf-required-label {
    color: var(--brown-700); }
  body:has(.fx-home) .moduletable.newsletter .cf-btn:not(#_) {
    border-radius: var(--r-sm) !important;
    background: var(--brown-700) !important;
    background-color: var(--brown-700) !important;
    color: var(--cream-100) !important;
    font-family: var(--font-display); font-weight: 600; font-size: 13px;
    letter-spacing: .08em; text-transform: uppercase;
    padding: 14px 24px; border-radius: var(--r-sm);
    transition: background .2s; }
  body:has(.fx-home) .moduletable.newsletter .cf-btn:hover {
    background: var(--brown-600) !important; }
  body:has(.fx-home) .moduletable.newsletter .cf-btn .cf-btn-text {
    color: var(--cream-100) !important; }
"""

RESTORE += """
/* \u2500\u2500 Hero type, scaled for the shorter Joomla hero \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
   Daniel's note: the headline crowds the photograph here in a way it does
   not on the prototype. Measured at 1440x900:

     prototype   hero 900px, text block 520px, 380px of image above it
     Joomla      hero 728px (the header takes 172px), same 520px of text,
                 leaving only 208px of image

   The text is not too big in itself, it is too big for a hero that lost
   172px. Keeping the prototype's proportion of 58% text to hero means a
   422px text block in a 728px hero, so everything here is the prototype's
   value times 0.81. The prototype itself is untouched: its hero is still
   the full viewport, and these rules only apply inside .fx-home. */
  .fx-home .hero__title {
    font-size: clamp(32px, 4.85vw, 65px); margin-bottom: 19px; }
  .fx-home .hero__subtitle {
    font-size: clamp(22px, 2.55vw, 29px); margin-bottom: 29px; }
"""

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
counter = ''.join(between(src, lambda l: l.strip() == '<script>',
                               lambda l: l.strip() == '</script>', 'counter script'))
counter = re.sub(r'^\s{4}', '', counter, flags=re.M)
counter = counter.replace("document.querySelectorAll('[data-target]')",
                          "root.querySelectorAll('[data-target]')")
counter = re.sub(r'^[ \t]+(const counterObserver)', r'  \1', counter, flags=re.M)
# a wrong slice used to fail silently, so check what came out
for must in ('animateCounter', 'IntersectionObserver', 'requestAnimationFrame'):
    if must not in counter:
        raise SystemExit(f'build: counter script is missing {must}; the slice is wrong')

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
# The newsletter module, saved from the live site with its session tokens
# stripped, so the preview shows the restyle in its real markup.
chrome_news = open(os.path.join(HERE, 'joomla-newsletter.html')).read()
# The live <head> carries five inline <style> blocks holding 56 custom
# properties: the whole colour palette, including the header background.
# Without them the chrome renders unpainted, so the preview must load them
# first, in the order the live page does.
chrome_vars = open(os.path.join(HERE, 'joomla-inline-head.css')).read()
# The social icons are CSS mask images set in a style attribute:
#   style="--icon-mask-url:url(/images/icons/.../facebook.svg)"
# Absolutising src= and href= misses those, so on Vercel they resolved
# against the preview's own domain and the icon row came out empty.
for _name in ('chrome_hdr', 'chrome_ftr'):
    globals()[_name] = re.sub(r'url\((/(?!/))', r'url(https://felidaefund.org\1',
                              globals()[_name])
harness_art = open(f'{OUT}/article.html').read()
def _preview_src(m):
    # Joomla gets a flat folder of JPEGs; prototype/assets still holds the
    # webp originals, and the badges in a subfolder. Map back to whatever
    # actually exists so the preview never shows a broken image.
    name = m.group(1)
    stem = os.path.splitext(name)[0]
    for rel in (stem + '.webp', name, 'badges/' + stem + '.webp', 'badges/' + name):
        if os.path.exists(os.path.join(P, 'assets', rel)):
            return f'src="assets/{rel}"'
    raise SystemExit(f'preview: no source on disk for {name}')
harness_art = re.sub(r'src="/images/homepage/([^"]+)"', _preview_src, harness_art)
preview = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Homepage — Joomla build preview</title>
<link rel="icon" type="image/svg+xml" href="https://felidaefund.org/templates/genesis4/images/favicon.svg" />
<link href="https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;500;600;700;800&family=Literata:ital,wght@0,300;0,400;0,500;1,300;1,400&display=swap" rel="stylesheet">
<!-- The live site's four stylesheets, in the live order, so this page shows
     exactly what the article will look like once it is pasted into Joomla.
     The header, footer and newsletter are the live site's real markup, and
     the homepage sits inside the same after-content wrappers it occupies on
     Joomla. So this page exercises the same CSS the real one does, which is
     what makes it worth reviewing instead of a screenshot. The signup is
     inert here: its session tokens are stripped and submit is disabled.
     The homepage CSS and JS are inlined so this page is self-contained and
     works from Vercel, the local server, or straight off disk. -->
<style>
@VARS@
</style>
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
<main>
<article class="default item-page">
  <section class="intro"><div class="headline-details center"><div class="headline">
    <h1>Home</h1></div></div></section>
  <section class="default"></section>
</article>
<!-- the module's real wrappers: after-content > inner > moduletable > mod-custom -->
<section class="after-content">
  <div class="after-content-inner">
    <div class="moduletable "><div class="mod-custom custom">
@ART@
    </div></div>
  </div>
</section>
@NEWSLETTER@
</main>
@FOOTER@
<script>
@JS@
</script>
</body></html>
""".replace('@B@', B).replace('@ART@', harness_art) \
    .replace('@CSS@', open(f'{OUT}/homepage.css').read()) \
    .replace('@JS@',  open(f'{OUT}/homepage.js').read()) \
    .replace('@NEWSLETTER@', chrome_news) \
    .replace('@VARS@', chrome_vars) \
    .replace('@HEADER@', chrome_hdr).replace('@FOOTER@', chrome_ftr)
open(f'{P}/joomla-preview.html','w').write(preview)
# ── one paste for the Joomla module: markup + script together ─────────
# The template would be a tidier home for the script, but that means
# editing index.php. Inlining it keeps the whole homepage in one Custom
# HTML module, which is also what gets removed if it is ever rolled back.
open(f'{OUT}/module.html','w').write(
    ARTICLE_HTML + '\n<script>\n' + open(f'{OUT}/homepage.js').read().rstrip() + '\n</script>\n')
print('module.html  (article + inlined script, paste this into the module)')

print('joomla-preview.html -> prototype/')
print('article.html', len(open(f'{OUT}/article.html').read()), 'bytes')
print('homepage.css', len(open(f'{OUT}/homepage.css').read()), 'bytes')
print('homepage.js ', len(open(f'{OUT}/homepage.js').read()), 'bytes')
