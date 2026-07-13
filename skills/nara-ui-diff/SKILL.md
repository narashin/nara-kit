---
name: nara-ui-diff
description: >-
  Env-diff visual regression check: drive a QA/Prod baseline and a local target through the SAME screen at the SAME viewport/auth/context, measure computed-style + getBoundingClientRect on both, report ONLY the differing values as drift candidates (human decides regression vs intended). Depends on chrome-devtools/playwright MCP.
  USE FOR: "ui-diff", "env diff", "환경 비교", "QA랑 로컬 비교해줘", "마이그레이션 후 디자인 안 깨졌나", "리팩터 전후 스타일 비교", "visual regression check", "computed style diff", "prod vs local UI".
  DO NOT USE FOR: figma-diff / design-node vs runtime (OUT OF SCOPE — future ui-diff mode, not built), golden-path E2E scenario authoring (→ nara-golden-path-discover), running/writing Playwright test code (→ nara-test-implement), code diff review (→ nara-code-review), pixel-screenshot-only "looks similar" checks (screenshots are supporting evidence only here).
---

# ui-diff — 환경 간 UI 회귀 비교 (env-diff)

UI 회귀 조사관. **배포된 QA/Prod 런타임(baseline)** 과 **로컬 dev 런타임(target)** 을 **같은 화면·같은 viewport·같은 auth/context**로 열어 computed-style + `getBoundingClientRect`를 양쪽에서 측정하고, **차이나는 값만 drift 후보**로 표면화한다. "비슷해 보이니 OK" 결론 금지, 자동 수정 금지 — regression인지 의도된 변경인지는 **사람이 판단**.

용도: 마이그레이션/리팩터 후 디자인이 그대로 유지됐는지 검증.

> **Scope = env-diff only.** figma-diff(design-node ↔ runtime)는 같은 `ui-diff` 우산 아래 **미구현 미래 모드** — `references/modes/`가 확장 seam. 여기서 figma 비교 시도 금지.

## 인자 ($ARGUMENTS)

`nara-ui-diff [--screen <name>] [--driver <auto|chrome-devtools|playwright>] [--props <csv>] [--screenshot] [--dry-run]`

| 인자 | 기본값 | 설명 |
|------|--------|------|
| `--screen <name>` | auto | `.claude/ui-diff/screens/<name>.md`. 1개뿐이면 자동 선택 |
| `--driver` | `auto` | MCP-first 사다리 (chrome-devtools → playwright). [drivers](references/drivers.md) |
| `--props <csv>` | 표준 후보셋 | 측정할 computed-style prop. [measure](references/modes/env-diff.md) |
| `--screenshot` | false | 위치/시각 **보조** 증거만 (primary 신호 아님) |
| `--dry-run` | false | dev 서버 기동·브라우저 open·쓰기 skip, 계획만 출력 |

## Core Rules

