---
name: nara-grill
description: >-
  Pressure-test an idea, plan, design, ticket, or RFC by researching facts first, then validating decisions one question at a time.
  Silence is never consent; no source is mutated. Verdict: confirmed | pending | aborted | Blocked.
  USE FOR: "grill", "찔러줘", "이 설계 구멍", "설계 검증", "계획 반박해줘", brainstorm/design exploration before committing.
  DO NOT USE FOR: 외부 SoT 로컬화 (→ nara-prep), AC 초안 생성 (→ nara-ac-draft), 코드 리뷰 (→ nara-code-review), 작업 분할·계획 (→ nara-plan).
---

# nara-grill — 집중 검증

아이디어·계획·설계·티켓·RFC를 사실 조사 후 **한 번에 한 질문씩** 검증한다.

## 계약

사용자의 명시적 답변 또는 확인 가능한 근거 없이 결정을 확정하거나 적용하지 않는다. **침묵·다음 질문으로의 진행·과거 유사 답변은 동의가 아니다.** 사실 근거는 사용자를 대신해 선택을 승인하지 않는다. 소스를 수정하거나 문서·티켓·ADR을 만들지 않는다.

1. 요청과 제공된 자료를 읽는다.
2. 코드·환경에서 확인 가능한 사실을 **먼저** 조사한다.
3. 사용자만 결정할 수 있는 미해결 사항을 식별한다.
4. 영향이 가장 큰 질문 **하나**를 권고·짧은 이유와 함께 제시한다.
5. 답변을 반영하고 결정이 수렴할 때까지 하나씩 반복한다. 이미 답한 질문은 반복하지 않는다.
6. 합의 전에 구현하거나 문서를 수정하지 않는다.

같은 domain 용어가 다른 의미로 쓰이거나 인접 개념 구분이 결정에 필요하면 그 의미를 질문한다. 확정된 용어는 이후 `nara-prep`/`nara-ac-draft` 산출물에 담을 수 있지만, 이 스킬은 glossary·domain 문서·ADR을 자동 생성·수정하지 않는다.

사용자가 멈추면 완료로 보고하지 않고 `pending`(답변 대기) / `aborted`(사용자 중단) / `Blocked`(충돌 또는 필수 근거 부족) 중 하나로 보고한다.

## 출력

내용이 있는 섹션만 사용한다: `## Decisions` / `## Assumptions` / `## Remaining risks` / `## Receipt`. Receipt에는 각 결정과 `confirmed | pending | aborted | Blocked`, 사용자 답변 또는 근거 위치(`파일:라인`), 적용 여부를 기록한다.
