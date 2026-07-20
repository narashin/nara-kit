# naranizer — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Rewrite AI-drafted Korean text (Slack messages, review comments, announcements) into the user's own measured writing style, loaded from a local style profile built from real message history.

## 호출

- Claude Code: `/naranizer`
- Codex: `$naranizer`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "나라나이저", "naranize", "내 말투로", "내 스타일로 바꿔", "말투 프로필 만들어", "말투 프로필 갱신".
- **DO NOT USE FOR:** 일반 AI 티 제거 without persona (use nara-humanizer), 영어 텍스트, 내용 요약·사실 수정 (문체만 다룸), 코드 리뷰 (use nara-code-review).

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
