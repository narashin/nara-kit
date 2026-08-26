# 그림 패턴 카탈로그 — HTML / SVG

그림이 되는 개념과 그 형태를 고정해 둔 목록. 매번 재발명하지 않기 위한 것.

**매체 규칙 (2026-08-26 유저 결정) — ASCII 아트와 mermaid는 쓰지 않는다.** 노트 본문에 박스 문자(`┌─┐`)로 그림을 그리지 않는다. 그림은 아래 두 매체 중 하나다.

| 매체 | 언제 | 배치 |
| --- | --- | --- |
| **HTML 문서** | 그림이 3개 이상이거나 서로 이어지는 설명일 때 (기본값) | 노트와 **같은 폴더**에 `<노트-slug>-그림.html`. 노트에서 `[[...]]` 링크 |
| **SVG 단품** | 독립된 그림 1~2개뿐일 때 | `2_personal/Study/_assets/<노트접두>-<이름>.svg`. 노트에 `![[...]]` 인라인 임베드 |

**HTML은 임베드가 안 된다** — vault의 HTML Reader 플러그인은 뷰어라서 파일 탐색기에서 클릭해 별도 탭으로 연다(Operating Mode: Balance). 그래서:

- 노트 링크 옆에 "파일 탐색기에서 클릭해서 연다"를 한 줄 적는다.
- **HTML의 절 번호를 노트의 절 번호와 1:1로 맞춘다** — 나란히 놓고 읽는 구도가 전제라서.
- SVG는 반대로 노트 안에 바로 렌더되므로, 스크롤 중간에 그림이 나와야 하는 노트면 SVG를 고른다.

**HTML 제약** — 플러그인이 스크립트를 막고 로컬 이미지 참조(`<img src="./...">`)를 못 읽는다. 따라서 self-contained 한 파일: `<style>` 블록 + 순수 마크업만. 외부 폰트·이미지·JS 없이 그린다.

---

## HTML 스타일 베이스 (검증됨 — graphql-basics-그림.html 계열)

새 HTML을 만들 때 이 스타터에서 시작한다. 색·구성이 이미 vault의 다른 그림과 일관돼 있다.

```html
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: "Pretendard", "Apple SD Gothic Neo", -apple-system, sans-serif;
         background:#f4f5f7; color:#1f2430; padding:40px 32px 80px;
         max-width:1180px; margin:0 auto; line-height:1.6; }
  h1 { font-size:26px; margin-bottom:6px; }
  .sub { color:#6b7280; font-size:14px; margin-bottom:36px; }        /* 부제: 예시 값·기준일·출처 */
  h2 { font-size:19px; margin:52px 0 6px; display:flex; align-items:center; gap:10px; }
  h2 .no { background:#1f2430; color:#fff; border-radius:8px; width:28px; height:28px;
           display:inline-flex; align-items:center; justify-content:center; font-size:14px; flex:none; }
  .lead { color:#4b5563; font-size:14px; margin-bottom:18px; }       /* 절 요지 한 줄 */
  .panel { background:#fff; border:1px solid #e2e5ea; border-radius:14px; padding:22px; }
  .row2 { display:grid; grid-template-columns:1fr 1fr; gap:20px; align-items:start; }
  .code { font-family:ui-monospace,"SF Mono",Menlo,monospace; font-size:12px; background:#f6f8fa;
          border:1px solid #e2e5ea; border-radius:8px; padding:10px 12px; white-space:pre; overflow-x:auto; }
  .code .hl { background:#fff3bf; border-radius:3px; padding:0 2px; }  /* 노랑 = 이번에 주목할 자리 */
  .code .cm { color:#8a919e; }                                        /* 주석·부연 */
  .cap { font-size:12px; color:#6b7280; margin-top:8px; }              /* 그림 아래 "읽는 법" */
  .sdl { font-family:ui-monospace,Menlo,monospace; font-size:.86em; background:#eef2f7;
         border:1px solid #d9dfe8; border-radius:5px; padding:0 5px; color:#28456e; white-space:nowrap; }
</style>
```

색 팔레트 (의미 고정 — 바꾸지 않는다):

| 의미 | 배경 / 테두리 / 글자 |
| --- | --- |
| 좋음·해결·응답 | `#e5f3ea` / `#cfe6d8`·`#bcdcc8` / `#1b7f4d` |
| 나쁨·문제·폐기 | `#fdeaea` / `#e3a6a1` / `#b3261e` |
| 강조·특별 취급 | `#e8efff`·`#eef4ff` / `#b7ccf7`·`#cdddfa` / `#274b9b` |
| 보류·확인 중 | `#fff3d6` / `#eddcae` / `#946200` |
| 중립·비활성 | `#f0f1f4`·`#f8f9fb` / `#e2e5ea` / `#6b7280`·`#8a919e` |

