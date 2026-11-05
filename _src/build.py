"""Builds the static site.  Run from the repo root:   python3 _src/build.py

Single source of truth
  _src/data/books.json   every book (ASINs, titles, covers, pages, units ...)
  _src/data/promos.json  every promotion (start/end in UTC, store, book)
Everything else is generated from these: book cards, buy buttons, series paths,
Pflege book pages, JSON-LD, sitemap.xml, llms.txt and assets/deals.js.

Page fragments: _src/pages/*.html. Front matter until a line '---':
  title / description / image / nav (books|pflege|level|bonus|about) / noindex: yes
  book: a1          -> Book JSON-LD for that book
  ld: home|pflege   -> generated graph for home / Pflege series page
  jsonld: {...}     -> any other hand-written JSON-LD
Tokens you can put in a page body:
  <!--@cards zero-->  <!--@cards pflege-->   book cards of a series
  <!--@buy a1-->                              Kindle + paperback buttons
  <!--@path a1-->                             reading-order strip for the book's series
  <!--@include name-->                        _src/partials/name.html
"""
import datetime, html, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "_src"
BASE = "https://kavindukahanda.github.io/taprobane-german/"
# Inquiry form: paste the free form service's endpoint URL here (e.g. Formspree / Web3Forms).
# While it is empty the contact page shows only the Instagram panel, no broken form.
FORM_ENDPOINT = "https://api.web3forms.com/submit"
FORM_FIELDS = {"access_key": "9dec6495-6247-4654-ae41-2cefd22fd3c8", "from_name": "German from Zero website"}
INSTAGRAM = "https://www.instagram.com/deutschvonzero/"
SITE = "German from Zero"
PUB = "Taprobane Holdings"
TODAY = datetime.date.today().isoformat()

DATA = json.loads((SRC / "data/books.json").read_text(encoding="utf-8"))
SERIES, BOOKS = DATA["series"], DATA["books"]
BY_ID = {b["id"]: b for b in BOOKS}
PROMOS = json.loads((SRC / "data/promos.json").read_text(encoding="utf-8"))["promos"]
esc = html.escape

NAV = [("books", "./#books", "Books"), ("pflege", "pflege.html", "For nurses"),
       ("level", "level-test.html", "Level test"), ("bonus", "bonus.html", "Free resources"),
       ("about", "about.html", "About"), ("contact", "contact.html", "Contact")]
STORES = [("com", "Amazon.com"), ("de", "Amazon.de"), ("co.uk", "Amazon.co.uk"), ("in", "Amazon.in"),
          ("ca", "Amazon.ca"), ("com.au", "Amazon.com.au"), ("fr", "Amazon.fr"), ("it", "Amazon.it"),
          ("es", "Amazon.es"), ("nl", "Amazon.nl")]


# ---------- brand ----------
def logo(cls="logo"):
    """The '0' + waving German flag mark (same idea as the Instagram logo)."""
    return (f'<svg class="{cls}" viewBox="0 0 72 48" aria-hidden="true" focusable="false">'
            '<ellipse cx="19" cy="24" rx="11.5" ry="16.5" fill="none" stroke="currentColor" stroke-width="6.5"/>'
            '<path d="M33 11c9-5 17 4 35-1v8c-18 5-26-4-35 1z" fill="#000"/>'
            '<path d="M33 20c9-5 17 4 35-1v8c-18 5-26-4-35 1z" fill="#DD0000"/>'
            '<path d="M33 29c9-5 17 4 35-1v8c-18 5-26-4-35 1z" fill="#FFCE00"/></svg>')


def brand(small="Self-study German"):
    return (f'<a class="brand" href="./" aria-label="{SITE} — home"><span class="brand-mark">{logo()}</span>'
            f'<span><b>{SITE}</b><small>{small}</small></span></a>')


