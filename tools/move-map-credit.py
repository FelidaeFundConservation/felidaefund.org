"""Move the IUCN credit out of body prose and into the map figure.

On the pages still showing the static map it becomes that figure's
caption; the live map component does the same thing in its own injector.
"""
import glob, os, re, sys

CREDIT = re.compile(r'[ \t]*<p><em>(Distribution map courtesy of(?:(?!</em>).)*)</em></p>\n?', re.I | re.S)
FIG = re.compile(r'(<figure class="prose-figure"><img src="[^"]*-map-960\.webp"[^>]*/>)</figure>')

n = 0
for f in sorted(glob.glob(os.path.join(sys.argv[1], 'species-*.html'))):
    s = open(f, encoding='utf-8').read()
    c = CREDIT.search(s)
    if not c or not FIG.search(s):
        continue
    line = c.group(1).strip()
    s = CREDIT.sub('', s, count=1)
    s = FIG.sub(lambda m: m.group(1) +
                f'<figcaption class="rangemap__credit">{line}</figcaption></figure>', s, count=1)
    open(f, 'w', encoding='utf-8').write(s)
    n += 1
print(f'{n} page(s) updated')
