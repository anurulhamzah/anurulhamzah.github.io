"""Render the 1200x630 social preview image (assets/og-image.png).

Uses fonts installed with Windows (Bahnschrift, Consolas) and the scene crop in assets/img.
Run from the repository root:  python tools/make_og.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
W, H = 1200, 630
PAPER, INK, INK2, RULE, TAPE = "#f1f3ee", "#0f1b15", "#3d4c43", "#bcc7b9", "#bd1b50"


def bahn(size, wght=700, wdth=75):
    f = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", size)
    try:
        f.set_variation_by_axes([wght, wdth])
    except Exception:
        pass
    return f


mono = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 24)
mono_s = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 20)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# ruler on the left edge
d.line([(48, 0), (48, H)], fill=RULE, width=2)
for y in range(0, H, 10):
    L = 22 if (H - y) % 50 == 0 else 10
    d.line([(48 - L, y), (48, y)], fill=INK2, width=1)
flag_y = int(H * 0.35)
d.polygon([(48, flag_y - 16), (140, flag_y - 16), (128, flag_y), (140, flag_y + 16), (48, flag_y + 16)], fill=TAPE)
d.text((58, flag_y - 10), "1.30 m", font=ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 18), fill="white")

# scene plate on the right
scene = Image.open(ROOT / "assets/img/scene-prediction.webp").convert("RGB")
pw = 430
ph = int(scene.height * pw / scene.width)
plate = Image.new("RGB", (pw + 24, ph + 24), "#fbfcf9")
plate.paste(scene.resize((pw, ph), Image.LANCZOS), (12, 12))
px = W - pw - 24 - 56
img.paste(plate, (px, 120))
d.text((px, 120 + ph + 40), "Model output on a synthetic test scene:", font=mono_s, fill=INK2)
d.text((px, 120 + ph + 66), "species and trunk diameter (DBH)", font=mono_s, fill=INK2)

# text
x0 = 190
d.text((x0, 60), "AKHMAD FAUZI NURULHAMZAH", font=mono, fill=TAPE)
y = 120
for line in ("Applied data science,", "grounded in real-world", "industry experience."):
    d.text((x0, y), line, font=bahn(64, 800, 75), fill=INK)
    y += 70
d.text((x0, 430), "Master of Data Science", font=mono_s, fill=INK2)
d.text((x0, 458), "Monash University Indonesia", font=mono_s, fill=INK2)
d.text((x0, 496), "Thesis: 62.29% AP50, 7.62 cm DBH RMSE", font=mono_s, fill=INK2)
d.text((x0, 560), "anurulhamzah.github.io", font=mono, fill=INK)

out = ROOT / "assets/og-image.png"
img.save(out, optimize=True)
print(out, out.stat().st_size // 1024, "KB")

