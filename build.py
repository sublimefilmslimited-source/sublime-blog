#!/usr/bin/env python3
"""Sublime Media blog builder.

Reads posts/*.md (YAML front matter + Markdown) and writes a static blog to
public/blog/ :  index page, one folder per post, RSS feed, blog sitemap and
social cover images. Pages reuse the live site's CSS and JS (/assets/...).

Run:  python3 build.py
"""
import datetime as dt, html, json, math, os, re, shutil, sys
from pathlib import Path
from xml.sax.saxutils import escape as xesc

import markdown, yaml
from PIL import Image, ImageDraw, ImageFont

import graphics

ROOT = Path(__file__).resolve().parent
POSTS = ROOT / "posts"
OUT = ROOT / "public" / "blog"
SRC = ROOT / "src"
SITE = "https://www.sublimemedialimited.com"
BLOG = SITE + "/blog"
TODAY = dt.date.today()

AUTHOR = {
    "name": "Zelia Kafene",
    "role": "Founder & Chief Strategist, Sublime Media Limited",
    "bio": ("Zelia Kafene founded Sublime Media Limited in 2019 and leads its strategy work for brands "
            "across Africa. She also teaches at the School of Social Media Managers, where she trains new "
            "social media managers to do client-ready work."),
    "url": SITE + "/#about",
    "image": "/blog/img/zelia.jpg",
    "same_as": ["https://www.linkedin.com/in/emuobo-zelia-kafene-24488211a",
                "https://www.youtube.com/@Zeliakafene"],
}

# ---------------------------------------------------------------- template
LOGO = ('<svg viewBox="0 0 470 140" {extra}role="img" aria-label="Sublime Media Limited">'
        '<polygon points="36,10 108,4 76,44 62,44 62,64 34,96 34,38" fill="{a}"/>'
        '<polygon points="84,130 12,136 44,96 58,96 58,76 86,44 86,102" fill="#d80707"/>'
        '<text x="130" y="72" font-family="Gilroy,\'Arial Black\',sans-serif" font-weight="700" font-size="54" fill="{a}" letter-spacing="2">SUBLIME</text>'
        '<text x="132" y="112" font-family="Gilroy,\'Arial Black\',sans-serif" font-weight="700" font-size="26" fill="#d80707" letter-spacing="5">MEDIA LIMITED</text></svg>')

HEADER = f"""<header class="sm-header" id="smHeader">
  <div class="container sm-bar">
    <a class="sm-logo" href="/" aria-label="Sublime Media Limited home">
      {LOGO.format(extra='', a='#0b0b0c')}
    </a>
    <nav class="sm-nav" aria-label="Main">
      <ul>
        <li><a href="/#about">About</a></li>
        <li><a href="/#services">Services</a></li>
        <li><a href="/#work">Our Work</a></li>
        <li><a href="/school">School</a></li>
        <li><a href="/affiliate/">Affiliate</a></li>
        <li><a href="/blog/" class="active">Blog</a></li>
        <li><a href="/#contact">Contact</a></li>
      </ul>
    </nav>
    <a href="/#contact" class="btn btn-primary">Start a Project</a>
    <button class="sm-burger" id="smBurger" aria-label="Open menu" aria-expanded="false"><span></span><span></span><span></span></button>
  </div>
</header>"""

SOCIAL = """<div class="sm-social">
        <a href="https://www.instagram.com/sublime_medialimited/" aria-label="Instagram"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg></a>
        <a href="https://www.tiktok.com/@sublime_media" aria-label="TikTok"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M16.5 3a4.5 4.5 0 0 0 4 4v3a7.5 7.5 0 0 1-4-1.2V15a6 6 0 1 1-6-6h.5v3H10a3 3 0 1 0 3.5 3V3z"/></svg></a>
        <a href="https://www.linkedin.com/company/sublime-media-and-films-limited/" aria-label="LinkedIn"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M4 9h3.5v11H4zM5.8 3.5a2 2 0 1 1 0 4 2 2 0 0 1 0-4zM10 9h3.3v1.6h.1A3.7 3.7 0 0 1 16.7 9C20 9 20.5 11 20.5 14v6H17v-5.3c0-1.3 0-2.9-1.8-2.9s-2 1.4-2 2.8V20H10z"/></svg></a>
        <a href="https://www.youtube.com/@Zeliakafene" aria-label="YouTube"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M22 8.2a3 3 0 0 0-2.1-2.1C18 5.6 12 5.6 12 5.6s-6 0-7.9.5A3 3 0 0 0 2 8.2 31 31 0 0 0 1.6 12 31 31 0 0 0 2 15.8a3 3 0 0 0 2.1 2.1c1.9.5 7.9.5 7.9.5s6 0 7.9-.5a3 3 0 0 0 2.1-2.1 31 31 0 0 0 .4-3.8 31 31 0 0 0-.4-3.8zM10 15V9l5.2 3z"/></svg></a>
        <a href="https://whatsapp.com/channel/0029Vb8ksPe3WHTZIuuEqK12" aria-label="WhatsApp channel"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm4.5 12.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.8-1.4.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 0 0 1.8-1.3 2.2 2.2 0 0 0 .1-1.3c0-.1-.2-.2-.4-.3z"/></svg></a>
      </div>"""

