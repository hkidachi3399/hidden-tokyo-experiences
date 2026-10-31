#!/usr/bin/env python3
"""Publish scheduled blog posts.

Posts staged in _scheduled/*.html start with comment lines:
  <!--publish_at: 2026-11-08T09:00:00+09:00-->
  <!--thumb: ../manga.jpg-->
  <!--card: one-sentence summary for the blog index card-->
  <!--llms: one-sentence description for llms.txt-->
When publish_at has passed, the file moves to blog/, and the blog index,
sitemap.xml and llms.txt are updated. Run hourly by GitHub Actions.
"""
import re, sys, glob, os, datetime as dt, html

BASE = "https://hkidachi3399.github.io/hidden-tokyo-experiences/blog/"
now = dt.datetime.now(dt.timezone.utc)
published = []

def meta(src, key):
    m = re.search(r"<!--%s:\s*(.*?)\s*-->" % key, src)
    return m.group(1) if m else None

for path in sorted(glob.glob("_scheduled/*.html")):
    src = open(path, encoding="utf-8").read()
    when = meta(src, "publish_at")
    if not when:
        print("skip (no publish_at):", path); continue
    if dt.datetime.fromisoformat(when) > now:
        print("not yet:", path, when); continue
    thumb = meta(src, "thumb") or "../hero.jpg"
    card = meta(src, "card") or ""
    llms = meta(src, "llms") or ""
    title = html.unescape(re.search(r"<h1>(.*?)</h1>", src, re.S).group(1)).strip()
    datelabel = re.search(r'<span class="date">(.*?) ·', src).group(1)
    short = re.search(r'<span class="date">(.*?)</span>', src).group(1)
    clean = re.sub(r"<!--(publish_at|thumb|card|llms):.*?-->\n?", "", src)
    name = os.path.basename(path)
    open("blog/" + name, "w", encoding="utf-8").write(clean)
    os.remove(path)

    idx = open("blog/index.html", encoding="utf-8").read()
    cardhtml = (
        f'<a class="post-card" href="{name}">\n'
        f"<div class=\"thumb\" style=\"background-image:url('{thumb}')\"></div>\n"
        f'<div class="body">\n<span class="date">{" · ".join(short.split(" · ")[:2])}</span>\n'
        f"<h2>{title}</h2>\n<p>{card}</p>\n</div>\n</a>\n"
    )
    m = re.search(r"<!-- POSTS:START[^>]*-->\n", idx)
    open("blog/index.html", "w", encoding="utf-8").write(idx[: m.end()] + cardhtml + idx[m.end():])

    day = dt.datetime.fromisoformat(when).date().isoformat()
    sm = open("sitemap.xml", encoding="utf-8").read()
    entry = (f"<url>\n<loc>{BASE}{name}</loc>\n<lastmod>{day}</lastmod>\n"
             f"<changefreq>monthly</changefreq>\n<priority>0.7</priority>\n</url>\n")
    open("sitemap.xml", "w", encoding="utf-8").write(sm.replace("</urlset>", entry + "</urlset>"))

    l = open("llms.txt", encoding="utf-8").read()
    line = f"- [{title}]({BASE}{name}): {llms}\n"
    anchor = "- [Totoro's Forest Is Real"
    i = l.find(anchor)
    j = l.find("\n", i) + 1 if i >= 0 else len(l)
    open("llms.txt", "w", encoding="utf-8").write(l[:j] + line + l[j:])
    published.append(name)
    print("published:", name)

if published:
    print("::notice::published " + ", ".join(published))
sys.exit(0)
