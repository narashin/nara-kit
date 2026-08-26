---
name: nara-eli5-note
description: >-
  Explain something the way /eli5 would — plain words, one analogy, HTML/SVG diagrams for
  anything that can be drawn (never ASCII art, never mermaid) — and save it as a note in
  the user's Obsidian vault, matching that vault's folder and frontmatter conventions.
  USE FOR: "obsidian에 정리해", "옵시디언에 담아", "이거 노트로 남겨", "5살에게 설명하듯 정리해줘",
  "그림으로 정리해줘", "eli5로 노트 써줘", "이거 나중에 볼 수 있게 정리해".
  DO NOT USE FOR: explanation with no saving (use /eli5), session learnings into memory or
  handoff (use /nara-reflect), Confluence publishing (use /nara-publish-spec),
  architecture decisions (use /nara-adr), repo-facing docs.
---

# ELI5 노트 — 쉬운 설명을 Obsidian에 남긴다

실무에서 막힌 것을 **5살에게 가르치듯 풀고, 그릴 수 있는 건 그려서**, vault의 기존 관례에 맞춰 노트로 남긴다.

기존 `/eli5`는 설명하고 끝난다. `/nara-reflect`는 저장하지만 대상이 memory·handoff고 톤이 다르다. 이 스킬은 그 사이 — **설명의 질과 저장을 한 번에** 가져간다.

## 참조 자원

- **`references/vault-conventions.md`** — vault `narashin`의 폴더 두 계열, frontmatter 스키마, 톤, 노트 골격. 위치를 정하기 전에 읽는다.
- **`references/diagram-patterns.md`** — HTML/SVG 그림 패턴 8종, 매체 선택 규칙, HTML 스타일 베이스. 그림을 그리기 전에 읽는다.

## 절차

### 1. 톤을 먼저 고정한다

**이걸 건너뛰면 실패한다.** 같은 내용이 두 톤으로 갈리고, 잘못 고르면 노트를 다시 써야 한다.

| 톤 | 언제 | 특징 |
| --- | --- | --- |
| **eli5** | 개념 자체가 처음이거나, 남에게 설명할 일이 생길 때 | 비유 하나로 끝까지 간다. 전문 용어는 나올 때마다 즉시 풀어쓴다. 그림이 많다 |
| **실무 노트체** | 개념은 알고 이 사례의 원인·처방을 남길 때 | 용어를 그대로 쓴다. 코드·수치·검증이 중심 |

사용자 발화에 `5살`·`쉽게`·`그림으로`가 있으면 eli5다. `정리해`만 있으면 **어느 쪽인지 한 번 묻는다** — 두 톤의 결과물이 많이 다르므로 추측하지 않는다.

eli5를 골랐어도 **수치와 코드는 지운다는 뜻이 아니다.** 쉬운 말로 감싸서 같이 넣는다.

### 2. 재료를 모으고 실측과 추측을 가른다

노트에 들어갈 사실을 확정한다. 대화 중에 이미 확인한 것과 확인하지 못한 것을 명시적으로 나눈다.

- 파일·버전·수치는 **다시 확인한다.** 대화 초반의 수치가 나중에 뒤집혔을 수 있다.
- 확인 못 한 것은 노트에 `[미확인]` 또는 "확인하지 않았다"로 남긴다. 지우지 않는다 — 다음에 볼 사람에게는 그 공백이 정보다.
- 시각은 `date '+%Y-%m-%dT%H:%M'`로 얻는다. 추측하지 않는다.

### 3. 그림이 될 것을 판정하고 매체를 고른다

노트에 들어갈 개념을 훑고 **각각 "이건 그림이 되나"를 묻는다.** `references/diagram-patterns.md`의 8종 중 어디에 해당하는지 본다.

그림이 특히 잘 붙는 자리 셋.

- **before / after** — 처방의 효과가 결론일 때. 수치를 넣는다
- **왜 그렇게 되나** — 도구·시스템이 그렇게 판단한 이유. 대조 그림이 문장보다 빠르다
- **비유** — eli5 톤에서 개념을 실물로 옮길 때. 비유는 **하나만** 쓴다

**매체는 HTML 또는 SVG다. ASCII 아트와 mermaid는 쓰지 않는다** (2026-08-26 유저 결정 — 노트는 글, 그림은 렌더되는 파일).

- 그림 3개 이상·서로 이어지는 설명 → **HTML 문서 하나** (`<노트-slug>-그림.html`, 노트와 같은 폴더, `[[...]]` 링크. 절 번호를 노트와 1:1로 맞춘다)
- 독립 그림 1~2개 → **SVG 단품** (`2_personal/Study/_assets/`, `![[...]]` 인라인 임베드 — 이쪽만 노트 안에 바로 렌더된다)
- 스타일 베이스와 색 팔레트(의미 고정)는 `references/diagram-patterns.md`에 있다. 매번 새로 정하지 않는다.

