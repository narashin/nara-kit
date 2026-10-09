---
name: nara-qa-sheet
description: >-
  Build a single-file HTML checklist of the screens a human must check by hand, with checks and notes saved in the browser, for acceptance criteria that automation could not verify.
  USE FOR: "QA 시트 만들어", "수동 점검 목록", "직접 확인할 화면 정리", "e2e 체크리스트", "qa-sheet", gap이 Needs Confirm으로, browser-verify가 Unverifiable로 남긴 AC.
  DO NOT USE FOR: 자동 런타임 판정 (→ nara-browser-verify), 테스트 시나리오 발굴 (→ nara-test-discover), 요구사항 대비 점수 (→ nara-gap), PR 생성 (→ nara-pr).
---

# qa-sheet: 사람이 직접 볼 화면의 체크리스트

자동 검증이 닿지 않은 항목을 화면 단위 체크리스트로 만든다. 복잡한 사전 데이터가 필요하거나, 데이터를 바꾸는 조작이거나, 헤드리스로 인증을 못 세운 경우가 여기로 온다. 산출물은 HTML 파일 하나이고, 체크와 메모는 그 브라우저에 저장된다. `nara-browser-verify` 실행 결과가 없어도 만든다. 그때는 전부 `manual`이고 라벨은 전부 `code-only`다.

이 스킬은 목록을 만들 뿐이다. 제품 승인, 구현, PR 게시는 하지 않는다. **시트가 다 체크돼도 그것은 사람이 확인했다는 기록이지 이 스킬이 검증했다는 증거가 아니다.**

## Core Rules

1. **대상을 고정한다**: repo + `base..head` SHA(또는 PR head). 전달 직전에 다시 읽고, head가 움직였으면 영향받은 줄을 다시 판정한다.
2. **본 것만 쓴다**: 기존 화면의 라벨은 언어·대소문자·문장부호·띄어쓰기까지 그대로 인용한다. 진입 경로는 메뉴 단계마다 실제로 확인한 것만 안내문으로 쓴다. 라우트·컴포넌트명·식별자·i18n 키·티켓 문구는 라벨의 증거가 아니다. 수집 방법은 [ui-evidence](../nara-browser-verify/references/ui-evidence.md) (같이 설치된 스킬 파일. 없으면 이 문단만으로 진행).
3. **모르면 `code-only`**: 관찰한 라벨만 백틱으로 감싼다. 코드에서만 읽은 라벨은 큰따옴표("진행 중")로 쓰고 provenance를 `code-only`로 둔다. AC에만 있고 코드에 없는 라벨은 `spec-only`다. 코드에서만 확인한 화면은 라우트를 제목으로 쓴다. 라벨 없는 트리거는 `(아이콘)`, `(행 클릭)`처럼 적는다. 화면에 못 들어가도 목록은 만든다.
4. **자동과 수동을 섞지 않는다**: 줄의 상태는 [sheet-data](references/sheet-data.md)의 `auto-verified | partial | manual` 중 하나. 단위 테스트만으로는 `auto-verified`가 아니다. 데이터를 바꾸는 줄은 항상 `manual`.
5. **기대 결과는 근거가 있는 것만**: 줄마다 `source`가 AC 원문이거나 diff가 보여주는 동작이어야 한다. AC에 없고 diff에만 있는 동작(딥링크 진입 등)은 줄을 만들되 `source`를 `diff:`로 시작한다. AC에도 diff에도 없는 기대 결과는 쓰지 않는다. 같은 패턴의 변형(다른 옵션 선택 등)은 AC 줄에 섞지 않고 `diff:` 줄 하나로 묶는다.
6. **trigger도 지어내지 않는다**: AC에 When이 없으면 `trigger`는 `(Given 상태를 만든 뒤 화면 진입)`으로 쓰고, 그 상태를 만드는 방법은 `source`의 Given 원문에 맡긴다. 사용자 동작을 추측해 쓰지 않는다.
7. **AC와 diff가 어긋나면 줄은 남기고 판정은 안 한다**: AC가 요구하는 문구나 동작이 diff에 없으면 그 줄을 `manual`로 두고 `source`에 "diff에 없음"을 덧붙인다. 영수증에 한 줄로 알리고, 점수나 Missing 판정은 `nara-gap`에 맡긴다.
8. **비밀값 금지**: 자격 증명, 토큰, 서명된 URL, 개인정보, 소스 파일 경로(`src/...` 포함)를 시트에 넣지 않는다. `source`는 diff를 말로 설명한다.

## 인자 ($ARGUMENTS)

`nara-qa-sheet [<base>..<head> | <PR URL/번호>] [--env <local|dev|qa>] [--markdown]`

