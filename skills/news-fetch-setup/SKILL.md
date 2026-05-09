---
name: news-fetch-setup
description: Walks the user through end-to-end setup of the news-fetch Telegram markets brief. Use when the user has cloned the news-fetch repo and is installing it for the first time, OR hits errors during Telegram bot creation, FT/WSJ cookie export, scheduled-task registration, or folder trust. Triggers include phrases like "set up news-fetch", "configure the markets brief", "install the Telegram brief", "I cloned news-fetch, what now", "help me wire up the FT/WSJ fetcher", "the scheduled task isn't firing", "my FT cookie expired". Do NOT use for customising the brief CONTENT (theme dictionary, geography rule, view question style — point the user at CUSTOMISATION.md instead) or generic Claude Code setup unrelated to this repo.
---

# news-fetch setup walkthrough

You are walking the user through configuring a daily markets brief that fires at a chosen time, fetches news, and delivers it to Telegram.

The full step list is in `SETUP.md` at the repo root. **This skill makes the process interactive**: at each step, check the user's state, run safe inspection commands, verify results, and move on only when the step is confirmed working. Refer out to specific SETUP.md sections rather than duplicating long instructions.

## Operating principles

1. **Ask which step they're on** if not obvious. Steps are numbered 1–14 (see `SETUP.md`). New users start at step 1; people coming back to fix something jump to the relevant step.

2. **For each step**:
   - State the goal in 1 sentence
   - Show the command(s) — copy-pasteable, no narration
   - Run safe inspection commands yourself (`ls`, `grep` on public files, `which`, `python3 --version`)
   - **Never run commands that print user secrets** (bot tokens, cookie strings) — show the file path and let the user verify themselves
   - Confirm success explicitly before moving on

3. **Stop and ask the user when**:
   - They need to do something in the browser (Telegram, BotFather, Cookie-Editor, Claude Code UI)
   - They need to paste a secret you'd otherwise have to log
   - You see an error you can't diagnose from context

4. **Default assumptions** (state them, don't ignore them):
   - macOS
   - Claude Code 2.x signed in
   - Repo at `~/news-fetch` (offer alternatives if asked)

## The 14 steps (one-liners — full detail in SETUP.md)

| # | Step | SETUP.md ref | Notes |
|---|---|---|---|
| 1 | Confirm prerequisites | §0 | `python3 --version` ≥ 3.9; `which claude`; Telegram account. |
| 2 | Verify clone location | §1 | `~/news-fetch` recommended. NOT `~/Documents/` (iCloud EINTR risk). |
| 3 | Install Python deps | §2 | `python3 -m venv venv`, `pip install curl_cffi`. Verify `import curl_cffi` works. |
| 4 | Create Telegram bot | §3 | User does this in Telegram with @BotFather. Wait for them to confirm token + Start. |
| 5 | Get chat_id | §4 | `curl getUpdates`. If empty, user sends "hi" to bot first. |
| 6 | Configure `.env` | §5 | `cp .env.example .env`, `chmod 600`. Test with `echo "test" \| ./send_telegram.sh`. |
| 7 | FT cookie *(optional)* | §6 | Cookie-Editor → Export as Header String → save to `ft_cookie.txt` (`chmod 600`). Test with a real article URL from `ft.com/markets?format=rss`. |
| 8 | WSJ cookie *(optional)* | §7 | Same pattern, swap to `wsj.com`. Save to `wsj_cookie.txt`. |
| 9 | Customise `routine-prompt.md` | §8 | Find-replace `<USER_NAME>` and `<PROJECT_DIR>`. Ask if they want to keep finance framing or change beat (point to CUSTOMISATION.md). |
| 10 | Claude Code permission allowlist | §9 | Edit `~/.claude/settings.json`. Always `cp` a backup first. Replace path placeholders with their real `<PROJECT_DIR>`. |
| 11 | Trust the project folder | §10 | Add `hasTrustDialogAccepted: true` entry to `~/.claude.json` projects map. **User must quit + reopen Claude Code** for it to re-read. |
| 12 | (OPTIONAL) pmset daily wake | §11 | **Skip in manual-trigger mode (recommended).** Only run if user explicitly wants autonomous cron-fire: `sudo pmset repeat wakeorpoweron MTWRFSU 10:55:00`. Warn that Low Power Mode breaks this silently. |
| 13 | Create scheduled task | §12 | Use `mcp__scheduled-tasks__create_scheduled_task`. taskId `news-fetch-daily-brief`, prompt reads `<PROJECT_DIR>/routine-prompt.md`. **Default to manual-trigger** — omit `cronExpression`. Only add `cron 0 11 * * *` if the user did step 12 and explicitly wants autonomous mode. |
| 14 | Run Now to validate | §13 | Sidebar → Scheduled → Run Now. Wait 5–7 min. Confirm Telegram message + new file in `archive/`. This is also how the user runs the brief day-to-day in manual mode. |

## Common diagnostics

| Symptom | Likely cause | Fix |
|---|---|---|
| No Telegram message | Bot token wrong | Re-check `.env` step 6 |
| `## ERROR:` next to FT/WSJ stories in archive | Cookie expired | Redo step 7 / 8 |
| Permission prompts mid-run | Allowlist incomplete | Add missing entries (step 10) |
| "Folder is not trusted" | Trust didn't take | Step 11 again, then quit+reopen Claude Code |
| Run shown but no archive | Run was stopped early | Let it run full duration |
| (Autonomous-mode only) Task didn't fire | Mac off / Claude Code not running / Low Power Mode | Recommend switching to manual-trigger. Or: disable Low Power Mode, leave Claude Code open, keep Mac on charger |

When the user's first Telegram brief lands cleanly, **the setup is complete**. Tomorrow's automatic run fires without intervention.

## After setup

Point the user at `CUSTOMISATION.md` for tuning theme dictionary, geography weighting, section sizes, and view-forming question style after a week of usage.

## Style for this skill

- Be concrete. Exact commands, not "configure your settings".
- Verify each step before moving on.
- When you can't run something safely (involves secrets, requires UI), stop and ask.
- Keep responses short — user is reading and acting in parallel.
