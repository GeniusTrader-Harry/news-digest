# SETUP — manual walkthrough

This is the **non-interactive** setup guide. If you'd rather have a Claude Code skill walk you through it step by step, use `/news-digest-setup` after you clone the repo.

**Estimated time: 30–45 minutes** — mostly waiting on browser tabs and BotFather prompts; the actual scripted work is ~10 minutes.

## At a glance — which steps are required vs optional

| Steps | Time | Required? |
|---|---|---|
| **1–6**: prerequisites · clone · venv · Telegram bot · `.env` | ~15 min | ✅ Required |
| **7–8**: FT cookie · WSJ cookie | ~5 min each | ⚪ Optional — skip if no subscription. Brief still works using just CNBC + central banks + WebSearch, but loses most of its analytical depth (FT and WSJ are the primary tier). |
| **9, 10, 11, 13**: customise prompt · permissions · trust folder · register manual task · Run Now test | ~10 min | ✅ Required |
| **12**: pmset daily wake schedule | ~1 min | ⚪ Optional — only needed if you want **autonomous** cron-fire (vs the default manual-trigger mode). See "autonomous mode" notes in step 12. |

**Default mode is manual-trigger** — you click Run Now from the Claude Code Scheduled sidebar each morning. This is the most reliable mode because nothing depends on your Mac being awake at a fire time. ~25 min total setup if you skip the cookies and the wake schedule.

If you want **autonomous cron-fire** (laptop must be awake + Claude Code running + not in Low Power Mode at fire time), do step 12 as well and use a cron expression in step 13.

---

## 0. Prerequisites

