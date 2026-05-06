# news-digest

> A Claude Code routine that delivers a curated daily markets briefing to Telegram every morning. Built for finance-recruiting prep — customisable for any beat.

## What you get

Every morning at the time you set, a Telegram message arrives with:

- **Market in 60 seconds** — the defining story + overnight tone + key levels (S&P, FTSE, DXY, 10Y)
- **3–7 stories** across Macro & rates · Equities · M&A — each with a 2–3 sentence summary, a one-sentence interview hook, and a `[⏣ Theme]` tag for narrative continuity across days
- **Earnings mini-section** auto-prepended during peak earnings weeks
- **One thing to read deeper** — a single longer-form piece selected by an explicit four-point rubric (or honestly skipped if nothing meets the bar)
- **🎯 View-forming question** — one controversial question forced by today's stories, designed to make you take a position

Sources are tiered: **FT** (primary, full-body via curl_cffi-based paywall bypass) · **WSJ** (peer, same approach) · **Reuters** (breaking-facts backstop) · **CNBC + central banks** (aggregator/event-only). Bloomberg is skipped — its bot-protection blocks the fetcher (see [SETUP.md](SETUP.md#bloomberg)).

A real example brief lives in [examples/sample-brief.md](examples/sample-brief.md).

## How it works

```
                          ┌─────────────────────────┐
  cron 11:08 daily  ─────▶│ Claude Code scheduled   │
  (your machine)          │ task reads routine-     │
                          │ prompt.md and runs      │
                          └────────────┬────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        ▼                              ▼                              ▼
   FT RSS feeds              WSJ RSS feeds               Reuters / CNBC / CB pages
   triage → fetch_ft.sh      triage → fetch_wsj.sh       direct WebFetch
   (curl_cffi + cookie)      (curl_cffi + cookie)
        │                              │                              │
        └──────────────────────────────┼──────────────────────────────┘
                                       ▼
                          Synthesis (theme-tagged stories,
                          interview hooks, view question)
                                       │
                                       ▼
                          send_telegram.sh → Telegram bot → your chat
                                       │
                                       ▼
                                 archive/YYYY-MM-DD.md
```

## Quick install

**Prerequisites**: macOS · [Claude Code](https://claude.com/claude-code) 2.x · Python 3.9+ · a Telegram account.

```bash
# 1. Clone
git clone https://github.com/GeniusTrader-Harry/news-digest.git ~/news-digest
cd ~/news-digest

# 2. Install Python deps
python3 -m venv venv
source venv/bin/activate
pip install curl_cffi

# 3. Open with Claude Code and invoke the setup skill
#    (it walks you through Telegram bot creation, cookie export,
#     scheduled task registration, and trust dialog)
claude code .
# then in Claude:  /news-digest-setup
```

The setup skill is the recommended path — it interactively walks you through the manual bits (Telegram BotFather, FT/WSJ cookie export from Chrome, `pmset` wake schedule, Claude Code permission allowlist, scheduled task registration). For a non-interactive walkthrough see **[SETUP.md](SETUP.md)**.

## Customisation

The published prompt is opinionated: finance / S&T / ER recruiting framing, US-anchored UK-weighted geography, themes like *AI capex* / *Term premium* / *UK fiscal*. **All of this is meant to be tuned for your beat.** See **[CUSTOMISATION.md](CUSTOMISATION.md)** for how to swap:

- The audience framing (line 1 of [routine-prompt.md](routine-prompt.md))
- Geography weighting
- Theme dictionary
- Section sizes (Macro / Equities / M&A counts)
- Sources (add/remove outlets)
- The view-forming question style

## What's in this repo

| File | Role |
|---|---|
| [routine-prompt.md](routine-prompt.md) | The prompt the scheduled task runs every day. Templated — replace `<USER_NAME>` and `<PROJECT_DIR>` during setup. |
| [send_telegram.sh](send_telegram.sh) | Reads `.env`, chunks brief into ≤3800-char messages, POSTs to Telegram Bot API. Falls back to plain-text if Markdown parsing fails. |
| [fetch_ft.py](fetch_ft.py) / [fetch_ft.sh](fetch_ft.sh) | FT article fetcher: `curl_cffi` Chrome-131 TLS impersonation + your session cookie → JSON-LD body extraction → clean markdown. |
| [fetch_wsj.py](fetch_wsj.py) / [fetch_wsj.sh](fetch_wsj.sh) | WSJ fetcher: same TLS approach + hybrid extraction (JSON-LD metadata + `<p data-type="paragraph">` regex with style-block stripping). |
| [skills/news-digest-setup/SKILL.md](skills/news-digest-setup/SKILL.md) | Interactive Claude Code skill that walks you through full setup. Invoke with `/news-digest-setup`. |
| [examples/sample-brief.md](examples/sample-brief.md) | A real morning brief — shows what you'll get. |
| [.env.example](.env.example) | Template for Telegram credentials. Copy to `.env`, fill in. |

## Why this exists

Most "AI news digest" tools either (a) regurgitate Reddit/Twitter, or (b) summarise headlines you've already seen, badly. This routine flips it: **subscriber-grade primary sources** (FT, WSJ) with **explicit editorial rules** (theme tagging for cross-day continuity, sourcing priority FT > WSJ > Reuters, no-claim-without-source, view-forming question to make you actually take positions). It's designed for someone who reads the news for a reason — recruiting, trading, research — not just ambient awareness.

The opinionated bits are the value. Fork it, tune it for your beat.

## Limitations and honest caveats

- **Mac-only as written**: relies on `pmset` for daily-wake. Linux/Windows users would adapt the schedule mechanism.
- **Laptop-bound**: Claude Code scheduled tasks run on your machine. If your Mac is off at the fire time, the run is missed. Worth solving with Login Items + lid-closed-but-charging.
- **Cookie maintenance**: FT and WSJ session cookies expire every 2–4 weeks. The brief detects expiry (`⚠️ cookie may need refresh`) — re-export from Chrome takes ~30 seconds.
- **Bloomberg is excluded**: PerimeterX bot-protection defeats `curl_cffi` even with valid cookies. Read Bloomberg directly in your browser. Possible future work: Playwright with dedicated logged-in profile (~60–90 min setup, not built).
- **Quality varies with model**: routine targets Claude Code's high-effort mode. Lower-effort runs produce blander hooks.

## Contributing

Fork it, tune it, share it back. Issues and PRs welcome — particularly:
- Linux/Windows wake-schedule equivalents
- Other paywalled outlets people have working fetchers for (Economist, Barron's, etc.)
- Theme dictionaries for non-finance beats (climate, biotech, geopolitics, etc.)

## License

MIT — see [LICENSE](LICENSE).

---

Built with [Claude Code](https://claude.com/claude-code).
