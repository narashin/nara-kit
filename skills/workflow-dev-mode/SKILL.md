---
name: workflow-dev-mode
description: >-
  Implementation-first workflow with structured gates: SoT → gap → TDD → verify → branch finish.
  USE FOR: "dev mode", "구현 워크플로우", "개발 모드", "feature implementation".
  DO NOT USE FOR: docs-only artifacts (→ workflow-doc-mode), unstable requirements (→ interview), simple edits.
---

# Workflow Dev Mode

Implementation-first workflow (router classifies `dev`).

## Use when

bugfix / feature / refactor / impl delivery, 코드·설정·테스트 변경, design stable.

## Decision rules

1. Confirm implementation workflow.
2. Classify scope (모호 시 상향): `small` (1-2 files, single concern) / `medium` (3-10 files, single domain) / `large` (10+ files, multi-domain).
3. Walk the **mandatory core spine** (each step emits human-verifiable material): `gap → plan → execute → verify → code-review → reflect`. Pull conditional satellites (`prep` / `ac-draft` / `brainstorming` / `adr`) only by trigger — see Execution.

## Execution

**Entry (conditional):**
- **외부 SoT (URL/티켓) 있음** → `prep` (SoT fetch)
- **외부 SoT 없음, 한 줄 의도만** → `ac-draft` (US + Gherkin AC 생성)
- Readiness 2-3/4 → `ac-draft` (AC 보강) 또는 `ooo interview` (optional, ambiguity 크면) → `/prep` 재실행
- Readiness 0-1/4 → 의도 자체 명확화 우선 (`ac-draft` 또는 사용자 인터뷰)
- **`superpowers:brainstorming` (조건부)** — scope `large` 또는 greenfield/design 불안정일 때만. `small`/bugfix는 skip. (선택, superpowers; visual companion 포함)

**Entry 완료(SoT면 `prep`, thin intent면 `ac-draft`로 AC 확정 — Readiness 4/4) → 아래 core spine 진입.**

**Core spine (mandatory) — 항상 `gap`부터 순서대로:**
- `gap` → `plan` → `execute` → `verify` → `code-review` → `reflect`
- **plan**: 작성 후 AskUserQuestion 승인을 plan 단계에서 흡수 (별도 pre-execution phase 없음). 승인 후 execute.
- **execute**: `superpowers:SDD` default, `ooo run`/`auto` fallback. Implementation Notes Gate 적용 (scope-scaled, 아래).
- **reflect** 이후: `adr` (구조 결정 있었을 때만) → branch finish.

**제거됨**: `ooo evaluate` (완료 전 AI 점수 판정 = AI-as-judge 안티패턴). `verify` + `code-review`가 검증 담당.

## Gates

- Plan approval: plan 단계에 흡수된 AskUserQuestion 승인 ([상세](references/pre-execution-gate.md)). 별도 phase 아님.
- Component Pick: 카탈로그 5단계 ([상세](references/component-pick-procedure.md))
- **Implementation Notes Gate (scope-scaled, 아래)**

AskUserQuestion은 plan 승인에만. 라우팅/분기는 평문.

## Implementation Notes Gate (scope-scaled)

`medium`/`large` scope에서 Execute 단계 진입 시 `docs/implementation-notes.md` 자동 생성 (`small`은 skip — 아래 scope scaling). 구현 중 spec ↔ 코드 drift 추적용 running log.

### 파일 구조

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

> Written by `gap --verify`. Do not edit manually.
> Tracks which notes entries above have been resolved to gap.md outcomes. Prevents `/reflect` from re-processing already-resolved entries.

| Note ID | Mapped Gap Item | Resolution | Date | Source |
|---|---|---|---|---|
```

`Type`:
- `confirm` — 유저 확인만 받으면 진행 가능 (예: "이 동작 의도 맞나요?")
- `revise` — spec 자체 수정이 필요할 수 있는 항목 (예: "AC2 재시도 3회는 운영상 부족, 5회로 revise 검토 요청")

### 강제 메커니즘 (contract)

**0. Scope scaling (먼저 판정):**
- `small` (1-2 files, 단일 관심사) → Implementation Notes Gate **전체 skip**: 파일 생성 안 함, trailing `📝` 없음, verify gate 미적용. verify 시 "small scope — notes skipped" 1줄 표기.
- `medium` / `large` → 아래 1-3 전부 적용.

**1. Pre-flight (Execute 진입 시, medium/large only):**
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

### 카테고리 정의

원본 출처: Thariq (@trq212) on Twitter/X (2026-05). 원문 정의를 보존하며 표현만 한국어로.

| 카테고리 | When |
|---|---|
| Design decisions | spec이 모호한 지점에서 내가 내린 선택 (choices you made where the spec was ambiguous) |
| Deviations | spec과 의도적으로 다르게 구현한 부분 **+ 그 이유** (places where you intentionally departed from the spec, and why) |
| Tradeoffs | 검토한 대안 **+ 왜 이걸 골랐는지** (alternatives you considered and why you picked what you did) |
| Open questions | 유저가 **확인하거나 spec을 수정**하길 원할만한 사항 (anything you'd want me to confirm or revise) |

**핵심 4 카테고리는 원본 정의 그대로 유지.** 표현/예시 추가는 가능, 의미 변경 금지.

### 후속 산출물 chain

- `Deviations` → ADR 후보 (구조적 변경 시 `/adr` 호출)
- `Open questions` → 다음 세션 `/now`가 surface
- `Design decisions` → `/reflect`가 메모리 승격 평가
- `Tradeoffs` → code-review 시점에 리뷰어가 확인

### 형식

- `.md` (HTML 아님). LLM friendly, grep/diff 친화
- 종료 시 HTML 변환 옵션은 별도 (현 스킬 범위 밖)

**Load** [references/dev-workflow-details.md](references/dev-workflow-details.md) for routing table, output contract, examples, hallucination guards.
