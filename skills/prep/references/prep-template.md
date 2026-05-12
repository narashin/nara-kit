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
- [ ] [blocking] {구현 진행 불가한 미결 사항}
- [ ] [nice-to-have] {있으면 좋지만 없어도 진행 가능한 미결 사항}

## Agreed Exceptions
{의도적으로 구현하지 않기로 한 항목. gap 분석 시 이 항목은 갭으로 취급하지 않음}
```
