# env-diff — 절차 + 측정 spec

배포 런타임(baseline: QA/Prod)과 로컬 런타임(target)을 같은 조건으로 열어 computed-style + rect를 측정, **차이값만** drift 후보로 남긴다.

> **figma-diff seam**: design-node ↔ runtime 비교는 이 우산의 미래 모드. `references/modes/figma-diff.md`가 생기면 거기. env-diff에서 figma 시도 금지.

## 7단계 절차

1. **로컬 dev 확인/기동** — `env.md`의 `local_dev_cmd`로 기동, `local_ready_signal` 대기. 이미 떠 있으면 재사용. `--dry-run`이면 여기서 계획만 출력하고 중단.
2. **양쪽 open (동일 viewport + DPR)** — baseline과 target을 각각 격리된 컨텍스트로 open. viewport는 `emulate({viewport:'<w>x<h>x<dpr>'})`로 **DPR까지** 맞춘다 (`resize_page`는 width/height만 — DPR 불일치는 모든 rect delta를 조용히 오염시킴). driver별 시퀀스 → [drivers.md](../drivers.md).
3. **런타임 식별** — 도메인으로 baseline/target 구분, `{runtime→pageId}` 맵 유지.
4. **로그인 + context** — `login.md` selector + 크레덴셜(storageState 재사용 우선, 아니면 `login.local.md` — [profile.md](../profile.md))로 로그인. `env.md`의 flag/locale/role context를 양쪽 동일 적용.
5. **대상 화면 이동** — `screens/<name>.md`의 entry(start URL + nav/click/tab/modal) 따라 이동. controlled input은 native setter, 클릭은 real mouse press+release, 필요 시 `scrollIntoView` + `elementFromPoint`로 overlay 가림 확인. ready-signal 대기 후 측정.
6. **측정 + diff** — 아래 측정 spec으로 양쪽 eval → 각 prop을 px/hex/opacity로 비교 → **baseline ≠ target인 행만** 남김. 일치 prop은 완전 생략.
7. **(선택) `--screenshot`** — 위치/시각 보조 증거. primary 아님.

full computed dump(양쪽) + diff 표 + driver log를 `.claude/ui-diff/runs/<ts>/`에 기록. 채팅엔 receipt만.

## 측정 spec

**표준 후보 prop셋** (`--props`로 override):
`width, height, padding, margin, background-color, opacity, border, border-radius, font-size, color, z-index` + `getBoundingClientRect`의 `x, y, width, height`.

**직렬화 계약 (필수)** — 두 MCP 다 raw `CSSStyleDeclaration`/`DOMRect` 반환값을 `{}`로 떨군다. eval snippet은 primitive를 plain 배열로 **직접 복사**:

```js
// 각 driver의 eval 도구 안에서 실행 (chrome-devtools evaluate_script / playwright browser_evaluate)
(selectors, props) => selectors.map(sel => {
  const el = document.querySelector(sel);
  if (!el) return { sel, missing: true };
  const cs = getComputedStyle(el);
  const r = el.getBoundingClientRect();
  const style = {};
  for (const p of props) style[p] = cs.getPropertyValue(p);   // 문자열 primitive
  return { sel, style, rect: { x: r.x, y: r.y, width: r.width, height: r.height } };  // 숫자 primitive
})
```

**비교 규칙**:
- 색은 hex/rgb 정규화 후 비교, 치수는 px, opacity는 float
- **scroll-lock 스크롤바 caveat**: 한쪽만 스크롤 잠금이면 뷰포트 폭이 스크롤바 너비만큼 차이 → `±(스크롤바 절반)` 범위 width 차이는 **width 변화가 아니라 position shift**로 해석
- 측정 안 된 prop = `[UNVERIFIED]`, 추측값 금지

**diff 표** (artifact `diff.md`, 차이값만):

| Selector | Prop | Baseline | Target | Δ type |
|----------|------|----------|--------|--------|
| `.cta` | background-color | #22bb66 | #3399ff | hex |
| `.cta` | font-size | 14px | 16px | px |

baseline == target인 prop 행은 아예 없음. 0건이면 "parity confirmed".