인자가 없으면 현재 브랜치에서 감지한다: 저장소 기본 브랜치(`origin/HEAD`, 없으면 로컬 `main`·`master`·`develop` 중 처음 있는 것)와의 merge-base부터 `HEAD`까지를 대상으로 잡고, 영수증의 대상 줄에 감지한 base와 범위를 적는다. 작업 트리에 미커밋 변경이 있으면 그것도 범위에 넣고 그 사실을 적는다. `--env`가 없으면 `.claude/ui-diff/env.md`나 plan의 값을 쓰고, 그것도 없으면 `target.env`를 빼고 영수증에 `환경: 미지정`으로 적고 직링크를 넣지 않는다. `--markdown`은 HTML 대신 Markdown 목록을 낸다.

## Procedure

1. **Scope**: 대상 고정. `docs/requirements.md`, `docs/plan.md`, `docs/gap.md`, 같은 head의 `nara-browser-verify` 결과가 있으면 읽는다. diff도 대상도 못 정하면 `Blocked`.
2. **화면 추적**: 바뀐 컴포넌트를 호출자를 따라 라우트와 진입 화면까지 올린다. 못 올린 것은 범위 공백으로 남긴다.
3. **줄 만들기**: 영역 → 화면 → 체크. 체크마다 화면/라우트, 트리거, 기대 결과, 근거(AC 원문 또는 diff 요약). 같은 패턴은 한 번 설명하고 화면별 줄은 따로 둔다.
4. **상태 판정**: 증거의 head는 `nara-browser-verify` 영수증의 `head:` 또는 run 디렉터리(`.claude/browser-verify/runs/<ts>/`)의 `head` 파일에서 읽는다. 둘 다 없는 run은 증거로 쓰지 않는다. 같은 head에서 같은 화면·진입 경로·트리거·기대 결과를 자동 런타임이 실제로 밟았으면 `auto-verified`. 다른 화면이나 다른 경로의 증거면 `partial`로 두고 안 밟은 부분만 남긴다. 나머지는 `manual`.
5. **head가 움직였을 때**: 증거의 head에서 현재 head까지의 diff가 그 화면의 렌더 경로나 요청 경로를 건드렸으면 `manual`로 내리고 옛 증거를 `previousEvidence`로 남긴다. 안 건드렸으면 `auto-verified`를 유지하고 그 이유를 적는다.
6. **링크**: 환경의 base URL과 라우트가 확인됐을 때만 화면 직링크를 넣는다. ID, fragment, 환경을 지어내지 않는다. 못 넣으면 이유를 적는다.
7. **렌더**: [템플릿](assets/qa-sheet-template.html)을 `docs/qa/YYMMDD-<slug>.html`로 복사하고 `qa-data` JSON 블록만 교체한다. 렌더러 코드는 건드리지 않는다. `<slug>`와 `storageKey`는 [sheet-data](references/sheet-data.md)의 규칙으로 만든다. 같은 작업을 다시 만들면 같은 `storageKey`가 나와 체크가 보존된다. 기존 파일이 다른 작업의 것이면 덮어쓰지 않는다.
8. **자체 점검**: `python3 <skill>/assets/check_sheet.py <파일>`. JSON 파싱, id 중복, 상태값, 예시 문구 잔존을 본다. 이 점검은 데이터가 맞는지만 본다. 브라우저에서 체크가 저장되는지는 열어보지 않았으면 주장하지 않는다.

Markdown이나 파일 없는 목록은 `--markdown`이나 명시적 요청이 있을 때만 낸다.

## Output (receipt)

```
수동 QA 시트 생성 (recorded only).
- 대상: `web-ui` `abc1234..def5678` · 환경: local
- 체크 14개: 수동 9 / 부분 2 / 자동 검증 3 · code-only 4
- 확인 못 한 진입 경로 2건: 필요한 입력 = 관리자 메뉴가 보이는 스크린샷 1장
- artifact: `docs/qa/261008-ticket-filter.html`
- Next: 시트를 열어 체크한 뒤 "결과 복사"를 PR 본문에 붙인다
```

## Trailing status (필수)

```
sheet: <path> | none (<사유>)
target: <base>..<head>
checks: N (manual a / partial b / auto-verified c; code-only d / spec-only f; demoted e)
unverified-paths: N (<채우는 데 필요한 가장 작은 입력>) | 0    # 진입 경로만 센다. 라벨 공백은 limitations에만
self-check: pass (check_sheet.py → exit 0) | fail (<출력>) | not-run (<사유>)
```

`demoted`는 head가 움직여 `auto-verified`에서 `manual`로 내려간 줄 수다. 0이어도 적는다. `code-only`와 `spec-only`는 체크 줄 수다. 0이어도 적는다.
