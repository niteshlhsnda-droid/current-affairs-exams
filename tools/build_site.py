#!/usr/bin/env python3
"""Rebuild the current-affairs-exams static site with a shared theme.

Regenerates: style.css, index.html, archive.html, compare.html,
monthly/*.html, updates/*.html — preserving all factual content, dates,
quiz questions and answers. Only layout/chrome changes.

To roll the nav forward when a new daily/monthly is published, update
LATEST_DAILY / LATEST_MONTHLY below and re-run.
"""
import os, re, sys, html as ihtml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LATEST_DAILY = "2026-09-25"    # slug of newest daily page (updates/<slug>.html)
LATEST_MONTHLY = "2026-08"     # slug of newest monthly digest (monthly/<slug>.html)

MONTH_NAMES = ["January","February","March","April","May","June","July",
               "August","September","October","November","December"]
MON_ABBR = {"January":"Jan","February":"Feb","March":"Mar","April":"Apr","May":"May",
            "June":"Jun","July":"Jul","August":"Aug","September":"Sept","October":"Oct",
            "November":"Nov","December":"Dec"}

def month_label(slug):
    y, m = slug.split("-")
    return f"{MONTH_NAMES[int(m)-1]} {y}"

def date_label(slug):
    y, m, d = slug.split("-")
    return f"{int(d)} {MONTH_NAMES[int(m)-1]} {y}"

