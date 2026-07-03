# screen: example — screens/<your-screen>.md 로 복사해 사용

## Goal
<이 화면에서 무엇을 비교하나 — 1줄>

## Entry
- start: <local_url>/<path>
- steps: nav → `<selector>` 클릭 → modal `<selector>` open ...

## Data-Context
- account: <role/fixture>
- flag: <맞출 feature flag>

## Selectors
- container: <측정 범위 root selector>
- compare-target: <측정할 selector(들)>
- ready signal: <렌더 완료를 뜻하는 selector>

## Known pitfalls
- sticky header / lazy load / animation / overlay ...

## Regression notes
- <과거 깨졌던 지점 — 주시할 것>
