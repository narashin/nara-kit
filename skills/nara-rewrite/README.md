# nara-rewrite: 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Rewrite an existing answer or document so a reader without the project context can follow it, preserving meaning exactly (Korean and English).

## 호출

- Claude Code: `/nara-rewrite [텍스트 | 파일 경로] [tone only | structure only | review]`
- Codex: `$nara-rewrite ...`

대상을 주지 않으면 직전 답변을 다시 쓴다.

## 언제 쓰나

- **USE FOR:** "읽기 쉽게 다시 써", "읽기 쉽게 고쳐", "배경 모르는 사람이 읽게", "이 답변 정리해서 다시 써", "공유하게 다시 써줘", "rewrite this", "make this clearer", "deslopify", "tone only", "structure only", 문서 리뷰만 받고 싶을 때 "review".
- **DO NOT USE FOR:** AI 패턴 감지·자연도 등급 (→ nara-humanizer), 내 말투로 바꾸기 (→ naranizer), 공유 문서의 조사·어미만 복원하는 문법 수리·"한국어 다듬어" (→ nara-ko-prose), 번역투·AI 말투만 고치기 (→ nara-humanizer), 코드를 읽고 새 설명 만들기 (→ nara-explain), 사실 교정.

## 이웃 스킬과의 차이

nara-humanizer는 AI 작문 패턴을 찾아 등급을 매기고, naranizer는 내 말투로 바꾸고, nara-ko-prose는 빠진 조사와 어미만 복원한다. nara-rewrite는 독자가 배경을 모른다는 전제에서 결론을 앞으로 옮기고 맥락을 되살린다. 점수도 분석도 내지 않고 재작성본 하나만 돌려준다. `review`를 붙였을 때만 문제와 국소 수정 제안을 표로 준다.

## 설계 메모

출발점은 MTGVim/tiger-kit의 `tk-rewrite`(`5e35b6a`, MIT)다. 의미를 먼저 재구성하고 표현을 나중에 다듬는 두 단계, 양태와 강도와 시제를 지키는 의미 보존 점검, 0건 수정을 정상 결과로 보는 원칙을 가져왔고 본문과 예시는 새로 썼다. tiger-kit 공통 블록(질문 라운드, 결과 요약 서식, 산출물 경로)과 업스트림별 출처 이력은 가져오지 않았다. 한국어 표면 규칙은 fluent-korean 원문을 복사하지 않고 필요한 것만 직접 다시 썼다.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
