# aparnakallakuri.com

Personal site for Aparna Kallakuri — integrated marketing leader, Dubai.

Plain static HTML/CSS/JS. No build step, no dependencies, no framework. The
`site/` folder is published exactly as it sits on disk.

| I want to… | Read |
|---|---|
| Update the website's content | [EDITING.md](EDITING.md) — written for Aparna, no technical knowledge assumed |
| Set up hosting and the domain | [DEPLOY.md](DEPLOY.md) |
| Work on the code | [CLAUDE.md](CLAUDE.md) — conventions, design system, guardrails |
| Know what's unresolved | [SITE-NOTES.md](SITE-NOTES.md) — open questions about the content |

## Layout

```
site/                        published as-is
  index.html                 the whole page
  assets/css/styles.css      design tokens + styling
  assets/js/main.js          theme toggle, scroll reveal, count-up, diagram
  assets/img/                headshot, link-preview card
  Aparna-Kallakuri-CV.pdf    public CV (phone number removed)
  CNAME robots.txt sitemap.xml
scripts/check.py             pre-deploy checks — gates every deploy
scripts/make-web-cv.py       regenerates the public CV from the master résumé
.github/workflows/deploy.yml push to main → checks → GitHub Pages
"Aparna Kallakuri Resume_*.pdf"            master résumé — gitignored, never committed
```

## Local development

```bash
cd site && python3 -m http.server 8080     # http://localhost:8080
python3 scripts/check.py                   # run before every commit
```

## Publishing

Push to `main`. Checks run, then GitHub Pages publishes — live in about a minute.
If the checks fail nothing is deployed and the live site is untouched.
