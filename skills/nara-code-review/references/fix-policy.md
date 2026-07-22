# Phase 6: Fix Policy — Risk Tiers & Central Fixer

## Single central Fixer

Exactly ONE Fixer applies changes, serially, in issue-ledger order (critical →
major → minor). Reviewers and the Judge never edit code. Parallel fixing by multiple
agents causes: overwrites, duplicate fixes, divergent design directions,
changed-but-unclaimed false alarms, and untraceable regressions.

The main session may act as the Fixer directly, or delegate to one Fixer subagent —
either way there is one writer, one ordering.

Fix principles:
- Scope each fix to its finding only — no opportunistic refactoring.
- Match existing code style/conventions.
- After each fix, record in the ledger: finding id, files touched, hunks, and the
  claim of what was resolved (Verifier checks the claim — see [verification](verification.md)).

## Risk tiers (fix_risk)

Reviewer-proposed `fix_risk` is a candidate; the Fixer re-rates against this table
and may only raise, never lower.

| Tier | Examples | Default action |
|---|---|---|
| R0 | import 정리, formatter, 명확한 compile/lint 오류 | 자동 수정 |
| R1 | 로컬 동작 변경 + 재현/회귀 테스트 존재(또는 추가 가능) + 영향 범위 제한 | 테스트 기반 자동 수정 |
| R2 | public API, 비즈니스 동작, transaction, config, dependency | 리포트만 |
| R3 | auth 정책, migration, 데이터 삭제, concurrency 모델, 보안 경계 | 자동 수정 금지 (모드 무관) |

Structural findings (architecture-reuse structural lens) are always R3.

## Fix modes

```
--fix=none       아무것도 수정 안 함 (--report-only 별칭)
--fix=safe       기본값: R0 + 검증 가능한 R1 (회귀 테스트로 증명 가능한 것만)
--fix=selected   사용자가 finding ID를 골라서 승인한 것만
--fix=all        R2까지 허용. R3는 여전히 금지
```

- `severity: suggestion` is NEVER auto-fixed in any mode — auto-fixing suggestions
  turns review into generic refactoring. Report only.
- `auto_fixable: true` from a reviewer is an opinion, not permission. Permission
  comes from `fix_risk` tier × fix mode, after Judge confirmation.
- R1 "verifiable" means: an existing test reproduces the issue, or the Fixer adds a
  regression test alongside the fix. No test → treat as R2.

## Issue ledger

The ledger is the single ordered work queue, keyed by fingerprint:

```yaml
- id: BEH-001
  fingerprint: src/order/service.ts::completeOrder::결제 실패 시 COMPLETED 금지
  severity: major          # Judge's final_severity
  fix_risk: R1
  status: open | fixing | fixed | verified | failed | deferred
  claimed_files: []        # filled by Fixer
  proof: {}                # filled by Verifier
```

Ledger state transitions only move forward via Fixer (open→fixing→fixed) and
Verifier (fixed→verified | failed). Nothing is reported "applied" while unverified.