FOOTER = f"""<footer class="sm-footer">
  <div class="container sm-foot">
    <div>
      <a href="/" aria-label="Sublime Media Limited home">{LOGO.format(extra='style="height:46px;width:auto" ', a='#ffffff')}</a>
      <p>Marketing, branding and production for brands across Africa.</p>
      {SOCIAL}
    </div>
    <div>
      <h4>Explore</h4>
      <ul><li><a href="/#about">About Us</a></li><li><a href="/#services">Services</a></li><li><a href="/#work">Our Work</a></li><li><a href="/school">Sublime School</a></li><li><a href="/course">The Course</a></li><li><a href="/ebook">The E-book</a></li><li><a href="/starter-kit">Starter Kit</a></li><li><a href="/affiliate/">Become an Affiliate</a></li><li><a href="/blog/">Blog</a></li></ul>
    </div>
    <div>
      <h4>Get in touch</h4>
      <ul><li>info@sublimemedialimited.com</li><li>0702 500 0608</li><li>0809 695 6014</li><li><a href="/#contact">Start a project</a></li></ul>
    </div>
  </div>
  <div class="container sm-copy"><span>© <span id="year">{TODAY.year}</span> Sublime Media Limited. All rights reserved.</span><span>Lagos, Nigeria</span></div>
</footer>

<a class="sm-wa" href="https://wa.me/2347025000608?text=Hello%20Sublime%20Media!" aria-label="Chat on WhatsApp"><svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2z"/></svg></a>
<script src="/assets/js/main.js?v=9" defer></script>"""


def page(*, title, description, canonical, og_image, og_type, body, jsonld, extra_head=""):
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in jsonld)
    return f"""<!DOCTYPE html>
<html lang="en-NG">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{canonical}">
<meta property="og:site_name" content="Sublime Media Limited">
<meta property="og:locale" content="en_NG">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title)}">
<meta name="twitter:description" content="{html.escape(description)}">
<meta name="twitter:image" content="{SITE}{og_image}">
<link rel="alternate" type="application/rss+xml" title="Sublime Media Blog" href="{BLOG}/feed.xml">
<link rel="icon" type="image/svg+xml" href="/assets/img/favicon.svg">
<link rel="preload" href="/assets/css/app.css?v=9" as="style">
<link rel="stylesheet" href="/assets/css/app.css?v=9">
<link rel="stylesheet" href="/assets/css/site.css?v=9">
<link rel="stylesheet" href="/blog/blog.css?v={BUILD_V}">
{extra_head}{ld}
</head>
<body class="font-gilroy font-medium text-gray text-lg leading-[27px]">
<a class="bl-skip" href="#main">Skip to content</a>
{HEADER}
<main id="main">
{body}
</main>
{FOOTER}
</body>
</html>
"""


# ---------------------------------------------------------------- helpers
def slugify(s):
    s = re.sub(r"[^a-z0-9\s-]", "", s.lower())
    return re.sub(r"[\s-]+", "-", s).strip("-")


def fmt_date(d):
    return d.strftime("%-d %B %Y")


def read_time(text):
    return max(1, math.ceil(len(re.findall(r"\w+", text)) / 220))


