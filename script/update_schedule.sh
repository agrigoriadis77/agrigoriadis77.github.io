#!/usr/bin/env bash
# Usage: ./script/update_schedule.sh path/to/schedule.xlsx
# Run from the repo root.

VENV="$HOME/scheduleenv"
SCRIPT="$(dirname "$0")/xls_to_schedule_data.py"

if [ ! -f "$VENV/bin/python3" ]; then
    echo "🔧  Creating venv at $VENV ..."
    python3 -m venv "$VENV"
    "$VENV/bin/pip" install -q openpyxl xlrd
    echo "✅  venv ready"
fi

"$VENV/bin/python3" "$SCRIPT" "$@"

