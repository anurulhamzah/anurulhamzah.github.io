"""Generate the inline SVG charts on the thesis page from the numbers in the paper.

Usage (from the repository root):
    python tools/build_charts.py

Replaces whatever sits between <!-- chart:NAME --> and <!-- /chart:NAME --> (or a bare
<!-- chart:NAME --> marker) in projects/tree-diameter-estimation/index.html. Colours come
from CSS variables via the classes in assets/css/style.css, so charts follow light/dark mode.
All values are copied from the paper: Table 3 (depth ablation) and Table 6 (distance bins).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "projects" / "tree-diameter-estimation" / "index.html"
PAGE_BAYES = ROOT / "projects" / "bayesian-network-crf" / "index.html"

# Table 3: AP50 at 75,000 iterations, both arms trained from scratch: (label, RGB, RGB-D, delta, final?)
DEPTH = [
    ("Mask R-CNN R50 (ref.)", 6.54, 6.86, 0.32, False),
    ("MaskDINO ResNet-50", 32.00, 47.94, 15.93, False),
    ("MaskDINO Swin-T", 33.91, 50.84, 16.93, False),
    ("MaskDINO Swin-B", 38.95, 48.63, 9.68, False),
    ("MaskDINO Swin-L", 40.75, 50.82, 10.07, False),
    ("MaskDINO FocalNet-B", 43.75, 58.10, 14.35, False),
    ("MaskDINO FocalNet-L", 44.25, 57.18, 12.92, True),
]

# Table 6: bins, recall %, species correct %, mask IoU %
DIST = [
    ("0-5 m", 82.4, 99.6, 79.1),
    ("5-10 m", 79.3, 99.7, 75.8),
    ("10-15 m", 70.4, 99.8, 69.8),
    ("15-20 m", 59.5, 100.0, 65.4),
    ("20-30 m", 46.7, 99.6, 63.4),
    (">30 m", 34.5, 98.9, 61.0),
]


def depth_chart():
    w, left, right, top = 720, 190, 120, 44
    row_h = 36
    n = len(DEPTH)
    h = top + n * row_h + 50
    plot_w = w - left - right
    xmax = 60.0

    def x(v):
        return left + plot_w * v / xmax

    out = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-labelledby="t-depth d-depth">',
           '<title id="t-depth">Effect of adding a depth channel on AP50</title>',
           '<desc id="d-depth">Dumbbell chart. For each backbone, AP50 without depth and with depth, both trained from scratch. Depth adds between 9.68 and 16.93 points for the six MaskDINO backbones and 0.32 points for the Mask R-CNN reference.</desc>']
    # grid
    for t in range(0, 61, 10):
        out.append(f'<line class="s-rule" x1="{x(t):.1f}" x2="{x(t):.1f}" y1="{top - 8}" y2="{h - 40}" stroke-width="1"/>')
        out.append(f'<text x="{x(t):.1f}" y="{h - 24}" text-anchor="middle">{t}</text>')
    out.append(f'<text x="{left + plot_w / 2:.1f}" y="{h - 4}" text-anchor="middle">AP50 (%)</text>')
    # legend
    out.append(f'<circle class="c-canopy" cx="{left}" cy="14" r="5"/><text x="{left + 10}" y="18">without depth (RGB)</text>')
    out.append(f'<circle class="c-tape" cx="{left + 160}" cy="14" r="5"/><text x="{left + 170}" y="18">with depth (RGB-D)</text>')
    for i, (label, rgb, rgbd, delta, final) in enumerate(DEPTH):
        cy = top + i * row_h + row_h / 2
        weight = "c-strong" if final else ""
        out.append(f'<text class="{weight}" x="{left - 14}" y="{cy + 4:.1f}" text-anchor="end">{label}</text>')
        out.append(f'<line class="s-ink" x1="{x(rgb):.1f}" x2="{x(rgbd):.1f}" y1="{cy:.1f}" y2="{cy:.1f}" stroke-width="2"/>')
        out.append(f'<circle class="c-canopy" cx="{x(rgb):.1f}" cy="{cy:.1f}" r="5.5"/>')
        out.append(f'<circle class="c-tape" cx="{x(rgbd):.1f}" cy="{cy:.1f}" r="5.5"/>')
        out.append(f'<text x="{x(rgb) - 10:.1f}" y="{cy + 4:.1f}" text-anchor="end">{rgb:.2f}</text>')
        out.append(f'<text class="c-strong" x="{x(rgbd) + 10:.1f}" y="{cy + 4:.1f}">{rgbd:.2f} (+{delta:.2f})</text>')
    out.append("</svg>")
    return "\n".join(out)


def distance_chart():
    w, h = 720, 330
    left, right, top, bottom = 52, 150, 24, 44
    pw, ph = w - left - right, h - top - bottom
    n = len(DIST)

    def x(i):
        return left + pw * i / (n - 1)

    def y(v):
        return top + ph * (1 - v / 100.0)

    out = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-labelledby="t-dist d-dist">',
           '<title id="t-dist">Detection recall, mask IoU and species accuracy by camera distance</title>',
           '<desc id="d-dist">Line chart over six distance bins. Species accuracy stays between 98.9 and 100 percent. Mask IoU falls from 79.1 to 61.0 percent. Detection recall falls from 82.4 percent within 5 metres to 34.5 percent beyond 30 metres.</desc>']
    for v in (0, 25, 50, 75, 100):
        out.append(f'<line class="s-rule" x1="{left}" x2="{left + pw}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke-width="1"/>')
        out.append(f'<text x="{left - 10}" y="{y(v) + 4:.1f}" text-anchor="end">{v}</text>')
    for i, (label, *_rest) in enumerate(DIST):
        out.append(f'<text x="{x(i):.1f}" y="{h - 18}" text-anchor="middle">{label}</text>')
    def series(idx, cls, dash, name, bold=False):
        pts = [(x(i), y(row[idx])) for i, row in enumerate(DIST)]
        d = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<polyline class="{cls}" points="{d}" stroke-width="{3 if bold else 2}"{dash_attr}/>')
        fill = "c-tape" if cls == "s-tape" else ("c-canopy" if cls == "s-canopy" else "c-ink")
        for (px, py) in pts:
            out.append(f'<circle class="{fill}" cx="{px:.1f}" cy="{py:.1f}" r="{4.5 if bold else 3.5}"/>')
        last = DIST[-1][idx]
        lx, ly = pts[-1]
        out.append(f'<text class="{"c-strong" if bold else ""}" x="{lx + 12:.1f}" y="{ly + 4:.1f}">{name} {last:.1f}</text>')

    series(2, "s-canopy", None, "Species")
    series(3, "s-ink", "6 4", "Mask IoU")
    series(1, "s-tape", None, "Recall", bold=True)
    out.append("</svg>")
    return "\n".join(out)



# Bayesian/CRF project: weighted F1 of the CRF on train, validation and test (second run in the report)
CRF = [("Train", 0.9715), ("Validation", 0.9698), ("Test", 0.9650)]


def crf_chart():
    w, left, right, top = 480, 110, 40, 30
    row_h = 44
    h = top + len(CRF) * row_h + 56
    lo, hi = 0.950, 0.980
    pw = w - left - right

    def x(v):
        return left + pw * (v - lo) / (hi - lo)

    out = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-labelledby="t-crf d-crf">',
           '<title id="t-crf">Weighted F1 of the CRF by data split</title>',
           '<desc id="d-crf">Dot plot of weighted F1: 0.9715 on training, 0.9698 on validation and 0.9650 on test data. The axis runs from 0.95 to 0.98.</desc>']
    for t in (0.95, 0.96, 0.97, 0.98):
        out.append(f'<line class="s-rule" x1="{x(t):.1f}" x2="{x(t):.1f}" y1="{top - 8}" y2="{h - 40}" stroke-width="1"/>')
        out.append(f'<text x="{x(t):.1f}" y="{h - 24}" text-anchor="middle">{t:.2f}</text>')
    out.append(f'<text x="{left + pw / 2:.1f}" y="{h - 6}" text-anchor="middle">weighted F1 (axis starts at 0.95)</text>')
    for i, (label, v) in enumerate(CRF):
        cy = top + i * row_h + row_h / 2
        out.append(f'<text x="{left - 14}" y="{cy + 4:.1f}" text-anchor="end">{label}</text>')
        out.append(f'<line class="s-ink" x1="{x(lo):.1f}" x2="{x(v):.1f}" y1="{cy:.1f}" y2="{cy:.1f}" stroke-width="1.5"/>')
        cls = "c-tape" if label == "Test" else "c-canopy"
        out.append(f'<circle class="{cls}" cx="{x(v):.1f}" cy="{cy:.1f}" r="6"/>')
        out.append(f'<text class="c-strong" x="{x(v) + 12:.1f}" y="{cy + 4:.1f}">{v:.4f}</text>')
    out.append("</svg>")
    return "\n".join(out)
CHARTS = {"depth": (PAGE, depth_chart), "distance": (PAGE, distance_chart), "crf": (PAGE_BAYES, crf_chart)}


def main():
    pages = {}
    for name, (page, fn) in CHARTS.items():
        html = pages.get(page) or page.read_text(encoding="utf-8")
        pattern = re.compile(r"<!-- chart:%s -->(?:.*?<!-- /chart:%s -->)?" % (name, name), re.S)
        if not pattern.search(html):
            sys.exit("marker for chart '%s' not found in %s" % (name, page.name))
        block = "<!-- chart:%s -->\n%s\n<!-- /chart:%s -->" % (name, fn(), name)
        pages[page] = pattern.sub(lambda m: block, html, count=1)
    for page, html in pages.items():
        page.write_text(html, encoding="utf-8")
        print("charts written to", page.parent.name)


if __name__ == "__main__":
    main()