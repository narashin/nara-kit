# Phase 2: Context Map — Code Context + Change Intent

Two halves: what the code IS, and what the change was SUPPOSED to do. Reviewers get
both. Skipping the intent half forces reviewers into generic speculation.

## 2a. Code context

For each changed file:

1. Read full file content (diff alone is insufficient).
2. Check imported modules and type definitions.
3. Read the project's agent instruction files if present: `CLAUDE.md`, `AGENTS.md`, `.claude/rules/`.
4. Check related test files.
5. Search for reusable existing code — scan utility directories, shared modules,
   adjacent files with `grep -r` (feeds architecture-reuse).
6. Detect tech stack → read the relevant section of [stack-specific](stack-specific.md).
7. **DESIGN.md check (conditional)**: if changed files include `components/`,
   `pages/`, `styles/`, or `*.tsx`/`*.css`/`*.scss`, check for `DESIGN.md` at project
   root. If present, read its YAML frontmatter (colors, typography, rounded, spacing
   tokens) + Do's/Don'ts, and pass to **frontend-ux-a11y**. Skip otherwise.
8. **Historical context (conditional — only when triggered, never blanket)**: when
   the diff removes/alters a guard, branch, or comment whose purpose is unclear, or
   deletes/weakens an existing test — run `git log -p -- <file>` / `git blame` on
   those lines (optionally `git log --grep="<keyword>"`). Surface why the code
   existed (past incident, revert, legacy compat) to the relevant reviewers. Do NOT
   run this on every file — only on puzzling guards, legacy comments, and removed
   protections.

## 2b. Change intent (specification)

Collect what is available — never fabricate what isn't:

- User's review request wording (what they said they changed/want checked)
- Commit messages in scope (from Phase 1)
- `docs/plan.md`, `docs/requirements.md`, `docs/gap.md` if present — only sections
  relevant to changed files
- `docs/implementation-notes.md` if present (written by `nara-implement`): its
  Tradeoffs and Design decisions are the implementer's own account and go to the
  **claimed** bundle below, never to reviewers. Its **Deviations** section (and
  Open questions of type `revise`) is the one exception: it goes to
  [spec-fidelity](agents/spec-fidelity.md) only, as **declared deviations**
- Related issue/ticket if the user or branch name references one
- Changed test names (tests encode intended behavior)
- Previous behavior vs new behavior of changed public functions
- Public API contract changes visible in the diff
- Feature flag / rollout conditions guarding the change

Split what you collected into two bundles before dispatch:

- **requested** — what was asked for: requirement docs, the ticket, the user's
  request, commit subjects, previous vs new behavior, contract changes. Goes to
  every reviewer.
- **claimed** — what the implementer says about their own work:
  `docs/implementation-notes.md`, commit-body justifications, "intentionally deviates because…", "already
  handled by…", reported test results. Withheld from reviewers; goes to the Judge
  as leads ([adjudication](adjudication.md)).

A reviewer who reads the implementer's reasoning first ends up reviewing the
reasoning instead of the code.

The Deviations exception exists because that section is where an intentional
departure from the spec is recorded. Withhold it and spec-fidelity reports the
departure as a defect, the Judge cannot reject it (the reason is not in the code),
and a `--fix=safe` run reverts a decision someone made on purpose. The entry does
not make the mismatch disappear; it changes who decides (see the agent's rules).

## 2c. Specification availability

If no intent source beyond the diff exists, the report and every reviewer prompt
must state:

```
specification: unavailable
behavior review scope: 코드 내부 invariant와 기존 테스트 기준으로 제한됨
```

Reviewers then must not present product-requirement claims as fact — behavior
findings are limited to code invariants and existing tests.

`specification: available` can still mean "commit messages only". Record separately
whether a **written requirement** was found (and its path) — that, not
`specification`, is what routes [spec-fidelity](agents/spec-fidelity.md).
