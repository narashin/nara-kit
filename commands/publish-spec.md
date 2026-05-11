# publish-spec — 기획문서 Confluence 게시

`docs/plan/spec-*.md` 기획문서를 LYRIS Confluence 템플릿으로 변환하여 게시한다.
게시 전 dry-run으로 변환 결과를 로컬에서 반드시 확인한다.

## 인수 파싱

`$ARGUMENTS` 파싱 (순서 무관, 각 토큰을 패턴 매칭):

| 패턴 | 동작 |
|------|------|
| `https://wiki.workers-hub.com/...` | 게시 위치 부모 페이지 URL |
| `LYRIS-123` 또는 `SRE-123` | Jira 티켓 번호 |
| `spec-calendar-notification` | 파일명 직접 지정 |

예시:
```
/publish-spec https://wiki.workers-hub.com/display/lysre/SomeParent LYRIS-123
/publish-spec https://wiki.workers-hub.com/pages/viewpage.action?pageId=2735095793
```

### Parent Page URL → Page ID 변환

| URL 형식 | 추출 방법 |
|---------|---------|
| `?pageId=XXXXXXX` | URL 파라미터 직접 파싱 |
| `/display/SPACE/Page+Title` | `mcp__confluence__confluence_get_page(title, space_key)` 로 ID 조회 |

## Step 1: 게시 위치 확인

**Parent URL 미제공 시** → AskUserQuestion:
```
어느 Confluence 페이지 하위에 생성할까요?
페이지 URL을 붙여넣어 주세요.
(예: https://wiki.workers-hub.com/display/lysre/Development)
```

URL 수신 후 page ID 추출:
- `pageId=` 파라미터 있으면 직접 사용
- `/display/SPACE/Title` 형식이면 `confluence_get_page(title, space_key)`로 ID 조회
- 조회 실패 시 → 에러 메시지 + 재입력 요청

## Step 2: 문서 탐색

1. `docs/plan/` Glob: `spec-*.md` 파일 목록 확인
2. 없으면 → "`/lyris-orchestrate` → Planning 실행 먼저" 안내 후 **STOP**
3. 여러 파일 존재 + 파일명 미지정 → 목록 출력 후 사용자 선택 요청
4. `.omc/specs/deep-interview-*.md` 존재 시 함께 읽기 (Background/Problem 섹션 보강)

## Step 3: Confluence 템플릿 변환

spec-*.md 내용을 아래 LYRIS 표준 템플릿으로 변환한다.

### 변환 규칙

| Confluence 섹션 | spec-*.md 소스 | 보조 소스 |
|----------------|---------------|---------|
| 페이지 제목 | `LYRIS-XXX {spec 기능명}` | $ARGUMENTS 티켓번호 |
| Jira Ticket Link | $ARGUMENTS 파싱 또는 (미입력 시 빈칸) | — |
| Current Behavior | `## 요약` + deep-interview 배경 | deep-interview |
| Problem | `## 요약`의 현재→목표 gap | deep-interview |
| Assumptions / Constraints | `## 기술 제약` | — |
| Goal | `## 요약` (목표 관점 재작성) | — |
| Proposal | `## 유저 플로우` + `## 페이지 구조 & 컴포넌트` | — |
| Work to do — Scope | `## 수용 기준` 중 아키텍처적으로 명백한 에픽 수준 항목만 | — |
| Work to do — Task Breakdown | **작성 금지** — 구현 착수 시 코드 분석 후 개발자가 채움 | — |
| User / UX Notes | `## 유저 플로우`의 UX 세부사항 | designer 산출물 |
| Impact & Risk | `## 완성도 평가` Ambiguous + Missing Edge Cases | — |
| Open Questions | `## 완성도 평가` Undefined TBD + `## Next Actions` | — |

**티켓 번호 미입력 시:** 페이지 제목을 `{spec 기능명}` 으로 생성 (LYRIS-XXX 없이).

### 변환 출력 형식

```markdown
LYRIS-XXX {feature name}

Jira Ticket Link: {URL or leave blank}

## 1. Background

### Current Behavior
{description of current behavior}

### Problem
{problem description}

### Assumptions / Constraints
{technical constraints and assumptions}

## 2. Goal
{goal description}

## 3. Proposal
{user flow and screen/component design}

## 4. Work to do

### Scope _(planning stage — epic level only)_
{epic-level items only. e.g., "New API endpoint needed", "New page required"}

> **Note:** Common / Backend / Frontend task breakdown to be filled at implementation kickoff after code analysis. Do not fill at planning stage — anchoring prevention.

### Task Breakdown _(to be filled at implementation kickoff)_
Common:

Backend:

Frontend:

## 5. User / UX Notes
{UX details, interactions, edge cases}

## 6. Impact & Risk
{impact scope, risk factors, ambiguous items}

## 7. Open Questions
{open items, TBD, next actions}
```

## Step 4: Dry-run 출력

변환 결과를 터미널에 전체 출력:

```
╔══════════════════════════════════════════════════════════════╗
║  DRY-RUN PREVIEW — Confluence: lysre                         ║
║  Source: docs/plan/spec-{name}.md                            ║
╚══════════════════════════════════════════════════════════════╝

{변환된 Confluence 마크다운 전체}

══════════════════════════════════════════════════════════════╗
  Target    : {parent page title} (pageId={ID})
  Page title: {final title}
══════════════════════════════════════════════════════════════╝
```

## Step 5: 사용자 확인

AskUserQuestion으로 세 가지 옵션 제시:

- **y / yes** → Step 6 게시 진행
- **n / no** → 취소 (Confluence 변경 없음, 종료)
- **edit** → "수정할 섹션과 내용을 알려주세요" 후 재변환 → dry-run 재출력 → 재확인

## Step 6: Confluence 게시

### 중복 확인

`mcp__confluence__confluence_search` 로 동일 제목 페이지 탐색:
- CQL: `title = "{페이지 제목}" AND space = "lysre"`
- 존재하면 → `confluence_update_page` (기존 page ID 사용)
- 없으면 → `confluence_create_page`

### 생성

```
mcp__confluence__confluence_create_page(
  space_key: "lysre",
  parent_id: "{Step 1에서 추출한 page ID}",
  title: "{페이지 제목}",
  content: {변환된 마크다운},
  content_format: "markdown"
)
```

### 업데이트 (기존 페이지 존재 시)

```
mcp__confluence__confluence_update_page(
  page_id: "{기존 페이지 ID}",
  title: "{페이지 제목}",
  content: {변환된 마크다운},
  content_format: "markdown",
  is_minor_edit: false,
  version_comment: "Claude publish-spec {날짜}"
)
```

## Step 7: 결과 보고

**성공:**
```
게시 완료 — {Confluence 페이지 URL}
```

**실패:**
```
게시 실패: {에러 메시지}

수동 게시 방법:
  Confluence > lysre > 새 페이지 생성 > 아래 내용 복사
  ---
  {변환된 마크다운}
```

