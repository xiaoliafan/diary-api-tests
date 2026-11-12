#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$ROOT"

REPORT_DIR="${REPORT_DIR:-reports}"
mkdir -p "$REPORT_DIR"

PYTEST="$ROOT/.venv/bin/pytest"
if [ ! -x "$PYTEST" ]; then
    PYTEST="pytest"
fi

"$PYTEST" ui_tests \
    --html="$REPORT_DIR/ui-report.html" \
    --self-contained-html \
    "$@"
