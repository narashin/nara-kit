# Changelog

nara-kit의 모든 주요 변경을 기록한다. 형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/),
버전은 [Semantic Versioning](https://semver.org/lang/ko/)을 따른다.

nara-kit은 매니페스트 없는 Agent Skills repo — `main` 브랜치가 곧 릴리즈이고 git tag가 immutable snapshot이다.
각 tag = 여기의 한 버전 섹션. tag가 없는 진행 중 변경은 `[Unreleased]`에 쌓인다.

호환성 규칙(major 판정): 스킬 이름 삭제·rename, invocation 방식 변경, 산출물 경로 변경은 consumer에게 breaking.

## [Unreleased]

### Added
- `nara-design-studio` — **DESIGN.md → 팩 변환기** `assets/runtime/designmd_to_pack.py`. DESIGN.md(Stitch format) frontmatter는 color role set·typography scale·spacing·radii·컴포넌트 스타일 스펙을 이미 담고 있어 **번들 starter 팩(T1, 토큰 23개·컴포넌트 0)보다 토큰 표면이 넓다** — 산문으로 읽지 말고 팩으로 변환한다. `components:` 블록이 있으면 **T2**(각 항목이 마운트 가능한 standalone JSX + `_ds_bundle.js`), 없으면 T1.
  - **authored / derived 분리.** 엔진 크롬이 요구하지만 DESIGN.md가 정의하지 않는 토큰(`--ds-primary-hover`, ink 램프, `--ds-radius-200`, `--ds-shadow-popover` 등)은 `tokens.css`의 별도 주석 블록으로 emit + stdout 리포트. 매핑 가능한 role이 없으면 `MISSING` + exit 1 — 추론값이 authored 값과 섞이지 않는다.
  - **리터럴은 컴포넌트 스코프 토큰으로 승격.** DESIGN.md `components:`가 geometry를 리터럴로 적으므로(`padding: 12px 24px`) 그대로 인라인하면 팩 자신이 adherence 규칙을 위반한다 → `--ds-comp-<name>-<prop>`로 뽑고 JSX는 `var()`만 참조.
  - pyyaml 있으면 사용, 없으면 stdlib 파서로 폴백 — **새 의존성 0**.
- `nara-design-studio` — **emit-time adherence 게이트** `assets/runtime/check_adherence.py`. baseline 규칙 "tokens only — no hardcoded brand values"는 산문으로는 강제 불가(`padding: 16px`가 적힌 시점에 이미 위반)라 기계 검사로 전환. 기본 규칙 2개(raw hex / allowlist 밖 raw px, `1px` hairline은 허용)는 팩 협조 없이 동작, 위반 시 exit 1 + 라인 리포트. 인라인된 `:root { … }` 블록은 면제(`SKILL.md` §5가 portable single-file export에 토큰 블록 인라인을 지시하므로 그것은 정의부지 하드코딩이 아니다). 팩은 매니페스트 `adherenceConfig`로 규칙을 조일 수 있다.
- `nara-design-studio` — **그린필드 분기**(`SKILL.md` §2.1–2.2). 팩 tier는 "DS가 있나"만 답하고 "IA가 있나"는 아무도 묻지 않아, `startingPoints` 없는 팩에서 화면마다 nav·컬럼·상태값이 재발명되고 화면 2개째부터 일관성이 사라지던 문제. `manifest.startingPoints` 공백 여부로 **자동 판정**(유저에게 묻지 않음)하고, 보이는 IA(nav 형태·페이지 골격)는 기존 layout-direction candidate가 갈리는 축으로 흡수, 안 보이는 IA(상태 enum·정렬 기본·row 클릭 의미)는 후보 비교가 무의미하므로 기본값 통보 + 거부권. 확정된 화면은 팩 `startingPoints`로 **write back**해 다음 빌드부터 브라운필드로 수렴시킨다.

- `nara-jira-triage` — Step 7 `reconcile` 계약 명문화: 큐 이슈 상태를 **PR 실측**으로 되돌리는 전이 규약(strict KEY 경계 매칭 후 `MERGED`→`done`+`drain_state=done`, `OPEN`→`in_review`, 다건·미머지 close는 무변경+경고)과 증거 우선순위(PR 실측 > Jira 상태 > `pr_url` metadata — 후자는 KEY 검증 없이 심겨 오염 가능, 근거 아님)를 선언. `gh pr list --search`가 fuzzy라(`PROJ-40` 질의에 PROJ-39/29 혼입) 경계 매칭 `(^|[^A-Za-z0-9])<KEY>([^0-9]|$)` 필수.
  - **실행은 이 스킬이 하지 않는다** — 결정론(LLM 판단 0)이라 out-of-band 크론 스크립트 소유. 역할 분리 명문화: 오토파일럿=없는 것만 생성(classify에 LLM 필요) / 스크립트=있는 것만 상태 sync. Step 1~6 = 생성 전용.
  - 배경: 큐 `done` 전이가 jira-drain cleanup에만 있어 cleanup 미실행·큐 밖 손PR 건이 머지 후에도 `in_review`로 박제됨.

### Changed
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
- `nara-design-studio` — USE FOR 과광범으로 `brand-design`과 라우팅 충돌 → `DO NOT USE FOR` redirect(팩-agnostic 엔진 vs PRODUCT 전용 팩) 추가.
- `nara-test-verify` — `nara-test-discover`(S2/S3 ID)와 `nara-golden-path-discover`(제목+step, ID 없음) 이중 스키마 misfire 수정: 스키마 감지 + 페르소나 프롬프트(`agent-prompts.md`) fence 내 Input-schema 주입 + dispatch 배선. NEEDS_WORK/FAIL remediation loop 명시.
- `nara-jira-drain` — launch 후 metadata를 무조건 `working`으로 flip하던 것 수정: launch 커맨드 exit 성공 시에만 mark, `working=launched(실행 확정 아님)` 세만틱, 오발은 다운스트림 `PR_RESULT` 부재로 감지.
- `nara-trending-digest` — self-renew가 (a) 중복 cron 생성(`CronCreate` dedup 없음) → `CronList→Delete→Create`, (b) crawl 성공에 묶여 crawl 실패 시 스케줄 death → **Step 0**(crawl 전, ungated)로 이동. off-minute cron. fire-and-forget 계약.
- `nara-golden-path-discover` — 다운스트림 `nara-test-verify`가 golden-path 스키마를 파싱 못하던 문제 해결(test-verify 스키마 분기로; producer 측 변경 없음).

## [0.18.0] - 2026-07-22

### Added
- `nara-local-shot` — 로컬 실행 웹앱(SSO-gated 포함) 스크린샷 캡쳐+파일 저장 스킬. PR Before/After visual comparison·UI 검증용. 핵심: dev 서버 + chrome-devtools MCP로 직접 캡쳐(placeholder만 남기지 않음), 세션 없는 자동 브라우저는 더미 쿠키로 우회 — presence-only 미들웨어 + `.ico` matcher 트릭 + API-free 격리 프리뷰 전제. `references/auth-bypass.md`(메커니즘·httpOnly caveat·real-storageState fallback), `references/project-recipe.md`(webapp 구체값). nara-ui-diff(env-diff)와 스코프 구분.

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
