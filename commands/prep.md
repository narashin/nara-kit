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
| 기타 URL | 웹 문서 | `ctx_fetch_and_index` |
| 텍스트 | 구두 PRD | 그대로 구조화 |

인자 없으면 사용자에게 소스 URL/텍스트 요청.

## 실행

1. **소스 수집**: 위 도구로 외부 SoT 내용 가져오기 (병렬 가능)
2. **구조화**: 아래 템플릿으로 변환
3. **저장**: `docs/requirements.md`에 Write
4. **확인**: 요약 테이블 출력 (소스별 추출 항목 수 + [UNVERIFIED] 건수 + Open Questions 건수). 사용자 응답 대기 없이 바로 완료.

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
- [ ] FR-2: ...

## Non-Functional Requirements
- [ ] NFR-1: {성능/보안/접근성 등}

## UI/UX Requirements
- [ ] UX-1: {UI 요구사항 — Figma 참조 시 섹션/컴포넌트 단위로}

## API/Data Requirements
- [ ] API-1: {API 스펙 — 엔드포인트, 페이로드}

## Out of Scope
- {명시적 범위 밖 항목}

## Open Questions
- [ ] {미결 사항}

## Agreed Exceptions
{의도적으로 구현하지 않기로 한 항목. gap 분석 시 이 항목은 갭으로 취급하지 않음}
```

## 예시

<example>
입력: `/prep PROJ-456` (Jira 티켓만)

requirements.md 일부:
```markdown
# Requirements
- Source: https://jira.example.com/browse/PROJ-456
- Created: 2026-05-06
- Status: Draft

## Functional Requirements
- [ ] FR-1: 결재 요청 제출 — 사용자가 양식을 작성하고 제출할 수 있다 (AC-1)
- [ ] FR-2: 결재 승인 — 결재자가 요청을 승인할 수 있다 (AC-2)

## Agreed Exceptions
없음
```

요약 출력:
| Source | FR | UX | [UNVERIFIED] | Open Q |
|--------|----|----|--------------|--------|
| Jira PROJ-456 | 5 | 0 | 0 | 2 |
</example>

## 규칙

- **창작 금지 원칙**: 원본에 언급조차 없는 요구사항은 생성하지 않는다. `[UNVERIFIED]`는 원본에 언급은 있으나 세부사항이 불명확한 경우에만 사용. 원본에 없는 "합리적 추론" 항목은 Open Questions로 이동.
- **확신 없으면 표기**: 요구사항 출처가 명확하지 않으면 `[UNVERIFIED: <이유>]` 표기. 억측으로 채우지 않음.
- Figma: 스크린샷 저장 불필요. 화면명, 컴포넌트명, 인터랙션 흐름만 추출. 색상/간격 등 시각 디테일은 제외.
- Jira: description + acceptance criteria + 코멘트 중 기술 결정사항만. 일반 논의/질문은 제외.
- 비어있는 섹션도 헤더는 유지 (gap 분석 시 섹션 누락 방지). "없음" 한 줄 기재.
- `Agreed Exceptions` 섹션 반드시 포함 — gap 분석의 false positive 방지 핵심.
- `docs/` 디렉토리 없으면 생성.
- `docs/requirements.md` 이미 존재하면 덮어쓰기 전 사용자 확인.

