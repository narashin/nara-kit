# Existing-PR Mode — 기존 PR 본문 재생성

인자가 **이미 열린 PR**을 가리키면(신규 브랜치가 아니라) 생성이 아니라 **본문 재생성 + `gh pr edit`** 이다. 대상 repo가 cwd에 체크아웃 안 돼 있어도 된다.

## 감지

- 인자가 PR URL(`.../pull/<N>`) 또는 "기존 PR / 본문 갱신" 의도 → **existing-PR 모드** (이 파일).
- 그 외(로컬 브랜치에서 새 PR) → SKILL.md Steps 1~6 (신규 생성).

## 절차

1. **Fetch** (로컬 `git log`·base-branch 스크립트 대신):
   ```
   gh pr view <N> --repo <host/owner/repo> \
     --json number,title,state,baseRefName,headRefName,body,commits,url
   ```
   - base branch = 응답의 `baseRefName` (감지 스크립트 안 씀).
   - 사실 SoT = author가 쓴 기존 `body` + `commits` 헤드라인. 코드 미체크아웃이면 재검증 불가 → **원문 사실만 재구조화**, 지어내지 않는다.
2. **본문 재생성** — body-guide.md의 5섹션 QA-first 포맷으로. naranizer post-pass 신규와 동일 적용.
3. **제목**:
   - 요청이 "본문 갱신"이면 title 유지.
   - 제목이 신 포맷(`<TICKET> <type>: ...`) 아니면 type 접두 추가를 **제안**(강제 X).
   - Ticket ID는 기존 PR 것 유지 (커밋에서 재도출 X).
4. **반영** (신규와 동일 confirm 게이트 먼저 — 원격 PR 업데이트 = outward-facing):
   ```
   gh pr edit <N> --repo <host/owner/repo> --body-file <tmp>
   # 제목도 바꾸면 --title "<...>" 추가
   ```

## 주의

- 본문은 전체 덮어쓰기. 기존 본문의 손으로 쓴 메타(브랜치 rename 노트, 대체 PR 참조 등)는 재구조화 후 Linked Issues 아래 blockquote로 보존.
- 커밋이 원문 서술과 어긋나면(예: 원문 "권한 정책 그대로"인데 커밋에 access-control 추가) QA 표에 surface.
- 설치본·command stub이 stale일 수 있음 → repo의 최신 SKILL/body-guide 기준으로 작업.
