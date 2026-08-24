# nara-ko-prose — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

공유 산출물(PR 본문, RFC, ADR, Confluence)의 한국어를 한 가지 뜻으로 읽히게 수리한다. 빠진 조사·어미를 되돌리고, 명사구로 끊긴 문장을 종결어미로 맺고, 엠대시를 치환한다.

## 규칙 출처

규칙은 [snflkd/fluent-korean](https://github.com/snflkd/fluent-korean) (MIT)의 것이다. **이 스킬은 규칙 사본을 배포하지 않는다.** 실행 시점에 설치된 원문 파일을 읽어 적용하며, 원문이 없으면 `Unverifiable`로 건너뛴다. 원문 `## 상황과 목표` 절이 지침의 요약을 권장하지 않으므로 축약본도 두지 않는다.

nara-kit이 저작한 것은 호출 계약과 조항별 모드 배정([references/clause-map.md](references/clause-map.md))뿐이다.

사전 설치:

```
/plugin marketplace add snflkd/fluent-korean
/plugin install fluent-korean@fluent-korean
```

output style로 켤 필요는 없다. 파일이 디스크에 있으면 이 스킬이 읽는다.

## 호출

- Claude Code: `/nara-ko-prose`
- Codex: `$nara-ko-prose`
- 자동: `nara-pr`, `nara-rfc`, `nara-adr`, `nara-publish-spec`, `nara-spec-revision`이 초안 생성 후 post-pass로 부른다
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 모드

- `repair` (기본) — 결함 교정만. 어휘와 말투를 건드리지 않아 `naranizer` 결과와 공존한다. 산출물 스킬이 부르는 경로다.
- `full` — 원문 전 조항 적용. 문체까지 맞춘다. 사용자가 직접 부를 때 쓴다.

## 언제 쓰나

- **USE FOR:** "ko-prose", "한국어 다듬어", "문장 완결해", "조사 빠진 것 고쳐", "공유 문서 한국어 정리".
- **DO NOT USE FOR:** AI 티 제거·탐지 회피 (use nara-humanizer), 개인 말투 적용 (use naranizer), 커밋 메시지·변수명·주석·로그 문자열 (규약상 대상 아님), 영어 텍스트, 사실·수치 교정.

## humanizer·naranizer와의 구분

| | 잡는 결함 | 방향 |
|---|---|---|
| `nara-humanizer` | AI 마커 — 쉼표 과다, 유행어, 번역투, 균일한 리듬 | 덜어냄 |
| `nara-ko-prose` | 결핍 — 생략된 조사·어미·문장 성분, 명사구 종결 | 채움 |
| `naranizer` | 말투 부재 | 개인 프로필 적용 |

한자어에서 둘이 정면으로 어긋난다. humanizer는 "한자어 과다"를 결함으로 검출하고, fluent-korean 구 단위 2항은 한자어 적극 활용을 요구한다. 그래서 `repair` 모드는 그 조항을 적용하지 않는다.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
