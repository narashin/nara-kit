# Test Verify Output Format

Write to: `docs/test-scenarios/scenarios-review.md`

## Synthesis Process

1. Collect QA Lead findings
2. Collect Developer findings
3. Collect Red Team findings
4. Deduplicate: if QA Lead and Developer flag the same scenario for different reasons, merge into one item with both reasons
5. Sort all findings by severity (High → Medium → Low)
6. Generate Summary Verdict based on:
   - PASS: 0 High findings, ≤ 2 Medium findings
   - NEEDS_WORK: 1-2 High findings OR 3+ Medium findings
   - FAIL: 3+ High findings

## Template

```markdown
# Test Scenario Review Report

- Source: {input file name}
- Date: {YYYY-MM-DD}
- Reviewers: QA Lead, Developer, Red Team

## Summary Verdict
- Overall: PASS | NEEDS_WORK | FAIL
- Coverage assessment: {S3/S2 ratio evaluation or [S2 baseline not available]}
- Prior review: {if prior review section exists in source file: "Prior review found — findings [align/diverge] on [key items]". Otherwise omit this line.}
- Key gaps: {top 3 findings summarized}

## QA Lead Findings
### High
- {finding with scenario ID}
### Medium
- ...
### Low
- ...

## Developer Findings
### High
- ...
### Medium
- ...
### Low
- ...

## Red Team Findings
### Surviving Bug Paths
- {description}
### Additional Scenario Proposals
- [{ID}] {title}
### Adversarial Assessment
- {overall risk and confidence}

## Consolidated Action Items
- [ ] {actionable item derived from High findings}
- [ ] {actionable item derived from Medium findings}
...
```

## Example Findings

**QA Lead finding (High):**
```
CRUD 커버리지 갭: Delete 시나리오 0건. 주문 취소/삭제 경로 미검증.
영향: 취소 후 재고 복원, 결제 환불 흐름 전체 미테스트.
제안: [API-ORD-013] 주문 취소 시 재고 복원과 환불 상태 전이를 검증한다
```

**Developer finding (Medium):**
```
[API-ORD-008] 동시 주문 재고 정합성 — flaky risk HIGH.
이유: 테스트 환경에서 동시성 재현 불안정. sleep 기반 타이밍 의존.
제안: DB lock 단위 테스트로 대체하거나, retry + assertion 패턴 적용.
```

**Red Team finding:**
```
Surviving bug path: 할인코드 만료 시각과 주문 시각이 동시인 경계값.
[API-ORD-001]은 유효 할인만 테스트. 만료 직전/직후 1초 경계 미검증.
제안: [API-ORD-014] 할인코드 만료 경계(±1초)에서 주문 시 적용 여부를 검증한다
```
