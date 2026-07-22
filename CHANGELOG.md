# Changelog

nara-kit의 모든 주요 변경을 기록한다. 형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/),
버전은 [Semantic Versioning](https://semver.org/lang/ko/)을 따른다.

nara-kit은 매니페스트 없는 Agent Skills repo — `main` 브랜치가 곧 릴리즈이고 git tag가 immutable snapshot이다.
각 tag = 여기의 한 버전 섹션. tag가 없는 진행 중 변경은 `[Unreleased]`에 쌓인다.

호환성 규칙(major 판정): 스킬 이름 삭제·rename, invocation 방식 변경, 산출물 경로 변경은 consumer에게 breaking.

## [Unreleased]

### Added
- `nara-local-shot` — 로컬 실행 웹앱(SSO-gated 포함) 스크린샷 캡쳐+파일 저장 스킬. PR Before/After visual comparison·UI 검증용. 핵심: dev 서버 + chrome-devtools MCP로 직접 캡쳐(placeholder만 남기지 않음), 세션 없는 자동 브라우저는 더미 쿠키로 우회 — presence-only 미들웨어 + `.ico` matcher 트릭 + API-free 격리 프리뷰 전제. `references/auth-bypass.md`(메커니즘·httpOnly caveat·real-storageState fallback), `references/iris-ui-recipe.md`(iris-ui 구체값). nara-ui-diff(env-diff)와 스코프 구분.

### Changed
- `nara-skill-forge` — Darwin Skill의 두 메커니즘 이식(reference-모듈 리팩터): **회귀 래칫**(fix→재채점→prior-passing grader 회귀 또는 토큰 증가 시 워킹트리 복원, no-auto-commit에 맞춰 각색) + **runtime-neutrality gate**(Claude Code/Codex 양쪽 배포 대비 single-runtime lock grep 스캔). 세부는 `references/ratchet.md`·`references/runtime-gate.md`로 분리. body 리팩터로 waza advisory 통과(links 0→5, module-count 0→2, body-structure ❌→✓).
- `nara-skill-forge` — Darwin 9-dim 평가 루프 3라운드 적용(75.8→82.7): **Phase 2 결과 JSON 포맷 사실 오류 수정**(문서화된 flat 포맷이 `waza grade`에서 거부됨 → `waza run` 스키마 mock-probe 방식으로 교체, 적대적 subagent 실증), description `Triggers on:` → `USE FOR / DO NOT USE FOR` 전환(waza Compliance Low→Medium-High, 한글 "스킬 개선해줘" 트리거 추가, "Claude Code skill"→"agent skill" 런타임 중립화), 🔴 CHECKPOINT(Phase 3→4 승인 게이트)·🛑 Benchmark-only 분기·🛑 최종 STOP·iteration별 리포트 강제 추가. README.md 동기 재생성. 2차 라운드(→88.6): **Phase 1 no-Copilot 기본화**(waza 결정적 절반 check/grade/new-eval/mock은 의존, LLM 절반은 실행 에이전트가 대체 — task 직접 저작 기본, `waza suggest`는 Copilot 있을 때 옵션으로 강등, deterministic text/code grader만), Phase 5 cutoff 스케일 명시(`overall_score`/`aggregate_score` 0-1), 중복 규칙 3건 dedup, runtime-gate.md self-exclusion 각주(자기-오탐 차단), 벤치마크-only 분기를 CHECKPOINT 앞으로 재배열, "never authenticate Copilot" 명문화. 3차 라운드(독립 judge 실측 ~86-88, 자기추정 낙관편향 교정): **grader-validation 단계**(모든 grader를 정답+오답 주입으로 검증 — pass-both/fail-both false proxy는 Phase 2 전 폐기; ratchet가 hollow grader 위에 서지 않도록), **waza-absent degraded path**(CLI 없거나 깨지면 수동 audit+수동 grader, dry_run 마킹 — 점수 날조 금지), task당 **two-run 채점**(불일치=unresolved, 채점 노이즈 완화), Reporting/results-schema를 `references/reporting.md`로 progressive disclosure, Troubleshooting을 if-then 3열(trigger/first-fix/fallback) 표로 승격.
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
