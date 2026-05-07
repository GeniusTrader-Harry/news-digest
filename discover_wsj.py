#!/usr/bin/env python3
"""Discover fresh WSJ article URLs by scraping wsj.com section pages.

Why this exists:
  WSJ's RSS feeds at feeds.a.dj.com periodically go stale (return only old
  articles from a fixed snapshot, e.g. all items dated January 2025). The
  feed-server caches/CDN don't reliably refresh. Section pages on wsj.com
  itself stay current and serve as a reliable URL-discovery mechanism.

Strategy:
  1. Fetch a list of WSJ section pages with curl_cffi (Chrome-131 TLS
     impersonation) + the user's session cookie — same approach as fetch_wsj.
  2. Parse each page's HTML for article URLs matching the WSJ slug patterns:
     /articles/<slug>, /finance/<sub>/<slug>, /business/<sub>/<slug>,
     /economy/<sub>/<slug>, /markets/<sub>/<slug>, /tech/<sub>/<slug>.
  3. De-duplicate, strip query strings (e.g. `?mod=...` tracking), and
     output one URL per line on stdout.

Output is consumed by the daily-brief routine which then passes the URLs
to fetch_wsj.sh to pull full article bodies.

Usage:
  discover_wsj.py                  # scrape default sections, print URLs
  discover_wsj.py --max 12         # limit total output to N URLs
  discover_wsj.py --section URL    # additional section page to scrape
                                   # (repeatable)
"""
import argparse
import re
import sys
from pathlib import Path

from curl_cffi import requests

HERE = Path(__file__).resolve().parent
COOKIE_FILE = HERE / "wsj_cookie.txt"

DEFAULT_SECTIONS = [
    "https://www.wsj.com/news/markets",
    "https://www.wsj.com/finance",
    "https://www.wsj.com/news/business",
    "https://www.wsj.com/news/economy",
]

# Match any wsj.com path that looks like an article slug.
# Examples:
#   https://www.wsj.com/articles/some-slug-abc123
#   https://www.wsj.com/finance/stocks/the-chip-craze-...
#   https://www.wsj.com/economy/jobs/layoffs-2026-tracker-...
# Capture broadly (up to the closing quote) and strip query strings later —
# WSJ adds ?mod=... tracking params to most internal links.
ARTICLE_RE = re.compile(
    r'href="(https://www\.wsj\.com/(?:articles|finance|business|economy|markets|tech|politics|world)/[^"]+)"'
)


def load_cookies() -> dict:
    if not COOKIE_FILE.exists():
        print(f"ERROR: {COOKIE_FILE} not found", file=sys.stderr)
        sys.exit(2)
    raw = COOKIE_FILE.read_text().strip()
    return {kv.split("=", 1)[0].strip(): kv.split("=", 1)[1]
            for kv in raw.split(";") if "=" in kv}


def discover(sections: list, cookies: dict) -> list:
    seen = []
    for url in sections:
        try:
            r = requests.get(url, impersonate="chrome131", cookies=cookies, timeout=20)
        except Exception as e:
            print(f"WARN: {url}: {e}", file=sys.stderr)
            continue
        if r.status_code != 200:
            print(f"WARN: {url}: HTTP {r.status_code}", file=sys.stderr)
            continue
        for raw in ARTICLE_RE.findall(r.text):
            # Strip query string (?mod=...) and fragment (#...)
            clean = raw.split("?", 1)[0].split("#", 1)[0]
            # Skip URLs that look like section indices, not articles
            tail = clean.rsplit("/", 1)[-1]
            if "-" not in tail:
                continue
            if clean not in seen:
                seen.append(clean)
    return seen


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=20,
                   help="Limit total output to N URLs (default 20)")
    p.add_argument("--section", action="append", default=[],
                   help="Additional section URL to scrape (repeatable)")
    args = p.parse_args()

    cookies = load_cookies()
    sections = DEFAULT_SECTIONS + args.section
    urls = discover(sections, cookies)[: args.max]

    if not urls:
        print("ERROR: no article URLs discovered. Check WSJ cookie or section URLs.",
              file=sys.stderr)
        return 1

    for u in urls:
        print(u)
    return 0


if __name__ == "__main__":
    sys.exit(main())
