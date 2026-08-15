# aparnakallakuri.com

Aparna Kallakuri's personal site. Plain static HTML/CSS/JS — **no build step, no
framework, no dependencies**. `site/` is published exactly as it sits on disk.

Aparna is a marketing and communications leader, not an engineer. She edits this
site by asking you for changes in plain English. Treat her requests as content
direction, and handle the markup yourself.

## Layout

```
site/                       everything that gets published
  index.html                the entire page — all content lives here
  assets/css/styles.css     design tokens + all styling
  assets/js/main.js         theme toggle, scroll reveal, count-up, fan diagram
  assets/img/               headshot, og.png (link-preview card)
  Aparna-Kallakuri-CV.pdf   public CV — phone number already removed
  CNAME robots.txt sitemap.xml
scripts/check.py            pre-deploy checks (run before every commit)
scripts/make-web-cv.py      regenerates the public CV from the master résumé
.github/workflows/deploy.yml
"Aparna Kallakuri Resume_*.pdf"   master résumé — gitignored, never committed
```

The master résumé is deliberately **not** in the repo: it carries her mobile
number, so keeping it out means repo visibility can never leak it.

## Before you commit — always

```bash
python3 scripts/check.py
```

It verifies tag balance, that every local link and asset resolves, one `<h1>`,
alt text on images, required files, and that no private phone number leaks into
`site/`. The same script gates deployment, so a failure here means a failure in
CI. Fix it before committing rather than pushing and hoping.

To preview locally: `cd site && python3 -m http.server 8080`.

## Rules

**Never publish her phone number.** It is deliberately absent from the site and
scrubbed from the public CV. If she asks to add a phone number, confirm she means
to make it public — it will be scraped. `scripts/check.py` blocks it either way,
so add it to `PRIVATE_STRINGS` there if the policy ever changes.

**If she replaces the CV**, the master résumé lives at the repo root and the
public copy is generated: `python3 scripts/make-web-cv.py`. Never copy the master
into `site/` directly — it carries her mobile number in the visible text, the
tagged structure tree, and the bookmark titles.

**Use the design tokens.** Every colour, size and spacing value is a CSS custom
property at the top of `styles.css`. Never hard-code a hex value in a component
rule — it will break one of the theme states.

**Keep facts verifiable.** Every claim on this page traces to her résumé or her
LinkedIn profile. If she asks for a new stat or achievement, use her wording; do
not invent supporting detail, round numbers up, or embellish a result.

## Design system — "Positioned"

The visual language is borrowed from analyst evaluation charts — Gartner Magic
Quadrant, IDC MarketScape — because that is the vernacular of her industry, and
she personally built the analyst programme that put ZainTECH in those Leader
quadrants. The site is an instrument, not a magazine: coordinate grids, plotted
intervals, axis ticks, spec sheets.

Dark is the primary expression; light is a designed alternative, not an
inversion.

| | Dark (default) | Light |
|---|---|---|
| Ground | `#0c0a14` violet-black | `#ffffff` |
| Ink | `#f3f0fa` | `#14111f` |
| Grid | `#241f38` | `#e7e4f0` |
| Violet | `#8b5cf6` / `--violet-ink #a98bff` | `#6d3ee8` / `#5b29dc` |
| Signal | `#2dd4b0` / `--signal-ink #3dd9b4` | `#00a389` / `#00755e` |

Type: **Archivo** (display, set at `wdth 108-118` via the variable width axis —
that expanded setting is the signature; use the `.display` class), **IBM Plex
Sans** (body — a nod to her twelve years at IBM), **IBM Plex Mono** (data,
labels, dates).

Three rules that are easy to break:

- **Colour carries meaning.** Violet is structure, navigation and the system.
  **The signal teal means an outcome** — a result, a number she delivered. If it
  is teal it is a result. Never use it decoratively, and never render a result in
  violet. One deliberate exception: the unit signs (`$ M % +`) in the readout row
  are violet, because they qualify a figure rather than being the result.
  The signal colour was coral until it proved muddy against violet on the light
  ground; teal-green sits clear of violet on the wheel and reads as growth.
- **Two tokens per accent.** `--violet` / `--signal` are for fills, bars and
  marks; `--violet-ink` / `--signal-ink` are the text-safe versions. Using a fill
  token as text fails contrast in one of the themes.
