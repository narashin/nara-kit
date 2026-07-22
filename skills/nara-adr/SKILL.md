---
name: nara-adr
description: >-
  Record a significant architecture decision with context, alternatives, and consequences as an ADR.
  USE FOR: "adr", "write an ADR", "record a decision", "document architecture decision", "supersede an ADR".
  DO NOT USE FOR: RFC writing (use /nara-rfc), routine implementation choices, code review.
---

# ADR (Architecture Decision Record)

Record significant technical decisions with context, alternatives, and consequences.

## When to Use

- After a significant technical decision (library choice, architecture pattern, feature removal)
- When a decision involved trade-offs worth documenting
- When reversing or superseding a previous decision
- NOT for routine implementation choices

## Workflow

1. **Scan**: Read `docs/adr/` for next sequence number. Create dir if absent, start at `0001`.
2. **Gather context**: conversation, `git log --oneline -20`, `docs/plan/`, CLAUDE.md
3. **Write ADR**: Follow template and naming rules in [references/adr-template.md](references/adr-template.md). All sections required. Write in Korean (technical terms in English).
4. **Update references**: Note ADR in CLAUDE.md if relevant. Update old ADR status if superseding/deprecating.

## Error Handling (if-then)

| 트리거 | 대응 |
|---|---|
| 결정 컨텍스트 불충분 | 추측 금지 — 1~2개 focused 질문으로 명확화, 그래도 부족하면 중단 + 사유 보고 |
| `docs/adr/` 시퀀스 충돌 (동시 작성 / 누락 번호) | 재-scan 후 `max+1` 재계산. 기존 파일 덮어쓰기 금지 |
| supersede 대상 ADR 없음 | 중단 — 번호 지어내지 않고 사용자에게 대상 확인 요청 |
| `docs/plan/` · `git log` 부재 | 해당 소스 skip (실패 아님), 가용 컨텍스트로 진행 |
| 결정이 routine / 단순 구현 선택 | ADR 거부 + 사유 (When to Use 위반 → `/nara-rfc`나 코드로 리다이렉트) |
| 이미 ADR 있는 결정 재기록 (중복) | 기존 ADR 참조. supersede/amend면 그 흐름, 아니면 신규 생성 안 함 (append-only 로그 오염 방지) |
