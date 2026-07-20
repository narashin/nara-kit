# nara-memory-audit — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Audit durable auto-memory files for staleness in two tiers — bash prefilter, then subagent verify on flagged files, then human-approved fix/archive.

## 호출

- Claude Code: `/nara-memory-audit`
- Codex: `$nara-memory-audit`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "memory-audit", "메모리 감사", "메모리 점검", "stale memory", after a breaking rename / skill add-remove / migration.
- **DO NOT USE FOR:** writing memories (nara-reflect), permanent delete (manual rm), toolkit friction (nara-meta-feedback).

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
