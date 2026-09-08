#!/usr/bin/env python3
"""
Pre-deploy checks for aparnakallakuri.com.

Runs in GitHub Actions before publishing. If anything here fails the deploy is
skipped and the currently live site stays up, so a bad edit never reaches the
public site.

Standard library only — no install step, nothing to break.

Usage:  python3 scripts/check.py
"""

import os
import re
import subprocess
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

# Aparna's mobile must never reach the public site. See scripts/make-web-cv.py.
PRIVATE_STRINGS = ["524309765", "+971 52", "+97152"]

REQUIRED_FILES = [
    "index.html",
    "assets/css/styles.css",
    "assets/js/main.js",
    "assets/favicon.svg",
    "assets/img/aparna-kallakuri.png",
    "assets/img/og.png",
    "Aparna-Kallakuri-CV.pdf",
    "CNAME",
    "robots.txt",
    "sitemap.xml",
]

# Elements that must be explicitly closed for the layout to hold together.
TRACKED = {"html", "head", "body", "header", "main", "footer", "section",
           "article", "div", "figure", "details", "ul", "ol", "nav", "blockquote"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr", "path", "circle", "rect", "use"}

errors = []
warnings = []


class Checker(HTMLParser):
    """Tracks tag balance, ids, and local references."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.ids = set()
        self.refs = []        # (attr_value, kind)
        self.anchors = []
        self.imgs_without_alt = 0
        self.h1 = 0
        self.title = None
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and "href" in a:
            self.anchors.append(a["href"])
            self.refs.append((a["href"], "href"))
        if tag in ("img", "script") and "src" in a:
            self.refs.append((a["src"], "src"))
        if tag == "link" and "href" in a:
            self.refs.append((a["href"], "href"))
        if tag == "img" and "alt" not in a:
            self.imgs_without_alt += 1
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self._in_title = True
        if tag in TRACKED and tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in TRACKED and tag not in VOID:
            if not self.stack:
                errors.append("Closing </%s> with nothing open (line %d)"
                              % (tag, self.getpos()[0]))
                return
            open_tag, line = self.stack.pop()
            if open_tag != tag:
                errors.append(
                    "Mismatched tags: <%s> opened on line %d but closed by </%s> "
                    "on line %d" % (open_tag, line, tag, self.getpos()[0]))

    def handle_data(self, data):
        if self._in_title:
            self.title = (self.title or "") + data


def check_html():
    path = os.path.join(SITE, "index.html")
    if not os.path.exists(path):
        errors.append("site/index.html is missing")
        return
    html = open(path, encoding="utf-8").read()

    p = Checker()
    p.feed(html)

    for tag, line in p.stack:
        errors.append("<%s> opened on line %d is never closed" % (tag, line))

    if p.h1 != 1:
        errors.append("Expected exactly one <h1>, found %d" % p.h1)
    if not p.title or not p.title.strip():
        errors.append("<title> is empty")
    if p.imgs_without_alt:
        errors.append("%d <img> tag(s) have no alt text" % p.imgs_without_alt)

    # Every in-page link must point at an id that exists.
    for href in p.anchors:
        if href.startswith("#") and len(href) > 1 and href[1:] not in p.ids:
            errors.append("Link to %s but no element has that id" % href)

    # Every local file reference must resolve on disk.
    for value, _ in p.refs:
        if value.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:")):
            continue
        rel = value.split("?")[0].split("#")[0].lstrip("/")
        if rel and not os.path.exists(os.path.join(SITE, rel)):
            errors.append("References %s but site/%s does not exist" % (value, rel))

    # Metadata that keeps link previews and search results working.
    for needle, label in [
        ('property="og:title"', "Open Graph title"),
        ('property="og:image"', "Open Graph image"),
        ('name="description"', "meta description"),
        ('rel="canonical"', "canonical URL"),
        ("application/ld+json", "structured data"),
    ]:
        if needle not in html:
            warnings.append("Missing %s — link previews or SEO will degrade" % label)

    desc = re.search(r'<meta name="description" content="([^"]*)"', html)
    if desc and len(desc.group(1)) > 300:
        warnings.append("meta description is %d chars; search engines cut around 160"
                        % len(desc.group(1)))


def check_required_files():
    for rel in REQUIRED_FILES:
        if not os.path.exists(os.path.join(SITE, rel)):
            errors.append("Required file missing: site/%s" % rel)


def check_private_data():
    """The phone number must not appear anywhere in the published folder."""
    for dirpath, dirnames, filenames in os.walk(SITE):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for name in filenames:
            if name.startswith("."):
                continue
            full = os.path.join(dirpath, name)
            blob = open(full, "rb").read()
            for secret in PRIVATE_STRINGS:
                if secret.encode() in blob:
                    rel = os.path.relpath(full, ROOT)
                    errors.append(
                        "%s contains a private phone number (%r). "
                        "For the CV, re-run: python3 scripts/make-web-cv.py"
                        % (rel, secret))


def check_cname():
    path = os.path.join(SITE, "CNAME")
    if os.path.exists(path):
        domain = open(path, encoding="utf-8").read().strip()
        if not domain or " " in domain or "/" in domain:
            errors.append("site/CNAME must contain just the domain, found %r" % domain)


def check_asset_stamps():
    """CSS and JS must be linked with a ?v= hash of their contents.

    Without it, GitHub Pages' 10-minute cache can pair new markup with the
    previous stylesheet and script. See scripts/stamp-assets.py.
    """
    stamper = os.path.join(ROOT, "scripts", "stamp-assets.py")
    if not os.path.exists(stamper):
        warnings.append("scripts/stamp-assets.py is missing; asset URLs unchecked")
        return
    rc = subprocess.call([sys.executable, stamper, "--check"])
    if rc != 0:
        errors.append("asset cache stamps are out of date "
                      "(run: python3 scripts/stamp-assets.py)")


def main():
    check_required_files()
    check_html()
    check_private_data()
    check_cname()
    check_asset_stamps()

    for w in warnings:
        print("WARNING  %s" % w)
    for e in errors:
        print("ERROR    %s" % e)

    if errors:
        print("\n%d problem(s) found. The site was NOT deployed — the version "
              "already live stays up, untouched." % len(errors))
        return 1

    print("All checks passed%s. Safe to deploy." %
          (" (%d warning(s))" % len(warnings) if warnings else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
