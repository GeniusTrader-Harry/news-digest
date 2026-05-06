<!--
  TEMPLATE — this is the prompt the scheduled task runs every morning.

  Two things you MUST replace before this works:
    1. <USER_NAME>    → your name / nickname (used by the agent to address you)
    2. <PROJECT_DIR>  → absolute path to where you cloned this repo
                        (e.g. /Users/yourname/news-digest)

  Two things you SHOULD customise (see CUSTOMISATION.md):
    - The "for <USER_NAME>" framing in line 1 (this template is set up for
      finance / sales-and-trading / equity-research recruiting prep —
      replace with your beat: VC scouting, climate-tech monitoring, etc.)
    - The Geography rule, theme dictionary, and section sizes — your editorial
      taste, not someone else's.

  The setup skill (skills/news-digest-setup) walks you through this interactively.
-->

# Daily Markets Briefing — for <USER_NAME> (S&T / ER / AM recruiting prep — example template)

You are generating <USER_NAME>'s daily commercial-awareness briefing. They are preparing for sales & trading, equity research, and asset management interviews — the brief should help them sound informed and prepared on a desk call or superday.

Today's date: run `date "+%A, %d %B %Y"` first, and use that as the dated header.

## Step 1 — Gather news (parallel WebSearch / WebFetch)

Pull TODAY'S top stories (and overnight if pre-market) from these sources, in parallel:

