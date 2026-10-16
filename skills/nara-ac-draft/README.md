# nara-ac-draft — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Write docs/requirements.md, the requirements every later skill reads: localize an external source (Jira, Confluence, Figma, Linear, a URL or pasted text) keeping its AC verbatim, or turn a one-line intent into User Stories + Gherkin AC. Draft AC only where the source has none, and mark them as drafts.

## 호출

- Claude Code: `/nara-ac-draft`
- Codex: `$nara-ac-draft`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "요구사항 정리", "스펙 로컬화", Jira 티켓 ID·URL, Confluence URL, "한 줄 기획", "thin SoT", "US 뽑아", "AC 초안", "ac-draft".
- **DO NOT USE FOR:** 기능 기획 묶음·PRD (→ nara-planning), 테스트 시나리오 (→ nara-test-discover), 구현 (→ nara-implement), 요구사항 대비 진행률 (→ nara-gap).

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
