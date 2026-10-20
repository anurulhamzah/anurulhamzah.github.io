# anurulhamzah.github.io

Personal portfolio of Akhmad Fauzi Nurulhamzah: applied data science, machine learning and computer vision, with a background in forestry operations and internal audit.

Plain HTML, CSS and a small amount of vanilla JavaScript. No framework, no build step for the site itself, no trackers, no paid services. Fonts (Archivo, JetBrains Mono; SIL Open Font License) are self-hosted.

## Preview locally

From this folder:

```
python -m http.server 8000
```

Open http://localhost:8000. Any static file server works.

## Publish on GitHub Pages (free)

The repository must be public to use Pages on a free account, so its contents are publicly visible.

1. On GitHub, create a **public** repository named exactly `anurulhamzah.github.io` (no README or licence, so it starts empty).
2. From this folder:
   ```
   git remote add origin https://github.com/anurulhamzah/anurulhamzah.github.io.git
   git branch -M main
   git push -u origin main
   ```
3. In the repository go to **Settings, Pages**. Under **Build and deployment** choose **Deploy from a branch**, branch `main`, folder `/ (root)`, and save.
4. After a minute or two the site is at https://anurulhamzah.github.io/. Tick **Enforce HTTPS** once it is offered.
5. Open the URL and check it before sharing the link.

`.nojekyll` is included so GitHub does not run Jekyll over the files. `404.html` is served for unknown URLs.

If you ever host it as a project site (for example `github.io/some-repo/`) instead, the pages already use relative paths, but `404.html` uses `<base href="/">` and the canonical, Open Graph and sitemap URLs would need the new base path.

## Structure

```
index.html                         home page
projects/<slug>/index.html         case studies (clean URLs)
assets/css/style.css               all styles, light and dark via prefers-color-scheme
assets/js/main.js                  optional: highlights the current section in the nav
assets/img, assets/fonts           images (WebP) and self-hosted fonts
tools/                             maintenance scripts (not needed to serve the site)
```

## Maintenance scripts

Python 3 with Pillow and PyMuPDF for the image scripts.

- `python tools/check_site.py` checks internal links, anchors, alt text, headings, ids and meta tags.
- `python tools/build_charts.py` regenerates the two inline SVG charts on the thesis page from the numbers in the paper. Edit the tables at the top of the script to change them.
- `python tools/make_assets.py --paper <pdf> --out assets/img` re-crops the thesis figures from the extended-summary PDF in the public thesis repository.
- `python tools/make_og.py` re-renders the social preview image.

## Content notes

Metrics on the thesis page come from the paper's extended summary in the public repository https://github.com/anurulhamzah/Tree-Segmentation-and-Diameter-Estimation. The manuscript is described as in preparation for submission to *Ecological Informatics*; update that wording only when its status changes.