**그림 없는 노트는 이 스킬의 실패다.** 정말 그릴 게 없으면 노트 안에 왜 없는지 한 줄 남긴다.

### 4. 위치를 정한다

`references/vault-conventions.md`를 읽고 판정한다. 요지는 폴더가 두 계열이라는 것 —

- **커리큘럼**(`*-core/`) — 기존 과정의 다음 차시로 들어갈 때만. 번호를 이어받고 index 목록에 한 줄 추가하며 `study_*` frontmatter를 채운다. 주제가 그 커리큘럼의 축과 다르면 넣지 않는다
- **주제 노트**(`ai-agent/`·`react/` 등) — 실무에서 겪은 것은 여기. kebab-case 파일명, frontmatter는 `created`/`updated`/`tags`

맞는 폴더가 없으면 **새로 만든다.** 노트 한 개짜리 폴더가 이 vault에서 정상이다. 억지로 인접 폴더에 밀어넣으면 폴더명과 내용이 어긋난다.

넣기 전에 **대상 폴더의 기존 노트 하나를 읽어** frontmatter 스키마를 확인한다. references는 출발점이고 정본은 vault다.

### 5. 노트를 쓴다

골격은 `references/vault-conventions.md`에 있다. 두 절은 빼지 않는다.

- **`TL;DR`** — 불릿 4~6개. 이것만 읽어도 결론이 선다
- **`내가 틀렸던 것`** — 추적 중 잘못 짚은 것, 검색어에 속은 것, 오판한 것. **기존 vault 노트에서 가장 쓸모 있는 부분이 이 절이다.** 오판이 없었으면 절을 비우지 말고 생략한다

마지막에 **`다른 데도 쓰이는 감각`** 절로 이 사례를 넘어 남는 것을 적는다. 이게 없으면 노트가 일회성 기록으로 끝난다.

### 6. 저장하고 알린다

`obsidian_create_note`로 만든다. 같은 주제 노트가 이미 있으면 새로 만들지 않고 `obsidian_read_note`로 etag를 받아 `obsidian_edit_note`로 갱신한다(그때 `updated`도 고친다).

HTML·SVG 그림 파일은 MCP가 못 쓰므로 **vault 실경로에 직접 쓴다** — vault 경로는 `~/Library/Application Support/obsidian/obsidian.json`에서 얻는다. HTML을 열 때는 파일 탐색기에서 클릭한다는 안내를 노트에 한 줄 넣는다(HTML Reader 플러그인은 뷰어라 임베드 미지원).

저장 뒤 보고에 담을 것 — 경로 · 고른 톤과 그 이유 · 새 폴더를 만들었으면 그 사실 · 그림 몇 개를 어느 매체(HTML/SVG)로 어디에 넣었는지 · 노트에 `[미확인]`으로 남긴 것.

## 규율

**톤을 안 묻고 추측하지 않는다.** 이 스킬이 생긴 계기가 그 실패다 — "obsidian에 정리해라"를 받아 기존 vault 톤(실무 노트체)에 맞췄는데, 요청자가 원한 것은 eli5와 그림이었다.

**ASCII 아트·mermaid를 그리지 않는다.** 그림은 HTML 문서 또는 SVG 파일이다 (2026-08-26 유저 결정). 코드 펜스 안의 실제 코드는 그림이 아니므로 그대로 쓴다.

**기존 노트 톤에 맞추는 것과 요청받은 톤은 다른 축이다.** 충돌하면 요청이 이긴다. vault 관례는 frontmatter·파일명·폴더에 적용하고, 문체는 요청을 따른다.

**용어를 몰래 쓰지 않는다.** eli5 톤에서 `side effect`·`barrel`·`peer dependency` 같은 말을 처음 쓸 때는 그 자리에서 한 줄로 풀어쓴다. 각주로 미루지 않는다.

**비유를 두 개 섞지 않는다.** 레고로 시작했으면 끝까지 레고다. 중간에 도서관·나무로 갈아타면 읽는 사람이 매핑을 두 번 한다.

**수치는 단위와 기준을 붙인다.** `958 → 192`가 아니라 `gzip 958kB → 192kB`. 막대그림을 쓰면 한 칸이 얼마인지 밝힌다.

**"틀렸다"를 부드럽게 쓰지 않는다.** 오판은 오판으로 적는다. 그게 다음에 같은 함정을 피하게 한다.
