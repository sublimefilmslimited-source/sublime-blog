# Sublime Media blog — weekly post brief

This repo publishes https://www.sublimemedialimited.com/blog/. A cPanel cron job on the
web server copies `public/blog/` from the `main` branch into the live site at minute :07
of every hour. **Whatever is pushed to `main` goes live within the hour.**

## Weekly job (every Monday)
1. Read `TOPICS.md`. Pick the first unchecked topic, unless a clearly better, timely topic
   exists (e.g. a major Meta/Instagram/TikTok change). Alternate audiences week to week:
   aspiring/working social media managers (cta: school) and business owners (cta: agency).
2. Research before writing (WebSearch): what currently ranks for the keyword, what people
   ask, and any platform facts you state. Only state facts you have checked this week.
3. Write `posts/YYYY-MM-DD-<slug>.md` dated today (front matter format: copy the newest post).
4. `python3 build.py` (needs: pip install --break-system-packages markdown pyyaml pillow fonttools) and fix any warning. Check the output HTML renders (headings, FAQ, links).
5. Tick the topic in `TOPICS.md` (add the URL), commit, `git push origin main`.
6. Tell the owner (Zelia) the title, the link, and one line on why that topic.

## Writing rules
- Reader: Nigerian (and wider African) audience. Plain, warm, confident English, short
  sentences, no jargon without a one-line explanation. British spelling (organise, colour).
- 1,300–2,200 words. Start with a `<div class="tldr" markdown="1">` "In short" answer
  (2–4 sentences) that directly answers the search query.
- One H1 (the title, auto). H2s that mirror real search questions; H3s only when needed.
- Practical: steps, checklists, examples, scripts/templates, tables where they help.
- Use Nigerian context naturally (Lagos/Abuja businesses, naira ₦, WhatsApp, NYSC, Instagram-first
  commerce). Never invent statistics, client results, quotes or testimonials. Real Sublime
  results you may cite: grew the Ilorin Emirate Mall account from 0 to 13K followers in 3 months.
- First person plural ("we", Sublime Media / the School) is fine; Zelia is the author.
- Never mention AI writing the post.

## Images (every post) — for Google Images
- Add 3–4 original infographics via front matter `images:` (types: steps, checklist, table, chat;
  see graphics.py and the first post for the format) and place each with `{{image:<name>}}`
  right after the paragraph it illustrates.
- `name`: keyword-rich, hyphenated, unique (e.g. instagram-content-calendar-template).
- `alt`: describe exactly what the image shows, using the topic naturally (no keyword stuffing).
- `caption`: one helpful sentence. Keep item text short (one line label + short detail).
- Images get WebP + JPG, width/height, ImageObject schema and an image sitemap automatically.

## SEO checklist (every post)
- `keyword`: one primary search phrase with real intent; put it in the title, the
  description, the first 100 words, one H2 and the slug. 3–6 related `keywords`.
- `seo_title` ≤ 60 chars; `description` 140–155 chars, includes keyword + benefit.
- Slug: short, lowercase, hyphens, keyword-based, no dates/stop-word clutter.
- 3–5 FAQ items (front matter `faq`) answering real "People also ask" questions; answers
  40–80 words, standalone.
- Internal links (relative): at least 2 to products/pages (/course, /ebook, /starter-kit,
  /school, /#services, /#contact) and 1–2 to earlier blog posts when relevant.
- 1–3 external links to authoritative sources (Meta, TikTok, Google, official stats).
- `cover_title`: short version of the title (≤ 60 chars) for the cover image.

## Products & links (do not change prices without the owner)
- Course "Social Media Management Mastery" — Udemy only: /course (page), /school#catalog
- E-book "Social Media Management Mastery" — ₦10,000 on Selar: /ebook
- "The Social Media Manager Starter Kit" — ₦10,000 on Selar, 50+ templates: /starter-kit
- Affiliate programme: /affiliate/ (20% on e-book and starter kit only)
- Agency services & contact: /#services, /#contact; WhatsApp community:
  https://whatsapp.com/channel/0029Vb8ksPe3WHTZIuuEqK12
