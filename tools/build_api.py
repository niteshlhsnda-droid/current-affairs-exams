#!/usr/bin/env python3
"""Build the JSON API consumed by the Flutter current-affairs app.

Parses every updates/YYYY-MM-DD.md digest into structured JSON:

  api/v1/index.json          — list of all days, newest first, with metadata
  api/v1/latest.json         — pointer to the newest day + headline summary
  api/v1/daily/<slug>.json   — full structured digest for one day

Idempotent: re-running over the same sources produces byte-identical output.
Safe to call from build_site.py after the HTML rebuild.
"""
import os, re, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPDATES = os.path.join(ROOT, "updates")
API_V1 = os.path.join(ROOT, "api", "v1")
DAILY = os.path.join(API_V1, "daily")

TAG_EMOJI = {"🏦": "bank", "🎓": "upsc", "🏭": "psu", "⭐": "high-yield"}
EMOJI_RUN = re.compile(r"([\U0001F300-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F]+)\s*$")

MONTH_NAMES = ["January","February","March","April","May","June","July",
               "August","September","October","November","December"]

def date_label(slug):
    y, m, d = slug.split("-")
    return f"{int(d)} {MONTH_NAMES[int(m)-1]} {y}"

def strip_trailing_emoji(s):
    """Return (clean_text, [tags]) splitting a trailing emoji run into tags."""
    m = EMOJI_RUN.search(s)
    if not m:
        return s.strip(), []
    run, rest = m.group(1), s[:m.start()]
    tags = [TAG_EMOJI[ch] for ch in run if ch in TAG_EMOJI]
    return rest.strip(), tags

def clean_md(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)   # bold
    s = re.sub(r"\*(.+?)\*", r"\1", s)        # italic
    s = re.sub(r"`(.+?)`", r"\1", s)         # code
    return s.strip()

def parse_digest(slug, text):
    day = {"slug": slug, "date": date_label(slug),
           "categories": [], "one_liners": [], "quiz": []}
    lines = text.splitlines()
    section = None          # 'stories' | 'oneliners' | 'quiz' | None
    category = None
    qi = None               # current quiz question being built

    def close_question():
        nonlocal qi
        if qi and qi.get("options"):
            day["quiz"].append(qi)
        qi = None

    for raw in lines:
        line = raw.strip()
        if line.startswith("## "):
            close_question()
            h = line[3:].strip().lower()
            if "rapid-fire" in h or "one-liner" in h:
                section = "oneliners"
            elif line[3:].strip().startswith("🧠") or "quiz" in h:
                section = "quiz"
            elif "top stories" in h or "evening" in h:
                section = "stories"
            else:
                section = None
            category = None
            continue

        if section == "stories" and line.startswith("### "):
            close_question()
            name, _ = strip_trailing_emoji(line[4:].strip())
            category = {"name": clean_md(name), "stories": []}
            day["categories"].append(category)
            continue

        m = re.match(r"^(\d+)\.\s+\*\*(.+?)\*\*\s*[—–-]\s*(.*)$", line)
        if section == "stories" and m and category is not None:
            num, title, body = m.group(1), m.group(2), m.group(3)
            body, tags = strip_trailing_emoji(body)
            story = {"id": f"{slug}-{num}",
                     "title": clean_md(title),
                     "body": clean_md(body),
                     "tags": tags}
            category["stories"].append(story)
            continue

        if section == "oneliners" and line.startswith("- "):
            text_, _ = strip_trailing_emoji(line[2:])
            if text_:
                day["one_liners"].append(clean_md(text_))
            continue

        qm = re.match(r"^(\d+)\.\s+(.+)$", line)
        if section == "quiz":
            if qm and not re.search(r"[a-d]\)", line):
                close_question()
                qi = {"id": f"{slug}-q{qm.group(1)}",
                      "question": clean_md(qm.group(2)),
                      "options": [], "answer": None}
                continue
            # options may share one line: "a) X  b) Y  c) Z  d) W"
            opts = re.findall(r"([a-d])\)\s*(.+?)(?=\s+[a-d]\)\s*|$)", line)
            if opts and qi is not None:
                for key, text_ in opts:
                    qi["options"].append({"key": key,
                                          "text": clean_md(text_)})
                continue
            am = re.search(r"(\d+)-([a-d])", line)
            if am and "<details>" not in line and "summary" not in line:
                # answers line like "1-c, 2-b, 3-b" — end of quiz content
                for num, key in re.findall(r"(\d+)-([a-d])", line):
                    q = next((x for x in day["quiz"]
                              if x["id"] == f"{slug}-q{num}"), None)
                    if q:
                        q["answer"] = key
                if qi and qi.get("options"):
                    for num, key in re.findall(r"(\d+)-([a-d])", line):
                        if qi["id"] == f"{slug}-q{num}":
                            qi["answer"] = key
                close_question()
                section = None   # footer follows; nothing more to parse
                continue
    close_question()

    # Drop categories that ended up empty (defensive for odd formats)
    day["categories"] = [c for c in day["categories"] if c["stories"]]
    return day

def day_summary(day):
    stories = [s for c in day["categories"] for s in c["stories"]]
    high = [s for s in stories if "high-yield" in s["tags"]]
    return {
        "slug": day["slug"],
        "date": day["date"],
        "story_count": len(stories),
        "one_liner_count": len(day["one_liners"]),
        "quiz_count": len(day["quiz"]),
        "high_yield_count": len(high),
        "categories": [c["name"] for c in day["categories"]],
        "top_stories": [s["title"] for s in stories[:5]],
    }

def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    text = json.dumps(obj, ensure_ascii=False, indent=1,
                      sort_keys=False) + "\n"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)

def main():
    slugs = sorted(f[:-3] for f in os.listdir(UPDATES) if f.endswith(".md"))
    days = []
    for slug in slugs:
        with open(os.path.join(UPDATES, slug + ".md"), encoding="utf-8") as fh:
            text = fh.read()
        try:
            day = parse_digest(slug, text)
        except Exception as e:  # never let one bad digest kill the feed
            print(f"  WARNING: could not parse {slug}: {e}")
            continue
        days.append(day)
        write_json(os.path.join(DAILY, slug + ".json"), day)
        print(f"  {slug}: {sum(len(c['stories']) for c in day['categories'])} stories, "
              f"{len(day['one_liners'])} one-liners, {len(day['quiz'])} quiz")

    index = [day_summary(d) for d in reversed(days)]
    write_json(os.path.join(API_V1, "index.json"),
               {"count": len(index), "days": index})
    if index:
        latest = index[0]
        write_json(os.path.join(API_V1, "latest.json"),
                   {"latest": latest["slug"], "updated": latest["slug"],
                    "summary": latest})
    print(f"API DONE: {len(days)} days -> api/v1/")

if __name__ == "__main__":
    main()
