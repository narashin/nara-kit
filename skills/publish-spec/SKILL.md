---
name: publish-spec
description: Publish a local spec/plan markdown file to Confluence wiki. Converts to LYRIS Confluence RfC template format, previews (dry-run), confirms, then publishes. Use when user says 'publish', 'wiki에 올려', 'confluence에 게시', 'publish-spec', or at the end of workflow-doc-mode.
version: 0.2.0
---

# Publish Spec to Confluence

## Purpose

Convert a local markdown spec/plan document to the **LYRIS Confluence RfC template** and publish it. Follows a strict dry-run → confirm → publish flow.

## Trigger

- User says: "publish", "wiki에 올려", "confluence에 게시", "publish-spec"
- End of `workflow-doc-mode` when documentation artifact is complete
- User provides a spec file path explicitly

## MANDATORY: Title Format

```
LYRIS-XXX 한줄 설명
```

Examples from existing pages:
- `LYRIS-337 Additional Dashboard for Release PIC/Master`
- `LYRIS-272 [RfC] 복수의 Manager 할당 시 AND 승인 조건 추가`
- `LYRIS-323 [RfC] Add a comment to the post-approval task history of a ChangeRequest`

**Rules:**
- Jira ticket ID **필수** — 없으면 유저에게 물어볼 것
- `[RfC]` 태그는 optional (유저 지정 시에만 포함)
- 설명은 간결하게 한 줄

## MANDATORY: Body Template

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

### 섹션 매핑 가이드

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

### 변환 시 금지 사항

- spec.md 섹션 구조를 그대로 복사 금지 — 반드시 위 7개 섹션으로 재구성
- 빈 섹션 삭제 금지 — 헤딩은 유지하고 "(없음)" 또는 "-" 표기
- ASCII mockup은 code block으로 감싸서 유지
- TypeScript 타입 정의는 code block으로 유지
- **코드 레벨 참조 금지 (Confluence)**: 파일명, 타입명, 컴포넌트명, 함수명 등 코드 레벨 디테일을 Work to do에 포함하지 않음. 코드는 계속 변하므로 기획문서에 넣으면 금방 stale 됨
  - Confluence: "무엇을 해야 하는가" (what) — 시나리오 기준
  - 로컬 spec.md: "어떻게 해야 하는가" (how) — 코드 레벨 상세
- **언어 분리**: dry-run 프리뷰는 한국어 OK (유저가 검토해야 하므로). Confluence 게시 본문은 **영어** 필수. 유저가 한국어 명시 시에만 한국어

## Execution Flow

### Step 1: Collect Required Info

1. spec 파일 경로 확인 (미제공 시 최근 생성된 spec 자동 탐색)
2. Jira ticket ID 확인 (**필수** — 없으면 물어볼 것)
3. 게시 위치 확인: "어디에 게시할까?" (Confluence URL 또는 페이지 이름)
   - URL에서 space key + parent page ID 자동 파싱
   - 기본값: `confluence.local.md` 설정 참조

### Step 2: Template Conversion (Dry-Run)

1. spec.md 읽기
2. 7개 섹션 템플릿으로 재구성
3. 제목 포맷 적용: `LYRIS-XXX [RfC] 설명`
4. `confluence-draft.md`로 로컬 저장 (같은 디렉토리)
5. Dry-run 프리뷰 출력:
   - 제목
   - 게시 위치 (space > parent page)
   - 섹션 구조 (목차)
   - 총 크기
   - 주의사항 (task list 호환성 등)

### Step 3: User Confirmation

단일 질문: "게시할까?"
- "Publish" → Step 4
- "Cancel" → 중단. `confluence-draft.md`는 로컬에 남김

### Step 4: Publish

**CRITICAL: `content_format: "storage"` 사용. markdown 아님.**

Confluence는 자체 storage format (XHTML + Atlassian macro)을 사용한다. markdown으로 올리면 테이블, 코드블록 등이 깨진다. 반드시 storage format으로 변환하여 올릴 것.

