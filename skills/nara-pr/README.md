# nara-pr — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Analyze commits against the auto-detected base branch and generate a Pull Request title and body in Korean.

## 호출

- Claude Code: `/nara-pr`
- Codex: `$nara-pr`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "pr", "PR 만들어", "pull request", "PR 제목", "/nara-pr".
- **DO NOT USE FOR:** git commit, branch management, code review.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
