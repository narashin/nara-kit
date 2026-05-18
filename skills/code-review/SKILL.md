---
name: code-review
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
```

This is a contract enforcement gate — without trailing status, the review is considered incomplete.

## Auto-chain: Adversarial Review

After the final report, automatically invoke `codex:adversarial-review` (if codex plugin available):
1. Pass the review report as context
2. Codex challenges findings — looking for missed issues, false negatives, overly generous assessments
3. Append adversarial findings to the report

If codex unavailable, skip silently and note "adversarial review skipped" in report.
