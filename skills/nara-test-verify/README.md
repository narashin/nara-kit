# nara-test-verify — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Verify test scenarios via parallel QA Lead, Developer, and Red Team review personas, then synthesize a unified verdict.

## 호출

- Claude Code: `/nara-test-verify`
- Codex: `$nara-test-verify`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "시나리오 검증해", "테스트 리뷰", "시나리오 빠진 거 없나", "review test scenarios", "verify scenarios".
- **DO NOT USE FOR:** discovering new scenarios (use nara-test-discover), implementing test code (use nara-test-implement).

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
