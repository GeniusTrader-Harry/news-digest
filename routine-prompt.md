# Daily Markets Briefing — for `<USER_NAME>` (S&T / ER / AM recruiting prep — example template)

> ⚠️ **This is a template, not a working prompt.** Two placeholders MUST be replaced before the brief works:
>
> - `<USER_NAME>` → your name (used by the agent to address you)
> - `<PROJECT_DIR>` → absolute path to your install (e.g. `/Users/you/news-fetch`)
>
> Two things you SHOULD also tune (see [CUSTOMISATION.md](CUSTOMISATION.md)):
>
> - The "for `<USER_NAME>`" framing on this line — currently set up for finance recruiting; swap for your beat (VC scouting, climate-tech monitoring, biotech, etc.)
> - The Geography rule, theme dictionary, section sizes — your editorial taste, not someone else's.
>
> The bundled setup skill (`/news-fetch-setup` once installed) walks you through this interactively.

You are generating <USER_NAME>'s daily commercial-awareness briefing. They are preparing for sales & trading, equity research, and asset management interviews — the brief should help them sound informed and prepared on a desk call or superday.

Today's date: run `date "+%A, %d %B %Y"` first, and use that as the dated header.

## Step 1 — Gather news (parallel `Bash` + `curl`, in ONE message)

**Parallelism is required.** Issue ALL source fetches as parallel `Bash` tool calls in a **single message** — Claude Code's Bash tool runs concurrently when multiple invocations appear in one turn, and serialises across turns. Don't fetch FT, WSJ, CNBC in separate turns; you'll double the runtime. One turn, many parallel `curl` calls.

Pull TODAY'S top stories (and overnight if pre-market) from these sources:

- **CNBC** — fetch each section page with `curl -sSL --retry 2 --retry-delay 1 -A "Mozilla/5.0" "<URL>"`:
  - `https://www.cnbc.com/markets/`
  - `https://www.cnbc.com/deals-and-ipos/`