FAVICON = ("data:image/svg+xml," + re.sub(r"[<>#\"]", lambda m: {"<": "%3C", ">": "%3E", "#": "%23", '"': "'"}[m.group()],
           '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#fbf8f2"/>'
           '<ellipse cx="20" cy="32" rx="10" ry="15" fill="none" stroke="#0d2440" stroke-width="6"/>'
           '<path d="M33 20c8-4 14 3 26-1v7c-12 4-18-3-26 1z" fill="#000"/><path d="M33 28c8-4 14 3 26-1v7c-12 4-18-3-26 1z" fill="#DD0000"/>'
           '<path d="M33 36c8-4 14 3 26-1v7c-12 4-18-3-26 1z" fill="#FFCE00"/></svg>'))


# ---------- book components ----------
def amz(asin):
    return f"https://www.amazon.com/dp/{asin}"


def new_tag(b):
    u = b.get("new_until")
    return f' <span class="new-tag" data-until="{u}">New</span>' if u and u >= TODAY else ""


def pill(b):
    label = f'{b["level_name"]} · {b["level"]}' if b["series"] == "pflege" else f'{b["level"]} · {b["level_name"]}'
    return f'<span class="pill {b["colour"] if b["colour"] != "gold" else ""}">{esc(label)}{new_tag(b)}</span>'


def card(b):
    c = b["colour"] if b["colour"] != "gold" else ""
    head = f'Book {b["position"]}: {b["short"]}' if b["series"] == "zero" else b["short"]
    return (f'<div class="card bookcard" data-book="{b["id"]}"><a class="cov" href="{b["page"]}">'
            f'<img src="{b["cover"]}" alt="{esc(b["title"])} — cover" loading="lazy" width="562" height="900"></a>'
            f'<div class="body">{pill(b)}<h3><a href="{b["page"]}">{esc(head)}</a></h3><p>{esc(b["blurb"])}</p>'
            f'<div class="cardbtns"><a class="btn sm {c}" data-asin="{b["kindle"]}" data-fmt="kindle" href="{amz(b["kindle"])}">Kindle</a>'
            f'<a class="btn sm navy" data-asin="{b["paperback"]}" data-fmt="paperback" href="{amz(b["paperback"])}">Paperback</a></div></div></div>')


def cards(series):
    bs = sorted((b for b in BOOKS if b["series"] == series), key=lambda b: b["position"])
    return f'<div class="grid c{len(bs)}">' + "".join(card(b) for b in bs) + "</div>"


def rows(series):
    out = []
    for b in sorted((x for x in BOOKS if x["series"] == series), key=lambda x: x["position"]):
        c = b["colour"] if b["colour"] != "gold" else ""
        meta = " · ".join(x for x in [b["level_name"], "CEFR " + b["level"] if "·" not in b["level"] else b["level"],
                                       f'{b["pages"]} pages' if b.get("pages") else ""] if x)
        out.append(f'<div class="brow" id="{b.get("anchor", b["id"])}" data-book="{b["id"]}"><span class="num" aria-hidden="true">0{b["position"]}</span>'
                   f'<div class="cov"><a href="{b["page"]}"><img src="{b["cover"]}" alt="{esc(b["title"])} — cover" loading="lazy" width="562" height="900"></a></div><div>'
                   f'<span class="pill {c}">{esc(meta)}{new_tag(b)}</span><h3><a href="{b["page"]}">{esc(b["title"])}</a></h3><p>{esc(b["description"])}</p>'
                   f'<a class="btn {c}" data-asin="{b["kindle"]}" data-fmt="kindle" href="{amz(b["kindle"])}">Kindle eBook</a>'
                   f'<a class="btn navy" data-asin="{b["paperback"]}" data-fmt="paperback" href="{amz(b["paperback"])}">Paperback</a>'
                   f'<a class="more" href="{b["page"]}">{"All " + str(len(b["units"])) + " units &amp; details" if b.get("units") else "What’s inside"} →</a></div></div>')
    return "".join(out)


