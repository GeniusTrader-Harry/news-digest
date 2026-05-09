# CUSTOMISATION

The published `routine-prompt.md` is **opinionated** — it's set up for finance / sales-and-trading / equity-research / asset-management recruiting prep. The opinionated bits are the worked example. **All of them are meant to be tuned for your beat.**

## TL;DR — "I want to change X, edit Y"

| Want to... | Edit | Search for |
|---|---|---|
| Change who the brief is "for" | `routine-prompt.md` | line 1 — `<USER_NAME>` and the framing after it |
| Make it US-only / Asia-led / Europe-only | `routine-prompt.md` | the **Geography weighting** bullet |
| Change recurring-narrative tags | `routine-prompt.md` | the `⏣` block under **Theme tags** |
| Make brief shorter / longer | `routine-prompt.md` | section counts: `Macro & rates (2–3 stories)` etc. |
| Add a new paywalled outlet | new `fetch_X.py` + `routine-prompt.md` | mirror `fetch_wsj.py` pattern |
| Drop a source | `routine-prompt.md` + `~/.claude/settings.json` | remove from Step 1 + remove `WebFetch(domain:...)` line |
| Change the view-forming-question style | `routine-prompt.md` | `*🎯 Today's view-forming question*` block |
| Switch between manual / autonomous mode | scheduled-tasks.json | Manual: omit `cronExpression` (default). Autonomous: set e.g. `cronExpression: "0 11 * * *"`. Or just ask Claude: "make news-fetch manual-trigger only" or "set news-fetch to fire at 8am". See SETUP.md §12 for caveats on autonomous mode. |

This guide tells you the *why* behind each option and how the moving parts interact.

---

## TL;DR — six things you'll probably want to tune

| # | What | Where | Effort |
|---|---|---|---|
| 1 | **Audience framing** (line 1) | `routine-prompt.md` top | 30 sec |
| 2 | **Geography weighting** | Quality bar block | 1 min |
| 3 | **Theme dictionary** | Step 2 → Theme tags | 2–5 min |
| 4 | **Section sizes** | Output format | 30 sec |
| 5 | **Source list** (add/remove outlets) | Step 1 + Quality bar | 2 min |
| 6 | **View-forming question style** | Output format | 1 min |

The rest of this doc covers each in detail.

---

## 1. Audience framing

Line 1 of `routine-prompt.md`:

```
# Daily Markets Briefing — for <USER_NAME> (S&T / ER / AM recruiting prep — example template)
```

Replace with what you actually do. Examples:

```markdown
# Daily Climate-Tech Briefing — for <USER_NAME> (early-stage VC scouting)
# Daily Biotech Briefing — for <USER_NAME> (clinical-trial sell-side coverage)
# Daily Geopolitics Briefing — for <USER_NAME> (think-tank monitoring)
```

Then update the second paragraph to match. The agent uses this framing to bias what counts as "important" and how to write interview hooks.

## 2. Geography weighting

Default in the published template:
> Target rough share across the whole brief: **~50% US · ~25% UK · ~15% EU · ~10% Asia**

This makes sense for a London-based finance recruit. For a US fintech founder, an EU climate analyst, or an Asia-focused PM, change this. Examples:

| Beat | Suggested rule |
|---|---|
| US-only finance | 80% US · 10% Europe (when they affect US) · 10% Asia/EM (when they affect US) |
| Asia macro | 40% China · 25% Japan/Korea · 20% rest of Asia · 15% US (only when policy spillover) |
| EU policy | 50% EU institutions · 20% national-level UK/DE/FR · 20% global (US/China when affects EU) · 10% other |
| Climate tech | Source-tier instead of geography: 40% primary research · 30% companies · 20% policy · 10% capital flows |

The point is to be **explicit so the agent can self-check**. Vague "all of it equally" produces drift.

## 3. Theme dictionary

The published themes (`Rate-cut path`, `AI capex`, `UK fiscal`, `Term premium`, etc.) are recurring 2026 finance narratives. Your beat has different recurring narratives.

**Naming rules** (keep these):
- Capture the *tension*, not the topic (`AI capex` not `AI` — the tension is "will spend pay off?")
- Use insider vocabulary, not textbook (`Term premium` not `long-end yields rising`)
- Short — 2–4 words, readable inline

**Examples for other beats**:

```
Climate tech:
  ⏣ DAC unit economics    — direct-air-capture cost-per-tonne curve
  ⏣ EU green premium      — premium pricing for low-carbon goods
  ⏣ Permitting bottleneck — interconnection queues, NEPA reform, etc.
  ⏣ Hydrogen demand-side  — offtaker contracts vs supply build-out

Biotech / sell-side coverage:
  ⏣ Phase-3 readout       — pivotal trial results, primary-endpoint pass/fail
  ⏣ FDA AdCom watch       — advisory committee votes, label-narrowing risk
  ⏣ Chinese biotech listings — HKEX flow, US-listed China names
  ⏣ Big pharma BD          — late-stage in-licensing deal flow

VC / early-stage:
  ⏣ Series A reset        — 2024-cohort up/down/flat round visibility
  ⏣ AI-native incumbents  — challenger v incumbent dynamic by category
  ⏣ Founder secondaries   — early-employee liquidity events / DPI proxies
  ⏣ Vertical SaaS exits   — strategic vs sponsor M&A in long-tail SaaS
```

