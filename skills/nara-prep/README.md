# nara-prep — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Localize external SoT (Jira/Confluence/Figma/Linear) into docs/requirements.md. AC verbatim 보존.

## 호출

- Claude Code: `/nara-prep`
- Codex: `$nara-prep`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "prep", "/nara-prep TICKET-ID", "요구사항 정리", "스펙 로컬화", Jira URL, Confluence URL.
- **DO NOT USE FOR:** gap (→ /nara-gap), code impl (→ dev-mode), RFC (→ /nara-rfc), no external SoT (→ doc-mode).

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
