# Species page redesign — notes

Branch `species-redesign`, off `main` at 5d4a5ec. Reference page: `prototype/species-cheetah.html`
(heaviest of the 40 — 7 sections, 4 images).

## Donate: there are two asks, not one

They sit about forty lines apart at the bottom of every species page.

### Ask 1 — inside the prose, no button

`prototype/species-cheetah.html`, end of the Threats section. Present on **39 of 40** pages.

```html
<h3>Want to help us research and conserve this species?</h3>
<p>Felidae Conservation Fund helps researchers around the world study and protect felids of all sizes.</p>
<p><em>Make sure you write a comment with "Cheetah" so we can designate 100% of your
   donation to go to protecting this species.</em></p>
```

- Renders as plain prose on the cream page background.
- **No button, no link, no form.** It asks for a donation and gives the reader nothing to click.
- The "write a comment" line is a manual workaround for species designation — it exists because
  nothing carries the species through to the donation form.

### Ask 2 — the support section

`<section class="support">`, the last thing on the page. Present on **40 of 40**.

```html
<h2>Support the work behind this page</h2>
<p>Felidae is a 501(c)(3) nonprofit. Gifts fund field research, community science
   and habitat protection.</p>
<a href="#" class="btn-gold" onclick="openDonate(event)">Donate</a>
```

- Dark brown band, `rgb(31,18,4)`. Contrast measured fine in both colour schemes.
- Generic. No species context — the reader lands in the donation form with no indication
  they were reading about a cheetah.

### The "$25/mo · Protect this cat" version is NOT built

Does not appear in the repo, on the live site, or in the prototype. It is a mockup
(presumably Daniel's Figma). Treat as a proposal, not something to restyle.

### Open questions before designing this

1. **One ask or two?** Two weak asks is probably worse than one that works.
2. **Can the donate flow take a species parameter?** If Fundraise Up can accept it, the
   "write a comment" instruction disappears and the button can honestly promise designation.
   If it can't, the button must not claim it. Unresolved — ask before designing.
3. **Who sets the suggested amount?** `$25/mo` is a monthly default inherited from a mockup.
   That's a fundraising decision, not a design one. Route to Zara.

## Decisions made

| | |
|---|---|
| Design against | cheetah |
| Prev/next order | alphabetical, keep for now |
| Prev/next component | **missing from the prototype entirely** — exists on all live pages, dropped in the port. Needs rebuilding, not restyling. Live markup is `<nav class="pagenavigation">` with 218×218 thumbs at `/images/species/thumbs/<slug>` |

### Thumbnails: all 40 exist, but the extension is inconsistent

Checked every slug against the server.

- **37 are `.jpeg`**
- **3 are `.jpg`** — `african-asian-wildcat`, `domestic-cat`, `marbled-cat`

Do not hardcode `.jpeg`. A component that assumes it breaks on exactly those three,
one of which (`african-asian-wildcat`) is first alphabetically and so appears as the
"previous" target from `african-golden-cat`.

## Still open

- **Facts panel schema.** Only 3 fields appear on all 40, and one is `Publication Date`.
  Eleven different combinations of size fields across the set. This blocks the meta
  descriptions and the content ask to staff.
- **The variable section slot.** Cheetah has three sections no other page has
  ("Appearance & Build", "Speed of the Hunt", "Cheetah Cubs"). The template needs a
  defined home for them — flattening them would make all 40 pages identical and dull.
- **Threats heading.** `Threats to the Cheetah` — a different string on all 40.
  Deliberate pattern or should it be one label?