# ---------------------------------------------------------------- style.css
STYLE_CSS = """:root{
  --bg:#0d1424; --bg2:#111a30; --card:#182238; --line:#2a3a5f;
  --accent:#f5a524; --accent-ink:#1a1206;
  --text:#e9eef8; --muted:#9fabc7; --link:#7cc7ff;
  --bank:#0ea5e9; --upsc:#8b5cf6; --psu:#10b981; --hot:#f05252;
  --radius:14px; --max:1000px;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--text);
  font-family:"Segoe UI",system-ui,-apple-system,Roboto,"Helvetica Neue",Arial,sans-serif;
  line-height:1.65;font-size:16px}
a{color:var(--link)}
img{max-width:100%}

/* ---- site header + nav ---- */
.site-header{position:sticky;top:0;z-index:50;background:rgba(13,20,36,.97);
  backdrop-filter:blur(6px);border-bottom:1px solid var(--line)}
.site-header .inner{max-width:var(--max);margin:0 auto;padding:.65rem 1.2rem;
  display:flex;align-items:center;gap:1rem;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:.6rem;text-decoration:none;color:var(--text)}
.brand .logo{font-size:1.5rem}
.brand b{font-size:1.04rem;letter-spacing:.2px;display:block;line-height:1.25}
.brand small{display:block;color:var(--muted);font-size:.72rem;font-weight:400}
nav.main{margin-left:auto;display:flex;gap:.15rem;flex-wrap:wrap}
nav.main a{color:var(--muted);text-decoration:none;font-size:.9rem;font-weight:600;
  padding:.45rem .7rem;border-radius:8px}
nav.main a:hover{color:var(--text);background:var(--card)}
nav.main a.active{color:var(--accent)}

/* ---- layout ---- */
.wrap{max-width:var(--max);margin:0 auto;padding:1.4rem 1.2rem 2.5rem}
.wrap.narrow{max-width:860px}
.crumbs{font-size:.85rem;color:var(--muted);margin:0 0 1.1rem}
.crumbs a{color:var(--link);text-decoration:none}
.crumbs a:hover{text-decoration:underline}
.crumbs .sep{margin:0 .45rem;color:var(--line)}
.lede{color:var(--muted);max-width:70ch}

/* ---- hero (homepage) ---- */
.hero{background:linear-gradient(135deg,#2b1b4d 0%,#4a154b 55%,#7c2d12 100%);
  border-bottom:1px solid var(--line)}
.hero .inner{max-width:var(--max);margin:0 auto;padding:2.6rem 1.2rem 2.2rem}
.hero-kicker{display:inline-block;background:rgba(0,0,0,.35);
  border:1px solid rgba(255,255,255,.25);color:#ffe9b8;font-size:.72rem;font-weight:700;
  letter-spacing:1.2px;text-transform:uppercase;border-radius:999px;
  padding:.32rem .95rem;margin-bottom:1rem}
.hero h1{margin:0 0 .6rem;font-size:2.05rem;line-height:1.25;color:#fff}
.hero p.lead{color:#f3e3c3;max-width:62ch;margin:.4rem 0 1.3rem}
.hero .actions{display:flex;gap:.8rem;flex-wrap:wrap}
.btn{display:inline-block;text-decoration:none;font-weight:700;border-radius:10px;
  padding:.7rem 1.35rem;font-size:.95rem}
.btn.primary{background:var(--accent);color:var(--accent-ink)}
.btn.ghost{border:1px solid rgba(255,255,255,.45);color:#fff}
.top5{background:rgba(0,0,0,.28);border:1px solid rgba(255,255,255,.18);
  border-radius:var(--radius);padding:1rem 1.35rem;margin-top:1.5rem;max-width:760px}
.top5 h3{margin:.2rem 0 .6rem;color:#ffe9b8;font-size:.95rem}
.top5 ol{margin:.3rem 0 .4rem;padding-left:1.35rem;color:#fff;font-size:.92rem;line-height:1.8}
.top5 a{color:#ffe9b8;font-weight:600}

/* ---- cards / grids ---- */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:1rem;margin-top:1rem}
.mcard{display:block;text-decoration:none;color:var(--text);background:var(--card);
  border:1px solid var(--line);border-radius:var(--radius);padding:1rem 1.15rem;
  transition:transform .15s,border-color .15s}
.mcard:hover{transform:translateY(-2px);border-color:var(--accent)}
.mcard h3{margin:.1rem 0 .4rem;font-size:1.02rem;color:#fff}
.mcard p{margin:.15rem 0;color:var(--muted);font-size:.86rem;line-height:1.55}
.mcard .meta{display:flex;gap:.45rem;flex-wrap:wrap;margin-top:.55rem}
.mcard .go{color:var(--link);font-size:.85rem;font-weight:600}
.chip{font-size:.72rem;background:var(--bg2);border:1px solid var(--line);
  border-radius:999px;padding:.14rem .6rem;color:var(--muted)}
.chip b{color:var(--accent);font-weight:700}
.linkcard{display:flex;gap:.8rem;align-items:flex-start;background:var(--card);
  border:1px solid var(--line);border-radius:var(--radius);padding:1rem 1.15rem;
  text-decoration:none;color:var(--text);transition:transform .15s,border-color .15s}
.linkcard:hover{transform:translateY(-2px);border-color:var(--accent)}
.linkcard .ic{font-size:1.4rem}
.linkcard b{display:block;color:#fff;font-size:.98rem}
.linkcard span{color:var(--muted);font-size:.84rem}

/* ---- section headings ---- */
h2.section{color:var(--accent);margin:2.4rem 0 1rem;font-size:1.3rem;
  border-bottom:2px solid var(--line);padding-bottom:.45rem}
.wrap>h2.section:first-of-type{margin-top:.4rem}

/* ---- preserved article content ---- */
.content h1{font-size:1.7rem;margin:.2rem 0 1rem;color:#fff;line-height:1.3}
.content h2{color:var(--accent);font-size:1.22rem;margin:2.1rem 0 .8rem;
  border-bottom:2px solid var(--line);padding-bottom:.4rem}
.content h3{color:var(--link);font-size:1.02rem;margin:1.4rem 0 .5rem}
.content hr{border:none;border-top:1px solid var(--line);margin:1.6rem 0}
.content ul,.content ol{line-height:1.85;padding-left:1.4rem}
.content li{margin-bottom:.3rem}
.content b,.content strong{color:#fff}
.content .note{background:var(--bg2);border-left:4px solid var(--accent);
  border-radius:8px;padding:.75rem 1.05rem;margin:1rem 0;font-size:.9rem;color:var(--muted)}

/* ---- pills / tags ---- */
.pill{display:inline-block;font-size:.7rem;font-weight:700;letter-spacing:.4px;color:#fff;
  border-radius:6px;padding:.14rem .5rem;margin:0 .3rem .3rem 0}
.pill.bank{background:var(--bank)} .pill.upsc{background:var(--upsc)}
.pill.psu{background:var(--psu)} .pill.hot{background:var(--hot)}
.tags{display:flex;gap:.5rem;flex-wrap:wrap;margin:1rem 0}
.tag{background:var(--card);border:1px solid var(--line);border-radius:999px;
  padding:.35rem .95rem;font-size:.85rem}
.legend{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:.7rem;margin-top:1rem}
.legend .li{background:var(--card);border:1px solid var(--line);border-radius:10px;
  padding:.7rem .95rem;font-size:.86rem;color:var(--muted)}
.legend .li b{color:var(--text)}

/* ---- tables ---- */
.table-scroll{overflow-x:auto;margin:1.1rem 0;border-radius:12px;border:1px solid var(--line)}
table{width:100%;border-collapse:collapse;font-size:.87rem;background:var(--card)}
th,td{padding:.6rem .7rem;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}
thead th{background:var(--bg2);color:var(--accent);font-size:.78rem;
  text-transform:uppercase;letter-spacing:.4px;white-space:nowrap}
tbody tr:last-child th,tbody tr:last-child td{border-bottom:none}

/* ---- details / quiz answers ---- */
details{background:var(--bg2);border:1px solid var(--line);border-radius:10px;
  padding:.75rem 1.05rem;margin-top:.9rem}
summary{cursor:pointer;font-weight:600;color:var(--link)}

/* ---- archive ---- */
.searchbar{position:relative;margin:1.2rem 0 1.6rem;max-width:560px}
.searchbar input{width:100%;background:var(--card);border:1px solid var(--line);
  border-radius:12px;color:var(--text);font-size:1rem;padding:.8rem 1rem .8rem 2.8rem}
.searchbar input:focus{outline:none;border-color:var(--accent)}
.searchbar .icon{position:absolute;left:1rem;top:50%;transform:translateY(-50%);color:var(--muted)}
#no-results{display:none;text-align:center;color:var(--muted);padding:2rem}
.month-block{margin-bottom:2.4rem}
ul.days{list-style:none;padding:0;margin:.8rem 0 0;display:flex;flex-wrap:wrap;gap:.45rem .95rem}
ul.days li{font-size:.9rem}
ul.days li a{text-decoration:none;font-weight:600}
ul.days li a:hover{text-decoration:underline}
ul.days .cnt{color:var(--muted);font-size:.78rem}
ul.days.big{flex-direction:column;gap:0}
ul.days.big li{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--bank);
  border-radius:10px;padding:.8rem 1.1rem;margin-bottom:.6rem}
.dailies{margin:.8rem 0 0}

/* ---- prev / next ---- */
.pn{display:flex;justify-content:space-between;gap:1rem;margin:2.2rem 0 0;flex-wrap:wrap}
.pn a{display:inline-block;background:var(--card);border:1px solid var(--line);
  border-radius:10px;padding:.6rem 1.05rem;text-decoration:none;font-weight:600;font-size:.9rem}
.pn a:hover{border-color:var(--accent)}
.pn .next{margin-left:auto}
.backline{margin-top:1.4rem;font-size:.92rem}

/* ---- footer ---- */
footer.site{border-top:1px solid var(--line);background:var(--bg2);margin-top:2.5rem}
footer.site .inner{max-width:var(--max);margin:0 auto;padding:1.8rem 1.2rem;
  color:var(--muted);font-size:.85rem;line-height:1.7}
footer.site a{color:var(--link)}

@media(max-width:640px){
  .hero h1{font-size:1.55rem}
  nav.main{margin-left:0}
  .content h1{font-size:1.4rem}
}
"""

