# nara-now — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Assess current session state — git branch, changes, docs, gap score — and recommend the next action.

## 호출

- Claude Code: `/nara-now`
- Codex: `$nara-now`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "now", "what should I do", "where were we", "세션 시작", "어디까지 했지", "다음 뭐해", "지금 뭐해".
- **DO NOT USE FOR:** code implementation, gap analysis execution, commit or PR creation.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
