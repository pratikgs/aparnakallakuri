#!/usr/bin/env python3
"""
Stamp the CSS and JS links in index.html with a hash of their contents.

GitHub Pages serves every file with `cache-control: max-age=600` and no hash in
the filename. For ten minutes after a deploy a browser can therefore pair the
new index.html with the *previous* stylesheet and script — the markup for a new
feature arrives while the code that drives it does not. That is not theoretical:
it shipped a nav menu button that rendered but could not open.

Adding ?v=<hash> makes the URL change whenever the file changes, so new markup
can only ever load the assets it was built against.

Usage:  python3 scripts/stamp-assets.py         # rewrite index.html
        python3 scripts/stamp-assets.py --check  # exit 1 if stale (used by check.py)
"""

import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
INDEX = os.path.join(SITE, "index.html")

# (path relative to site/, regex capturing the whole href/src value)
ASSETS = [
    ("assets/css/styles.css", re.compile(r'(href=")(/assets/css/styles\.css)(\?v=[0-9a-f]+)?(")')),
    ("assets/js/main.js",     re.compile(r'(src=")(/assets/js/main\.js)(\?v=[0-9a-f]+)?(")')),
]


def digest(rel):
    with open(os.path.join(SITE, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:10]


def stamp(html):
    changed = []
    for rel, pat in ASSETS:
        want = digest(rel)
        m = pat.search(html)
        if not m:
            raise SystemExit("ERROR    %s is not linked from index.html" % rel)
        have = (m.group(3) or "")[3:]
        if have != want:
            changed.append((rel, have or "none", want))
        html = pat.sub(lambda mm, w=want: "%s%s?v=%s%s"
                       % (mm.group(1), mm.group(2), w, mm.group(4)), html, count=1)
    return html, changed


def main():
    with open(INDEX, encoding="utf-8") as fh:
        html = fh.read()
    new, changed = stamp(html)

    if "--check" in sys.argv:
        if changed:
            for rel, have, want in changed:
                print("ERROR    %s is stamped %s but its contents hash to %s"
                      % (rel, have, want))
            print("         Run: python3 scripts/stamp-assets.py")
            return 1
        return 0

    if not changed:
        print("Asset stamps already current.")
        return 0
    with open(INDEX, "w", encoding="utf-8") as fh:
        fh.write(new)
    for rel, have, want in changed:
        print("stamped  %-24s %s -> %s" % (rel, have, want))
    return 0


if __name__ == "__main__":
    sys.exit(main())
