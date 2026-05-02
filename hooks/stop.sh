#!/bin/bash
# Claude Code Stop hook — generates HTML report from today's tool log

LOG_DIR="${HOME}/.claude/work_logs"
TODAY=$(date +%Y%m%d)
LOGFILE="${LOG_DIR}/${TODAY}.jsonl"
REPORT="${LOG_DIR}/report_${TODAY}.html"

[ -f "$LOGFILE" ] || exit 0

python3 "$(dirname "$0")/../generate_report.py" "$LOGFILE" "$REPORT"

echo "[hooks/stop] 作業日報を生成しました: $REPORT"
