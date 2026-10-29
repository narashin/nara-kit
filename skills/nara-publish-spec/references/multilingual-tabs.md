# Multilingual Tabs (한국어 / English / 日本語)

한 페이지 안에 `한국어`, `English`, `日本語` 탭 세 개를 두고 같은 내용을 세 언어로 싣는 게시 방식이다.

## 언제 쓰나

- 원본이 `nara-rfc`가 만든 RFC(`docs/rfc/*-rfc.md`)일 때
- 유저가 세 언어 탭 게시를 요청했을 때

이 경우 SKILL.md의 "본문은 영어" 기본값 대신 이 문서를 따른다. 그 밖의 규칙(dry-run, 7개 섹션, 코드 레벨 참조 금지, 덮어쓰기 확인)은 그대로 적용된다.

## 원문과 번역

1. 로컬 원문은 한국어 Markdown 하나다. 번역본을 로컬 파일로 따로 만들지 않는다.
2. 한국어 탭 본문에 `nara-ko-prose` post-pass를 먼저 돌린다(규칙 원문이 없으면 건너뛴다). 영어·일본어는 이 수리를 마친 한국어본을 번역한다.
3. 세 언어에서 요구사항, 결정, 미결 질문, 불확실성 표시(`[UNVERIFIED]` 등), 링크가 일치해야 한다. 번역하면서 새 내용을 보태지 않는다.
4. 첨부된 목업 이미지는 세 탭 모두에서 참조한다. 이미지 속 UI 문구가 탭 언어와 다르면 이미지 옆에 그 사실을 한 줄로 설명한다.
5. dry-run 프리뷰에는 탭별 섹션 목차를 나란히 보여 주고, 세 탭의 미결 질문 수와 링크 수가 같은지 함께 적는다.

## Storage 형식

본문은 `ui-tabs` 매크로 하나 안에 `ui-tab` 매크로 세 개를 둔다. 각 탭 안은 [storage-format.md](storage-format.md)의 변환 규칙을 그대로 쓴다.

```html
<ac:structured-macro ac:name="ui-tabs">
  <ac:rich-text-body>
    <ac:structured-macro ac:name="ui-tab">
      <ac:parameter ac:name="title">한국어</ac:parameter>
      <ac:rich-text-body>
        <!-- 7 sections, Korean -->
        <ac:image><ri:attachment ri:filename="mockup.png"/></ac:image>
      </ac:rich-text-body>
    </ac:structured-macro>
    <!-- English, 日本語 tabs: same structure -->
  </ac:rich-text-body>
</ac:structured-macro>
```

[UNVERIFIED: 탭 제목 파라미터 이름(`title`)은 사이트에 설치된 탭 매크로 앱에 따라 다를 수 있다.] 처음 게시하는 사이트라면 탭이 이미 들어간 기존 페이지를 `convert_to_markdown=false`로 읽어 파라미터 이름을 맞춘다. 아래 게시 후 확인이 이 차이를 잡는 마지막 장치다.

## 게시 후 확인

게시(또는 갱신) 직후 페이지를 storage 형식으로 다시 읽고 다음을 확인한다.

- `ui-tab` 세 개가 있고 제목이 `한국어`, `English`, `日本語`다
- 각 탭에 7개 섹션 헤딩이 모두 있다
- 첨부 참조(`ri:attachment`)가 세 탭에 같은 파일명으로 들어 있고, 그 파일이 페이지 첨부 목록에 있다

하나라도 어긋나면 성공으로 보고하지 않고 어긋난 항목을 적는다.

## 중단 조건

탭 매크로를 쓸 수 없거나(매크로 미설치, MCP가 storage 갱신을 받지 않음) 위 확인이 실패하면 세 언어를 일반 본문으로 이어 붙여 올리지 않는다. 게시를 멈추고 중단 사유와 `confluence-draft.md` 경로를 보고한다.