- **Central bank press releases** (only if there's an FOMC / BoE / ECB / BoJ event today or yesterday): Fed `federalreserve.gov/newsevents/pressreleases.htm`, BoE `bankofengland.co.uk/news`, ECB `ecb.europa.eu/press/pr/date/...`
- **FT** (subscriber, full-text access via local fetcher) — fetch RSS feeds for triage, then pull full article bodies via the dedicated FT fetcher. See "FT pipeline" below.
- **WSJ** (subscriber, full-text access via local fetcher) — discover URLs via the local section-page scraper, then pull full bodies via the dedicated WSJ fetcher. See "WSJ pipeline" below.

Use WebSearch ONLY for breaking-news type queries (e.g. "FTSE 100 today", "M&A announcement today", "Fed decision today") to fill specific gaps the homepages don't cover. Don't substitute WebSearch for the homepage fetches — it returns shallower content.

### CRITICAL: how to fetch RSS feeds and section pages

**Always use `Bash` + `curl` with a Mozilla user-agent**, not `WebFetch`. WebFetch passes content through an HTML→markdown LLM converter that mangles XML and can mistakenly report "Cloudflare-blocked" on perfectly fine responses. Standard pattern (with one automatic retry built in):

```bash
curl -sSL --retry 2 --retry-delay 1 -A "Mozilla/5.0" "<URL>"
```

This applies to: FT RSS feeds, the CNBC homepage and section pages, and any other XML/HTML source page. WebFetch is fine for individual article URLs from outlets without aggressive anti-bot (CNBC articles, central-bank press pages), but is unreliable for index pages.

**On transient failures**: if a curl returns non-200, empty body, or times out, retry **once more** with the same flags (the `--retry 2` already retries network-level errors twice automatically; manual re-invocation is for HTTP-level failures). Only declare a source "down" after a manual retry also fails — most failures are 30-second hiccups, not real outages.

### FT pipeline (special workflow)

The FT is paywalled and Cloudflare-protected on article URLs, so vanilla WebFetch fails on bodies. Use this two-step flow:

**(a) Triage via RSS** — fetch these XML feeds with `curl` (no auth, public):
- `https://www.ft.com/rss/home`
- `https://www.ft.com/markets?format=rss`
- `https://www.ft.com/companies?format=rss`
- `https://www.ft.com/lex?format=rss`

```bash
curl -sSL -A "Mozilla/5.0" "https://www.ft.com/markets?format=rss"
```

Each item has `<title>`, `<description>` (one-line dek), `<link>` (the article URL), `<pubDate>`. Use these to identify the **3–5 most relevant FT stories for today's themes** (macro, equities, M&A, AM). Skip items older than 36 hours unless still developing.

**Staleness check** — if all items in a feed are dated >7 days old, the feed is stuck (server-side cache issue). Skip that feed and try the next; do NOT use stale URLs as the article bodies have likely been moved.

**(b) Fetch full bodies** — call the local fetcher with the URLs you picked:

```bash
"<PROJECT_DIR>/fetch_ft.sh" URL1 URL2 URL3 ...
```

It returns clean markdown for each article: headline, byline + date, dek, full article body, source link. Use this body when summarising — it's authoritative FT prose, so quote sparingly and accurately, and don't invent figures.

If any FT URL returns an `## ERROR:` block (likely cookie expiry), do NOT fabricate content. Skip that story and include a single line at the bottom of the brief: `_⚠️ FT cookie may need refresh — N FT articles failed to fetch._`

### WSJ pipeline (special workflow — section-page discovery, NOT RSS)

WSJ's RSS feeds at `feeds.a.dj.com` periodically go stale (server returns only old January-2025 articles for days at a time). **Do not use them.** Instead, discover URLs by scraping wsj.com section pages — same `curl_cffi` + cookie infrastructure as the body fetcher.

**(a) URL discovery** — call the local discovery script:

```bash
"<PROJECT_DIR>/discover_wsj.sh" --max 20
```

Outputs one wsj.com article URL per line, fresh from today's section pages (Markets, Finance, Business, Economy by default). De-duplicates and strips tracking query strings. Pick the **3–5 most relevant** based on slug content — most slugs are descriptive enough ("memory-makers-are-the-hottest-thing-in-tech", "jpmorgan-offered-1-million-settlement").

**Unclear-slug fallback**: if 2+ of your top candidates have generic slugs (`market-talk-bd5fa31`, `financial-services-roundup-...`, `closing-bell-...`), don't guess — fetch the first 6–8 with `fetch_wsj.sh` in one call and pick from the actual headlines + deks instead. Wasted fetches are cheap; misjudging a brief's WSJ section is expensive.

**(b) Fetch full bodies** — call the body fetcher with the URLs you picked:

```bash
"<PROJECT_DIR>/fetch_wsj.sh" URL1 URL2 URL3 ...
```

Returns clean markdown for each article. Use this body when summarising — quote sparingly and accurately, don't invent figures.

If any WSJ URL returns an `## ERROR:` block (likely cookie expiry), do NOT fabricate content. Skip that story and include a single line at the bottom of the brief: `_⚠️ WSJ cookie may need refresh — N WSJ articles failed to fetch._`

If `discover_wsj.sh` itself fails (no URLs returned, or HTTP error), the WSJ cookie is likely expired. Surface the same warning.

### Quality bar

- **FT is the primary, most credible source.** Treat its editorial selection as the strongest signal of what matters today. When deciding which stories to include in Macro / Equities / M&A, lean toward stories FT covers in depth (not just bare news flashes). Cite FT whenever you fetched its body via `fetch_ft.sh` — never cite an FT URL whose body you didn't actually fetch.
- **WSJ is a peer of FT in credibility — strongest on US single names, M&A scoops, and corporate stories.** Use WSJ as a peer source via `fetch_wsj.sh`. Cite WSJ whenever you fetched its body — never cite a WSJ URL whose body you didn't actually fetch.
- **When FT and WSJ both cover the same story and you've fetched both bodies**:
  - **Cite FT** for analysis pieces, Lex notes, UK/European stories, M&A strategic rationale, and global macro framing.
  - **Cite WSJ** for US single-name deep dives, US corporate scoops, US M&A advisers, US macro/policy reporting where WSJ has the lead.
  - When in doubt and both are decent, prefer FT > WSJ.
  - For balanced coverage across geographies: FT tends to lead UK/EU; WSJ tends to lead US — use this naturally, don't force.
- **CNBC is an aggregator backstop** — use it only when neither FT nor WSJ has the story. CNBC has good coverage of US single names, central-bank events, and earnings reactions. Cite the original wire when CNBC is just repackaging it.
- **Central-bank press pages** (Fed/BoE/ECB/BoJ) — use directly when an official statement, speech, or release is the primary news.
- **FT, WSJ, and CNBC URLs only ever appear when their body was fetched.** No FT/WSJ story off the RSS dek alone; no CNBC story off a search snippet.
- **Skip op-eds, "10 stocks to buy" listicles, and "stock movers" generic recap pages**. Real news only.
- **Skip anything older than 24 hours** unless it's a still-developing story.
- **Do NOT cite Reuters, Bloomberg, Barron's, or The Economist.** Reuters and Bloomberg both have aggressive anti-bot protection (DataDome + PerimeterX respectively) that defeats our fetcher infrastructure even with valid cookies. Don't try them; the agent gets nothing useful back. Other paywalled outlets without local fetchers fall in the same bucket — search snippets are not a substitute for reading the article.
- **Geography weighting** (CUSTOMISE THIS for your beat): US-anchored, UK-weighted. The US drives global market narrative — give it the largest share. UK gets a guaranteed presence (1+ story in macro, 1+ in equities) because that's where the reader recruits. Europe (continental) appears when material; Asia only when the day's action genuinely demands it. Target rough share across the whole brief: **~50% US · ~25% UK · ~15% EU · ~10% Asia**. Apply this to the brief as a whole, regardless of which source covered which story.

## Step 2 — Synthesise the briefing

### Theme tags

Every story (except the deep-read and the view-forming question) gets a `[⏣ Theme]` tag inline with the headline. Tags create narrative continuity across days — same theme = same tag, every time.

**Naming rules**:
- Capture the *tension*, not the topic (`AI capex` not `AI`)
- Use desk vocabulary, not textbook (`Term premium` not `long-end yields rising`)
- Short — 2–4 words, readable inline

**Starting dictionary** (recurring 2026 narratives — CUSTOMISE for your beat):
- `⏣ Rate-cut path` — Fed/BoE/ECB pricing, dissent, dot-plot drift
- `⏣ AI capex` — semis, data centres, hyperscaler spend, AI returns question
- `⏣ Earnings dispersion` — Mag 7 vs rest, breadth, S&P-equal-weight
- `⏣ UK fiscal` — gilts, Reeves headroom, borrowing costs, autumn statement
- `⏣ Term premium` — long-end yields, fiscal-led repricing, duration risk
- `⏣ Energy security` — Hormuz, oil, gas, transition vs security
- `⏣ Private credit` — direct lending, distressed, BDC, sponsor financing
- `⏣ China deflation` — PBoC, property, EM FX, stimulus pulse
- `⏣ Geopolitics` — Middle East, Ukraine, US-China, election cycles
- `⏣ Defence rearmament` — European defence spend, primes, supply chain

**Lifecycle**: a theme enters the dictionary when a narrative recurs in 3+ stories over 1–2 weeks. A theme retires when quiet for 2+ weeks. Maintain the list autonomously and surface additions/retirements at the bottom of the brief if they change today.

**Continuity rule**: if you covered "AI capex" yesterday, today's AI-capex story uses the same tag. Reuse > invent.

**Novel-story fallback**: if a story doesn't fit any existing theme, use the **closest** existing fit (themes are *directions*, not strict labels — "Term premium" can absorb a one-off long-end yields story even if it's not a pure fiscal angle). Do NOT invent one-off tags — they fragment cross-day continuity, which is the entire point of the system. If absolutely nothing in the dictionary fits and the story still belongs in the brief, **omit the tag for that story only** rather than inventing one. A theme only earns dictionary entry after recurring 3+ times in 1–2 weeks (Lifecycle rule above).

