"""Add a content hash to the CSS and JS links in every HTML page (cache busting).

Usage (from the repository root, after editing assets/css or assets/js):
    python tools/stamp_assets.py

A link such as  assets/css/style.css  becomes  assets/css/style.css?v=1a2b3c4d  where the value
is the first 8 hex digits of the SHA-256 of the file. When the file changes, the URL changes, so
browsers and CDNs cannot pair a new page with an old stylesheet or script. tools/check_site.py
fails if any stamp is missing or out of date.
"""
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r'((?:href|src)=")((?:\.\./)*assets/(?:css|js)/[^"?]+)(?:\?v=[0-9a-f]+)?(")')


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:8]


def main():
    changed = 0
    for page in sorted(ROOT.rglob("*.html")):
        if ".git" in page.parts:
            continue
        html = page.read_text(encoding="utf-8")

        def repl(m):
            target = (page.parent / m.group(2)).resolve()
            if page.name == "404.html":  # uses <base href="/">
                target = (ROOT / m.group(2)).resolve()
            if not target.exists():
                return m.group(0)
            return f"{m.group(1)}{m.group(2)}?v={digest(target)}{m.group(3)}"

        new = LINK.sub(repl, html)
        if new != html:
            page.write_text(new, encoding="utf-8")
            changed += 1
    print(f"stamped {changed} page(s)")


if __name__ == "__main__":
    main()