# ------------------------------------------------------- shared chrome
def site_header(prefix, active=""):
    def cls(name):
        return ' class="active"' if name == active else ""
    return f"""<header class="site-header"><div class="inner">
<a class="brand" href="{prefix}index.html"><span class="logo">📚</span><span><b>Current Affairs for Exams</b><small>Bank • UPSC • PSU — daily exam-ready digests</small></span></a>
<nav class="main" aria-label="Main navigation">
<a href="{prefix}index.html"{cls("home")}>Home</a><a href="{prefix}archive.html"{cls("archive")}>Archive</a><a href="{prefix}archive.html#today">Latest</a><a href="{prefix}monthly/{LATEST_MONTHLY}.html"{cls("monthly")}>Monthly</a><a href="{prefix}updates/{LATEST_DAILY}.html#quiz">Quiz</a><a href="{prefix}compare.html"{cls("compare")}>Compare</a>
</nav></div></header>"""

def site_footer(prefix):
    return f"""<footer class="site"><div class="inner">
<b>📚 Current Affairs for Exams</b> — original curation &amp; quizzes: <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.<br>
Compiled from public coverage on GKToday, Insights IAS, Drishti IAS, Testbook, AffairsCloud, Vision IAS, ForumIAS, IASbaba, ClearIAS, Adda247, Oliveboard, Jagran Josh, Guidely, StudyIQ, Unacademy &amp; PIB.<br>
<a href="{prefix}index.html">Home</a> · <a href="{prefix}archive.html">Archive</a> · <a href="https://github.com/niteshlhsnda-droid/current-affairs-exams">GitHub</a>
</div></footer>"""

