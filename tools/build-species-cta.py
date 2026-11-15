"""Turn the in-prose donation ask into a call to action.

On the live pages the ask is three paragraphs of body text at the end of
the Threats section with nothing to click, so it reads as part of the
article. This lifts it out into its own block with a real button.

The species name is taken from the page's own "write a comment with X"
line, which is the only place it is already written down.
"""
import glob, os, re, sys

ASK = re.compile(
    r'[ \t]*<h3>Want to help us research and conserve this[\s ]*species\?</h3>\s*'
    r'<p>(?P<body>Felidae Conservation Fund[^<]*)</p>\s*'
    r'<p><em>Make sure you write a comment with "(?P<name>[^"]+)"(?P<rest>[^<]*)</em></p>\n?',
    re.I)

AMOUNTS = ('10', '25', '50')


def block(name, body):
    chips = ''.join(
        f'<button type="button" class="cta__amt{" is-on" if a == "25" else ""}" '
        f'aria-pressed="{"true" if a == "25" else "false"}">${a}</button>'
        for a in AMOUNTS)
    return f'''        </div>
      </div>

      <div class="container">
        <aside class="cta" aria-labelledby="cta-h">
          <div class="cta__text">
            <h2 class="cta__title" id="cta-h">Help us protect the {name.lower()}</h2>
            <p class="cta__body">{body}</p>
          </div>
          <div class="cta__action">
            <div class="cta__amounts" role="group" aria-label="Monthly amount">{chips}<span class="cta__per">a month</span></div>
            <a class="btn-gold cta__go" href="#" onclick="openDonate(event)">Protect this cat</a>
            <p class="cta__note">Write &ldquo;{name}&rdquo; in the comment so we can designate 100% of your gift to this species.</p>
          </div>
        </aside>
      </div>

      <div class="container" hidden>
        <div>'''


def run(proto, only=None):
    n = 0
    for f in sorted(glob.glob(os.path.join(proto, 'species-*.html'))):
        if only and os.path.basename(f) != only:
            continue
        s = open(f, encoding='utf-8').read()
        if 'class="cta"' in s:
            continue
        m = ASK.search(s)
        if not m:
            continue
        body = m.group('body').replace(' ', ' ')
        s = s[:m.start()] + block(m.group('name'), body) + s[m.end():]
        open(f, 'w', encoding='utf-8').write(s)
        n += 1
    print(f'{n} page(s) given a call to action')


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
