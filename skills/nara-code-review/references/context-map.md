# Phase 2: Context Map — Code Context + Change Intent

Two halves: what the code IS, and what the change was SUPPOSED to do. Reviewers get
both. Skipping the intent half forces reviewers into generic speculation.

## 2a. Code context

For each changed file:

1. Read full file content (diff alone is insufficient).
2. Check imported modules and type definitions.
3. Read project CLAUDE.md and .claude/rules/ if present.
4. Check related test files.
5. Search for reusable existing code — scan utility directories, shared modules,
   adjacent files with `grep -r` (feeds architecture-reuse).
6. Detect tech stack → read the relevant section of [stack-specific](stack-specific.md).
7. **DESIGN.md check (conditional)**: if changed files include `components/`,
   `pages/`, `styles/`, or `*.tsx`/`*.css`/`*.scss`, check for `DESIGN.md` at project
   root. If present, read its YAML frontmatter (colors, typography, rounded, spacing
   tokens) + Do's/Don'ts, and pass to **frontend-ux-a11y**. Skip otherwise.

## 2b. Change intent (specification)

Collect what is available — never fabricate what isn't:

- User's review request wording (what they said they changed/want checked)
- Commit messages in scope (from Phase 1)
- `docs/plan.md`, `docs/requirements.md`, `docs/gap.md` if present — only sections
  relevant to changed files
- Related issue/ticket if the user or branch name references one
- Changed test names (tests encode intended behavior)
- Previous behavior vs new behavior of changed public functions
- Public API contract changes visible in the diff
- Feature flag / rollout conditions guarding the change

## 2c. Specification availability

If no intent source beyond the diff exists, the report and every reviewer prompt
must state:

```
specification: unavailable
behavior review scope: 코드 내부 invariant와 기존 테스트 기준으로 제한됨
```

Reviewers then must not present product-requirement claims as fact — behavior
findings are limited to code invariants and existing tests.
