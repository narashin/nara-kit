---
name: nara-spec-revision
description: >
  This skill should be used when the user wants to "revise a spec", "update spec with feedback",
  "apply review feedback to spec", "log a spec change", "spec revision", "spec 수정", "피드백 반영",
  "개정 이력", "changelog 추가", or has review comments/feedback on an existing Confluence
  specification page that should be recorded as a dated revision. Requires Confluence MCP tools.
---

# Spec Revision — Dated Changelog + Inline Edits for Confluence Specs

Record a revision on an existing Confluence spec by **(1) prepending a dated changelog entry at the top of the page** and **(2) editing the changed sections inline** — striking through what was removed and marking what is new — mirroring the team's RfC revision convention. Traceability comes from the **top changelog + inline `<del>` markers + Confluence version history**, not from a separate appended "Revision vN" section.

> **Pattern reference** (the shape to mirror): a top `<blockquote>` holding dated `**YYYY-MM-DD Updated**: …` lines newest-first, with the body edited in place (`<del>old</del>` + `**(Revised YYYY-MM-DD)** new`, decision-table rows struck/bolded). Example in the wild: Confluence `pageId=4276145441`.

## When to Use

- Review feedback / a decision change has been received on a Confluence spec page
- The change should be recorded on the page with a clear "what changed & why" trail
- The original wording must stay legible (via strikethrough), not be silently overwritten

**Standalone entry point.** Invoke independently of any prior session — the gap between a `nara-publish-spec` session and a `nara-spec-revision` session is normally days~weeks. No workflow-continuity assumption. Confluence URL + feedback input is enough to complete in one session.

## Inputs (Required)

1. **Confluence page URL** — required. Reject + request if missing.
2. **Feedback source** — one or both:
   - User-provided in conversation (paste, summary, bullets — raw text OK)
   - Confluence inline comments — auto-parsed from the raw XHTML (`ac:inline-comment-marker`) on Step 1 fetch
3. Zero feedback = block the revision. Guide: "paste feedback or confirm inline comments, then re-invoke".

## Publish Safety

Updating a shared spec is an outward-facing publish. **Dry-run → confirm → publish**: show the user (a) the exact top changelog entry text and (b) a section-level before→after list of the inline edits, get a "go", then call `confluence_update_page`. `update_page` returns a **markdown rollback view** (cannot verify macro/table render), so tell the user to eyeball the live page after.

## Workflow

### Step 1: Fetch Current Page

Use `mcp__confluence__confluence_get_page`:
- By URL (extract title + space key) or by `title` + `space_key`
- `convert_to_markdown: false` → raw storage format (XHTML), required for inline editing + macro preservation
- `include_metadata: true` → `page_id`, current `version`

Record `page_id`, current `version`, and the full raw storage content.

### Step 2: Locate the Changelog Block

- Find the top `<blockquote>` immediately after the title / first Jira macro (`ac:name="jira"`).
- If it exists, new entries go **on top** (newest-first) of its existing dated lines.
- If none exists, create one just after the opening Jira macro `<p>…</p>` (or as the first element if there is no macro).
- Determine the revision date from the user (or "today" if given). The team uses **dates**, not `vN` — do not invent version numbers.

### Step 3: Collect Review Feedback

Gather from user-provided comments, Confluence inline comments (`ac:inline-comment-marker` in raw XHTML), and conversation context. Structure each point as:
1. **What was raised** — the concern or suggestion
2. **Rationale** — why it matters (use case, risk)
3. **Resolution** — accepted / rejected / deferred, and what changed

### Step 4: Apply the Revision (two parts)

Work on the **full raw storage** string. Apply surgical edits — leave every unchanged fragment byte-for-byte identical (preserves macros, tables, `ac:macro-id`s, images).

**(a) Top changelog entry** — prepend one `<p>` as the first child of the top `<blockquote>`:

```
<p><strong>YYYY-MM-DD Updated</strong>: one-paragraph summary of what changed and why (the key decisions, in the user's framing). Reference sections touched.</p>
```

Newest entry first; keep all prior entries below it, unchanged.

**(b) Inline body edits** — in each changed section, edit in place:
- Removed / superseded wording → wrap in `<del>…</del>`.
- New wording → follow with `<strong>(Revised YYYY-MM-DD)</strong>` then the new text.
- Decision / comparison tables → strike the old cell value and bold the new one in the same row (`<del>old</del> <strong>new</strong>`), or add a status like `<strong>Changed (YYYY-MM-DD)</strong>`.
- Section heading whose content materially changed → optionally suffix `(revised YYYY-MM-DD)`.
- Do **not** append a separate bottom "Revision vN" section, and do **not** repeat unchanged content.

**(c) Large structural additions** — if the change adds substantial new material (not just edits), add a **new subsection** in the right place; for a many-field before→after delta, an inline comparison table (Area | before | after, new value bolded) is fine. Still log it in the top changelog entry.

**Same-day correction / revert**: if a change from earlier the same day is being undone, **edit or remove that day's changelog line and restore the inline text** so the page reads as if the retracted change never happened — do not stack contradictory lines.

### Step 5: Dry-run → Update Confluence Page

1. **Dry-run**: present the top changelog entry text + the section-level before→after edit list; get confirmation.
2. On "go", call `mcp__confluence__confluence_update_page`:
   - `page_id` (Step 1), `title` unchanged
   - `content`: full storage content with (a) the changelog entry prepended + (b) inline edits applied
   - `content_format: storage`
   - `version_comment`: `vN (YYYY-MM-DD): brief summary` (N = the Confluence page version, informational)

### Step 6: Confirm

Report: page URL, new Confluence version number, and a summary of the changes. Remind the user to **eyeball the live page** (macros/tables) since `update_page` only returns a markdown rollback view.

## Output Templates

**Top changelog block** (create if absent; prepend new line if present):

```html
<blockquote>
  <p><strong>YYYY-MM-DD Updated</strong>: … newest summary …</p>
  <p><strong>YYYY-MM-DD Updated</strong>: … older entry, unchanged …</p>
</blockquote>
```

**Inline edit** (prose):

```html
<p>… <del>the old sentence that no longer holds</del> <strong>(Revised YYYY-MM-DD)</strong> the new sentence. …</p>
```

**Comparison table** (only for large multi-field deltas):

```html
<table class="wrapped"><colgroup><col/><col/><col/></colgroup><tbody>
  <tr><th scope="col">Area</th><th scope="col">Before</th><th scope="col">After</th></tr>
  <tr><td>[area]</td><td>[previous]</td><td><strong>[new]</strong></td></tr>
</tbody></table>
```

## Edge Cases

- **Multiple rounds**: each round adds a new dated line at the **top** of the changelog blockquote (newest-first); earlier lines stay.
- **Same-day revert**: edit/remove that day's changelog line and restore the inline text — don't leave contradictory strikethroughs.
- **Partial feedback**: touch only the changed sections; everything else stays verbatim.
- **Deferred items**: note in the changelog + add to the page's Open Questions section.
- **Rejected feedback**: capture the decision + rationale in the changelog entry (or an Open Questions note); no body edit needed.
- **No top macro/blockquote anchor**: create the blockquote as the first element of the page.
- **No Confluence MCP**: generate the full edited XHTML locally for manual copy-paste.

## Language

- All Confluence content in **English** (specs are shared across teams).
- Changelog + inline edits in English.
- Conversation with the user follows the user's language preference.