구성 원칙:

- **절마다 `h2 .no` 번호 + `.lead` 요지 한 줄.** 그림 문서 혼자 읽혀도 서사가 서게.
- **개념어는 `.sdl` 칩으로 실제 식별자(필드명·파일명)와 1:1 대응** — "일대일 매칭이 안 되면 이해가 어렵다"는 피드백에서 나온 규칙.
- 그림 아래 `.cap`에 **읽는 법**을 붙인다. 그림만 두면 해석이 갈린다.
- 상태 배지·판정 표에는 위 팔레트의 의미 색만 쓴다.

---

## 패턴 8종 — 언제 무엇을 그리나

형태 판정은 매체와 무관하게 그대로다. 각 패턴의 HTML 구현 힌트를 붙인다.

### 1. before / after 대비

**언제** — 고치기 전과 후가 결론일 때. 수치를 반드시 넣는다.
**구현** — `.row2` 두 칸에 같은 구조를 나란히. 제목에 빨강/초록 배지(`화면 2개 · 클릭 2번` vs `화면 1개 · 클릭 0~1번`). 미니 UI 목업이 필요하면 표·탭·패널을 div로 흉내 낸다 — 실물 스크린샷보다 요점만 남은 목업이 낫다.

### 2. 흐름 / 파이프라인 / 생애주기

**언제** — 순서가 있고, 어느 단계가 문제/핵심인지가 요점일 때.
**구현** — 단계마다 3열 grid 행: `행동(누가·언제) | 코드·요청(무엇을) | 결과(뭐가 오나)`. 문제 지점은 `.hl` 노랑이나 빨강 칩. 가로 흐름이면 카드 사이 `→` 셀.

### 3. 층 구조 / 포함 관계

**언제** — 무엇이 무엇 안에 있는지.
**구현** — 중첩 박스: 바깥 div 테두리 안에 안쪽 div. 각 층에 monospace 라벨. (SearchInput > group > filters 중첩 그림이 이 패턴.)

### 4. 트리 / 갈라지는 판단

**언제** — 분류 체계, 조건 분기.
**구현** — 들여쓰기 + 왼쪽 보더(`border-left`)로 층을 표현하거나, 분기 카드 2~3개를 나란히 두고 조건을 위에 단다.

### 5. 크기·비율 비교

**언제** — 숫자 여러 개의 상대 크기가 결론일 때.
**구현** — div 막대: `width`를 값에 비례시키고 막대 끝에 수치+단위. 기준(1칸=얼마)을 `.cap`에 밝힌다.

### 6. 같은 것 / 다른 것 대조

**언제** — 헷갈리는 두 개념을 가를 때. 표로 충분하면 표를 쓴다.
**구현** — `.row2` 대조, 또는 판정 표(`안 깨짐`/`깨짐`을 의미 색으로). "눈에는 같은데 전송은 다름" 류는 같은 UI를 두 번 그리고 아래 코드만 다르게.

### 7. 비유 그림

**언제** — eli5에서 개념을 실물로 옮길 때. **비유는 하나만**, 끝까지 그것으로.
**구현** — 비유 쪽(주문서·창구)과 실제 쪽(쿼리·엔드포인트)을 같은 절 안에 나란히 — 비유만 그리고 실물 대응을 안 붙이면 장식이다.

### 8. 상태 전이 / 판정 지도

**언제** — 무엇이 어떤 조건에서 어떤 상태로 가는지. 부분 실패 지도, nullable 지도.
**구현** — 상태별 카드에 살아남는 것(초록 ○)과 죽는 것(빨강 ✕)을 목록으로. 조건은 카드 제목에.

---

## 쓰지 말아야 할 때

- **문장이 더 짧을 때.** "A 다음에 B"를 카드 두 개로 그리지 않는다.
- **정확한 수치 여러 개.** 그건 노트 본문의 표다. 그림은 상대 크기와 구조만.
- **코드 자체가 이미 그림일 때.** 짧은 코드 블록이 구조를 보여주면 노트에 코드 펜스로 쓴다 — 코드 펜스는 ASCII 아트가 아니다.
- **그림 1개짜리에 HTML 문서를 만들 때.** 그건 SVG 단품으로.
