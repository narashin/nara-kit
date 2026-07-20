# nara-test-discover — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Discover behavior-focused test scenarios for a feature, file, or directory via a 4-stage pipeline.

## 호출

- Claude Code: `/nara-test-discover`
- Codex: `$nara-test-discover`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "테스트 시나리오 만들어", "테스트 케이스 뽑아", "시나리오 발굴", "test scenarios", "discover test scenarios".
- **DO NOT USE FOR:** implementing test code (use nara-test-implement), reviewing existing scenarios (use nara-test-verify).

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
