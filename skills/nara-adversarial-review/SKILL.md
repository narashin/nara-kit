---
name: nara-adversarial-review
description: >-
  Adversarially attack an existing review report: refute confirmed findings,
  hunt missed issues blind, audit report rigor. Append-only — never edits code
  or rewrites the original report body.
  USE FOR: "리뷰 리포트 공격해", "이 리뷰 오탐 없나", "리뷰 빠진 거 찾아",
  "adversarial review", "리뷰 검증해줘", after a nara-code-review report.
  DO NOT USE FOR: 리뷰 자체 생성 (→ nara-code-review), 원격 PR 리뷰
  (→ nara-pr-review), 코드 수정 (→ nara-implement), 설계 검증 (→ nara-grill).
---

# Adversarial Review — 리뷰 리포트 공격

리뷰 리포트를 신뢰하지 않고 공격한다: 오탐(false positive), 누락(false negative),
과도한 낙관(rigor 위반). 산출물은 원 리포트에 **append-only**로 추가되는
`## Adversarial Review` 섹션.

## Input

- 인자: 리포트 경로. 없으면 `./docs/review/`의 최신 파일.
- 리포트에서 리뷰 스코프(manifest의 baseline/head, 파일 목록)를 복원한다.
  manifest가 없으면 리포트에 적힌 파일 목록으로 대체하고 그 한계를 명시한다.
- 리포트도 코드도 수정하지 않는다 (append 제외). 코드는 read-only.

## Attack lanes (3 agents, parallel) — [attack-protocol](references/attack-protocol.md)

1. **refuter** — finding마다 반박 시도: failure_path를 실제 코드에서
   재추적, 기존 guard·caller·test에서 counterevidence 수색. 목표는 방어가 아니라
   격추.
2. **blind hunter** — 리포트를 **보지 않고** 같은 스코프의 diff를 리뷰한 뒤,
   결과를 리포트와 대조해 누락 finding을 찾는다. 블라인드가 깨지면 무효.
3. **rigor auditor** — 리포트 내부 무결성: evidence level이 근거와 일치하는가,
   verified 주장에 실제 proof가 있는가(hash/hunk/validation), E1 이하가
   finding으로 승격돼 있지 않은가, trailing status 존재·정합 여부.

## Verdict & Output

finding별: `upheld | refuted | weakened(사유)`. 누락 후보는 nara-code-review의
finding 스키마(있으면 그 형식, 없으면 location/invariant/failure_path/impact 최소
필드)로 기술. 리포트 말미에 섹션 append 후 요약을 한국어로 보고.

Trailing status (필수):

```
adversarial: N upheld, N refuted, N weakened, N missed-found
report: appended (<path>)
```

## Codex

`/codex:adversarial-review`가 있으면 그것을 직접 실행하라고 사용자에게 권한다
(`disable-model-invocation`이라 자동 호출 불가). 이 스킬은 codex 없이도 동작하는
네이티브 경로이며, 둘을 겹쳐 돌려도 된다 (관점 다양성).
