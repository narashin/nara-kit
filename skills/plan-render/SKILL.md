---
name: plan-render
description: >-
  Render long plan/spec markdown into a derived self-contained HTML viewer.
  USE FOR: "plan-render", "plan html", "spec html", "긴 plan 읽기 힘들어", "plan 시각화".
  DO NOT USE FOR: editing plan body, new specs (use workflow-doc-mode),
  package diagrams (use workflow-viz), generic HTML reports.
---

# plan-render

**UTILITY SKILL.** Derive HTML viewer next to a plan/spec MD. MD = source of truth. Idempotent via sync hash.

## Threshold

| Frontmatter | Size | Action |
|-------------|------|--------|
| `render: skip` | any | Skip |
| `render: force` | any | Render |
| `render: auto` (or absent) | ≥ 200 lines or ≥ 8 KB | Render |
| `render: auto` (or absent) | smaller | Skip |

## Steps

1. Resolve target. User-supplied path: accept any `.md`. Auto-discovery: scan `docs/{plan,spec,rfc}/` only.
2. Threshold via `wc -l`/`wc -c`. Skip → one-line receipt.
3. Sync hash: SHA-256 first 12 chars of body after frontmatter, **excluding the viewer-link blockquote**.
4. Parse title + H2/H3 TOC + body.
5. Render from [template.html](references/template.html), 6 placeholders.
6. Write `<basename>.html` next to MD. Hash unchanged → skip overwrite.
7. Insert/refresh viewer link in MD header (idempotent).
8. Emit receipt.

Full procedure → [workflow.md](references/workflow.md).

## Hook

PostToolUse on `docs/{plan,spec,rfc}/*.md` Write/Edit nudges this skill. Hook never auto-runs.

## Examples

- Long MD → `spec-checkout.html` written, MD header updated.
- Short MD → `status: skipped — below threshold`.
- `render: force` → always renders.

## Troubleshooting

- Hash unchanged = idempotent skip.
- Header missing = check frontmatter closing fence.
- No pandoc = ask before adding dep.