- **Themes are defined three times.** Bare `:root` (dark), then
  `@media (prefers-color-scheme: light)` guarded as
  `:root:not([data-theme="dark"])`, then `:root[data-theme="light"]`. A colour
  defined in only one of those blocks renders one theme's text on the other
  theme's ground. Change a token in all three places.

## Section patterns

`index.html` is commented by section. To add an item, copy the nearest sibling
block and edit it — the classes carry all the styling.

- **An employer** — a `<button class="mk" role="tab">` in `.roster__marks` plus a
  matching `<section class="panel" role="tabpanel">`. The button's `data-key`,
  its `id` (`t-<key>`), and the panel's `id` (`p-<key>`) must all agree, and the
  career chart row's `data-target` must use the same key — that is what keeps the
  chart and the tabs in sync. Order is newest first.
- **An outcome** — an `<li>` in `.outcomes`: `<b>` the figure, `<span>` what it
  measured. `.outcomes` is one shared grid and each `li` is `display: contents`,
  so the figures line up in a true column. Don't give the `li` its own grid.
- **A case note** — `<article class="spec">` in `#proof`, always Context / Move /
  Result. The result column carries `class="res"`, which is what makes it teal.
- **A testimonial** — `<figure class="voice">` in `#voices`.
- **A stat** — `<div class="readout__item">`. `data-count` drives the count-up and
  must be a bare integer, with any `$`, `%` or `+` in a sibling `<span class="u">`.

**The career chart** is generated SVG with real geometry: the x-axis is a true
linear time scale from May 2007, so bar positions encode actual dates. Do not
hand-edit the coordinates. If her roles change, recompute them — the mapping is
`x = 132 + (2026.58 - t) / (2026.58 - 2007.33) * 856`, where `t` is a decimal
year.

**Both axes run newest-first.** Rows are reverse chronological (most recent at
the top) and the **time axis is reversed** — 2026 sits at the left edge and time
runs backwards to the right. Because of that inversion a bar's *left* edge comes
from its **end** date and its right edge from its start date; getting this
backwards produces negative widths. Year ticks descend left to right.

Each `.ct-row` is a real button with `role`, `tabindex` and an `aria-label`.

**The fan diagram** in "One offering, nine assets" is hand-authored SVG.
Within-group dot spacing is 14px and between-group 27px so the three journey
stages read as three groups. Change a dot and change its path endpoint to match.

## Company marks

The five employer marks are the companies' **real logos**, inlined as SVG.
Sources: IBM and EY from Wikimedia Commons (both hosted there as public domain,
being below the threshold of originality), HP from Simple Icons (CC0), and
ZainTECH and Soroco from the companies' own websites.

Rules for these:

- **Monochrome via `currentColor`.** Every fill is rewritten to `currentColor` so
  the wall reads as one set and works in both themes. Do not reintroduce brand
  colours — five clashing palettes on a violet ground looks like a sponsor
  banner, and mixed light/dark logo variants break one of the themes.
- **Each carries its own `--lh`.** Aspect ratios run from ~6:1 (ZainTECH) to 1:1
  (HP). Equal heights would make the wide wordmarks dwarf the round marks, so
  every logo has a hand-tuned optical height on `.mk__logo`. Re-tune by eye if
  you swap one.
- **EY's viewBox is cropped** to `0 0 479 400` to drop the "Building a better
  working world" tagline, which is illegible at this size. The paths are
  untouched.
- **The accessible name lives on the button**, as `aria-label`, because the SVG
  replaced the text that used to name it. Every `.mk` must keep one.

Trademarks belong to their owners. The footer carries a notice
(`.footer__legal`) stating that the logos identify former employers and imply no
endorsement or affiliation. **Do not remove it while the logos are in use** —
it is what makes this nominative use rather than an implied endorsement.

## Deployment

Push to `main` → checks run → GitHub Pages publishes → live in about a minute.
There is nothing to build and nothing to run by hand. A failed check means the
old version stays live.

When you finish a change for Aparna, commit and push it, then tell her plainly
what changed and that it will be live in a minute or two. Do not leave her work
sitting uncommitted — an uncommitted change is not on her website.
