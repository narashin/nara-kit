# QA 시트 데이터

템플릿의 `<script type="application/json" id="qa-data">` 블록 하나만 교체한다. 렌더러는 이 JSON을 읽어 화면을 그리고, 값은 전부 텍스트로 넣는다(HTML로 해석하지 않는다). 문자열 안의 백틱 구간만 코드 글꼴로 바뀐다.

```json
{
  "storageKey": "qa-261008-ticket-filter",
  "title": "티켓 목록 필터 수동 QA",
  "target": { "repo": "web-ui", "base": "abc1234", "head": "def5678", "env": "local" },
  "generatedAt": "2026-10-08",
  "limitations": [
    "관리자 메뉴 진입 경로 미확인. 필요한 입력: 관리자 메뉴가 보이는 스크린샷 1장"
  ],
  "areas": [
    {
      "name": "티켓",
      "screens": [
        {
          "title": "`티켓 목록`",
          "route": "/tickets",
          "link": "http://localhost:3000/tickets",
          "entry": "`티켓` > `목록`",
          "provenance": "observed",
          "checks": [
            {
              "id": "tickets-filter-status",
              "trigger": "`상태` 필터에서 `진행 중` 선택",
              "expect": "목록이 진행 중 티켓만 남고 URL에 status=in_progress가 붙는다",
              "source": "AC: 상태 필터를 고르면 목록과 URL이 함께 바뀐다",
              "state": "manual",
              "provenance": "observed"
            }
          ]
        }
      ]
    }
  ]
}
```

## slug와 storageKey

`<slug>`는 현재 브랜치명에서 타입 접두사(`feature/` `fix/` `chore/` 등)와 티켓 키(`PROJ-123-`)를 뗀 나머지다. `feature/PROJ-123-status-filter` → `status-filter`. 브랜치가 없거나 `main`이면 요구사항 문서 제목을 kebab-case로 쓴다. `storageKey`는 `qa-<slug>`로 날짜를 넣지 않는다. 날짜는 파일명에만 있다. 그래야 다음 날 같은 작업을 다시 만들어도 체크가 따라온다.

## 필드

| 필드 | 규칙 |
|---|---|
| `storageKey` | 체크·메모가 저장되는 브라우저 키. 같은 작업 재생성은 유지, 다른 작업은 새 값. |
| `target` | 시트가 묶인 정확한 대상. `head`가 바뀌면 시트를 다시 만든다. |
| `limitations` | 확인 못 한 라벨·연결은 "무엇이 빈 것 + 필요한 입력" 한 줄. 직링크를 못 넣은 것은 이유만. 없으면 빈 배열. |
| `target.env` | 환경을 모르면 키를 뺀다. 빈 문자열을 쓰지 않는다. |
| `screens[].title` | 관찰한 화면 제목은 백틱. 모르면 라우트를 그대로 쓴다. |
| `screens[].entry` | 실제로 밟은 메뉴 단계만. 모르면 필드를 뺀다. |
| `screens[].link` | 확인된 base URL + 라우트일 때만. 모르면 뺀다. |
| `checks[].id` | 시트 안에서 유일. 재생성해도 같은 체크는 같은 id (체크 상태가 따라온다). |
| `checks[].state` | `manual` \| `partial` \| `auto-verified` |
| `checks[].provenance` | `observed` \| `code-only` \| `spec-only` \| `user-provided`. `spec-only`는 기대 문구가 AC에만 있고 코드 어디에도 없을 때 |
| `checks[].source` | AC 원문, 또는 `diff:`로 시작하는 동작 설명. 파일 경로는 쓰지 않는다. AC 문구가 diff에 없으면 "diff에 없음"을 덧붙인다 |
| `checks[].evidence` | `auto-verified`·`partial`일 때 필수: 어떤 실행이 어느 head에서 무엇을 밟았는지 |
| `checks[].previousEvidence` | head 이동으로 `manual`이 된 줄에만. 옛 실행과 그 head |

## 상태와 출처는 다른 축이다

`state`는 누가 확인했는가이고 `provenance`는 라벨을 어디서 얻었는가다. `auto-verified`이면서 `code-only`인 줄은 없다(자동으로 밟았으면 관찰한 것이다). `manual`이면서 `code-only`인 줄은 흔하다: 화면에 못 들어가 봤고 사람이 확인해야 하는 줄이다.

`auto-verified` 줄은 체크된 채로 고정돼 접힌 묶음에 들어간다. 사람이 풀 수 없다. `partial`과 `manual`은 본 목록에 남는다.

## "결과 복사"

시트의 버튼이 체크 결과와 메모를 Markdown으로 클립보드에 넣는다. 대상 SHA, 체크된 줄과 안 된 줄, 메모, 한계 목록이 들어간다. PR 본문에 붙이는 용도이고, 붙이는 것은 사람이 한다.
