#!/usr/bin/env python3
"""Generate the market coverage map in site/index.html.

The map is plain inline SVG with no runtime dependency, in keeping with the
rest of the site. Geometry comes from Natural Earth 110m admin-0 countries,
which is public domain:

    https://github.com/nvkelso/natural-earth-vector  (geojson/ne_110m_admin_0_countries.geojson)

India is drawn from Natural Earth's India point-of-view edition instead, so
its boundary matches how India officially depicts itself — Jammu and Kashmir
entire, including Pakistan-administered Kashmir and Aksai Chin. Natural Earth
only publishes point-of-view editions at 10m, so that one file is bigger; only
India's polygon is read from it, and it is simplified to the same tolerance as
everything else so the linework matches.

    ne_110m_admin_0_countries.geojson      base map
    ne_10m_admin_0_countries_ind.geojson   India, India's point of view

Download both next to this script and run:

    python3 scripts/make-market-map.py ne110.geojson ne10_ind.geojson

It prints the <svg> block to stdout. Paste it into the MARKETS section of
site/index.html, inside <div class="map__scroll">.

To change which markets are painted, edit REGIONS below and re-run. The map
carries no visible labels, so also update the <title> text — it is the only
place the markets are named, and screen readers read it in place of the
figure.
"""

import json
import math
import sys

# ---------------------------------------------------------------- projection

# Equirectangular. Straight meridians and parallels are the point: they give
# the map the same coordinate-grid language as the career chart. Antarctica is
# dropped and the north is clipped at 78N, which is the usual framing for a
# thematic world map and keeps the block a readable banner shape.
LON_W, LON_E = -180.0, 180.0
LAT_S, LAT_N = -56.0, 78.0

WIDTH = 1000.0
SCALE = WIDTH / (LON_E - LON_W)
HEIGHT = round((LAT_N - LAT_S) * SCALE, 1)


def project(lon, lat):
    return (lon - LON_W) * SCALE, (LAT_N - lat) * SCALE


# ------------------------------------------------------------------- regions

# Markets Aparna has worked in. Order controls only the order of the emitted
# <path> elements; the legend order lives in index.html.
NORTH_AFRICA = ["EGY", "LBY", "TUN", "DZA", "MAR", "ESH"]
MIDDLE_EAST = ["SAU", "ARE", "QAT", "KWT", "BHR", "OMN", "YEM",
               "JOR", "LBN", "SYR", "IRQ"]

REGIONS = [
    ("na",     ["USA", "CAN"]),
    ("mexico", ["MEX"]),
    ("argentina", ["ARG"]),
    ("uki",    ["GBR", "IRL"]),
    ("dach",   ["DEU", "AUT", "CHE"]),
    ("spgi",   ["ESP", "PRT", "GRC", "ITA"]),
    ("poland", ["POL"]),
    ("mea",    MIDDLE_EAST + NORTH_AFRICA),
    ("india",  ["IND"]),
    ("lanka",  ["LKA"]),
]

DROP = {"ATA"}  # Antarctica — outside the frame anyway

# Simplification tolerance in degrees. At this scale 1 degree is ~2.8px, so
# 0.3 keeps coastlines honest at the size the map actually renders.
TOL_REGION, TOL_LAND = 0.3, 0.45
# Smallest ring worth drawing, in square degrees. Painted markets get a much
# lower bar so small Gulf states survive; background land does not need them.
MIN_AREA_REGION, MIN_AREA_LAND = 0.06, 3.0


# ---------------------------------------------------------------- simplifying

def simplify(points, tol):
    """Douglas-Peucker. Pure stdlib, so the site keeps its no-dependency rule."""
    if len(points) < 3:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        lo, hi = stack.pop()
        if hi <= lo + 1:
            continue
        ax, ay = points[lo]
        bx, by = points[hi]
        dx, dy = bx - ax, by - ay
        span = math.hypot(dx, dy)
        far, fard = -1, tol
        for i in range(lo + 1, hi):
            px, py = points[i]
            if span == 0:
                d = math.hypot(px - ax, py - ay)
            else:
                d = abs(dy * px - dx * py + bx * ay - by * ax) / span
            if d > fard:
                far, fard = i, d
        if far != -1:
            keep[far] = True
            stack.append((lo, far))
            stack.append((far, hi))
    return [p for p, k in zip(points, keep) if k]


