"""Static checks for the site: broken internal links/assets, anchors, alt text, headings, meta.

Usage (from the repository root):  python tools/check_site.py
Exits with status 1 if any problem is found. External URLs are listed, not fetched.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urldefrag, urlparse

ROOT = Path(__file__).resolve().parent.parent
problems = []
externals = {}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.refs, self.imgs, self.headings = [], [], [], []
        self.title, self.meta, self.lang = "", {}, None
        self._in_title = False
        self._h = None
        self.stack = []
        self.void = {"meta", "link", "img", "br", "hr", "input", "base", "source", "col"}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag not in self.void:
            self.stack.append(tag)
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "title" and not self.title and "svg" not in self.stack:
            self._in_title = True
        if tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.meta[key] = a.get("content", "")
        if tag in ("a", "link") and a.get("href"):
            self.refs.append(("href", a["href"]))
        if tag in ("img", "script", "source") and a.get("src"):
            self.refs.append(("src", a["src"]))
        if tag == "img":
            self.imgs.append(a)
        if re.fullmatch(r"h[1-6]", tag):
            self._h = [int(tag[1]), ""]

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if self._h and tag == "h%d" % self._h[0]:
            self.headings.append(tuple(self._h))
            self._h = None
        if tag not in self.void:
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._h:
            self._h[1] += data


def check(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    p = Page()
    p.feed(path.read_text(encoding="utf-8"))
    if p.stack:
        problems.append(f"{rel}: unclosed tags at end: {p.stack}")
    if not p.lang:
        problems.append(f"{rel}: <html> has no lang")
    t = p.title.strip()
    if not t or len(t) > 70:
        problems.append(f"{rel}: title missing or longer than 70 chars ({len(t)})")
    d = p.meta.get("description", "")
    if not d or len(d) > 175:
        problems.append(f"{rel}: meta description missing or longer than 175 chars ({len(d)})")
    for k in ("og:title", "og:description", "og:image"):
        if rel != "404.html" and k not in p.meta:
            problems.append(f"{rel}: missing {k}")
    dup = {i for i in p.ids if p.ids.count(i) > 1}
    if dup:
        problems.append(f"{rel}: duplicate ids {sorted(dup)}")
    h1 = [h for h in p.headings if h[0] == 1]
    if len(h1) != 1:
        problems.append(f"{rel}: expected exactly one h1, found {len(h1)}")
    prev = 0
    for level, text in p.headings:
        if prev and level > prev + 1:
            problems.append(f"{rel}: heading jumps from h{prev} to h{level} ('{text.strip()[:40]}')")
        prev = level
    for img in p.imgs:
        if "alt" not in img or not img["alt"].strip():
            problems.append(f"{rel}: <img> without alt text: {img.get('src')}")
        if not img.get("width") or not img.get("height"):
            problems.append(f"{rel}: <img> without width/height: {img.get('src')}")
    for kind, ref in p.refs:
        if ref.startswith(("mailto:", "tel:", "javascript:")):
            continue
        if re.match(r"https?://", ref):
            externals.setdefault(ref, []).append(rel)
            continue
        if ref.startswith("/"):
            problems.append(f"{rel}: root-absolute path breaks under a project base path: {ref}")
            continue
        target, frag = urldefrag(ref)
        target = unquote(urlparse(target).path)
        dest = path if not target else (path.parent / target)
        if dest.is_dir():
            dest = dest / "index.html"
        if not dest.exists():
            problems.append(f"{rel}: broken {kind} -> {ref}")
            continue
        if frag and dest.suffix == ".html":
            q = Page()
            q.feed(dest.read_text(encoding="utf-8"))
            if frag not in q.ids:
                problems.append(f"{rel}: anchor #{frag} not found in {dest.relative_to(ROOT).as_posix()}")


pages = [p for p in ROOT.rglob("*.html") if ".git" not in p.parts]
for page in sorted(pages):
    if page.name == "404.html":
        continue  # uses <base href="/"> by design; checked by eye
    check(page)

# unused / missing assets
used = " ".join(p.read_text(encoding="utf-8") for p in pages) + (ROOT / "assets/css/style.css").read_text(encoding="utf-8")
for f in (ROOT / "assets").rglob("*"):
    if f.is_file() and f.name not in used and f.name not in ("og-image.png",):
        problems.append(f"assets: {f.relative_to(ROOT).as_posix()} is not referenced anywhere")

print(f"{len(pages)} pages checked, {len(externals)} distinct external URLs")
for u in sorted(externals):
    print("  ext:", u)
if problems:
    print("\nPROBLEMS")
    for x in problems:
        print(" -", x)
    sys.exit(1)
print("\nNo problems found.")
