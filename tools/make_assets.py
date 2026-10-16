"""Crop figures from the public thesis summary PDF and write optimised WebP files.

Usage:
    python tools/make_assets.py --paper "<path to Multitask Learning for Forestry.pdf>" --out assets/img

The PDF lives in the public repository
https://github.com/anurulhamzah/Tree-Segmentation-and-Diameter-Estimation
Crop rectangles are expressed in pixels of a 110-dpi render of the page (the numbers I measured
by eye), converted to PDF points internally.
"""
import argparse
import io
import os

import fitz  # PyMuPDF
from PIL import Image

PX = 72 / 110  # 110-dpi pixels -> PDF points

# name: (page index, (x0, y0, x1, y1) in 110-dpi pixels)
CROPS = {
    "fig-architecture": (3, (132, 104, 780, 600)),
    "scene-rgb": (6, (113, 23, 451, 213)),
    "scene-truth": (6, (459, 23, 797, 213)),
    "scene-boxes": (6, (113, 237, 451, 429)),
    "scene-prediction": (6, (459, 237, 797, 429)),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    doc = fitz.open(args.paper)
    for name, (page, (x0, y0, x1, y1)) in CROPS.items():
        clip = fitz.Rect(x0 * PX, y0 * PX, x1 * PX, y1 * PX)
        pix = doc[page].get_pixmap(dpi=240, clip=clip)
        img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
        path = os.path.join(args.out, name + ".webp")
        img.save(path, "WEBP", quality=84 if name.startswith("scene") else 92, method=6)
        print(name, img.size, os.path.getsize(path) // 1024, "KB")


if __name__ == "__main__":
    main()
