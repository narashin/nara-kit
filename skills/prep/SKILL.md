---
name: prep
description: Localize external source-of-truth (Jira ticket, Confluence page, Figma URL, Linear issue, PRD text) into docs/requirements.md. Use when starting a new task that has an external spec. Triggers on "prep", "/prep TICKET-ID", Jira URL, Confluence URL, Figma URL, "요구사항 정리", "스펙 로컬화".
version: 0.1.0
---

# prep — 외부 SoT를 로컬 요구사항 문서로 변환

외부 Source of Truth(Jira, Figma, PRD 등)를 `docs/requirements.md`로 로컬화한다.
이후 세션에서 원본 재fetch 없이 이 문서만 참조하여 토큰을 절약한다.

## 입력

`$ARGUMENTS`에서 소스를 파싱한다:

| 패턴 | 소스 타입 | 도구 |
|------|----------|------|
| Jira URL 또는 티켓 ID (예: `PROJ-123`) | Jira 이슈 | `mcp__jira__jira_get_issue` |
| Confluence URL | Confluence 페이지 | `mcp__confluence__confluence_get_page` |
| Figma URL (`figma.com/...`) | Figma 디자인 | `mcp__figma-remote-mcp__get_design_context` |
| Linear URL 또는 ID | Linear 이슈 | `mcp__linear__get_issue` |
| 기타 URL | 웹 문서 | WebFetch |
| 텍스트 | 구두 PRD | 그대로 구조화 |

인자 없으면 사용자에게 소스 URL/텍스트 요청.

## 실행

1. **소스 수집**: 위 도구로 외부 SoT 내용 가져오기 (병렬 가능)
2. **구조화**: 아래 템플릿으로 변환
3. **저장**: `docs/requirements.md`에 Write
4. **확인**: 요약 테이블 출력 (소스별 추출 항목 수 + [UNVERIFIED] 건수 + Open Questions 건수)

## 출력 템플릿 (`docs/requirements.md`)

```markdown
# Requirements

- Source: {원본 URL/티켓}
- Created: {날짜}
- Status: Draft | Reviewed

## Background
{배경 및 현재 상태}

## Goal
{달성 목표}

## Functional Requirements
- [ ] FR-1: {기능 요구사항}

## Non-Functional Requirements
- [ ] NFR-1: {성능/보안/접근성 등}

## UI/UX Requirements
- [ ] UX-1: {UI 요구사항}

## API/Data Requirements
- [ ] API-1: {API 스펙}

## Out of Scope
- {명시적 범위 밖 항목}

## Open Questions
- [ ] {미결 사항}

## Agreed Exceptions
{의도적으로 구현하지 않기로 한 항목. gap 분석 시 이 항목은 갭으로 취급하지 않음}
```

## 규칙

- **창작 금지**: 원본에 없는 요구사항 생성 금지. `[UNVERIFIED]`는 원본 언급은 있으나 세부사항 불명확한 경우만.
- **확신 없으면 표기**: `[UNVERIFIED: <이유>]`. 억측으로 채우지 않음.
- Figma: 화면명, 컴포넌트명, 인터랙션 흐름만. 색상/간격 등 시각 디테일 제외.
- Jira: description + acceptance criteria + 기술 결정사항만. 일반 논의/질문 제외.
- 비어있는 섹션도 헤더 유지. "없음" 한 줄 기재.
- `Agreed Exceptions` 섹션 필수 — gap 분석의 false positive 방지 핵심.
- `docs/requirements.md` 이미 존재하면 덮어쓰기 전 사용자 확인.