def buy(b):
    k = " " + b["colour"] if b["colour"] in ("teal", "coral") else ""
    note = "Opens your own Amazon store — change it in the menu. The Kindle edition is in Kindle Unlimited."
    return (f'<div class="buybox" data-book="{b["id"]}"><a class="btn{k}" data-asin="{b["kindle"]}" data-fmt="kindle" href="{amz(b["kindle"])}">Kindle eBook</a>'
            f'<a class="btn ghost" data-asin="{b["paperback"]}" data-fmt="paperback" href="{amz(b["paperback"])}">Paperback</a>'
            f'<small>{note}</small></div>')


def path(b):
    bs = sorted((x for x in BOOKS if x["series"] == b["series"]), key=lambda x: x["position"])
    parts = []
    for x in bs:
        here = ' class="here" aria-current="page"' if x is b else ""
        label = f'{x["level"]} {x["level_name"]}' if x["series"] == "zero" else x["short"]
        parts.append(f'<a href="{x["page"]}"{here}><img src="{x["cover"]}" alt="" width="562" height="900">{esc(label)}</a>')
    return '<div class="path">' + '<span class="arr" aria-hidden="true">→</span>'.join(parts) + "</div>"


def chips(b):
    c = [f'CEFR {b["level"]}' if "·" not in b["level"] else b["level"]]
    if b.get("pages"): c.append(f'{b["pages"]} pages')
    if b.get("units"): c.append(f'{len(b["units"])} units')
    if b.get("print"): c.append(b["print"])
    c += ["Paperback & Kindle", "Kindle Unlimited"]
    return '<div class="chips">' + "".join(f"<span>{esc(x)}</span>" for x in c) + "</div>"


# ---------- JSON-LD ----------
def book_ld(b):
    s = SERIES[b["series"]]
    d = {"@type": "Book", "@id": BASE + b["page"] + "#book", "name": b["title"], "url": BASE + b["page"],
         "image": BASE + b["cover"], "author": {"@type": "Organization", "name": PUB},
         "publisher": {"@id": BASE + "#publisher"}, "inLanguage": ["en", "de"],
         "educationalLevel": "CEFR " + b["level"].replace("·", "–"), "learningResourceType": "Self-study course book",
         "audience": {"@type": "EducationalAudience", "educationalRole": "student",
                      "audienceType": "English speakers learning German" if b["series"] == "zero" else "Nurses and caregivers learning German"},
         "isPartOf": {"@id": BASE + ("#series" if b["series"] == "zero" else "pflege.html#series")},
         "position": b["position"], "description": b["description"],
         "workExample": [{"@type": "Book", "bookFormat": "https://schema.org/EBook",
                          "identifier": {"@type": "PropertyValue", "propertyID": "ASIN", "value": b["kindle"]}, "url": amz(b["kindle"])},
                         {"@type": "Book", "bookFormat": "https://schema.org/Paperback",
                          "identifier": {"@type": "PropertyValue", "propertyID": "ASIN", "value": b["paperback"]}, "url": amz(b["paperback"])}],
         "sameAs": [amz(b["kindle"]), amz(b["paperback"])]}
    if b.get("pages"): d["numberOfPages"] = b["pages"]
    if b.get("released"): d["datePublished"] = b["released"]
    return d


def org_ld():
    return {"@type": "Organization", "@id": BASE + "#publisher", "name": PUB, "url": BASE,
            "brand": SITE, "sameAs": [INSTAGRAM]}


def series_ld(key):
    s = SERIES[key]
    sid = BASE + ("#series" if key == "zero" else "pflege.html#series")
    return {"@type": "BookSeries", "@id": sid, "name": s["name"], "url": BASE + ("" if key == "zero" else "pflege.html"),
            "publisher": {"@id": BASE + "#publisher"}, "description": s["description"],
            "hasPart": [{"@id": BASE + b["page"] + "#book"} for b in BOOKS if b["series"] == key]}


def faq_ld(body):
    qa = re.findall(r"<details><summary>(.*?)</summary><p>(.*?)</p></details>", body, re.S)
    strip = lambda t: html.unescape(re.sub(r"<[^>]+>", "", t)).strip()
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": strip(q),
            "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in qa]} if qa else None