def ring_area(points):
    """Unsigned shoelace area, in square degrees."""
    a = 0.0
    for i in range(len(points)):
        x0, y0 = points[i]
        x1, y1 = points[(i + 1) % len(points)]
        a += x0 * y1 - x1 * y0
    return abs(a) / 2.0


def rings_of(geom):
    if geom["type"] == "Polygon":
        return list(geom["coordinates"])
    if geom["type"] == "MultiPolygon":
        return [ring for poly in geom["coordinates"] for ring in poly]
    return []


def path_for(geom, tol, min_area):
    """Outer rings only — holes are invisible at this scale and cost bytes."""
    out = []
    for ring in rings_of(geom):
        pts = [(lon, lat) for lon, lat in ring
               if -180.0 <= lon <= 180.0]
        if len(pts) < 4 or ring_area(pts) < min_area:
            continue
        pts = simplify(pts, tol)
        if len(pts) < 3:
            continue
        # Clip to the frame after projecting, so the north edge cuts cleanly.
        proj = []
        for lon, lat in pts:
            x, y = project(lon, min(max(lat, LAT_S), LAT_N))
            proj.append(f"{round(x, 1):g} {round(y, 1):g}")
        out.append("M" + " ".join(proj) + "Z")
    return "".join(out)


# ------------------------------------------------------------------- emitting

def load(src):
    by_iso = {}
    for f in json.load(open(src))["features"]:
        p = f["properties"]
        iso = p.get("ISO_A3")
        # Natural Earth leaves ISO_A3 as "-99" for a few entries; fall back to
        # the sovereignty code so France and Norway are not silently dropped.
        if not iso or iso == "-99":
            iso = p.get("SOV_A3") or p.get("ADM0_A3")
        by_iso[iso] = f["geometry"]
    return by_iso


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "ne110.geojson"
    pov = sys.argv[2] if len(sys.argv) > 2 else "ne10_ind.geojson"

    by_iso = load(src)

    # India's own depiction of its northern boundary. Drawn after the
    # background land, so where it reaches past a neighbour's 110m polygon it
    # simply paints over it rather than leaving a seam.
    try:
        by_iso["IND"] = load(pov)["IND"]
    except (IOError, OSError, KeyError):
        print("<!-- warning: no India point-of-view file; using the base map, "
              "which draws the line of control -->", file=sys.stderr)

    assigned, groups = set(), []
    for key, isos in REGIONS:
        members = [i for i in isos if i in by_iso]
        missing = [i for i in isos if i not in by_iso]
        if missing:
            print(f"<!-- warning: no geometry for {' '.join(missing)} -->",
                  file=sys.stderr)
        assigned.update(members)
        d = "".join(path_for(by_iso[i], TOL_REGION, MIN_AREA_REGION)
                    for i in members)
        groups.append((key, d))

    land = "".join(
        path_for(g, TOL_LAND, MIN_AREA_LAND)
        for iso, g in sorted(by_iso.items())
        if iso not in assigned and iso not in DROP
    )

    print(f'<svg viewBox="0 0 {WIDTH:g} {HEIGHT:g}" role="img" '
          f'aria-labelledby="map-title">')
    # The map carries no visible labels, so this title is the only thing that
    # names the markets. It is the accessible equivalent of the whole figure.
    print('  <title id="map-title">World map with ten markets marked: North '
          'America, Mexico, Argentina, the UK and Ireland, Germany Austria '
          'and Switzerland, Spain Portugal Greece and Italy, Poland, the '
          'Middle East and North Africa, India and Sri Lanka.</title>')

    print('  <g class="wm-grat" aria-hidden="true">')
    lon = LON_W
    while lon <= LON_E:
        x = round(project(lon, 0)[0], 1)
        print(f'    <line x1="{x:g}" y1="0" x2="{x:g}" y2="{HEIGHT:g}"/>')
        lon += 30
    lat = LAT_S
    while lat <= LAT_N:
        y = round(project(0, lat)[1], 1)
        print(f'    <line x1="0" y1="{y:g}" x2="{WIDTH:g}" y2="{y:g}"/>')
        lat += 30
    print('  </g>')

    print(f'  <path class="wm-land" d="{land}"/>')
    for key, d in groups:
        print(f'  <path class="wm-mk" data-market="{key}" d="{d}"/>')
    print('</svg>')


if __name__ == "__main__":
    main()
