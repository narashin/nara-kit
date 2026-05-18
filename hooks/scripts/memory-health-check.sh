#!/usr/bin/env bash
# SessionStart hook: silently audit memories. Surface flag count via systemMessage.
# Runs from any project directory. Skips if memory dir not found.
#
# Reads JSON from stdin (Claude Code hook input) but only needs `cwd` field.

set -euo pipefail

input=$(cat)
cwd=$(echo "$input" | jq -r '.cwd // ""')

if [[ -z "$cwd" ]]; then
  echo '{"continue": true, "suppressOutput": true}'
  exit 0
fi

# Build project slug = absolute path with / replaced by -
slug=$(echo "$cwd" | sed 's|/|-|g')
mem_dir="$HOME/.claude/projects/$slug/memory"

if [[ ! -d "$mem_dir" ]]; then
  echo '{"continue": true, "suppressOutput": true}'
  exit 0
fi

# Locate audit script — it lives in the plugin install
audit_script="${CLAUDE_PLUGIN_ROOT:-}/skills/memory-audit/scripts/audit.sh"
if [[ ! -f "$audit_script" ]]; then
  echo '{"continue": true, "suppressOutput": true}'
  exit 0
fi

flagged=0
total=0
for f in "$mem_dir"/*.md; do
  [[ -e "$f" ]] || continue
  [[ "$(basename "$f")" == "MEMORY.md" ]] && continue
  total=$((total + 1))
  score=$(bash "$audit_script" --log "$f" 2>/dev/null | jq -r '.score // 0')
  if [[ "$score" -ge 2 ]]; then
    flagged=$((flagged + 1))
  fi
done

if [[ $flagged -gt 0 ]]; then
  jq -nc \
    --arg msg "메모리 health: ${flagged}/${total} 건 flag됨 (score>=2). \`/memory-audit\` 검토 권장." \
    '{continue: true, suppressOutput: true, systemMessage: $msg}'
else
  echo '{"continue": true, "suppressOutput": true}'
fi
