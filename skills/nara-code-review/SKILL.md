---
name: nara-code-review
description: >-
  Multi-agent parallel code review + auto-fix for local commits.
  USE FOR: "리뷰해줘", "코드 검수", "버그 찾아줘", "review code", "check for bugs",
  "audit code", "cleanup", or after finishing code changes before committing.
  DO NOT USE FOR: PR review on remote (use review skill), general refactoring,
  or documentation-only changes.
---

# Code Review — 5-Agent Iterative Review & Auto-Fix

5 specialist agents review code in parallel, fix issues, then re-review fixes in an iterative loop until convergence.

## Flow

0. **Load project override** (if `.claude/overrides/code-review.md` exists) — see "Project Override" below
1. **Collect changes** + parse arguments — [phases](references/phases.md)
2. **Gather context** (full files, types, tests, reusable code) — [phases](references/phases.md)
3. **Launch 5 agents in parallel** via Agent tool — [agents](references/agents.md)
   - logic | type-safety | error-handling | architecture | security-performance
   - Each agent receives base checklist + project override (if loaded) as a single merged prompt
4. **Aggregate & filter** (confidence >= threshold, merge duplicates) — [fix-loop](references/fix-loop.md)
5. **Auto-fix -> re-review -> converge** (max 3 rounds) — [fix-loop](references/fix-loop.md)
6. **Final report** in Korean, saved to `./docs/review/YYMMDD-<desc>.md` — [fix-loop](references/fix-loop.md)

## Key Rules

- **All report output MUST be in Korean (한국어)**
- Confidence >= 80 required (speculative concerns stay at 50 or below)
- Iterative convergence: loop stops when clean, max rounds hit, no progress, or only suggestions remain
- See [cross-cutting](references/cross-cutting.md) and [stack-specific](references/stack-specific.md) for additional checklists

## Project Override (Step 0)

Convention: project-local checks live in `.claude/overrides/code-review.md` (in the cwd of the project being reviewed, not in nara-kit).

```bash
# Run before Step 1
test -f .claude/overrides/code-review.md && cat .claude/overrides/code-review.md
```

Behavior:
- **Exists**: read body. Inject as "project-specific checklist" block into every agent prompt in Step 3. Apply alongside base checks.
- **Missing**: skip silently. No fallback fetch, no remote lookup.
- **Conflict resolution**: override never disables a base check. It can only add, raise severity, or narrow scope.

Override file format (example structure projects should follow):

```markdown
# Project: <name> — code-review override

## Stack-specific checks
| 항목 | 심각도 | 기준 |
|------|--------|------|
| ... | ... | ... |

## Local static analysis (optional)
\`\`\`bash
npx tsc --noEmit
pnpm lint
\`\`\`

## Project rules
- bullet rules
```

## Output Status (mandatory trailing line)

Final report must end with:

```
overrides: applied (.claude/overrides/code-review.md)   # when loaded
overrides: none                                          # when missing
claimed-vs-observed: match | MISMATCH (<n> claimed-but-unchanged, <m> changed-but-unclaimed)
```

This is a contract enforcement gate — without trailing status, the review is considered incomplete.

## Claimed-vs-Observed Gate (auto-fix 검증)

auto-fix 라운드(Flow step 5)에서 에이전트가 "고쳤다"고 보고한 것을 그대로 믿지 않는다. 각 라운드 종료 후:

1. `git diff --name-only` → **관측된** 변경 경로 집합
2. 에이전트가 fix했다고 **주장한** 경로 집합과 대조
3. 불일치 시 escalate (applied로 보고 금지):
   - 주장했으나 미변경 (claimed-but-unchanged) → fix 실패 또는 환각
   - 변경됐으나 미주장 (changed-but-unclaimed) → scope 이탈 / 의도치 않은 변경

self-report는 후보, `git diff`가 심판. 불일치는 최종 리포트에 `→ ESCALATE:`로 표면화하고 위 trailing status에 반영.

## Adversarial Review (manual follow-up)

After the final report, **suggest the user run `/codex:adversarial-review` themselves** — it cannot be auto-invoked (that command sets `disable-model-invocation`). If they run it:
1. It receives the review report as context
2. Codex challenges findings — missed issues, false negatives, overly generous assessments
3. Append adversarial findings to the report

If codex is unavailable, skip and note "adversarial review skipped" in the report.
