# nara-qa-sheet — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Build a single-file HTML checklist of the screens a human must check by hand, with checks and notes saved in the browser, for acceptance criteria that automation could not verify.

## 호출

- Claude Code: `/nara-qa-sheet`
- Codex: `$nara-qa-sheet`
- 데이터 점검만: `python3 skills/nara-qa-sheet/assets/check_sheet.py <sheet>.html`

## 언제 쓰나

- **USE FOR:** "QA 시트 만들어", "수동 점검 목록", "직접 확인할 화면 정리", "e2e 체크리스트", "qa-sheet", gap이 Needs Confirm으로, browser-verify가 Unverifiable로 남긴 AC.
- **DO NOT USE FOR:** 자동 런타임 판정 (→ nara-browser-verify), 테스트 시나리오 발굴 (→ nara-test-discover), 요구사항 대비 점수 (→ nara-gap), PR 생성 (→ nara-pr).

## 왜 있나

`nara-gap`은 증거가 없으면 `Needs Confirm`, `nara-browser-verify`는 `Unverifiable`을 낸다. 맞는 판정이지만 그 항목을 누가 언제 확인하는지는 남지 않는다. 복잡한 사전 데이터가 필요하거나 데이터를 바꾸는 조작이라 자동으로 못 밟은 화면은 결국 사람이 열어봐야 하고, 이 스킬은 그 목록을 체크할 수 있는 파일 하나로 만든다.

## 쓰는 법

1. `/nara-qa-sheet`를 부른다. 대상(`base..head`나 PR)을 안 주면 base 브랜치 대비 현재 브랜치를 잡고, 감지한 범위를 영수증에 적는다.
2. `docs/qa/YYMMDD-<slug>.html`을 브라우저로 연다. 체크와 메모는 그 브라우저에 저장된다.
3. 다 본 뒤 "결과 복사"를 눌러 PR 본문에 붙인다.

`code-only` 배지가 붙은 줄은 화면에 직접 들어가 보지 못하고 코드에서만 확인한 것이다. 버튼 이름이 실제와 다를 수 있다는 뜻이고, 지어낸 이름을 적지 않기 위한 표시다.

## 설계 메모

출발점은 MTGVim/tiger-kit의 `tk-qa-sheet`다. 자동 검증과 수동 체크를 분리하고 head가 움직이면 자동 표시를 내린다는 규칙을 가져왔고, 템플릿과 점검 스크립트는 새로 썼다. 그쪽은 시트 자체를 헤드리스로 다시 검증하고 JS 없는 정적 목록까지 재생성하는데, 여기서는 데이터 점검(`check_sheet.py`)까지만 한다.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
