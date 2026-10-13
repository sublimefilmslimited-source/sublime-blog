# Sublime Media blog

Weekly blog for https://www.sublimemedialimited.com/blog/

- `posts/` — one Markdown file per post (front matter: title, description, date, category, keyword, faq…)
- `build.py` — turns posts into the static site in `public/blog/` (pages, cover images, RSS, sitemap)
- `deploy.sh` — run by a cPanel cron job; copies `public/blog/` into `public_html/blog/`

A post dated in the future stays hidden until its date. Set `draft: true` to hold a post back.
