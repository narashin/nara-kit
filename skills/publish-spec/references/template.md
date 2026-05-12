# Publish Spec Template & Conversion Rules

## Title Format

```
LYRIS-XXX 한줄 설명
```

Examples:
- `LYRIS-337 Additional Dashboard for Release PIC/Master`
- `LYRIS-272 [RfC] 복수의 Manager 할당 시 AND 승인 조건 추가`
- `LYRIS-323 [RfC] Add a comment to the post-approval task history of a ChangeRequest`

Rules:
- Jira ticket ID **필수** — 없으면 유저에게 물어볼 것
- `[RfC]` 태그는 optional (유저 지정 시에만 포함)
- 설명은 간결하게 한 줄

## Body Template (7 Sections)

spec.md 내용을 아래 7개 섹션 구조로 **반드시 변환**. 원본 spec의 섹션 구조가 다르면 매핑해서 재구성할 것. 빈 섹션이라도 헤딩은 유지.

```markdown
# LYRIS-XXX Jira Ticket Summary

Jira Ticket Link: LYRIS-XXX

## 1. Background

### Current Behavior
(현재 동작 방식. spec의 "현재 동작" 또는 기존 구현 설명을 여기에)

### Problem
(해결하려는 문제. spec의 "문제" 섹션)

### Assumptions / Constraints
(전제 조건, 제약사항. spec의 scope/constraints 내용)

## 2. Goal
(이 기능이 달성하려는 목표. 3~5개 bullet)

## 3. Proposal
(제안하는 해결 방법 요약. 상태 매트릭스, 특수 처리 등 포함)

## 4. Work to do

### Common
(FE/BE 공통 정책, 모델 변경 등. 시나리오 기준으로 기술)

### Backend
(BE 시나리오. "Scenario N — 제목: 설명" 형식. 코드 파일/클래스명 금지)

### Frontend
(FE 시나리오. "Scenario N — 제목: 설명" 형식. 코드 파일/클래스명 금지)

## 5. User / UX Notes
(UI 동작 규칙, 조건부 표시, UX 안내 문구 등)

## 6. Impact & Risk
(리스크와 대응 방안. 테이블 권장)

## 7. Open Questions
(미결 사항. 번호 매긴 리스트)
```

## Section Mapping Guide

| spec.md 원본 섹션 | Confluence 템플릿 매핑 |
|---|---|
| Background / 현재 동작 | 1. Background > Current Behavior |
| 문제 / Problem | 1. Background > Problem |
| 요구사항 요약 / Constraints | 1. Background > Assumptions / Constraints |
| User Scenario / Acceptance | 2. Goal (요약) + 5. User / UX Notes (상세) |
| State Scope / 매트릭스 | 3. Proposal |
| UI Design / 모달 / History | 4. Work to do > Frontend (시나리오 기준) + 5. User / UX Notes |
| API Design / BE 요구사항 | 4. Work to do > Backend (시나리오 기준) |
| Checklist / 점검사항 | 6. Impact & Risk + 7. Open Questions |
| Scope 정리 / Phase | 4. Work to do (In Scope) + 7. Open Questions (Out of Scope) |
| File Impact | **Confluence에 포함하지 않음** — 로컬 spec.md에만 유지 |
| Risk & Mitigation | 6. Impact & Risk |

## Conversion Constraints

- spec.md 섹션 구조를 그대로 복사 금지 — 반드시 위 7개 섹션으로 재구성
- 빈 섹션 삭제 금지 — 헤딩은 유지하고 "(없음)" 또는 "-" 표기
- ASCII mockup은 code block으로 감싸서 유지
- TypeScript 타입 정의는 code block으로 유지
- **코드 레벨 참조 금지 (Confluence)**: 파일명, 타입명, 컴포넌트명, 함수명 등 코드 레벨 디테일을 Work to do에 포함하지 않음
  - Confluence: "무엇을 해야 하는가" (what) — 시나리오 기준
  - 로컬 spec.md: "어떻게 해야 하는가" (how) — 코드 레벨 상세
- **언어 분리**: dry-run 프리뷰는 한국어 OK. Confluence 게시 본문은 **영어** 필수. 유저가 한국어 명시 시에만 한국어
