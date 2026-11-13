"""Bind the last two words of a block so no single word is left alone.

text-wrap: pretty removes most orphans but will not force a break that
would make a worse line, so a few survive in narrow columns. This ties
the final space of each block with a non-breaking space, which is the
only way to guarantee it.

Run over the prototype's HTML; it is idempotent.
"""
import glob, os, re, sys

TAGS = ('p', 'h1', 'h2', 'h3', 'h4', 'figcaption', 'blockquote', 'li')
CLOSE = re.compile(r'</(' + '|'.join(TAGS) + r')>')
SKIP_IN = re.compile(r'<(script|style|svg|select|textarea)\b', re.I)
MAX_TAIL = 15          # a very long last word would overflow a narrow column


def protect(html):
    out, changed = html, 0
    # Work right to left so earlier offsets stay valid.
    for m in reversed(list(CLOSE.finditer(html))):
        end = m.start()
        # Walk back over trailing inline tags and whitespace.
        i = end
        tail = []
        while i > 0:
            if out[i - 1] == '>':
                j = out.rfind('<', 0, i)
                if j == -1:
                    break
                if SKIP_IN.match(out, j):
                    i = -1
                    break
                i = j
                continue
            break
        if i <= 0:
            continue
        # Blocks are often written with the closing tag on its own line,
        # so step over any trailing whitespace before looking for the word.
        while i > 0 and out[i - 1].isspace():
            i -= 1
        if i <= 0:
            continue
        # Collect the last word, then the space before it.
        k = i
        while k > 0 and not out[k - 1].isspace():
            if out[k - 1] in '<>':
                k = -1
                break
            tail.append(out[k - 1])
            k -= 1
        if k <= 0 or not tail:
            continue
        word = ''.join(reversed(tail)).strip()
        if not word or len(word) > MAX_TAIL:
            continue
        sp_end = k
        sp_start = k
        while sp_start > 0 and out[sp_start - 1].isspace():
            sp_start -= 1
        if sp_start == sp_end or sp_start == 0:
            continue
        if out[sp_start - 1] in '>':      # space right after a tag: leave it
            continue
        before = out[:sp_start]
        # need at least one more word in this block
        if not re.search(r'\w\s*$', before):
            continue
        if out[sp_start:sp_end] != ' ':
            out = before + ' ' + out[sp_end:]
            changed += 1

        # A hyphen is its own break opportunity, so binding "long-term
        # protection." still lets the line split after "long-". When the
        # second-to-last word is hyphenated, bind one word further back.
        prev = re.search(r'([^\s<>]+)\s*$', before)
        if prev and '-' in prev.group(1) and len(prev.group(1)) <= MAX_TAIL:
            ps_end = prev.start(1)
            ps_start = ps_end
            while ps_start > 0 and out[ps_start - 1].isspace():
                ps_start -= 1
            if (ps_start < ps_end and ps_start > 0 and out[ps_start - 1] != '>'
                    and re.search(r'\w\s*$', out[:ps_start])
                    and out[ps_start:ps_end] != ' '):
                out = out[:ps_start] + ' ' + out[ps_end:]
                changed += 1
            # The hyphen itself is still a break opportunity, so the line
            # can split after "long-". Swap it for a non-breaking hyphen,
            # which looks identical and holds the word together.
            w_start, w_end = prev.start(1), prev.end(1)
            out = out[:w_start] + out[w_start:w_end].replace('-', '\u2011') + out[w_end:]
    return out, changed


if __name__ == '__main__':
    total_f = total_c = 0
    for f in sorted(glob.glob(os.path.join(sys.argv[1], '*.html'))):
        if os.path.basename(f) == 'joomla-preview.html':
            continue
        src = open(f, encoding='utf-8').read()
        out, n = protect(src)
        if out != src:
            open(f, 'w', encoding='utf-8').write(out)
            total_f += 1
            total_c += n
    print(f'{total_c} blocks bound across {total_f} files')
