# How to update the website

Everything about the books and promotions lives in **two files**. Edit them, run the build, push.

| File | What it holds |
|---|---|
| `_src/data/books.json` | every book: ASINs, titles, covers, pages, units, "New" tag |
| `_src/data/promos.json` | every promotion: book, store, start, end |

Build: `python3 _src/build.py` (from the repo root). It regenerates all pages, book cards, buy buttons, JSON-LD, `sitemap.xml`, `llms.txt` and `assets/deals.js`. Never edit the root `.html` files directly – they are overwritten.

## Add a book
1. Put the cover in the repo root (e.g. `cover-pflege-b4.jpg`, 562×900).
2. Copy one entry in `books.json`, change `id`, `position`, titles, ASINs, `cover`, `page`, `blurb`, `description`.
3. Pflege books get their page generated automatically. A new German from Zero level needs a page fragment in `_src/pages/` (copy `b2.html`, change `book:` and the tokens).
4. Optional: `"new_until": "YYYY-MM-DD"` shows a "New" tag until that day, then it disappears by itself.
5. Build, push, resubmit the sitemap in Search Console.

## Change a release date / status
Edit `released` or `status` (`released`, `upcoming`, `preorder`) in `books.json`. Build.

## Update a retailer link
Change the `kindle` or `paperback` ASIN in `books.json`. Every button on every page follows. The visitor's own Amazon store is chosen automatically.

## Launch a promotion
Add one line to `promos.json`:
```
{"book": "pflege-b2", "store": "*", "start": "2026-12-01T08:00Z", "end": "2026-12-08T08:00Z", "kind": "countdown", "text": "<b>Deutsch B2 Pflege</b> at a reduced price"}
```
- Times are UTC. Amazon deals start at 00:00 Pacific = **08:00 UTC** (winter) / 07:00 UTC (summer).
- `store`: `*` = all stores, or `com`, `co.uk`, `de` …
- `kind`: `free` (label "Free on Kindle") or `countdown` (label "Kindle deal").
- The site shows **one** deal at a time: the one ending soonest for the visitor's store. The book's card gets a flag.

## End a campaign
Nothing to do – the bar and flags disappear at `end`. To stop early, set `end` to the new time and build.

## Pages
Home · German from Zero A1–B2 · Pflege series page + one page per Pflege book · Level test · Free resources · About · Legal · 404.
