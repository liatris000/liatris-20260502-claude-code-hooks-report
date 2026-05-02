#!/bin/bash
# Claude Code PostToolUse hook
# stdin: {"session_id":"...","tool_name":"...","tool_input":{...},"tool_response":{...}}

LOG_DIR="${HOME}/.claude/work_logs"
mkdir -p "$LOG_DIR"

TODAY=$(date +%Y%m%d)
LOGFILE="${LOG_DIR}/${TODAY}.jsonl"

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name','unknown'))" 2>/dev/null || echo "unknown")
SESSION_ID=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('session_id','')[:8])" 2>/dev/null || echo "")

# Extract exit code for Bash tool
EXIT_CODE=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
resp = d.get('tool_response', {})
if isinstance(resp, dict):
    print(str(resp.get('exit_code', '')))
else:
    print('')
" 2>/dev/null || echo "")

ENTRY=$(python3 -c "
import json, datetime
entry = {
    'ts': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    'event': 'tool_result',
    'tool': '${TOOL_NAME}',
    'session': '${SESSION_ID}',
    'exit_code': '${EXIT_CODE}'
}
print(json.dumps(entry, ensure_ascii=False))
")

echo "$ENTRY" >> "$LOGFILE"
