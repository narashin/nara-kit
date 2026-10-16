---
name: nara-grill
description: >-
  Pressure-test an idea, plan, design, ticket, or RFC by researching facts first, then asking every currently answerable decision in one round, deferring only questions that depend on an open answer.
  Silence is never consent; no source is mutated. Verdict: confirmed | pending | aborted | Blocked.
  USE FOR: "grill", "찔러줘", "이 설계 구멍", "설계 검증", "설계 리뷰", "design review", "API 설계 검토", "리팩터링 계획 검토", "모듈 경계", "계획 반박해줘", brainstorm/design exploration before committing.
  DO NOT USE FOR: 외부 SoT 로컬화 (→ nara-prep), AC 초안 생성 (→ nara-ac-draft), 코드 리뷰 (→ nara-code-review), 작업 분할·계획 (→ nara-plan).
---

# nara-grill — 집중 검증

> 출력 형식은 [nara-kit 출력 계약](../nara-now/references/output-contract.md)을 따른다. 이 본문이 다르게 정한 곳은 본문이 우선한다. 파일이 없으면(단독 설치) 이 줄은 건너뛴다.

아이디어·계획·설계·티켓·RFC를 사실 조사 후 검증한다. 질문은 **지금 답할 수 있는 것을 한 라운드에 모두** 묻고, 다른 답에 달린 질문만 미룬다.

## 계약

사용자의 명시적 답변 또는 확인 가능한 근거 없이 결정을 확정하거나 적용하지 않는다. **침묵·다음 질문으로의 진행·과거 유사 답변은 동의가 아니다.** 사실 근거는 사용자를 대신해 선택을 승인하지 않는다. 소스를 수정하거나 문서·티켓·ADR을 만들지 않는다.

1. 요청과 제공된 자료를 읽는다.
2. 코드·환경에서 확인 가능한 사실을 **먼저** 조사한다. 사용자에게 사실을 묻지 않는다. 조사는 결정을 바꿀 수 있는 사실까지만 한다. 검토 대상이나 대화에 **수치 주장**이 등장하고 그 근거가 될 CSV가 있으면, 그 값을 `nara-claim-audit`으로 읽기 전용 대조한 뒤 결과를 질문 근거로 쓴다 (교체하지 않는다). 수치 주장이 없거나 CSV가 없으면 이 대조는 하지 않는다.
3. 사용자만 결정할 수 있는 미해결 사항을 **결정 트리**로 정리한다. 지금 추측 없이 답할 수 있는 결정 전부가 이번 라운드의 **frontier**다. 다른 결정의 답이나 아직 조사 중인 사실에 걸린 결정은 그 갈래만 미룬다.
4. frontier를 한 라운드에 묻는다. 질문마다 번호(`Q1`, `Q2`)와 고를 수 있는 안, 권고와 짧은 이유를 붙인다. 서로 독립된 질문만 묶는다. 질문 블록이 응답의 마지막 블록이고, 뒤에는 답 형식 안내 한 줄만 둔다.
5. 답을 반영하고 트리를 다시 계산한다: 새로 드러난 가정, 답끼리의 모순, 이제 풀린 의존 질문. 다음 frontier를 묻는다. 이미 답한 질문은 반복하지 않는다.
6. 끝내기 전 **완료 점검**: 트리 전체에서 안 본 갈래, 숨은 가정, 모순이 남았는지 본다. 남았으면 그것이 다음 frontier다.
7. **공유 이해 확인**: 결정·이유·의도적으로 열어 둔 가정을 짧게 요약해 보여 주고, 사용자가 그 요약이 맞다고 확인한 결정만 `confirmed`로 둔다.
8. 합의 전에 구현하거나 문서를 수정하지 않는다.

대상이 설계(구현 전 설계, 대규모 리팩터링 계획, API 설계, 모듈 경계)면 사실 조사와 질문 선정에 [design-probes](references/design-probes.md)의 압박 축을 사용한다. 이미 코드 diff가 존재하면 이 스킬이 아니라 `nara-code-review`로 리다이렉트한다.

같은 domain 용어가 다른 의미로 쓰이거나 인접 개념 구분이 결정에 필요하면 그 의미를 질문한다. 확정된 용어는 이후 `nara-prep`/`nara-ac-draft` 산출물에 담을 수 있지만, 이 스킬은 glossary·domain 문서·ADR을 자동 생성·수정하지 않는다.

사용자가 멈추면 완료로 보고하지 않고 `pending`(답변 대기) / `aborted`(사용자 중단) / `Blocked`(충돌 또는 필수 근거 부족) 중 하나로 보고한다.

## 출력

질문 라운드 중간 응답은 섹션 헤더 없이 쓴다: 조사한 사실, 가정, 미룬 질문(무엇에 걸렸는지), 질문 블록 순서. 아래 섹션과 Receipt는 결정이 확정되거나 사용자가 멈췄을 때의 최종 보고에 쓴다.

내용이 있는 섹션만 사용한다: `## Decisions` / `## Assumptions` / `## Remaining risks` / `## Receipt`. Receipt에는 각 결정과 `confirmed | pending | aborted | Blocked`, 사용자 답변 또는 근거 위치(`파일:라인`), 적용 여부를 기록한다. 미룬 질문이 있으면 무엇에 걸려 있는지 함께 적는다.

**다음**: 결정이 확정되면 `/nara-plan`. 구조 결정이 있었으면 `/nara-adr`.

Provenance: frontier 라운드, 의존 갈래 보류, 완료 점검, 공유 이해 확인은 tiger-kit `tk-grill`(MTGVim/tiger-kit `5e35b6a`, MIT)에서 가져왔다. 판정 4종과 "침묵은 동의가 아니다"는 nara-kit 쪽 계약이다.
