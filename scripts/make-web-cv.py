#!/usr/bin/env python3
"""
Build the public, web-safe copy of Aparna's CV from the master résumé.

The master PDF carries her personal mobile number. Publishing it invites
scraping, so this script removes it in three places — the number survives in
all of them independently:

  1. the visible page content stream,
  2. the tagged-PDF structure tree (/T and /E on StructElem objects, which
     screen readers announce),
  3. the document outline / bookmark titles (/Title).

Redacting only the first leaves the number trivially recoverable with `strings`.

The contact line is re-typeset using the résumé's own embedded Calibri subset,
so the result is visually identical apart from the removed number.

Usage:  python3 scripts/make-web-cv.py
Needs:  pip install pymupdf
"""

import os
import sys
import tempfile

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("PyMuPDF is required:  pip install pymupdf")

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(HERE, "Aparna Kallakuri Resume_July 2026.pdf")
OUT = os.path.join(HERE, "site", "Aparna-Kallakuri-CV.pdf")

PHONE = "524309765"
REMOVE = "+971 524309765 | "  # dropped from the contact line, separator and all
LINK = "https://www.linkedin.com/in/aparna-kallakuri-1655204/"
KEEP_PRE = "Dubai, UAE | aparna15k@gmail.com | "
KEEP_LINK = "LinkedIn"

INK = (0x1E / 255, 0x1E / 255, 0x1E / 255)
BLUE = (0x00 / 255, 0x36 / 255, 0x6D / 255)


def main():
    if not os.path.exists(SRC):
        sys.exit("Master résumé not found: %s" % SRC)

    doc = fitz.open(SRC)
    page = doc[0]

    # --- Extract the embedded Calibri subset so the rebuilt line matches. ---
    fontfile = os.path.join(tempfile.mkdtemp(), "calibri.ttf")
    for f in page.get_fonts(full=True):
        if f[3].endswith("+Calibri"):
            doc.extract_font(f[0])
            with open(fontfile, "wb") as fh:
                fh.write(doc.extract_font(f[0])[3])
            break
    else:
        sys.exit("Could not find the embedded Calibri font in the source PDF.")

    # --- Locate the contact line and record its exact geometry. ---
    line = None
    for block in page.get_text("dict")["blocks"]:
        for candidate in block.get("lines", []):
            if PHONE in "".join(s["text"] for s in candidate["spans"]):
                line = candidate
    if line is None:
        sys.exit("Contact line containing the phone number was not found.")

    bbox = fitz.Rect(line["bbox"])
    baseline = line["spans"][0]["origin"][1]
    size = line["spans"][0]["size"]

    # --- 1. Visible content: drop the old line and its hyperlink. ---
    for lk in page.get_links():
        if fitz.Rect(lk["from"]).intersects(bbox):
            page.delete_link(lk)
    page.add_redact_annot(bbox + (-1, -1, 1, 1))
    page.apply_redactions()

    # --- Re-typeset the line, centred on the original, phone removed. ---
    page.insert_font(fontname="cal", fontfile=fontfile)
    font = fitz.Font(fontfile=fontfile)
    w_pre = font.text_length(KEEP_PRE, size)
    w_link = font.text_length(KEEP_LINK, size)
    x = bbox.x0 + (bbox.width - (w_pre + w_link)) / 2

    page.insert_text((x, baseline), KEEP_PRE, fontname="cal", fontsize=size, color=INK)
    page.insert_text((x + w_pre, baseline), KEEP_LINK, fontname="cal", fontsize=size, color=BLUE)

    # "LinkedIn" is underlined in the master; insert_text does not draw that.
    underline_y = baseline + size * 0.10
    page.draw_line((x + w_pre, underline_y), (x + w_pre + w_link, underline_y),
                   color=BLUE, width=size * 0.05)

    page.insert_link({
        "kind": fitz.LINK_URI,
        "from": fitz.Rect(x + w_pre, bbox.y0, x + w_pre + w_link, bbox.y1),
        "uri": LINK,
    })

    # --- 2 & 3. Structure tree and bookmark titles. ---
    patched = 0
    for xref in range(1, doc.xref_length()):
        for key in ("T", "E", "Title", "Alt", "ActualText", "TU"):
            try:
                typ, val = doc.xref_get_key(xref, key)
            except Exception:
                continue
            if typ == "string" and PHONE in val:
                doc.xref_set_key(xref, key, fitz.get_pdf_str(val.replace(REMOVE, "")))
                patched += 1

    doc.set_metadata({})
    doc.del_xml_metadata()
    doc.save(OUT, garbage=4, deflate=True, clean=True)
    doc.close()

    # --- Verify: nothing anywhere, including the uncompressed raw bytes. ---
    check = fitz.open(OUT)
    text = "".join(pg.get_text() for pg in check)
    raw = open(OUT, "rb").read()
    ok = PHONE not in text and PHONE.encode() not in raw and b"+971" not in raw

    print("Patched %d structure/outline strings." % patched)
    print("Contact line now: %s" % next(l for l in text.splitlines() if "gmail" in l).strip())
    print("Phone in visible text : %s" % (PHONE in text))
    print("Phone in raw bytes    : %s" % (PHONE.encode() in raw))
    print("Wrote %s (%.1f KB, %d pages)" % (OUT, len(raw) / 1024, check.page_count))
    check.close()

    if not ok:
        sys.exit("FAILED: the phone number is still recoverable from the output.")
    print("\nOK — web CV is clean.")


if __name__ == "__main__":
    main()
