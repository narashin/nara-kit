# PR 본문 이미지 첨부: 숨은 ref에 커밋하고 blob 링크로 넣는다

이미지 파일 경로가 주어졌을 때만 이 파일을 따른다. 웹 편집기의 끌어다 놓기 대신, 이미지를 저장소의 숨은 ref에 커밋하고 그 커밋의 blob 링크를 본문에 넣는다.

`gh pr edit --attach`(gh 2.99.0+)는 쓰지 않는다. gh 소스가 GitHub Enterprise Server를 호스트 검사에서 막고(`attaching files is not supported on GitHub Enterprise Server`), 토큰을 바꿔도 풀리지 않는다. 이 방식은 호스트와 gh 버전에 상관없이 하나로 간다.

근거: GitHub Enterprise Server 3.19.9 저장소에서 업로드, 본문 삽입, 브라우저 표시까지 실측했다. github.com에서는 직접 실측하지 않았고, 같은 방식을 쓰는 `gh attach` 확장(enthus-appdev)이 github.com 전용으로 동작한다는 것이 근거다.

## 범위

- 지원: PNG, JPEG, GIF, WebP. `file --mime-type`이 `image/*`인 일반 파일만.
- 미지원: 동영상(mp4 등). 이 방식에서 재생기로 보이는지 확인하지 않았다. 동영상이 오면 첨부하지 않고 `skipped: 동영상 미지원`으로 receipt에 남긴다.
- 보이는 사람: 저장소를 읽을 수 있는 사람. 비공개·internal 저장소면 로그인한 브라우저에서만 보이고, 공개 저장소면 누구나 본다.

## 사전 조건

1. **호스트를 PR URL에서 도출한다.** `https://git.example.com/acme/web-ui/pull/<N>`이면 호스트 `git.example.com`, 저장소 `acme/web-ui`. URL이 없으면 `git remote get-url origin`에서 같은 방식으로. 모든 `gh` 호출에 `GH_HOST=<host>`를 붙인다. 빠뜨리면 gh 기본값인 github.com으로 가서 엉뚱한 곳에 실패한다.
2. PR이 이미 있어야 한다(번호 `<N>`). 신규 생성 흐름이면 `gh pr create` 성공 직후에 이 절차를 시작한다.
3. 쓰기 권한: `gh api repos/<owner>/<repo> -q .permissions.push`가 `true`. 아니면 업로드하지 않고 `❌ 실패:`로 멈춘다.
4. 파일명은 ASCII로. 공백·한글은 `-`로 바꿔 사본을 만든다. 링크 경로를 인코딩하는 실수를 막는다.

## 업로드 (Git Data API)

ref 이름은 `refs/uploads/issues/<N>`. 브랜치 목록에 나오지 않는다.

```bash
export GH_HOST=<host>; R=repos/<owner>/<repo>; REF=uploads/issues/<N>

# 1. ref가 이미 있는지 본다. 있으면 그 커밋 위에 쌓아야 한다
PARENT=$(gh api $R/git/ref/$REF -q .object.sha 2>/dev/null)   # 없으면 빈 값
BASE_TREE=${PARENT:+$(gh api $R/git/commits/$PARENT -q .tree.sha)}

# 2. 파일마다 blob 생성
BLOB=$(gh api -X POST $R/git/blobs -f content="$(base64 -i <file> | tr -d '\n')" -f encoding=base64 -q .sha)

# 3. tree: 기존 ref가 있으면 base_tree로 기존 파일을 유지
#    {"base_tree":"<BASE_TREE>","tree":[{"path":"<name>","mode":"100644","type":"blob","sha":"<BLOB>"}, ...]}
TREE=$(gh api -X POST $R/git/trees --input <tree.json> -q .sha)

# 4. commit: 기존 ref가 있으면 parents에 넣는다
#    {"message":"upload: PR #<N> attachments","tree":"<TREE>","parents":["<PARENT>"]}  (없으면 "parents":[])
COMMIT=$(gh api -X POST $R/git/commits --input <commit.json> -q .sha)

# 5. ref: 없으면 만들고, 있으면 fast-forward로 옮긴다 (force 금지)
gh api -X POST  $R/git/refs -f ref=refs/$REF -f sha=$COMMIT        # 처음
gh api -X PATCH $R/git/refs/$REF -f sha=$COMMIT -F force=false     # 두 번째부터
```

