---
name: adr
description: >-
  Record a significant architecture decision with context, alternatives, and consequences as an ADR.
  USE FOR: "adr", "write an ADR", "record a decision", "document architecture decision", "supersede an ADR".
  DO NOT USE FOR: RFC writing (use /rfc), routine implementation choices, code review.
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
