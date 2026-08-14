# 축별 필수 증거 매트릭스

판정의 단위는 criterion이 아니라 **축**이다. 축마다 무엇이 증거로 인정되는지 고정돼 있고, 다른 종류로 대체할 수 없다.

## 매트릭스

| 축 | 필수 증거 (primary) | 보조 | 대체 불가 |
|---|---|---|---|
| **geometry / layout** | `getBoundingClientRect` + computed `position`/`margin`/`padding`/`gap` | 스크린샷 | 눈대중 "비슷해 보임" |
| **typography** | computed `font-family`(실제 loaded)/`font-size`/`line-height`/`letter-spacing` | 스크린샷 | 소스 CSS 선언값 (로드 실패·fallback을 못 봄) |
| **color / paint** | computed `color`/`background`/`border`/`fill`/`stroke`/`opacity`/`shadow` | 스크린샷 | 디자인 토큰 값 (적용됐는지 증명 못 함) |
| **asset presence / integrity** | **실제로 열어본 스크린샷** + 리소스 로드 성공 | computed | DOM에 element가 있다는 사실 (`<svg>` 존재 ≠ 렌더됨) |
| **imagery** | **실제로 열어본 스크린샷** + image request 성공·intrinsic dimensions·`object-fit` | computed | `src` 속성값 |
| **전체 렌더 / 시각적 인상** | **실제로 열어본 스크린샷** | — | DOM·accessibility tree |
| **behavior / mutation** | trusted input + 관련 **network request와 response** | 최종 UI 상태 | toast·local DOM 변화·응답만 (셋 다 단독 불충분) |
| **a11y focus / keyboard** | trusted `Tab`/`Enter`/`Escape`/arrow 입력 + **표시된 focus 스크린샷** | accessibility tree | `document.activeElement` 값만 (표시된 focus를 증명 못 함) |
| **responsive / state** | 승인된 viewport마다 위 축 재측정 (`window.innerWidth` 실측) | — | breakpoint 소스값 |

## 판정 규칙

- 축마다 `Pass | Fail | Unverifiable` 하나를 기록한다.
- **필수 증거가 없는 축은 자동 `Unverifiable`.** 보조 증거만으로 Pass 금지.
- **한 축이라도 `Unverifiable`이면 aggregate `Pass` 금지.** aggregate는 `Fail`(위반 있음) 또는 `Unverifiable`(위반은 없으나 미확인 축 존재)이 된다.
- criterion과 무관한 축은 검사하지 않는다 — "검사 안 함"과 "Unverifiable"을 구분해 적는다. 범위 밖 축은 `해당 없음`.
- 각 발견 사항에 축·named element/region·관찰값·viewport/state·검사한 스크린샷 경로를 붙인다.

## 7축 verbatim 비교 (승인된 reference가 있을 때만)

디자인 시안이나 승인된 기준 스크린샷과 "그대로인가"를 비교하라는 criterion에서만 적용한다. reference와 candidate를 **같은 viewport·DPR·zoom·폰트 로딩 완료 상태**에서 각각 캡처해 실제로 열어본 뒤, 아래 7축을 각각 기록한다.

1. **Asset presence/integrity** — logo·SVG·icon·favicon·raster·background 누락/대체/중복. SVG는 element 존재가 아니라 rendered shape·`viewBox`·aspect ratio·fill/stroke·clipping으로 확인.
2. **Content** — 표시 text·label·숫자·badge와 그 **순서**.
3. **Geometry/layout** — position·dimension·spacing·alignment·radius·border·overlap·clipping·wrapping·crop.
4. **Typography** — loaded font family/fallback·weight·rendered size·line-height·letter-spacing·text-transform·줄바꿈.
5. **Color/paint** — foreground/background/border·SVG fill·stroke·opacity·shadow·gradient.
6. **Imagery** — request/load 성공·source·intrinsic dimension·aspect ratio·`object-fit`/`object-position`·crop·해상도.
7. **Responsive/state** — 승인된 viewport와 hover/focus/active/disabled/loading/error 상태마다 위 축 재확인.

규칙: **하나라도 unchecked이면 aggregate `Pass` 아님.** pixel-perfect tolerance가 승인 criteria에 없으면 임의 threshold를 만들지 말고, 명백한 mismatch만 보고하고 미세차는 `Unverifiable`로 남긴다. 차이는 `defect` / 승인된 deviation / 환경 / `unverifiable`로 분류하며, design intent를 만들거나 일반 critique로 넓히지 않는다.

## 회귀 주장

"이전에는 됐는데 깨졌다"는 주장에는 **비교 가능한 baseline 런타임 증거**가 필요하다. 없으면 현재 관찰된 실패만 보고한다. baseline이 실제로 배포돼 있고 환경 비교가 목적이면 이 스킬이 아니라 `nara-ui-diff`다.
