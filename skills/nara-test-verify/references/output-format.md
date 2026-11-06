# Test Verify Output Format

Write to: `docs/test-scenarios/scenarios-review.md`

## Synthesis Process

1. Take the critic's findings as they came; merge two findings only when they cite the same reference for the same reason.
2. Number findings `F-1`, `F-2`, ... in severity order (High → Medium → Low). A later re-check cites these numbers.
3. Verdict from the counts:
   - PASS: 0 High findings, ≤ 2 Medium findings
   - NEEDS_WORK: 1-2 High findings OR 3+ Medium findings
   - FAIL: 3+ High findings
4. Split action items by fix target: `fix: scenario` goes back to the producer; `fix: upstream:<doc>` goes to the Upstream Findings table for the user. This skill edits neither.

## Template

```markdown
# Test Scenario Review Report

- Source: {input file name}
- Date: {YYYY-MM-DD}
- Reviewer: critic (lenses: contract, survivor) · dispatch: {subagent | inline (no subagent tool)}
- Inputs: scenarios · requirements AC/Edge Cases {or [UNVERIFIED: requirements not available]} · plan context {or none} · whitelist {N files}

## Summary Verdict
- Overall: PASS | NEEDS_WORK | FAIL
- Coverage assessment: {discover: ACs with no scenario, or "all AC mapped" | golden-path: atomic-path coverage}
- Prior review: {see SKILL.md Prior Review Handling; omit when there is none}
- Key gaps: {top 3 findings summarized}

## Findings
### High
- F-1 [lens: contract] [fix: scenario] {finding with reference} → {proposed scenario}
### Medium
- ...
### Low
- ...

## Upstream Findings
| 대상 문서 | 절 | 결함 | 제안 변경 | 구분 |
|---|---|---|---|---|
| {doc} | {section or AC-ID} | {defect} | {proposed change} | editorial \| semantic |

## Action Items
- 시나리오 보강 → `{producer skill}` 재실행: {F-numbers}
- 상류 문서 → 사용자가 고칠지 결정: {F-numbers} (semantic은 AC 의미가 바뀌므로 승인 후에만)
```

Omit `## Upstream Findings` when no finding has an upstream fix target.

On a re-check, add `- Re-check of: {prior review date} · changed: {IDs}` under Date, put a `## Prior Findings` section (`F-N: resolved|unresolved|regressed — reason`) before `## Findings`, and number new findings after the prior review's last F-N.

## Example Findings

```
F-1 [lens: contract] [fix: scenario] Delete 시나리오 0건. 주문 취소 경로를 덮는 AC가 있는데 시나리오가 없다.
→ [API-ORD-013] 주문 취소 시 재고 복원과 환불 상태 전이를 검증한다

F-2 [lens: contract] [fix: scenario] [API-ORD-008] 동시 주문 재고 정합성이 sleep 타이밍에 기대 flaky 위험이 높다.
→ DB lock 단위 테스트로 대체

F-3 [lens: survivor] [fix: upstream:requirements (semantic)] 할인코드 만료 시각과 주문 시각이 같은 경계의 기대값이 어느 문서에도 없다. [API-ORD-001]은 유효 할인만 본다.
→ [API-ORD-014] 만료 경계(±1초)에서 주문 시 적용 여부를 검증한다 (기대값은 요구사항이 정해야 함)
```