def page_shell(title, prefix, active, crumbs, main_html, description=""):
    desc = description or "Exam-ready daily current affairs for Bank, UPSC and PSU aspirants — rapid-fire one-liners, top stories and quizzes."
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="/current-affairs-exams/auth.js"></script>
<title>{title}</title>
<meta name="description" content="{ihtml.escape(desc, quote=True)}">
<link rel="stylesheet" href="{prefix}style.css">
</head>
<body>
{site_header(prefix, active)}
<main class="wrap">
<nav class="crumbs" aria-label="Breadcrumb">{crumbs}</nav>
{main_html}
</main>
{site_footer(prefix)}
</body>
</html>
"""

def crumbs(prefix, *items):
    # items: list of (label, href|None)
    parts = []
    for label, href in items:
        parts.append(f'<a href="{href}">{label}</a>' if href else f"<span>{label}</span>")
    return '<span class="sep">›</span>'.join(parts)

# ------------------------------------------------------- content extract
def extract_body(path, prefix):
    """Return (title, cleaned inner HTML) preserving all factual content.

    Handles both the legacy inline-style format (<div class="wrap">) and the
    new shared-theme format (<div class="content"> inside <main class="wrap">),
    so the script is idempotent."""
    src = open(path, encoding="utf-8").read()
    m = re.search(r"<title>(.*?)</title>", src, re.S)
    title = m.group(1).strip() if m else "Current Affairs for Exams"
    # new format first
    m = re.search(r'<div class="content">\n(.*)\n</div>\n(?:<div class="pn">|<p class="backline">|</main>)', src, re.S)
    if m:
        body = m.group(1)
    else:
        m = re.search(r'<div class="wrap">(.*)</div>\s*</body>', src, re.S)
        if not m:
            raise ValueError(f"no .wrap in {path}")
        body = m.group(1)
        before = body
        body = re.sub(r'^\s*<a class="back"[^>]*>.*?</a>\s*', "", body)
        body = re.sub(r'\s*<p style="margin-top:2rem"><a class="back"[^>]*>.*?</a></p>\s*$', "", body)
        if body == before:
            print(f"  NOTE: back-link strip matched nothing in {path}")
    # anchor the quiz section for nav links (no-op if already present)
    body = re.sub(r"<h2>([^<]*Quiz[^<]*)</h2>", r'<h2 id="quiz">\1</h2>', body)
    return title, body

# ------------------------------------------------------- archive parse
def parse_archive():
    src = open(os.path.join(ROOT, "archive.html"), encoding="utf-8").read()
    if 'id="q"' in src and "month-block" in src:
        return parse_archive_new(src)
    return parse_archive_legacy(src)

def parse_archive_new(src):
    """Parse the redesigned archive.html (idempotent re-runs)."""
    months = []
    blocks = re.findall(r'<section class="month-block" data-search="([^"]*)">(.*?)</section>', src, re.S)
    for ds, b in blocks:
        dailies = []
        for lm in re.finditer(r'<li(?: id="today")?><a href="updates/([^"]+)">([^<]+)</a> <span class="cnt">· ([^<]*)</span></li>', b):
            dailies.append((lm.group(1).replace(".html", ""), lm.group(2), lm.group(3)))
        m = re.search(r"<h3[^>]*>([^<]+)</h3>", b)
        label = m.group(1).strip() if m else ""
        if 'class="days big"' in b:
            # current-month block (no monthly digest yet); slug from data-search "YYYY MM ..."
            slug = "-".join(ds.split()[:2])
            note_m = re.search(r'<p class="lede">([^<]*)</p>', b)
            months.append({"slug": slug, "label": label or month_label(slug),
                           "note": note_m.group(1) if note_m else "",
                           "dailies": dailies, "current": True})
        else:
            ms = re.search(r'href="monthly/(\d{4}-\d{2})\.html"', b)
            slug = ms.group(1) if ms else ""
            # repair: a September-2026 block left slug-less by an older buggy run
            if not slug and dailies and all(s.startswith("2026-09") for s, _, _ in dailies):
                slug = "2026-09"
            note_m = re.search(r"</h3><p>(.*?)</p>", b, re.S)
            note = re.sub(r"<[^>]+>", "", note_m.group(1)).strip() if note_m else ""
            if slug == "2026-09":
                months.append({"slug": slug, "label": label or "September 2026",
                               "note": note or "Full September monthly digest publishes at month-end.",
                               "dailies": dailies, "current": True})
                continue
            dsum_m = re.search(r"Daily pages — ([^<]*)</summary>", b)
            months.append({"slug": slug, "label": label,
                           "note": note,
                           "dsum": dsum_m.group(1) if dsum_m else "",
                           "dailies": dailies, "current": False})
    months.sort(key=lambda m: 0 if m.get("current") else 1)
    return months

def parse_archive_legacy(src):
    months = []  # dicts: slug, label, note, dailies=[(slug,label,cnt_note)]
    # September 2026 special block
    m = re.search(r"<h3[^>]*>September 2026 — daily updates</h3>\s*<ul class=\"days\">(.*?)</ul>", src, re.S)
    sept_days = []
    sept_note = ""
    if m:
        for lm in re.finditer(r'<li><a href="updates/([^"]+)">([^<]+)</a> <span>([^<]*)</span></li>', m.group(1)):
            sept_days.append((lm.group(1).replace(".html", ""), lm.group(2), lm.group(3).strip(" —")))
        mn = re.search(r"</ul>\s*<p[^>]*>(Full September[^<]*)</p>", src)
        if mn:
            sept_note = mn.group(1)
    months.append({"slug": "2026-09", "label": "September 2026", "note": sept_note,
                   "dailies": sept_days, "current": True})
    # month cards + their dailies details
    pat = re.compile(
        r'<a class="mcard" href="monthly/(\d{4}-\d{2})\.html"><h3>([^<]+)</h3><p>(.*?)</p>.*?</a>'
        r'\s*(?:<details class="dailies"><summary>📅 Daily pages — (.*?)</summary>\s*<ul>(.*?)</ul>\s*</details>)?',
        re.S)
    for m in pat.finditer(src):
        slug, label, note, dsum, dlist = m.groups()
        dailies = []
        if dlist:
            for lm in re.finditer(r'<li><a href="updates/([^"]+)">([^<]+)</a> <span>([^<]*)</span></li>', dlist):
                dailies.append((lm.group(1).replace(".html", ""), lm.group(2), lm.group(3).strip(" ·")))
        months.append({"slug": slug, "label": label, "note": re.sub(r"<[^>]+>", "", note),
                       "dsum": dsum, "dailies": dailies, "current": False})
    return months

# ------------------------------------------------------- builders
def build_style():
    p = os.path.join(ROOT, "style.css")
    open(p, "w", encoding="utf-8").write(STYLE_CSS)
    print("wrote style.css")

def build_dailies(dates):
    upd = os.path.join(ROOT, "updates")
    idx = {d: i for i, d in enumerate(dates)}
    for d in dates:
        path = os.path.join(upd, d + ".html")
        title, body = extract_body(path, "../")
        i = idx[d]
        prev_d = dates[i - 1] if i > 0 else None
        next_d = dates[i + 1] if i + 1 < len(dates) else None
        pn = []
        if prev_d:
            pn.append(f'<a class="prev" href="{prev_d}.html">← {date_label(prev_d)}</a>')
        if next_d:
            pn.append(f'<a class="next" href="{next_d}.html">{date_label(next_d)} →</a>')
        main = (f'<div class="content">\n{body}\n</div>\n'
                f'<div class="pn">{"".join(pn)}</div>\n'
                f'<p class="backline"><a href="../archive.html">📁 All dates in the archive</a></p>')
        c = crumbs("../", ("Home", "../index.html"), ("Archive", "../archive.html"), (date_label(d), None))
        html = page_shell(title, "../", "", c, main)
        open(path, "w", encoding="utf-8").write(html)
    print(f"rewrapped {len(dates)} daily pages")

def build_monthlies():
    md = os.path.join(ROOT, "monthly")
    slugs = sorted(f[:-5] for f in os.listdir(md) if f.endswith(".html"))
    for s in slugs:
        path = os.path.join(md, s + ".html")
        title, body = extract_body(path, "../")
        main = (f'<div class="content">\n{body}\n</div>\n'
                f'<p class="backline"><a href="../archive.html">📁 All dates in the archive</a></p>')
        c = crumbs("../", ("Home", "../index.html"), ("Archive", "../archive.html"), (month_label(s), None))
        html = page_shell(title, "../", "monthly" if s == LATEST_MONTHLY else "", c, main)
        open(path, "w", encoding="utf-8").write(html)
    print(f"rewrapped {len(slugs)} monthly pages")

def build_compare():
    path = os.path.join(ROOT, "compare.html")
    title, body = extract_body(path, "")
    main = f'<div class="content">\n{body}\n</div>'
    c = crumbs("", ("Home", "index.html"), ("Site comparison", None))
    html = page_shell(title, "", "compare", c, main)
    open(path, "w", encoding="utf-8").write(html)
    print("rewrapped compare.html")

def build_archive(months):
    newest = LATEST_DAILY
    # month HTML blocks, September 2026 (current) first
    blocks_by_year = {}
    for mi, m in enumerate(months):
        slug = m["slug"]
        dailies = m["dailies"]
        ds = f"{slug.replace('-', ' ')} {m['label'].lower()} " + " ".join(l.lower() for _, l, _ in dailies)
        if m.get("current"):
            items = []
            for s, l, n in dailies:
                today = ' id="today"' if s == newest else ""
                items.append(f'<li{today}><a href="updates/{s}.html">{l}</a> <span class="cnt">· {n}</span></li>')
            block = f"""<section class="month-block" data-search="{ds}">
