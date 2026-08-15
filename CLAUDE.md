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

## Design system

Indigo + marigold on limestone. The marigold is drawn from the backdrop of her
own headshot.

| | Light | Dark |
|---|---|---|
| Ground | `#e9eae5` limestone | `#0c1426` deep indigo |
| Ink | `#101b33` | `#edede6` |
| Accent | `--accent` marks · `--accent-ink` small text · `--accent-display` large text | `#f0b23c` |

Type: **Newsreader** (display serif), **IBM Plex Sans** (body — a nod to her
twelve years at IBM), **IBM Plex Mono** (dates, stats, labels).

Two things that are easy to get wrong:

- **Three accent tokens, not one.** Marigold fails contrast as small text on
  limestone. `--accent-ink` (7.0:1) is for body-size accent text,
  `--accent-display` (3.7:1, large-text AA) only for big serif moments, and
  `--accent` for marks and rules. Do not collapse them.
- **Themes are defined three times.** Bare `:root` (light), then
  `@media (prefers-color-scheme: dark)` guarded as `:root:not([data-theme="light"])`,
  then `:root[data-theme="dark"]`. A colour defined only inside one of those
  blocks renders one theme's text on the other theme's background. Always change
  a token in all three places.

## Section patterns

`index.html` is commented by section. To add an item, copy the nearest sibling
block and edit it — the classes carry all the styling.

- **A job** — `<article class="job">` in `#career`, newest first. The IBM entry
  nests its four sub-roles in a `<details class="subroles">`.
- **A case note** — `<article class="case">` in `#proof`, always Context / Move /
  Result in that order. Result text renders in the accent colour.
- **A testimonial** — `<figure class="voice">` in `#voices`.
- **A stat** — `<div class="numbers__item">` in the numbers band. The
  `data-count` attribute drives the count-up animation; it must be a bare
  integer, with any `$`, `%` or `+` in a sibling `<span class="unit">`.
- **A detail list** — `<div class="detail">` in `#beyond`. Inside each `<li>`,
  `<b>` is the label and `<span>` the supporting line; both render as blocks.

The fan diagram in "One offering, nine assets" is hand-authored SVG. Node
coordinates are commented — within-group spacing is 14px and between-group 27px
so the three journey stages read as three groups. If you change one dot, change
its path endpoint to match.

## Deployment

Push to `main` → checks run → GitHub Pages publishes → live in about a minute.
There is nothing to build and nothing to run by hand. A failed check means the
old version stays live.

When you finish a change for Aparna, commit and push it, then tell her plainly
what changed and that it will be live in a minute or two. Do not leave her work
sitting uncommitted — an uncommitted change is not on her website.