- macOS (manual-trigger mode works on any platform with Claude Code; the optional `pmset` autonomous-wake schedule in step 12 is Mac-only)
- [Claude Code](https://claude.com/claude-code) 2.x installed and signed in
- Python 3.9+ (`python3 --version` to check)
- A Telegram account
- Optional but recommended: an FT subscription (personal, or via uni / library) and a WSJ subscription. Without these, the brief falls back to CNBC + central-bank sources only — usable but much shallower.

## 1. Clone the repo

Pick a location that's NOT inside `~/Documents/` (which is iCloud-synced on most Macs and can produce intermittent file errors). The recommended location is `~/news-digest`:

```bash
git clone https://github.com/GeniusTrader-Harry/news-digest.git ~/news-digest
cd ~/news-digest
```

If you put it elsewhere, remember the absolute path — you'll need it in step 8 to replace `<PROJECT_DIR>` in the routine prompt.

## 2. Install Python dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install curl_cffi
```

Verify:
```bash
python3 -c "import curl_cffi; print('curl_cffi', curl_cffi.__version__)"
```
You should see something like `curl_cffi 0.13.0`.

## 3. Create your Telegram bot

1. In Telegram, search for **@BotFather**, start a chat.
2. Send `/newbot`. Pick:
   - A **display name** (e.g. "Markets Brief")
   - A **username** ending in `bot` (e.g. `yourname_markets_bot` — must be globally unique)
3. BotFather replies with a token like `123456789:ABCdef...`. **Save this — it's a secret.**
4. Search for your new bot in Telegram (by the username you chose) → open the chat → tap **Start** (or send any message). This is required for the bot to be allowed to message you.

## 4. Get your chat_id

In Terminal, replace `<TOKEN>` and run:

```bash
curl -s "https://api.telegram.org/bot<TOKEN>/getUpdates" | python3 -m json.tool
```

Look for `"chat":{"id": 1234567890, ...` — that number is your chat_id.

## 5. Configure `.env`

```bash
cp .env.example .env
chmod 600 .env
nano .env   # or open in any editor
```

Fill in:
```
TELEGRAM_BOT_TOKEN=123456789:ABCdef...   # from step 3
TELEGRAM_CHAT_ID=1234567890               # from step 4
```

Test delivery:
```bash
echo "test message from setup" | ./send_telegram.sh
```
You should receive the message in your Telegram chat with the bot. If not, double-check the token + chat_id. If it works, you'll see `OK: briefing sent.`

## 6. (Optional) FT cookie setup

Skip this if you don't have an FT subscription. The brief still works without FT — just falls back to CNBC + central banks (much shallower).

1. In Chrome, install the **Cookie-Editor** extension ([Chrome Web Store](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)) and pin it to the toolbar.
2. Log into **https://www.ft.com/** (Imperial / personal sub / whatever you have).
3. Click the Cookie-Editor icon → **Export → Export as Header String** at the bottom of the popup.
4. Paste the result into `~/news-digest/ft_cookie.txt` (create the file). Lock it down:
   ```bash
   chmod 600 ft_cookie.txt
   ```
5. Test:
   ```bash
   ./fetch_ft.sh https://www.ft.com/content/<paste-any-recent-article-uuid>
   ```
   You should see a clean markdown article (headline + byline + body). If you see `## ERROR:` blocks, the cookie didn't authenticate — re-export.

## 7. (Optional) WSJ cookie setup

Same procedure as FT, swap domains:

1. Log into https://www.wsj.com/ in Chrome.
2. Cookie-Editor → Export as Header String.
3. Paste into `~/news-digest/wsj_cookie.txt`. `chmod 600 wsj_cookie.txt`.
4. Test URL discovery (the section-page scraper that replaces stale RSS feeds):
   ```bash
   ./discover_wsj.sh --max 5
   ```
   Should print 5 fresh wsj.com URLs, one per line. If it errors with "no article URLs discovered", the cookie didn't authenticate — re-export.
5. Test body fetching with one of those URLs:
   ```bash
   URL=$(./discover_wsj.sh --max 1)
   ./fetch_wsj.sh "$URL"
   ```
   Should print clean markdown (headline, byline, body).

**Why not WSJ RSS?** WSJ's `feeds.a.dj.com` endpoints periodically return only stale articles (e.g. all items from January 2025) — server-side caching/CDN issue we can't fix. The section-page scraper bypasses it by going to wsj.com directly.

## 8. Customise `routine-prompt.md` for your install

```bash
nano routine-prompt.md
```

Find-and-replace:
- `<USER_NAME>` → your name (or the name the agent should use to address you)
- `<PROJECT_DIR>` → your absolute install path (e.g. `/Users/yourname/news-digest`)

Optional but encouraged: tune the audience framing in line 1, the geography rule, the theme dictionary, and section sizes — see [CUSTOMISATION.md](CUSTOMISATION.md). The defaults are an example for finance-recruiting prep; your beat is probably different.

## 9. Add Claude Code permissions

Edit `~/.claude/settings.json`. If `permissions.allow` doesn't exist, create it. Add the following entries (replace `/Users/yourname/news-digest` with your real `<PROJECT_DIR>`):

```json
{
  "permissions": {
    "allow": [
      "WebSearch",
      "WebFetch(domain:www.cnbc.com)",
      "WebFetch(domain:cnbc.com)",
      "WebFetch(domain:federalreserve.gov)",
      "WebFetch(domain:www.federalreserve.gov)",
      "WebFetch(domain:bankofengland.co.uk)",
      "WebFetch(domain:www.bankofengland.co.uk)",
      "WebFetch(domain:ecb.europa.eu)",
      "WebFetch(domain:www.ecb.europa.eu)",
      "WebFetch(domain:bis.org)",
      "WebFetch(domain:www.bis.org)",
      "WebFetch(domain:imf.org)",
      "WebFetch(domain:www.imf.org)",
      "WebFetch(domain:ft.com)",
      "WebFetch(domain:www.ft.com)",
      "WebFetch(domain:wsj.com)",
      "WebFetch(domain:www.wsj.com)",
      "WebFetch(domain:feeds.a.dj.com)",
      "Bash(/Users/yourname/news-digest/send_telegram.sh)",
      "Bash(/Users/yourname/news-digest/fetch_ft.sh:*)",
      "Bash(/Users/yourname/news-digest/fetch_wsj.sh:*)",
      "Bash(/Users/yourname/news-digest/discover_wsj.sh:*)",
      "Bash(curl:*)",
      "Bash(date:*)",
      "Bash(mkdir:*)",
      "Bash(cat:*)",
      "Bash(echo:*)",
      "Bash(ls:*)",
      "Bash(grep:*)",
      "Bash(sed:*)",
      "Bash(awk:*)",
      "Bash(cut:*)",
      "Bash(tr:*)",
      "Bash(head:*)",
      "Bash(tail:*)",
      "Bash(sort:*)",
      "Bash(uniq:*)",
      "Bash(wc:*)",
      "Bash(python3:*)",
      "Read(/Users/yourname/news-digest/**)",
      "Write(/Users/yourname/news-digest/archive/**)"
    ]
  }
}
```

This pre-approves the tools the routine uses, so the scheduled task fires without permission prompts.

**Why so many Bash entries?** The agent uses standard Unix text-processing tools (`grep`, `sed`, `head`, `tail`, etc.) to parse fetched HTML/XML between fetcher calls. If any one of these isn't allowlisted, the scheduled task pauses mid-run waiting for an interactive permission prompt — bad for an autonomous routine when you might not be at the laptop. The list above covers everything the agent has needed across multiple test runs.

## 10. Trust the project folder

Claude Code refuses to fire scheduled tasks from untrusted folders. To trust it:

**Option A — UI**: Open Claude Code → File → Open Folder → navigate to `~/news-digest` → click **Trust** when prompted.

**Option B — direct edit**: Add an entry to `~/.claude.json`:
```python
python3 -c "
import json
p = '/Users/yourname/.claude.json'  # adjust username
with open(p) as f: d = json.load(f)
d.setdefault('projects', {})['/Users/yourname/news-digest'] = {
    'allowedTools': [],
    'hasTrustDialogAccepted': True,
    'projectOnboardingSeenCount': 0,
}
with open(p, 'w') as f: json.dump(d, f, indent=2)
print('OK')
"
```
Quit and reopen Claude Code for it to re-read the file.

## 11. (OPTIONAL) Schedule the daily Mac wake — only if you want autonomous cron-fire

**Skip this step if running in manual-trigger mode** (the default). You only need it if you set a cron schedule in step 12 and want your Mac to wake from sleep automatically.

```bash
sudo pmset repeat wakeorpoweron MTWRFSU 10:55:00
```

Verify:
```bash
pmset -g sched
```
You should see `wakepoweron at 10:55AM every day`. This wakes your Mac from sleep at 10:55 every day so a cron-scheduled task can fire. Doesn't wake from full shutdown — keep your Mac sleeping not off.

**Caveat**: macOS **Low Power Mode** throttles or defers scheduled tasks silently. If you rely on this for autonomous fire, also disable Low Power Mode (System Settings → Battery → Low Power Mode → "Never") or accept that runs will be missed when the battery drops below ~20%.

To cancel later: `sudo pmset repeat cancel`.

## 12. Create the scheduled task

In Claude Code, with the `~/news-digest` folder open, ask Claude:

> "Create a scheduled task called `news-digest-daily-brief` that runs at 11:00 daily. The prompt should read `<PROJECT_DIR>/routine-prompt.md` and follow its instructions exactly."

Or use the scheduled-tasks MCP directly. The minimal task spec:

- **taskId**: `news-digest-daily-brief`
- **cronExpression**: `0 11 * * *` (or whatever time you prefer; cron runs in your local timezone)
- **prompt**:
  ```
  Read the file `<PROJECT_DIR>/routine-prompt.md` and follow its instructions exactly. Do not skip the Telegram delivery step. If anything fails, surface a clear error.
  ```

Note: Claude Code applies a small dispatch jitter — your `0 11` task actually fires around 11:08.

## 13. Test end-to-end with "Run Now"

In the Claude Code sidebar → **Scheduled** section → click your `news-digest-daily-brief` task → **Run now**.

Wait 5–7 minutes. You should:
1. See a brief land in your Telegram chat with the bot
2. See a new file `~/news-digest/archive/$(date +%F).md`

If something fails, the agent surfaces an error in the live session output. Common issues + fixes:

| Symptom | Likely cause | Fix |
|---|---|---|
| No Telegram message | Bot token wrong | Re-check `.env` |
| `## ERROR:` in archive next to FT/WSJ stories | Cookie expired | Re-export per step 6/7 |
| Permission prompts mid-run | Allowlist incomplete | Add missing entries to `~/.claude/settings.json` |
| Run shown but no archive | Folder not trusted, or run was stopped early | Trust folder per step 10; let it run full duration |
| Task didn't fire when expected (autonomous mode only) | Mac was off / Claude Code not running / Low Power Mode active at fire time | Best fix: switch to manual-trigger mode. Or: keep Mac on charger, disable Low Power Mode, ensure Claude Code is open at the fire window |

## 14. (Autonomous mode only) Set Claude Code to auto-launch

Skip if running in manual-trigger mode. If you set a cron schedule in step 12, you also want Claude Code to be open at the fire window:

System Settings → General → Login Items → click `+` → add Claude.app.

## You're done

**Manual mode**: each morning, click Run Now on `news-digest-daily-brief` in the Claude Code Scheduled sidebar. Brief lands in Telegram in 5–7 minutes.

**Autonomous mode**: at your cron fire time (typically ~7 minutes after the cron minute due to dispatch jitter), a brief should arrive without any input from you — *if* your Mac is awake, Claude Code is running, and Low Power Mode is off.

After 1–2 weeks, revisit:

- The theme dictionary — prune themes that didn't recur, add ones that emerged
- The geography rule — does the actual coverage match your weighting?
- Section sizes — too long? too short?

See [CUSTOMISATION.md](CUSTOMISATION.md) for the editing guide.

---

## Notes / FAQ

### Reuters and Bloomberg are excluded

Both Reuters and Bloomberg use aggressive anti-bot protection — Reuters runs **DataDome**, Bloomberg runs **PerimeterX**. Both require JavaScript challenge solving to mint a valid session cookie, and `curl_cffi` (which works for FT and WSJ) gets HTTP 401 / 403 regardless of your subscription cookies.

Even with a valid Reuters or Bloomberg subscription, you can't bypass this with our infrastructure. Realistic options if you really want them:

- **Skip both from the automated brief** (current default) and read them directly in your browser
- **Build a Playwright-based fetcher** with a dedicated logged-in Chrome profile per outlet (~60–90 min one-off setup each; not included in this repo)

If you build a Playwright fetcher for either, PRs welcome.

### Cookie rotation

FT/WSJ session cookies typically last 2–4 weeks. When the brief shows `⚠️ FT cookie may need refresh — N FT articles failed to fetch`, re-do step 6 or 7. ~30 seconds.

### Why a separate `Claude Projects` folder, not `Documents`?

`~/Documents/` on macOS is heavily-monitored (Spotlight, iCloud, Time Machine, MS Office sync, etc.). EINTR storms during heavy filesystem activity can break reads. `~/` directly is much quieter and avoids the issue.
