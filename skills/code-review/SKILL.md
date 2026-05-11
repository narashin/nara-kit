---
name: code-review
description: "5-agent parallel code review covering architecture, correctness, reliability, security, and test coverage. Use when the user asks to '리뷰해줘', 'code review', 'PR 리뷰', 'review this', 'PR 올리기 전에 확인', '배포 전 확인', or before merging any significant change. Returns findings grouped by severity (High/Medium/Low) with file:line references. Stack-specific checklists available for Next.js, TypeScript, Node.js, Spring Boot, Python, DB migrations, and Infra."
---

# Code Review Skill (5-Agent Iterative)

Senior code reviewer role. Flag only what is traceable to specific code — do not infer bugs from naming alone. If unsure whether a pattern is intentional, raise as open question, not a finding.

## Input

Review scope: git diff, PR changed files, or files explicitly named by the user.
When scope is unclear, ask before reviewing.

## Finding Format

Each finding: `[Severity] path/to/file:line — description (one line)`

**Examples:**
- `[High] queries/user.ts:34 — fetch() called directly. Must go through libs/fetch.ts for auth cookies.`
- `[Medium] components/List.tsx — duplicates existing <EmptyState>. Reuse from components/common/.`
- `[Low] constants/api.ts:12 — magic number 3000. Extract as REQUEST_TIMEOUT constant.`

## 5-Agent Loop

Run all 5 in parallel, then synthesize findings.

1. **Architecture** — boundaries, dependency direction, cohesion
2. **Correctness** — logic errors, state handling, edge cases
3. **Reliability** — failure modes, retries, timeouts, rollback safety
4. **Security** — auth/authz, secret handling, input validation, unsafe defaults
5. **Test** — coverage quality, missing scenarios, brittle assertions

All agents also apply cross-cutting checks. See `references/cross-cutting.md`.

## Output Contract

Return in this order:
1. Findings grouped by severity (High → Medium → Low), each with file:line reference.
2. Open questions (patterns that may be intentional).
3. One-paragraph change summary.

If no findings: state "No critical findings" explicitly, then mention residual risk and testing gaps.

## Severity Levels

- **High**: production-impacting bug/risk, data/security issue, breaking behavior.
- **Medium**: likely bug, missing guardrail, significant maintainability risk.
- **Low**: minor inconsistency or non-blocking improvement.

## Iteration Rules

- Run at least one full 5-agent pass.
- If High findings exist, run a second pass on touched areas.
- Keep findings concrete and actionable.

## Checklist Discipline

- Do not weaken acceptance criteria.
- Do not suggest deleting failing tests without root-cause analysis.
- Prefer minimal, targeted fixes.
- Flag only what is visible in the diff — do not audit untouched code. Pre-existing issues in diff-touched files may be surfaced as Low with an explicit scope caveat.
- When asking for scope, list accepted input formats: file paths, git diff, or PR link.

## References

- **`references/cross-cutting.md`** — Log Hygiene, Pattern Consistency, Doc-Code Alignment checks (load for every review)
- **`references/stack-specific.md`** — Load when codebase uses Next.js, TypeScript, Node.js, Spring Boot, Python, DB migrations, or Infra changes