**두 번째 업로드는 반드시 이어 붙인다.** 부모 없는 커밋으로 ref를 강제로 옮기면 앞 커밋이 ref에서 끊기고, 이미 본문에 들어간 이미지 링크가 가비지 컬렉션 뒤에 깨진다.

링크 형식: `https://<host>/<owner>/<repo>/blob/<COMMIT>/<name>?raw=true`. 커밋 SHA로 고정하므로 이후 같은 이름 파일을 다시 올려도 기존 링크는 바뀌지 않는다.

## 본문에 넣기

다른 바이트는 전부 그대로 둔다. 본문을 다시 생성하지 않는다.

- 위치: repo 템플릿에 `스크린샷`·`Screenshots` 헤딩이 있으면 그 아래. 없으면 `## 확인 방법 (QA 가이드)` 절 바로 다음에 `## 스크린샷` 절을 새로 만든다. 이미지는 QA 표의 증거다.
- Before/After 쌍은 2열 표로. 헤더는 역할(`수정 전` / `수정 후`), 이미지 한 줄, 그 아래 각 이미지에서 무엇이 보이는지 캡션 한 줄. 파일명을 캡션으로 쓰지 않는다.

  ```markdown
  | 수정 전 | 수정 후 |
  |---|---|
  | ![before](<link>) | ![after](<link>) |
  | 반려 사유가 잘려 보임 | 반려 사유 전체가 두 줄로 보임 |
  ```

- 단독 이미지는 한 줄 설명 뒤에 `![<설명>](<link>)`.
- 반영: `gh api -X PATCH $R/pulls/<N> -F body=@<body-file>`.

## 검증

CLI로 확인할 수 있는 것만 통과로 적는다.

1. 바이트: `gh api "$R/contents/<name>?ref=refs/$REF" -H "Accept: application/vnd.github.raw"`로 받은 파일이 로컬 원본과 `cmp`로 같다.
2. 본문: 다시 읽은 본문에 각 링크가 정확히 한 번 있고, 삽입 전 본문 바이트가 그대로 남아 있다.
3. 렌더 HTML: `gh api $R/pulls/<N> -H "Accept: application/vnd.github.html+json" -q .body_html`에 링크와 같은 `<img src>`가 있다.
4. 브라우저 표시는 CLI로 확인하지 못한다. 토큰을 붙여 링크를 받으면 SSO 로그인 페이지로 넘어간다. 자동화 브라우저에 세션이 없으면 사용자에게 PR 페이지를 열어 확인해 달라고 한다.

receipt 한 줄: `첨부 <n>장: 바이트 ✓ · 본문 ✓ · 렌더 미확인(브라우저 세션 필요)`.

## 실패와 정리

- 업로드가 ref를 만든 뒤 본문 수정이 실패하면, 다시 시도하기 전에 본문을 읽어 실제 상태를 보고하고 ref가 남아 있다고 적는다.
- ref 삭제(`gh api -X DELETE $R/git/refs/$REF`)는 사용자가 요청할 때만 한다. 삭제하면 그 ref의 이미지를 쓰는 본문·댓글 링크가 전부 깨진다고 먼저 알린다.
- base64로 바꾼 임시 파일, tree/commit JSON 등 이 실행이 만든 파일만 지운다.

출처: [tiger-kit `tk-pr-media`](https://github.com/MTGVim/tiger-kit/tree/main/skills/tk-pr-media)의 검증 항목과 [`gh attach`](https://github.com/enthus-appdev/gh-attach)의 `refs/uploads/issues/<N>` 규칙을 참고했다. 코드는 가져오지 않았다.
