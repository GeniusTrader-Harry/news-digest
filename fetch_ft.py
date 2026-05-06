#!/usr/bin/env python3
"""Fetch FT article(s) by URL, bypass Cloudflare via curl_cffi Chrome impersonation,
extract structured content from JSON-LD, output as markdown to stdout.

Usage:
  fetch_ft.py URL [URL ...]

Reads cookies from ./ft_cookie.txt (next to this script). If a fetch returns a
login/paywall page, prints an error and continues with remaining URLs.
"""
import json
import re
import sys
import time
from pathlib import Path
from typing import Optional

from curl_cffi import requests

HERE = Path(__file__).resolve().parent
COOKIE_FILE = HERE / "ft_cookie.txt"


def load_cookies() -> dict:
    if not COOKIE_FILE.exists():
        print(f"ERROR: {COOKIE_FILE} not found", file=sys.stderr)
        sys.exit(2)
    raw = COOKIE_FILE.read_text().strip()
    cookies = {}
    for kv in raw.split(";"):
        if "=" in kv:
            k, _, v = kv.partition("=")
            cookies[k.strip()] = v
    return cookies


def extract_news_article(html: str) -> Optional[dict]:
    """Pull the NewsArticle JSON-LD block, if present."""
    for raw in re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL
    ):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and data.get("@type") == "NewsArticle":
            return data
    return None


def author_name(author_field) -> str:
    if isinstance(author_field, list) and author_field:
        author_field = author_field[0]
    if isinstance(author_field, dict):
        return author_field.get("name", "")
    if isinstance(author_field, str):
        return author_field
    return ""


def fetch_one(url: str, cookies: dict) -> str:
    try:
        r = requests.get(url, impersonate="chrome131", cookies=cookies, timeout=25)
    except Exception as e:
        return f"## ERROR: fetch failed for {url}\n\n{e}\n"

    if r.status_code != 200:
        return (
            f"## ERROR: HTTP {r.status_code} for {url}\n\n"
            f"Likely Cloudflare challenge (cookie may need refresh).\n"
        )

    # Detect login/auth-redirect pages
    title_match = re.search(r"<title[^>]*>([^<]*)</title>", r.text)
    title = (title_match.group(1) if title_match else "").strip()
    if (
        "Security Verification" in title
        or "Sign in" in title and "Financial Times" in title
        or "Subscribe to read" in r.text[:30000]
    ):
        return (
            f"## ERROR: paywall/login page returned for {url}\n\n"
            f"Title was: {title}. Cookie has likely expired — re-export from "
            f"Chrome and overwrite ft_cookie.txt.\n"
        )

    article = extract_news_article(r.text)
    if not article:
        return (
            f"## ERROR: no NewsArticle JSON-LD found for {url}\n\n"
            f"Page title: {title}. Page structure may have changed.\n"
        )

    headline = article.get("headline", title) or "(no headline)"
    description = article.get("description", "") or ""
    body = article.get("articleBody", "") or ""
    author = author_name(article.get("author"))
    published = article.get("datePublished", "")[:10]

    parts = [f"## {headline}"]
    byline_bits = [b for b in (author, published) if b]
    if byline_bits:
        parts.append(f"_FT · { ' · '.join(byline_bits) }_")
    if description:
        parts.append(f"**{description}**")
    if body:
        parts.append(body)
    parts.append(f"🔗 {url}")
    return "\n\n".join(parts) + "\n"


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: fetch_ft.py URL [URL ...]", file=sys.stderr)
        return 1
    cookies = load_cookies()
    urls = sys.argv[1:]
    chunks = []
    for i, url in enumerate(urls):
        if i:
            time.sleep(0.5)
        chunks.append(fetch_one(url, cookies))
    print("\n---\n\n".join(chunks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
