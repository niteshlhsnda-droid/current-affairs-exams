#!/usr/bin/env python3
"""Convert updates/2026-09-24.md to the initial HTML page in the site's
new-format shell (matching the 2026-09-23 page structure)."""
import re, html

SRC = "/home/hatch/workspace/current-affairs-exams/updates/2026-10-07.md"
DST = "/home/hatch/workspace/current-affairs-exams/updates/2026-10-07.html"
SLUG = "2026-10-07"
DATE_LONG = "7 October 2026"
DATE_SHORT = "7 Oct 2026"

def inline(t):
    # markdown links first (before escaping)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    t = html.escape(t, quote=True).replace('&#x27;', "&#x27;")
    # unescape the link tags we just made
    t = t.replace('&lt;a href=&quot;', '<a href="').replace('&quot;&gt;', '">').replace('&lt;/a&gt;', '</a>')
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    return t

md = open(SRC, encoding='utf-8').read().split('\n')
body = []
i = 0
in_details = False
list_open = None

def close_list():
    global list_open
    if list_open:
        body.append('</%s>' % list_open)
        list_open = None

while i < len(md):
    s = md[i].strip()
    if s.startswith('<details>'):
        close_list(); in_details = True; body.append('<details>'); i += 1; continue
    if s.startswith('</details>'):
        close_list(); in_details = False; body.append('</details>'); i += 1; continue
    if in_details:
        if s.startswith('<summary>'):
            body.append(re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s))
        elif s:
            body.append('<p>%s</p>' % inline(s))
        i += 1; continue
    if s.startswith('# '):
        close_list(); body.append('<h1>%s</h1>' % inline(s[2:])); i += 1; continue
    if s.startswith('## '):
        close_list()
        h = s[3:]
        aid = ' id="quiz"' if 'Quiz' in h else ''
        body.append('<h2%s>%s</h2>' % (aid, inline(h))); i += 1; continue
    if s.startswith('### '):
        close_list(); body.append('<h3>%s</h3>' % inline(s[4:])); i += 1; continue
    if s == '---':
        close_list(); body.append('<hr>'); i += 1; continue
    m = re.match(r'^\d+\.\s+(.*)$', s)
    if m:
        if list_open != 'ol':
            close_list(); body.append('<ol>'); list_open = 'ol'
        q = m.group(1)
        body.append('<li>%s</li>' % inline(q)); i += 1
        # quiz options line follows immediately
        if i < len(md) and re.match(r'^\s*a\)', md[i]):
            close_list()
            body.append('<p>%s</p>' % inline(md[i].strip()))
            i += 1
        continue
    if s.startswith('- '):
        if list_open != 'ul':
            close_list(); body.append('<ul>'); list_open = 'ul'
        body.append('<li>%s</li>' % inline(s[2:])); i += 1; continue
    if s == '':
        close_list(); i += 1; continue
    close_list()
    body.append('<p>%s</p>' % inline(s)); i += 1
close_list()

inner = '\n'.join(body)

page = '''<!DOCTYPE html>
<html lang="en">
<head>
<script src="/current-affairs-exams/auth.js"></script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Current Affairs — {ds}</title>
<meta name="description" content="Exam-ready daily current affairs for Bank, UPSC and PSU aspirants — rapid-fire one-liners, top stories and quizzes.">
<link rel="stylesheet" href="../style.css">
</head>
<body>
<header class="site-header"><div class="inner">
<a class="brand" href="../index.html"><span class="logo">📚</span><span><b>Current Affairs for Exams</b><small>Bank • UPSC • PSU — daily exam-ready digests</small></span></a>
<nav class="main" aria-label="Main navigation">
<a href="../index.html">Home</a><a href="../archive.html">Archive</a><a href="../archive.html#today">Latest</a><a href="../monthly/2026-08.html">Monthly</a><a href="../updates/{slug}.html#quiz">Quiz</a><a href="../compare.html">Compare</a>
</nav></div></header>
<main class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="../index.html">Home</a><span class="sep">›</span><a href="../archive.html">Archive</a><span class="sep">›</span><span>{dl}</span></nav>
<div class="content">
{inner}
</div>
<div class="pn"><a class="prev" href="2026-10-06.html">← 6 October 2026</a></div>
<p class="backline"><a href="../archive.html">📁 All dates in the archive</a></p>
</main>
<footer class="site"><div class="inner">
<b>📚 Current Affairs for Exams</b> — original curation &amp; quizzes: <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.<br>
Compiled from public coverage on GKToday, Insights IAS, Drishti IAS, Testbook, AffairsCloud, Vision IAS, ForumIAS, IASbaba, ClearIAS, Adda247, Oliveboard, Jagran Josh, Guidely, StudyIQ, Unacademy &amp; PIB.<br>
<a href="../index.html">Home</a> · <a href="../archive.html">Archive</a> · <a href="https://github.com/niteshlhsnda-droid/current-affairs-exams">GitHub</a>
</div></footer>
</body>
</html>
'''.format(ds=DATE_SHORT, slug=SLUG, dl=DATE_LONG, inner=inner)