- **Reuters** — `https://www.reuters.com/markets/`, `https://www.reuters.com/business/finance/`, `https://www.reuters.com/markets/deals/`
- **CNBC** — `https://www.cnbc.com/markets/`, `https://www.cnbc.com/deals-and-ipos/`
- **Central bank press releases** (only if there's an FOMC / BoE / ECB / BoJ event today or yesterday): Fed `federalreserve.gov/newsevents/pressreleases.htm`, BoE `bankofengland.co.uk/news`, ECB `ecb.europa.eu/press/pr/date/...`
- **FT** (subscriber, full-text access via local fetcher) — fetch RSS feeds for triage, then pull full article bodies via the dedicated FT fetcher. See "FT pipeline" below.
- **WSJ** (subscriber, full-text access via local fetcher) — fetch RSS feeds for triage, then pull full article bodies via the dedicated WSJ fetcher. See "WSJ pipeline" below.

Use WebSearch for breaking-news type queries (e.g. "FTSE 100 today", "M&A announcement today", "Fed decision today") to fill gaps the homepages miss.

### FT pipeline (special workflow)

The FT is paywalled and Cloudflare-protected, so vanilla WebFetch fails. Use this two-step flow:

**(a) Triage via RSS** — fetch these XML feeds (no auth, public):
- `https://www.ft.com/rss/home`
- `https://www.ft.com/markets?format=rss`
- `https://www.ft.com/companies?format=rss`
- `https://www.ft.com/lex?format=rss`

Each item has `<title>`, `<description>` (one-line dek), `<link>` (the article URL), `<pubDate>`. Use these to identify the **3–5 most relevant FT stories for today's themes** (macro, equities, M&A, AM). Skip items older than 36 hours unless still developing.

**(b) Fetch full bodies** — call the local fetcher with the URLs you picked:

```bash
"<PROJECT_DIR>/fetch_ft.sh" URL1 URL2 URL3 ...
```

It returns clean markdown for each article: headline, byline + date, dek, full article body, source link. Use this body when summarising — it's authoritative FT prose, so quote sparingly and accurately, and don't invent figures.

If any FT URL returns an `## ERROR:` block (likely cookie expiry), do NOT fabricate content. Skip that story and include a single line at the bottom of the brief: `_⚠️ FT cookie may need refresh — N FT articles failed to fetch._`

### WSJ pipeline (special workflow — same shape as FT)

Same two-step pattern: RSS for triage, local fetcher for body.

**(a) Triage via RSS** — fetch these XML feeds (no auth, public):
- `https://feeds.a.dj.com/rss/RSSMarketsMain.xml`
- `https://feeds.a.dj.com/rss/RSSWorldNews.xml`
- `https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml`
- `https://feeds.a.dj.com/rss/RSSWSJD.xml` (tech)
- `https://feeds.a.dj.com/rss/RSSOpinion.xml`

Each item has `<title>`, `<description>` (often 1–2 sentences with numbers), `<link>` (the wsj.com URL), `<pubDate>`. Identify the **3–5 most relevant WSJ stories for today's themes** that aren't already better covered by FT or Reuters. Skip items older than 36 hours unless still developing.

**(b) Fetch full bodies** — call the local fetcher with the URLs you picked:

```bash
"<PROJECT_DIR>/fetch_wsj.sh" URL1 URL2 URL3 ...
```

Returns clean markdown for each article: headline, byline + date, dek, full article body, source link. Use this body when summarising — quote sparingly and accurately, don't invent figures.

If any WSJ URL returns an `## ERROR:` block (likely cookie expiry), do NOT fabricate content. Skip that story and include a single line at the bottom of the brief: `_⚠️ WSJ cookie may need refresh — N WSJ articles failed to fetch._`

### Quality bar

- **FT is the primary, most credible source.** Treat its editorial selection as the strongest signal of what matters today. When deciding which stories to include in Macro / Equities / M&A, lean toward stories FT covers in depth (not just bare news flashes). Cite FT whenever you fetched its body via `fetch_ft.sh` — never cite an FT URL whose body you didn't actually fetch.
- **WSJ is a peer of FT in credibility — strongest on US single names, M&A scoops, and corporate stories.** Use WSJ as a peer source via `fetch_wsj.sh`. Cite WSJ whenever you fetched its body — never cite a WSJ URL whose body you didn't actually fetch.
- **Reuters is the breaking-facts backstop.** When FT/WSJ and Reuters cover the same story and you've fetched all of them:
  - **Cite FT** for analysis pieces, Lex notes, UK/European stories, M&A strategic rationale, and global macro framing.
  - **Cite WSJ** for US single-name deep dives, US corporate scoops, US M&A advisers, US macro/policy reporting where WSJ has the lead.
  - **Cite Reuters** when the story is breaking news and Reuters has the cleaner first-source account (numbers, official quotes), or when FT/WSJ have only thin headline relays.
  - When in doubt and multiple are decent, prefer FT > WSJ > Reuters.
  - For balanced coverage across geographies: FT tends to lead UK/EU; WSJ tends to lead US — use this naturally, don't force.
- **CNBC is an aggregator backstop** — use it only when none of FT/WSJ/Reuters has the story, and prefer the originals over a CNBC repackage of the same wire content.
- **FT, WSJ, and Reuters URLs only ever appear when their body was fetched.** No FT/WSJ story off the RSS dek alone; no Reuters story off a search snippet.
- **Skip op-eds, "10 stocks to buy" listicles, and "stock movers" generic recap pages**. Real news only.
- **Skip anything older than 24 hours** unless it's a still-developing story.
- **Do NOT cite Bloomberg, Barron's, The Economist** or other paywalled outlets whose body you cannot fetch. Headlines from search snippets are NOT a substitute for reading the article — they invite hallucinated content.
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

### Earnings-season auto-mode

If today's news flow contains **3+ earnings releases** (visible from the Reuters/CNBC homepages or FT companies feed), prepend an `*📊 Earnings today*` mini-section above Macro & rates:

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
| 3 | **Reuters Breakingviews column** | Sharp, contrarian, opinionated takes on a topic in today's brief. |
| 4 | **IMF / BIS / OECD / NBER working paper or speech** | Only when directly relevant to today's themes — institutional-economist angle. |
| 5 | **Sell-side public commentary** (GS / JPM / BlackRock published research excerpts visible via Reuters/CNBC) | Rare but valuable when a material call has been published. |

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

Save the briefing to `<PROJECT_DIR>/archive/$(date +%F).md`, then pipe it to the sender:

```bash
BRIEF_FILE="<PROJECT_DIR>/archive/$(date +%F).md"
# (write the briefing markdown to $BRIEF_FILE)
cat "$BRIEF_FILE" | "<PROJECT_DIR>/send_telegram.sh"
```

The sender chunks at 3800 chars, posts to Telegram, and falls back to plain-text if Markdown parsing fails.

## Step 4 — Confirm

After the sender prints `OK: briefing sent.`, your run is complete. If anything failed (no stories found, send error, FT/WSJ cookie expired), report the error clearly so the user can debug — do NOT send a half-empty briefing.
