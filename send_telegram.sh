#!/usr/bin/env bash
# Reads markdown briefing on stdin and sends it to Telegram in <=4000-char chunks,
# splitting at blank-line boundaries when possible so sections aren't cut mid-paragraph.
# Usage:  cat briefing.md | ./send_telegram.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: $ENV_FILE not found" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$ENV_FILE"

: "${TELEGRAM_BOT_TOKEN:?TELEGRAM_BOT_TOKEN missing in .env}"
: "${TELEGRAM_CHAT_ID:?TELEGRAM_CHAT_ID missing in .env}"

API="https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage"
MAX_CHARS=3800   # below the 4096 hard limit, leaves room for markdown overhead

# Read all of stdin
INPUT="$(cat)"

if [[ -z "$INPUT" ]]; then
  echo "ERROR: empty input on stdin" >&2
  exit 1
fi

# Split into chunks at blank lines, never exceeding MAX_CHARS.
python3 - "$INPUT" "$MAX_CHARS" <<'PY' | while IFS= read -r -d '' chunk; do
import sys
text, max_chars = sys.argv[1], int(sys.argv[2])
paragraphs = text.split("\n\n")
chunks, buf = [], ""
for p in paragraphs:
    candidate = (buf + "\n\n" + p) if buf else p
    if len(candidate) <= max_chars:
        buf = candidate
    else:
        if buf:
            chunks.append(buf)
        # If a single paragraph exceeds max_chars, hard-split it
        while len(p) > max_chars:
            chunks.append(p[:max_chars])
            p = p[max_chars:]
        buf = p
if buf:
    chunks.append(buf)
for c in chunks:
    sys.stdout.write(c + "\0")
PY
  # Send each chunk
  curl -sS -X POST "$API" \
    --data-urlencode "chat_id=${TELEGRAM_CHAT_ID}" \
    --data-urlencode "text=${chunk}" \
    --data-urlencode "parse_mode=Markdown" \
    --data-urlencode "disable_web_page_preview=true" \
    -o /tmp/telegram_resp.json

  if ! grep -q '"ok":true' /tmp/telegram_resp.json; then
    echo "Markdown send failed, retrying as plain text:" >&2
    cat /tmp/telegram_resp.json >&2
    echo >&2
    curl -sS -X POST "$API" \
      --data-urlencode "chat_id=${TELEGRAM_CHAT_ID}" \
      --data-urlencode "text=${chunk}" \
      --data-urlencode "disable_web_page_preview=true" \
      -o /tmp/telegram_resp.json
    if ! grep -q '"ok":true' /tmp/telegram_resp.json; then
      echo "ERROR: Telegram send failed even as plain text" >&2
      cat /tmp/telegram_resp.json >&2
      exit 1
    fi
  fi
  sleep 0.3   # gentle pacing to avoid Telegram rate limits
done

echo "OK: briefing sent."