1. **측정 delta = 후보, 판정 아님** — AI는 의심 생성기, regression-vs-intended는 사람이 판단. 자동 수정·"버그/정상" 단정 금지.
2. **computed 증거가 판정 근거** — 스크린샷은 위치/시각 **보조 증거만** (`--screenshot`), primary 신호 아님.
3. **차이나는 prop만 인라인 보고** — 양쪽 full computed dump는 디스크 artifact, 채팅 인라인 금지.
4. **Parity 필수** — 같은 화면·viewport(width/height/**DPR**)·auth/role/flag/locale를 양쪽에 맞춘다. DPR은 `emulate`로만 설정 가능(`resize_page`는 크기만). parity 불가면 diff 무의미 — honesty note 남기고 clean regression으로 제시 금지.
5. **Engine/profile 분리** — 이 스킬은 절차+템플릿만. 모든 제품값(URL/login/context/screens)은 소비 repo의 `.claude/ui-diff/` profile. 없으면 템플릿에서 bootstrap 후 중단(user-global provisioning 금지).
6. **크레덴셜 격리** — tracked profile·artifact·response 어디에도 크레덴셜 금지. gitignore된 `login.local.md`에만(또는 storageState), **절대 출력 안 함**. [profile](references/profile.md)
7. **MCP-first 드라이버** — chrome-devtools(same-domain 격리) → playwright. MCP 없으면 raw CDP는 unsupported 탈출구(러너 안 만듦). 실제 사용 driver를 artifact에 기록. [drivers](references/drivers.md)
8. **직렬화 규율** — eval snippet은 `getComputedStyle`/`getBoundingClientRect` primitive를 plain object로 **직접 복사**. 두 MCP 다 raw CSSStyleDeclaration/DOMRect는 `{}`로 떨굼.
9. **receipt 먼저 → 중단** — artifact 쓰고 영수증 출력 후 정지(자동 체이닝 없음).

## Step 0 — Profile load + override

```bash
test -f .claude/overrides/ui-diff.md && cat .claude/overrides/ui-diff.md   # add/raise/narrow only, 없으면 silent skip
```

`.claude/ui-diff/{env.md, login.md, login.local.md, screens/<name>.md}` 로드. **없으면** `references/templates/`에서 repo-local로 bootstrap 후 **중단** — "env.md 채우고 `login.local.md.example` → `login.local.md` 복사" 안내 receipt. `git check-ignore .claude/ui-diff/login.local.md` 실패(=untracked 아님) 시 **ESCALATE**, 진행 거부.

## Auto-detect gate (human usability)

- `--screen` 없고 `screens/*.md` 정확히 1개 → 그것 사용
- `env.md`에 `baseline_url` 있고 로컬 dev 도달 가능 → 플래그 없이 진행
- scope→intensity: 단일 screen = 직행, 다수(`--screen all`) = per-screen 루프 + 진행 receipt
- 있는 신호(preview/QA URL, single-screen)가 공급 가능한 플래그는 강제하지 않음

## Procedure

[references/modes/env-diff.md](references/modes/env-diff.md)의 7단계 따름: (1) `env.md`로 로컬 dev 확인/기동 → (2) baseline+target을 동일 viewport(+DPR via `emulate`)로 open → (3) domain으로 런타임 식별 → (4) `login.md`+creds로 로그인, context 스위치(flag/locale/role) → (5) `screens/<name>.md`로 대상 화면 이동(real click + ready-signal) → (6) 양쪽 hand-serialized eval로 측정, **차이값만** 남겨 diff → (7) 선택 `--screenshot`. full dump+diff+driver log는 `.claude/ui-diff/runs/<ts>/`.

## Output (receipt)

```
UI env-diff 완료 (recorded only).
- screen: `<name>` · driver: `chrome-devtools` · viewport: `1440x900@2`
- drift candidates: `<N>`건 (top: `.cta` background-color #2b6→#39f · font-size 14px→16px)
- side effects: browser: 2 runtimes opened (baseline qa.example.com / target localhost:3000), 0 writes to app
- artifact: `.claude/ui-diff/runs/<ts>/diff.md` (+ full dumps, driver log)
- next: 유저가 각 candidate를 regression vs intended 판단
```

- status `recorded only` — 측정만, **버그/정상 판정 절대 안 함**
- browser/MCP 부수효과는 `side effects:` 줄에 명시(런타임 수 + 도메인 + `0 writes to app`)
- parity 불가 시 honesty note, drift를 clean regression으로 제시 금지
- drift 0건도 유효: `drift candidates: 0건 (parity confirmed)`
- `--dry-run` → status `skipped`(브라우저 open 안 함)
- 실패 시 `❌ 실패:` 블록

## Hallucination & Safety Guards

- 렌더값/selector/URL 창작 금지 — 측정 안 한 prop은 `[UNVERIFIED]`, 추측 px/hex 금지
- 크레덴셜을 artifact·response·driver log 어디에도 출력 금지 (auth는 `login.local.md` 파일명으로만 참조)
- parity-honesty gate: viewport/auth/context 못 맞추면 명시하고 clean signal로 제시 금지
- AI = 후보 생성기: "이건 버그"/"이건 정상" 금지 — "X만큼 다름, 사람 판단"만

## Standalone Mode

MCP 강화 optional + 수동 fallback. MCP driver 미연결 시 raw CDP(`--remote-debugging-port=9222`)는 **unsupported 최후 수단**(전용 러너 안 만듦 — [drivers](references/drivers.md)). 그마저 불가면 스타일 소스 정적 비교 + 모든 런타임값 `[UNVERIFIED: requires live runtime]`. **워크플로 스파인 아님** — NL/slash 트리거만, per-tool-call hook 없음.

## References

- [modes/env-diff.md](references/modes/env-diff.md) — 7단계 절차 + 측정 spec + figma seam
- [drivers.md](references/drivers.md) — MCP-first 사다리 + raw-CDP 탈출구 + nara-golden-path-discover 대비 우선순위 근거
- [profile.md](references/profile.md) — `.claude/ui-diff/` 스키마 + bootstrap + 크레덴셜 모델
- `references/templates/` — 소비 repo로 bootstrap되는 env/login/screens 템플릿
