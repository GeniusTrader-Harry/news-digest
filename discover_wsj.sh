#!/usr/bin/env bash
# Wrapper around discover_wsj.py that activates the project venv first.
# Usage:  discover_wsj.sh [--max N] [--section URL]...
# Output: one wsj.com article URL per line on stdout.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/venv/bin/activate"
exec python3 "$SCRIPT_DIR/discover_wsj.py" "$@"
