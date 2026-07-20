# nara-golden-path-discover — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Discover live, parallel-safe, golden-path E2E scenarios and emit a Playwright-ready export (frontmatter + atomic-path coverage + SKIP/WARNING taxonomy), consuming nara-test-discover's E2E decomposition as input.

## 호출

- Claude Code: `/nara-golden-path-discover`
- Codex: `$nara-golden-path-discover`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "골든패스 발굴", "golden path E2E", "Playwright 시나리오 export", "라이브 E2E 시나리오 뽑아", "playwright-ready export", "golden path 시나리오 만들어".
- **DO NOT USE FOR:** generic/unit/backend scenario discovery (use nara-test-discover), implementing or running Playwright code (use nara-test-implement), reviewing existing scenarios (use nara-test-verify), writing requirements/AC (use nara-prep or nara-ac-draft).

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