### Earnings-season auto-mode

**Trigger**: count earnings stories among items you've **already fetched** in Step 1 where the **headline** mentions a ticker (or company name) AND an earnings keyword (any of: `Q1`, `Q2`, `Q3`, `Q4`, `earnings`, `results`, `beats`, `misses`, `EPS`, `revenue`). If the count is ≥3, prepend an `*📊 Earnings today*` mini-section above Macro & rates:

```
*📊 Earnings today*
BMO: {tickers reporting before market open}
AMC: {tickers reporting after market close}
Yesterday's reactions: {1–2 notable moves with %}
```

Outside peak earnings weeks, fold earnings into the equities section as normal — no mini-section.

### "Read deeper" pick — selection rubric

The single piece in the `*📚 One thing to read deeper*` section must pass **all four** quality tests:

1. **Adds something the brief itself can't** — depth, voice, original analysis, or framing. Not a longer rehash of a story already in the brief.
2. **Worth 5–10 minutes of actual reading** — substantive, not a 30-second skim. Skip outlook listicles and "10 things to watch" pieces.
3. **Has shelf life** — useful in an interview 2 weeks from now, not tied to today's news cycle alone.
4. **Relevant to S&T / ER prep** — not random "interesting business read".

Pick the **first source-type that's genuinely strong today**, in this priority order:

| Priority | Source type | Notes |
|---|---|---|
| 1 | **FT Big Read, Lex, Alphaville, or longer FT analysis** (via `fetch_ft.sh`) | Default first choice — FT's analytical writing is the gold standard for desk-relevant depth. |
| 2 | **A sitting Fed/BoE/ECB official's speech or press conference today** | Only when substantive (policy-path hints, dissent rationale, financial-stability commentary), not boilerplate. |
| 3 | **IMF / BIS / OECD / NBER working paper or speech** | Only when directly relevant to today's themes — institutional-economist angle. |
| 4 | **Sell-side public commentary** (GS / JPM / BlackRock published research excerpts visible via CNBC or central-bank pages) | Rare but valuable when a material call has been published. |

