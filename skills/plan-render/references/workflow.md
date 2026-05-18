# plan-render workflow (detailed)

Detailed procedure, placeholders, receipt format, and rules. Loaded on demand from SKILL.md.

## Inputs

- Markdown under `docs/plan/`, `docs/spec/`, `docs/rfc/`, or a user-given path.
- Optional frontmatter directive: `render: auto | force | skip` (default `auto`).

## Outputs

1. **Updated MD** — viewer-link line inserted/refreshed at top.
2. **HTML** — same directory, same basename, `.html` extension.

Treat HTML as a build artifact. Suggest adding `docs/**/*.html` to `.gitignore` if the team doesn't publish them, but do not modify `.gitignore` without confirmation.

## Step 1 — Resolve target

Two cases:

- **User-supplied path** (e.g., `/plan-render evals/x/y.md`): accept any `.md` file the user names. Do not impose the `docs/` restriction — the user has explicit intent.
- **Auto-discovery** (no path argument): scan `docs/plan/**/*.md`, `docs/spec/**/*.md`, `docs/rfc/**/*.md` only. Reject everything else. Multiple candidates → ask which.

Reject paths already ending in `.html`. Reject paths that don't exist.

## Step 2 — Threshold check

Read frontmatter (lines between leading `---` fences). Compare:

- Lines: `wc -l "$MD"`
- Bytes: `wc -c "$MD"`

Apply rule table in SKILL.md. If skipping, emit a one-line receipt and exit without writing HTML.

```
status: skipped — MD 142 lines / 5.3 KB below threshold (render: auto)
```

## Step 3 — Compute sync hash

Hash the MD body **excluding** (a) the frontmatter and (b) the viewer-link blockquote line (`> 📄 **HTML viewer:**...`). Excluding the viewer line is critical: it makes re-renders idempotent because the line gets inserted/refreshed every run.

Use first 12 chars of SHA-256:

```bash
awk '/^---$/{c++; next} c>=2 && !/^> 📄 \*\*HTML viewer:\*\*/' "$MD" \
  | shasum -a 256 | cut -c1-12
```

This hash anchors HTML to a specific MD body content. Stale HTML (hash mismatch) shows a banner in the viewer.

## Step 4 — Parse MD structure

Extract:
- **Title** — first `# H1` after frontmatter. If none, fallback to filename (no extension).
- **TOC** — H2 and H3 headings only (skip H1 — it's the title). Empty-body headings are included.
- **Body** — full markdown after frontmatter, viewer-link line excluded.

**Slug algorithm** (GitHub-style):
1. Lowercase.
2. Strip characters not in `[\p{L}\p{N}\s-]` (preserve Unicode letters, including Korean).
3. Spaces → `-`.
4. Collapse consecutive `-`.
5. Deduplicate: if slug exists, append `-1`, `-2`, ... in document order.

Do not transform semantically. Preserve code fences, tables, lists as-is.

## Step 5 — Render HTML

Load `references/template.html`. Replace placeholders:

| Placeholder | Value |
|-------------|-------|
| `__TITLE__` | Plan title (from Step 4) |
| `__MD_PATH__` | Basename of source MD (e.g., `spec-foo.md`) — HTML and MD live in the same directory, so a basename works as the relative link |
| `__MD_HASH__` | Sync hash from Step 3 |
| `__GENERATED_AT__` | ISO 8601 UTC, second precision: `YYYY-MM-DDTHH:MM:SSZ` |
| `__TOC_HTML__` | Sidebar TOC as `<a>` list (one `<li>` per H2/H3, `<a class="toc-h3">` for H3) |
| `__BODY_HTML__` | Rendered markdown body |

**Renderer selection** (deterministic, no user prompt):

1. If `pandoc` is on `PATH` → `pandoc -f gfm -t html5 --highlight-style=tango`.
2. Else if MD body uses only basic features (H1-H6, lists, code fences, blockquotes, inline code/bold/italic/links, tables, hr) → use an inline minimal renderer. The template's CSS handles styling.
3. Else (MD contains raw HTML, footnotes, math, or other GFM extensions beyond #2) → emit `❌ 실패: needs pandoc for advanced GFM features. Install pandoc or simplify MD.` Do not add dependencies silently.

No CDN. The file must stay self-contained.

## Step 6 — Write HTML

Save to `<md_dir>/<md_basename>.html`. If the existing HTML's hash already matches Step 3, emit `status: skipped — hash unchanged` and exit without overwriting.

## Step 7 — Insert/refresh MD viewer link

Inject (or replace) a viewer block immediately after the closing frontmatter fence:

```markdown
> 📄 **HTML viewer:** [`spec-foo.html`](./spec-foo.html) — derived, read-only. MD is source of truth.
```

Idempotency: if a line matching `^> 📄 \*\*HTML viewer:\*\*` already exists immediately after frontmatter, replace it. Otherwise insert it.

## Step 8 — Receipt

Follow the shared receipt contract (3-6 lines, no full artifact body):

```
status: applied
artifact: docs/plan/spec-foo.html (12.4 KB)
md_updated: docs/plan/spec-foo.md (header refreshed)
hash: a3f1c92b8e44
next: open in browser or share path
```

Optional fields when relevant:
- `override: frontmatter render:force` — when a threshold override drove the decision.
- `source: <path> (<lines>/<bytes>, render: <mode>)` — when skip needs justification.

Status labels: `applied` / `skipped` / `pending escalation` / `recorded only`.
Errors use `❌ 실패:` block.

## Rules

1. **Never edit the plan body during render.** Only the viewer-link header line may change.
2. **HTML is derived.** Suggest `.gitignore` but do not modify it without confirmation.
3. **No network resources.** Template must stay fully self-contained. No CDN scripts, no remote fonts.
4. **No frameworks.** Plain HTML + CSS + minimal vanilla JS only.
5. **Threshold override is frontmatter-only.** Honor `render: force|skip` from frontmatter, not CLI flags.
6. **Hash-based skip.** Re-running on unchanged MD is a no-op. Cheap to invoke from hooks.
7. **Receipt-only response.** Do not paste the rendered HTML body into chat.

## Hook integration

The PostToolUse hook in `hooks/hooks.json` watches `docs/{plan,spec,rfc}/*.md` Write/Edit and nudges via `systemMessage` when the threshold is crossed. The hook does not invoke this skill directly — preserves user agency.