def jsonld(meta, body):
    g = None
    if meta.get("book"):
        g = [org_ld(), book_ld(BY_ID[meta["book"]])]
    elif meta.get("ld") == "home":
        g = [org_ld(), series_ld("zero"), series_ld("pflege")] + [book_ld(b) for b in BOOKS]
    elif meta.get("ld") == "pflege":
        g = [org_ld(), series_ld("pflege")] + [book_ld(b) for b in BOOKS if b["series"] == "pflege"]
    if g is not None:
        f = faq_ld(body)
        if f: g.append(f)
        return json.dumps({"@context": "https://schema.org", "@graph": g}, ensure_ascii=False)
    return meta.get("jsonld")


# ---------- shell ----------
def header(active):
    links = "".join(f'<a href="{h}"{" aria-current=page" if k == active else ""}>{t}</a>' for k, h, t in NAV)
    opts = "".join(f'<option value="{v}">{t}</option>' for v, t in STORES)
    return f'''<a class="skip" href="#main">Skip to content</a>
<div class="promo" id="promo" role="region" aria-label="Current offer" hidden></div>
<header class="site-header"><div class="wrap">
{brand()}
<button class="menu-btn" aria-expanded="false" aria-controls="site-nav" aria-label="Menu"><span></span><span></span><span></span></button>
<nav class="nav" id="site-nav" aria-label="Main">{links}
<label class="store"><span>Store</span> <select aria-label="Choose your Amazon store">{opts}</select></label></nav>
</div></header>'''


def footer():
    zero = "".join(f'<a href="{b["page"]}">{b["level"]} {b["level_name"]}</a>' for b in BOOKS if b["series"] == "zero")
    pfl = "".join(f'<a href="{b["page"]}">{b["level_name"]} · {b["short"]}</a>' for b in BOOKS if b["series"] == "pflege")
    return f'''<footer class="site-footer"><div class="wrap"><div class="cols">
<div>{brand("by " + PUB)}<p>Clear, structured self-study German for English speakers — from your first word to B2, and the German you need on the ward.</p>
<p><a class="ig" href="{INSTAGRAM}" target="_blank" rel="noopener">Follow @deutschvonzero on Instagram</a> — a free German tip every few days.</p>
<p>Questions or corrections? <a class="inline" href="contact.html">Get in touch →</a></p></div>
<div><h2 class="fh">German from Zero</h2>{zero}</div>
<div><h2 class="fh">German for Nurses</h2>{pfl}</div>
<div><h2 class="fh">Help</h2><a href="level-test.html">Find your level</a><a href="bonus.html">Free resources</a><a href="./#faq">FAQ</a><a href="about.html">About the publisher</a><a href="contact.html">Contact</a><a href="legal.html">Legal &amp; privacy</a></div>
</div><div class="legal">© <span id="year">2026</span> {PUB}. Independent publisher; not affiliated with telc gGmbH, the Goethe-Institut, ÖSD or any exam provider. Language learning only — no medical, legal or immigration advice. Amazon and Kindle are trademarks of Amazon.com, Inc.</div>
</div></footer>
<script src="assets/deals.js"></script><script src="assets/site.js" defer></script>'''


def inquiry():
    if not FORM_ENDPOINT:
        return ""
    hidden = "".join(f'<input type="hidden" name="{esc(k)}" value="{esc(v)}">' for k, v in FORM_FIELDS.items())
    return f'''<div class="cpanel form-panel"><span class="eyebrow dark">Inquiry</span><h2>Send an inquiry</h2>
<form id="inquiry" action="{esc(FORM_ENDPOINT)}" method="POST" novalidate>{hidden}
<input type="hidden" name="subject" value="German from Zero – website inquiry">
<label>Topic<select name="topic" required><option value="">Choose…</option><option>Question about a book</option><option>I found a mistake</option><option>Which level is right for me?</option><option>Teacher / school / bulk order</option><option>Something else</option></select></label>
<label>Your name <span class="opt">(optional)</span><input name="name" autocomplete="name" maxlength="80"></label>
<label>Your e-mail <span class="opt">(so we can reply)</span><input name="email" type="email" autocomplete="email" required maxlength="120"></label>
<label>Message<textarea name="message" rows="5" required maxlength="3000"></textarea></label>
<input class="hp" type="checkbox" name="botcheck" tabindex="-1" autocomplete="off" aria-hidden="true">
<p class="note">We use your e-mail only to answer this message. See <a href="legal.html">privacy</a>.</p>
<button class="btn navy" type="submit">Send inquiry</button><p class="form-status" role="status" aria-live="polite"></p></form></div>'''


