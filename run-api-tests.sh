#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$ROOT"

RESULTS_DIR="${RESULTS_DIR:-reports/allure-results}"
REPORT_DIR="${REPORT_DIR:-reports/allure-report}"

PYTEST="$ROOT/.venv/bin/pytest"
if [ ! -x "$PYTEST" ]; then
    PYTEST="pytest"
fi

pytest_status=0
"$PYTEST" tests \
    --alluredir="$RESULTS_DIR" \
    --clean-alluredir \
    "$@" || pytest_status=$?

if command -v allure >/dev/null 2>&1; then
    allure generate "$RESULTS_DIR" --clean -o "$REPORT_DIR"
    echo "Allure 报告：$REPORT_DIR/index.html"
else
    echo "Allure 原始结果：$RESULTS_DIR"
    echo "未检测到 allure 命令，安装 Allure CLI 后可生成 HTML 报告："
    echo "  allure generate $RESULTS_DIR --clean -o $REPORT_DIR"
fi

exit "$pytest_status"
