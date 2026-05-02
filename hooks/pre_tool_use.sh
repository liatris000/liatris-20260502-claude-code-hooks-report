#!/bin/bash
# Claude Code PreToolUse hook
# stdin: {"session_id":"...","tool_name":"...","tool_input":{...}}

LOG_DIR="${HOME}/.claude/work_logs"
mkdir -p "$LOG_DIR"

TODAY=$(date +%Y%m%d)
LOGFILE="${LOG_DIR}/${TODAY}.jsonl"

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name','unknown'))" 2>/dev/null || echo "unknown")
SESSION_ID=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('session_id','')[:8])" 2>/dev/null || echo "")

ENTRY=$(python3 -c "
import json, datetime
entry = {
    'ts': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    'event': 'tool_call',
    'tool': '${TOOL_NAME}',
    'session': '${SESSION_ID}',
    'cwd': '$(pwd)'
}
print(json.dumps(entry, ensure_ascii=False))
")

echo "$ENTRY" >> "$LOGFILE"
