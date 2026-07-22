---
name: nara-rfc
description: >-
  Generate a complete RFC document in Korean Markdown for technical decisions and feature proposals.
  USE FOR: "rfc", "RFC 작성", "기술 결정 문서", "설계 문서 써줘", "/nara-rfc TICKET-ID".
  DO NOT USE FOR: ADR (use /nara-adr), code implementation, PR creation.
---

# rfc — RFC 문서 작성

You are a senior software engineer and tech lead.

## Steps

1. TICKET-ID 인자 확인. 없으면 유저에게 질문.
2. 유저에게 배경, 문제, 제안 내용 인터뷰 (최대 3회 왕복).
3. 아래 RFC v2 템플릿의 모든 섹션을 채워 `docs/rfc/<TICKET-ID>-rfc.md`에 작성.
4. "Work to do" 항목은 검증 가능하게 (what/where/condition) 기술.
5. 유저 확인 후 파일 저장.

## Rules

- Do not invent business requirements.
- Convert unstructured notes into actionable items.
- Add acceptance hints when useful (e.g., "when X, UI hides Y").
- **저장 파일 본문에는 RFC Markdown만** 담는다 (메타 설명·잡담 없이). 이 규칙은 파일 *내용* 계약일 뿐 — Steps 2·5의 인터뷰·사용자 확인·파일 저장은 반드시 수행한다 (chat-only 덤프 금지).

## Error Handling

- TICKET-ID 미제공 → 유저에게 티켓 ID 질문 후 대기.
- 배경 정보 불충분 → 추가 인터뷰로 명확화. 추측 금지.
- `docs/rfc/` 디렉토리 없음 → 자동 생성.

# {TICKET-ID} - [RFC] {제목}

- Status: Draft | Review | Done
- Author: {이름}
- Created At: {YYYY-MM-DD}
- Related Ticket / Doc: {링크(들)}

---

## 1. Background
### Current Behavior
- ...
### Problem
- ...
### Assumptions / Constraints
- ...

---

## 2. Goal
- ...

---

## 3. Proposal (Summary)
- ...

---

## 4. Work to do

### Common
- ...

### Backend
- ...

### Frontend
- ...

---

## 5. User / UX Notes (Optional)
- ...

---

## 6. Impact & Risk
### Impact
- ...
### Risk & Mitigation
- ...

---

## 7. Open Questions
- [ ] ...
