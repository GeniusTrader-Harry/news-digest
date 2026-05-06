#!/usr/bin/env python3
"""Fetch WSJ article(s) by URL, bypass Cloudflare/Datadome via curl_cffi Chrome
impersonation, extract metadata from JSON-LD and body from <p data-type="paragraph">
tags, output as markdown to stdout.

Usage:
  fetch_wsj.py URL [URL ...]

Reads cookies from ./wsj_cookie.txt (next to this script). If a fetch returns a
login/paywall page, prints an error and continues with remaining URLs.
"""
import html
import json
import re
import sys
import time
from pathlib import Path
from typing import Optional

from curl_cffi import requests

HERE = Path(__file__).resolve().parent
COOKIE_FILE = HERE / "wsj_cookie.txt"


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


def extract_news_metadata(text: str) -> Optional[dict]:
    """Pull headline/description/author/date from a NewsArticle JSON-LD block."""
    for raw in re.findall(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
        text, re.DOTALL,
    ):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        candidates = data if isinstance(data, list) else [data]
        for item in candidates:
            if isinstance(item, dict) and item.get("@type") in (
                "NewsArticle", "Article", "ReportageNewsArticle",
            ):
                return item
    return None


def extract_body_paragraphs(text: str) -> str:
    """WSJ stores body in <p data-type="paragraph"> tags. Strip <style>/<script>
    blocks first since WSJ embeds CSS-in-JS inside paragraphs for styled links."""
    cleaned_html = re.sub(
        r"<(style|script)\b[^>]*>.*?</\1>", "", text, flags=re.DOTALL | re.IGNORECASE
    )
    paras = re.findall(
        r'<p[^>]*data-type="paragraph"[^>]*>(.*?)</p>',
        cleaned_html, re.DOTALL,
    )
    cleaned = []
    for p in paras:
        # Strip remaining HTML tags (links, em, etc.) but preserve text
        stripped = re.sub(r"<[^>]+>", "", p).strip()
        stripped = html.unescape(stripped)
        # Drop any leftover CSS-class noise that escaped <style> stripping
        stripped = re.sub(r"\.css-[a-z0-9-]+\{[^}]*\}", "", stripped)
        stripped = re.sub(r"@media[^{]*\{[^}]*\}", "", stripped)
        stripped = re.sub(r"\s+", " ", stripped).strip()
        if len(stripped) >= 30:
            cleaned.append(stripped)
    return "\n\n".join(cleaned)


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
            f"Likely Cloudflare/Datadome challenge or expired session "
            f"(cookie may need refresh).\n"
        )

    title_match = re.search(r"<title[^>]*>([^<]*)</title>", r.text)
    title = (title_match.group(1) if title_match else "").strip()
    if (
        "Verifying you are human" in r.text[:30000]
        or "Are you a robot" in title
        or "Sign In" in title and "WSJ" in title
    ):
        return (
            f"## ERROR: bot/login page returned for {url}\n\n"
            f"Title was: {title}. Cookie has likely expired — re-export from "
            f"Chrome and overwrite wsj_cookie.txt.\n"
        )

    meta = extract_news_metadata(r.text)
    if not meta:
        return (
            f"## ERROR: no NewsArticle JSON-LD found for {url}\n\n"
            f"Page title: {title}. WSJ page structure may have changed.\n"
        )

    body = extract_body_paragraphs(r.text)
    if not body:
        return (
            f"## ERROR: article body extraction returned empty for {url}\n\n"
            f"WSJ may have changed paragraph markup. Headline was: "
            f"{meta.get('headline','')}\n"
        )

    headline = meta.get("headline", title) or "(no headline)"
    description = (meta.get("description") or "").strip()
    author = author_name(meta.get("author"))
    published = (meta.get("datePublished") or "")[:10]

    parts = [f"## {headline}"]
    byline_bits = [b for b in (author, published) if b]
    if byline_bits:
        parts.append(f"_WSJ · { ' · '.join(byline_bits) }_")
    if description:
        parts.append(f"**{description}**")
    parts.append(body)
    parts.append(f"🔗 {url}")
    return "\n\n".join(parts) + "\n"


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: fetch_wsj.py URL [URL ...]", file=sys.stderr)
        return 1
    cookies = load_cookies()
    chunks = []
    for i, url in enumerate(sys.argv[1:]):
        if i:
            time.sleep(0.5)
        chunks.append(fetch_one(url, cookies))
    print("\n---\n\n".join(chunks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
