# nara-test-implement — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Implement production-grade test code from a test scenarios document, matching existing project conventions.

## 호출

- Claude Code: `/nara-test-implement`
- Codex: `$nara-test-implement`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "테스트 코드 짜줘", "시나리오 구현해", "implement test scenarios", "write tests from scenarios", "generate test code".
- **DO NOT USE FOR:** discovering test scenarios (use nara-test-discover), reviewing test quality (use nara-test-verify).

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
