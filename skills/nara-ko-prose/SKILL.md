---
name: nara-ko-prose
description: >-
  Repair Korean prose in shared artifacts (PR, RFC, ADR, Confluence): restore dropped particles and endings, complete noun-phrase sentence breaks, replace em-dashes. Reads the installed snflkd/fluent-korean (MIT) rules.
  USE FOR: "ko-prose", "한국어 다듬어", "문장 완결해", "조사 빠진 것 고쳐", "공유 문서 한국어 정리".
  DO NOT USE FOR: AI 티 제거 (nara-humanizer), 개인 말투 (naranizer), 커밋 메시지·변수명·주석·로그, 영어 텍스트, 사실 교정.
license: MIT
---

# ko-prose — 공유 문서 한국어 명확성 수리

여러 사람이 함께 읽는 산출물의 한국어를 한 가지 뜻으로 읽히게 고친다. 압축·전보체 때문에 **빠진 문법 재료를 되돌리는 가산 작업**이며, AI 마커를 덜어내는 감산 작업(`nara-humanizer`)과 방향이 반대다.

규칙의 출처는 [snflkd/fluent-korean](https://github.com/snflkd/fluent-korean) (MIT)이다. 이 스킬은 **규칙 사본을 배포하지 않고** 설치된 원문을 읽어 적용한다. 원문 `## 상황과 목표` 절이 지침의 요약을 명시적으로 권장하지 않으므로, 축약본을 만들지 않는다.

## Steps

1. **규칙 원문 확보.** 아래 Rule Source 순서로 탐색. 못 찾으면 Step 5의 `Unverifiable`로 종료 — 추측으로 대체하지 않는다.
2. **대상 텍스트 확보.** 인자·파일 경로·호출한 스킬이 넘긴 초안. 한국어 부분만 대상. 영어 구간은 원형 유지.
3. **모드 판별.** 인자에 `full`이 없으면 `repair`. 적용 조항은 [clause-map.md](references/clause-map.md).
4. **수리.** 원문 전문(예시 포함)을 읽은 상태에서 해당 조항만 적용. 제외 대상은 Scope 표를 따른다.
5. **자체 검증 게이트 통과 후 출력.** Verification 절의 4항을 점검하고 trailing status를 붙인다.

## Rule Source

탐색 순서. 앞에서 찾으면 뒤는 보지 않는다.

```bash
# 1) 인자로 경로를 받은 경우 그 경로
# 2) marketplace clone
ls ~/.claude/plugins/marketplaces/fluent-korean/plugins/fluent-korean/output-styles/fluent-korean.md
# 3) versioned cache (여러 버전이면 가장 높은 버전)
ls -d ~/.claude/plugins/cache/fluent-korean/fluent-korean/*/output-styles/fluent-korean.md | sort -V | tail -1
```

셋 다 없으면 미설치다. 설치 안내는 `/plugin marketplace add snflkd/fluent-korean` 이후 `/plugin install fluent-korean@fluent-korean`.

## Modes

| 모드 | 호출 경로 | 성격 |
|------|-----------|------|
| `repair` (기본) | 산출물 스킬의 post-pass | 결함 교정만. 어휘 선택·말투를 건드리지 않아 `naranizer` 결과와 공존한다 |
| `full` | 사용자 직접 호출 | 원문 전 조항 적용. 문체까지 원문 기준으로 맞춘다 |

`repair`가 조항의 부분집합인 이유는 분량 절약이 아니라 **`naranizer`와의 공존**이다. 원문 `## 동작 범위` 4항(사용자 어조 모방 금지)을 PR 본문에 그대로 적용하면 개인 말투 변환이 통째로 취소된다. 조항별 판단 근거는 clause-map.md에 남긴다.

## Scope

| 대상 | 처리 |
|------|------|
| 헤더·목록 항목 | 종결어미 완결 요구를 적용하지 않는다 (원문 `## 문장 단위` 2항이 스스로 제외한다) |
| 커밋 메시지·변수명·코드 주석·로그 문자열 | 적용 금지 (원문 `## 동작 범위` 2항). 프로젝트 관례를 따른다 |
| 코드 블록·인용 | 원형 유지 |
| 영어·혼합 텍스트 | 한국어 구간만 |
| 고유명사·기술 용어 | 정착된 번역어·음차가 있으면 사용, 없으면 원어 유지 |

## Verification

출력 전 4항을 점검한다. 위반이 있으면 수정하고 다시 점검한다.

- [ ] 원본의 명사·고유명사·수치·날짜가 결과에 모두 보존되었다
- [ ] 부정·인과 방향이 반전되지 않았다
- [ ] `repair` 모드에서 어휘를 교체하거나 문장 순서를 바꾸지 않았다
- [ ] 격식 수준이 원본과 같다

## Output

응답은 수리된 텍스트 자체다 (nara-kit 표준 receipt 형식 미적용 — `nara-humanizer`와 같은 이유로, 산출물이 곧 응답이다). 텍스트 뒤에 변경 항목을 조항별로 짧게 적고, 마지막 줄에 trailing status를 붙인다.

```
✓ ko-prose: mode=<repair|full> · source=<marketplace|cache|arg> · 조항 <적용 목록> · 검증 4항 통과
```

파일 경로가 입력이면 Edit으로 제자리 교체를 제안하고, 사용자 동의 후에만 쓴다.

## Examples

`repair` 모드. 어휘를 바꾸지 않고 빠진 문법 재료만 되돌린다.

```
입력:  토큰 카운트 함수 오류 수정. 지출 비용 추론 시 음수 반환 — 캐시 히트 케이스 누락 원인.
출력:  토큰 카운트 함수의 오류를 수정했습니다. 지출한 비용을 추론할 때 음수가 반환되었고,
       원인은 캐시 히트 케이스가 누락된 것입니다.
```

적용 조항: 문장 단위 1(성분 복원), 문장 단위 2(종결어미 완결), 구 단위 1(조사 복원), 구 단위 4(엠대시 치환). `countTokens` 같은 식별자와 "캐시 히트" 같은 기술 용어는 그대로 둔다.

목록 항목은 종결어미를 강제하지 않는다.

```
입력:  - `countTokens()` 캐시 분기 추가
출력:  - `countTokens()` 캐시 분기 추가        (변경 없음 — 원문 문장 단위 2항이 목록을 제외)
```

## Error Handling

- 규칙 원문 미발견 → `Unverifiable: fluent-korean 미설치 — 규칙 원문 없이 수리하지 않는다.` 설치 명령 안내 후 종료. 호출한 산출물 스킬은 이 결과를 받으면 건너뛴다.
- 대상 텍스트가 한국어를 포함하지 않음 → 대상 아님을 밝히고 종료.
- 원본이 이미 기준을 충족 → 변경 없음을 밝히고 원본을 그대로 반환한다. 과교정 금지.
- `full` 모드에서 `naranizer` 결과를 덮게 되는 경우 → 덮는다는 사실을 먼저 알리고 사용자 확인을 받는다.