<h3 style="color:var(--link);margin:0 0 .2rem">{m["label"]}</h3>
<p class="lede">{m["note"] or "Daily updates."}</p>
<ul class="days big">
{chr(10).join(items)}
</ul>
</section>"""
        else:
            ditems = "".join(
                f'<li><a href="updates/{s}.html">{l}</a> <span class="cnt">· {n}</span></li>'
                for s, l, n in dailies)
            det = ""
            if dailies:
                det = f"""<details class="dailies"><summary>📅 Daily pages — {len(dailies)} day{"s" if len(dailies) != 1 else ""}</summary>
<ul class="days">{ditems}</ul></details>"""
            elif m.get("dsum"):
                det = f"""<details class="dailies"><summary>📅 Daily pages — {m["dsum"]}</summary><ul class="days"></ul></details>"""
            block = f"""<section class="month-block" data-search="{ds}">
<a class="mcard" href="monthly/{slug}.html"><h3>{m["label"]}</h3><p>{m["note"]}</p>
<div class="meta"><span class="chip"><b>{len(dailies)}</b> daily pages</span><span class="chip">🏦 Bank</span><span class="chip">🎓 UPSC</span><span class="chip">🏭 PSU</span></div>
<p class="go" style="margin-top:.5rem">Open monthly digest →</p></a>
{det}
</section>"""
        blocks_by_year.setdefault(slug[:4], []).append(block)

    body_parts = [f"""<h1 style="color:#fff;margin:.2rem 0 .4rem">📁 Archive by Date</h1>
