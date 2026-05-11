---
name: adr
description: >-
  This skill should be used when the user asks to "write an ADR",
  "record a decision", "document architecture decision", "create ADR",
  "supersede an ADR", "backfill a decision", "/adr",
  or when a significant technical decision has been made
  that should be recorded for future reference.
---

# ADR (Architecture Decision Record)

Record significant technical decisions with context, alternatives considered, and consequences.
ADRs answer "why did we do it this way?" — the question that comes up months later.

## When to Use

- After making a significant technical decision (library choice, architecture pattern, removal of feature)
- When a decision involved trade-offs worth documenting
- When reversing or superseding a previous decision
- NOT for routine implementation choices or obvious patterns

## Workflow

### 1. Scan Existing ADRs

Read `docs/adr/` to determine the next sequence number.
If directory does not exist, create it and start at `0001`.

### 2. Gather Decision Context

Sources to check (in order of priority):
- Current conversation context (brainstorming results, discussion)
- Recent git history (`git log --oneline -20`)
- Related plan files in `docs/plan/`
- CLAUDE.md project notes

### 3. Write the ADR

Create file: `docs/adr/NNNN-<decision-slug>.md`

Naming rules:
- Zero-padded 4-digit sequence number
- kebab-case slug, imperative verb, max 6 words
- Examples: `0001-use-better-sqlite3.md`, `0002-remove-slash-commands.md`

Use the template below. All sections required. Write in Korean (technical terms in English).

### 4. Update References

- If decision affects CLAUDE.md, note the ADR number there
- If decision supersedes a previous ADR, update the old ADR's status to `superseded by ADR-NNNN`
- If decision deprecates a previous ADR, update the old ADR's status to `deprecated (see ADR-NNNN)`

## Template

```markdown
# ADR-NNNN: <title>

- Status: accepted | superseded by ADR-NNNN | deprecated (see ADR-NNNN)
- Date: YYYY-MM-DD
- Supersedes: ADR-NNNN (if applicable, otherwise omit this line)

## Context

Why this decision was needed. What problem or constraint triggered it.

## Options Considered

1. **Option A** — pros / cons
2. **Option B** — pros / cons
3. **Option C** — pros / cons (if applicable)

## Decision

What was chosen and the primary reasoning.

## Consequences

### Positive
- What improves

### Negative
- Trade-offs accepted
- Known limitations

### Follow-up
- Any future work this decision creates (if applicable)
```

## Guidelines

- **Be concise** — each section 2-5 sentences max. Not a design doc.
- **Options Considered is mandatory** — even if choice was obvious, state why alternatives were rejected. This prevents re-discussion.
- **Status transitions**: `accepted` → `superseded by ADR-NNNN` or `deprecated (see ADR-NNNN)`. Always include the related ADR number for traceability. Never delete ADRs.
- **Follow-up section** — include when the decision creates concrete future work. Omit if no follow-up exists. When included, list actionable items, not vague intentions.
- **Conciseness** — "2-5 sentences" applies to prose paragraphs. Bullet lists in Consequences count per-item, not per-bullet.
- **One decision per ADR** — if two decisions are coupled, write two ADRs and cross-reference.
- **Date format** — always YYYY-MM-DD, never relative dates.

## Backfilling Past Decisions

When recording a decision made in a previous session:
1. Use the original decision date, not today
2. Add `(backfilled YYYY-MM-DD)` after the date
3. Reconstruct context from git history and CLAUDE.md

