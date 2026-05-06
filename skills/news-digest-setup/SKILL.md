---
name: news-digest-setup
description: Walk a user through manual setup of the news-digest daily briefing routine end-to-end. Use when the user has cloned the news-digest repo and wants to install the daily Telegram brief. Handles Telegram bot creation, FT/WSJ cookie export, Claude Code permissions, folder trust, pmset wake schedule, and scheduled task registration.
---

# news-digest setup walkthrough

You are walking the user through configuring a daily markets brief that fires at a chosen time, fetches news, and delivers it to Telegram.

The full step list is in `SETUP.md` at the repo root. This skill makes the process interactive: at each step, you check the user's state, run safe commands on their behalf, verify results, and move on only when the step is confirmed working.

## How to use this skill

1. **Ask which step they're on** if not obvious from context. The 14 steps below are numbered. New users start at step 1; users coming back to fix something should jump to the relevant step.

2. **For each step**:
   - Read the rationale aloud (1–2 sentences)
   - Show the command(s) the user should run
   - Run safe inspection commands yourself (`ls`, `grep`, `cat -- public files only`) to verify state
   - **NEVER run commands that contain or print user secrets** (the bot token, cookie strings, etc.) — display the file path so the user can verify themselves
   - When the step succeeds, say so explicitly and move on

3. **Stop and ask the user when**:
   - They need to do something in the browser (Telegram, BotFather, Cookie-Editor, Claude Code UI)
   - They need to paste a secret you'd otherwise have to log
   - You see an error you can't diagnose from context

4. **Always assume**:
   - The user is on macOS
   - They have Claude Code 2.x signed in
   - The repo is at `~/news-digest` (offer to use a different path if they prefer)

## The 14 steps

### Step 1: Confirm prerequisites
Run `python3 --version` (need 3.9+) and `which claude` (Claude Code installed). Confirm the user has a Telegram account.

### Step 2: Verify clone location
Check `~/news-digest/` exists and contains `routine-prompt.md` + the fetcher scripts. If not, prompt them to `git clone https://github.com/GeniusTrader-Harry/news-digest.git ~/news-digest`. Strongly recommend NOT using `~/Documents/news-digest` (iCloud-synced; produces intermittent EINTR errors on heavy file activity).

### Step 3: Install Python deps
Walk through:
```bash
cd ~/news-digest
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install curl_cffi
```
Verify: `python3 -c "import curl_cffi; print(curl_cffi.__version__)"`. Should print a version like `0.13.0`.

### Step 4: Telegram bot creation (USER does this in Telegram app)
Tell the user:
> 1. Open Telegram, search **@BotFather**, start chat
> 2. Send `/newbot`, follow prompts (name + username ending in `bot`)
> 3. **Save the token BotFather gives you** — looks like `123456789:ABCdef...`
> 4. Search for your new bot, open it, tap **Start**

Wait for them to confirm they have the token + have started the chat.