def load_posts():
    posts = []
    for f in sorted(POSTS.glob("*.md")):
        raw = f.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
        if not m:
            sys.exit(f"{f.name}: missing front matter")
        meta, body = yaml.safe_load(m.group(1)), m.group(2)
        meta.setdefault("slug", slugify(meta["title"]))
        for k in ("date", "updated"):
            if isinstance(meta.get(k), str):
                meta[k] = dt.date.fromisoformat(meta[k])
        meta.setdefault("updated", meta["date"])
        if meta.get("draft") or meta["date"] > TODAY:
            continue  # scheduled posts wait for their date
        for req in ("title", "description", "date", "category", "keyword"):
            if not meta.get(req):
                sys.exit(f"{f.name}: front matter needs '{req}'")
        if len(meta["description"]) > 160:
            print(f"warning: {f.name} description is {len(meta['description'])} chars (aim for <=155)")
        meta["body_md"] = body
        meta["url"] = f"{BLOG}/{meta['slug']}/"
        meta["path"] = f"/blog/{meta['slug']}/"
        posts.append(meta)
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def render_md(md_text):
    md = markdown.Markdown(extensions=["toc", "tables", "attr_list", "sane_lists", "smarty", "md_in_html"],
                           extension_configs={"toc": {"permalink": False, "toc_depth": "2"}})
    out = md.convert(md_text)
    toc = md.toc_tokens
    # external links open safely in a new tab
    out = re.sub(r'<a href="(https?://(?!www\.sublimemedialimited\.com)[^"]+)"',
                 r'<a href="\1" target="_blank" rel="noopener">', out)
    # lazy-load + decode images inside the article
    out = out.replace("<img ", '<img loading="lazy" decoding="async" ')
    # wrap tables for small screens
    out = out.replace("<table>", '<div class="bl-table"><table>').replace("</table>", "</table></div>")
    return out, toc


def wrap(text, font, width, draw):
    words, lines, line = text.split(), [], ""
    for w in words:
        t = (line + " " + w).strip()
        if draw.textlength(t, font=font) <= width:
            line = t
        else:
            lines.append(line); line = w
    lines.append(line)
    return lines


def cover(post, dest):
    """1200x630 branded social/cover image."""
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), "#ffffff")
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 18, H], fill="#d80707")
    d.polygon([(1060, 0), (W, 0), (W, 140)], fill="#0b0b0c")
    d.polygon([(W, 490), (W, H), (1060, H)], fill="#d80707")
    bold = ImageFont.truetype(str(SRC / "Gilroy-Bold.ttf"), 64)
    med = ImageFont.truetype(str(SRC / "Gilroy-Medium.ttf"), 28)
    small = ImageFont.truetype(str(SRC / "Gilroy-Bold.ttf"), 24)
    d.text((80, 70), post["category"].upper(), font=small, fill="#d80707")
    title = graphics._clean(post.get("cover_title") or post["title"], SRC)
    size = 64
    while True:
        bold = ImageFont.truetype(str(SRC / "Gilroy-Bold.ttf"), size)
        lines = wrap(title, bold, 960, d)
        if len(lines) <= 4 or size <= 44:
            break
        size -= 4
    y = 125
    for ln in lines[:5]:
        d.text((80, y), ln, font=bold, fill="#0b0b0c")
        y += int(size * 1.15)
    d.text((80, H - 95), "Zelia Kafene  ·  Sublime Media Limited", font=med, fill="#5d5f64")
    d.text((80, H - 55), "sublimemedialimited.com/blog", font=small, fill="#d80707")
    im.save(dest, "JPEG", quality=86, optimize=True, progressive=True)


def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u}
                                for i, (n, u) in enumerate(items)]}


ORG = {"@type": "Organization", "@id": SITE + "/#org", "name": "Sublime Media Limited", "url": SITE + "/",
       "logo": {"@type": "ImageObject", "url": SITE + "/assets/img/favicon.svg"},
       "sameAs": ["https://www.instagram.com/sublime_medialimited/",
                  "https://www.linkedin.com/company/sublime-media-and-films-limited/",
                  "https://www.tiktok.com/@sublime_media"]}
PERSON = {"@type": "Person", "@id": SITE + "/#zelia", "name": AUTHOR["name"], "jobTitle": AUTHOR["role"],
          "url": AUTHOR["url"], "image": SITE + AUTHOR["image"], "sameAs": AUTHOR["same_as"],
          "worksFor": {"@id": SITE + "/#org"}}