<p class="lede">Every daily digest and monthly compilation — newest first. Use the search to jump to any date.</p>
<div class="searchbar"><span class="icon">🔍</span><input id="q" type="search" placeholder="Filter by date or month — e.g. 2026-08-15 or August" aria-label="Filter archive"></div>
<div id="no-results">No dates match your search.</div>"""]
    for year in sorted(blocks_by_year, reverse=True):
        body_parts.append(f'<h2 class="section year-h">📅 {year}</h2>\n' + "\n".join(blocks_by_year[year]))
    body_parts.append("""<script>
const q=document.getElementById('q');
q.addEventListener('input',()=>{
  const s=q.value.trim().toLowerCase();let any=false;
  document.querySelectorAll('h2.year-h').forEach(h=>{
    let visAny=false,el=h.nextElementSibling;
    while(el&&!(el.tagName==='H2'&&el.classList.contains('year-h'))){
      if(el.classList&&el.classList.contains('month-block')){
        let vis=0;
        el.querySelectorAll('ul.days li').forEach(li=>{
          const hit=!s||li.textContent.toLowerCase().includes(s)||el.dataset.search.includes(s);
          li.style.display=hit?'':'none';if(hit)vis++;
        });
        const card=el.querySelector('.mcard');
        if(card)card.style.display=(!s||el.dataset.search.includes(s))?'':'none';
        const show=!s||el.dataset.search.includes(s)||vis>0;
        el.style.display=show?'':'none';if(show){visAny=true;any=true;}
      }
      el=el.nextElementSibling;
    }
    h.style.display=visAny?'':'none';
  });
  document.getElementById('no-results').style.display=any?'none':'block';
});
</script>""")
    c = crumbs("", ("Home", "index.html"), ("Archive", None))
    html = page_shell("Archive — Current Affairs for Exams", "", "archive", c,
                      "\n".join(body_parts))
    open(os.path.join(ROOT, "archive.html"), "w", encoding="utf-8").write(html)
    print(f"rebuilt archive.html ({len(months)} month blocks)")

def build_index(months, top5, compare_section, sept_days):
    # hero one-liners
    lis = "\n".join(f"<li>{li}</li>" for li in top5)
    newest_note = next((n for s, l, n in sept_days if s == LATEST_DAILY), "")
    hero = f"""<div class="hero"><div class="inner">