def tokens(body):
    body = body.replace("<!--@inquiry-->", inquiry())
    body = re.sub(r"<!--@include ([\w-]+)-->", lambda m: (SRC / "partials" / f"{m.group(1)}.html").read_text(encoding="utf-8"), body)
    body = re.sub(r"<!--@cards (\w+)-->", lambda m: cards(m.group(1)), body)
    body = re.sub(r"<!--@rows (\w+)-->", lambda m: rows(m.group(1)), body)
    body = re.sub(r"<!--@buy ([\w-]+)-->", lambda m: buy(BY_ID[m.group(1)]), body)
    body = re.sub(r"<!--@path ([\w-]+)-->", lambda m: path(BY_ID[m.group(1)]), body)
    left = re.findall(r"<!--@[^>]*-->", body)
    if left: raise SystemExit(f"Unknown token(s): {left}")
    return body


def page(name, meta, body):
    body = tokens(body)
    title, desc = meta["title"], meta["description"]
    url = BASE + ("" if name == "index" else name + ".html")
    img = BASE + meta.get("image", "og-books.jpg")
    robots = '<meta name="robots" content="noindex">' if meta.get("noindex") else ""
    ld = jsonld(meta, body)
    ld = f'<script type="application/ld+json">{ld}</script>' if ld else ""
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">{robots}<meta name="theme-color" content="#0d2440">
<link rel="canonical" href="{url}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="{"book" if meta.get("book") else "website"}"><meta property="og:url" content="{url}"><meta property="og:image" content="{img}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:site_name" content="{SITE}"><meta name="twitter:image" content="{img}"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Lora:ital,wght@0,600;0,700;1,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">{ld}</head><body>
{header(meta.get("nav", ""))}
<main id="main">{body}</main>
{footer()}</body></html>
'''


# ---------- generated Pflege book pages ----------
def pflege_page(b):
    units = ""
    if b.get("units"):
        units = ('<section class="block alt"><div class="wrap"><div class="head"><span class="eyebrow dark teal-t">Inside the book</span>'
                 f'<h2>{len(b["units"])} units, <em class="teal-t">ward by ward</em></h2></div><ol class="topics">'
                 + "".join(f"<li lang=\"de\">{esc(u)}</li>" for u in b["units"]) + "</ol></div></section>")
    nxt = [x for x in BOOKS if x["series"] == "pflege" and x["position"] == b["position"] + 1]
    band = (f'<div class="band teal" style="margin-top:36px"><div><h2>Next step: {esc(nxt[0]["short"])}</h2><p>{esc(nxt[0]["blurb"])}</p></div>'
            f'<a class="btn" href="{nxt[0]["page"]}">See {esc(nxt[0]["short"])} →</a></div>') if nxt else \
           ('<div class="band teal" style="margin-top:36px"><div><h2>Free ward phrase cards</h2><p>Printable German–English phrases for your first shifts. No sign-up.</p></div>'
            '<a class="btn" href="bonus.html#pflege">Download free</a></div>')
    eyebrow = f'{b["level_name"]} of 3 · German for Nurses &amp; Caregivers'
    body = f'''<section class="hero teal"><div class="wrap bookhero">
