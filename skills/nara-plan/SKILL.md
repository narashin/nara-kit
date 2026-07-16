---
name: nara-plan
description: >-
  Split a spec or request into independently verifiable VERTICAL work units — each with its own goal, scope, acceptance criteria, and verification — written to docs/plan.md.
  This is the dev-mode plan step. Never implements code or posts to a remote tracker.
  USE FOR: "plan", "계획 짜줘", "작업 나눠", "수직 분할", "작업 단위로 쪼개", dev-mode plan step.
  DO NOT USE FOR: 스펙 작성 (→ nara-prep / doc-mode), 구현 (→ nara-implement), 원격 Jira 티켓 생성 (→ nara-slack-to-jira).
---

# nara-plan — 수직 작업 단위 분할

요청이나 스펙을 **독립적으로 검증 가능한 수직 작업 단위**로 나눠 구현 계획을 만든다.

소스 우선순위: 사용자 지정 소스 → 현재 대화 → `docs/requirements.md` → 요청 → 관련 코드. 구현하거나 원격 트래커에 게시하지 않는다.

## 계약

- 요구사항별 **source traceability**를 남긴다 (어느 요구사항 → 어느 작업 단위).
- 각 작업 단위는 독립적인 목표·범위·인수 기준(AC)·검증을 가진 **수직 슬라이스**로 구성한다 (그 동작에 필요한 타입·API·UI·테스트를 한 단위에 포함).
- 동작의 테스트는 해당 단위에 포함한다. **수평적인 type-only / API-only / UI-only / test-only 단위를 만들지 않는다.**
- 독립 동작으로 분할할 근거가 부족하면 억지로 만들지 않고 `Unresolved split report`를 반환한다.
- 근거 없는 요구사항이나 미해결 충돌은 `Blocked` 또는 `Unverifiable`로 구분한다.

## 산출물

`docs/plan.md`에 `# <Feature> Plan` 형식으로 작성한다 (사용자가 경로를 지정하면 그 경로). 각 작업 단위: `## T-N <제목>` + `목표` / `범위(포함·제외)` / `AC` / `검증` / `의존성` / `요구사항 추적`.

## 출력 (receipt)

경로, 상태, 작업 단위 수, 요구사항별 traceability, 의존성, `증거`, `미검증`, 미해결 분할 문제를 보고한다. 이후 단계로 `/nara-implement <작업 단위>`를 제시한다.
