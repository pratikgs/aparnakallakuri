# Deploying aparnakallakuri.com

One-time setup. After this, every push to `main` republishes the site
automatically and nobody needs to touch this file again.

Hosting is **GitHub Pages**, driven by `.github/workflows/deploy.yml`. No second
account, no build step, no bill.

---

## 1. Push the repo

```bash
cd /Users/pratik/work/aparna
git add -A
git commit -m "Aparna Kallakuri personal site"
gh repo create aparnakallakuri --private --source=. --push
```

Private is fine — GitHub Pages serves public sites from private repos on Free
plans as long as the deployment goes through Actions, which is what this uses.
If you hit any restriction, `gh repo edit --visibility public` and re-run; the
repo is safe to make public because the master résumé (the only file holding her
phone number) is gitignored and never committed.

Keep that master PDF somewhere you can find it — it's the input to
`scripts/make-web-cv.py` whenever her CV changes.

## 2. Turn on Pages

**Settings → Pages → Build and deployment → Source: `GitHub Actions`.**

That is the only setting that matters. Do *not* pick "Deploy from a branch" —
the workflow won't be used and the checks will be skipped.

Push once and watch the **Actions** tab. You should see *Check the site* pass,
then *Publish*. The site will be live at `https://<you>.github.io/aparnakallakuri/`
before the domain is attached.

## 3. Point the domain

`site/CNAME` already contains `aparnakallakuri.com`, which claims the domain on
deploy. Add these records at whatever registrar holds the domain:

| Type | Name | Value |
|---|---|---|
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| CNAME | `www` | `<your-github-username>.github.io` |

Then **Settings → Pages → Custom domain** → enter `aparnakallakuri.com` → Save.
Wait for the DNS check to go green, then tick **Enforce HTTPS** (the certificate
can take up to an hour to issue; the tick box is greyed out until it's ready).

Verify:

```bash
dig +short aparnakallakuri.com
curl -sI https://aparnakallakuri.com | head -1
```

## 4. Give Aparna access

- **Settings → Collaborators → Add people** → her GitHub account → **Write**.
- Have her sign in at [claude.ai/code](https://claude.ai/code) with the same
  GitHub account and open the repo.
- Send her `EDITING.md`.

Write access is enough. She never needs to touch Settings, Actions, or DNS.

---

## How the safety net works

`.github/workflows/deploy.yml` runs `scripts/check.py` **before** publishing. It
fails the build — and skips the deploy entirely — on:

- unclosed or mismatched HTML tags
- a link or asset that points at a file which doesn't exist
- an in-page link to an anchor that isn't there
- an image with no alt text, or a missing/duplicated `<h1>`
- any required file missing (CSS, JS, CV, og image, CNAME…)
- **her phone number appearing anywhere in `site/`**

A failed check leaves the live site exactly as it was. The worst case for a bad
edit is that the site doesn't change — never that it breaks.

Pull requests get checked but never published, so a risky change can be opened as
a PR and reviewed first.

## Maintenance

Effectively none. There are no dependencies to update — the site is HTML, CSS and
one vanilla JS file, and the workflow uses pinned major versions of the official
GitHub actions.

The one recurring task: **when Aparna's résumé changes**, drop the new master PDF
at the repo root and run `python3 scripts/make-web-cv.py` (needs
`pip install pymupdf`). That regenerates the public copy with her mobile number
stripped from the visible text, the tagged structure tree, and the bookmark
titles — all three of which hold it independently. `scripts/check.py` will fail
the deploy if it's ever missed.

## Rolling back

```bash
git revert HEAD && git push        # undo the last change
```

Or **Actions → Publish site →** pick an earlier successful run → **Re-run all
jobs**.
