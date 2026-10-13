#!/bin/bash
# Runs on the web server (cPanel cron). Pulls the latest blog from GitHub
# and copies public/blog into the live site. Only touches public_html/blog.
set -e
REPO="$HOME/sublime-blog"
LIVE="$HOME/public_html/blog"
if [ ! -d "$REPO/.git" ]; then
  git clone --depth 1 https://github.com/sublimefilmslimited-source/sublime-blog.git "$REPO"
else
  git -C "$REPO" fetch --depth 1 origin main -q
  git -C "$REPO" reset --hard origin/main -q
fi
mkdir -p "$LIVE"
cp -R "$REPO/public/blog/." "$LIVE/"