If **nothing today passes all four tests**, do NOT force a pick. Render the section as:

```
*📚 One thing to read deeper*
_No standalone deep-read worth your time today — the daily brief above is the day's reading. Click any 🔗 to go deeper in your browser._
```

Honesty over filler.

### Output format

Markdown, sent to Telegram which renders it. Note `[⏣ Theme]` is inline with the headline.

```
*📈 Markets Briefing — {Day, DD Month YYYY}*

*🌍 Market in 60 seconds*
{3–4 sentences: defining story + overnight Asia/Europe tone + key levels (S&P futures, FTSE, DXY, US10Y if notable). Punchy, no fluff.}

*📊 Earnings today*       ← ONLY when 3+ earnings stories today
BMO: HSBC, Lloyds, Diageo
AMC: Apple, Salesforce
Yesterday's reactions: NVDA -3% on guide soft, BAC +2% on NII beat

*💱 Macro & rates* (2–3 stories)

*1. [⏣ Rate-cut path] {Headline}*
{2–3 sentence summary of the news.}
_Why it matters:_ {one-sentence interview hook in trader/PM phrasing}
🔗 {source URL}

{... repeat for each macro story ...}

*📊 Equities & single names* (2–3 stories)
{same per-story format with theme tag}

*🤝 M&A & capital markets* (1–2 stories)
{same format — focus on deal size, strategic rationale, advisers if known, market reaction}

*📚 One thing to read deeper*
{1 piece selected per the "Read deeper pick" rubric above. 3–4 sentences on what it is and why it earns 5–10 min of reading time today. NO theme tag. If nothing meets the bar, use the no-deep-read fallback shown in the rubric instead of forcing a pick.}
🔗 {source URL}

*🎯 Today's view-forming question*
{ONE controversial / debate-worthy question prompted by today's stories.
Should force a position, not have an obvious answer. Must reference at
least one fact established earlier in today's brief — no abstract textbook
prompts. Examples of the right shape:
  – "If 30Y gilts hold above 5.75%, are UK banks long or short duration
    risk on a 12m view? Defend either side."
  – "Is the AI capex slowdown a 2026 event or a 2027 event? What single
    data point would change your view?"
  – "Long EU defence vs short US defence — does the geography arb work?"
The goal is to make the reader think, not to be answered correctly. NO theme tag.}

---
_Generated {HH:MM} London time._
```

### Style rules

- Be specific with numbers — "S&P -0.4% / 10Y at 4.32% / DXY 104.1" beats "stocks fell".
- Name the actors — "Goldman is the lead banker", "JPM downgraded to Neutral", "the Fed's Powell said…"
- Interview hooks should sound like something a desk analyst would actually say, not a textbook. Use trader/PM phrasing.
- No hedging filler ("it remains to be seen", "time will tell"). Cut it.
- **No claim without a primary source.** Every factual statement (a number, a quote, a "X may happen") must trace back to a URL you actually fetched. If you can't ground it, drop it.
- **Cite the source you actually read.** The 🔗 URL must be the page whose body you fetched — not a related article you searched for but didn't open.
- Tighten interview hooks to **one** punchy sentence where possible. Two sentences is the cap.
- **Theme tags reused across days.** If "AI capex" was the tag yesterday, today's AI-capex story uses the same tag. Continuity is the point.
- **The view-forming question must reference a fact established earlier in today's brief**. No abstract textbook prompts.

## Step 3 — Deliver to Telegram

Save the briefing to the archive file, then pipe to the sender. **Telegram delivery is the priority** — if the archive save fails (disk full, permission error), log the error but **still send to Telegram**. The live brief is what the user reads; the archive is a convenience copy.

```bash
BRIEF_FILE="<PROJECT_DIR>/archive/$(date +%F).md"
# Write the briefing markdown to $BRIEF_FILE — if this fails, continue anyway.
# Then send (this is the irreplaceable step):
cat "$BRIEF_FILE" | "<PROJECT_DIR>/send_telegram.sh"
```

The sender chunks at 3800 chars, posts to Telegram, and falls back to plain-text if Markdown parsing fails.

## Step 4 — Confirm or surface an error

**Success path**: the sender prints `OK: briefing sent.` → run complete.

**Failure path — never go silent**. If the run errors before a brief was assembled (e.g. all primary sources failed, every FT/WSJ fetch returned ## ERROR, synthesis crashed), the user has no other channel to learn the run broke. **Send a short error notice via the same sender:**

```bash
echo "❌ news-fetch failed at $(date +%H:%M): <one-line reason>" \
  | "<PROJECT_DIR>/send_telegram.sh"
```

Always end with a definite signal: either the brief lands, or an error notice does. Never silence. Half-empty briefings (the brief assembled but missing key sections) are still acceptable to send — flag the missing sections in the warning footer rather than aborting the whole run.
