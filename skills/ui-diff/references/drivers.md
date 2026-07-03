# drivers — MCP-first 사다리

env-diff는 **연결된 MCP 서버에 의존**한다. raw CDP를 primary로 nativize하지 않는다.

## 우선순위

| Rung | Driver | 언제 |
|------|--------|------|
| 1 (primary) | **chrome-devtools MCP** | 기본. 특히 baseline과 target이 **같은 도메인**일 때 (isolatedContext로 쿠키/스토리지 격리) |
| 2 | **playwright MCP** | 단일 환경이거나 QA/Prod가 **다른 도메인**일 때(격리 무의미), 또는 snapshot uid churn이 심할 때. raw CSS selector가 더 편함 |
| 3 (탈출구) | raw CDP | **MCP 미연결 시에만.** unsupported 최후 수단 — 아래 |

> **왜 golden-path-discover와 우선순위가 다른가**: `golden-path-discover/references/live-crawl.md`는 Playwright primary(chrome-devtools는 "DOM snapshot 지향, selector 지향 아님"). env-diff는 반대로 chrome-devtools primary — **같은 도메인 두 환경(QA vs 로컬)을 한 브라우저에서 쿠키 안 섞고** 여는 게 핵심 요구인데, playwright `browser_tabs`는 브라우저 컨텍스트 1개를 공유해 per-tab 격리 파라미터가 없다. 이 격리는 chrome-devtools `new_page({isolatedContext})`만 native 지원. 의도된 divergence — 목적이 다름.

## chrome-devtools 시퀀스 (per runtime)

1. **open (격리)** — 시딩이 필요하면 `new_page({url:'about:blank', isolatedContext:'baseline'|'target'})` 먼저 → `navigate_page({type:'url', url:<runtime url>, initScript:<seed token/flag>})`. `initScript`는 **다음 navigation의 페이지 스크립트 전에** 실행되므로, `new_page({url})`로 바로 열면 첫 문서엔 너무 늦음. 쿠키/스토리지 시딩이면 격리 컨텍스트에 set 후 navigate.
2. **viewport 통일** — `emulate({viewport:'<w>x<h>x<dpr>'})`로 **DPR 포함** 일치. `resize_page`는 width/height만 — DPR 안 바뀜.
3. **런타임 선택** — `list_pages`로 각 런타임의 **숫자 pageId** 획득 → `{runtime→pageId}` 맵 저장 → `select_page({pageId:<number>})`로 전환. **`select_page`에 isolatedContext 문자열('baseline') 넘기지 말 것** — isolatedContext는 쿠키 격리용, pageId는 활성 페이지 선택용(별개).
4. **로그인** — `take_snapshot` → `fill_form`(uid로 batch) → `click` submit → `wait_for`(post-login marker). DOM 바뀌면 re-snapshot (chrome-devtools 타깃은 uid 기반).
5. **측정** — `evaluate_script`에 [env-diff.md](modes/env-diff.md) 직렬화 snippet. 반환은 JSON-serializable만 — raw style/rect는 `{}`.

## playwright 시퀀스

`browser_navigate({url})` → `browser_snapshot`(rect만 필요하면 `{boxes:true}`로 getBoundingClientRect 직접 획득 가능, computed-style은 여전히 evaluate 필요) → `browser_fill_form`/`browser_type` + `browser_click`(raw CSS selector 허용) → `browser_wait_for` → `browser_evaluate`(같은 직렬화 계약). **DPR 주의**: `browser_resize`도 width/height만 — DPR parity 필요한데 playwright만 있으면 **parity 한계 honesty note** 남기고 진행(조용히 진행 금지).

> `browser_run_code_unsafe`(full page object, RCE 상당)는 **사용 안 함**. env-diff 측정(getComputedStyle/rect 직렬화)엔 불필요.

## raw CDP 탈출구 (unsupported)

MCP driver가 **하나도** 없을 때만. 전용 WebSocket 러너를 만들지 않는다 — 사용자에게 Chrome을 `--remote-debugging-port=9222 --user-data-dir=<디버그 프로필>`로 띄우도록 안내하고, raw CDP는 **unsupported 최후 수단**임을 receipt에 명시(driver: `cdp-direct` + "unsupported/last-resort" 마커). 디버그 프로필 dir은 인증 세션 쿠키가 디스크에 남으므로 **gitignore된 경로**(`.claude/ui-diff/runs/<ts>/chrome-profile/`) 아래에 둘 것. **MCP가 하나라도 연결돼 있으면 happy path에서 cdp-direct 선택 금지.**
