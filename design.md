# Design rules for the prototype

Read this before changing anything in `prototype/`. It applies to people
and to agents. It exists because most of the defects found so far were
not typos, they were a rule nobody had written down.

## The layers

Change things at the lowest layer that will do the job.

| File | Governs | Changing it affects |
|---|---|---|
| `tokens.css` | colour, type, radius, shadow, spacing scale, nav height | all 85 pages |
| `base.css` | reset, typography, container, buttons, section headings | all 85 pages |
| `components.css` | nav, footer, donate modal, newsletter | all 85 pages |
| `page.css` | interior page patterns: headers, fact boxes, cards, galleries, body copy | all pages except the homepage |
| `components/*.js` | the markup for nav, footer, donate modal | all 85 pages |
| a page file | that page's content and structure | one page |

Tokens cannot move a section or change a sentence. Layout and copy are
per page.

## Rules

**Never hardcode a colour.** Every painted colour must resolve to a token.
The check is in "Verifying" below; it currently passes at 100%.

**Don't invent sections.** The prototype is a port of a real site. If a
block has no equivalent on the live page, it needs someone's agreement
before it ships. Two things have already been removed for failing this:
a related-projects section and a theme picker.

**Don't ship a link that goes nowhere.** No `href="#"` placeholders, no
buttons pointing at pages that do not exist. If a destination is not
ready, do not render the control. The footer carried four dead legal
links for weeks because nobody applied this.

**No orphan headings.** A heading with nothing under it reads as a
section that failed to load. If the content moved elsewhere, the heading
goes with it.

**Emphasis is weight, not colour.** `strong` keeps the surrounding
colour. Load the weight you need rather than tinting text darker.

**Images take the largest variant available.** Joomla puts a thumbnail in
`src` and the real sizes in `srcset`. A small source image is held to its
own width rather than stretched across the column.

**Breadcrumbs follow the menu, not the URL.** The live site builds its
trail from the URL path, so `/science` reads "Home > Science & Research"
even though the menu files it under Learn. People navigate the menu.

**Port faithfully, flag defects.** If the live page has a broken link or
an odd bold run, carry it across and add it to the list below. Silently
correcting content hides problems from the people who own it.

## Verifying

Run these after any change. Each catches something the others do not.

1. **Tag balance.** Parse every page and every component template with an
   HTML parser. `node --check` cannot do this: component markup lives in
   a template literal, so broken HTML is still valid JavaScript. A nav
   shipped broken because that distinction was missed.
2. **Link audit.** Every internal `href` must resolve to a file that
   exists.
3. **Page sweep.** Load all 85 pages and assert: nav is one row at its
   token height, footer, donate modal, newsletter and breadcrumb are
   present, nothing scrolls horizontally. Repeat at 375px for the
   hamburger.
4. **Homepage geometry.** Compare section rectangles and document height
   against the previous commit served alongside. Measure after
   `document.fonts.ready` and at a fixed width: webfonts and viewport
   width both move the numbers, and both have caused false alarms.
5. **Compare against the live page.** Structural checks prove the
   prototype is internally consistent. They cannot tell you something was
   never carried across. Galleries, module text, body images and the
   newsletter were all lost this way, and all were found by a person
   looking at the live page.


## Refreshing content from the live site

Zara edits the live Joomla site. To pull those edits into the prototype:

```
python3 tools/port-from-joomla.py --fetch
```

That downloads all 83 source pages and regenerates the 85 prototype pages.
Without `--fetch` it reuses whatever is already cached in `tools/live/`,
which is git-ignored because it is derived data.

Two things this does not cover:

- The homepage is Daniel's hand-built page, not generated. Homepage copy
  has to be edited in `prototype/index.html`.
- Regenerating overwrites every generated page. Design changes belong in
  `tokens.css`, `page.css`, `components.css` or the component JS, never in
  a page file, or the next refresh erases them.

## Known defects on the live site

Carried across as-is. These are content decisions for Felidae, not bugs
to fix in the prototype.

- Tsavo Cheetah Project: "signing up free here" points at
  `/felidaefund.org`, which 404s.
- Ways to Donate: an email link missing its `mailto:` scheme, so it
  resolves to `/info@felidaefund.org`.
- Bay Area Bobcat Project: a bold run reads "The Project Team i",
  swallowing the first letter of "includes".
- `/careers` and `/take-action/volunteer-and-career-opportunities` are
  the same page under two URLs with two different titles.
- 39 species pages repeat the same boilerplate paragraph; 20 carry an
  identical IUCN map credit as body copy rather than as a caption.

## Known gaps in the prototype

- The IA is stored twice in `site-nav.js`: desktop dropdowns as markup,
  mobile as a lookup table. They have already drifted apart once.
- `tokens.css` and the WordPress `theme.json` palette have drifted on
  four slugs, `gold-500` visibly.
- Four accent tokens are provisional and need sign-off.
- Forms cannot receive submissions. The newsletter and the two volunteer
  forms are inert.
- 61 live pages are linked but not ported: news articles, store products,
  media sub-galleries, webinars, publications, archived projects.
