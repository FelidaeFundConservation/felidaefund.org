import re, sys

DROP = re.compile(r'\.nav__|\.nav\b|\.footer|\.modal|\.donate-freq|\.donate-amount|\.donate-custom'
                  r'|\.donate-impact|\.donate-submit|\.donate-note|\.newsletter|\.sr-only')

def split_blocks(css):
    """Yield (prelude, body) for each top-level block."""
    out, depth, buf, start = [], 0, '', 0
    i = 0
    while i < len(css):
        ch = css[i]
        if ch == '{':
            if depth == 0:
                prelude = css[start:i]
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                out.append((prelude, css[css.index('{', start)+1:i]))
                start = i+1
        i += 1
    return out

def prefix_sel(sel):
    s = sel.strip()
    if not s: return None
    if s.startswith('.fx-home'): return s
    if DROP.search(s): return None
    if s.startswith('[data-theme'): return None
    if s == 'html': return None                     # replaced by a hand-written .fx-home rule
    if s == 'body': return '.fx-home'
    if s == ':root': return ':root'
    if s in ('*', '*::before', '*::after'): return '.fx-home ' + s
    if re.fullmatch(r'[a-z]+[a-z0-9]*', s): return '.fx-home ' + s   # bare element: img, a, button
    return '.fx-home ' + s

def scope_rules(css, indent='  '):
    lines = []
    for prelude, body in split_blocks(css):
        pre = prelude.strip()
        # keep leading comments that sit in the prelude
        comments = re.findall(r'/\*.*?\*/', pre, re.S)
        pre = re.sub(r'/\*.*?\*/', '', pre, flags=re.S).strip()
        if pre.startswith('@keyframes'):
            lines.append(f'{indent}{pre} {{{body}}}')
            continue
        if pre.startswith('@media') or pre.startswith('@supports'):
            inner = scope_rules(body, indent + '  ')
            if inner.strip():
                lines.append(f'{indent}{pre} {{\n{inner}\n{indent}}}')
            continue
        sels = [prefix_sel(x) for x in pre.split(',')]
        sels = [x for x in sels if x]
        if not sels: continue
        decl = ' '.join(l.strip() for l in body.strip().splitlines() if l.strip())
        if not decl: continue
        for c in comments:
            if '─' not in c: lines.append(f'{indent}{c}')
        lines.append(f'{indent}{", ".join(sels)} {{ {decl} }}')
    return '\n'.join(lines)

if __name__ == '__main__':
    print(scope_rules(open(sys.argv[1]).read()))
