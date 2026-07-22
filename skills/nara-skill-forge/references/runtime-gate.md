# Runtime-Neutrality Gate

nara-kit ships the SAME SKILL.md to Claude Code (`/nara-<skill>`) AND Codex
(`$nara-<skill>`). A body that hardcodes one runtime misleads the other agent's
parser — it may read "in Claude Code" and conclude "not for me".

## Scan (Phase 0)

```bash
grep -nE "(in Claude Code|Claude Code skill|Claude Code only|Cursor only|Codex only|~/\.claude/skills/[a-z]|/plugin install)" \
  skills/<name>/SKILL.md skills/<name>/references/*.md 2>/dev/null
```

Non-empty output = red flag → make Phase 4 round 1 a P0 `runtime-lock` fix.
Ignore hits inside `runtime-gate.md` itself — it quotes the patterns it scans
for, so self-hits are always false positives.

## Red vs allowed

| Red flag (fix) | Allowed (skip) |
|---|---|
| "in Claude Code", "Claude Code skill/user" prose | frontmatter trigger phrases |
| Install path pinned to one runtime only | nara-kit ecosystem skill-name refs (`/nara-…`, `$nara-…`) |
| Single-runtime badge | section explicitly marked runtime-specific |
| Hardcoded `~/.claude/skills/…` with no neutral equivalent | commit-message / repo-release prose |

## Fix pattern

- Runtime-specific verb → neutral ("dispatch a subagent", not "use the Claude
  Code Agent tool").
- Path pinned to `.claude/` → describe the artifact and let each runtime resolve it.
- Exception — a skill name explicitly bound to one runtime (e.g. `*-codex`): the
  gate does not apply.
