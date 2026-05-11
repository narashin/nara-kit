---
name: commit
description: Generate a git commit message following conventional commits format with ticket ID prefix. Use when ready to commit changes. Triggers on "commit", "커밋 메시지", "commit message", "/commit TICKET-ID".
version: 0.1.0
---

# commit — Git 커밋 메시지 생성

### Commit Message Format
- Format: `<TICKET-ID> <type>: <Subject>`
- `<TICKET-ID>`: Use argument if provided (e.g., `/commit PROJ-111`). Otherwise use `NO-ISSUE`.
- `<type>`: feat, fix, docs, style, refactor, perf, test, chore, ci, revert
- `<Subject>`: Capitalized verb, present tense, under 72 chars

### Best Practices
- Run pre-commit checks before committing.
- Each commit should be atomic and logically grouped.
- Suggest splitting if multiple distinct changes exist.

### Examples
- `PROJ-111 feat: Add new feature`
- `OPS-999 fix: Fix ticket re-open logic`
- `NO-ISSUE refactor: Merge duplicated logics`
- `NO-ISSUE docs: Update README for setup instructions`
