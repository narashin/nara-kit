# Publish Spec Execution Procedure

## Step 1: Collect Required Info

1. spec 파일 경로 확인 (미제공 시 최근 생성된 spec 자동 탐색)
2. Jira ticket ID 확인 (**필수** — 없으면 물어볼 것)
3. 게시 위치 확인: "어디에 게시할까?" (Confluence URL 또는 페이지 이름)
   - URL에서 space key + parent page ID 자동 파싱
   - 기본값: `confluence.local.md` 설정 참조

## Step 2: Template Conversion (Dry-Run)

1. spec.md 읽기
2. 7개 섹션 템플릿으로 재구성 (see references/template.md)
3. 제목 포맷 적용: `LYRIS-XXX [RfC] 설명`
4. `confluence-draft.md`로 로컬 저장 (같은 디렉토리)
5. Dry-run 프리뷰 출력:
   - 제목
   - 게시 위치 (space > parent page)
   - 섹션 구조 (목차)
   - 총 크기
   - 주의사항 (task list 호환성 등)

## Step 3: User Confirmation

단일 질문: "게시할까?"
- "Publish" → Step 4
- "Cancel" → 중단. `confluence-draft.md`는 로컬에 남김

## Step 4: Publish

Use Confluence storage format (see references/storage-format.md).

## Step 5: Post-Publish

- 성공: Confluence page URL 출력
- 실패: 에러 메시지 + `confluence-draft.md` 경로 안내 (수동 업로드용)

## Configuration

`~/.claude/confluence.local.md`:

```yaml
---
confluence_base_url: https://wiki.example.com
default_space_key: SPACE
default_parent_page_id: "PARENT_PAGE_ID"
default_parent_page_name: Parent Page
---
```

첫 실행 시 설정 없으면 유저에게 "게시 위치" 한 번만 물어보고 저장.

## Error Handling

- MCP 미연결 → REST API → XHTML 로컬 export
- Auth 실패 → API token 확인 안내
- Space 미존재 → 가용 space 목록 표시
- Network 에러 → `confluence-draft.md` 로컬 보관
