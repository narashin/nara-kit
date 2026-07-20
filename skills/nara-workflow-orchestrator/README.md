# nara-workflow-orchestrator — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Classify natural-language workflow requests into doc or dev mode and route to the correct downstream workflow skill.

## 호출

- Claude Code: `/nara-workflow-orchestrator`
- Codex: `$nara-workflow-orchestrator`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "now", "워크플로우", "workflow", "어떤 모드", "start work".
- **DO NOT USE FOR:** direct implementation tasks, standalone documentation edits, simple bug fixes.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
