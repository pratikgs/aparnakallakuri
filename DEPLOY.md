# Deploying aparnakallakuri.com

Hosting is **GitHub Pages**, driven by `.github/workflows/deploy.yml`. No second
account, no build step, no bill.

**Status: live.** Repo `pratikgs/aparnakallakuri`, Pages enabled with the Actions
source, first deploy green, custom domain claimed. The only outstanding step is
**the DNS records in section 3** — until those exist the site is reachable only
at its temporary address, and will render unstyled there (see the note at the
end of section 3).

Sections 1 and 2 are kept as a record of what was done, and for rebuilding from
scratch.

---

## 1. Push the repo

```bash
cd /Users/pratik/work/aparna
git add -A
git commit -m "Aparna Kallakuri personal site"
gh repo create aparnakallakuri --public --source=. --push
```

**The repo must be public on a GitHub Free account.** Pages only publishes from a
private repo on Pro, Team or Enterprise. That is fine here: the master résumé —
the only file holding her phone number — is gitignored and never committed, so
nothing private is in the repo. The published site is public either way.

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

The domain is already claimed on the repo (`cname: aparnakallakuri.com`), which
is what stops anyone else pointing their Pages site at it. What remains is DNS.

**The domain is registered at Namecheap** on Namecheap BasicDNS
(`dns1/dns2.registrar-servers.com`). Go to **Domain List → Manage
aparnakallakuri.com → Advanced DNS**.

First **delete the parking records** Namecheap adds by default — typically a
`CNAME` for `www` pointing at `parkingpage.namecheap.com`, and an A or *URL
Redirect Record* on `@`. Leaving them in place will fight the records below.

Then add:

| Type | Host | Value | TTL |
|---|---|---|---|
| A Record | `@` | `185.199.108.153` | Automatic |
| A Record | `@` | `185.199.109.153` | Automatic |
| A Record | `@` | `185.199.110.153` | Automatic |
| A Record | `@` | `185.199.111.153` | Automatic |
| CNAME Record | `www` | `pratikgs.github.io.` | Automatic |

All four A records — they are GitHub's Pages load balancers and the redundancy
is the point. The CNAME value is the *account* host, `pratikgs.github.io`, not
the repo.

Then **Settings → Pages** on the repo: wait for the DNS check to go green and
tick **Enforce HTTPS**. That box stays greyed out until GitHub issues the
certificate — usually minutes, occasionally up to an hour.

Verify:

```bash
dig +short aparnakallakuri.com                    # expect the four 185.199.x.x
curl -sI https://aparnakallakuri.com | head -1    # expect HTTP/2 200
```

While DNS is still on Namecheap parking, `dig` returns `162.255.119.146`. When it
returns the four GitHub addresses instead, it has switched.

**The temporary address renders unstyled — this is expected.** Until the domain
resolves, the site is served from `https://pratikgs.github.io/aparnakallakuri/`,
a sub-path. The page links its CSS, JS and images as root-relative paths
(`/assets/...`), which is correct for the apex domain where the site sits at `/`,
but resolves to `pratikgs.github.io/assets/...` on the sub-path and 404s. Nothing
is broken and nothing needs changing — attaching the domain fixes it. Do **not**
"fix" this by rewriting the paths to be relative; that would break the real site.

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
