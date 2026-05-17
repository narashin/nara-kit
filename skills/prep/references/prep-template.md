# prep — Input Sources & Output Template

## 입력 소스

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

## Raw 원문 템플릿 (`docs/sources/<id>.raw.md`)

`<id>` 규칙: Jira는 `proj-123` (소문자), Confluence는 page-id, Figma는 file-key, 기타는 슬러그.

```markdown
---
source_id: {id}
source_url: {원본 URL}
source_type: jira | confluence | figma | linear | web | text
fetched_at: {ISO8601 timestamp}
fetched_by: prep skill
source_hash: {SHA-256 첫 16자 — 본문 기준}
---

{fetched 원문 verbatim. 의역/요약/재정렬/번역 절대 금지.}
{Jira: description + acceptance criteria 원문 그대로}
{Confluence: 본문 그대로 (HTML→MD 변환만 허용, 내용 변형 금지)}
{Figma: 노드 트리 + 텍스트 콘텐츠 + 컴포넌트명 원문}
```

## 출력 템플릿 (`docs/requirements.md`)

```markdown
---
created: {ISO8601}
updated: {ISO8601}
sources:
  - id: {source-id-1}
    url: {URL-1}
    raw_file: docs/sources/{id-1}.raw.md
    fetched_at: {ISO8601}
    source_hash: {SHA-256 첫 16자}
  - id: {source-id-2}
    url: {URL-2}
    raw_file: docs/sources/{id-2}.raw.md
    fetched_at: {ISO8601}
    source_hash: {SHA-256 첫 16자}
status: Draft | Reviewed
---

# Requirements

> 원문 검증 필요 시: `docs/sources/<id>.raw.md` 참조 (verbatim).

## Background
{배경 및 현재 상태 — raw에서 추출 또는 인용}

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
- [ ] [blocking] {구현 진행 불가한 미결 사항}
- [ ] [nice-to-have] {있으면 좋지만 없어도 진행 가능한 미결 사항}

## Agreed Exceptions
{의도적으로 구현하지 않기로 한 항목. gap 분석 시 이 항목은 갭으로 취급하지 않음}
```
