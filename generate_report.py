#!/usr/bin/env python3
"""
Claude Code work log -> HTML report generator
Usage: python3 generate_report.py <logfile.jsonl> <output.html>
"""
import json
import sys
from collections import Counter
from datetime import datetime, timezone

def load_log(path):
    entries = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return entries

def build_report(entries, output_path, report_date=None):
    calls = [e for e in entries if e.get("event") == "tool_call"]
    tool_counter = Counter(e["tool"] for e in calls)
    sessions = list({e["session"] for e in calls if e.get("session")})

    if not report_date:
        report_date = datetime.now().strftime("%Y-%m-%d")

    total_calls = len(calls)

    # Determine timeline
    times = []
    for e in calls:
        try:
            ts = datetime.strptime(e["ts"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            times.append(ts)
        except Exception:
            pass
    duration_str = ""
    if len(times) >= 2:
        delta = max(times) - min(times)
        minutes = int(delta.total_seconds() // 60)
        duration_str = f"{minutes}分"

    # Top tools bar chart data
    top_tools = tool_counter.most_common(8)
    max_count = max((c for _, c in top_tools), default=1)

    bars_html = ""
    colors = ["#6C8EFF","#5CE6C8","#FF7E7E","#FFD166","#A78BFA","#34D399","#F97316","#64748B"]
    for i, (tool, count) in enumerate(top_tools):
        pct = int(count / max_count * 100)
        color = colors[i % len(colors)]
        bars_html += f"""
        <div class="bar-row">
          <span class="bar-label">{tool}</span>
          <div class="bar-wrap">
            <div class="bar" style="width:{pct}%; background:{color};">{count}</div>
          </div>
        </div>"""

    # Recent calls timeline
    timeline_rows = ""
    for e in reversed(calls[-20:]):
        tool = e.get("tool", "-")
        ts_raw = e.get("ts", "")
        try:
            ts_dt = datetime.strptime(ts_raw, "%Y-%m-%dT%H:%M:%SZ")
            ts_display = ts_dt.strftime("%H:%M:%S")
        except Exception:
            ts_display = ts_raw
        cwd = e.get("cwd", "")
        session = e.get("session", "")
        timeline_rows += f"""
        <tr>
          <td class="ts">{ts_display}</td>
          <td><span class="badge">{tool}</span></td>
          <td class="dim">{cwd}</td>
          <td class="dim">{session}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Claude Code 作業日報 {report_date}</title>
<style>
  :root {{
    --bg: #0f1117;
    --card: #1a1d2e;
    --border: #2a2d3e;
    --text: #e2e8f0;
    --dim: #8892a4;
    --accent: #6C8EFF;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Segoe UI', system-ui, sans-serif;
    padding: 2rem;
    min-height: 100vh;
  }}
  h1 {{ font-size: 1.6rem; font-weight: 700; margin-bottom: 0.25rem; }}
  .subtitle {{ color: var(--dim); font-size: 0.9rem; margin-bottom: 2rem; }}
  .stats-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
  }}
  .stat-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem;
  }}
  .stat-card .label {{ color: var(--dim); font-size: 0.75rem; text-transform: uppercase; letter-spacing: .05em; }}
  .stat-card .value {{ font-size: 2rem; font-weight: 700; color: var(--accent); margin-top: 0.3rem; }}
  .section {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }}
  .section h2 {{ font-size: 1rem; margin-bottom: 1rem; color: var(--dim); text-transform: uppercase; letter-spacing: .05em; }}
  .bar-row {{ display: flex; align-items: center; margin-bottom: 0.6rem; gap: 0.75rem; }}
  .bar-label {{ width: 110px; font-size: 0.82rem; flex-shrink: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
  .bar-wrap {{ flex: 1; background: rgba(255,255,255,.05); border-radius: 6px; overflow: hidden; height: 22px; }}
  .bar {{ height: 100%; border-radius: 6px; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px; font-size: 0.75rem; font-weight: 600; color: #fff; transition: width .4s ease; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.83rem; }}
  th {{ text-align: left; color: var(--dim); font-weight: 500; padding: 0.4rem 0.6rem; border-bottom: 1px solid var(--border); }}
  td {{ padding: 0.4rem 0.6rem; border-bottom: 1px solid rgba(255,255,255,.04); vertical-align: middle; }}
  .ts {{ font-family: monospace; color: var(--dim); white-space: nowrap; }}
  .dim {{ color: var(--dim); font-family: monospace; font-size: 0.75rem; max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
  .badge {{ background: rgba(108,142,255,.18); color: var(--accent); border-radius: 6px; padding: 2px 8px; font-size: 0.78rem; font-family: monospace; }}
  footer {{ text-align: center; color: var(--dim); font-size: 0.75rem; margin-top: 2rem; }}
</style>
</head>
<body>
<h1>Claude Code 作業日報</h1>
<p class="subtitle">{report_date} &nbsp;·&nbsp; 自動生成 by Stop Hook</p>

<div class="stats-grid">
  <div class="stat-card">
    <div class="label">ツール呼び出し数</div>
    <div class="value">{total_calls}</div>
  </div>
  <div class="stat-card">
    <div class="label">セッション数</div>
    <div class="value">{len(sessions)}</div>
  </div>
  <div class="stat-card">
    <div class="label">稼働時間</div>
    <div class="value">{duration_str or "-"}</div>
  </div>
  <div class="stat-card">
    <div class="label">使用ツール種類</div>
    <div class="value">{len(tool_counter)}</div>
  </div>
</div>

<div class="section">
  <h2>ツール使用頻度</h2>
  {bars_html}
</div>

<div class="section">
  <h2>直近の作業タイムライン</h2>
  <table>
    <thead><tr><th>時刻</th><th>ツール</th><th>ディレクトリ</th><th>セッション</th></tr></thead>
    <tbody>{timeline_rows}</tbody>
  </table>
</div>

<footer>Generated by <a href="https://github.com/liatris000/liatris-20260502-claude-code-hooks-report" style="color:var(--accent)">claude-code-hooks-report</a></footer>
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html)
    print(f"Report written to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: generate_report.py <input.jsonl> <output.html>")
        sys.exit(1)
    entries = load_log(sys.argv[1])
    build_report(entries, sys.argv[2])
