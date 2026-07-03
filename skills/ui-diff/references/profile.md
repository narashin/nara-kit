# profile — `.claude/ui-diff/` 스키마 + bootstrap + 크레덴셜

Engine/profile 분리: 스킬 = 엔진(절차+템플릿), 모든 제품값 = **소비 repo의 `.claude/ui-diff/`**.

## Lookup + bootstrap

1. `<repoRoot>/.claude/ui-diff/` 있으면 로드
2. 없으면 `skills/ui-diff/references/templates/`에서 repo-local로 생성 후 **중단** — "env.md 채우고 `login.local.md.example` → `login.local.md` 복사" 안내. 엔진은 repo-local 파일만 생성(user-global provisioning 금지)

## 파일

### `.claude/ui-diff/env.md` (tracked, non-secret)
4섹션: **local**(local_url, local_dev_cmd, local_ready_signal, notes) · **baseline**(baseline_url = qa/staging/prod-like, notes) · **viewport**(width, height, device_scale_factor) · **auth/context**(requires_login, default_user_role, seed_or_fixture, context_notes = feature-flag/locale/org-selector). endpoint+viewport+context parity의 단일 소스.

### `.claude/ui-diff/login.md` (tracked, non-secret)
selector만: username/password/submit/post_login_ready/optional_modal_close + 4단계 flow + 2FA/captcha/SSO blocker note. **비밀값 0.**

### `.claude/ui-diff/screens/<name>.md` (tracked, per screen)
고정 skeleton: Goal / Entry(start URL + nav·click·tab·modal open) / Data-Context(account·fixture·flag) / Selectors(container·compare-target·ready signal) / Known pitfalls(sticky header·lazy load·animation·overlay) / Regression notes(과거 깨진 지점). Step 5에서 소비.

### `.claude/ui-diff/runs/<ts>/` (gitignore 권장)
run artifact: 양쪽 full computed dump, diff 표, driver/session log, 선택 스크린샷, (raw-CDP 시) chrome-profile. **소비 repo `.gitignore`에 `.claude/ui-diff/runs/` 추가 권고.**

## 크레덴셜 모델 (golden-path canon 준수)

우선순위:

1. **SSO / 쿠키 게이트 앱 → storageState (권장, golden-path와 동일)**: 사용자가 **1회 사람 손으로** 로그인(agent가 타이핑 안 함), 세션을 gitignore된 storageState 파일로 저장, 이후 **파일명으로만 재사용**. raw 토큰은 채팅/artifact를 절대 통과 안 함. (`golden-path-discover/references/live-crawl.md`의 SSO 패턴 그대로.)
2. **비-SSO form 로그인 → `login.local.md` (opt-in, 더 약함)**: 사용자가 **명시적으로 opt-in**할 때만 `login.local.md`의 크레덴셜을 form에 채운다. 이건 storageState보다 **보안적으로 약한** 경로 — golden-path와 "동등"이 아님. 규칙: (a) 타이핑한 값 절대 echo 금지, (b) receipt·artifact·log 어디에도 안 남김, (c) 약한 경로임을 사용자에게 고지.

공통 하드 룰:
- 크레덴셜은 gitignore된 `login.local.md`(또는 storageState 파일)에만. `login.md`엔 selector+flow만.
- 스킬은 `login.local.md.example`(placeholder)만 ship. 사용자가 복사해 실값 기입.
- **Step 0에서 `git check-ignore .claude/ui-diff/login.local.md` 확인** — ignore 안 되면 ESCALATE + 진행 거부(커밋 위험).
  - 루트 `.gitignore`의 `*.local.md`가 `login.local.md`는 매치(ignored), `login.local.md.example`은 non-match(tracked) — 템플릿은 커밋 가능, 실크레덴셜 파일은 불가.
- 크레덴셜은 **어디에도 출력 안 함** — auth는 파일명으로만 참조.

## 피드백 루프 (reflect 라우팅 미러)

run 중 학습한 friction을 알맞은 durable surface로: 화면별 지식 → `screens/<name>.md` Known-pitfalls/Regression-notes · 로그인/context 변화 → `login.md`/`login.local.md`/`env.md` · 제품-무관 엔진 교훈 → 이 스킬 SKILL.md/references. 한 번 맞은 friction이 재발하지 않게.
