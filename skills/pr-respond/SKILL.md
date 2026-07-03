---
name: pr-respond
description: >-
  Analyze and respond to PR review comments by technically verifying each, then accepting, rebutting, or holding.
  USE FOR: "리뷰 대응", "PR 리뷰", "리뷰 코멘트", "respond to review", "handle review feedback".
  DO NOT USE FOR: creating PRs, requesting code review, merging branches.
---

# PR Review Response

Systematically analyze and respond to PR review comments. Verify each comment technically before deciding accept, rebut, or hold.

**Core principle**: `receiving-code-review` superpowers -- no performative agreement, no unverified acceptance, technical accuracy first.

## Input

| Argument | Action |
|----------|--------|
| (none) | Auto-detect PR from current branch |
| `<PR#>` or `<URL>` | Use specified PR |
| `--dry-run` | Analysis + draft only, no code changes or replies |
| `--status` | List unreplied comments only |

## Decision Rules

1. **Classify** each comment: blocking / suggestion / question / nitpick / praise (skip praise)
2. **Verify in codebase**: read file:line, check if issue is real, check tests, git blame
3. **Decide**:
   - Technically valid -> **ACCEPT** (but side-effect analysis first, then implement one at a time)
   - Reviewer lacks context or technically inaccurate -> **REBUT** (evidence-based, no defensive tone)
   - Uncertain or architecture decision needed -> **HOLD** (present analysis, delegate to user)
   - Conflicts with spec/source-of-truth, or cannot be verified either way -> **ASK** (reply to the reviewer as a question: category + your recommendation + evidence — not a confirmed fix or rebuttal). Distinct from HOLD: HOLD delegates to the *user*, ASK posts to the *reviewer* thread.
4. **Reply** in comment thread (`gh api .../comments/{id}/replies`), never top-level

## Hard Rules

- No "You're right!", "Great point!", "Thanks!" -- only "Fixed." or technical explanation
- Side-effect analysis mandatory before accepting (trace callers, check tests, API contracts)
- Implement one comment at a time, verify, then next
- No auto-commit -- suggest commit message only
- Related comments -> holistic judgment, no partial accepts
- Cannot verify or conflicts with source-of-truth -> ASK the reviewer (question + recommendation + evidence), never assert as confirmed defect or rebuttal

## References

- [7-phase execution procedure](references/procedure.md)
- [Output format](references/output-format.md) (standard, --dry-run, --status)
- [Worked examples](references/examples.md)