### Step 5: Get chat_id
Ask the user to paste their bot token (one-time, you'll use it in a curl). Run:
```bash
curl -s "https://api.telegram.org/bot<TOKEN>/getUpdates" | python3 -m json.tool
```
Find `"chat":{"id": NUMBER}` in the output. That's the chat_id.

If output is empty: ask the user to send "hi" to their bot in Telegram, then re-run.

### Step 6: Configure .env
```bash
cd ~/news-digest
cp .env.example .env
chmod 600 .env
```
Tell the user to edit `.env` with their token + chat_id (don't print these to the conversation). Say:
> Open `.env` in your editor and replace the two `replace_with_*` placeholders with the values you have.

After they confirm: test delivery without printing the secrets:
```bash
echo "Setup test from news-digest" | ~/news-digest/send_telegram.sh
```
They should see the message in Telegram. If they get `OK: briefing sent.`, ✅.

### Step 7: FT cookie (OPTIONAL — skip if no FT subscription)
Ask: do they have an FT subscription (personal, university library via SSO, etc.)?

If yes, walk them through:
> 1. Install Cookie-Editor extension in Chrome ([link](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm))
> 2. Pin it to toolbar
> 3. Log into ft.com
> 4. Click Cookie-Editor icon → Export → Export as Header String
> 5. Paste into `~/news-digest/ft_cookie.txt` (create the file)
> 6. `chmod 600 ~/news-digest/ft_cookie.txt`

After: test with a real FT URL. Pull a fresh URL from RSS:
```bash
curl -s 'https://www.ft.com/markets?format=rss' | grep -oE '<link>https://www\.ft\.com/content/[^<]+</link>' | head -1
```
Then run `~/news-digest/fetch_ft.sh <that-url>`. Expect clean markdown output with headline, byline, body. If you see `## ERROR:` blocks, cookie didn't authenticate — re-export.

### Step 8: WSJ cookie (OPTIONAL — same as FT)
Same pattern, swap domain. Same Cookie-Editor flow on `wsj.com`. Save to `~/news-digest/wsj_cookie.txt`. Test with:
```bash
WSJ=$(curl -s 'https://feeds.a.dj.com/rss/RSSMarketsMain.xml' -A 'Mozilla/5.0' | grep -oE '<link>https://www\.wsj\.com/articles/[^<]+</link>' | head -1 | sed 's|<link>||;s|</link>||')
~/news-digest/fetch_wsj.sh "$WSJ"
```

### Step 9: Customise routine-prompt.md
Two find-replaces the user MUST do:
- `<USER_NAME>` → their name (or whatever they want the agent to call them)
- `<PROJECT_DIR>` → the absolute path, typically `/Users/<their-username>/news-digest`

You can do this for them with `sed -i '' 's|<USER_NAME>|Their Name|g' routine-prompt.md` etc., but ASK FIRST whether they want to keep the finance-recruiting framing or change the audience (line 1).

If they want a different beat, point them at `CUSTOMISATION.md` — the geography rule, theme dictionary, and view-forming question style all need tuning.

### Step 10: Add Claude Code permission allowlist
Read their current `~/.claude/settings.json`. Find or create a `permissions.allow` array, and add the entries from `SETUP.md` step 9 (replacing path placeholders with their real `<PROJECT_DIR>`).

This is a JSON edit — do it carefully. Always back up first:
```bash
cp ~/.claude/settings.json ~/.claude/settings.json.bak
```

### Step 11: Trust the project folder
Edit `~/.claude.json` to add a trust entry:
```python
python3 -c "
import json
p = '/Users/<USER>/.claude.json'  # actual user
with open(p) as f: d = json.load(f)
d.setdefault('projects', {})['/Users/<USER>/news-digest'] = {
    'allowedTools': [],
    'hasTrustDialogAccepted': True,
    'projectOnboardingSeenCount': 0,
}
with open(p, 'w') as f: json.dump(d, f, indent=2)
print('OK')
"
```

After running, tell the user: **You must quit and reopen the Claude Code app** for the change to take effect. The app reads `~/.claude.json` only at startup.

### Step 12: pmset wake schedule
This requires `sudo`, so the user runs it themselves:
```bash
sudo pmset repeat wakeorpoweron MTWRFSU 10:55:00
```
Where `10:55:00` is 13 minutes before their target fire time of `11:08`. Adjust if they want a different time.

Verify: `pmset -g sched` should show `wakepoweron at 10:55AM every day`.

Heads up: this only wakes the Mac from sleep, not from a full shutdown. They need to keep the laptop sleeping (lid closed + on charger is fine), not powered off.

### Step 13: Create scheduled task
Use the `mcp__scheduled-tasks__create_scheduled_task` tool with:
- `taskId`: `news-digest-daily-brief`
- `cronExpression`: `0 11 * * *` (or whatever time they want; runs in their local timezone)
- `description`: `Daily markets briefing pushed to Telegram`
- `prompt`:
  ```
  Read the file `<PROJECT_DIR>/routine-prompt.md` and follow its instructions exactly. Do not skip the Telegram delivery step. If anything fails, surface a clear error.
  ```

Replace `<PROJECT_DIR>` with the actual path.

### Step 14: Run Now to validate end-to-end
Tell the user: in the Claude Code sidebar → Scheduled section → click `news-digest-daily-brief` → **Run Now**.

The run takes 5–7 minutes. Monitor it with:
```bash
ls -la ~/news-digest/archive/
```
Wait for a new dated `.md` file to appear. Once it does, the user should also see a Telegram message land in their bot chat.

If the run fails, check the live session output in the sidebar. Common diagnostics:
- "Permission required for X" → that tool wasn't in the allowlist; add to step 10
- `## ERROR:` in archive → cookie expired; redo step 7 or 8
- "Folder is not trusted" → step 11 didn't take; quit/reopen Claude Code
- Run shown but no archive → run was stopped early or ran into silent error

When today's brief lands cleanly in Telegram, **the setup is complete**. Tomorrow's run at the cron time fires automatically.

### Final pointer

After 1–2 weeks of usage, the user should revisit `CUSTOMISATION.md` to:
- Tune the theme dictionary (drop dead themes, add new ones)
- Adjust geography weighting
- Tweak section sizes
- Change the view-forming question style for their actual reading habit

Nothing in the setup is set-and-forget. The brief gets better the more it's tuned.

## Style for this skill

- Be concrete. Give exact commands, not "configure your settings".
- Verify each step before moving on. Don't let the user push through a broken state.
- When you can't run something safely (involves their secrets, requires UI interaction), stop and ask them to do it.
- Keep responses short — the user is reading and acting in parallel. Don't write essays.
