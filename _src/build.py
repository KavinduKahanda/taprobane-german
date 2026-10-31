"""Builds the static site: wraps each _src/pages/*.html fragment in the shared
header/footer. Run:  python3 _src/build.py   (from the repo root)

Fragment format: first lines are front matter until a line '---':
  title: ...
  description: ...
  image: cover-a1.jpg          (optional, for social previews)
  nav: home|books|pflege|level|bonus
  jsonld: <one-line JSON>      (optional)
Then the page body (sections)."""
import pathlib, re, html

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://kavindukahanda.github.io/taprobane-german/"
EMAIL = "kavindukahanda@outlook.com"

NAV = [("home", "./", "Home"), ("books", "./#zero", "German from Zero"),
       ("pflege", "pflege.html", "German for Nurses"), ("level", "level-test.html", "Level test"),
       ("bonus", "bonus.html", "Free resources")]

STORES = [("com", "Amazon.com"), ("de", "Amazon.de"), ("co.uk", "Amazon.co.uk"), ("in", "Amazon.in"),
          ("ca", "Amazon.ca"), ("com.au", "Amazon.com.au"), ("fr", "Amazon.fr"), ("it", "Amazon.it"),
          ("es", "Amazon.es"), ("nl", "Amazon.nl")]


def header(active):
    links = "".join(
        f'<a href="{h}"{" aria-current=page" if k == active else ""}>{t}</a>' for k, h, t in NAV)
    opts = "".join(f'<option value="{v}">{t}</option>' for v, t in STORES)
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="wrap">
<a class="brand" href="./"><span class="brand-mark">T</span><span><b>Taprobane German</b><small>Self-study German</small></span></a>
<button class="menu-btn" aria-expanded="false" aria-label="Menu">☰</button>
<nav class="nav">{links}<a class="cta" href="./#books">All books</a>
<label class="store">Store <select aria-label="Choose your Amazon store">{opts}</select></label></nav>
</div></header>'''


FOOTER = f'''<footer class="site-footer"><div class="wrap"><div class="cols">
<div><a class="brand" href="./" style="margin-bottom:14px"><span class="brand-mark">T</span><span><b>Taprobane German</b><small>by Taprobane Holdings</small></span></a><p>Clear, structured self-study German for English speakers — from your first word to B2, and the German you need on the ward.</p>
<p>Questions or corrections? <a style="display:inline" href="mailto:{EMAIL}">{EMAIL}</a></p></div>
<div><h4>German from Zero</h4><a href="a1.html">A1 Beginner</a><a href="a2.html">A2 Elementary</a><a href="b1.html">B1 Intermediate</a><a href="b2.html">B2 Upper intermediate</a></div>
<div><h4>German for Nurses</h4><a href="pflege.html#b1">Band 1 · B1 Pflege</a><a href="pflege.html#b2">Band 2 · B2 Pflege</a><a href="pflege.html#b3">Band 3 · Exam Trainer</a></div>
<div><h4>Help</h4><a href="level-test.html">Find your level</a><a href="bonus.html">Free resources</a><a href="./#faq">FAQ</a><a href="legal.html">Legal &amp; privacy</a></div>
</div><div class="legal">© <span id="year">2026</span> Taprobane Holdings. Independent publisher; not affiliated with telc gGmbH, the Goethe-Institut, ÖSD or any exam provider. Language learning only — no medical, legal or immigration advice. Amazon and Kindle are trademarks of Amazon.com, Inc.</div>
</div></footer>
<script src="assets/site.js" defer></script>'''


def page(name, meta, body):
    title = meta["title"]; desc = meta["description"]
    url = BASE + ("" if name == "index" else name + ".html")
    img = BASE + meta.get("image", "og-home.jpg")
    robots = '<meta name="robots" content="noindex">' if meta.get("noindex") else ""
    ld = f'<script type="application/ld+json">{meta["jsonld"]}</script>' if meta.get("jsonld") else ""
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}">{robots}
<link rel="canonical" href="{url}"><meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website"><meta property="og:url" content="{url}"><meta property="og:image" content="{img}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:site_name" content="Taprobane German"><meta name="twitter:image" content="{img}"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='46' fill='%230d2440' stroke='%23c9963a' stroke-width='6'/%3E%3Ctext x='50' y='66' font-size='50' text-anchor='middle' fill='%23e8c47f' font-family='Georgia'%3ET%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Lora:ital,wght@0,600;0,700;1,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">{ld}</head><body>
{header(meta.get("nav", ""))}
<main id="main">{body}</main>
{FOOTER}</body></html>
'''


def main():
    for f in sorted((ROOT / "_src" / "pages").glob("*.html")):
        txt = f.read_text(encoding="utf-8")
        fm, body = txt.split("\n---\n", 1)
        meta = {}
        for line in fm.strip().splitlines():
            k, v = line.split(":", 1); meta[k.strip()] = v.strip()
        meta["noindex"] = meta.get("noindex") == "yes"
        (ROOT / f"{f.stem}.html").write_text(page(f.stem, meta, body), encoding="utf-8")
        print("built", f.stem + ".html")


if __name__ == "__main__":
    main()
