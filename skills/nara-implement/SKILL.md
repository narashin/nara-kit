---
name: nara-implement
description: >-
  Implement an approved code change under a verification gate, then stop at staged — never auto-commit.
  Supports a TDD option (red→green) and direct/delegated execution. Verdict: Pass | Fail | Blocked | Unverifiable.
  USE FOR: "구현", "implement", "execute", "이 계획대로 짜줘", "작업 단위 구현", dev-mode execute step.
  DO NOT USE FOR: 테스트 코드만 생성 (→ nara-test-implement), 장애 수정 (→ nara-incident-fix), 커밋 메시지 (→ nara-commit), 원인 불명 버그 (→ nara-incident).
---

# nara-implement — 검증 게이트 구현

승인된 전략 없이 파일을 수정하지 않는다. 순서를 지킨다:

```text
understand → inspect → strategy approval → implement → verify → stop at staged → report
```

실제로 읽지 않은 출처나 실행하지 않은 검증을 "통과했다"고 보고하지 않는다. 입력 우선순위: 현재 요청 → 확정된 결정 → `docs/plan.md` → `docs/requirements.md` → CLAUDE.md → 코드/테스트.

## 1. 전략 승인 (수정 전 필수 게이트)

수정 전 관련 코드·테스트·상태를 **비파괴적으로** 조사한다(파일 생성·수정·삭제, 에이전트 실행 금지). 이후 실행 모드(`direct`|`delegated`)와 TDD 여부를 이유와 함께 **한 번에** 제안하고 승인을 기다린다. **구현 지시(예: "구현해줘") 자체는 전략 승인이 아니다** — mode/TDD 미지정이면 제안 후 대기, 요청에 이미 명시됐거나 사용자가 즉시 진행을 승인했으면 다시 묻지 않고 진행한다. 판단 기준·제안 형식은 [실행 세부](references/execution-detail.md).

## 2. 구현과 검증

승인 모드로 가장 작은 일관 단위씩 구현하고 focused verification을 반복한다. TDD 승인 시 **실제 실행해 red를 관찰한 뒤** 최소 구현으로 green — 사후에 테스트를 붙여 TDD라 부르지 않는다. non-TDD에서도 검증을 생략하지 않는다. 완료 후 가장 넓은 관련 검증을 한 번 실행하고 실패를 `change-related`/`pre-existing`/`environment`/`unverifiable`로 분류한다. 고위험 변경에만 독립 reviewer 1회(review→fix→regression). 상세: [실행 세부](references/execution-detail.md).

## 3. 정지와 보고 (커밋 금지)

**자동 커밋·push·PR·merge·tag·release·publish 금지.** change-related 검증이 성공하면 변경을 staged 상태로 두고 정지한 뒤 `/nara-commit`을 다음 단계로 제시한다. 다른 사용자 호출형 스킬도 자동 실행하지 않는다.

change-related 실패가 남으면 `Fail`, 입력·권한·결정이 없으면 `Blocked`, 검증했으나 증거를 못 얻으면 `Unverifiable`. 이 상태를 완료로 보고하지 않는다. **`Pass`는 실행한 검증 증거로만** — 증거 없이 성공을 자기선언(self-adjudicate)하지 않는다. 못 얻으면 `Pass`가 아니라 `Unverifiable`.

`## Strategy` / `## Changed`(동작 설명) / `## Verification`(명령·결과·실패 분류) / `## Remaining risks` / `## Receipt`(상태 `Pass|Fail|Blocked|Unverifiable`, Evidence는 `파일:라인`)로 보고한다.
