# Implementation Notes Gate (scope-scaled)

구현 중 **spec ↔ 코드 drift**를 추적하는 running log. `medium`/`large` scope에서 execute 진입 시 `docs/implementation-notes.md`를 자동 생성한다.

> 이 계약은 원래 `nara-workflow-dev-mode`가 들고 있었으나, 실사용 측정 결과 그 스킬이 60일간 1회 호출된 반면 `nara-implement`는 실제로 실행되므로 이리로 옮겼다. 파일 경로·섹션명·카테고리 정의는 **바뀌지 않았다** — `nara-gap --verify`와 `nara-reflect`가 같은 구조를 계속 읽는다.

## 파일 구조

```markdown
# Implementation Notes

> Spec: docs/requirements.md
> Started: {ISO 8601 timestamp}

## Design decisions
- {ID} {결정 한 줄} — Why: {spec 모호점 어떻게 해석} — Where: {file:line}

## Deviations
- {ID} {스펙 어김} — Why: {의도된 사유} — Where: {file:line}

## Tradeoffs
- {ID} {선택 A vs B} — Picked: A — Why: {기준}

## Open questions
- {ID} {질문 한 줄} — Type: `confirm` | `revise` — Context: {결정 내릴 정보 부족 사유 또는 spec 수정 제안 근거}

## Reconciliation Log

> Written by `nara-gap --verify`. Do not edit manually.
> Tracks which notes entries above have been resolved to gap.md outcomes. Prevents `/nara-reflect` from re-processing already-resolved entries.

| Note ID | Mapped Gap Item | Resolution | Date | Source |
|---|---|---|---|---|
```

`Type`:
- `confirm` — 유저 확인만 받으면 진행 가능 (예: "이 동작 의도 맞나요?")
- `revise` — spec 자체 수정이 필요할 수 있는 항목 (예: "AC2 재시도 3회는 운영상 부족, 5회로 revise 검토 요청")

## 강제 메커니즘 (contract)

**0. Scope scaling (먼저 판정):**
- `small` (1-2 files, 단일 관심사) → Implementation Notes Gate **전체 skip**: 파일 생성 안 함, trailing `📝` 없음, verify gate 미적용. verify 시 "small scope — notes skipped" 1줄 표기.
- `medium` / `large` → 아래 1-3 전부 적용.

**1. Pre-flight (execute 진입 시, medium/large only):**
- `docs/implementation-notes.md` 없으면 빈 4섹션 헤더로 생성 후 다음 도구 호출
- 이미 있으면 그대로 사용. 기존 entry ID 최댓값 +1로 다음 ID 부여 (예: DD-3 있으면 다음은 DD-4)

**2. Trailing status (매 코드 변경 응답 끝, medium/large only):**
```
📝 notes: +N <type>(<ID 또는 한 줄 요약>), +N <type>(...)
```
- `<type>`: `design` | `deviation` | `tradeoff` | `open Q`
- 변경 없으면: `📝 notes: no new entries this turn`
- ID 부여 권장 (`DD-1`, `DEV-1`, `TO-1`, `OQ-1` 등) — 추적·후속 인용 친화

예시:
```
📝 notes: +1 design(DD-1 notification_id를 X-Notification-Id 헤더로), +2 tradeoff(TO-1 nodemailer 채택, TO-2 transporter 싱글톤)
```

**3. State gate (verify 진입 시, medium/large only):**
- `small` scope → gate 미적용 (notes 없이 verify 통과).
- `docs/implementation-notes.md` 미존재 → reject
- 파일 존재 + **4섹션 모두 빈 헤더만** (entry 0건) → reject
- 4섹션 중 **최소 1개 섹션에 entry 1개 이상** → accept (entry 수 임계 없음)
- "implementation-notes 작성 후 verify 재시도" 안내

## 카테고리 정의

원본 출처: Thariq (@trq212) on Twitter/X (2026-05). 원문 정의를 보존하며 표현만 한국어로.

| 카테고리 | When |
|---|---|
| Design decisions | spec이 모호한 지점에서 내가 내린 선택 (choices you made where the spec was ambiguous) |
| Deviations | spec과 의도적으로 다르게 구현한 부분 **+ 그 이유** (places where you intentionally departed from the spec, and why) |
| Tradeoffs | 검토한 대안 **+ 왜 이걸 골랐는지** (alternatives you considered and why you picked what you did) |
| Open questions | 유저가 **확인하거나 spec을 수정**하길 원할만한 사항 (anything you'd want me to confirm or revise) |

**핵심 4 카테고리는 원본 정의 그대로 유지.** 표현/예시 추가는 가능, 의미 변경 금지.

## 후속 산출물 chain

- `Deviations` → ADR 후보 (구조적 변경 시 `/nara-adr` 호출)
- `Open questions` → 다음 세션 `/nara-now`가 surface
- `Design decisions` → `/nara-reflect`가 메모리 승격 평가
- `Tradeoffs` → code-review 시점에 리뷰어가 확인

## 형식

- `.md` (HTML 아님). LLM friendly, grep/diff 친화
- 종료 시 HTML 변환 옵션은 별도 (현 스킬 범위 밖)