<span class="hero-kicker">Updated {date_label(LATEST_DAILY)} · Bank • UPSC • PSU</span>
<h1>📚 Current Affairs for Exams</h1>
<p class="lead">Exam-ready daily current affairs — top stories, 60-second rapid-fire one-liners and a quiz, compiled from 17 top sources: GKToday, Insights IAS, Drishti IAS, Testbook, AffairsCloud and more.</p>
<div class="actions">
<a class="btn primary" href="updates/{LATEST_DAILY}.html">Read today's digest →</a>
<a class="btn ghost" href="archive.html">Browse the archive</a>
</div>
<div class="top5"><h3>⚡ Today's top 5 — {date_label(LATEST_DAILY)}</h3>
<ol>{lis}</ol>
<a href="updates/{LATEST_DAILY}.html">Read all {newest_note.split(",")[0] if newest_note else "stories"} + rapid-fire + quiz →</a>
</div>
</div></div>"""

    quick = f"""<h2 class="section">🚀 Quick links</h2>
<div class="grid">
<a class="linkcard" href="updates/{LATEST_DAILY}.html"><span class="ic">📰</span><span><b>Today's digest</b><span>{date_label(LATEST_DAILY)} — top stories, rapid-fire, quiz</span></span></a>
<a class="linkcard" href="updates/{LATEST_DAILY}.html#quiz"><span class="ic">🧠</span><span><b>Today's quiz</b><span>10 questions — test yourself</span></span></a>
<a class="linkcard" href="monthly/{LATEST_MONTHLY}.html"><span class="ic">📅</span><span><b>{month_label(LATEST_MONTHLY)} digest</b><span>Full monthly compilation</span></span></a>
<a class="linkcard" href="archive.html"><span class="ic">🗂️</span><span><b>Full archive</b><span>87 day-wise pages · 12 monthly digests</span></span></a>
<a class="linkcard" href="compare.html"><span class="ic">⚔️</span><span><b>Site comparison</b><span>Which CA site for which exam</span></span></a>
</div>"""

    legend = """<h2 class="section">🏷️ Exam-tag legend</h2>
<div class="legend">
<div class="li"><b>🏦 Bank</b> — IBPS, SBI, RBI &amp; banking-awareness exams</div>
<div class="li"><b>🎓 UPSC</b> — Civil Services Prelims &amp; Mains</div>
<div class="li"><b>🏭 PSU</b> — PSU, SSC &amp; other government exams</div>
<div class="li"><b>⭐ High-yield</b> — most likely to be asked</div>
</div>"""

    # month grid (12 months, newest first)
    cards = []
    for m in months:
        slug = m["slug"]
        n = len(m["dailies"])
        if m.get("current"):
            # monthly digest not published yet — link to latest daily instead
            cards.append(f"""<a class="mcard" href="updates/{LATEST_DAILY}.html"><h3>{m["label"]}</h3>
<p>{n} daily updates · monthly digest at month-end</p>
<div class="meta"><span class="chip">🏦</span><span class="chip">🎓</span><span class="chip">🏭</span></div>
<p class="go" style="margin-top:.5rem">Open latest daily →</p></a>""")
            continue
        sub = f"{n} daily page{'s' if n != 1 else ''}"
        cards.append(f"""<a class="mcard" href="monthly/{slug}.html"><h3>{m["label"]}</h3>