**Lifecycle (keep this rule)**: themes enter when 3+ stories recur over 1–2 weeks; retire after 2+ weeks of silence. Resist the temptation to keep dead themes in the dictionary — they make the brief feel stale.

## 4. Section sizes

Default:
- Macro & rates: 2–3 stories
- Equities & single names: 2–3 stories
- M&A & capital markets: 1–2 stories
- Plus 1 deep-read + 1 view question

Total = 5–8 themed stories per brief. ~5 min read.

For a longer/shorter brief, bump these up/down. Trade-off: bigger sections mean less editorial discrimination per story (the agent fills the slots even if material is thin). Smaller sections force harder choices but might feel under-cooked on heavy news days.

Realistic ranges:
- **Light brief** (2 min read): 1–2 / 1–2 / 0–1 — about 4 stories total
- **Standard** (5 min, default): 2–3 / 2–3 / 1–2 — 5–8 stories
- **Long brief** (10 min): 4–5 / 4–5 / 3–4 — 11–14 stories

For a non-finance beat you may want completely different section labels. The brief structure is `*Section emoji*` headers — change them freely:

```
*🌱 Carbon markets*           (2–3 stories)
*🏭 Industry transitions*     (2–3 stories)
*🏛️ Policy & regulation*      (1–2 stories)
```

Just keep the per-story format consistent: `*N. [⏣ Theme] {Headline}*` + summary + interview hook + 🔗.

## 5. Source list

The published template uses: FT (primary) · WSJ (peer) · CNBC · central banks · WebSearch. Reuters and Bloomberg are intentionally excluded — both use anti-bot protection (DataDome / PerimeterX) that defeats `curl_cffi`.

To add a source, two things:

**a)** Add it to Step 1 in `routine-prompt.md`:
```
- **The Information** — `https://www.theinformation.com/`
```

**b)** If it's paywalled, you need a fetcher pipeline like `fetch_ft.sh` / `fetch_wsj.sh`. The pattern:
1. Find an RSS or sitemap feed for triage (no auth)
2. Confirm `curl_cffi` Chrome-131 impersonation can bypass any Cloudflare/Datadome at the article URL
3. Find where the body lives in the HTML (JSON-LD `articleBody`? `<article>` tags? `<p data-type="paragraph">`? other?)
4. Copy `fetch_wsj.py` as a starting template and adapt

If the publisher uses **PerimeterX** ("Are you a robot?" 403s) or **DataDome** ("Please enable JS" 401s), `curl_cffi` won't work — you'd need Playwright with a logged-in profile. Bloomberg uses PerimeterX; Reuters uses DataDome. Both are blocked in this template by design.

To remove a source, delete its line from Step 1 and any references in the Quality bar.

## 6. View-forming question

The published prompt's view-forming question is finance-coded:
> "If 30Y gilts hold above 5.75%, are UK banks long or short duration risk on a 12m view? Defend either side."

For a different beat, change the example phrasing in the prompt so the agent knows what shape to produce:

| Beat | Example shape |
|---|---|
| VC scouting | "If [Series A startup X] is now post-product-market-fit at $5M ARR, is the right next hire a CRO or a head of growth? When does the answer flip?" |
| Climate policy | "If the EU CBAM is enforced as written, do UK steelmakers benefit or get caught in the crossfire? What single 2026 data point would shift your view?" |
| Biotech | "If [drug X]'s Phase-3 reads out positive but with a worse safety profile than placebo, what's the right framing for the label? Where does the FDA most likely land?" |

The hard rule is **forces a position, can be defended either way, references a fact established earlier in today's brief**. Keep that rule, change the examples.

---

## Things you should probably leave alone

These rules are general — they apply to any beat:

- **No claim without a primary source** (style rules)
- **Cite the source you actually read** (style rules)
- **Theme tag continuity across days** (Step 2 → Continuity rule)
- **The four-test rubric for the deep-read pick** (Step 2 → Read deeper)
- **Honesty fallback when no deep-read meets the bar** (don't force filler)

Removing these makes the brief noticeably worse. They exist because LLMs default to plausible-sounding noise without them.

---

## How to know your customisation is working

After a week of briefs:

1. **Read your archive** (`~/news-fetch/archive/`). Are the themes you tagged actually recurring? Are the geography shares roughly matching your target?
2. **Check the deep-read picks**. If the agent is forcing picks on slow days, your filter isn't strict enough.
3. **Test the view-forming questions** on yourself. Can you actually take a position and defend it? If they feel abstract or unanswerable, the prompt examples need to be more grounded.
4. **Notice missing stories**. If you read an FT piece in your browser that didn't make the brief, ask why — usually it means a theme is missing from the dictionary or a source isn't weighted right.

The brief gets better the more you tune it. Your edits compound.
