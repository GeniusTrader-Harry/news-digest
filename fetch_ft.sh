#!/usr/bin/env bash
# Wrapper around fetch_ft.py that activates the project venv first.
# Usage:  fetch_ft.sh URL [URL ...]
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/venv/bin/activate"
exec python3 "$SCRIPT_DIR/fetch_ft.py" "$@"
