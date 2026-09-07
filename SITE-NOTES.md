# Open questions about the content

Everything on the site traces to Aparna's résumé, her LinkedIn profile, or both.
These are the points where the two sources disagree, or where a judgement call
was made that she should confirm.

### 1. The headshot is only 160×160

It was extracted from the résumé PDF — the only copy available. It is sharp
enough at the 148px it renders at, but soft on retina screens and in link
previews. Replace `site/assets/img/aparna-kallakuri.png` with a 600px+ original
and regenerate the link-preview card.

### 2. ZainTECH end date

The résumé (July 2026) says Jun 2024 – Jul 2026. Her LinkedIn still says
"Present". The site follows the résumé and shows 2024–2026, and the hero still
describes her as Senior Manager, Content Strategy at ZainTECH. Worth confirming
which is current.

### 3. There is no "open to opportunities" badge

Her recent LinkedIn activity is almost entirely job applications, so she probably
wants one — but asserting an employment status she hasn't published publicly
wasn't a call to make for her. One line under the hero eyebrow:

```html
<p class="eyebrow" style="color:var(--accent-ink)">Open to senior marketing roles</p>
```

### 4. The testimonials are excerpts

Condensed from LinkedIn recommendations written by **Aarti Kamath** and
**Aditi Som**. Reusing them is standard practice, but a note to each is a
courtesy — and they may be glad to be asked.

### 5. The `$200M` stat is her own aggregate

It comes from her LinkedIn About section. The résumé itemises `$60M` in
opportunities and `$6M` in revenue at IBM. Both figures are hers; they count
different things. If the number needs to survive line-by-line questioning in an
interview, swap it for the itemised ones.

### 6. Unverified claim, deliberately left off

A web search surfaced a claim that she spoke on a Web Summit Qatar panel
alongside JPMorganChase's CMO. No source substantiates it, so it is not on the
site. If it's true it's a strong addition — she would just need to confirm it.

### 7. What each market on the map actually covers

The market coverage map paints whole countries, so every regional acronym had
to be resolved to a country list. These live in `REGIONS` in
`scripts/make-market-map.py`; re-run it after any edit.

- **SPGI** — Spain, Portugal, Greece, **Italy**. Confirmed; the I is Italy, not
  Israel. Israel is not painted anywhere on the map.
- **MEA** — Middle East plus **North Africa** only. Iran and Turkey are not
  included.
- **North America** — United States and Canada. Mexico is its own market.
- **Poland** — read from "polamd" in the brief as a typo for Poland.
- **Sub-Saharan Africa was removed** after first being drawn. Africa below the
  Sahara is now background land, not a market.
- **Bahrain** has no polygon at Natural Earth's 110m resolution, so it is not
  drawn. The rest of the Gulf reads as one mass, so this is invisible in
  practice.

### 8. India is drawn from India's point of view

India uses Natural Earth's India edition, so Jammu and Kashmir is shown
entire — including Pakistan-administered Kashmir and Aksai Chin — as Indian
maps are required to show it. Every other country comes from the standard
edition, which draws the line of control instead. This is a deliberate choice,
not a data mismatch: audiences in India expect it, and audiences elsewhere are
very unlikely to notice.

### 9. The map has no labels and no dates

The legend was removed, so nothing on the figure names a market — the only
text is the section dek, "Ten markets across five continents". A reader who
does not recognise a shape learns nothing from it. The markets are still named
in the SVG `<title>`, so screen readers get the full list, but sighted readers
do not. Worth revisiting if the map is meant to carry the point on its own.

The map also says *where* but never *when*. Ten markets could be read as
current scope rather than nineteen years of accumulated scope; the fix is a
line in the figure caption, not more geometry.

### 10. Where the current copy came from

The Sep 2026 content pass took its wording from five documents Aparna supplied
(kept in her Downloads, not in the repo): *Core Expertise*, *Case Studies*,
*Description of each role in the company*, *Beyond the Day Job*, and
*AI-Enabled Marketing | How I Work*. Section copy is hers, lightly edited to
British spelling and the site's register. If a claim on the page needs
checking, those documents are the source, not the résumé.

Two things to know about that pass:

- **Mount Carmel teaching.** Her earlier brief said "Digital Marketing"; the
  *Beyond the Day Job* document says "Principles of Marketing". The document
  wins, since it is her own newer writing, but the year (2015–16) and audience
  (undergraduates) come from the brief. **Worth confirming which subject is
  right** — the two sources disagree and only she can settle it.
- **EY has no case study.** The *Case Studies* document covers ZainTECH,
  Soroco, MAFTECH and IBM WebSphere only, so the old EY case note was retired.
  Her EY outcomes still appear in the Experience panel.

### 11. What was dropped in the Sep 2026 pass

- The old **Areas of practice** four-cell grid, replaced by the six-area
  **Core expertise** matrix.
- Two old case notes: *One offering, nine assets* (the fan diagram moved to
  the new AI section, where it illustrates the workflow rather than sitting as
  a standalone result) and *Getting on the analysts' map* (the Leader
  recognition it carried survives in the ZainTECH experience panel and the
  hero lede).

---

## Resolved

- **Her phone number is off the public site and out of the public CV.** The
  master résumé held it in three independent places: the visible page content,
  the tagged-PDF structure tree (which screen readers announce), and the
  bookmark titles. `scripts/make-web-cv.py` strips all three;
  `scripts/check.py` fails the deploy if it ever reappears.