<div class="cover3d"><img src="{b["cover"]}" alt="{esc(b["title"])} — cover" width="562" height="900"></div>
<div><span class="eyebrow">{eyebrow}</span><h1>{esc(b["title"])}</h1>
<p class="lead">{esc(b["description"])}</p>{chips(b)}<!--@buy {b["id"]}--></div></div></section>
<section class="block"><div class="wrap two">
<div><span class="eyebrow dark teal-t">Who it's for</span><h2>Is this your book?</h2><p style="font-size:1.08rem">{esc(b["for"])}</p>
<a class="btn line" href="pflege.html#choose">Compare the three books</a></div>
<div><span class="eyebrow dark teal-t">Good to know</span><h2>Learning German, not medicine</h2><p>Language learning only — no doses and no treatment instructions. Always follow your employer’s procedures.</p></div>
</div></section>
{units}
<!--@include pflege-features-->
<section class="block alt"><div class="wrap"><div class="head"><span class="eyebrow dark teal-t">The series</span><h2>Where this book fits</h2></div><!--@path {b["id"]}-->{band}</div></section>'''
    meta = {"title": f'{b["title"]} — Self-Study Book for Nurses & Caregivers',
            "description": f'{b["description"]} Paperback and Kindle.'[:300], "image": "og-pflege.jpg",
            "nav": "pflege", "book": b["id"]}
    return page(b["page"][:-5], meta, body)


# ---------- other generated files ----------
def deals_js():
    out = []
    for p in PROMOS:
        b = BY_ID[p["book"]]
        out.append({"s": p["start"], "e": p["end"], "st": p["store"], "asin": b["kindle"], "book": b["id"],
                    "kind": p["kind"], "t": p["text"], "page": b["page"]})
    return "/* GENERATED by _src/build.py from _src/data/promos.json — do not edit */\nwindow.DEALS=" + json.dumps(out, ensure_ascii=False) + ";\n"


def llms():
    lines = [f"# {SITE}", "", f"> Self-study German books for English speakers by {PUB}: {SERIES['zero']['name']} (A1–B2) and {SERIES['pflege']['name']} (B1 Pflege, B2 Pflege, Exam Trainer).", ""]
    for key in ("zero", "pflege"):
        lines += [f"## {SERIES[key]['name']}", "", f"> {SERIES[key]['description']}", ""]
        for b in BOOKS:
            if b["series"] == key:
                extra = f' {b["pages"]} pages.' if b.get("pages") else ""
                lines.append(f'- [{b["title"]}]({BASE}{b["page"]}): {b["description"]}{extra} Amazon: {amz(b["paperback"])} (paperback), {amz(b["kindle"])} (Kindle)')
        lines.append("")
    extra = SRC / "partials/llms-extra.md"
    return "\n".join(lines) + (extra.read_text(encoding="utf-8") if extra.exists() else "")


def main():
    built = []
    for f in sorted((SRC / "pages").glob("*.html")):
        fm, body = f.read_text(encoding="utf-8").split("\n---\n", 1)
        meta = {}
        for line in fm.strip().splitlines():
            k, v = line.split(":", 1); meta[k.strip()] = v.strip()
        meta["noindex"] = meta.get("noindex") == "yes"
        (ROOT / f"{f.stem}.html").write_text(page(f.stem, meta, body), encoding="utf-8")
        if not meta["noindex"] and f.stem != "404": built.append(f.stem)
    for b in BOOKS:
        if b["series"] == "pflege":
            (ROOT / b["page"]).write_text(pflege_page(b), encoding="utf-8"); built.append(b["page"][:-5])
    (ROOT / "assets/deals.js").write_text(deals_js(), encoding="utf-8")
    (ROOT / "llms.txt").write_text(llms(), encoding="utf-8")
    order = ["index", "pflege"] + [b["page"][:-5] for b in BOOKS]
    built = sorted(set(built), key=lambda n: (order.index(n) if n in order else 99, n))
    urls = "".join(f"<url><loc>{BASE}{'' if n == 'index' else n + '.html'}</loc><lastmod>{TODAY}</lastmod></url>" for n in built)
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n', encoding="utf-8")
    print("built:", ", ".join(n + ".html" for n in built), "+ 404.html, sitemap.xml, llms.txt, assets/deals.js")


if __name__ == "__main__":
    main()
