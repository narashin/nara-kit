# nara-humanizer — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Detect AI writing patterns in Korean text and rewrite as natural human prose. Based on KatFishNet (94.88% AUC) + empirical patterns.

## 호출

- Claude Code: `/nara-humanizer`
- Codex: `$nara-humanizer`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "humanizer", "윤문", "AI 티 제거", "한국어 자연스럽게", "humanize", "ai-detection 회피".
- **DO NOT USE FOR:** 개인 말투/페르소나 적용 (use naranizer), 영어 텍스트, 코드 리뷰 (use nara-code-review), 번역, 사실 검증.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
