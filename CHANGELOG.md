# Changelog

nara-kit의 모든 주요 변경을 기록한다. 형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/),
버전은 [Semantic Versioning](https://semver.org/lang/ko/)을 따른다.

nara-kit은 매니페스트 없는 Agent Skills repo — `main` 브랜치가 곧 릴리즈이고 git tag가 immutable snapshot이다.
각 tag = 여기의 한 버전 섹션. tag가 없는 진행 중 변경은 `[Unreleased]`에 쌓인다.

호환성 규칙(major 판정): 스킬 이름 삭제·rename, invocation 방식 변경, 산출물 경로 변경은 consumer에게 breaking.

## [Unreleased]

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
- `nara-design-studio` — USE FOR 과광범으로 `lyris-design`과 라우팅 충돌 → `DO NOT USE FOR` redirect(팩-agnostic 엔진 vs LYRIS 전용 팩) 추가.
- `nara-test-verify` — `nara-test-discover`(S2/S3 ID)와 `nara-golden-path-discover`(제목+step, ID 없음) 이중 스키마 misfire 수정: 스키마 감지 + 페르소나 프롬프트(`agent-prompts.md`) fence 내 Input-schema 주입 + dispatch 배선. NEEDS_WORK/FAIL remediation loop 명시.
- `nara-jira-drain` — launch 후 metadata를 무조건 `working`으로 flip하던 것 수정: launch 커맨드 exit 성공 시에만 mark, `working=launched(실행 확정 아님)` 세만틱, 오발은 다운스트림 `PR_RESULT` 부재로 감지.
- `nara-trending-digest` — self-renew가 (a) 중복 cron 생성(`CronCreate` dedup 없음) → `CronList→Delete→Create`, (b) crawl 성공에 묶여 crawl 실패 시 스케줄 death → **Step 0**(crawl 전, ungated)로 이동. off-minute cron. fire-and-forget 계약.
- `nara-golden-path-discover` — 다운스트림 `nara-test-verify`가 golden-path 스키마를 파싱 못하던 문제 해결(test-verify 스키마 분기로; producer 측 변경 없음).

## [0.18.0] - 2026-07-22

### Added
- `nara-local-shot` — 로컬 실행 웹앱(SSO-gated 포함) 스크린샷 캡쳐+파일 저장 스킬. PR Before/After visual comparison·UI 검증용. 핵심: dev 서버 + chrome-devtools MCP로 직접 캡쳐(placeholder만 남기지 않음), 세션 없는 자동 브라우저는 더미 쿠키로 우회 — presence-only 미들웨어 + `.ico` matcher 트릭 + API-free 격리 프리뷰 전제. `references/auth-bypass.md`(메커니즘·httpOnly caveat·real-storageState fallback), `references/iris-ui-recipe.md`(iris-ui 구체값). nara-ui-diff(env-diff)와 스코프 구분.

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
