---
name: spec-revision
description: >
  This skill should be used when the user wants to "revise a spec", "append v2 to spec",
  "update spec with feedback", "version the spec", "apply review feedback to spec",
  "spec revision", "spec 수정", "피드백 반영", "v2 append", or has review comments/feedback
  on an existing Confluence specification page that should be versioned and appended.
  Requires Confluence MCP tools to be available.
---

# Spec Revision — Versioned Feedback Append for Confluence Specs

Append a versioned revision section to an existing Confluence specification page based on review feedback, preserving the original content as-is and clearly documenting what changed and why.

## When to Use

- Review feedback has been received on a Confluence spec page
- The user wants to create a new version (v2, v3, ...) reflecting the feedback
- The original spec must be preserved for traceability

**Standalone entry point.** Invoke independently of any prior session — `publish-spec` 호출 세션과 `spec-revision` 세션 사이에 며칠~몇 주 갭이 정상. Workflow continuity 가정 X. Confluence URL + 피드백 입력만 있으면 단일 세션에서 완결.

## Inputs (Required)

1. **Confluence page URL** — 필수. URL 없으면 reject + 요청
2. **Feedback source** — 둘 중 하나 (또는 병행):
   - User-provided in conversation (paste, 요약, bullet 등 raw text 허용)
   - Confluence inline comments — Step 1 fetch 시 `ac:inline-comment-marker` 자동 파싱
3. 피드백 0건 = revision 차단. "피드백 paste or inline comment 확인 후 재호출" 안내

## Workflow

### Step 1: Fetch Current Page

Use `mcp__confluence__confluence_get_page` to retrieve the current page:
- By URL: extract page title and space key from the URL
- By title + space_key
- Set `convert_to_markdown: false` to get raw storage format (XHTML)
- Set `include_metadata: true` to get page_id and version number

Record: `page_id`, current `version`, and existing content.

### Step 2: Determine Current Version

Scan the existing content for version markers:
- Search for `Version N — Revised` pattern in the content
- If none found, the current content is v1
- Next version = highest found version + 1

### Step 3: Collect Review Feedback

Gather feedback from:
- User-provided review comments (inline in conversation)
- Confluence inline comments (visible in raw XHTML as `ac:inline-comment-marker`)
- Discussion context from the conversation

Structure each feedback point as:
1. **What was raised** — the concern or suggestion
2. **Rationale** — why it matters (use case, risk, etc.)
3. **Resolution** — what changed (accepted/rejected/deferred)

### Step 4: Generate Revision Section

Build the append content in Confluence storage format (XHTML). Structure:

```
<hr/>
<ac:structured-macro ac:name="info" ac:schema-version="1">
  <ac:rich-text-body>
    <p><strong>Version N — Revised YYYY-MM-DD</strong></p>
  </ac:rich-text-body>
</ac:structured-macro>

<h1>Revision: vN</h1>

<h3>Review Discussion Summary</h3>
<!-- Numbered list of feedback points with rationale -->

<h3>Changes Applied in vN</h3>
<!-- Comparison table: Area | v(N-1) | vN -->

<h3>Revised: [Section Name]</h3>
<!-- Only sections that changed — each prefixed with "Revised:" -->
```

**Rules:**
- Include ONLY sections that changed — do not repeat unchanged content
- Use `<h3>Revised: [Original Section Name]</h3>` for each changed section
- The comparison table must have columns: Area, v(N-1), vN
- Bold the new values in the vN column
- Keep the same XHTML structure/style as the original document (tables, lists, etc.)

### Step 5: Update Confluence Page

Combine: original content (unchanged) + revision append section.

Use `mcp__confluence__confluence_update_page`:
- `page_id`: from Step 1
- `title`: unchanged
- `content`: full content (original + appended revision)
- `content_format`: `storage`
- `version_comment`: `vN: brief summary of changes`

### Step 6: Confirm

Report to user:
- Page URL
- New version number
- Summary of changes applied

## Output Format — Comparison Table Template

```html
<table class="wrapped">
  <colgroup><col/><col/><col/></colgroup>
  <tbody>
    <tr>
      <th scope="col">Area</th>
      <th scope="col">v(N-1)</th>
      <th scope="col">vN</th>
    </tr>
    <tr>
      <td>[Changed area]</td>
      <td>[Previous value]</td>
      <td><strong>[New value]</strong></td>
    </tr>
  </tbody>
</table>
```

## Edge Cases

- **Multiple rounds of feedback**: Each round gets its own version section (v2, v3, v4...)
- **Partial feedback**: Only include changed sections in the revision — skip unchanged areas
- **Deferred items**: Mark as "Under discussion" in the revision, add to Open Questions
- **Rejected feedback**: Still document in Discussion Summary with rationale for rejection
- **No Confluence MCP**: Fall back to generating the XHTML locally for manual copy-paste

## Language

- All Confluence content in **English** (spec documents are shared across teams)
- Discussion summary in English
- Conversation with user follows user's language preference