# ---------------------------------------------------------------- pages
def figure_html(p, spec):
    base = f"/blog/{p['slug']}/{spec['name']}"
    w, h = spec["_size"]
    cap = html.escape(spec.get("caption", ""))
    cls = "bl-fig tall" if h > w * 1.1 else "bl-fig"
    return (f'<figure class="{cls}" itemprop="image" itemscope itemtype="https://schema.org/ImageObject">'
            f'<a href="{base}.jpg"><picture><source srcset="{base}.webp" type="image/webp">'
            f'<img src="{base}.jpg" alt="{html.escape(spec["alt"])}" width="{w}" height="{h}" loading="lazy" decoding="async" itemprop="contentUrl"></picture></a>'
            + (f'<figcaption itemprop="caption">{cap}</figcaption>' if cap else "")
            + '<meta itemprop="creditText" content="Sublime Media Limited"></figure>')


def post_html(p, posts):
    md_src = p["body_md"]
    for spec in p.get("images", []):
        tag = "{{image:" + spec["name"] + "}}"
        if tag not in md_src:
            sys.exit(f"{p['slug']}: image '{spec['name']}' has no {tag} placeholder in the text")
        md_src = md_src.replace(tag, "\n\n" + figure_html(p, spec) + "\n\n")
    body_html, toc = render_md(md_src)
    rt = read_time(p["body_md"])
    img = f"/blog/{p['slug']}/{p['slug']}.jpg"
    toc_html = ""
    if len(toc) >= 3:
        toc_html = ('<nav class="bl-toc" aria-label="On this page"><b>On this page</b><ol>'
                    + "".join(f'<li><a href="#{t["id"]}">{html.escape(t["name"])}</a></li>' for t in toc)
                    + "</ol></nav>")
    faq_html, faq_ld = "", None
    if p.get("faq"):
        faq_html = ('<section class="bl-faq" id="faq"><h2>Frequently asked questions</h2>'
                    + "".join(f"<details><summary>{html.escape(q['q'])}</summary><div>{markdown.markdown(q['a'])}</div></details>"
                              for q in p["faq"]) + "</section>")
        faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
                  "mainEntity": [{"@type": "Question", "name": q["q"],
                                  "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", q["a"])}}
                                 for q in p["faq"]]}
    cta = p.get("cta", "school")
    cta_block = {
        "school": ('Want the full system, step by step?',
                   'Social Media Management Mastery takes you from your first post to paid client work, with templates you can use right away.',
                   '/school#catalog', 'See the course &amp; e-book →'),
        "agency": ('Need a team to run your social media?',
                   'Sublime Media plans, creates and manages content for brands across Africa, with monthly reports you can read in five minutes.',
                   '/#contact', 'Start a project →'),
    }[cta]
    related = [x for x in posts if x["slug"] != p["slug"]]
    related.sort(key=lambda x: (x["category"] != p["category"], -x["date"].toordinal()))
    rel_html = ""
    if related:
        rel_html = ('<section class="bl-related"><h2>Keep reading</h2><div class="bl-grid">'
                    + "".join(card(x) for x in related[:3]) + "</div></section>")
    upd = (f' · Updated <time datetime="{p["updated"].isoformat()}">{fmt_date(p["updated"])}</time>'
           if p["updated"] != p["date"] else "")
    body = f"""
<article class="bl-post" itemscope itemtype="https://schema.org/BlogPosting">
  <header class="bl-post-head container">
    <nav class="bl-crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span><a href="/blog/">Blog</a><span>/</span><a href="/blog/#{slugify(p['category'])}">{html.escape(p['category'])}</a></nav>
    <span class="sm-pill"><i></i>{html.escape(p['category'])}</span>
    <h1 itemprop="headline">{html.escape(p['title'])}</h1>
    <p class="bl-dek">{html.escape(p.get('dek', p['description']))}</p>
    <div class="bl-byline">
      <img src="{AUTHOR['image']}" alt="{AUTHOR['name']}" width="48" height="48">
      <div><b itemprop="author">{AUTHOR['name']}</b><span><time datetime="{p['date'].isoformat()}" itemprop="datePublished">{fmt_date(p['date'])}</time>{upd} · {rt} min read</span></div>
    </div>
  </header>
  <figure class="bl-cover container"><img src="{img}" alt="{html.escape(p.get('image_alt', p['title']))}" width="1200" height="630" fetchpriority="high"></figure>
  <div class="bl-layout container">
    <aside class="bl-side">{toc_html}
      <div class="bl-side-cta"><b>{cta_block[0]}</b><a class="btn btn-primary" href="{cta_block[2]}">{cta_block[3]}</a></div>
    </aside>
    <div class="bl-body" itemprop="articleBody">
      {body_html}
      {faq_html}
      <div class="bl-cta"><h2>{cta_block[0]}</h2><p>{cta_block[1]}</p><a class="btn btn-white" href="{cta_block[2]}">{cta_block[3]}</a></div>
      <div class="bl-author">
        <img src="{AUTHOR['image']}" alt="{AUTHOR['name']}" width="88" height="88" loading="lazy">
        <div><b>Written by {AUTHOR['name']}</b><small>{AUTHOR['role']}</small><p>{AUTHOR['bio']}</p></div>
      </div>
      <div class="bl-share">Share: <a href="https://wa.me/?text={html.escape(p['title'])}%20{p['url']}" target="_blank" rel="noopener">WhatsApp</a><a href="https://www.linkedin.com/sharing/share-offsite/?url={p['url']}" target="_blank" rel="noopener">LinkedIn</a><a href="https://x.com/intent/post?url={p['url']}" target="_blank" rel="noopener">X</a></div>
    </div>
  </div>
  {('<div class="container">' + rel_html + '</div>') if rel_html else ''}
</article>"""
    ld = [{"@context": "https://schema.org", "@type": "BlogPosting", "@id": p["url"] + "#post",
           "mainEntityOfPage": p["url"], "headline": p["title"][:110], "description": p["description"],
           "image": [{"@type": "ImageObject", "url": SITE + img, "width": 1200, "height": 630, "caption": p["title"]}]
                    + [{"@type": "ImageObject", "url": f"{SITE}/blog/{p['slug']}/{s['name']}.jpg", "caption": s.get("caption") or s["alt"],
                        "width": s["_size"][0], "height": s["_size"][1], "creditText": "Sublime Media Limited",
                        "creator": {"@id": SITE + "/#org"}, "copyrightNotice": "© Sublime Media Limited"} for s in p.get("images", [])], "datePublished": p["date"].isoformat(), "dateModified": p["updated"].isoformat(),
           "author": PERSON, "publisher": ORG, "articleSection": p["category"], "inLanguage": "en-NG",
           "keywords": ", ".join([p["keyword"]] + p.get("keywords", [])),
           "wordCount": len(re.findall(r"\w+", p["body_md"]))},
          crumbs_ld([("Home", SITE + "/"), ("Blog", BLOG + "/"), (p["title"], p["url"])])]
    if faq_ld:
        ld.append(faq_ld)
    head = (f'<meta property="article:published_time" content="{p["date"].isoformat()}">\n'
            f'<meta property="article:modified_time" content="{p["updated"].isoformat()}">\n'
            f'<meta property="article:author" content="{AUTHOR["name"]}">\n'
            f'<meta property="article:section" content="{html.escape(p["category"])}">\n')
    return page(title=p.get("seo_title", p["title"]) + " | Sublime Media", description=p["description"],
                canonical=p["url"], og_image=img, og_type="article", body=body, jsonld=ld, extra_head=head)


