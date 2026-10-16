---
name: nara-handoff
description: >-
  Record where this session stopped — in-progress threads, open questions, verification state, next safe step — into docs/handoff.md by merging with the previous handoff, so the next session's nara-now resumes without re-deriving context.
  USE FOR: "handoff", "인계", "여기까지 남겨", "이어서 할 수 있게", "세션 끊기 전에", "다음 세션용 메모", "세션 마무리" when work is unfinished.
  DO NOT USE FOR: 배운 것·실수에서 재발 방지 찾기 (→ nara-retro), 다음 할 일 추천 (→ nara-now), 결정 기록 (→ nara-adr), 메모리 정리 (→ nara-grooming).
---

# handoff: 어디서 멈췄나를 남긴다

> 출력 형식은 [nara-kit 출력 계약](../nara-now/references/output-contract.md)을 따른다. 이 본문이 다르게 정한 곳은 본문이 우선한다. 파일이 없으면(단독 설치) 이 줄은 건너뛴다.

다음 세션이 코드와 커밋만으로는 복원할 수 없는 흐름을 `docs/handoff.md` 한 장에 남긴다. 다음 세션의 `nara-now`가 이 파일을 가장 먼저 읽는다. 단기 인계 계약이라 할 일이 다 풀리면 파일을 지운다.

배운 것, 반복된 실수, 규칙·메모리로 남길 지식은 이 스킬의 몫이 아니다. 그런 후보가 보이면 receipt 끝에 `/nara-retro`를 한 줄로 권하고 직접 쓰지 않는다.

## 1. 수집

1. **기존 `docs/handoff.md`**: 있으면 먼저 읽는다. 미해소 In Progress와 Open Questions는 carry-forward 후보다. 이번 세션이 실제로 해소한 항목만 지운다. 안 건드린 항목은 그대로 둔다.
2. **세션**: 이번 대화에서 하다 만 일, 답 없이 남은 질문, 검증한 것과 못 한 것.
3. **Git**: 브랜치, `git rev-parse HEAD`, `git status --short` 파일 수. 코드 변경 나열은 하지 않는다. 커밋으로 복원되는 정보다.
4. **`docs/gap.md`**: 있으면 점수와 Agreed Exceptions. Agreed Exception이 이번 세션에 바뀌었으면 gap.md에도 반영한다.
5. **`docs/implementation-notes.md`**: 있으면 `Open questions` 절만 가져온다. `## Reconciliation Log`에서 이미 해소된 항목은 건너뛴다. 파일은 지우지 않는다(PR 리뷰 참고용).

## 2. 쓸지 판정

| 상태 | 동작 |
|---|---|
| In Progress 또는 Open Questions가 하나라도 남음 | 9절 스키마로 merge write |
| carry-forward 후에도 둘 다 비었음 | 파일 삭제. 삭제가 실패하면 stale 경고만 남기고 강제 삭제하지 않는다 |
| 파일도 없고 남은 것도 없음 | 아무것도 안 쓰고 `handoff: 없음` |

통째 덮어쓰기는 금지다. 무관한 다음 세션이 이전의 미완 작업을 지우는 교차 세션 손실을 막는다.

## 3. 쓰기

- 스키마와 작성 규칙: [references/handoff-schema.md](references/handoff-schema.md).
- 🔴 **CHECKPOINT: write 전 preview.** 무엇을 추가·유지·제거하는지 diff로 먼저 보여 준다. 승인 대기는 아니다. 보여 준 뒤 진행한다.
- 검증 상태는 이번 세션에서 실행해 확인한 것과 가정한 것을 나눈다. 미검증을 done으로 쓰지 않는다.
- baseline SHA는 필수다. 다음 세션의 `nara-now`가 이 값으로 stale을 판정한다.

## 4. Receipt

```
인계 기록 (applied).
- artifact: `docs/handoff.md` (baseline: <sha>)
- in progress: <n> (carry-forward <k>, 신규 <m>, 해소 제거 <r>)
- open questions: <n>
- next: 다음 세션 `/nara-now`
```

배운 것이나 재발 방지 후보가 보였으면 마지막에 `- retro 후보: <한 줄> → /nara-retro`를 붙인다. 없으면 그 줄은 쓰지 않는다.

## 실패 처리

| 트리거 | 대응 |
|---|---|
| git 저장소 아님 | context 절에 `branch: unknown`, `HEAD: unknown`을 적고 계속. 다음 세션의 stale 판정은 불가로 표시 |
| 기존 handoff가 스키마와 다름 | 읽을 수 있는 항목만 carry-forward하고, 못 읽은 원문은 맨 끝 `## 미분류 이전 내용` 절에 그대로 보존 |
| 해소 여부를 확신 못 함 | 지우지 않고 유지. 항목 끝에 `(해소 확인 필요)` |
