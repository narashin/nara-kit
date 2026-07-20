# nara-commit — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Analyze staged git changes and generate a conventional commit message with ticket ID prefix.

## 호출

- Claude Code: `/nara-commit`
- Codex: `$nara-commit`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "commit", "커밋 메시지", "commit message", "/nara-commit TICKET-ID", 커밋 생성.
- **DO NOT USE FOR:** git push, PR creation, branch management.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
