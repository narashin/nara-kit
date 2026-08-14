# anti-cheat — 증거를 위조하지 않는 실행 규율

LLM이 브라우저 검증에서 흔히 치는 지름길과, 그것을 막는 규칙.

## 상호작용은 trusted input만

provider-native trusted pointer/keyboard API를 쓴다. 다음은 **상호작용 증거가 아니다**:

- `element.click()`
- `form.submit()`
- `dispatchEvent(new MouseEvent(...))` 및 동류의 합성 이벤트

이유: 합성 이벤트는 브라우저의 hit-testing·포커스 이동·기본 동작·이벤트 순서를 건너뛴다. 가려진 버튼, `pointer-events: none`, 비활성 상태, 겹친 오버레이가 전부 통과해 버린다. 사용자가 실제로 못 누르는 것을 "눌렀다"고 보고하게 된다.

`evaluate_script`는 **관찰 전용** — 상태·computed value·좌표를 읽을 때만 쓴다.

정확한 control을 못 찾으면 비슷한 label의 버튼을 반복 탐색하지 말고 mode·tab·scroll·toggle 상태를 먼저 inspect한다.

## mutation 주장에는 network 근거

"저장됐다 / 전송됐다 / 삭제됐다"는 주장에는 관련 **request와 response**가 필요하다. 다음은 각각 단독으로 불충분하다:

- toast 문구
- 로컬 DOM 변화
- 응답만 있고 UI transition을 안 본 경우

acceptance 판정은 **하나의 흐름 안에서** UI transition → request/response → 최종 UI 상태를 연결한다.

## 스크린샷은 찍는 게 아니라 보는 것

인용하는 스크린샷은 (1) 존재하고 (2) non-empty이며 (3) **실제로 열어봐야** 한다. 경로만 적고 내용을 안 본 스크린샷은 증거가 아니다. 디렉터리를 못 찾거나, 이미지가 없거나, 열어보기가 실패하면 그 축은 `Unverifiable`이다.

**툴이 보고한 경로를 그대로 믿지 않는다.** 실측(2026-08-14, playwright MCP): 허용 root 밖 절대 경로 저장은 거부되고, 상대 경로는 **작업 트리 루트 기준**으로 떨어진다 — 툴 응답의 경로 문자열과 실제 위치가 다를 수 있다. 저장 직후 존재와 크기를 확인한 뒤 그 절대 경로만 인용한다.

확인 명령 자체도 조용히 실패할 수 있다. zsh에서 매치 없는 glob(`ls dir/*.png`)은 `no matches found`로 **명령 전체를 중단**시켜, 실제로는 존재하는 다른 인자까지 검사되지 않은 채 "없다"로 읽히기 쉽다. 존재 확인은 glob 없이 정확한 경로로 하거나 `find`를 쓴다.

DOM·accessibility tree·network·computed-style로 시각 증거를 대체할 수 없다 (반대 방향도 마찬가지 — [evidence-matrix](evidence-matrix.md) 참조).

## 직렬화 규율

`getComputedStyle`/`getBoundingClientRect` 결과를 그대로 반환하면 **드라이버마다 다른 방식으로 망가진다** (2026-08-14 실측):

| 드라이버 | raw 반환 시 | 실패 모드 |
|---|---|---|
| chrome-devtools MCP | `{}` | 조용한 측정 실패 — 빈 값을 "측정했다"고 오인 |
| playwright MCP | CSS 속성 전량(1000줄+) 직렬화 | 컨텍스트 폭파 — 필요한 값이 노이즈에 묻힘 |

어느 쪽이든 증거로 못 쓴다. 필요한 primitive를 plain object로 **직접 복사**해서 반환한다.

```js
// evaluate in page: copy primitives explicitly, never return the live objects
const el = document.querySelector(sel);
const cs = getComputedStyle(el);
const r  = el.getBoundingClientRect();
return {
  color: cs.color, fontSize: cs.fontSize, backgroundColor: cs.backgroundColor,
  x: r.x, y: r.y, width: r.width, height: r.height,
};
```

빈 객체를 받고도 "측정했다"고 넘어가지 않는다 — 빈 반환은 측정 실패다. 반대로 거대한 dump를 받았으면 그것도 실패다: 필요한 키만 좁혀 다시 측정한다.

증거 파일 경로에도 드라이버 제약이 있다. playwright MCP는 **허용된 root(작업 트리 / `.playwright-mcp/`) 밖에 쓰지 못하고**, chrome-devtools MCP도 workspace root 밖 저장을 거부한다. 증거는 먼저 허용 경로에 쓰고, 필요하면 그 뒤에 옮긴다.

## 모션

CDP round-trip 스냅샷에 animation이 안 보인다고 없다고 추론하지 않는다. trigger **전에** `animationstart`/`animationend`/`transitionstart`/`transitionend`와 필요하면 `MutationObserver`를 등록하고, trusted 입력 뒤 하나의 event timeline을 확인한다.

synthetic DOM probe는 순수 CSS 계산에만 유효하다. framework mount/unmount lifecycle이 중요한 criterion이면 실제 component render cycle을 통한 재현을 검증한다.

## 필드 비우기

provider `fill(uid, "")`가 값을 실제로 지우는지 확인한다. empty fill이 no-op이면 nonempty 값을 넣은 뒤 trusted Backspace를 쓰거나, 필드 끝에서 문자 수만큼 Backspace를 보낸다. 저장 전에 빈 값을 다시 관찰한다.

## 조건부 상태와 다이얼로그

특정 API 상태에서만 나타나는 UI는 실제 전송·저장보다 `initScript` response mock을 우선한다. application이 실제로 parse하는 envelope에 맞춘다 — shape를 추측하지 말고 소스 mapping을 inspect한다. mock은 label하고 검증 후 제거한다.

상호작용 전에 native alert/confirm handler를 설치한다. 이미 열린 blocking dialog가 있으면 진행 전에 accept 또는 dismiss한다.

## parity

승인된 viewport·DPR·zoom·locale·role/flag를 재현한 상태에서만 측정값을 비교한다. DPR은 `emulate`로만 바뀐다 — `resize_page`/`browser_resize`는 width/height만 바꾼다. parity를 못 맞추면 honesty note를 남기고, 그 축을 clean signal로 제시하지 않는다.
