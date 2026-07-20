# nara-incident-fix — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Implement a TDD fix (Red-Green-Refactor) based on docs/incident-report.md analysis.

## 호출

- Claude Code: `/nara-incident-fix`
- Codex: `$nara-incident-fix`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "incident-fix", "장애 수정", "버그 고쳐", "fix the incident", "incident 수정 구현".
- **DO NOT USE FOR:** incident analysis (use /nara-incident), general bug investigation, code review.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
