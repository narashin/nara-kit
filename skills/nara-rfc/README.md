# nara-rfc — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Generate a complete RFC document in Korean Markdown for technical decisions and feature proposals.

## 호출

- Claude Code: `/nara-rfc`
- Codex: `$nara-rfc`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "rfc", "RFC 작성", "기술 결정 문서", "설계 문서 써줘", "/nara-rfc TICKET-ID".
- **DO NOT USE FOR:** ADR (use /nara-adr), code implementation, PR creation.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