def card(p):
    return f"""<a class="bl-card" href="{p['path']}">
  <img src="/blog/{p['slug']}/{p['slug']}.jpg" alt="" width="1200" height="630" loading="lazy" decoding="async">
  <div><span>{html.escape(p['category'])} · {read_time(p['body_md'])} min read</span>
  <h3>{html.escape(p['title'])}</h3><p>{html.escape(p['description'])}</p>
  <time datetime="{p['date'].isoformat()}">{fmt_date(p['date'])}</time></div></a>"""


def index_html(posts):
    cats = sorted({p["category"] for p in posts})
    filters = "".join(f'<a href="#{slugify(c)}">{html.escape(c)}</a>' for c in cats)
    feat = posts[0] if posts else None
    sections = ""
    for c in cats:
        items = [p for p in posts[1:] if p["category"] == c]
        if not items:
            continue
        sections += (f'<section class="bl-cat" id="{slugify(c)}"><h2>{html.escape(c)}</h2>'
                     f'<div class="bl-grid">{"".join(card(p) for p in items)}</div></section>')
    feat_html = ""
    if feat:
        feat_html = f"""<a class="bl-feature" href="{feat['path']}">
      <img src="/blog/{feat['slug']}/{feat['slug']}.jpg" alt="" width="1200" height="630" fetchpriority="high">
      <div><span class="sm-pill"><i></i>Latest · {html.escape(feat['category'])}</span><h2>{html.escape(feat['title'])}</h2>
      <p>{html.escape(feat['description'])}</p><b>Read the article →</b></div></a>"""
    body = f"""
<section class="sm-page-hero bl-hero">
  <div class="container">
    <nav class="bl-crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span><span>Blog</span></nav>
    <h1>The Sublime <span class="shape-bg">Blog</span></h1>
    <p class="lead">Practical social media advice for brands and for the people who manage them. New posts every week.</p>
    <div class="bl-filters">{filters}</div>
  </div>
</section>
<div class="container bl-index">
  {feat_html}
  {sections}
  <div class="bl-cta"><h2>Get new posts on WhatsApp</h2><p>Join the free School of Social Media Managers community for weekly tips and new articles.</p><a class="btn btn-white" href="https://whatsapp.com/channel/0029Vb8ksPe3WHTZIuuEqK12">Join the channel →</a></div>
</div>"""
    ld = [{"@context": "https://schema.org", "@type": "Blog", "@id": BLOG + "/#blog", "name": "The Sublime Blog",
           "url": BLOG + "/", "publisher": ORG, "inLanguage": "en-NG",
           "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": p["url"],
                         "datePublished": p["date"].isoformat(), "author": {"@id": SITE + "/#zelia"}} for p in posts[:20]]},
          crumbs_ld([("Home", SITE + "/"), ("Blog", BLOG + "/")])]
    return page(title="Social Media Marketing Blog for Nigerian Brands & SMMs | Sublime Media",
                description="Practical social media marketing advice from Sublime Media: strategy, content, ads and careers in social media management, written for Nigeria and Africa.",
                canonical=BLOG + "/", og_image="/blog/img/og-blog.jpg", og_type="website", body=body, jsonld=ld)


