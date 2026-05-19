---
name: workflow-dev-mode
description: >-
  Run implementation-first workflow enforcing structured gates from SoT localization through gap analysis, TDD, verification, and branch finish.
  USE FOR: "dev mode", "구현 워크플로우", "implementation workflow", "개발 모드", "feature implementation".
  DO NOT USE FOR: documentation-only artifacts (→ workflow-doc-mode), design exploration without stable requirements (→ ooo interview or superpowers:brainstorming), simple one-file edits (→ direct edit).
---

# Workflow Dev Mode

Implementation-first workflow (router classifies `dev`).

## Use when

bugfix / feature / refactor / impl delivery, 코드·설정·테스트 변경, design stable.

## Decision rules

1. Confirm implementation workflow.
2. Classify scope (모호 시 상향): `small` (1-2 files, single concern) / `medium` (3-10 files, single domain) / `large` (10+ files, multi-domain).
3. Walk gates: SoT -> discovery -> gap -> plan -> pre-execution -> TDD -> verify.

## Execution

- External req -> `prep` (SoT fetch)
- Readiness 4/4 -> `superpowers:brainstorming` -> `gap`; 2-3/4 -> `ooo interview` -> `/prep`; 0-1/4 -> `ooo interview` 필수
- `backlog/` + Level 1 -> `/backlog decompose`. 없으면 `gap` full
- plan per subtask -> Pre-execution gate -> execute
- **Execute 진입 시: `docs/implementation-notes.md` 생성 (pre-flight, 빈 템플릿)** ← Implementation Notes Gate 참조
- Execute: `superpowers:SDD` default, `ooo run`/`auto` fallback. **각 응답 끝 trailing `📝 notes: +N` 강제**
- Subtask 완료 -> `/backlog done` (auto-verify)
- 완료 -> `ooo evaluate` -> `code-review` -> `reflect` (notes 흡수) -> `adr` -> branch finish

## Gates

- Pre-execution: plan + AskUserQuestion 승인 ([상세](references/pre-execution-gate.md))
- Component Pick: 카탈로그 5단계 ([상세](references/component-pick-procedure.md))
- **Implementation Notes Gate (필수, 아래)**

AskUserQuestion은 Pre-execution gate에만. 라우팅/분기는 평문.

## Implementation Notes Gate (필수)

Execute 단계 진입 시 `docs/implementation-notes.md` 자동 생성. 구현 중 spec ↔ 코드 drift 추적용 running log.

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
- {ID} {유저 확인 필요} — Context: {결정 내릴 정보 부족 사유}
```

### 강제 메커니즘 (contract)

**1. Pre-flight (Execute 진입 시):**
- `docs/implementation-notes.md` 없으면 빈 4섹션 헤더로 생성 후 다음 도구 호출

**2. Trailing status (매 코드 변경 응답 끝):**
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

**3. State gate (verify 진입 시):**
- `docs/implementation-notes.md` 미존재 → reject
- 파일 존재 + **4섹션 모두 빈 헤더만** (entry 0건) → reject
- 4섹션 중 **최소 1개 섹션에 entry 1개 이상** → accept (entry 수 임계 없음)
- "implementation-notes 작성 후 verify 재시도" 안내

### 카테고리 정의

| 카테고리 | When |
|---|---|
| Design decisions | spec이 모호한데 내가 결정함 |
| Deviations | spec과 다르게 구현함 (의도된 차이) |
| Tradeoffs | 대안 검토 후 선택 |
| Open questions | 유저 확정 필요 사항 |

### 후속 산출물 chain

- `Deviations` → ADR 후보 (구조적 변경 시 `/adr` 호출)
- `Open questions` → 다음 세션 `/now`가 surface
- `Design decisions` → `/reflect`가 메모리 승격 평가
- `Tradeoffs` → code-review 시점에 리뷰어가 확인

### 형식

- `.md` (HTML 아님). LLM friendly, grep/diff 친화
- 종료 시 HTML 변환 옵션은 별도 (현 스킬 범위 밖)

**Load** [references/dev-workflow-details.md](references/dev-workflow-details.md) for routing table, output contract, examples, hallucination guards.
