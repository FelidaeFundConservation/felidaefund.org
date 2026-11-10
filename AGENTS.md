# Working with Irene on this repo

`design.md` covers what to build. This file covers how to talk about it.

## Replies

**Answer the question that was asked. Only that question.** If she asks for
a URL, give the URL. If she asks whether something works, say yes or no.
Findings she did not ask for are not a bonus, they are noise she has to read
past. Hold them until she asks, or drop them.

**Match the length to the ask.** A one-line question gets a one-line answer.
Analysis gets analysis. Never answer a small question with a long piece:
interesting material is not a reason to send it.

**State the point in the first sentence.** Not context, not setup, not what
you are about to do. The answer.

**Point form by default.** Bullets and tables, not paragraphs. Prose only
when the reasoning genuinely does not fit a list.

**Be punchy.** Lead with the answer. Then the reasoning. Then the caveats.
Never make her read three paragraphs to find the one sentence she asked for.

**Open with the question** when the reply needs locating — several threads
are usually open at once. Skip the restatement when she just asked and the
answer is one line.

**Explain the jargon.** Irene is a product designer who has taught herself
the engineering side. She is the most technical person on this team, and she
is still not a backend developer. Any term from a specialist's world gets a
plain-language gloss the first time it appears, in the same breath, without
being asked and without being condescending about it.

Not "add it to the CSP" but "add it to the Content Security Policy, the list
of outside domains the site is allowed to load from."

Not "it's a template override" but "it's a template override, a PHP file that
changes what Joomla outputs. PHP runs on the server, so breaking it can take
the page down, unlike CSS which only makes it look wrong."

Covers at least: CSP, COOP, PHP, template override, module position, custom
field, specificity, cascade, viewport, DOM, scoping, `!important`, srcset,
breakpoint, attribution, UTM.

**Give exact click paths for admin work.** "System → Plugins → search
codemirror → Editor - CodeMirror → Enabled → Save", not "enable CodeMirror".
Name the menu, the screen and the button.

## Accuracy

**Verify before asserting.** Check headers, read the CSS, measure in the
browser. Most of the real defects on this project were found by measuring
something that looked fine.

**Flag anything invented.** A new colour, a new value, a new section: say so
explicitly. Match what the prototype does rather than improving on it.

**Say when something is wrong.** Including when it was your own earlier
claim. Correct it in a sentence and move on.

## Her time

Felidae is unpaid volunteer work competing with a job search and an art show.
Protect the work that produces a portfolio artifact. Route vendor and account
questions back to whoever holds the login. Don't volunteer her for scope she
did not ask for.

## Email

No em dashes. Plain language. Grammar fixes only. Never change her meaning
unless it is logically wrong, and say so if you do.
