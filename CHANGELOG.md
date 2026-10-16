# Changelog

nara-kit의 모든 주요 변경을 기록한다. 형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/),
버전은 [Semantic Versioning](https://semver.org/lang/ko/)을 따른다.

nara-kit은 매니페스트 없는 Agent Skills repo — `main` 브랜치가 곧 릴리즈이고 git tag가 immutable snapshot이다.
각 tag = 여기의 한 버전 섹션. tag가 없는 진행 중 변경은 `[Unreleased]`에 쌓인다.

호환성 규칙(major 판정): 스킬 이름 삭제·rename, invocation 방식 변경, 산출물 경로 변경은 consumer에게 breaking.
단 `0.x` 구간에서는 semver 관례대로 breaking을 minor로 올린다 — `1.0.0`은 API 안정 선언으로 읽히므로 표면이 굳은 뒤에 붙인다.

## [Unreleased]

## [0.26.1] - 2026-10-16

### Changed
- **`nara-planning`의 USE FOR에 "기획서 써줘", "요구사항 정의서", "스토리보드"를 더했다.** 기획서를 쓰자는 요청이 planning으로 가도록 트리거만 넓혔고 본문 동작은 그대로다

### Fixed
- **`nara-ac-draft`의 다음 단계 안내가 파일마다 다르던 문제.** `SKILL.md`는 `nara-plan`, references는 `nara-gap`·`nara-grill`이었다. gap은 구현 뒤 verify에서 부르므로(ADR-0001) 모두 `nara-plan`(설계가 흔들리면 `nara-grill` 먼저)으로 맞췄다
- **`nara-ac-draft` 평가 세트의 채점 조건이 이제 맞는 답과 틀린 답을 가른다(6/6).** `validation.yaml`을 처음 만들었다. 맞는 답은 현재 스킬을, 틀린 답은 실제로 나온 동작(옛 ac-draft, 옛 prep, 스킬 없는 응답, 비발동 요청에 스킬을 억지로 적용한 결과)을 서브에이전트로 돌려 얻었다
  - waza의 task 수준 `output_contains`·`output_not_contains`는 정규식이 아니라 글자 그대로 찾는다. `(?i)(...)` 패턴은 어떤 출력에도 맞지 않아, "Why 없음" task는 만들어진 뒤로 늘 실패하는 조건이었다. 넷을 반드시 들어가는 문자열로 바꿨다
  - 원문 AC task가 금지하던 `[draft]`는 올바른 영수증의 "[draft] 0개"에도 걸렸다. 옛 버전이 지어 붙이던 `AC-4`를 금지하는 조건으로 바꿨다
  - `executor`를 `copilot-sdk`에서 `mock`으로 바꿨다. copilot은 좌석이 없어 probe가 오류로 끝나고 채점기에 빈 출력이 갔다
  - 다른 평가 세트의 task 조건에도 정규식처럼 보이는 문자열이 29개 있다(design-studio 22, design-pack-builder 4, rewrite 2, retro 1). 하나씩 확인하지 않았다

## [0.26.0] - 2026-10-16

> **업그레이드 시 수동 조치 필요.** `nara-prep`이 없어졌다. `rm -rf ~/.agents/skills/nara-prep ~/.claude/skills/nara-prep` 후(`~/.claude/skills/`의 항목은 `~/.agents/skills/`를 가리키는 심링크라 링크만 지우면 사본이 남는다) 전역 `add` 명령을 다시 실행한다(`npx skills update`는 전역 설치를 갱신하지 않는다). `/nara-prep`을 부르는 Multica autopilot 지침이나 개인 규칙 파일은 `/nara-ac-draft`로 바꿔야 한다. 스킬 파일만 바꿔서는 이미 등록된 autopilot 사본이 바뀌지 않는다.

### Changed (breaking: skill removal)
- **`nara-prep`을 `nara-ac-draft`에 합쳤다.** 이제 `docs/requirements.md`를 쓰는 입구는 ac-draft 하나다. 티켓 ID나 URL, 붙여 넣은 본문을 받으면 원문을 가져와 AC를 그대로 옮기고, 한 줄 의도를 받으면 지금처럼 US와 Gherkin AC를 만든다. 원본에 AC가 없을 때만 초안을 쓰고 `[draft]`를 붙여 원문 AC와 구분한다. 예전에는 prep이 AC 없음으로 막히면 ac-draft로 넘어가야 했다
  - 60일 세션 기록(Claude Code + Codex 499개)에서 prep 호출은 0건이었다. 이름이 걸린 2개 세션은 nara-kit을 고치던 세션이라 본문 언급이었다. Multica jira-drain 안의 호출은 이 집계에 안 잡힌다
  - 가져온 규칙은 둘이다: 원문 AC를 고치거나 보강하지 않기, 원문에 없는 FR·구체값을 만들지 않기(`[UNVERIFIED]`). 버린 것: `docs/sources/<id>.raw.md` 사본과 해시, 3일 재실행 판정, Readiness 4기준 점수, `[PREP]` 꼬리 줄
  - `requirements.md`의 형식과 `sources[].fetched_at`은 그대로라 plan·gap·test-discover·browser-verify는 바뀌지 않는다. `nara-now`의 7일 경과 판정도 그대로이고, 추천 명령만 `/nara-ac-draft <원본>`으로 바뀌었다. `sources: [internal-draft]`는 경과 판정에서 뺀다
  - ac-draft 평가 세트: 초안 전용이던 eval 수준 grader 둘(US·Gherkin 절, `[UNVERIFIED]` 표지)을 초안 task로 내렸다. 외부 원본 task가 그 조건을 만족할 이유가 없어서다. prep의 task 셋(Jira 로컬화, 붙여 넣은 본문, gap 요청 비발동)을 옮기고, 원본에 AC가 없을 때 `[draft]`를 다는지 보는 task를 더했다. gap 평가의 redirect 문자열도 `ac-draft`로 바꿨고 판별 검사는 8/8 그대로다

### Added
- **`nara-planning`: 기능 하나의 기획 묶음(`docs/product/<slug>/`)을 소유하고 흐름까지 이끄는 스킬.** PRD, 근거 원장, 결정 로그, 해당할 때만 정책·흐름·IA, 요청 시 화면 설계서·운영 개발 요청서를 쓴다. PRD 머리의 커버리지 표가 다음 할 일을 고르고, 남의 몫(결정 질문, 인수 기준, 수치 대조)은 동의를 받아 같은 세션에서 `nara-grill`·`nara-ac-draft`·`nara-claim-audit`를 실행한다. 별도 워크플로 스킬이 아니라 산출물을 소유한 스킬이 흐름을 이끄는 형태다
  - 지어내지 않기: 근거 없는 수치·정책·일정은 본문에 쓰지 않고 미결로 둔다. 사용자가 채우라고 하면 `[가정]` 라벨, 측정해야 아는 기준선은 가정으로도 채우지 않는다
  - 문서끼리 대조: PRD·정책·흐름·IA·인수 기준·코드에서 같은 사실이 다르게 적혔는지 맞춰 보고, 어긋나면 어느 쪽도 고르지 않고 결정으로 올린다
  - 번호 참조(`E-3`, `P-1`, `PROJ-123 참고`) 대신 뜻을 쓰고 추적 키는 HTML 주석으로 숨긴다. 인터뷰 원문과 개인정보는 저장소 밖에 둔다. 응답은 존댓말과 결론·먼저 정할 것·이번에 한 일·진행 상황 형식
  - 상태값(`drafting | handed-off | measuring | closed`)은 이 스킬만 바꾸고, 개발 중인 기능의 인수 기준만 `docs/requirements.md`에 두며 나머지는 묶음 안으로 옮긴다(복사 아님)
  - 측정: skill-creator 반복 5회, 시나리오 5개(새 기능 시작, 인터뷰 정리, 숫자를 채워 달라는 압박, 화면 설계서, 운영 개발 요청서)를 스킬 사용·미사용으로 1회씩 돌렸다. 마지막 회차 통과율 100% 대 77%, 시간은 약 2.4배, 토큰은 약 42% 더 든다. 각 1회 실행이라 경향이고 증명이 아니다
  - 출처: phuryn/pm-skills `01f0c62`(MIT)에서 인터뷰 원칙, 가정 분류, KPI 정의표, 6요소 가치 제안, 핵심·조건부 문서 구조 등을 규칙만 골라 다시 썼다

### Changed
- **`nara-grill`에 제품 기획용 압박 축 reference(`references/product-probes.md`)를 더했다.** 대상이 기획 묶음이나 PRD이면 사용자와 근거, 범위, 정책과 권한, 상태와 예외, 데이터, 운영, 측정, 가정 붕괴, 문서 사이 일치 축에서 위험한 결정만 묻는다. 체크리스트로 쓰지 않고, 빠짐없음은 `nara-planning`의 커버리지 표가 맡는다. grill이 문서를 쓰지 않는 계약은 그대로다
- **`nara-ac-draft`가 기획 묶음을 입력으로 읽는다.** 목표·범위·결정·정책·흐름을 근거로 쓰고, 묶음에 확정된 값은 `[UNVERIFIED]` 대신 그 결정·규칙 이름을 단다. 미결이나 가정 값은 확정으로 옮기지 않고, 묶음끼리 다른 사실은 blocking Open Question으로 올린다. frontmatter에 `product:` 경로를 남긴다
- **`nara-now`가 기획 묶음의 `status:`를 읽어 추천한다.** 현재 브랜치의 묶음이 `drafting`이면 `/nara-planning <slug>`를 먼저 추천한다. 폴더 존재나 수정 시각으로 추측하지 않으므로, 기획이 끝난 묶음(`handed-off`, `closed`) 때문에 기획으로 되돌아가지 않는다. `measuring` 묶음은 부차 언급 한 줄로만 알린다


## [0.25.0] - 2026-10-16

> **업그레이드 시 수동 조치 필요.** `nara-reflect`, `nara-meta-feedback`, `nara-memory-audit`가 없어졌다. `npx skills update`는 지워진 스킬을 지우지 않으므로 설치본에 옛 사본이 남는다. `rm -rf ~/.claude/skills/nara-reflect ~/.claude/skills/nara-meta-feedback ~/.claude/skills/nara-memory-audit` (Codex는 `~/.codex/skills/` 같은 이름) 후 update. 옛 이름을 부르는 Multica autopilot이나 개인 규칙 파일도 새 이름으로 바꿔야 한다.

### Changed (breaking: skill split, rename, removal)
- **`nara-reflect`를 `nara-handoff`와 `nara-retro`로 나눴다.** reflect는 "어디서 멈췄나"와 "무엇을 배웠나"를 한 스킬에서 했다. 60일 세션 기록에서 reflect는 7회, meta-feedback과 memory-audit은 0회 불렸다(이름으로 찾은 값, 표기 변형은 못 셌을 수 있다)
  - `nara-handoff`: `docs/handoff.md` 9절 스키마, 이전 handoff와의 carry-forward merge, 비면 삭제. 다음 세션 `nara-now`가 이 파일을 먼저 읽는 연결은 그대로다. 배운 것은 쓰지 않고 `/nara-retro`를 권한다
  - `nara-retro`: reflect의 학습 라우팅(auto-memory 직접 write + dual-store, 나머지 suggest-only)에 tiger-kit `tk-retro`(`5e633e3`)의 규율을 더했다. 학습마다 관찰, 영향, 원인 확신도, 최소 예방, 소유 층, 판정 검사를 적고, 기계로 잡을 수 있는 실수는 규칙보다 테스트·린트·스크립트를 먼저 제안하고, 규칙이 이미 있었는데 어겼으면 규칙을 더 쓰지 않고 이유를 찾고, `no change`를 정상 결론으로 둔다
  - 측정: 스킬 개수 갱신을 세 번 놓친 세션(규칙은 이미 있음) + 처음 들은 placeholder 규범으로 옛 reflect와 새 retro를 2회씩 돌렸다. 둘 다 기계 검사 추천과 placeholder의 CLAUDE.md 라우팅은 4회 모두 맞췄다. 옛 reflect 한 번은 이미 있는 규칙을 다시 적는 feedback 메모리("커밋 전에 직접 grep으로 대조")를 만들었고, 새 retro는 2회 모두 그 후보를 메모리로 보내지 않았다. 새 retro는 2회 모두 소유자를 hook 대신 `tools/` 스크립트로 잡고 판정 검사(지금 상태에서 실패, 고친 뒤 Pass)를 적었다. 갈린 곳도 있다. 새 retro 한 번은 placeholder 규범의 이유("공개 repo")를 규칙 문장과 별도로 메모리에도 남겼고 다른 한 번은 남기지 않았다. 두 곳에 남기는 예외 조건이 판단에 맡겨져 있다는 뜻이다. 모두 2회 관찰이라 경향이고 증명이 아니다
- **`nara-meta-feedback`을 `nara-retro`의 skill-incident 모드로 합쳤다.** redaction 규약, pre-flight 스캔, `cannot_generalize_safely` 중단, 4절 출력 템플릿은 그대로다. tk-retro의 실패 평면(선택·로딩·지시 해석·계획·실행·형식·평가·호스트 호환·로컬 override·효율)과 사건·대조군 재현을 더했다. 로컬 denylist는 `.claude/overrides/retro.md`, 없으면 예전 `meta-feedback.md`를 읽는다
- **`nara-memory-audit`을 `nara-grooming`으로 바꾸고 범위를 넓혔다.** 메모리 2단 감사(`scripts/audit.sh`, 회귀 42건 통과)는 그대로이고, tiger-kit `tk-grooming`(`5e633e3`)에서 규칙(CLAUDE.md·AGENTS.md·rules)과 스킬의 중복·충돌·stale override 감사를 가져왔다. 사용자가 동작을 바로잡았을 때 그 동작을 요구한 낡은 지침을 증거 사슬로 찾는다. 수정은 위치 등급(저장소 밖 / 추적 안 됨 / 추적됨)별로 하나씩 승인받고, git 밖 파일은 영속 백업 뒤에만 고친다. 설치본은 소스에서 고친다
- tk-compound(완료 PR 묶음 진단)는 새 스킬로 만들지 않았다. 리뷰 지적을 확정·기각·미해결로 가르고 독립 사건 수로 세는 규칙만 retro에 넣었다

### Added
- **`nara-ask-repo`**: 저장소 질문 하나에 읽기 전용으로, 주장마다 `path:line`을 붙여 답한다. tiger-kit `tk-ask-repo`(`5e633e3`)에서 검색 출발점 고정, 선언은 모양만 증명, 못 찾음과 없음의 구분(`없음 | 아직 반영 안 됨 | 자리만 있음 | 실제 사용 중`), 영향 범위 셋 분류, 소비자 쪽부터 보는 책임 판정, 답 먼저 쓰는 형식을 가져왔다. 다른 로컬 checkout과 원격 GitHub 저장소를 커밋 SHA로 고정해 읽는 부분은 새로 붙였다(URL 호스트로 `gh api --hostname`, 넓으면 scratch에 partial clone, 받은 코드는 실행 안 함). 원본은 명시 호출 전용이지만 읽기만 해서 자연어 호출을 열었다
  - 측정: 동적 조회(`exporters[\`export${format}\`]`)로만 불리는 함수를 "지워도 돼?"로 물었다. 스킬 없이도 2회 모두 "쓰이고 있다"고 맞혔다. 차이는 근거였다. 스킬 없이는 `path:line`이 0/2, 스킬로는 2/2. 존재 라벨을 그대로 쓴 것은 1/2이라, 라벨을 답 첫 문단에 그대로 쓰라고 본문을 고쳤다(재측정 안 함)

### Fixed
- `nara-explain` 검사기가 인라인 요소(`<em>`·`<code>`·`<a>`) 뒤에서 줄이 바뀌고 다음 줄이 `pie`·`flowchart` 같은 도표 키워드로 시작하는 산문을 mermaid로 잘못 실패시키던 것(0.24.0 Known issue). 텍스트를 블록 요소 단위로 이어 붙여 블록의 첫 줄만 도표 선언으로 본다. 회귀 테스트 세 건은 수정 전 검사기에서 실패하고 수정 후 통과한다

## [0.24.0] - 2026-10-16

> **업그레이드 시 확인.** 원격에 쓰는 여섯 스킬은 이제 `/nara-<name>`으로만 불린다. `nara-explain` 변경 설명 산출물이 `docs/explain/<target>.html`로 옮겨졌다. 신규 스킬 셋은 `npx skills update`로 들어온다.

### Known issue
- `nara-explain` 검사기가 인라인 요소(`<em>` 등) 뒤에서 줄이 바뀌고 다음 줄이 `pie`·`flowchart` 같은 도표 키워드로 시작하는 산문을 mermaid로 잘못 실패시킨다. 해당 줄을 이어 쓰면 피할 수 있다

### Changed (breaking: artifact)
- **`nara-explain`의 변경 설명(PR·커밋·브랜치·범위·작업 트리)이 HTML 한 장이 됐다.** 산출물이 `docs/explain-<target>.md`에서 `docs/explain/<target>.html`로 바뀐다. 다른 범위(프로젝트·기능·메서드)와 Brief는 그대로 Markdown이고, 변경 설명도 "md로"라고 하면 Markdown이다
  - tiger-kit `tk-explain-diff`의 핵심 산출물이 오프라인 단일 HTML인데, 앞서 이 스킬에 증류할 때 규율만 가져오고 형식을 빠뜨렸다. 이번에 형식과 함께 빠졌던 내용 규칙도 넣었다: 바뀌지 않아야 할 계약·불변식과 그 근거, 같은 입력의 이전/이후 예시, 변경 노드에서 출발해 영향만 보여 주는 의존 그래프, 의도(문서)와 검증된 동작(코드)의 구분
  - 지키게 하는 장치: `assets/change-template.html`(시작 템플릿, 라이트·다크 토큰, 목차, 접힌 답, 근거 역링크)과 `assets/check_explain.py`(표준 라이브러리 정적 검사: 템플릿 표지·TODO 잔존, 제목, id 중복·깨진 앵커, 외부 리소스 로드, 필수 절, `<details>`, `base..head` SHA 쌍, `path:line`, mermaid·코드 펜스). 렌더는 검사하지 않으므로 receipt에 "render not checked"를 적는다
  - 그림은 직선 흐름이면 세로로 쌓는 상자(바뀜·그대로·사라짐을 테두리와 글자로 구분), 갈래·그래프면 인라인 SVG. 패턴은 `nara-eli5-note`의 그림 카탈로그를 형제 링크로 쓴다
  - 측정: 같은 커밋 설명 task로 2회 모두 파일을 만들고 검사기를 통과했고 grader 4개(부모 SHA, `path:line`, `<details`, 검사기 실행) 통과. 그중 한 파일을 브라우저로 390px·1280px에서 열어 가로 넘침 없음(scrollWidth = innerWidth), 최소 글자 12px, 답 접힘을 확인했다
  - 안 가져온 것: tiger-kit 공용 테마 자산과 설정 파일, 실험 중인 `standard | dialogue | dialogue-eli5 | all` 탭

### Changed (contract reaches installed skills)
- **출력 계약이 설치본에 실린다.** `references/output-contract.md`(저장소 루트)를 `skills/nara-now/references/output-contract.md`로 옮겼다. 설치되는 것은 `skills/<name>/`뿐이라, 지금까지 계약은 nara-kit 저장소 안에서 작업할 때만(CLAUDE.md가 주입할 때만) 적용됐고 다른 저장소의 설치본은 계약을 본 적이 없었다. 이번 Next Action 규칙도 옮기지 않았으면 효과가 없었다
  - 59개 SKILL.md 모두 제목 아래에 계약을 가리키는 한 줄을 넣었다(형제 링크, ADR-0002). 본문이 다르게 정한 곳은 본문이 우선하고, 파일이 없으면(단독 설치) 그 줄은 건너뛴다
  - `tools/check-docs.py`가 이 줄이 없는 스킬과 계약 파일 부재를 실패시킨다. 한 스킬에서 줄을 지웠을 때 실패하는 것을 확인했다
  - `waza check`의 "link escapes skill directory" 경고가 스킬마다 하나씩 늘어난다. 형제 링크 규약상 예상된 경고다
  - Multica autopilot은 등록된 SKILL.md 사본만 쓰므로 계약 파일이 없고, 그 줄은 건너뛴다

### Changed (behavior)
- **`nara-grill`이 질문을 한 라운드에 묶는다(tiger-kit `tk-grill`).** "한 번에 한 질문씩"을 버리고, 지금 추측 없이 답할 수 있는 결정(frontier)을 번호(`Q1`, `Q2`)와 권고를 붙여 한 번에 묻는다. 다른 답에 달린 질문만 미루고 무엇에 걸렸는지 적는다. 결정을 바꿀 수 있는 사실까지만 조사하고, 끝내기 전 빠진 갈래·숨은 가정·모순을 점검하며, 결정 요약을 사용자가 확인한 것만 `confirmed`로 둔다. 질문 라운드 중간 응답은 헤더 없이 쓰고 섹션과 Receipt는 최종 보고에. 판정 4종과 "침묵은 동의가 아니다"는 그대로
  - 측정: 독립 결정 셋과 그중 하나에 달린 결정 하나가 있는 설계 노트로 수정 전 2회는 둘 다 질문 하나만 하고 멈췄다(0/2). 수정 후 2회는 독립 질문 4~5개를 한 라운드에 묻고 의존 질문(중복 제거 키)은 둘 다 미뤘다(2/2). 처음 단 "Q4가 없어야 한다" grader는 질문 번호가 run마다 달라 번호를 재는 결함이었고 뺐다
- **출력 계약 Next Action 규칙**(tiger-kit `tk-adhd`): 남은 사람 할 일은 빠짐없이, 없으면 `next: 없음`(후속 작업을 지어내지 않음), 스킬이 할 수 있는 일을 사용자 명령으로 넘기지 않음. 분량보다 빠짐없음이 먼저, `planned`와 `applied` 구분, 진행 보고의 시간·진행률은 잰 값만
- **`naranizer`가 양태를 보존한다.** "줄여야 합니다"를 "줄이는 것이 어떨까요?"로 바꾸는 것을 허용 예로 들고 있었는데, 이것은 해야 할 일을 해도 되는 일로 바꾸는 의미 변경이다. 자기 판단을 부드럽게 쓰는 것은 그대로 허용하고, 요구·권고·확정의 양태는 불변으로 바꿨다. 자체검증에 "양태 불변" 항목 추가

### Changed (breaking: invocation)
- **원격에 쓰는 여섯 스킬이 명시 호출 전용이 됐다**: `publish-spec`, `spec-revision`, `slack-to-jira`, `worklog`, `jira-triage`, `release-finalize`. 모델이 "준비돼 보인다"는 판단으로 게시·티켓 생성·태그 push를 시작하지 못하게 한다. Claude Code는 프론트매터 `disable-model-invocation: true`, Codex는 새 `agents/openai.yaml`의 `policy.allow_implicit_invocation: false`(Codex는 SKILL.md 플래그를 읽지 않는다)
  - 대가: 이 여섯의 description이 컨텍스트에 실리지 않아 "위키에 올려", "시간 기록해줘" 같은 자연어로는 안 불린다. `/nara-<name>` 또는 `$nara-<name>`으로 부른다. 각 스킬 README의 호출 절을 그렇게 고쳤다
  - Multica autopilot은 등록된 SKILL.md 사본을 쓰므로 이 변경을 재등록 전까지 받지 않는다. 사본을 다시 동기화할 때 autopilot 프롬프트가 스킬을 명시 호출하는지 확인할 것
  - `waza check`가 이 여섯을 spec compliance 8/9(`spec-allowed-fields: disable-model-invocation`)로 표시한다. Claude Code 호스트 확장이라 agentskills.io 핵심 목록에 없을 뿐이고 `npx skills add . --list`는 이 여섯도 찾는다
  - 출발점은 tiger-kit의 `user` / `hybrid` 구분이다. 그쪽은 description 접두어와 README 열까지 세 표면을 스크립트로 맞추고, 여기는 두 표면만 둔다

### Added
- **신규 스킬 셋(tiger-kit `5e35b6a` 재대조 결과, 56 → 59).** 앞선 증류에서 "이미 있음"으로 넘겼다가, 주 산출물 형식까지 행으로 대조하자 nara-kit에 대응물이 없다고 드러난 것들이다
  - `nara-rewrite`: 맥락 모르는 독자를 위한 의미 보존 재작성(한국어·영어). 요구는 요구로, 권고는 권고로, 강도·시제·근거 위치를 지키는 자체 점검을 출력 전에 돌린다. 산출물은 **재작성 한 벌**이고 머리말·분석 블록·점수가 없다. `review` 모드만 `위치 | 문제 | 제안` 지적을 낸다. 고칠 곳이 없으면 원문 그대로가 정상 결과. humanizer(AI 패턴 등급)·naranizer(내 말투)·ko-prose(조사·어미 수리)와 트리거를 나눴고, 그 셋의 DO NOT 줄이 이 스킬을 가리킨다
  - `nara-roadmap`: 불분명한 상황 → 제약 기반 로드맵. repo 없는 기획도 대상. grill과 같은 frontier 라운드로 묻고, 제약을 고정/협상 가능/미확인으로, 범위를 후보/권고/합의로 가른다. 마일스톤은 결과·범위·완료 증거·의존성, 반복 운영은 따로, 조사 마일스톤은 계속/보류/중단 기준. no-go도 결론. 날짜·담당자·수치는 지어내지 않고 `[UNVERIFIED]`. 기본은 대화, 저장 요청 시 `docs/plan/roadmap-<slug>.md`. 기획 흐름 맨 앞
  - `nara-prototype`: 결정 질문 하나를 위한 일회성 프로토타입(UI 변형 2개 또는 로직 harness). 가설과 측정 기준을 먼저 세우고, 저장소가 이미 답하면 만들지 않는다. 연동마다 fake/real 선언, 실행마다 `## Tested` 영수증(명령·cwd·exit code·증거). 산출물은 `## Confirmed`로 시작해 `verdict: Pass | Fail | Blocked | Unverifiable`로 끝나는 `docs/prototypes/<slug>/REPORT.md`. 승격·커밋하지 않는다. 화면 핸드오프는 design-studio가 그대로 맡는다
  - 측정: 측정(같은 요청, 스킬 없음 2회 대 스킬 2회). rewrite: 스킬 없는 2회는 둘 다 요구의 "반드시"를 빼서 강도를 낮추고 재작성 뒤에 변경 설명을 붙였다. 스킬 2회는 "반드시"·숫자·식별자를 지켰지만 내용 없는 상투 문장까지 보존해 "정보 없는 문장은 뺀다" 규칙을 넣었고, 재실행 2회는 상투 문장만 빼고 사실 문장은 남겼다. roadmap: 스킬 없는 2회도 날짜를 지어내지 않고 질문을 여럿 물어 첫 턴 내용은 좋았다. 차이는 질문마다 고를 안과 권고, 요청 주체 구분, `[UNVERIFIED]` 표시였고 grader 차이의 상당 부분은 어휘 차이다. 로드맵 초안 단계는 재지 않았다. prototype: 스킬 없는 2회도 harness를 실제로 돌리고 fake 한계를 밝혔다. 스킬 2회는 `## Confirmed` 비교표, `## Tested` 실행 기록, `verdict:`를 남겼고, 그중 1회가 API 지연을 한 값에 고정해 결정 조건(지연 400ms 경계)을 놓쳐서 "fake 값에 걸린 기준은 경계까지 돌린다" 규칙과 판정 단위(질문 전체) 정의를 넣었다. 두 스킬의 몫은 판단의 질보다 형식·기록의 고정이다
- `tools/eval-fixture.py generate <skill> [--task id]`: Copilot 좌석 없이 실제 모델 출력을 얻는 경로. `claude -p`를 설정·MCP·도구 없이 돌리고 SKILL.md와 references를 시스템 프롬프트에, 태스크 프롬프트와 fixture를 stdin에 넣는다. `validate --right-from gen`이 그 출력을 right 쪽에 쓴다. 도구가 꺼져 있어 스킬 벤치마크가 아니라 그레이더 검증용이고, 생성마다 헤드리스 과금이 든다(nara-gap 1회 약 0.26달러)

- `tools/check-docs.py`: 카탈로그 정합성 검사(표준 라이브러리만). 스킬 디렉터리 ↔ `skills/README.md` 행 1:1, 세 문서(`README.md`·`skills/README.md`·`CLAUDE.md`)의 스킬 수, `metadata.nara.scope: multica` 태그 ↔ Multica 연동 묶음 일치, 형제 스킬 링크 해석, 프론트매터 `name`과 README.md 존재, 명시 호출 전용 플래그의 Claude Code·Codex 두 표면 일치. CLAUDE.md 릴리즈 절의 형제 링크 grep 한 줄을 대체한다. tiger-kit의 같은 역할 스크립트는 행과 디렉터리만 비교해 숫자 드리프트(2026-10-09의 51 대 55, 루트 README의 55 대 56)를 못 잡는다
- `evals/nara-code-review` task `string-identity-conflation`: 부분 문자열·접두어·구분자 없는 합성 키로 정체성을 가르는 결함 셋을 심은 fixture. tiger-kit 리뷰 프로토콜의 "두 엔티티를 만들어 공격하라" 규칙을 들일지 재려고 만들었고, 규칙 없는 현재 스킬이 두 번 다 셋을 잡고 충돌 쌍까지 만들어서 규칙은 넣지 않았다. task는 회귀 감시로 남긴다. `validation.yaml`은 실제로 관찰된 실패 출력이 아직 없어 만들지 않았다

### Changed
- `skills/README.md` 카탈로그를 라이프사이클 단계(Workflow / Requirements / Code Lifecycle / Documentation / Testing / Automation / Meta)에서 **하고 싶은 일** 기준 9묶음(준비·기획 / 구현 / 검증 / 리뷰·PR·릴리즈 / 디자인 / 글쓰기·설명 / 세션·툴킷 / 연동·자동화 / Multica 연동)으로 재편. tiger-kit `5e35b6a` 증류 결과이고 리포트는 gitignore 대상인 `docs/research/`에 로컬 보관한다. 단계 기준으로도 어긋나 있던 5행(`design-*` 셋이 Workflow, `incident`·`slack-to-jira`가 Requirements)이 제자리로 갔다. 디렉터리는 안 옮겼으므로 consumer에게 breaking 아님
- **Multica 연동** 묶음 신설: `multica` CLI 없이는 동작하지 않는 다섯 스킬(`jira-triage`, `jira-drain`, `review-reminder`, `review-queue`, `pr-activity-reminder`)을 일반 스킬과 분리. 루트 README에 묶음별 색인과 제외 안내 추가. Multica를 스케줄 호스트 선택지로만 쓰는 `trending-digest`·`release-watch`·`worklog`는 일반 묶음에 남김. 다섯 스킬 프론트매터에 `metadata.nara.scope: multica`를 달아 묶음 소속을 `check-docs.py`가 검사한다(Claude Code는 `metadata`를 무시한다)
- 출력 계약 9절에 ESCALATE 자리 규칙 추가: 답을 받아야 진행하는 항목은 receipt의 마지막 산문 블록, 꼬리 산문은 앞으로. 근거는 2026-10-12 로컬 transcript 68개 측정(턴 종료 메시지의 10~14%가 질문 뒤 꼬리 산문)

- **`nara-pr-respond`가 답글에서 끝나지 않고 스레드 정리까지 간다.** 승인 목록에 push, 답글, 스레드 resolve(`resolveReviewThread`), 재리뷰 요청(`gh pr edit --add-reviewer`)을 명령과 함께 올리고, 승인되면 그 순서로 실행한다. "Fixed." 답글은 수정이 원격 브랜치에 올라간 뒤에만 단다
  - 새 처분 **FOLLOW-UP**: 맞는 지적이지만 이 PR이 만들지도 키우지도 않은 기존 결함이면 여기서 고치지 않고, 범위 밖이라는 것과 별도 이슈 여부를 답한다. 코멘트가 달린 줄이 PR에서 안 바뀌었고 blame이 PR보다 앞서는지를 먼저 본다. 런타임 장애·보안·데이터 손실·권한·공개 API는 이 PR에 남긴다. 리뷰어가 수정을 요청한 것이면 사용자가 뒤집을 수 있게 표시한다
  - resolve는 답글이 실제로 달렸고 처분이 끝난 스레드만(ACCEPT·FOLLOW-UP·답변한 질문). HOLD·ASK·답을 기다리는 REBUT은 열어 둔다. 재리뷰는 리뷰어별 마지막 상태가 `CHANGES_REQUESTED`인 사람과 지적이 고쳐진 사람에게. 중간에 끊겼다 다시 들어오면 원격 상태부터 읽는다
  - 측정: 같은 fixture(바뀐 줄 지적·안 바뀐 줄의 기존 결함 지적·nit, 변경 요청 리뷰어 1명)로 수정 전 2회는 0/2 통과(둘 다 기존 결함을 HOLD로 넣었고 resolve·재리뷰는 "스킬에 없음"으로 빠지거나 선택 사항으로만 나옴), 수정 후 2회는 2/2 통과. 출처는 tiger-kit `tk-pr-respond`(`5e35b6a`)
- **`nara-explain`이 PR·커밋·브랜치·작업 트리 설명을 따로 다룬다(tiger-kit `tk-explain-diff` 증류).** 비교 기준 SHA를 먼저 고정하고(PR은 merge base, 커밋은 부모), 주장마다 `path:line`을 달고(삭제된 코드는 `base:`), 배경 → 직관 → 흐름 → 꼭 볼 곳/훑어도 되는 곳 → 이해 확인 순서로 쓴다. 보안·스키마·마이그레이션·호환·공개 API 변경은 작아도 "꼭 볼 곳"에 둔다. USE FOR에 "이 PR 뭐 바꿨는지 설명해줘", "이 커밋 설명", "diff 설명" 추가. 저장 기준을 "길면"에서 "약 40줄 초과 또는 요청 시, `docs/explain-<short SHA | pr-N | 기능명>.md`"로 구체화
  - 측정: 이 repo 커밋 하나를 팀원에게 설명하는 task로 수정 전 2회는 0/2 통과(부모 SHA 없음, 줄 인용 없음, 두 run 모두 "커밋은 scope 표 어느 행에도 없다"고 표시), 수정 후 2회는 2/2 통과. 수정 후 출력은 경고만 하고 막지 않는 stale 검사 같은 "꼭 볼 곳"까지 짚었다
- 두 스킬 SKILL.md 토큰이 늘었다(pr-respond 782 → 972, explain 461 → 595). 절차와 템플릿은 references로 내리고 본문에는 결정 규칙만 남겼다
- **`nara-pr`이 repo의 PR 규칙을 먼저 읽는다(tiger-kit `tk-pr-open` 증류).** 기본 브랜치의 PR 템플릿, CONTRIBUTING·AGENTS·CLAUDE.md의 PR 지침, 최근 머지된 PR 제목을 본다. 제목은 repo 지침 > 템플릿·관리자 문서 > 최근 머지 관례 > 내장 형식 순서. 템플릿이 있으면 헤딩·HTML 주석·체크리스트를 그대로 두고 채우며, QA 표는 템플릿의 검증 헤딩 아래로 간다. 체크박스는 이 브랜치에서 확인한 것만 체크한다. 확인 화면에 어떤 규칙이 정했는지 한 줄(`규칙: template ... · title ...`). 내장 5섹션과 `<TICKET> <type>:` 제목은 규칙이 없을 때의 기본값이 됐다
  - 측정: PR 템플릿과 CONTRIBUTING 제목 규칙이 있는 저장소를 만드는 fixture 스크립트(`evals/nara-pr/fixtures/template-repo.sh`)로 수정 전 2회는 0/2 통과(내장 5섹션으로 템플릿을 덮어쓰고 제목은 `PROJ-77 feat:`), 수정 후 2회는 2/2 통과(`feat(report): ... (PROJ-77)`, 템플릿 헤딩 유지)
  - 함께 고침: body-guide가 "— (기능 없음)"을 요구해 ko-prose의 em dash 금지와 부딪히던 것을 "(기능 없음)"으로. Step 0의 "1~6"을 실제 단계 수인 "1~8"로

### Fixed
- `tools/check-docs.py`의 형제 링크 검사가 `references/` 안에서 거는 `../../nara-*` 링크를 세지 못했다(예전 grep 한 줄도 같았다). 정규식을 넓혀 검사 대상이 8개에서 15개로 늘었다
- 직전 커밋 CHANGELOG에서 `check-docs.py` 항목의 한 문장이 code-review eval 항목 끝에 잘못 붙어 있던 것을 제자리로
- 루트 `README.md` 영문 소개가 55 skills, 바로 아래 한글이 56개로 어긋나 있던 것을 56으로 통일

## [0.23.0] - 2026-10-12

### Added

- **`nara-research` 신설: 결정 하나를 위한 외부 선행 사례 비교와 남의 스킬·repo 증류를 리포트 한 장으로 남긴다.** 외부 repo를 보고 "뭘 가져올까"를 정하는 일이 매번 대화 안에서 끝나서 어느 revision을 읽었는지, 왜 안 가져왔는지가 남지 않았다
  - 두 모드다. 선행 사례 비교는 결정과 후보를 받아 외부 증거로 가르고, 증류(`--source`)는 스킬·워크플로·repo를 `keep | adapt | omit`으로 가르고 형태(reference 추가 / 기존 스킬 개선 / 독립 스킬 / no-op)를 판정한다. 결과는 제안이고 적용은 `nara-skill-forge`, 기록은 `nara-adr`이 한다
  - 출처는 revision을 고정하고(SHA·버전·접근일) 결정에 걸리는 주장은 구절을 인용한다. 링크가 열리는 것과 주장을 뒷받침하는 것은 다른 검사다. 못 읽은 주장은 `[UNVERIFIED: requires <source>]`로 남기고 재현 안 한 효능은 그렇다고 적는다. trailing status가 `sources`·`claims`·`verdict`·`distill`을 센다
  - 산출물은 `docs/research/YYMMDD-<slug>.md` 하나다. 상태 파일은 없고 같은 결정을 다시 보면 `--update`로 갱신 절을 덧붙인다
  - 출발점은 tiger-kit `tk-research`(`fd7a7a0`)다. 증거 규율, 증류 절차, 출처 색인 형식을 가져왔고 영속 연구 상태(frontier 재생성, 체크포인트 ID, `--resume`)와 실험 하네스, HTML 리포트는 안 가져왔다. 워크플로를 상태머신으로 포장한 스킬은 nara-kit에서 쓰이지 않았다
  - evals는 트리거·안티트리거 2건이고 실제 실행 전이라 `validation.yaml`은 아직 없다

- **`nara-qa-sheet` 신설: 자동 검증이 못 닿은 화면을 사람이 볼 체크리스트로 넘긴다.** `nara-gap`과 `nara-browser-verify`는 증거가 없으면 `Unverifiable`을 낸다. 맞는 판정이지만 그 항목을 누가 확인하는지는 남지 않았다
  - 산출물은 HTML 파일 하나(`docs/qa/YYMMDD-<slug>.html`)다. 체크와 메모가 브라우저에 저장되고, "결과 복사"가 PR 본문에 붙일 Markdown을 만든다
  - 자동으로 밟은 줄(`auto-verified`)과 사람이 볼 줄을 분리한다. 그 뒤 커밋이 해당 화면의 렌더·요청 경로를 건드리면 자동 표시를 `manual`로 내리고 옛 증거는 이전 증거로만 남긴다
  - 화면에 직접 못 들어가 본 줄은 `code-only`로 표시하고 라벨을 지어내지 않는다
  - 출발점은 MTGVim/tiger-kit의 `tk-qa-sheet`이고 템플릿과 점검 스크립트(`check_sheet.py`)는 새로 썼다. 그쪽이 하는 시트 자체의 헤드리스 재검증과 JS 없는 정적 목록 재생성은 가져오지 않았다
  - verify의 세 번째 트랙이 아니다. 판정은 여전히 두 트랙이 하고 이 스킬은 인계만 한다. `nara-now`는 gap의 `Needs Confirm`이나 browser-verify의 `Unverifiable`이 남아 있으면 리뷰 준비 문구 뒤에 인계 한 줄을 덧붙인다
  - `nara-browser-verify` 영수증에 `head:` 줄이 생겼다(run 디렉터리에도 같은 값). 시트의 자동 검증 표시가 어느 커밋의 증거인지 여기서 읽는다. 이 값이 없던 run은 증거로 쓰지 않는다

- **UI 라벨과 진입 경로는 본 것만 쓴다는 규칙을 다섯 군데에 넣었다.** PR 본문의 "어디서", 테스트 시나리오의 진입경로, 골든패스 export의 Entry path, QA 시트, 충실도 리뷰어의 문구 비교가 대상이다. 라우트·컴포넌트명·i18n 키·티켓 문구는 라벨의 증거가 아니고, 확인 못 한 것은 `code-only`로 두고 채우는 데 필요한 가장 작은 입력을 적는다
  - 수집 방법(초기 렌더 뒤 화면 텍스트를 한 번에 받기, breadcrumb이 증명하는 범위, 못 구했을 때 적을 네 가지)은 `nara-browser-verify/references/ui-evidence.md`가 소유한다. 나머지는 핵심 문단을 직접 갖고 형제 링크로 가리키므로 그 파일이 없어도 동작한다

- **`nara-code-review`에 기획 충실도 리뷰어 `spec-fidelity`가 생겼다.** 기존 리뷰어는 전부 "이 코드가 깨질 수 있나"를 묻는다. 기획문서는 참고 자료로만 들어가서, 내부적으로 흠 없는 코드가 요청과 다른 기능이어도 finding이 나오지 않았다
  - 문서로 된 요구사항(`docs/requirements.md`, `docs/plan.md`의 해당 작업 단위, spec 파일, 티켓 AC)이 있을 때만 뜬다. 커밋 메시지나 테스트 이름만으로는 안 뜬다. 그건 한 일이지 요청받은 일이 아니다. 안 뜨면 리포트 헤더에 `fidelity: skipped`로 남긴다
  - 누락, 다르게 구현, 부분 구현, 요청 없는 동작 네 가지로 분류한다. 요구사항을 원문 그대로 인용하지 않은 finding은 취합에서 떨어진다
  - 기획문서가 말하지 않은 부분은 finding이 아니라 확인 질문으로 보낸다. 코드 쪽에 나중 결정의 흔적이 있으면 어느 쪽을 고칠지 사람이 정하도록 R3로 올린다
  - `nara-gap`과 겹치지 않는다. 그쪽은 요구사항 전체 대비 점수이고 이쪽은 이번 변경에 대한 finding이다. `docs/gap.md`는 단서로만 쓰고 판정으로 베끼지 않는다
  - `nara-pr-review`도 같은 라우팅을 재사용하므로, PR이 가리키는 티켓이나 스펙을 읽을 수 있을 때 함께 뜬다

- **`nara-design-studio` 런타임이 호스트에게 무엇을 하는 호스트인지 묻는다.** 호스트가 페이지 스크립트보다 먼저 `window.STUDIO_HOST = { fulfills: true, layoutCheck: false }`를 선언하고, 런타임이 그걸 읽어 문구와 메뉴를 고른다. `serve.py`는 아무것도 선언하지 않고 지금 동작을 그대로 유지한다
  - `fulfills`는 **호스트가 받은 것을 이미 처리했다**는 뜻이다. 그러면 Send to Agent와 Export → PNG가 복사용 텍스트 상자를 띄우지 않고 토스트 한 줄로 끝낸다. 끝난 일을 복사하라고 내놓으면 실패한 일처럼 읽힌다. Export → PNG의 "watch-captures.sh를 돌리는 browser-MCP 에이전트가 Downloads에 저장한다" 안내도 같이 사라진다 — 에이전트를 직접 붙들고 있는 호스트에서는 전부 거짓이다
  - `layoutCheck: false`는 **`check-layout.py`를 함께 배포하지 않는 호스트**라는 뜻이다. Export 메뉴에서 layout contract 항목이 빠지고, Spec.md의 "Export → Layout contract (JSON)으로 기계 검증하라" 문장도 빠진다. 계약 본문은 남는다. 없는 메뉴와 없는 스크립트를 구현자가 찾게 만드는 문장이 제일 비싼 거짓말이다
  - **응답에 플래그를 싣는 방식을 먼저 만들었고 되돌렸다.** `/__capture`가 `{"fulfilled":true}`를 주고 studio.js가 그걸 읽는 구조였는데, 답이 필요한 자리 중 하나가 **메뉴 라벨**이다. 메뉴는 열리는 순간 동기로 만들어지니 응답을 기다릴 수 없고, 라벨은 첫 클릭 **전에** 맞아야 한다. 같은 사실을 두 군데서 관리하게 되는 문제도 있었다
  - 없는 키는 "예"로 읽는다(`layoutCheck !== false`). 기존 소비자가 선언 없이 그대로 동작해야 하고, `serve.py`는 그 스크립트와 같은 디렉터리에 있다
  - `flash()`에 `studio-flash` 클래스를 붙였다. 호스트가 디자인을 캡처할 때 화면에 남아 있던 토스트가 같이 찍히는 것을 걷어낼 수 있어야 한다


- **`nara-eli5-note`가 읽을 사람을 인자로 받는다.** 나이(5·10·15·20~30·40+), 학년(초등~대학원), 직군(매니저·엔지니어·디자이너·디렉터·PM·동료), 관계(배우자·부모·아이·친구) 네 계열이고 기본값은 5살이다. 그동안 톤이 eli5 하나로 뭉쳐 있어서 사실상 5살 고정이었다
  - **플래그를 만들지 않았다.** 인자에 쓴 자연어에서 읽는다(`/nara-eli5-note 15살에게 설명하듯 ... 정리해`). 대상이 인자에 있으면 되묻지 않고, 없으면 기본값으로 간다 — 축이 하나 늘었다고 질문이 하나 늘면 안 된다
  - 대상은 어휘와 비유 소재만이 아니라 **그림 비중과 절 개수**도 바꾼다. 15살 아래면 절마다 그림 하나를 목표로 잡고, 직군·대학원으로 갈수록 그림 자리를 표와 코드가 채운다. 수치는 어느 대상이든 지우지 않고 감싼다
  - 대상이 엔지니어·대학원이면 eli5 대신 실무 노트체를 권한다. 그 대상에게 비유는 번역이 한 겹 더 붙는 일이다
  - 표는 `dreambigou/eli5`(MIT)의 audience 표를 노트라는 매체에 맞게 고쳐 `references/audience.md`로 네이티브화했다. 그 스킬이 설치돼 있지 않아도 동작한다
  - 고른 대상은 노트 도입부 인용 블록에 한 줄 남긴다. frontmatter는 건드리지 않는다 — vault 스키마가 `created`/`updated`/`tags` 셋뿐이다
  - 같은 커밋에서 `references/` 참조를 백틱에서 마크다운 링크로 바꿨다. `waza check` 링크 점수가 1/2에서 8/9로 올랐고 orphan 경고가 사라졌다
- **판정 카드에서 재리뷰를 요청할 수 있다.** 카드를 `in_progress`로 옮기면 PR 전체를 다시 판정하고, 결과를 그 카드에 붙인 뒤 `in_review`로 되돌린다. 라운드마다 반복 가능하다. **새 커밋 감지로 자동 발동하지는 않는다.** 사람이 요청할 때만 돈다. 착수가 `/drain` 코멘트로 옮겨갔으므로 이 드래그는 보드에 남은 유일한 컬럼 제스처다
  - 착수 가드를 "실행 중"으로 좁혔다(`review_state ∈ {dispatched, blocked}`). 예전엔 `review_state`에 값이 있기만 하면 건너뛰었는데, 판정값(`passed`/`changes_requested`)이 바로 그 자리에 저장되고 `/post`가 그걸 읽어 "게시할 판정이 있다"를 판정한다. 그래서 값을 지울 수도 없고, 있다고 바쁘다고 읽으면 첫 판정이 영구히 굳어 드래그가 할 일이 없어진다
  - `todo`가 "리뷰해줘"로 읽히는 건 아직 판정 안 난 판정 카드 하나뿐이다. `reviewed`가 붙은 카드는 드래그로만 돈다
  - 수집 시 `reviewed_sha`를 남긴다. 나중에 증분 재리뷰로 갈 여지를 열어둔 기록이고, 지금 판정은 매번 전체다

- **게시 계약을 `nara-pr-review/references/posting.md`로 분리했다.** 스킬 6단계와 별도 게시 실행이 같은 문서를 본다. 규칙을 양쪽에 복사해두면 한쪽만 바뀌어 갈라진다
  - 이 과정에서 드러난 것: **헤드리스 실행에 nara- 스킬이 하나도 로드되지 않았다.** 스킬은 `~/.claude/skills`에 있고 `~/.codex/skills`에는 `.system` 6개뿐이다. 실행기(git 밖) 프롬프트가 `$nara-pr-review <url>`, `$nara-claim-audit`을 참조해왔는데 전부 죽은 참조였고, 리뷰와 기획 산출물은 스킬이 아니라 프롬프트 템플릿만 보고 만들어졌다. 실행기가 계약 스킬을 워크트리에 복사하는 방식으로 바꿨다 — `SKILL.md` + `references/` 트리를 구조 보존해서, SKILL.md 안의 상대 링크가 그대로 열린다. 처음엔 플랫하게 이름을 바꿔 복사했는데 그게 링크를 전부 깨뜨렸다
  - `posting.md`의 형제 스킬 링크에 부재 동작을 명시했다. 헤드리스 실행에서는 그 스킬이 복사되지 않으므로 열리지 않는 것이 정상이고, 게시 규칙은 이 문서로 완결된다
- **판정을 PR에 게시하는 제스처가 생겼다.** 카드에 `/post`(코멘트만) 또는 `/approve`(approve까지)라고 코멘트하면 판정이 PR에 올라간다. 그동안 파이프라인이 PR에 대해 완전히 read-only여서, 판정이 나와도 사람이 손으로 옮겨 적는 것 말고는 전달 경로가 없었다
  - **트리거를 라벨에서 코멘트로 바꿨다.** 처음엔 라벨(`post-comment`/`post-approve`)로 만들었는데 GUI에 라벨 UI가 없어서 CLI 전용이었다. 게다가 `issue label add`는 이름이 아니라 label UUID를 받는다. 사람이 실제로 쓸 수 있는 입력은 코멘트다. 라벨 경로도 남겨뒀다
  - 토큰은 코멘트 맨 앞에서만 인식한다. 뒤에 말을 이어 쓸 수 있고(`/post 이대로 올려줘`), "나중에 /post 할게"나 `/poster`는 발동하지 않는다. 스크립트 코멘트는 전부 멘션으로 시작하므로 자기 코멘트에 스스로 걸리지 않는다
  - **모든 거부가 카드에 이유를 남기고 트리거를 소비한다.** 판정 없음·PR 주소 없음·repo 매핑 없음 모두. 첫 구현은 비용을 아끼려고 판정 없는 카드의 코멘트를 안 읽었는데, 그러면 `/post`가 조용히 무시된다. 답하는 비용은 CLI 호출 하나고, 답하지 않는 비용은 제스처에 대한 신뢰다
  - 재요청은 새 코멘트로 한다. 소비 기준이 코멘트 id라서 같은 카드에 다시 쓰면 다시 게시된다
  - **status 드래그가 아닌 이유.** 남의 PR에 게시하는 건 바깥으로 나가는 행동이라 컬럼 이동이 암시할 성격이 아니다. 라벨 둘이 동시에 붙으면 추측하지 않고 아무것도 게시하지 않는다
  - **approve는 `status: pass`에서 유도하지 않는다.** 머지 신호라서 사람이 approve를 명시한 것만이 근거다. 다만 허용 여부는 판정문의 `status:`와 `blocking:` 카운트로 **게시 세션이 뜨기 전에** 결정한다. `blocking`이 0보다 크거나 `status`가 `changes_requested`·`blocked`면 워크트리 없이 거부하고 이유를 카드에 남긴다
  - 처음엔 이 게이트를 게시 세션의 판정문 독해에 맡겼고, 그게 오작동했다. `blocking: 0` 판정의 summary가 "주석 보정과 회귀 테스트가 필요하다"로 끝나는 것을 "수정을 요구하는 판정"으로 읽어 approve를 거부했다. 그건 approve-with-nits의 정상 모양이라, 그 규칙 아래서는 비차단 지적만 있는 PR이 영구히 approve되지 못한다. 같은 카드에서 하루 간격으로 두 번 같은 거부가 나왔고 매번 워크트리와 세션을 2분씩 태웠다. 기계 필드가 옆에 있는데 산문을 판별식으로 쓴 것이 원인이다
  - 스크립트가 아니라 워크트리 에이전트가 게시한다. 판정문은 보드용으로 쓰인 글이라 `status:`·`blocking:` 같은 기계 헤더와 "PR에는 게시하지 않았다" 류 내부 문구가 섞여 있고 언어도 보드 기준이다. 다시 쓰기가 필요하고 그건 판단이다. 지적 내용·근거·심각도는 변경 금지
  - 판정문은 스크립트가 카드 코멘트에서 뽑아 워크트리에 넣어준다. 판정 당시의 `.review-result.md`는 수집 때 워크트리와 함께 사라지고, codex 샌드박스는 카드에 접근할 수 없다
  - 게시 성공 후 status는 건드리지 않는다. 카드를 닫는 권한은 reconcile에만 있고, 조건은 PR이 `MERGED`/`CLOSED`인 것 하나다
  - `post_*` 키는 `review_*`와 별개다. 판정과 게시는 다른 실행이고 재시도 조건도 다르다
- **판정에 되물을 수 있다.** 카드에 `/ask <질문>`이라고 코멘트하면 새 세션이 그 PR을 다시 보고 답하고, 답이 질문 아래 스레드로 돌아온다. 그동안 판정은 막다른 길이었다 — 리뷰는 헤드리스 워크트리에서 돌고 그 워크트리는 수집과 함께 사라지므로, 사람이 판정을 읽는 시점에 판정을 쓴 세션이 존재하지 않았다. 기존 두 제스처는 둘 다 판정을 바깥으로 내보내는 것이라 판정을 의심할 경로가 없었다
  - **재리뷰는 대안이 아니다.** 새 리뷰는 카드를 읽지 않아서 질문을 볼 수 없고, 같은 판정을 다시 낸다. 그래서 `/ask`는 세션에 리뷰가 볼 수 없었던 두 가지를 준다: 먼저 나온 판정문과 질문
  - **판정문을 남의 주장으로 취급하게 프롬프트가 강제한다.** 오탐이면 오탐이라고 답하는 것이 이 실행의 목적이고, 판정을 방어하는 것은 실패다. 자기가 쓴 판정을 방어하는 것이 이 자리의 기본 실패 모양이라 프롬프트에 이름 붙여 적었다
  - 판정문이 없어도 답한다. 아직 리뷰가 안 돌아간 카드에서 질문을 거부하는 것은 "물어본다"는 말의 이상한 해석이다. 이 경우 판정문 부재를 밝히고 PR만 근거로 답한다
  - 답은 `--parent`로 질문 아래 스레드에 달린다. 질문과 답은 한 번의 주고받음이고, 평평한 카드에서는 여러 왕복이 파이프라인 자신의 상태 코멘트와 뒤섞인다
  - 반복이 곧 대화다. 소비 기준이 코멘트 id라서 `/ask`를 다시 쓰면 다시 돈다. 질문 없는 `/ask`는 이유를 남기고 트리거를 소비한다
  - `/ask`에는 라벨 짝이 없다. 질문은 본문이 필요해서 라벨로 표현할 수 없다
  - `ask_*` 키는 `post_*`·`review_*`와 별개다. 덕분에 한 카드에서 질문과 게시가 동시에 떠 있어도 서로의 상태를 덮지 않는다
  - 카드가 `cancelled`로 가면 리뷰어와 답변 세션을 **둘 다** 정리한다. `review_state`만 보고 판단하면 진행 중인 질문이 워크트리째 남는다
  - 카드 코멘트 조회를 실행 단위로 memoise했다. 두 패스가 같은 카드에서 같은 목록을 읽고 그런 카드가 20여 개라서, 안 하면 분당 CLI 호출이 두 배가 된다. `comment()`가 자기가 쓴 카드의 캐시를 버리므로 패스 실행 순서에 의존하지 않는다

- `nara-wip-sweep` 신설 — `In Progress`로 방치된 할당 티켓을 한 번에 쓸어내 분류한다. "In Progress 35건"은 작업량이 아니라 상태 부채이고, 그게 섞여 있으면 어떤 브리핑도 "오늘 무엇부터"를 답할 수 없다
  - 분류 근거는 **실측**이다: 단어 경계 매칭(`(^|[^A-Za-z0-9])KEY([^0-9]|$)`) PR 조회, subtask 보유(컨테이너), 본문 AC 유무, 마지막 갱신 경과일. `gh pr list --search`는 fuzzy해서 `PROJ-4` 질의에 `PROJ-40`이 온다
  - **티켓을 전이시키지 않는다.** 팀이 보는 Jira에서 상태 변경은 "이 일을 안 한다"는 선언이라 사람 판정이다. `metadata.pr_url` 같은 캐시된 링크도 근거로 쓰지 않는다 — 키 검증 없이 심어져 딴 티켓 PR이 붙은 사례가 있다
  - 산출물은 실행 디렉터리의 `wip-sweep.md`. 여러 프로젝트를 걸치는 상태 보고서라 어느 repo의 `docs/`에도 넣지 않는다
  - 첫 실행(35건)에서 사실상 종료 4건(머지 PR 보유), 착수 불가 3건(본문 없음), 컨테이너 3건, 방치 1건을 분리했다. `LYRIS-505`는 merged PR 19건이라 다수 규칙에 따라 모호로 남겼다

- `nara-worklog` subtask 전환 마커 — `worklog.py mark <SUBTASK>`가 ledger에 `ev: "switch"`를 append하고, 리듀서가 마커 이후 구간을 그 티켓에 귀속시킨다. 브랜치 하나로 여러 subtask를 오가는 실제 작업 방식을 위한 것 (worklog를 leaf에 다는 방향)
  - 마커는 **브랜치 티켓의 ledger**에 들어간다 — hook이 쓰는 그 파일이므로 subtask별 ledger가 새로 생기지 않는다. 마커 이전 구간은 브랜치 티켓(대개 부모)에 남고, 그건 `mark`를 잊었다는 신호다
  - 마커는 시간을 만들거나 없애지 않는다. span을 자를 뿐이라 귀속 합계 = 원본 합계 (테스트로 고정). 유휴 구간의 마커는 자기 시간 없이 다음 span의 소유자만 정한다
  - 출력이 `(날짜 × 티켓)` 버킷 구조로 바뀌어 Jira 쓰기가 버킷당 1건이 된다. 승인 게이트에 **부모 귀속 경고**(subtask 있는 티켓인데 마커 없이 부모로 잡힌 구간)와 **쓰기 전 `jira_get_worklog` 대조**를 추가 — watermark는 이 ledger 안에서만 유효해서 다른 경로로 올라간 기록을 모른다
  - **마커 없이 지난 시간은 사후 분리 불가.** hook은 브랜치명의 티켓 키만 안다. 추측으로 채우지 않는다
  - 3-리뷰어 집중 코드 리뷰 반영 (17건 → R0/R1 15건 적용, R2 2건 이월). 리포트: `docs/review/260903-worklog-marker-mode.md`
    - **시간이 창조되는 경로 2개**를 테스트로 막았다: `read_switches`의 `sorted()`를 제거하면 조각이 겹쳐 60분 입력이 100분으로 청구되고(subtask 2개 소실), `build_spans`의 `sorted()`를 제거하면 span이 -2h 20m가 된다. 둘 다 `attribute`의 `else: break`가 전제하는 정렬인데 테스트가 0건이었다
    - naive `ts` + 마커가 `TypeError`를 냈다 — `read_switches`는 승격하는데 `build_spans`는 안 했다. 마커가 방아쇠라 이 변경이 만든 새 크래시 경로다. `as_aware()` 헬퍼로 세 리더를 통일
    - 버킷 정렬 키가 ISO **문자열**이었다. 한 ledger에 offset이 섞이면(컨테이너 TZ=UTC + 호스트 KST) 문자열 순서 ≠ 시각 순서라 문서화된 오름차순 쓰기가 역전된다
    - `NARA_WORKLOG_GAP_MINUTES` 검증 추가 — 문서에 "1 이상의 정수"라 적어놓고 코드에 검사가 없었다. `0`은 조용히 모든 유휴를 분할해 읽기·검토 시간을 전부 빼먹는다
    - 승인 게이트 Example 표에 **티켓 열**을 넣었다. "단위는 (날짜×티켓) 버킷"이라 선언하면서 표는 티켓 열이 없어, 하루 2버킷이 한 행으로 접히고 사람이 일 합계만 승인하는 동안 쓰기는 서로 다른 issue_key에 2건 나갔다
    - 내가 추가한 `day_spans()` 테스트 헬퍼가 **정렬을 해서** `reversed(spans)` 회귀를 가렸다 — 실제로는 `jira_started`가 3h36m 어긋난다. 정렬 제거 + 버킷 1개가 span 2개를 갖는 픽스처로 pin. 리뷰 전 assertion은 이 변이를 잡았으므로 커버리지 순손실이었다
    - 테스트 54 → **69건**, 변이 재검증 **12/12 KILLED**(전부 이전엔 생존)
    - 이월 R2 2건은 같은 뿌리 — watermark가 아직 날짜 단위 가정이라 하루 안에서 귀속이 교차하면 부분실패 시 시간 소실/중복 게시가 가능하고, `day["time_spent"]`가 raw 합계를 한 번만 내려 승인값(`3h 59m`)과 실제 기록(`3h 56m`)이 어긋난다

### Changed

- **`nara-code-review`의 Judge가 지적을 기각하려면 직접적인 반대 증거가 있어야 한다.** 이미 있는 가드, 불가능한 상태, 이미 처리하는 호출자, 테스트 같은 것이다. "추측 같다"나 낮은 확신은 기각 사유가 아니고, 재현도 반박도 못 하면 `needs-context`로 둔다. `downgraded`는 영향이 실제로 작다고 잰 경우에만 쓴다
  - 리뷰어가 돌아와도 대상을 읽은 흔적(`coverage:`)이 없으면 통과로 세지 않는다. 한 번 새로 띄우고, 그래도 안 되면 그 리뷰어를 `unverifiable`로 리포트에 남긴다. 빈 응답이 "지적 0건"으로 집계되던 구멍이다
  - 구현자의 설명(구현 노트, 커밋 본문의 해명, "이미 처리됨", 테스트 통과 주장)은 리뷰어에게 주지 않고 Judge에게 단서로만 준다. 해명을 먼저 읽은 리뷰어는 코드가 아니라 해명을 리뷰한다
  - 확정된 지적이 틀렸다는 증거가 있으면 새 Judge가 그 건만 다시 본다. 받아들여지면 `disproved`로 닫고 ledger에서도 `DISPROVED`로 빠진다(Verifier가 MISMATCH로 올리지 않는다). Fixer와 main 세션이 스스로 기각할 수는 없다
  - 충실도 리뷰어의 `Missing` 지적은 symbol이 없다. Verifier의 Located 판정은 그 파일에서 `validation`이 지목한 구현이 생겼는지로 한다
  - `docs/implementation-notes.md`의 Tradeoffs·Design decisions는 구현자 해명 묶음으로 수집해 Judge에게만 준다. **Deviations 절만 예외로 충실도 리뷰어에게 준다.** 의도적 이탈을 리뷰어가 못 보면 결함으로 잡히고, Judge는 코드 밖 이유로 기각할 수 없어 `--fix=safe`가 결정을 되돌린다. 선언된 이탈은 지적에서 사라지지 않고 `declared: <ID>` + R3로 올라가 사람이 정한다

- **`nara-code-review`의 Judge가 minor finding도 사실 검토한다.** 그동안 자동 수정 대상이 아닌 minor는 Judge를 건너뛰고 `unadjudicated`로 리포트에 실렸다. 거짓인 minor도 읽는 사람의 수정 시간을 쓴다. 이제 건너뛰는 것은 어떤 모드에서도 고치지 않는 `suggestion`뿐이다. 리뷰당 Judge 호출이 늘어난다

- **`nara-pr-review`가 리뷰어와 lane을 subagent로 띄우라고 명시한다.** 그동안 "4 lane, 병렬"이라고만 적혀 있어서 main 세션이 lane을 직접 순회해도 문구상 위반이 아니었다. 다른 리뷰 스킬 셋(`nara-code-review`, `nara-adversarial-review`, `nara-test-verify`)은 이미 subagent를 명시한다
  - code-plane 리뷰어와 PR-plane lane 4개를 한 배치로 띄우고 Judge도 별도 subagent로 둔다. `nara-code-review`가 없는 standalone fallback 경로에도 같은 규칙이 적용된다. 그 경로에는 디스패치 지시가 아예 없었다
  - subagent의 shell은 main의 `export GH_HOST`를 물려받지 않는다. 수집분을 프롬프트에 붙여 넣고, 추가 조회는 명령마다 `GH_HOST=<host>`를 붙이게 했다
  - trailing status에 `dispatch:` 줄을 추가했다. subagent를 못 띄우는 환경에서는 inline으로 내려가되 사유를 남긴다. code-plane 리뷰어에게는 변경 파일 전체 본문을 프롬프트에 넣어 주고 스스로 조회하게 두지 않는다

- **`nara-jira-triage`의 보드가 Jira의 거울이 됐다.** 지금까지는 착수 가능한 티켓만 큐에 넣고 Jira로는 아무것도 되쓰지 않아서, 손으로 In Progress로 옮긴 티켓은 보드에 없고 PR이 열린 티켓은 Jira에서 계속 In Progress였다
  - **폴링이 In Progress와 In Review까지 본다.** 이 상태의 티켓은 `card_origin=mirror` 카드로 들어온다. 착수 지시가 아니라서 멘션도 구현 가능성 판정도 없고, 카드 상태는 스킬이 아니라 reconcile이 옮긴다. config에 `mirror_statuses`가 없으면 예전처럼 동작한다
  - **구현 가능성을 큐에 넣는 시점에 본다.** 구현·버그픽스 티켓이 무엇을 바꾸는지, 끝났다는 조건이 무엇인지, 미결 사항이 남았는지를 판정해서 부족하면 카드를 `blocked`로 두고 빠진 것을 질문으로 단다. 표시는 `triage_block`이고 `drain_state`와 다른 키다(착수 실행기가 모르는 `drain_state` 값을 보면 `/drain`을 거부한다). 판정은 후보라서 애매하면 막지 않고, 막힌 카드도 사람이 `/drain`으로 넘길 수 있다
  - **취소된 카드는 dedup에서 없는 것으로 본다.** 한 번 취소된 티켓은 Jira에서 다시 To Do가 돼도 영영 큐에 안 들어왔다. `done` 카드는 스킵 근거로 남겼다. 머지됐는데 Jira 전이가 실패한 티켓이 회차마다 다시 들어오는 것을 막기 위해서다
  - **reconcile 계약을 `references/reconcile.md`로 옮기고 넓혔다.** Jira 되쓰기가 기본 ON이 됐고 "열린 PR → In Review" 전이, Jira In Review와 To Do 복귀의 카드 반영, draft PR 제외, 본문이 바뀐 `blocked` 카드의 해제가 추가됐다. 스킬 본문은 257 토큰 줄었다. reference 모듈이 3개에서 5개가 되면서 `waza check`의 module-count 권고가 새로 뜬다

- **`nara-eli5-note`의 그림 HTML이 노트 안에 임베드되고 JS가 돈다.** `![[<파일>.html|-]]`로 쓰면 Embed HTML 플러그인이 sandbox 속성 없는 `srcdoc` iframe으로 렌더한다. 그동안 "HTML은 임베드 미지원, 파일 탐색기에서 클릭해 별도 탭으로 연다, 스크립트 차단이니 `<style>` + 순수 마크업만"으로 못박아 뒀던 제약이 전부 사실이 아니었다
  - 낡은 서술의 출처는 플러그인을 하나만 본 것이다. vault에 HTML Reader와 Embed HTML 둘이 깔려 있고 **역할이 갈린다.** `[[...]]` 링크는 HTML Reader가 별도 탭으로 열면서 스크립트를 막고, `![[...]]` 임베드는 Embed HTML이 iframe으로 렌더하면서 스크립트를 살린다. 같은 파일이 걸린 방식에 따라 다르게 동작한다
  - **임베드가 안 보인다고 불가능으로 읽지 않는다.** 첫 실측에서 빈 파일 카드로 떨어졌는데 원인은 플러그인이 설치만 되고 `community-plugins.json`에 없었던 것이다. 그래서 스킬이 노트에 "박스 대신 파일 카드만 보이면 Embed HTML 플러그인을 켠다"를 한 줄 넣게 했다. 새 머신·iOS에서 같은 증상이 난다
  - **높이 토큰 `|-`가 필수다.** 없으면 기본 높이에 걸려 긴 문서가 표 한가운데서 잘린다. `-`는 `height: fit-content`로 파싱되고 그때만 플러그인이 iframe 내부 `scrollHeight`를 재서 실제 높이로 늘린다. `800x2400`·`height:fit-content;width:100%` 문법도 같이 적어뒀다
  - HTML 절 번호를 노트 절 번호와 1:1로 맞추라는 규칙을 폐기했다. 두 창을 나란히 놓고 읽는 구도가 전제였고, 임베드는 노트 흐름 안에 들어간다
  - 남은 제약은 로컬 이미지 참조(`<img src="./...">`)뿐이다. 한 파일 self-contained는 그대로 두고 `<script>`를 허용 목록에 넣었다

- **`nara-eli5-note`가 eli5 톤일 때 이해도 확인 5문항을 붙인다.** 읽은 것과 이해한 것은 다르고 후자는 물어봐야 드러난다. **실무 노트체에는 넣지 않는다.** 이미 이해한 것을 나중에 찾으려고 남기는 기록이라 자기 자신에게 내는 문제가 노이즈다. 되묻지 않고 톤에서 판정하고, 요청이 있으면 그때만 예외다. 붙이는 자리는 폴더로 갈린다
  - **주제 노트** → 그림 HTML 마지막 절에 인라인 `<script>` 객체선다. 정답만 알리지 않고 **틀린 선택지를 눌렀을 때도 왜 틀렸는지** 한 줄 준다. 정답 여부만 주면 다시 읽을 자리를 못 찾는다
  - **커리큘럼 노트(`*-core/`)** → 노트 본문 `## 예측 문제` 절에 `**Q1.**` 형식. vault의 학습 앱(`_web/build.py` → `study.html`)이 이 형식을 카드로 만들고 localStorage 간격 반복으로 돌린다. 카드 id가 문항 내용 해시라서 순서를 바꿔도 이력이 유지된다. 이 절은 학습 앱과의 계약이므로 **톤과 무관하게 채운다.** 대신 **HTML 퀴즈는 만들지 않는다.** 중복이고 그 이력을 잃는다
  - 착안은 `geoffreylitt/explain-diff-html` gist다. 거기서 가져온 것은 퀴즈 절과 "중간 난이도, 함정 아님" 기준, 그리고 다이어그램 패밀리를 소수만 골라 반복하라는 지시다. **가져오지 않은 것**: 날짜 접두 파일명과 repo 밖 저장(vault frontmatter `created`가 이미 그 일을 한다), 문체 지정(대상 보정이 문체를 이미 결정한다), Background를 초보용·직결용 이중으로 쓰는 것(한 노트에 대상은 하나라는 규율과 충돌한다)
  - 같은 gist에서 **코드 블록 저장 전 점검**을 가져왔다. 커스텀 div에 `white-space: pre`나 `pre-wrap`이 없으면 브라우저가 줄바꿈을 전부 합친다
  - 패턴 8종에 **한 노트당 2~3종 상한**을 달았다. 여덟 개가 다 적혀 있으면 절마다 다른 형태를 고르게 되고, 그러면 독자가 절마다 읽는 법을 새로 배운다

- **fidelity가 배지에서 스위치가 됐다.** 상단 바에 `Styled | Wireframe` 분절 컨트롤이 생기고, `config.fidelity`는 "이 디자인이 무엇인가"가 아니라 "어디서 열리는가"가 된다. 첫 실행 투어 커밋에서 "빌드 타임에 정해지니 배지로만 보인다"고 정했던 것을 뒤집는다
  - 뒤집은 근거는 와이어프레임 패스가 실제로 하는 일이다. **같은 마크업 위에 스타일시트를 덮는다.** 섹션 순서도 인터랙션 타깃도 그대로다. 그러면 두 모습은 같은 디자인의 두 읽기이고 어느 쪽도 거짓이 아니다. 구조를 보고 다음에 스타일을 보는 것은 리뷰 한 번에 여러 번 일어난다
  - 배지가 맞게 짚었던 것은 남겼다. "Styled"는 디자인에 기대하는 기본값이라 컨트롤이 중립적인 두 선택지를 내놓는 대신 **어느 읽기가 켜져 있는지**를 말한다
  - **리터럴 색을 쓴다.** 바의 나머지는 팩 토큰을 쓰는데 여기만 예외다. 실제 팩에서 `--studio-accent`가 색으로 풀리지 않았고, 무효한 `var()`는 앞선 선언으로 되돌아가는 대신 속성을 `unset`으로 만든다. 그래서 흰 글자 + 안 칠해진 배경이 되어 선택된 칸이 사라졌다. 대비를 배경에만 걸지 않은 것도 같은 이유다 — 선택된 칸은 글자가 진해지고 굵어지므로 호스트 스타일시트가 배경을 이겨도 상태가 읽힌다
  - 컨테이너 반경을 알약에서 바의 버튼과 같은 값으로 내리고, 양 끝 칸이 바깥 모서리에서 그 반경을 반복한다. 알약 안의 각진 링은 곡률에서 잘려 렌더링 오류처럼 읽혔다
  - 쓰이지 않게 된 `.studio-fidelity` 규칙을 지웠다

- **PR 한 건이 카드 한 장을 쓴다. `nara-pr-activity-reminder`는 카드를 만들지 않는다.** 활동을 그 PR을 이미 들고 있는 카드에 코멘트로 적는다 — 내가 연 PR이면 jira-triage 작업 카드, 남이 연 PR이면 `리뷰 필요:` 판정 카드다. 둘 다 없으면 로그만 남기고 건너뛴다. `tracker_type=activity`라는 카드 종류가 사라진다
  - 판정 카드가 없다는 건 `nara-review-reminder`가 "이 PR은 내 리뷰 대상이 아니다"라고 이미 판단했다는 뜻이다. `cancelled`은 "무시하라"이고 그쪽 dedup은 상태를 안 보므로 재생성되지 않는다. 거기에 카드를 새로 만드는 건 그 판단을 손으로 뒤집는 것이었다
  - **활동의 정의도 누가 PR을 열었는지에 따라 갈린다.** 내 PR에서는 커밋이 내 것이라 알리면 내 push에 내가 알림을 받고(실제로 그랬다), 정작 중요한 "리뷰어가 처음 남긴 코멘트"는 아무에게도 답글이 아니라서 대댓글 필터에 안 걸린다. 그래서 내 PR은 커밋을 보지 않고 남이 단 인라인 코멘트 전부를 본다. 남의 PR은 그대로 대댓글 + 새 커밋이다
  - **실측: 열린 활동 카드 10장 전부가 중복이었다.** 8장은 같은 PR의 판정 카드와, 2장은 내 작업 카드와 겹쳤다. 마이그레이션은 하지 않는다 — 기존 카드는 PR이 머지될 때 닫히고, 그 사이에도 활동을 계속 받는다(전환용 폴백). 마지막 한 장이 닫히면 그 분기와 스위퍼를 지운다
  - 카드를 닫는 일도 그만뒀다. 작업 카드는 `jira-reconcile`이, 판정 카드는 `nara-review-reminder` reconcile이 각자 닫는다
  - 형제 카드 링크(`review_issue_key`)와 그 백필 패스는 릴리즈 전에 없앴다. 카드가 하나면 링크할 형제가 없다

- **판정 카드가 리뷰 요청부터 PR 머지까지 산다.** reconcile 종료 조건에서 "`reviews[].author.login`에 내가 있음"을 뺐다. 남는 건 PR `MERGED`/`CLOSED` → `done`, 팀 경유인데 팀원이 이미 리뷰 → `cancelled` 둘이다
  - 그 조건이 **하필 카드가 쓸모 있어지는 순간**이었다. 이 repo들은 `dismiss_stale_reviews=False`라 내가 approve한 뒤 저자가 push해도 승인이 유지되고 재요청도 안 간다. 대댓글과 새 커밋은 정확히 그 다음부터 오는데 카드는 이미 닫혀 있었다. 실측으로 열린 PR 6건이 판정 카드는 `done`인 채 활동만 쌓이고 있었다
  - 판정이 어디까지 갔는지는 상태가 아니라 `reviewed` · `review_state` · `reviewed_sha`가 말한다. 카드가 `done`으로 너무 일찍 닫혀 갚아야 할 리뷰 12건이 보드에서 사라졌던 직전 수정과 같은 방향으로 한 칸 더 간 것이다
  - 수명이 길어져도 중복 생성은 없다 — dedup은 `pr_url`만 보고 상태를 안 본다. 드레인도 안 끌려간다 — `nara-review-queue` 조건이 `status todo` + `reviewed != true`인데 판정 후엔 `reviewed=true`다

- **게시 코멘트 길이를 지적 수가 정한다.** `nara-pr-review`의 게시 계약(`references/posting.md`)에 분량 규칙을 넣었다. 서두와 맺음말을 쓰지 않고("리뷰 진행했습니다", "확인 부탁드립니다"), 지적 하나는 한 문장이 기본이며 근거가 필요하면 `파일:줄`을 붙여 두 문장까지다. 끝에서 다시 요약하지 않는다
  - 지적이 여섯 개를 넘으면 차단 항목을 먼저 다 쓰고 비차단은 중요한 것부터 다섯 개까지만 남긴다. 나머지는 "사소한 것 N건 생략"으로 한 줄 처리한다. 열 개를 나열하면 정작 고쳐야 할 줄이 묻힌다
  - 리뷰를 받는 쪽은 자기 코드를 이미 안다는 게 근거다. 배경 설명은 읽는 사람에게 새 정보가 아니다

- **큐 티켓 착수가 자동에서 `/drain` 코멘트 트리거로 바뀌었다.** 카드를 `in_progress`로 끌면 워커가 붙던 동작을 없앴다. 이제 카드에 `/drain`이라고 코멘트할 때만 돈다. 실행기는 그대로 codex다
  - 컬럼이 입력에서 출력으로 바뀌었다. `/drain`은 어느 status에서든 받고 스크립트가 카드를 `in_progress`로 옮긴다. 사람은 카드를 읽고 한 번만 입력한다
  - 드래그를 판별식으로 쓸 때는 `in_progress`에 카드를 넣는 주체가 셋인데 하나만 착수를 뜻하는 문제가 있었다. 사람 드래그는 착수, Jira 미러 두 경로는 "다른 데서 손으로 하는 중". 미러가 스스로 `drain_state=manual`을 찍어줘서 성립했던 가드다. 타이핑된 `/drain`은 미러가 만들 수 없으므로 마커 대신 트리거 자체가 의도를 담는다. `manual`은 이제 거부 근거로만 읽는다
  - **재작업도 같은 토큰이다.** 판정이 끝난 카드(`implemented`/`stopped`)에 `/drain`을 쓰면 기존 브랜치와 PR을 재사용하는 재착수로 분기한다. 사람이 외울 토큰은 하나다
  - 소비 기준은 코멘트 id다. 재요청은 새 `/drain`으로 한다. 이 덕에 재착수 실패가 매 폴링마다 같은 코멘트를 반복하던 동작도 없어졌다
  - 거부는 전부 이유를 카드에 남기고 트리거를 소비한다. 이미 워커가 붙은 카드, Jira가 In Progress라고 말하는 카드, repo 매핑이 없는 카드, 그리고 착수 대상이 아닌 리뷰 추적 카드까지
- **`nara-review-queue`의 제스처 계약 파일 이름이 `references/post-gesture.md` → `references/card-gestures.md`로 바뀌었다.** 게시 두 개만 다루던 문서가 `/ask`까지 세 제스처를 다루게 됐다. 이 파일을 참조하던 곳은 `nara-review-queue/SKILL.md`와 `nara-pr-review/references/posting.md` 둘이고 함께 갱신했다
- **리뷰 필요 카드 본문에 코멘트 명령 세 개를 적는다.** 제스처를 외운 사람만 쓸 수 있으면 아무도 안 쓴다. 판정 완료 코멘트에도 같은 목록이 붙는다. 이 변경 전에 만들어진 카드에는 없다
- **게시 본문이 리뷰한 모델을 밝히고, 차단성을 라벨 대신 문장으로 쓴다.** `차단:` `비차단:` 콜론 접두어는 보드에서 스캔용이지 남의 PR에서 사람이 읽는 문장이 아니었다. 이제 "Blocking 요소가 있습니다"로 열고, 비차단 지적은 뒤에 "Non-blocking 의견으로는 ..."으로 이어 붙인다. 지적을 빼지는 않는다. 표현만 바뀐 것이다
  - 모델 표기는 카드 metadata의 `review_model`을 먼저 보고 없으면 판정문 헤더를 본다. 둘 다 없으면 줄을 생략한다. 게시 세션 자신의 모델로 채우지 않는다. 게시는 리뷰를 돌린 세션이 아니라서 그 값을 적으면 얇은 판정이 무거운 모델의 판정처럼 보인다
  - 본문은 게시 직전 `nara-ko-prose`를 태운다. 스킬이 없으면 건너뛰고, 영어 repo에서는 애초에 돌리지 않는다

- `nara-code-review`에 판단 모델 선택을 도입 — 리뷰어·Judge·Fixer 3역이 `$JUDGMENT_MODEL` 하나를 공유하고, Verifier는 `sonnet` 고정. 세 역할은 열린 판단(무엇이 문제인가·유효한가·어떻게 고치는가)이라 모델 성능에 직접 좌우되지만, Verifier는 hash/hunk에 앵커된 확인 작업이라 같은 값을 치를 이유가 없다
  - 리뷰어 dispatch 직전 1회 질문(`opus` 기본 권장 | `fable`)으로 정하고 재리뷰 라운드에서 다시 묻지 않는다. `--model=opus|fable`로 질문을 건너뛴다
  - 미가용 시 **다른 모델로 대체하지 않는다** — `model`을 생략해 세션 모델을 상속하고 실제 사용 모델을 리포트 헤더에 기록한다. 조용한 강등이 리포트에 안 보이면 낮은 발견율을 모델 탓으로 돌릴 수 없다
  - 오케스트레이션 자체(Flow 0–3, 5, 9)는 세션 모델 고정이다. 스킬 안에서 자기 모델을 바꿀 수 없다. 같은 이유로 main 세션이 직접 Fixer로 뛰면 배정 모델을 지킬 수 없으므로, 세션 모델이 배정 모델보다 약하면 위임하도록 명시했다
  - Verifier의 3단계 중 **Resolved만은 관측 hunk만으로 결정되지 않는다**(`failure_path`가 더 이상 성립하지 않는지 판단해야 한다). 결정 불가일 때 Verifier 모델에서 판정하지 말고 그 항목만 리뷰어 모델로 재dispatch한다
  - override는 이 값을 재배정할 수 있다. 자원 노브이지 base check가 아니므로 Conflict rule 대상이 아니다

- `nara-release-watch` 2단계 분리 — **watch**(매일, 판정 없음)와 **digest**(사람 트리거, 증류 판정). 임계(`@minor`)가 알림과 판정을 동시에 죽여서 릴리즈 잦은 repo(stablyai/orca: minor 고정 + 일간 패치)를 감시할 수 없던 것이 동기
  - watch는 새 릴리즈를 `highlights[]`(기계 필터: fix/chore 등 conventional prefix, "Notable changes" 마케팅 섹션, first-contribution 보일러플레이트 제거 — orca 실측 주간 617줄 중 8할이 fix)와 함께 판정 없이 알리고 큐(`~/.claude/release-watch-queue.json`)에 적재한다
  - digest는 큐 누적분(여러 repo)을 한꺼번에 4분류 판정한다 — 누적이라 교차 repo 패턴 판정이 가능해졌다. 읽기와 드레인(`digest --drain`)을 분리해 판정·배달 실패 시 백로그를 잃지 않는다
  - 두 단계를 별도 autopilot으로 등록한다 (watch 매일 08:47 KST, digest 매주 월 09:23 KST). 에이전트도 분리했다 — watch 에이전트의 지시문이 "판정하지 말 것"이라 한 에이전트가 두 단계를 겸하면 그 계약이 흐려진다. 잡은 둘이지만 watchlist·폴러·큐를 공유하는 한 파이프라인이다
  - 단계 계약을 데이터로 강제한다: `poll` 출력에 `"stage": "watch"` / `"judgment": "forbidden"`, `digest` 출력에 `"digest"` / `"required"`. receipt 첫 줄에도 stage를 쓰게 해 판정이 섞이면 자기 모순이 드러나게 했다. 스킬이 증류 루브릭을 함께 싣고 있어 산문 금지만으로는 watch 알림이 판정으로 흐른다
  - suppressed는 큐에 들어가지 않는다 — digest는 "알린 것 중에서" 판정한다. 테스트 59 → 74건

- `evals/`를 추적 대상으로 전환 — 이전에는 `evals/*` ignore + 3개 스위트만 allowlist였다. 추적하지 않으면 **스킬 성능을 측정할 수 없고**, 측정하지 않는 스위트는 채점 대상 스킬에 대해 조용히 썩는다. 45개 스위트 / 205개 파일이 추적된다. `evals/**/results/`(실행 산출물)는 계속 ignore
  - allowlist가 막아주던 것은 실재하는 위험이었다. 전환 전 스캔에서 **5개 스위트에 사내 식별자 61건**이 나왔다 — Jira 프로젝트 키, 내부 repo명, `git.linecorp.com` 호스트, 조직명, 그리고 **Slack 채널 ID와 실제 메시지 타임스탬프**. 공개 repo에 사내 식별자가 올라가 history rewrite까지 갔던 전례가 있어 전환 **전에** 정화했다
  - 치환은 placeholder로: `PROJ`/`OPS`(티켓 키), `web-ui`/`api-server`(repo), `git.example.com`, `acme-sre`, `C0123456789`, Slack ts 무력화. `lyris-{fe,be}-classify.yaml`은 파일명까지 개명. **태스크가 검증하는 구분은 보존** — jira-triage 스위트가 FE→BE 라우팅을 채점하므로 두 placeholder repo명이 서로 반대편에 남아야 한다 (`output_not_contains` 대칭 유지 확인)
  - CLAUDE.md에 **eval 식별자 스캔 게이트** 추가 — `evals/`를 건드리는 커밋을 막는다. allowlist를 없앤 대신 스캔이 그 자리를 대신한다
  - 측정 공백 확인: eval이 없는 스킬 7개 (`eli5-note`, `local-shot`, `review-queue`, `review-reminder`, `spec-revision`, `trending-digest`, `wt`). 이번 전환의 목적이 측정이므로 기록해 둔다

- `nara-worklog`가 **사람 시간과 agent 시간을 가른다.** 모든 이벤트에 `role`이 붙고 Jira worklog에는 `role: human`만 올라간다. dispatch된 codex 워커는 티켓 이름이 붙은 브랜치에서 돌아 사람과 똑같은 이벤트를 만들기 때문에, 구분이 없으면 무인 실행 한 시간이 팀 스프린트 리포트에 내 시간으로 들어간다
  - **역할 필터는 그룹화 전에 적용된다.** 나중에 걸러내면 워커의 턴이 사람의 유휴 간격을 메워 두 개의 별개 접속이 한 span으로 붙는다. 사람 10분 + agent 1시간 + 사람 10분이 `20m`이어야 하고 `2h 15m`이면 안 된다는 것을 테스트로 고정했다
  - `agent_seconds`/`agent_time_spent`로 따로 보고한다. 청구액이 아니라 자동화가 얼마나 걷어갔는지의 지표이고 `total_seconds`에 합산하지 않는다
  - 판별은 `NARA_WORKLOG_ROLE`(dispatcher가 워커에 심는다)이 1차, `~/orca/workspaces` 경로가 백스톱이다. 오타 같은 미지의 값은 `human`으로 떨어진다 — 인식 못 하는 역할을 만들면 사람 집계와 agent 집계 양쪽에서 사라진다
  - role 없는 기존 이벤트는 `human`으로 읽는다. ledger는 append-only이므로 과거 기록이 계속 세어져야 한다
- `nara-worklog` hook이 **harness에 의존하지 않는다.** 이벤트 이름을 `--event`로 받고 stdin 페이로드는 폴백이다. Claude Code와 Codex 둘 다 `UserPromptSubmit`/`Stop`을 노출하지만 두 페이로드 스키마가 계속 같다는 데 시계를 걸지 않는다 — 한쪽이 키를 바꾸면 조용히 멈춘다. Codex 배선 절차는 `references/hook-setup.md`에 추가
  - **손으로 JSON을 편집하다 두 번 틀렸다.** `UserPromptSubmit` 대신 `PostToolUse`에 넣어 턴 경계가 무의미해졌고(도구 호출마다 발동), 닫는 괄호를 빠뜨려 `~/.codex/hooks.json` 전체가 파싱 불가가 됐다. 후자는 worklog만 죽는 게 아니라 그 파일의 **모든** hook이 함께 죽는다. 문서는 이제 파서를 거치는 스크립트를 제시한다
  - **`-> str | None`을 추가했다가 3.9 폴백을 깨뜨렸다.** `TypeError`로 `exit=1`이고, 폴백이 발동하는 머신에서는 그게 모든 턴 차단이다. 첫 줄의 `from __future__ import annotations`가 그 방어이고, 문서에 실측 검증 한 줄을 넣었다
  - 테스트 69 → **78건**. role 3건(청구 제외·유휴 간격 비브리지·필드 없음=human)과 argv 이벤트 5건
- `nara-worklog` idle 임계 기본값 **30 → 90분**. 실측 하루에서 30분은 62분짜리 기획 검수 유휴와 55분 유휴를 청구에서 잘라냈다 — 생각·검수 시간도 작업 시간이라는 판단
  - "세션 시작~종료"를 그대로 쓰는 안은 실측으로 기각했다: 같은 ledger가 2h43m(30분 모델) vs **15h38m**(세션 모델)으로 갈렸고, 세션 하나가 18:34에 시작해 다음날 08:11까지 열려 있어 **707분 수면 구간이 청구**됐다. 문제는 세션 경계가 아니라 임계값이었다
  - 90분은 62·55·35분 유휴를 살리고 707분은 버리는 지점. 같은 날 값이 2h43m → 4h15m

- `nara-release-watch` 경로 감시 모드 — watchlist 항목을 `owner/repo:some/dir`로 쓰면 릴리즈가 아니라 **그 경로를 건드린 커밋**을 본다. repo 릴리즈가 특정 디렉터리의 변경을 대변하지 못할 때 필요하다
  - 실측 동기: `mattpocock/skills`는 릴리즈가 2026-08-06에 멈췄는데 `skills/productivity/grill-me`는 2026-08-15에 바뀌었고 repo 전체는 계속 활발했다. 릴리즈로 감시하면 그 변경을 영구히 못 보고, repo 전체 커밋으로 감시하면 하루 여러 건이라 노이즈다. 해당 경로 커밋은 2026-04 이후 6건 — 감시 대상으로 적정
  - state가 `repo` vs `repo:path`로 분리되므로 같은 repo를 repo 레벨과 여러 경로로 동시에 감시해도 충돌하지 않는다. watermark 단위는 태그 대신 커밋 SHA
  - `@minor`/`@major`와 prerelease 필터는 SHA에 무의미해 실질적으로 무시된다 — 16진수 SHA에는 prerelease 키워드가 나올 수 없다(모든 키워드가 비-16진수 문자를 포함). 특수 분기 없이 안전함을 테스트로 고정
  - 경로에 커밋이 0건이면 `unwatchable`로 1회 보고(거의 항상 오타), `..`가 든 경로는 파싱 단계에서 폐기
  - 판정 루브릭은 두 모드에 동일 적용 — 스킬 diff는 그 자체로 "증류할 게 있나"라는 질문이다

- `nara-release-watch` 신설 — watchlist repo의 신규 릴리즈를 폴링해 nara-kit에 증류할 값이 있는 것만 판정·보고한다. `nara-trending-digest`와 짝이지만 다른 일이다: trending은 **모르는 repo 발견**, 이건 **아는 repo 추적**. 배달 경로(Slack DM + Obsidian)만 공유
  - **2층 구조가 설계의 핵심.** "새 릴리즈 있나"는 GitHub API 한 방(LLM 0), "증류할 만한가"는 스킬 표면을 알아야 하는 판단이다. 분리하면 신규 0건인 날 모델을 아예 안 깨운다 — 기존 autopilot이 Claude 풀 절반을 쓰고 있어 실질적인 절약
  - **조용한 날엔 아무것도 보내지 않는다.** AI 툴링 repo 릴리즈는 버스티해서, 매일 "없음"을 보내면 6일치 무소식이 7일째 진짜 소식을 덮는다. 폴링은 매일, 알림은 있을 때만. 예외는 `needs_attention` — `gh` 인증 실패는 조용한 날과 구별이 안 되므로 조용함으로 접지 않고 매 실행 보고한다 (이게 없으면 토큰 만료 후 영구히 "평온"해 보인다)
  - 노이즈 통제는 실측으로 정했다. `openai/codex`가 `rust-v0.153.0-alpha.5`를 플래그 없는 정식 릴리즈로 올려서 **prerelease를 태그 문자열로도 판정**하고, `anthropics/claude-code`가 `v2.1.258`(패치 거의 매일)이라 watchlist 항목별 **`@minor`/`@major` 임계**를 뒀다. 억제된 릴리즈도 `last_seen`은 전진시킨다 — 안 그러면 같은 패치를 매 실행 재평가하고 수렴하지 않는다. 첫 관측은 baseline만 기록하고 침묵(첫날 히스토리를 쏟으면 쓸모 있는 말을 하기 전에 무시당한다). 버전을 파싱 못 하면 억제하지 않는다
  - 릴리즈·태그가 둘 다 없는 repo는 `unwatchable`로 **1회 보고 후 억제** — 조용히 감시하는 척 하지 않되 매일 조르지도 않는다 (실제로 `browserbase/skills`가 이 경로로 걸렸다)
  - 판정 루브릭 4분류(`이미 있음`/`의존`/`증류 후보`/`무시`)의 **기본값은 `의존`**. 이 잡은 구조상 흡수 루프라서 기본값이 `증류 후보`면 매일 "우리도 만들자" 후보만 쌓인다 — vendor-free는 배포 산출물 속성이고 nativize는 이식이 싸고 테제가 날카로울 때만. `이미 있음`은 겹치는 **스킬 이름을 대야** 쓸 수 있다 (인상으로 릴리즈를 버리면 진짜 새로운 것을 놓친다)
  - config는 `~/.claude/release-watch.md`(사람, 마크다운 산문 허용) + `~/.claude/release-watch-state.json`(기계, 원자적 재작성) 분리. 상태가 매번 덮어써지므로 사람이 편집하는 목록과 같은 파일에 둘 수 없다. 목록은 `watch.py seed`가 스타에서 후보만 제시하고 **자동 추가하지 않는다** — 스타는 다른 이유로도 누르니 노이즈다

- `nara-worklog` 신설 — 세션 타임스탬프를 날짜별 Jira worklog로 올린다. **수집(hook)과 쓰기(스킬)를 분리한 것이 설계의 핵심**: 시작 시각은 "기록해야 한다는 걸 알기 전"에 지나가므로 LLM 선언으로는 안 지켜지고(hook이 필요), 반대로 팀이 읽는 티켓에 확인 없이 숫자가 올라가면 안 되며 hook은 shell이라 MCP를 못 쓴다(스킬이 필요)
  - 수집: `assets/nara-worklog-stamp.py`를 `UserPromptSubmit` + `Stop`에 배선. 브랜치명의 `ABC-123`으로 티켓을 판정하고 `~/.claude/worklog/<TICKET>.jsonl`에 append. 티켓 키 없는 브랜치는 skip. stdout 무출력·항상 exit 0 계약 — `UserPromptSubmit` hook의 stdout은 모델 컨텍스트로 주입되고 non-zero는 턴을 막는다. 설치는 일회성 수동 작업 ([references/hook-setup.md](skills/nara-worklog/references/hook-setup.md)) — `~/.claude/hooks/`와 `settings.json`은 배포 대상이 아니다
  - 산정: `assets/worklog.py`(표준 라이브러리만)가 소유한다. LLM이 시각을 더하면 같은 ledger에서 매번 다른 숫자가 나오고 그 숫자는 스프린트 리포트에 들어간다. `prompt → turn_end` 구간은 길어도 자르지 않고(에이전트 실행 = 작업 시간), `turn_end → prompt`(자리 비움)와 `turn_end` 없는 `prompt → prompt`(턴 중간에 죽은 세션)만 idle 임계 30분으로 자른다. 자정 분할로 날짜별 1건 — 여러 날 걸린 티켓이 PR 날짜에 뭉치지 않는다. 한 티켓 워크트리 여러 개는 합집합 병합(세션별 합산이면 중복 계상). 분 단위 **내림** — 안 쓴 1분을 청구하지 않고, 정확히 30초일 때 banker's rounding도 피한다
  - 멱등성: `jira_add_worklog`가 멱등이 아니라서 ledger의 `logged` watermark가 유일한 중복 방지 장치다. 날짜 오름차순으로 쓰고 중간 실패 시 **성공한 날짜까지만** watermark를 올려 실패한 날이 다시 제안되게 한다. Jira 쓰기 0건이면 record하지 않는다
  - `nara-pr` 스텝 8 추가 — PR 생성 후 미기록 시간을 한 줄 알리기만 한다. 쓰기는 승인 게이트가 있는 `nara-worklog` 소관 (스크립트 없으면 스킵)

- `nara-eli5-note` 편입 — 로컬 전용 스킬(`~/.agents/skills`, 2026-08-24 신설)을 nara-kit으로 올림. 실무에서 막힌 것을 eli5 또는 실무 노트체로 풀어 Obsidian vault 관례(폴더 두 계열·frontmatter·노트 골격)에 맞춰 저장하고, 그림을 필수로 동반한다
  - **그림 매체는 HTML/SVG — ASCII 아트·mermaid 금지** (2026-08-26 유저 결정. 노트는 글, 그림은 렌더되는 파일). 그림 3개 이상·연결된 설명이면 노트 옆 `<slug>-그림.html`(HTML 뷰어 플러그인으로 열고, 절 번호를 노트와 1:1로 맞춤), 독립 그림 1~2개면 `_assets/` SVG 인라인 임베드
  - `references/diagram-patterns.md`가 패턴 8종의 판정 기준(before/after·생애주기·층 구조·트리·비율·대조·비유·상태 지도)을 매체 무관으로 유지하고, HTML 스타일 베이스 CSS + 의미 고정 색 팔레트(초록=해결·빨강=문제·파랑=강조·노랑=보류)를 제공 — 노트마다 그림 스타일을 재발명하지 않는다
  - 규율: 톤(eli5 vs 실무 노트체)을 추측하지 않고 묻는다 · `TL;DR`·`내가 틀렸던 것` 절 필수 · 비유는 하나만 · 개념어는 실제 식별자(필드명·파일명)와 1:1 대응
  - `references/vault-conventions.md`는 설치자 vault 실측 스냅샷 — 포크 시 자기 vault에 맞게 갱신해서 쓴다

### Fixed

- **`nara-jira-triage`가 남의 subtask를 내 큐에 넣었다.** subtask 게이트가 "컨테이너는 빼고 ready 상태인 subtask를 대신 큐에 넣는다"로 읽혔는데, parent의 `subtasks` 필드에는 assignee가 없다. 내가 담당인 RfC 하나가 걸리자 다른 사람이 담당인 하위 작업 8건이 한 번에 큐 카드가 됐다. 이제 큐 대상은 poll 결과에 자기 행으로 온 티켓뿐이다. poll이 `assignee = currentUser()`라서 내 subtask는 어차피 따로 오고, `subtasks` 필드는 컨테이너 판정에만 쓴다. 추가 조회는 없다
- **같은 일을 하는 실행기가 둘이었다.** `nara-pr-activity-reminder`의 로직이 결정론이라 크론 스크립트로 옮겼는데(`SKILL.md`가 "LLM 오토파일럿이 아니라 셸 크론이 정석"이라고 못 박은 그 변경) **Multica 오토파일럿을 안 껐다.** 6주간 매시간 둘이 같이 돌았고, 스크립트에만 있던 author 가드가 오토파일럿에는 없어서 오토파일럿 쪽이 내가 연 PR에도 추적 카드를 만들었다. 결정론 로직을 매시간 LLM으로 돌리느라 구독 풀도 같이 태웠다. 오토파일럿을 정지했고, 스킬 본문에 "동시에 돌리지 말 것"을 명시했다
- **판정 카드가 아침 브리핑에서 안 보였다.** `multica-brief.py`의 "남의 PR 리뷰 대기" 버킷이 `todo`/`in_progress`만 담는데, 판정 카드의 판정 후 기본 상태는 `in_review`("판정 났고 게시는 사람 차례")다. 즉 **할 일이 남은 카드만 정확히 골라서 빠뜨렸다** — 실측으로 보드에 열려 있던 판정 카드 한 장이 브리핑에 없었다. 이제 브리핑이 훑는 모든 상태를 담는다. 판정 카드가 머지까지 살면서 활동을 받게 된 지금은 `in_review`가 그 카드가 대부분을 보내는 자리다
- **에이전트 판정이 카드를 `done`으로 닫아서 사람이 갚아야 할 리뷰가 보드에서 사라졌다.** 파이프라인은 설계상 PR에 아무것도 게시하지 않으므로, 판정이 나와도 GitHub 기준으로는 리뷰를 안 남긴 리뷰어 그대로다. 그런데 `reviewed=true` + `done`으로 카드를 닫았고, dedup이 `reviewed`를 보므로 리마인더가 다시 만들지도 않는다. **실측: 열린 PR 12건이 내 리뷰가 하나도 안 나간 상태로 카드 없이 남아 있었다.** 활동 추적 카드만 열려 있어서 그걸 보고 리뷰해야 하는 건지 헷갈리는 게 정상이었다
  - `nara-review-reminder`의 reconcile 계약은 카드를 닫는 조건을 둘로 못 박아 뒀다. PR이 `MERGED`/`CLOSED`거나 `reviews[].author.login`에 내가 있을 때. 디스패처가 계약에 없는 세 번째 조건을 만들어 쓰고 있었다. (그 둘째 조건도 같은 이유로 결국 없앴다 — 위 Changed의 "판정 카드가 리뷰 요청부터 PR 머지까지 산다")
  - 판정 후 status를 `in_review`로 바꿨다. 뜻은 "판정 나왔고 게시는 사람 차례". 닫는 권한은 reconcile에만 남는다. `reviewed=true`는 중복 카드 방지용으로 유지하되 종료 의미를 뺐다
  - `nara-review-queue`의 `--done-status` 기본값을 `in_review`로. 플래그 이름은 하위호환으로 유지
  - 이미 닫힌 19건 백필: PR이 열려 있고 내 리뷰가 없는 15건을 `in_review`로 되살렸다. 머지된 4건은 그대로 `done`
- **`pr-activity-reminder`의 열린 카드 조회도 창에 잘렸다.** 아래 dedup 결함과 같은 것인데 이 파일만 남아 있었다. `issue list --limit 100`을 통째로 받아 클라이언트에서 걸렀고, 정렬이 보드 position이라 done/cancelled가 창을 채운다(`has_more: true` 실측). 밀려난 추적 카드는 안 보이므로 **같은 PR에 활동 카드가 중복 생성**되고 머지된 PR이 안 닫힌다. 상태별 조회로 교체 — 열린 컬럼만 보면 창에 안 걸린다(실측 30건). `--metadata tracker_type=activity`로 좁히지 않은 이유는 고아 카드 복구가 **metadata가 빈** 행을 찾아야 해서다

- **자동 PR 리뷰가 엔터프라이즈 호스트를 못 찾았고, 회복한 뒤에도 판정이 카드에 오르지 못했다.** `nara-pr-review` 1단계는 "체크아웃 없이 `gh --repo` 기준"이라고만 적혀 있어 호스트를 도출하라는 지시가 없었다. `gh`에 github.com과 엔터프라이즈 호스트가 둘 다 로그인돼 있으면 기본 호스트는 github.com이므로, `GH_HOST` 없는 `--repo <owner/repo>`는 diff를 한 줄도 받지 못한 채 `Could not resolve to a Repository`로 죽는다. PR URL의 hostname을 `GH_HOST`로 export하는 것을 1단계 계약으로 올리고, 실패 증상과 이유는 `references/pr-plane.md`로 내렸다. 그쪽에 있던 "GHES면 `GH_HOST` 설정 확인"은 환경 점검으로 읽혀서 도출 규칙 역할을 하지 못했다
  - 실행 측(`multica-dispatch.py`, git 밖 `dotfiles/ops`) 결함 2건을 같이 고쳤다. 스크립트는 자기 `gh` 호출에는 `GH_HOST`를 넘기면서 리뷰어 프롬프트에는 호스트를 넘기지 않았다. 이제 PR URL에서 도출해 리터럴로 박는다 (스크립트가 이미 아는 결정값이라 워커 추론에 맡길 이유가 없다)
  - 그리고 `blocked`가 종착 상태로 굳었다. 수집 루프가 `dispatched`만 보고 착수 루프는 state가 있는 카드를 건너뛰므로, 첫 `gh` 호출에 실패한 리뷰어가 스스로 회복해 결과 파일을 다시 써도 판정이 워크트리에 갇힌다. 실측 사례에서 16분 뒤 `changes_requested`가 쓰였는데 아무것도 걷어가지 않아 사람이 손으로 카드에 옮겼다. 이제 `blocked`도 계속 폴링하고, 상태가 실제 판정으로 바뀌면 정상 수집한다. 여전히 `blocked`인 동안은 재코멘트하지 않는다
- **dedup이 조회 창을 넘겨 이미 처리한 것을 다시 만들었다.** `nara-review-reminder`와 `nara-jira-triage` 모두 `multica issue list`를 통째로 훑어 비교했는데, 그 호출은 100건에서 잘린다(`has_more: true`). done/cancelled가 목록을 지배하므로 워크스페이스가 100건을 넘은 시점(2026-09-04 실측)부터 오래된 이슈가 창 밖으로 밀리고, **내가 취소해둔 PR에 리마인더가 다시 생기고 이미 큐잉한 티켓이 다시 큐에 들어간다.** 서버측 metadata 필터(`--metadata "pr_url=..."` / `"jira_key=..."`)로 교체 — 서버가 걸러 창과 무관하다
  - 같은 결함이 `jira-reconcile.sh`에도 있었다(git 밖, `dotfiles/ops`). 그쪽은 열린 이슈만 필요하므로 `OPEN_STATUSES`별로 조회해 합치도록 고쳤다. 고친 직후 조회 결과에 `LYRIS-425`가 새로 나타났다 — 실제로 밀려 있었다는 증거다
  - review-reminder에 **리뷰가 불필요한 PR을 무시하는 방법**을 명시했다: 카드를 `cancelled`로 옮긴다. dedup이 상태를 보지 않으므로 재생성되지 않는다. `done`은 "내가 리뷰했다"는 뜻으로 reconcile이 쓰므로 구분한다
- `nara-pr-activity-reminder`가 **`main`에 없었다** — `multica-agent` 브랜치에만 존재하고 머지된 적이 없어, `main`이 곧 릴리즈인 이 repo에서 소비자에게 배포되지 않았다. 실행 주체(`~/.local/bin/pr-activity-reminder.py`)는 git 밖이라 동작에는 영향이 없었고, 없어진 것은 계약 문서와 배포였다. 그 브랜치는 `main`보다 39커밋 뒤처져 통째 머지하면 `evals/` 전체가 삭제로 들어가므로 스킬 디렉터리만 꺼내왔다
- 스킬 카운트가 49에 멈춰 있었다 — 실제 54개(`nara-` 53 + `naranizer`). 스킬을 추가할 때 `README.md`·`CLAUDE.md`·`skills/README.md` 카운트 갱신이 반복적으로 빠진다
- 8-리뷰어 코드 리뷰 반영 — `nara-worklog`·`nara-release-watch`·`eval-fixture` 신규 Python 933 LOC 대상. raw 51건 → R0/R1 21건 적용, R2/R3 17건 이월. 리포트: `docs/review/260902-worklog-release-watch-eval-fixture.md`
  - **`fetch_versions`가 gh 실패를 "버전 없음"으로 오분류했다.** 판정이 `releases is None and tags is None`이라, 태그만 쓰는 repo(releases가 정상적으로 `[]`)에서 tags 호출만 실패하면 `unwatchable`로 낙인하고 `unwatchable_reported`를 영구 기록해 **그 repo가 영원히 조용해졌다**. 단계별 조기 반환으로 교체 — 부수적으로 실패 확정 후 두 번째 호출을 하지 않으므로 전 repo 실패 시 왕복이 절반이 된다
  - **`PRERELEASE_RE`에 단어 경계가 없어 정식 릴리즈가 사라졌다.** `v1.0.0-aarch64`(a**rc**h64), `-source`(sou**rc**e), `-devtools`, `-nextgen`이 prerelease로 오탐. 구분자 앵커(`(?:^|[-._+])`)로 교체하고 안정 태그 부정 케이스 6종을 테스트로 고정
  - **`--through`에 offset 없는 값이 들어가면 ledger가 영구 오염됐다.** naive watermark가 hook의 aware `ts`와 비교되며 `TypeError`를 내고, `list`는 디렉터리 전체를 훑으므로 **오염된 티켓 1개가 모든 티켓 조회를 죽였다.** `cmd_record`가 거부(exit 1, ledger 무변경)하고 `watermark()`는 디스크에 이미 있는 값을 승격한다
  - `gh_json`이 `OSError`·`SubprocessError`를 잡는다 — docstring이 "any failure"를 주장했지만 gh 미설치·hang은 예외를 전파해 repo 1개가 poll 전체를 죽였다
  - `argparse` 플래그를 서브커맨드 양쪽에서 사용 가능하게. **리뷰 중 자체 발견**: `parents=[common]`의 서브파서 default가 루트 파싱값을 clobber해서 `--state X list`가 X를 무시하고 **실제 state 파일**을 읽었다 — 원래 문제보다 나쁜 회귀였다. `argparse.SUPPRESS` + `apply_defaults()`로 해소
  - `total_seconds`를 날짜별 **내림값의 합**으로. Jira는 날짜당 1회 쓰이므로 raw 초 합계는 날짜별로 버린 잔여를 되살려 실제 게시량보다 크게 보고했다(하루 최대 59초 × 날짜 수). `unpostable_days` 필드 추가
  - hook의 `os.makedirs`를 티켓 매칭 판정 **앞으로** — 배선이 정상인데 디렉터리가 없어서 스킬이 "hook 미설치"로 오판하고 **거짓 재설치 루프**를 유발했다
  - `save_state`가 `abspath`로 정규화(bare 상대 파일명에서 `os.makedirs("")` 크래시), watchlist 후행 주석 분리를 `\s+--\s`로 제한(`some/repo--name` 절단), `MIN_POSTABLE_SECONDS` 상수화(임계 드리프트)
  - `eval-fixture.py`: `find("{")`의 -1을 슬라이스에 그대로 써서 `[-1:]`이 마지막 한 글자가 되어 의도한 진단 에러가 발화하지 않던 것, probe stale 재사용으로 거짓 green이 나던 것, 채점 0건에 성공을 반환하던 공허 통과, provenance 필드를 그레이더가 읽는다는 거짓 주석
  - 테스트 46 → **93건**. 변이 테스트가 드러낸 무보호 지점을 고정했다 — API `prerelease` 플래그 단독 케이스(`rel(prerelease=True)` 호출이 0건이었다), `jira_started` **배선**(함수 단위 테스트만 있어 상수 치환에도 통과했다), `fetch_versions`/`gh_json`(테스트 참조 0건). `test_stamp.py` 신설 14건 — 69 LOC 훅이 모든 세션의 모든 턴에서 도는데 테스트가 없었다. `run()` 헬퍼가 `--gap-minutes`를 명시 전달해 환경 의존 거짓 실패(`NARA_WORKLOG_GAP_MINUTES=10`에서 5건 실패)를 제거
  - **hook 인터프리터 배선 수정** (PRF-001, 이월 예정이었으나 즉시 적용) — bare `python3`가 pyenv shim으로 해석돼 순수 오버헤드를 지불했다. 실측 **438.8ms → 55.1ms**(8배), 턴당 2회 발동이므로 약 0.77초 절감. `nara-review-gate.py`도 같은 배선이었고 PreToolUse라 **모든 Bash 호출마다** 발생했다
    - 버전을 고정하지 않는 폴백 체인을 쓴다: `for P in /opt/homebrew/bin/python3 /usr/bin/python3; do [ -x "$P" ] && exec "$P" <hook>; done; exit 0`. pyenv 버전 경로가 제일 빠르지만(18.8ms) 업그레이드로 사라지면 exec 실패로 **모든 턴이 막힌다**. `exec`가 종료 코드를 보존하므로 exit 2 차단이 유지되고, `; exit 0`이 두 경로 부재 시 fail-open을 보장한다(그것 없이는 마지막 `[ -x ]` 실패가 exit 1이 된다) — 셋 다 실측 확인
    - 두 hook 모두 3.9에서 컴파일되므로 `/usr/bin/python3`(3.9.6) 폴백이 유효하다. 이 파일에 3.10+ 문법을 쓰면 폴백이 깨진다

- **eval 점수가 측정처럼 보이는 가짜였던 것을 막았다.** `waza run nara-gap`이 `4 passed / 4 failed`를 내놓고 있었는데, executor가 `mock`이라 스킬이 호출되지 않는다(`tool_call_count: 0`). mock의 출력은 `프롬프트 + 태스크명 + description + 픽스처 원문`을 그대로 이어붙인 것이라, 통과한 4건은 **단정 문자열이 자기 description에 이미 적혀 있어서** 통과한 동어반복이었다 — `Score`는 description의 `"produces docs/gap.md with a score (0-100)"`에 대소문자 무시로 매칭됐다
  - 원인은 2026-08-26 `f4dd7ac`의 `real_run` 그레이더 제거다. 사유("mock에서 절대 통과 못 하는 단정은 게이트가 아니다")는 **행동 게이트로는 맞고 출처(provenance) 게이트로는 틀렸다**. 제거 전엔 항상 0/8로 시끄럽게 고장났고, 제거 후엔 4/8로 조용히 그럴듯해졌다 — 나쁜 쪽으로 바뀐 거래다
  - `real_run`(`len(output) > 40`, `'Mock response for:' not in output`)을 **45개 스위트 전체**에 출처 게이트로 복원했다. mock 실행은 이제 8/8 실패하며 이유를 명시한다. 판별력은 그대로 — RIGHT 8/8 통과 / WRONG 0/8 통과 확인
  - CLAUDE.md의 실행 방법이 **없는 명령**(`waza eval <skill>`)이었다. 실제는 `waza run`이고, 어느 경로가 무엇을 재는지(정적 `check`·구조적 `coverage`·행동 `grade`) 표로 명시했다
- `tools/eval-fixture.py` 추가 — 그레이더 판별력 검증을 `validate <skill>` 한 명령으로. 2026-08-24에 만들어졌지만 **untracked `results/`에 방치돼 유실 직전이던** `make-validation.py`를 일반화한 것이다. 테이블은 `evals/<skill>/validation.yaml`로 이관해 추적한다(`right`/`wrong`, task id 키). `wrong`은 **실제 관측된 실패**를 재현해야 한다 — 지어낸 실패는 판별이 너무 쉬워서 아무것도 증명하지 못한다
  - 이관 과정에서 테이블이 픽스처와 어긋난 것도 잡혔다: `iris-api@a1b2c3d`(정화 전 사내 repo명)를 픽스처의 placeholder `billing-api@a1b2c3d`로 맞췄다. 식별자 게이트가 잡아준 건이다
  - executor 블로커는 그대로다 — `copilot-sdk`는 seat 미할당, `mock`은 스킬을 호출하지 않는다. 즉 지금 측정 가능한 것은 **그레이더의 판별력**이고 스킬 행동은 실제 실행 경로가 뚫려야 한다

## [0.22.0] - 2026-08-26

### Added

- `nara-ko-prose` 신설 — 공유 산출물(PR 본문·RFC·ADR·한국어 Confluence 본문)의 한국어 명확성 수리. 생략된 조사·어미·문장 성분을 되돌리고, 명사구로 끊긴 문장을 종결어미로 맺고, 엠대시를 치환한다
  - 규칙 출처는 [snflkd/fluent-korean](https://github.com/snflkd/fluent-korean) (MIT). **사본을 배포하지 않고** 설치된 원문을 실행 시점에 읽는다 — 원문 `## 상황과 목표` 절이 지침의 요약을 권장하지 않으므로 축약본도 두지 않으며, 원문 미발견 시 `Unverifiable`로 종료한다. nara-kit이 저작한 것은 호출 계약과 조항별 모드 배정뿐
  - 모드 2종. `repair`(기본, 산출물 스킬 post-pass 경로)는 결함 교정만 하고, `full`(사용자 직접 호출)은 전 조항을 적용한다. `repair`가 부분집합인 이유는 분량이 아니라 **`naranizer`와의 공존** — 원문 동작 범위 4항(사용자 어조 모방 금지)을 PR 본문에 적용하면 개인 말투 변환이 통째로 취소된다
  - `nara-humanizer`와 방향이 반대다. humanizer는 AI 마커를 **덜어내고**(쉼표 과다·유행어·번역투), ko-prose는 압축이 만든 결핍을 **채운다**. 한자어에서 정면으로 어긋나므로(humanizer는 "한자어 과다"를 검출, 원문 구 단위 2항은 적극 활용을 요구) `repair`는 그 조항을 적용하지 않는다
  - 적용 제외: 커밋 메시지·변수명·코드 주석·로그 문자열(원문 동작 범위 2항), 헤더·목록의 종결어미 요구(원문 문장 단위 2항이 스스로 제외), 코드 블록·인용, 영어 텍스트

### Changed

- `nara-pr`: Step 6에 `nara-ko-prose` repair post-pass 추가 (naranizer **다음**에 실행 — 어휘·말투를 건드리지 않아 앞 단계를 되돌리지 않는다). 기존 Step 6 → 7
- `nara-rfc`: Step 5에 `nara-ko-prose` repair post-pass 추가. 기존 Step 5 → 6
- `nara-adr`: Workflow Step 4에 `nara-ko-prose` repair post-pass 추가. 기존 Step 4 → 5
- `nara-publish-spec`: Language 규칙에 조건부 `nara-ko-prose` repair 추가 — 본문이 **한국어일 때만** Step 2 preview 전에 실행. 영어 본문은 대상 아님
- `nara-spec-revision`은 배선하지 않음 — 본문 규약이 영어 전용이므로 한국어 수리 대상이 없다
- `nara-reflect`: durable memory를 **두 층**(파일 기반 memory dir + memory MCP 도구)으로 인정하도록 §3·§4·실패 처리 표 개정
  - dedup을 층별로 분리 — 도구 층 검색은 명사 키워드 1~3개, 문장형 쿼리 금지, **0건을 부재로 단정 금지**(짧은 키워드 재시도 → ID 조회로 확정)
  - dual-store 스텝 신설 — 파일 층에 write한 학습은 도구 층에도 독립 레코드로. 세션 요약 레코드로 갈음 금지, UPDATE도 양쪽
  - receipt를 층별로 분리 표기 — 파일 경로 / 레코드 ID 나란히, 한쪽만 있으면 `divergence`, 도구 미설치면 `store: file-only (<사유>)`
- `nara-reflect`: `nara-memory-audit` **Tier 1 피기백** — write 후 `audit.sh`(bash, ~0 토큰)로 파일 층 점수만 읽어 receipt에 `memory health: total N | flagged M` 한 줄. `M>0`이면 `/nara-memory-audit` **추천만** (Tier 2·수정은 여전히 audit 스킬 소관). 스크립트/`jq`/`git` 부재 시 줄 생략 — 의존 아님
- `nara-reflect`: tiebreaker·skill 추천 트리거·실패 처리 표를 `references/routing-rules.md`로 분리 (조건부 발동 규칙만 이동 — 매 세션 발동 계약은 본문 유지). 3078 → 2737 토큰
- `nara-memory-audit`: dual-store 대칭 맞춤 — Apply에 step 6 **mirror the removal** 추가(파일 archive 시 MCP 쌍둥이 레코드도 같은 승인 배치에서 supersede/삭제, 도구 없으면 skip+명시). Rules에 커버리지 한계 선언 — Tier 1은 bash라 MCP 못 읽음, 파일 층은 프록시일 뿐 **MCP 전용 레코드는 감사 사각**
- `references/output-contract.md` §4: receipt 압축 축을 서드파티 플러그인 이름(`caveman lite/full/ultra`)에서 동작 기준 3단계(`full` / `compact` / `minimal`)로 교체. 배포되는 규약이 특정 스타일 플러그인의 설치를 전제하지 않게 됐다 — 세션에 걸린 어떤 출력 스타일이든 그 요구를 세 단계 중 하나로 매핑해 적용한다. "압축은 형식만 줄이고 §1의 4요소는 어느 수준에서도 빠지지 않는다"는 제약을 명문화
- `README.md`: My Setup 표에서 `caveman` 행 제거 (로컬에서 제거한 플러그인)

### Fixed

- `nara-memory-audit` Tier 1(`scripts/audit.sh`) 오탐 2건 — 값싼 선별기가 값비싼 Tier 2를 보호하는 대신 일거리를 만들어내고 있었다
  - **skill 존재 검사가 틀린 루트에서 해석됐다.** `$CLAUDE_PROJECT_DIR/skills/`만 뒤졌으므로, 스킬 문서가 지시하는 그대로 실행하면(감사 대상 메모리가 *설명하는* repo에서 실행 — 즉 `skills/` 트리가 없는 소비 애플리케이션 repo) 스킬을 언급한 **모든** 메모리가 broken으로 잡혔다. 최고 신뢰 신호로 문서화된 검사라 독자는 이를 신뢰하고, Tier 2는 서브에이전트 예산을 오탐 반증에 썼다
  - 이제 ref의 **형태별로** 해석하고, 형태별 식별자로 보고한다. `skills/<name>/`는 repo 상대 **경로** 주장이라 `skills/<name>`으로, `/nara-<name>`은 **설치된 스킬** 주장이라 `/<name>`으로. 판정이 어느 주장에서 나왔는지 항상 귀속되고, 같은 ref가 broken과 unknown에 동시에 오르는 일이 구조적으로 불가능하다
  - 루트 탐색 순서는 `$NARA_SKILLS_DIRS`(콜론 구분, 목록 전체를 대체) → `$CLAUDE_PROJECT_DIR/skills` → `${CLAUDE_CONFIG_DIR:-~/.claude}/skills` → `~/.codex/skills` → `~/.agents/skills`. 선언된 루트는 첫 번째만이 아니라 전부 탐색한다. 런타임 중립 — 어느 에이전트 디렉터리도 존재를 요구하지 않는다
  - **경로 주장은 repo 트리가 없을 때 "어디에도 없음"까지 판정한다.** 툴킷에서 제거된 스킬은 모든 루트에 없으므로 어느 repo에서 물어도 반박 가능하다 — 이를 unknown으로 내리면 제거된 스킬이 `healthy`로 읽히며 살아 있는 드리프트가 침묵한다. 반대로 어느 에이전트 루트엔 있는 경우엔 `unknown`에서 멈춘다: `nara-` 이전 맨이름(`code-review`, `commit`, `gap`, `jira-triage`)이 그 루트의 범용 이름 서드파티 스킬과 충돌하므로(`code-review`는 실제로 Codex skills 디렉터리에 존재한다) clear 처리하면 마이그레이션 드리프트 부류가 통과한다
  - **Form B 언급이 Form A 주장을 대신 해결하지 못한다.** 같은 스킬명이고 한쪽이 해석되니 넘어가고 싶어지지만, 그러면 위의 확대가 뒷문으로 들어온다 — 파일에 `/nara-x`를 한 줄 덧붙이면 바뀌지 않은 거짓 `skills/nara-x/` 주장의 판정이 지워진다
  - **해석 불가는 실패가 아니다.** 신설 `skill_ref_unknown`은 **0점**이며 "스킬은 존재하는데 이 repo가 경로를 확인할 수 없다"만 뜻한다. JSON `details`에 `skill_refs_unknown` 필드가 추가됐다. `signals[]`에는 새 값이 들어가므로, 배열 길이로 점수를 세던 코드는 과다 계산한다 — `score` 필드를 쓸 것
  - **`ref_paths` 정제기가 파일명의 일부를 지웠다.** YAML 인용부호를 떼려고 `[`, `]`, `"`, `'`, 공백을 문자 클래스로 일괄 삭제했으므로, 선언되지 않은 경로를 조회하게 됐다. 이제 항목별로 앞뒤 공백을 다듬고 인용부호 **한 쌍**만, 인라인 플로우 시퀀스는 외곽 `[ ]` **한 쌍만 쌍으로서** 떼어낸다. 값 안의 문자는 살아남는다
  - 보고된 증상은 브래킷(여러 주류 프레임워크의 동적 라우트 관례인 `app/[locale]/page.tsx`)이었지만, 실제 피해자는 **공백**이었다 — 외부 노트 볼트를 가리키는 절대경로의 `Mobile Documents`가 잘려, 메모리 2개가 선언한 경로 3개가 전부 영구히 missing으로 잡히고 있었다. 이 오탐이 독자를 미는 "해결책"은 `ref_paths`에서 앵커를 지우는 것이고, 그러면 실제 정보가 사라지고 신호 2·3이 영구 무장해제된다. 그래서 **앵커가 아니라 판독기를 고친다**는 규칙을 `SKILL.md` Rules에 명문화했다
  - 브래킷 앵커를 되살리자 신호 3에 **글롭 구멍**이 열렸다. git은 맨 pathspec을 wildmatch로 파싱하므로 `[locale]`이 문자 클래스가 되어 무관한 형제 경로(`app/l/`, `app/a/` …)의 커밋이 앵커에 귀속됐다 — 진짜 drift 0인데 `code_drift`가 발화. `:(literal)` 접두로 고정했다. 수정 전에는 브래킷이 잘려 앵커가 아예 해석되지 않았으므로 도달 불가였던 경로다
  - 같은 잘못된 루트 가정이 **Tier 2 서브에이전트 프롬프트에도** 있었다(`skills/<name>/SKILL.md`를 확인하라고 지시). 값비싼 층이 값싼 층의 오탐을 재확인할 구조였다. 이제 Tier 1과 같은 형태 구분을 따르고, 디렉터리 존재만 보는 Tier 1보다 엄격할 수 있는 유일한 경우(`SKILL.md` 없는 빈 디렉터리)를 근거에 명시하게 했다
  - `references/scoring.md`의 프론트매터 규약에서 절대경로를 일괄 "규약 위반"으로 규정한 문장을 완화했다 — repo 밖에 실제로 존재하는 앵커(외부 노트 볼트, 머신 로컬 설정)에는 절대경로가 정직한 형태다. 신호 2는 여전히 답하고 신호 3만 눈이 먼다
  - **실측** (이 repo의 메모리 48개, `HEAD` 대비). 소비 repo 기준(문서가 지시하는 대로 cwd = `CLAUDE_PROJECT_DIR` = 소비 repo) broken 판정 19건 → 3건: 3건은 0.21.0에서 제거된 스킬이라 계속 broken(폴백이 되살린 진짜 드리프트), 8건은 정직한 `unknown`, 나머지 9건은 실제 해석 성공. 판정 슬롯은 Form A 11 + Form B 9 = 20이므로 3+8+9로 맞는다 — 형태별 식별자 도입으로 수정 전 19와 단순 차감이 성립하지 않는다. flagged(2점 이상) 10 → 3. nara-kit repo 기준 broken 4 → 4로 마이그레이션 드리프트 탐지가 보존됐고, flagged는 6 → 4(공백 정제 수정분)
  - 하네스가 지키지 못하던 것 3건을 케이스로 메웠다 — **공백 경로**(CHANGELOG가 실제 피해자로 지목한 바로 그것인데 브래킷 케이스 4종이 전부 green인 채로 통과했다), 절대경로 as-given 폴백(외부 볼트 앵커 3개가 여기 달려 있다), `/nara-kit` 제외. 셋 다 해당 mutation을 재삽입하면 실패하는 것을 확인했다
  - `NARA_SKILLS_DIRS`는 **탐색 목록만** 대체한다. Form A의 권위 판정은 `$CLAUDE_PROJECT_DIR/skills`를 직접 보므로 이 변수로 우회되지 않는다 — 문서에 "목록 전체를 대체"라고만 적었던 것을 좁혔고, unknown 판정을 결정시키는 수단은 `CLAUDE_PROJECT_DIR`임을 Troubleshooting에 명시했다
  - 회귀 스위트 `evals/nara-memory-audit/` 추적 시작 (`.gitignore` opt-in). `regress.sh`는 케이스별로 임시 repo를 만드는 결정론적 하네스 18종·단정 42개로, bash 3.2·5.x 및 툴킷이 설치되지 않은 환경에서 동일하게 통과한다. 9종은 **가드**다 — 수정이 검사를 느슨하게 만드는 방향으로 "통과"하는 것을 막는다: 어디에도 없는 스킬 ref는 계속 broken인지, repo 내 마이그레이션 경로는 계속 broken인지, 진짜 없는 브래킷 경로는 계속 invalid인지, 에이전트 루트 이름 충돌이 낡은 경로를 지우지 않는지, `/nara-x` 언급이 거짓 경로 주장을 지우지 않는지, 브래킷 앵커의 **진짜** 변경은 여전히 drift로 잡히는지, 공백 경로가 계속 해석되는지, 절대경로 앵커가 계속 해석되는지, `/nara-kit`이 스킬로 오인되지 않는지
  - `eval.yaml`의 태스크 레이어는 `executor: mock`과 "mock 마커가 출력에 없어야 한다"는 단정이 정면 모순이어서 **구조적으로 0/4**였다(실행해 확인). mock은 프롬프트를 되돌려줄 뿐 스킬을 호출하지 않으므로 어떤 단정도 판별력이 없다 — eval 레벨 그레이더를 제거하고, 태스크는 실제 executor가 붙을 때까지 **기록된 시나리오**임을 명시했다. `output_contains` 문자열이 태스크 자기 이름에서 에코되어 통과하던 것도 이름을 바꿔 끊었다. 같은 모순이 있던 `evals/nara-gap/eval.yaml`도 함께 고쳤다

## [0.21.0] - 2026-08-14

> **BREAKING — 업그레이드 시 수동 조치 필요.** 스킬 4종이 제거됐다. `npx skills update`는 **삭제된 스킬을 지우지 않으므로** 설치본에 옛 사본이 그대로 남는다:
>
> ```bash
> rm -rf ~/.claude/skills/nara-workflow-orchestrator \
>        ~/.claude/skills/nara-workflow-dev-mode \
>        ~/.claude/skills/nara-workflow-doc-mode \
>        ~/.claude/skills/nara-workflow-viz
> npx skills update
> ls ~/.claude/skills | grep -c '^nara-'   # 47 (+ naranizer = 48)
> ```
>
> 옛 사본을 남겨두면 존재하지 않는 흐름을 가리키는 지침이 계속 로드된다. Codex 쪽 설치 경로도 동일하게 정리한다.
>
> **대체 경로**: `orchestrator`/`dev-mode`/`doc-mode` → 개별 스킬 직접 호출 + `nara-now`의 다음 행동 추천 · `viz` → 대체 없음(입력 `workflow.json`이 애초에 없어 실행 불가였다) · Implementation Notes Gate → `nara-implement`.

### Removed

- **워크플로 메타 스킬 4종 제거** — `nara-workflow-orchestrator`, `nara-workflow-dev-mode`, `nara-workflow-doc-mode`, `nara-workflow-viz`. **BREAKING**: 소비자 설치본에는 옛 스킬이 그대로 남으므로 수동 삭제가 필요하다 (`rm -rf ~/.claude/skills/nara-workflow-*` 후 `npx skills update`).
  - 근거는 취향이 아니라 실측이다. `~/.claude/projects/**/*.jsonl`에서 최근 60일 호출을 세면(사람의 슬래시 호출 `<command-name>`과 어시스턴트의 Skill 툴 호출 `"skill":` **양쪽**) 네 스킬 합계가 **1회**다 — `dev-mode` 1, 나머지 셋은 **각 0회**. 같은 기간 `nara-now` 74, `nara-reflect` 63, `nara-code-review` 23. 즉 흐름이 불필요한 게 아니라 **흐름을 스킬로 포장하면 아무도 부르지 않는다**. `viz`는 입력이어야 할 `workflow.json`이 저장소에 아예 없어 애초에 실행 불가였다.
  - 같은 날 `dev-mode` spine을 6→5단계로 고치며 3개 파일을 갱신했는데, 측정 결과 그 편집이 바꾼 실행 경로는 0이었다. 문서만 고친 셈이고, 그게 이 제거의 직접적 계기다.
  - **계약은 죽이지 않고 옮겼다** — Implementation Notes Gate(scope scaling·pre-flight·trailing `📝`·state gate·카테고리 4종 원문)는 `nara-implement/references/implementation-notes.md`로 이관. `docs/implementation-notes.md`의 **경로·섹션명·`Reconciliation Log` writer(`nara-gap --verify`)는 불변**이라 `nara-gap`·`nara-reflect` 연결이 그대로 산다.
  - 흐름 서술은 `skills/README.md`에 **"권장 순서이지 실행되는 스킬이 아니다"**로 남겼다. `CLAUDE.md`·전역 `rules/workflow.md`도 같은 방향으로 갱신. 다음 단계 안내는 `nara-now`(74회)가 맡는다 — 새 워크플로 스킬을 만들지 않는다는 것이 이 변경의 핵심 조건이다.
  - `nara-ac-draft`는 2회지만 **유지**한다. AC가 대개 외부 SoT에 이미 있고 `nara-prep`이 verbatim으로 옮기므로, AC 게이트가 우회되는 게 아니라 통과되는 것이다 — 낮은 호출수가 정상 동작이다.

### Changed
- **`nara-now`가 진행 위치를 추적한다** (제거된 워크플로 스킬의 대체재). 74회로 최다 호출되는 스킬이 "지금 어디고 다음이 뭔지"를 맡는다 — 흐름을 별도 스킬로 만들면 아무도 부르지 않는다는 게 측정의 결론이라, **새 워크플로 스킬을 만들지 않는 것이 이 설계의 조건이다.**
  - 추측하지 않기 위해 상태를 기록으로 남긴다: `nara-implement`가 유닛 검증 통과(`Pass`) 시 `docs/plan.md`의 **그 유닛 헤딩에만** `— ✅ done`을 붙이고, `nara-now`는 그 표식만 읽는다. 커밋 로그·파일 변경으로 완료를 유추하지 않는다. `Fail`·`Blocked`·`Unverifiable`엔 표식을 안 붙인다.
  - 추천이 **실행 가능한 명령 형태**로 나온다 — "구현하세요"가 아니라 `/nara-implement T-2`, 인자까지 채워서(`/nara-prep PROJ-123`). 그대로 복사해 붙일 수 있어야 한다.
  - 결정표에 진행 행 추가: plan에 미완료 유닛 있으면 `{done}/{total} 완료 · 다음 T-N {제목}`.
- **스킬 말미 handoff 표준화** — `nara-prep`·`nara-grill`·`nara-gap`·`nara-code-review`·`nara-reflect`에 `**다음**: /nara-<skill>` 한 줄. 다음 단계를 사람이 기억하지 않아도 화면에 남는다.
- **dev-mode core spine이 6→5단계** — `plan → execute → verify → code-review → reflect`. `nara-gap`이 spine 맨 앞에서 빠졌다: 구현 전 gap은 greenfield에서 score ~0의 무정보 산출물인데, 사용자 작업이 대부분 기획부터 시작하는 greenfield라 상시 발생했다. **축은 brownfield/greenfield가 아니라 타이밍이었다** — greenfield라도 구현 *후* 요구사항-vs-코드 대조는 유효하므로 gap을 verify 단계로 옮겨 생성+판정을 1회로 합쳤다. brownfield 인수인계처럼 "이 코드 얼마나 됐나"가 먼저 필요하면 entry에서 조건부 위성으로 호출한다.
  - **verify는 2-track** — 코드 AC는 `nara-gap`, `browser-visible: yes` AC는 `nara-browser-verify`. 초기 검토안이던 "gap 전면 조건부화"는 기각됐다: `gap --verify`가 기존 `gap.md`를 전제하므로(`nara-gap/SKILL.md`) 생성이 안 돌면 `docs/implementation-notes.md`의 `## Reconciliation Log` **유일한 writer**와 `nara-now` 라우팅이 함께 죽는다.
  - `nara-now` 결정표 재작성 — `gap.md` 부재가 더 이상 "gap 분석 필요" 신호가 아니다(verify 전엔 없는 게 정상). 3행이 `/nara-plan`, 3-bis가 `/nara-implement`, 3-ter가 verify로 갈린다.
  - 근거: `docs/adr/0001-verify-browser-ac-at-runtime.md` (repo-local).
- `nara-ac-draft`(주 소유) / `nara-prep`(외부 SoT 있을 때만) — AC마다 **`browser-visible: yes|no|unknown` 태그**. 검증 경로 자체는 `nara-plan`의 기존 `검증` 필드가 계속 소유하고, 상류엔 태그만 붙는다. prep의 **no-derive 원칙을 건드리지 않기 위한 선택** — 검증 경로는 raw SoT에 없는 순수 엔지니어링 판단이라 prep이 만들면 verbatim 보존이 무너지고, 그 원칙은 `nara-gap`의 verbatim pre-scan(`git grep -F`)과 맞물린 구조적 제약이다. greenfield엔 외부 SoT가 없어 prep이 아예 안 돌므로 주 소유자는 `ac-draft`다.
- `nara-plan` — `검증` 필드 계약 추가. `browser-visible: yes` AC를 포함한 단위는 대상 URL·viewport·auth·통과 조건과 실행 주체(`nara-browser-verify`)를 명시해야 하며, "UI 확인" 같은 문구로 대체하면 그 단위는 `Blocked`. 태그 없는 레거시 `requirements.md`는 `unknown`으로 취급해 중단 없이 진행한다.
- `CLAUDE.md` — **형제 스킬 링크 규약 성문화**. `../nara-<other>/references/*.md` 참조는 신규 패턴이 아니라 이미 4곳(`naranizer`, `nara-design-studio`, `nara-golden-path-discover` 2곳)에서 쓰이던 관행이었고, 저장소 루트 `references/`가 배포되지 않으므로 공용 파일로 빼는 선택지 자체가 없다. 이제 모든 형제 참조는 **대상 부재 시 동작을 명시**해야 한다(스킵 후 진행 / `Unverifiable`). `waza check`는 대상 존재 여부와 **무관하게** 동일한 `link escapes skill directory`를 내므로 깨짐 감지기가 아니다 — 릴리스 전 실행할 grep 기반 체크를 Release 절에 넣었다. 근거: `docs/adr/0002-link-sibling-skill-references.md`.

### Added
- `nara-claim-audit` (신규 스킬) — **기획문서의 수치 주장을 CSV 스냅샷과 대조**한다. 문제는 "몰라서 비워둔 수치"가 아니라 **자신 있게 틀린 수치**다 — 실제 12개인데 8개라고 쓰고 그 위에 기획이 쌓이면 정합성이 끝에 가서 깨진다. `[UNVERIFIED]` 규약은 이미 10개 스킬이 쓰지만 **쓰는 사람이 추측 중임을 자각할 때만** 붙으므로 이 실패를 원리적으로 못 잡는다. 실증 수요: 데이터 파일 20개 중 10개 이상에서 문서 수치 불일치.
  - **측정은 `assets/audit.py`(Python 표준 라이브러리만, 새 의존성 0)가 소유한다.** 사람이 못 세는 양이라 자동 교체가 기본값인데, LLM이 마커를 해석하면 같은 문서에서 매번 다른 값이 나와 자동 교체의 전제가 무너진다. 테스트 60개(`test_audit`/`test_apply`/`test_candidates`).
  - **마커는 제한된 mini-DSL** — `count rows` / `distinct|sum|avg|max|min <col>` + `where <col> <op> <값>`(AND만) + 단위 환산. 자연어·JOIN·서브쿼리·`or`는 **해석하지 않고 `syntax_error`로 거부**한다. "활성"이 `status=active`인지 `last_login` 기준인지를 추측하면 스킬이 병을 옮긴다.
  - **없는 것을 0으로 세지 않는다** — 컬럼·파일 부재, 데이터 행 0건 CSV는 전부 `mapping_failure`. 헤더만 남은 export를 0으로 보고하면 "관리자 0명"이라는 자신 있는 오답이 문서에 박힌다.
  - **자동 교체는 건별 승인 없이**(수백 건 전제) 하되 두 겹으로 막는다: 교체 전 **스냅샷**(gitignore 확인 실패 시 ESCALATE·진행 거부, receipt에 복구 명령) + **살균 게이트**(1/10 이하 붕괴·10배 폭증 차단, 10 미만 소수는 비율 검사 면제). 마커 없는 숫자(날짜·목차 번호·순번)는 절대 건드리지 않는다.
  - **`--bootstrap`** — 마커 없는 기존 문서용. 노이즈 필터 후 후보만 제시하고 **교체하지 않는다**(매핑이 추론이므로). 실측: `spec-naranizer.md` 숫자 토큰 71개 → 후보 22개, 실제 주장 재현율 100%.
  - **판정에 `ambiguous` 추가** — 마커 앞 구간에 숫자가 둘 이상이면 어느 것이 주장인지 확정 불가이므로 교체하지 않는다. 코드 리뷰가 실행으로 재현한 결함: `활성 사용자 10명 (전체 50명 중)`에서 **맞는 10은 두고 50을 10으로 바꿔** 무관한 사실을 조작했고, `월 1,200건`은 `1,1200건`이 됐다. 마커는 그 수치 **바로 뒤**에 두는 것이 규칙이며, 한 줄 다중 마커는 각자 직전 마커 이후 구간만 본다.
  - 리뷰에서 함께 닫은 것: 필터 결과 0행을 0으로 확정하던 문제(→ `mapping_failure`), 코드펜스 안 예시까지 교체하던 문제, 스냅샷이 재실행 시 원본을 덮어써 복구본을 파괴하던 문제(→ run별 디렉터리), `git check-ignore`가 엉뚱한 경로를 검사해 tracked 경로를 통과시키던 문제, 금칙어 부분문자열이 `joined_at`·`selected`를 오거부하던 문제, 숫자/문자열 비교를 행 단위로 결정해 `"1,200"`을 조용히 누락하던 문제, 부분 export(`5000→1000`)가 살균 게이트를 통과하던 문제(→ 절반 이상 이동은 전부 보류). 전체: `docs/review/260814-claim-audit.md`.
  - 진입 지점 2곳: `nara-publish-spec` 스텝 0 게이트(미확인 수치 남으면 게시 거부), `nara-grill` 사실 조사(수치 주장 + CSV 있을 때만 읽기 전용 대조 — 수치가 문서에 굳기 전에 잡는다). `nara-workflow-doc-mode` 스텝 추가는 실사용되지 않아 보류.
- `nara-browser-verify` (신규 스킬) — **브라우저 AC를 헤드리스 런타임에서 판정**한다. 지금까지 `verify` 슬롯은 `nara-gap --verify` 하나였고 그것은 `docs/requirements.md` 텍스트를 코드에 `git grep -F`로 대조하므로 **화면에 보이는 AC를 원리적으로 검증할 수 없었다** (전 스킬 SKILL.md에 `headless` 언급 0건이었음). `nara-test-implement`는 커밋되는 테스트 *코드*를 쓰는 다른 산출물이고, `nara-local-shot`은 캡처만, `nara-ui-diff`는 배포 baseline과의 *비교*라 greenfield엔 baseline 자체가 없다.
  - **판정 스킬이라 후보가 아니라 결론을 낸다** — `Pass | Fail | Blocked | Unverifiable` terminal token 하나. 정적 소스 분석으로 `Pass`를 낼 수 없고, MCP 드라이버가 없으면 `Unverifiable: requires live runtime`으로 끝난다.
  - **축별 필수 증거 매트릭스**(`references/evidence-matrix.md`) — geometry/typography/color는 computed 값이 primary, asset/imagery/전체 렌더는 **실제로 열어본 스크린샷** 필수(computed·DOM 대체 불가), behavior/mutation은 trusted input + network request·response, a11y focus는 trusted key + 표시된 focus 스크린샷. **한 축이라도 필수 증거가 없으면 그 축 `Unverifiable`이고 aggregate `Pass` 금지.** "검사 안 함"과 "Unverifiable"을 구분해 적는다.
  - **anti-cheat 실행 규율**(`references/anti-cheat.md`) — `element.click()`/`form.submit()`/`dispatchEvent()`는 상호작용 증거가 **아니다**(합성 이벤트는 hit-testing·기본 동작·이벤트 순서를 건너뛰어 가려진 버튼·`pointer-events:none`·비활성 상태를 전부 통과시킨다). `evaluate_script`는 관찰 전용. mutation 주장에는 request+response 필요 — toast·로컬 DOM 변화·응답만으로는 각각 불충분. 인용한 스크린샷은 존재+non-empty+**실제 inspect**. 직렬화는 primitive를 plain object로 직접 복사(안 하면 두 MCP 다 `{}`를 떨구는데 그걸 측정 성공으로 오인).
  - **소유권 기반 정리**(`references/session-lifecycle.md`) — run-owned만 종료, `killall`·broad `pkill` 금지, 강제 종료 전 PID+profile 대조. dev 서버는 프로세스 exit가 아니라 **HTTP/port readiness를 poll**. 증거 디렉터리는 `git check-ignore` 통과 필수(실패 시 ESCALATE·진행 거부).
  - 서버 기동·auth bypass·드라이버 사다리는 복제하지 않고 형제 스킬 reference를 링크한다(`../nara-local-shot/references/auth-bypass.md`, `../nara-ui-diff/references/drivers.md`) — 단독 설치 시 스킵하고 repo 근거로 판단. 근거: [ADR-0002](docs/adr/0002-link-sibling-skill-references.md).
  - 배경·대안 비교: [ADR-0001](docs/adr/0001-verify-browser-ac-at-runtime.md).
- `nara-design-studio` — **레이아웃 파리티 검사** `assets/runtime/layout-contract.js` + `check-layout.py`. 핸드오프의 일치 기준은 픽셀이 아니라 **레이아웃**(섹션 순서·테이블 컬럼 순서·필드 순서·액션이 어느 쪽에 붙는지)인데, 지금까지 스펙은 그것을 순서 있는 형태로 진술하지 않아 구현자가 PNG 보고 재유추했다. 추출기는 **하나**를 디자인 쪽(스튜디오)과 구현 쪽(실제 페이지 콘솔/브라우저 MCP) 양쪽에서 돌려 정규화 JSON을 만들고, `check-layout.py`가 diff한다(exit 1 = 드리프트). 섹션 이름은 양쪽이 다르므로(디자인은 라벨, 앱은 없음) **콘텐츠 겹침**으로 정렬한다. `Spec.md` 최상단에 계약이 실리고 Export 메뉴에 `Layout contract (JSON)` 추가. 라디오/체크박스 옵션 라벨은 필드가 아니므로 제외 — 옵션 문구 변경이 드리프트로 오탐되지 않는다. 테스트 13개(`test_check_layout.py`).
- `nara-design-studio` / `nara-design-pack-builder` — **팩 → 실제 prop 매핑** `components[].real`(`import`/`from`/`propMap`/`drop`/`notes`). 팩 컴포넌트는 **적응된 복제본**이다 — `adapt-guide.md` §1–§2가 store/router/context 결합을 plain prop으로, CSS-in-JS를 토큰 스타일로, i18n 훅을 문자열로 바꾸라고 **요구**하므로 divergence는 구조적으로 발생한다. 그런데 존재하지 않는 prop을 넘기면 React가 **조용히 무시**한다 — 타입 에러도, 린트도, 실패 테스트도 없이 화면만 틀어진다. pack-builder Step 4가 적응하는 그 순간에 기록하고(나중 역추적은 원본 DS 재독), 런타임이 `/_pack/_ds_manifest.json`을 읽어 **해당 후보가 실제로 렌더한** 컴포넌트 행만 `Spec.md`에 넣는다. `real` 없는 팩에는 명시적 경고 — "모름"과 "동일함"이 같게 읽히면 안 된다.
- `nara-design-studio` — **DESIGN.md → 팩 변환기** `assets/runtime/designmd_to_pack.py`. DESIGN.md(Stitch format) frontmatter는 color role set·typography scale·spacing·radii·컴포넌트 스타일 스펙을 이미 담고 있어 **번들 starter 팩(T1, 토큰 23개·컴포넌트 0)보다 토큰 표면이 넓다** — 산문으로 읽지 말고 팩으로 변환한다. `components:` 블록이 있으면 **T2**(각 항목이 마운트 가능한 standalone JSX + `_ds_bundle.js`), 없으면 T1.
  - **authored / derived 분리.** 엔진 크롬이 요구하지만 DESIGN.md가 정의하지 않는 토큰(`--ds-primary-hover`, ink 램프, `--ds-radius-200`, `--ds-shadow-popover` 등)은 `tokens.css`의 별도 주석 블록으로 emit + stdout 리포트. 매핑 가능한 role이 없으면 `MISSING` + exit 1 — 추론값이 authored 값과 섞이지 않는다.
  - **리터럴은 컴포넌트 스코프 토큰으로 승격.** DESIGN.md `components:`가 geometry를 리터럴로 적으므로(`padding: 12px 24px`) 그대로 인라인하면 팩 자신이 adherence 규칙을 위반한다 → `--ds-comp-<name>-<prop>`로 뽑고 JSX는 `var()`만 참조.
  - pyyaml 있으면 사용, 없으면 stdlib 파서로 폴백 — **새 의존성 0**.
- `nara-design-studio` — **emit-time adherence 게이트** `assets/runtime/check_adherence.py`. baseline 규칙 "tokens only — no hardcoded brand values"는 산문으로는 강제 불가(`padding: 16px`가 적힌 시점에 이미 위반)라 기계 검사로 전환. 기본 규칙 2개(raw hex / allowlist 밖 raw px, `1px` hairline은 허용)는 팩 협조 없이 동작, 위반 시 exit 1 + 라인 리포트. 인라인된 `:root { … }` 블록은 면제(`SKILL.md` §5가 portable single-file export에 토큰 블록 인라인을 지시하므로 그것은 정의부지 하드코딩이 아니다). 팩은 매니페스트 `adherenceConfig`로 규칙을 조일 수 있다.
- `nara-design-studio` — **그린필드 분기**(`SKILL.md` §2.1–2.2). 팩 tier는 "DS가 있나"만 답하고 "IA가 있나"는 아무도 묻지 않아, `startingPoints` 없는 팩에서 화면마다 nav·컬럼·상태값이 재발명되고 화면 2개째부터 일관성이 사라지던 문제. `manifest.startingPoints` 공백 여부로 **자동 판정**(유저에게 묻지 않음)하고, 보이는 IA(nav 형태·페이지 골격)는 기존 layout-direction candidate가 갈리는 축으로 흡수, 안 보이는 IA(상태 enum·정렬 기본·row 클릭 의미)는 후보 비교가 무의미하므로 기본값 통보 + 거부권. 확정된 화면은 팩 `startingPoints`로 **write back**해 다음 빌드부터 브라운필드로 수렴시킨다.

- `nara-jira-triage` — Step 7 `reconcile` 계약 명문화: 큐 이슈 상태를 **PR 실측**으로 되돌리는 전이 규약(strict KEY 경계 매칭 후 `MERGED`→`done`+`drain_state=done`, `OPEN`→`in_review`, 다건·미머지 close는 무변경+경고)과 증거 우선순위(PR 실측 > Jira 상태 > `pr_url` metadata — 후자는 KEY 검증 없이 심겨 오염 가능, 근거 아님)를 선언. `gh pr list --search`가 fuzzy라(`PROJ-40` 질의에 PROJ-39/29 혼입) 경계 매칭 `(^|[^A-Za-z0-9])<KEY>([^0-9]|$)` 필수.
  - **실행은 이 스킬이 하지 않는다** — 결정론(LLM 판단 0)이라 out-of-band 크론 스크립트 소유. 역할 분리 명문화: 오토파일럿=없는 것만 생성(classify에 LLM 필요) / 스크립트=있는 것만 상태 sync. Step 1~6 = 생성 전용.
  - 배경: 큐 `done` 전이가 jira-drain cleanup에만 있어 cleanup 미실행·큐 밖 손PR 건이 머지 후에도 `in_review`로 박제됨.

- `nara-review-reminder` — **팀 리뷰 요청 확장 + 리마인더 이슈 reconcile** (`references/teams-and-reconcile.md` 신규). 필터가 `reviewRequests[].login`만 봤는데 GitHub은 팀 요청을 `{"__typename":"Team","slug":"<org>/<team>"}`으로 주고 **`login` 필드가 없다** — 팀으로 걸린 요청은 100% 누락돼 티켓이 아예 생기지 않았다(실측: sandbox-dns#721의 한 팀, api-server 열린 PR 다수의 팀 요청 전건). `gh api /user/teams`로 `<organization.login>/<slug>`를 조립해 **동적으로** 해석한다 — 팀 slug 하드코딩은 팀 이동 시 조용히 썩고, 어차피 오탐 위험을 줄여주지도 않는다(그건 아래 별개 필터의 몫).
  - **"내 차례" 필터.** 팀 요청은 팀원 아무나 처리하면 되므로, 매칭된 팀의 멤버 중 리뷰를 이미 남긴 사람이 있으면 티켓을 만들지 않는다. GitHub이 "팀원 1명 리뷰 시 팀 요청 자동 해제"를 하는지에 **의존하지 않는다** — 해제되지 않은 채 남아 있는 PR이 관측됐고(해당 리뷰어들이 그 팀 비멤버라 반증은 아니나 확증도 없다) 어느 쪽이든 직접 계산이 맞다. 개인 지정이 함께 있으면 팀원 리뷰와 무관하게 대상 — 나를 콕 집은 요청이므로.
  - **Step 0 reconcile.** 리마인더 이슈를 닫는 주체가 아무도 없어 끝난 PR의 이슈가 영구히 쌓였다. 생성 루틴 **전에** 열린 이슈를 실측 대조해 머지·클로즈·내 리뷰 완료는 `done`, 팀원이 대신 처리한 건은 `cancelled`로 전환한다(전환 건에는 코멘트·멘션 없음 — 조용히 닫는다).
  - `tracker_type=review` metadata 신설. `pr-activity-reminder`의 `activity` 이슈도 `pr_url`을 갖고 있어, 이 구분 없이는 reconcile이 **남의 자동화 이슈를 닫는다**. `request_via`는 reconcile이 "팀 경유만" 여부를 재조회 없이 판정하게 한다.
  - `read:org` 스코프 부재 시 **중단하지 않고** 개인 매칭만으로 계속 진행 — 리마인더가 통째로 죽는 것보다 부분 동작이 낫다.
  - waza: 토큰 1200→1677(+477, 상세는 reference로 분리해 +1152에서 축소), 링크 이탈 advisory는 baseline과 동일한 `../README.md` 백링크 1건으로 불변.

- `nara-jira-triage` — Step 7 reconcile 계약에 **Pass C(Jira 역기록)** 추가. Pass A가 merged PR로 큐를 `done` 처리해도 Jira는 `In Progress`에 남아 두 트래커가 갈라졌다. Pass C는 A의 `MERGED` 1건 분기에서만, 그리고 **Jira assignee가 나인 티켓에만** 전이를 건다.
  - **기본 OFF**(`JIRA_SYNC=1` 명시 opt-in). 팀이 보는 트래커에 대한 유일한 외부 mutation이므로 자동 실행을 기본값으로 두지 않는다 — merged가 곧 종료인지는 팀 워크플로의 판단이다.
  - **종료 상태명은 프로젝트마다 다르다.** 전이 id 하드코딩 금지를 계약에 명문화 — 한 프로젝트는 `Resolved`/`Closed`를 노출하고 다른 프로젝트는 `Done` 하나뿐이라, 이름 하나로 고정하면 한쪽이 통째로 막힌다. `to.statusCategory.key == "done"`인 전이 중 `$JIRA_CLOSE_STATUSES` 순서로 첫 매칭을 고른다(카테고리 제약이 있어 동명의 비-done 상태를 잘못 집을 수 없다).
  - 실행 주체는 여전히 이 스킬이 아니라 out-of-band 크론 스크립트 — 스킬은 계약만 선언한다.
- `nara-local-shot` — Before/After 비교를 **두 revision·두 pass로 명시적 절차화** (Step 1 재작성 + `references/comparison-passes.md` 신규). 기존 Step 1은 As-Is 복원을 `git show`+preview page 한 경로로만 처방해서, subject가 **real app page**이거나 옛 렌더가 그 사이 바뀐 공유 코드에 기대던 경우(복원 시 drift) 필요한 두 번째 pass — 베이스 revision 워크트리 + dev server 재시작 + deps/build/codegen 산출물 갱신 — 를 아무도 언급하지 않았다. 그 비용은 앱을 띄우는 시퀀스이고 teardown 이후에 발견되므로 런치를 두 번 지불하게 되며, 비교표는 한 열만 채운 채 placeholder로 나간다.
  - **As-Is 존재 여부를 먼저 판정.** 순수 추가 변경은 선행 렌더가 없으므로 To-Be만 찍고 그 사실을 보고 — 없는 이전 상태를 뒤지지 않는다. 현재 상태 확인만 원하면 single pass.
  - **네이밍 스킴 선고정** `<state>-asis.png` / `<state>-tobe.png` — 두 pass가 같은 state를 쓰므로 무자격 이름은 충돌. Step 6에 teardown 전 계획된 shot 전수 존재 확인 추가(사후 발견 = 전체 재런치).
  - 트리 전환은 in-place `checkout`/`stash` 대신 별도 워크트리 — 미커밋 To-Be 작업 보존. revision 넘어온 stale 산출물이 비교의 반대편을 조용히 렌더하는 케이스 경고.
  - waza: advisory fail 집합 불변(baseline 4개 그대로, 신규 0), module-count 2→3(optimal 유지), 토큰 1318→1566(SKILL.md는 요약만, 절차는 reference로 분리).
- `nara-design-studio` — 부트스트랩 게이트를 **프로젝트 1회 결정** 모델로 재작성. 어떤 디자인 시스템 위에 짓는지는 프로젝트 고유 결정이므로 **상속되지 않는다** — 유저의 `defaultPackPath`나 공유 디렉터리에 팩이 있다는 이유로 신규 repo가 무관한 회사의 디자인 언어를 조용히 물려받는 것을 막는다. 결정을 확정할 수 있는 소스는 `.claude/overrides/nara-design-studio.md` 하나뿐이고(있으면 무질문 사용, 없으면 반드시 질문 후 여기에 기록), `settings.local.md`의 `defaultPackPath`(`packPath`는 alias)와 `~/.claude/design-packs/*/`(팀·사내 배포가 팩을 떨어뜨리는 자리)는 **질문의 기본 선택지로 강등** — 단독으로 이기지 않는다. 기존엔 단일 글로벌 `packPath`뿐이라 프로젝트마다 다른 팩을 쓰려면 매번 그 줄을 고쳐야 했다. 선택지에 **DESIGN.md 변환**을 추가하고 (a)의 소스 범위를 "design-system codebase"에서 설치된 npm 패키지·Storybook·배포 dist까지로 확장했다(UMD를 배포하는 DS는 컴포넌트별 adaptation이 아예 불필요한 경우가 많다).
- `nara-code-review` — trailing status 계약을 **증거 없이 쓸 수 있는 verdict가 하나도 없게** 만들고 실패 불가 테스트 카탈로그를 주입 (3커밋, forge EPT 검증):
  - `agents/tests-regression.md`에 **실측 vacuous 기전 10종** 열거(기존엔 `"Assertions that cannot fail"` 한 줄뿐). 실제 리뷰에서 mutation으로 증명된 사례 — `mockImplementationOnce`+React 동기 재시도 / 대상 상수로 기대값 계산 / `not.toBe` 방향 미고정 / 가드 없는 분기 / 소스가 안 읽는 필드로 `it.each` / 부재 단정 / React가 `null`을 렌더 안 함 / boundary 밖 chrome 단정 / 최상단 고정 mock / 키·상수 리터럴 복제.
  - `report.md` trailing status가 **명령 종료 상태와 파일 수를 인용**하도록 강화. `validation: pass`는 인용된 exit code로만, `scope-integrity`는 양측 카운트로만 성립.
  - **`scope-integrity`에 세 번째 상태 `expanded` 추가.** 성립 조건 3개(파일별 사유·수정 적용 **전** 공개·명시적 승인) 전부 충족해야 하고 하나라도 없으면 `MISMATCH`. 사후 승인은 MISMATCH를 되돌리지 않는다 — 먼저 공개하는 이유가 유저가 아직 거절할 수 있어야 한다는 것이므로. `expanded`는 `→ ESCALATE:`를 달지 않고 applied로 보고된다.
    - 배경: `match | MISMATCH` 2상태에서는 **사유를 적고 승인까지 받은 확장도 ESCALATE로 끝나** 통제된 실행이 escalate로 보이고 미공개 드리프트와 구분되지 않았다.
  - 템플릿이 산문과 어긋난 4슬롯 정합: `validation: pass`에 `baseline <base> → exit <code>` 슬롯(비-0 exit을 baseline 인용으로 강등하는 경로는 산문에만 있고 템플릿은 `exit 0`을 하드코딩했다) / `scope-integrity: match`·`fix-ledger: match`도 카운트 인용 / `overrides: none`은 확인 명령을 인용(`none`은 "찾아봤다"는 주장, `unverifiable`은 안 찾았다는 뜻) / `→ ESCALATE:`는 **블록 바로 아래** 고정(리포트 본문 유무와 무관하게 status와 함께 이동).
  - eval 신규 task 2 + fixture 2(승인된 확장 / baseline 인용된 비-0 exit). 기존 `validation-status-evidence-001`이 **반대 케이스 회귀 가드**로 작동 — 미baseline·미공개는 여전히 `fail`·`MISMATCH`이고 3라운드 전부 green.
  - 미해소(다음 테마): `→ ESCALATE:`가 MISMATCH에만 규정돼 `validation: fail`·`unverifiable`의 escalate 여부 미정 / `unverifiable`과 zero-fix 표(`match`+`0,0,0` 강제)의 상호작용 / SKILL.md가 500 하드리밋 대비 632토큰 초과(20 모듈 통합·examples 섹션 부재와 함께 별 테마).
- `nara-code-review` — 검증 단계의 **wall-clock 낭비와 조용한 오염 경로 2건**을 `verification.md`에서 차단 (실사용 세션 회고 기반, SKILL.md 무변경):
  - **뮤테이션 재검증 스코프 규칙 신설.** 스킬이 `tests-regression`에서 "살아남는 mutation을 지목하라"는 증거를 요구하면서 정작 **수정 후 재검증 범위는 규정하지 않아** 라운드마다 전량(10~20종 × 30초~4분) 재실행됐다 — 10분 툴 타임아웃에 두 번 걸린 실측 사례. 재실행 대상을 **이번 라운드가 바꾼 파일에 mutation site가 있거나 kill하는 테스트가 바뀐 mutant**로 한정(나머지는 이전 판정을 라운드 표기와 함께 재진술), 전량 스윕은 수렴 후 최대 1회, 배치당 ≤4 + 배치별 결과 즉시 영속화(타임아웃이 앞 배치 결과를 못 버리게).
  - **뮤테이션 잔존물 가드.** 배치 러너는 프로덕션 코드를 in-place로 변형하고 종료 시 되돌리므로, 타임아웃 kill은 **변형된 채로 남은 파일**을 만든다. 배치 전 pre-state(`git stash create` 또는 파일별 `git hash-object`)와 `git status --porcelain`을 기록해 배치 후 비교 — 불일치면 기록된 pre-state로 복원 후 STOP·escalate, 다음 배치를 dirty carry-over 위에서 시작 금지, 잔존물 검사가 실패한 실행은 verified로 보고 금지.
  - **writer 계열 validator의 경로 한정.** formatter·`--fix` linter·codemod는 매니페스트 파일을 명시 인자로만 실행하고 repo-wide 글롭(`npm run format` → `prettier --write .`)은 금지. 매니페스트 밖 재작성은 ledger가 설명할 수 없어 `changed-but-unclaimed`로 떠오르고 `scope-integrity`를 오염시키며 commit amend를 유발한다(실측: amend 2회). 경로 한정이 불가능한 도구는 check/dry-run으로만 실행.
  - eval 신규 task 2 + fixture 2(타임아웃 배치의 잔존물 / 글롭 formatter가 12개 무관 파일 재작성). 후자는 `scope-expansion-disclosed-001`의 대칭 케이스 — 사유·승인 없는 확장은 validator가 전부 green이어도 `MISMATCH`로 남는다. 설치된 waza(v0.31.0)에 `eval` 커맨드가 없어 러너 대신 **편향 없는 서브에이전트 프로브 2회**로 grader 문구를 실측했고, 초안 anchor 3개가 오탐으로 드러나 교정: (1) trailing status를 요구하지 않는 프롬프트에 대문자 `ESCALATE`를 요구한 건 계약 근거 없음(모델은 "에스컬레이션"·소문자 인용) → 제거, (2) **상태값 anti-anchor는 구조적으로 사용 불가** — 올바른 실행일수록 복구 후 목표 상태(`scope-integrity: match (scope 2 → touched 2)`)를 처방하므로 `output_not_contains`가 정답을 떨어뜨린다 → positive-only anchor로 전환. 미고정 구간은 task description에 명시(잔존물 task는 "batch 4를 시작하지 않는다"를 substring으로 붙들 수 없어, 복원·보고는 맞고 carry-over 위에서 재개하는 실행을 통과시킨다).
  - 채택 안 함: 리뷰어 수 축소(3→2). 리뷰어는 병렬이라 대기시간 = max(개별)이고 축소는 토큰만 줄이며 검출력을 깎는다.

## [0.20.0] - 2026-07-22

### Changed
- `nara-adversarial-review` — forge 하드닝 (EPT 프로브 검증):
  - code-review 계약 변경 sync: refuter에 non-runtime finding 재검증 규칙(사실 자체를 grep/read로), rigor auditor에 observability 루브릭 인지(suggestion의 E3-무실행경로는 위반 아님) + 신규 정상 status 값(`manual-only`, zero-fix `match`/`0,0,0`, empty-scope n/a) 등재.
  - 프로토콜 gap 규정화: refuted↔weakened 경계 규칙(path 불성립+실결함 → refuted+missed-found 재정식화·상호링크), missed-found 채택에 원 리포트 게이트 적용, `N missed-found`=채택분만 카운트, refuter 입력=confirmed+unadjudicated, manifest 부재 시 finding location 복원 허용, diff 미복원·rejected 섹션 부재 fallback.
  - 런타임 중립화("Agent tool" → "병렬 subagent") + SKILL↔protocol 모순 1건 해소(refuter 대상 범위).
- `nara-pr-review` — forge 하드닝 (EPT 프로브 검증):
  - PR-plane/code-plane 경계 규정: lane 산출물은 프로세스 평면 요약만(finding-schema 변환·dedup·Judge 비대상), lane 발견 코드 결함은 code-plane으로 이관 후 finding ID 참조(이중 보고 금지).
  - 리포트 구성 명문화(code-plane finding 섹션 + lane 요약 4 + trailing status), adjudication 준용 규칙(code-review 설치 시 adjudication.md), 수집 실패 시 부분 데이터 리뷰 금지(`❌ 실패:` 중단), receipt↔게시 초안 시점 분리, 재사용 목록에 routing 명시, ci 다중 실패 표기.
- `nara-code-review` — 리뷰 관점 15종 검토 후 14종을 기존 10 agent에 흡수(신규 agent 0 — 직교성 유지, 체크당 owner 1명):
  - 신규 섹션: deploy-window/시간축 호환(contracts, mixed-version·rollback deserialize) / business abuse(security, rate-limit·자원 독점) / failure aftermath(resilience, DLQ·재처리·수동 복구) / data lifecycle(resilience, cascade delete·soft-delete 누출) / i18n(frontend, 하드코딩 문자열·조사/복수형) / observability 심화(operations, 추적성·retry-vs-영구실패·alert actionability).
  - 라우팅 구멍 수리: 순수 코드의 신규 failure path(새 catch/외부 호출)도 operations-config 트리거.
  - context-map에 조건부 historical-context 단계(의문 guard/legacy 주석 → `git log -p`/`blame`).
  - P2 불릿: AC 완전성·temporal 경계(behavior), caller sweep 의무화(contracts), 과금 API(performance), mock fidelity(tests), add-without-delete·temp compat 기한(architecture), double-submit·dead-end 에러(frontend), 위험 기본값(operations).
- `nara-code-review` — skill-forge 5 iter (전부 kept):
  - 빈 스코프 정의: clean tree에서 base에 이미 머지된 커밋 재리뷰 방지(merge-base 가드) + fallback 순서 + n/a trailing status 규정.
  - `manual-only` 수렴 라벨 신설(confirmed 잔존이 전부 R2/R3) + fix 0건 시 trailing status 규칙(`match`/`0,0,0`, n/a는 `--fix=none` 전용).
  - description에 DO NOT redirect 추가: production incident root-cause → nara-incident (토큰 패리티 1097→1096).
  - routing.md 런타임 중립화("Agent tool" → "parallel subagents").
  - eval 수리: 구 5-agent 체계 잔재 assertion("High") 및 과광폭 not_contains("요구사항") 교정.
- `nara-code-review` — forge 2라운드 (iter 6–8, 전부 kept):
  - non-runtime finding 시맨틱 정립: 관측 가능한 불일치(rename leftover·중복 util·dead code)는 유효한 suggestion finding — E레벨을 "주장 사실의 관측가능성"으로 재해석(E3=repo 검증, E2=diff 도출), E2 게이트 동일 적용. suggestion의 failure_path는 비용 경로(drift·혼동)로 서술.
  - 부기 명확화: policy-excluded(suggestion·R3)는 auto-fix candidate 아님(Judge 스킵 근거), 통계표 `-(unadjudicated)` 표기 + fingerprint 병합 집계 규칙, zero-fix 런은 validation 실행 의무 없음(실행된 것만 보고).
  - `--staged` 스코프 옵션 신설(커밋 직전 staged만) + NL 매핑("staged만" 요청 시 플래그 없이 적용) + staged manifest 시맨틱(head=index) + 제외 dirty 파일 고지.

## [0.19.0] - 2026-07-22

### Fixed
- workflow-core 스킬 결함 일괄 수정 (darwin-skill 최적화 + 독립 adversarial 검증):
  - `nara-reflect` — handoff.md 통째 덮어쓰기 + 기존 handoff 미읽음으로 인한 **교차세션 데이터 손실** 수정 (§1 carry-forward + §3 merge). memory frontmatter의 phantom "글로벌 CLAUDE.md 스키마 일치" 주장 제거. 타깃 충돌 tiebreaker(prescriptive→CLAUDE.md / descriptive→memory) + preview CHECKPOINT.
  - `nara-gap` — score 공식 div-by-zero(전 항목 Agreed Exception) 가드 + `N/A` gate 분기 + Needs Confirm/Unknown deflation 명문화.
  - `nara-ac-draft` — `docs/requirements.md` 무가드 덮어쓰기(prep 산출물 clobber = 데이터 손실) 가드 추가 + self-rerun AC-ID 안정성.
  - `nara-rfc` — "Output ONLY RFC Markdown" 룰 ↔ interview/파일저장 스텝 모순 해소 (파일-내용 계약으로 rescope).
  - `nara-workflow-doc-mode` — clear-path frontmatter↔body 순서 모순 + prep-role mismatch(prep는 grill 산출 persist 불가) 수정, AC 기록 타깃 명시.
  - `nara-workflow-orchestrator` — "now" 트리거 `nara-now` 충돌 제거, scope dead-code 제거, 라우팅 표 중복 제거(SKILL.md=SoT).
  - `nara-workflow-dev-mode` — frontmatter spine ↔ body core spine drift 수정 (TDD를 execute 옵션으로 정정).

### Changed
- `nara-plan` — 수직 분할 6-step 절차 추가 (기존엔 계약+템플릿만 있고 분할 알고리즘 부재).
- `nara-adr` — Error Handling if-then 분기 추가 (context 부족/seq 충돌/supersede 누락/source 부재/routine 거부/중복).

### Fixed (non-core 스킬 defect batch — triage 후 real-defect 9건, 독립 adversarial 검증)
- `nara-now` — 버려진 `claude-mem` 참조를 memory 도구(engram 등)로 교체 (SKILL step5 + `now-tables.md`). 세션 진입 스킬의 메모리 arm이 조용히 죽어 있던 것 수정.
- `nara-pr-respond` — 동료 PR 스레드 답글 **무단 auto-post** 방지: preview-default(draft→show→confirm→post) 게이트를 SKILL + `references/procedure.md`(실행 절차) 양쪽에 강제.
- `nara-review-reminder` — Multica 이슈 description의 리터럴 `\n`(백슬래시-n 렌더) → `printf` 실개행. fire-and-forget 자동화 계약 명시.
- `nara-local-shot` — 배포 시 미해결되는 `[[wiki-link]]` Obsidian 참조를 인라인 설명으로 교체.
- `nara-design-studio` — USE FOR 과광범으로 전용 팩 스킬과 라우팅 충돌 → `DO NOT USE FOR` redirect(팩-agnostic 엔진 vs 전용 팩) 추가.
- `nara-test-verify` — `nara-test-discover`(S2/S3 ID)와 `nara-golden-path-discover`(제목+step, ID 없음) 이중 스키마 misfire 수정: 스키마 감지 + 페르소나 프롬프트(`agent-prompts.md`) fence 내 Input-schema 주입 + dispatch 배선. NEEDS_WORK/FAIL remediation loop 명시.
- `nara-jira-drain` — launch 후 metadata를 무조건 `working`으로 flip하던 것 수정: launch 커맨드 exit 성공 시에만 mark, `working=launched(실행 확정 아님)` 세만틱, 오발은 다운스트림 `PR_RESULT` 부재로 감지.
- `nara-trending-digest` — self-renew가 (a) 중복 cron 생성(`CronCreate` dedup 없음) → `CronList→Delete→Create`, (b) crawl 성공에 묶여 crawl 실패 시 스케줄 death → **Step 0**(crawl 전, ungated)로 이동. off-minute cron. fire-and-forget 계약.
- `nara-golden-path-discover` — 다운스트림 `nara-test-verify`가 golden-path 스키마를 파싱 못하던 문제 해결(test-verify 스키마 분기로; producer 측 변경 없음).

## [0.18.0] - 2026-07-22

### Added
- `nara-local-shot` — 로컬 실행 웹앱(SSO-gated 포함) 스크린샷 캡쳐+파일 저장 스킬. PR Before/After visual comparison·UI 검증용. 핵심: dev 서버 + chrome-devtools MCP로 직접 캡쳐(placeholder만 남기지 않음), 세션 없는 자동 브라우저는 더미 쿠키로 우회 — presence-only 미들웨어 + `.ico` matcher 트릭 + API-free 격리 프리뷰 전제. `references/auth-bypass.md`(메커니즘·httpOnly caveat·real-storageState fallback), `references/프로젝트별 레시피(구체값은 소비 repo 소유). nara-ui-diff(env-diff)와 스코프 구분.

- `nara-pr-review` — 원격 PR evidence-based 리뷰 (gh 기반, 체크아웃 없음). 코드 평면(nara-code-review 리뷰어 체계 재사용, 미설치 시 lane 요약 fallback) + PR 평면 4 lane(description↔diff 정합 / commit 구성 / CI 신호 / discussion 커버리지). 리포트 우선, 코멘트 게시는 finding 단위 승인 후에만 — approve/request-changes는 항상 사람.
- `nara-adversarial-review` — 기존 리뷰 리포트 공격 검증: refuter(finding 격추 시도) + blind hunter(리포트 미열람 재리뷰 후 대조) + rigor auditor(evidence level·proof·trailing status 무결성). 원 리포트에 append-only. `/codex:adversarial-review`의 네이티브 대안 (의존+fallback).

### Changed
- `nara-grill` — design-review 흡수: 설계 대상(구현 전 설계·대규모 리팩터링·API 설계·모듈 경계)일 때 `references/design-probes.md` 압박 축(경계·소유권 / API 계약 / 변경 비용·롤백 / 규모·실패 모드 / 코드베이스 정합) 사용. USE FOR에 "설계 리뷰"/"design review" 등 추가. 코드 diff 존재 시 code-review로 리다이렉트 명시.
- `nara-code-review` — **전면 재설계: 고정 5-agent → Evidence-based Reviewer→Judge→Fixer→Verifier 파이프라인.**
  - 리뷰어 직교화: 코어 4 (behavior-state / contracts-compatibility / resilience-data-integrity / tests-regression) + 조건부 6 (security-privacy / performance-resources / architecture-reuse / frontend-ux-a11y / database-migration / operations-config, 변경 내용 트리거 라우팅). security-performance 분리, cross-cutting 공통 체크리스트 해체(항목별 주 담당 agent 지정) — 공통 주입은 Universal Reviewer Contract만.
  - Evidence Level(E0–E3) 도입: 최종 finding 조건 = `evidence >= E2 AND confidence >= threshold`. E1 이하는 "미검토 리스크/확인 질문"으로 분리. confidence 구간 기준 명문화.
  - Finding 스키마 강제: invariant / preconditions / failure_path / counterevidence_checked / validation 필수, fingerprint = path+symbol+invariant (라인 넘버 아님).
  - 역할 분리: read-only Reviewer → blind Judge(원 confidence·proposed fix·중복발견 은닉, critical/major·보안·auto-fix 후보·충돌 필수 심사) → 중앙 단일 Fixer(ledger 순 직렬) → 별도 Verifier.
  - Auto-fix 위험 등급 R0–R3 + `--fix=none|safe|selected|all` (기본 safe = R0+검증가능 R1). suggestion·R3는 어떤 모드에서도 자동 수정 금지.
  - Claimed-vs-Observed를 파일 단위 → issue 단위로 강화: 라운드 시작 hash 스냅샷 + hunk·validation proof, mismatch 3분류(claimed-but-unchanged / changed-but-unclaimed / changed-but-unresolved). 수정 시 최종 baseline 전체 diff 재리뷰 필수.
  - Scope 보완: dirty→staged+unstaged+untracked, clean→HEAD~1, 시작 시 review manifest 고정(외부 변경 = scope mismatch). Context에 변경 의도(spec) 수집 단계 추가, 없으면 `specification: unavailable` 명시.
  - Override 보완: Accepted exceptions 테이블(`suppressed-by-project-exception`) + override 내 임의 shell command 자동 실행 금지(프로젝트 정의 validation script만).
  - references 재구성: agents.md/phases.md/fix-loop.md/cross-cutting.md 삭제 → scope/context-map/routing/reviewer-contract/finding-schema/adjudication/fix-policy/verification/report + agents/*.md 10개.
- `nara-skill-forge` — Darwin Skill 메커니즘 이식 + darwin 9-dim 평가 루프 하드닝(baseline 75.8 → 독립 judge 실측 ~87). **회귀 래칫**(fix→재채점→prior-passing grader 회귀 또는 토큰 증가 시 워킹트리 복원, no-auto-commit 각색) + **runtime-neutrality gate**(single-runtime lock grep 스캔, `references/ratchet.md`·`runtime-gate.md`). description `Triggers on:`→`USE FOR / DO NOT USE FOR`(런타임 중립 "agent skill"), 🔴 CHECKPOINT/🛑 Benchmark-only/🛑 최종 STOP 게이트. **Phase 2 결과 포맷 사실 오류 수정**(flat 리스트는 `waza grade` 거부 → `waza run` mock-probe 스키마, 적대적 subagent 실증), **Phase 1 no-Copilot 기본화**(waza 결정적 절반 의존, LLM 절반은 실행 에이전트가 대체 — task 직접 저작, `waza suggest`는 Copilot 옵션), **grader-validation**(정답+오답 주입으로 hollow grader 폐기), **waza-absent degraded path**(dry_run 마킹, 점수 날조 금지), task당 two-run 채점, Reporting/results-schema를 `references/reporting.md`로 progressive disclosure, Troubleshooting if-then 3열 표.
- `nara-empirical-prompt-tuning` — description USE FOR에서 "스킬 개선" 제거, DO NOT USE FOR에 "스킬 개선/강화/벤치마크 → nara-skill-forge" 리다이렉트 추가. skill-forge와의 라우팅 충돌("스킬 개선해줘" 코인플립) 해소. README.md 동기.

## [0.17.0] - 2026-07-16

### Added
- `nara-implement` — 검증 게이트 구현 스킬 (전략 승인 → TDD 옵션(red→green) → verify → staged 정지). **자동 커밋 없음** (글로벌 no-auto-commit 룰 준수 → `/nara-commit` 위임). dev-mode `execute` 단계.
- `nara-grill` — 사실 조사 후 한 번에 한 질문씩 설계 검증 (침묵≠동의). dev/doc 설계 탐색 satellite.
- `nara-plan` — 스펙을 독립 검증 가능한 수직 작업 단위로 분할 → `docs/plan.md`. dev-mode `plan` 단계.
- 세 스킬 모두 4-state verdict(`Pass | Fail | Blocked | Unverifiable`) + "미실행/미확인은 통과 보고 금지" 하네스 채택.

### Changed
- **superpowers 의존 전부 제거** — nara-kit이 이제 superpowers 없이 완결.
  - design exploration `superpowers:brainstorming` → `nara-grill`
  - plan `superpowers:writing-plans` → `nara-plan`
  - execution(SDD/TDD) `superpowers:subagent-driven-development` + `test-driven-development` + `executing-plans` → `nara-implement`
  - branch finish `superpowers:finishing-a-development-branch` → dev-mode 내 네이티브 git 시퀀스
  - `superpowers:receiving-code-review` 원칙 → `nara-pr-respond` 본문 인라인
  - 남은 외부 참조는 `codex:adversarial-review`(선택) 하나뿐.
- `nara-incident` — red-capable feedback-loop gate 추가 (재현 없이 가설 "유력" 금지, `Blocked`/`Unverifiable` 상태 도입).
- dev-mode/doc-mode/orchestrator 라우팅을 네이티브 스킬로 재배선. 스킬 수 41 → 44.

### 출처
- `github.com/MTGVim/tiger-kit` v19 (mattpocock/skills=superpowers 계보의 vendor-neutral fork)에서 `tk-implement`/`tk-grill-me`/`tk-to-tickets`/`tk-diagnosing-bugs` 패턴을 나라화해 흡수.

## [0.16.0] 및 이전

이 CHANGELOG 도입(위 Unreleased) 이전의 릴리즈 기록은 git tag와 커밋 로그에 있다:

```sh
git tag --sort=-creatordate      # v0.16.0 … v0.11.3
git log <prev-tag>..<tag> --oneline
```

주요 마일스톤: 플러그인 → Agent Skills 포맷 전환(`nara-` prefix, hooks 제거), naranizer/humanizer, release-prep/finalize, ui-diff, jira-triage/drain 등.