open(DST, 'w', encoding='utf-8').write(page)
print('wrote', DST, len(page), 'bytes')

# Web-visibility upgrade: add OG/Twitter meta + PostHog (head) and the
# cookie-consent banner (before </body>), matching tools/build_site.py.
# (Applied after .format() so the snippet's curly braces are never
#  misinterpreted by .format().)
SITE_ABS = "https://niteshlhsnda-droid.github.io/current-affairs-exams"
page = open(DST, encoding='utf-8').read()
og = f'''<meta property="og:type" content="website">
<meta property="og:site_name" content="Current Affairs for Exams">
<meta property="og:title" content="Current Affairs — {DATE_SHORT} — Bank • UPSC • PSU">
<meta property="og:description" content="Exam-ready daily current affairs for {DATE_LONG} — top stories, rapid-fire one-liners and quiz.">
<meta property="og:url" content="{SITE_ABS}/updates/{SLUG}.html">
<meta property="og:image" content="{SITE_ABS}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Current Affairs — {DATE_SHORT} — Bank • UPSC • PSU">
<meta name="twitter:description" content="Exam-ready daily current affairs for {DATE_LONG} — top stories, rapid-fire one-liners and quiz.">
<meta name="twitter:image" content="{SITE_ABS}/og-image.png">
<meta name="theme-color" content="#0d1424">'''
posthog = '''<script>
(function(){
  var POSTHOG_KEY="phc_y8aXUtfCQhZfTPeYq5VebFcGGztU5AedbYLgM4pdqagD";
  var POSTHOG_HOST="https://eu.i.posthog.com";
  if(!POSTHOG_HOST||POSTHOG_HOST.indexOf("https://eu.i.posthog.com")===0){POSTHOG_HOST="https://eu.i.posthog.com";}
  function loadPH(){
    if(window.posthog||!POSTHOG_KEY||POSTHOG_KEY.indexOf("phc_y8aXUtfCQhZfTPeYq5VebFcGGztU5AedbYLgM4pdqagD")===0)return;
    var s=document.createElement("script");s.async=true;
    s.src=POSTHOG_HOST.replace(/\\/$/,"")+"/static/array.js";
    s.onload=function(){try{posthog.init(POSTHOG_KEY,{api_host:POSTHOG_HOST,capture_pageview:true,autocapture:true});}catch(e){}};
    document.head.appendChild(s);
  }
  try{if(localStorage.getItem("cc-consent")==="accepted"){loadPH();}}catch(e){}
  window.__loadPostHog=loadPH;
})();
</script>'''
banner = '''<div id="cc-banner" hidden>
<span>We use optional analytics cookies (PostHog) to understand visits and improve the site. No ads, no cross-site tracking.</span>
<span class="cc-actions"><button id="cc-accept" type="button">Accept</button><button id="cc-decline" type="button">Decline</button></span>
</div>
<script>
(function(){
  var key="cc-consent";
  function show(){var b=document.getElementById("cc-banner");if(b)b.hidden=false;}
  function choose(v){
    try{localStorage.setItem(key,v);}catch(e){}
    var b=document.getElementById("cc-banner");if(b)b.hidden=true;
    if(v==="accepted"&&typeof window.__loadPostHog==="function"){window.__loadPostHog();}
  }
  try{if(localStorage.getItem(key))return;}catch(e){return;}
  if(document.readyState==="loading"){document.addEventListener("DOMContentLoaded",show);}
  else{show();}
  document.getElementById("cc-accept").addEventListener("click",function(){choose("accepted");});
  document.getElementById("cc-decline").addEventListener("click",function(){choose("declined");});
})();
</script>'''
page = page.replace('<link rel="stylesheet" href="../style.css">\n</head>',
                    '<link rel="stylesheet" href="../style.css">\n' + og + '\n' + posthog + '\n</head>', 1)
page = page.replace('</body>', banner + '\n</body>', 1)
open(DST, 'w', encoding='utf-8').write(page)
print('patched', DST, 'with OG/meta + PostHog + consent banner')