**Confluence MCP 우선:**
```
mcp__confluence__confluence_create_page(
  space_key: "<space>",
  title: "LYRIS-XXX 설명",
  content: "<Confluence storage format XHTML>",
  content_format: "storage",
  parent_id: "<parent page ID>"
)
```

**MCP 미연결 시:** REST API fallback 또는 XHTML 로컬 export

### Confluence Storage Format 변환 규칙

spec.md → storage format 변환 시 반드시 아래 규칙을 따를 것.

**Headings:**
```
## 1. Background  →  <h1>1. Background</h1>
### Current Behavior  →  <h3>Current Behavior</h3>
```

**Lists (bullet):**
```html
<ul style="list-style-type: square;">
  <li>item 1</li>
  <li>item 2</li>
</ul>
```

**Lists (ordered):**
```html
<ol>
  <li>item 1</li>
  <li>item 2</li>
</ol>
```

**Tables:**
```html
<table class="wrapped">
  <colgroup><col/><col/></colgroup>
  <tbody>
    <tr><th scope="col">Header 1</th><th scope="col">Header 2</th></tr>
    <tr><td>val 1</td><td>val 2</td></tr>
  </tbody>
</table>
```

**Code blocks:**
```html
<ac:structured-macro ac:name="code" ac:schema-version="1">
  <ac:parameter ac:name="language">typescript</ac:parameter>
  <ac:plain-text-body><![CDATA[const x = 1;]]></ac:plain-text-body>
</ac:structured-macro>
```

**Bold / Inline code:**
```html
<strong>bold text</strong>
<code>inline code</code>
```

**Jira ticket link macro:**
```html
<ac:structured-macro ac:name="jira" ac:schema-version="1">
  <ac:parameter ac:name="server">Jira</ac:parameter>
  <ac:parameter ac:name="serverId">fd8fda8e-f52c-3c30-9024-3257ba6f1611</ac:parameter>
  <ac:parameter ac:name="key">LYRIS-XXX</ac:parameter>
</ac:structured-macro>
```

**Line break:** `<br/>`
**Paragraph:** `<p>text</p>`
**Empty line:** `<p><br/></p>`

**Reference (LYRIS-337 page):** 실제 팀 페이지의 storage format을 `confluence_get_page(convert_to_markdown=false)`로 조회하여 패턴을 따를 것.

### Step 5: Post-Publish

- 성공: Confluence page URL 출력
- 실패: 에러 메시지 + `confluence-draft.md` 경로 안내 (수동 업로드용)

## Configuration

`~/.claude/plugins/personal/workflow-orchestrator/confluence.local.md`:

```yaml
---
confluence_base_url: https://wiki.workers-hub.com
default_space_key: lysre
default_parent_page_id: "2735095793"
default_parent_page_name: Development
---
```

첫 실행 시 설정 없으면 유저에게 "게시 위치" 한 번만 물어보고 저장.

## Safety

- **Always dry-run first** — 프리뷰 없이 게시 금지
- **Never overwrite** existing pages without explicit confirmation
- **Title collision**: 동일 제목 페이지 존재 시 update 또는 새 생성 선택
- **[UNVERIFIED] check**: 마커 포함 시 경고
- **Template compliance**: 7개 섹션 구조 미준수 시 게시 차단

## Language

- **Dry-run 프리뷰**: 한국어 OK — 유저가 검토/이해해야 하므로
- **Confluence 게시 본문**: 영어 필수 — 팀 공유 문서이므로
- 유저가 한국어 명시 시에만 한국어로 게시

## Error Handling

- MCP 미연결 → REST API → XHTML 로컬 export
- Auth 실패 → API token 확인 안내
- Space 미존재 → 가용 space 목록 표시
- Network 에러 → `confluence-draft.md` 로컬 보관