<p>{sub} · exam tags, one-liners &amp; quiz</p>
<div class="meta"><span class="chip">🏦</span><span class="chip">🎓</span><span class="chip">🏭</span></div>
<p class="go" style="margin-top:.5rem">Open →</p></a>""")
    month_grid = f"""<h2 class="section">📅 Browse by month</h2>
<div class="grid">
{chr(10).join(cards)}
</div>"""

    recent = "\n".join(
        f'<li><a href="updates/{s}.html">{l}</a> — {n}</li>' for s, l, n in sept_days[:4])
    recent_html = f"""<h2 class="section">🗂️ Recent digests</h2>
<ul class="tight">
{recent}
<li><a href="archive.html">All 87 day-wise pages →</a></li>
</ul>"""

    main = None  # (hero is rendered outside .wrap; see shell below)
    # assemble: hero is outside .wrap
    shell_top = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="/current-affairs-exams/auth.js"></script>
<title>Current Affairs for Exams — Bank • UPSC • PSU</title>
<meta name="description" content="Exam-ready daily current affairs for Bank, UPSC and PSU aspirants — top stories, rapid-fire one-liners and quizzes.">
<link rel="stylesheet" href="style.css">
</head>
<body>
{site_header("", "home")}
{hero}
<main class="wrap">
{quick}
{legend}
{month_grid}
{recent_html}
{compare_section}
</main>
{site_footer("")}
</body>
</html>
"""
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(shell_top)
    print("rebuilt index.html")

def main():
    print("parsing archive...")
    months = parse_archive()
    print(f"  {len(months)} month blocks; dailies: " +
          ", ".join(f"{m['slug']}:{len(m['dailies'])}" for m in months))
    upd = os.path.join(ROOT, "updates")
    dates = sorted(f[:-5] for f in os.listdir(upd) if f.endswith(".html"))
    print(f"  {len(dates)} daily pages: {dates[0]} … {dates[-1]}")

    # hero data from latest daily
    latest_src = open(os.path.join(upd, LATEST_DAILY + ".html"), encoding="utf-8").read()
    m = re.search(r"Rapid-fire one-liners.*?</h2>\s*<ul>(.*?)</ul>", latest_src, re.S)
    lis = re.findall(r"<li>(.*?)</li>", m.group(1), re.S) if m else []
    top5 = lis[:5]
    print(f"  hero one-liners extracted: {len(top5)}")

    # site-comparison section from index (content preserved verbatim; both formats)
    old_index = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    m = re.search(r'(<h2(?: class="section")?>⚔️ Which site for what\?</h2>.*?<a href="compare\.html">→ Full head-to-head comparison.*?</a></p>)',
                  old_index, re.S)
    compare_section = ""
    if m:
        sec = m.group(1)
        print("  compare section extracted from index.html")
    else:
        fb = os.path.join(ROOT, "tools", "index_compare_section.snippet")
        if os.path.exists(fb):
            sec = open(fb, encoding="utf-8").read()
            print("  compare section restored from tools/index_compare_section.html")
        else:
            print("  WARNING: compare section not found anywhere")
            sec = ""
    if sec:
        sec = re.sub(r'<h2(?: class="section")?>', '<h2 class="section">', sec, count=1)

        def table_fix(tm):
            t = tm.group(0)
            if '<div class="table-scroll">' in t:
                return t  # already converted (idempotent re-run)
            t = t.replace("<table>", '<div class="table-scroll"><table><thead>', 1)
            t = re.sub(r"</tr>\s*<tr><td", "</tr></thead><tbody><tr><td", t, count=1)
            t = t.replace("</table>", "</tbody></table></div>", 1)
            return t
        sec = re.sub(r"(?:<div class=\"table-scroll\">)?<table>.*?</table>(?:</div>)?", table_fix, sec, flags=re.S)
        compare_section = sec.strip()

    sept_days = months[0]["dailies"]

    build_style()
    build_dailies(dates)
    build_monthlies()
    build_compare()
    build_archive(months)
    build_index(months, top5, compare_section, sept_days)

    # JSON feed for the Flutter app — regenerated with every site rebuild
    # so the app always sees the newest digests.
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import build_api
        build_api.main()
    except Exception as e:
        print(f"  WARNING: build_api failed: {e}")
    print("DONE")

if __name__ == "__main__":
    main()
