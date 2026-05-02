# claude-code-hooks-report

Claude Code の Hooks を使って、毎日の作業ログを自動記録し HTML 日報を生成するツールです。

## デモ

👉 **[デモページを見る](https://liatris000.github.io/liatris-20260502-claude-code-hooks-report/)**

## 仕組み

```
Claude Code セッション
  ↓ PreToolUse hook
  ~/.claude/work_logs/YYYYMMDD.jsonl にログ追記
  ↓ Stop hook
  generate_report.py でHTML生成
  → report_YYYYMMDD.html
```

## セットアップ

```bash
# 1. フックスクリプトをコピー
mkdir -p ~/.claude/hooks
cp hooks/*.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.sh

# 2. generate_report.py をコピー
cp generate_report.py ~/.claude/

# 3. Claude Code の settings.json にフック設定を追記
# 設定ファイルの場所: ~/.claude/settings.json
# settings-example.json の内容を参考に追記する
```

## 生成されるファイル

| ファイル | 説明 |
|---|---|
| `~/.claude/work_logs/YYYYMMDD.jsonl` | ツール呼び出しログ |
| `~/.claude/work_logs/report_YYYYMMDD.html` | HTML 日報 |

## 手動でレポートを生成する場合

```bash
python3 generate_report.py ~/.claude/work_logs/20260502.jsonl report.html
```

## Zenn 記事

詳細は → https://zenn.dev/liatris