def feed_xml(posts):
    items = "".join(f"""
  <item><title>{xesc(p['title'])}</title><link>{p['url']}</link><guid isPermaLink="true">{p['url']}</guid>
    <pubDate>{dt.datetime.combine(p['date'], dt.time(8, 0)).strftime('%a, %d %b %Y %H:%M:%S +0100')}</pubDate>
    <category>{xesc(p['category'])}</category><description>{xesc(p['description'])}</description></item>""" for p in posts[:30])
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>
  <title>The Sublime Blog</title><link>{BLOG}/</link><description>Practical social media advice for brands and social media managers.</description>
  <language>en-ng</language><atom:link href="{BLOG}/feed.xml" rel="self" type="application/rss+xml"/>{items}
</channel></rss>
"""


def sitemap_xml(posts):
    body = f"\n  <url><loc>{BLOG}/</loc><lastmod>{(posts[0]['updated'] if posts else TODAY).isoformat()}</lastmod></url>"
    for p in posts:
        imgs = [f"{BLOG}/{p['slug']}/{p['slug']}.jpg"] + [f"{BLOG}/{p['slug']}/{s['name']}.jpg" for s in p.get("images", [])]
        body += (f"\n  <url><loc>{p['url']}</loc><lastmod>{p['updated'].isoformat()}</lastmod>"
                 + "".join(f"<image:image><image:loc>{u}</image:loc></image:image>" for u in imgs) + "</url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            f'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">{body}\n</urlset>\n')


def main():
    global BUILD_V
    BUILD_V = TODAY.strftime("%Y%m%d")
    posts = load_posts()
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "img").mkdir(parents=True)
    shutil.copy(SRC / "blog.css", OUT / "blog.css")
    # author photo, resized
    Image.open(SRC / "zelia.jpg").convert("RGB").resize((176, 176)).save(OUT / "img" / "zelia.jpg", quality=85)
    cover({"category": "The Sublime Blog", "title": "Practical social media advice for brands and the people who run them"},
          OUT / "img" / "og-blog.jpg")
    for p in posts:
        d = OUT / p["slug"]
        d.mkdir(parents=True)
        cover(p, d / f"{p['slug']}.jpg")
        for spec in p.get("images", []):
            spec["_size"] = graphics.render(spec, SRC, d, p["category"])
        (d / "index.html").write_text(post_html(p, posts), encoding="utf-8")
    (OUT / "index.html").write_text(index_html(posts), encoding="utf-8")
    (OUT / "feed.xml").write_text(feed_xml(posts), encoding="utf-8")
    (OUT / "sitemap.xml").write_text(sitemap_xml(posts), encoding="utf-8")
    print(f"built {len(posts)} post(s) -> {OUT}")


if __name__ == "__main__":
    main()
