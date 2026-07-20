# nara-workflow-dev-mode — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Implementation-first workflow with structured gates: SoT → gap → TDD → verify → branch finish.

## 호출

- Claude Code: `/nara-workflow-dev-mode`
- Codex: `$nara-workflow-dev-mode`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "dev mode", "구현 워크플로우", "개발 모드", "feature implementation".
- **DO NOT USE FOR:** docs-only artifacts (→ workflow-doc-mode), unstable requirements (→ ac-draft), simple edits.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
