---
name: publish-spec
description: >-
  Publish a local spec/plan markdown file to Confluence wiki via dry-run, confirm, and publish flow.
  USE FOR: "publish", "wiki에 올려", "confluence에 게시", "publish-spec", "스펙 게시".
  DO NOT USE FOR: creating specs from scratch (use workflow-doc-mode), editing existing Confluence pages directly.
---

# Publish Spec to Confluence

Convert a local markdown spec/plan to the **LYRIS Confluence RfC template** (7 mandatory sections) and publish. Strict dry-run -> confirm -> publish flow.

## Execution Flow

1. **Collect info**: spec file path, Jira ticket ID (required -- ask if missing), publish location
2. **Template conversion (dry-run)**: restructure into 7-section template, save as `confluence-draft.md`, show preview
3. **User confirmation**: single question "게시할까?" -- Publish or Cancel
4. **Publish**: convert to Confluence storage format (XHTML), create page via MCP
5. **Post-publish**: output page URL on success, or draft path on failure

## Critical Rules

- **Always dry-run first** -- never publish without preview
- **Never overwrite** existing pages without explicit confirmation
- **7-section compliance required** -- block publish if template not followed
- **No code-level references in Confluence** (file names, type names, function names) -- those belong in local spec.md only
- **Storage format required**: `content_format: "storage"` (XHTML), not markdown
- **Language**: dry-run preview in Korean OK; Confluence body in English unless user specifies Korean
- **[UNVERIFIED] markers**: warn if present before publishing

## Safety

- Title collision -> ask update or create new
- MCP unavailable -> REST API fallback -> XHTML local export
- Network error -> keep `confluence-draft.md` locally

## References

- [7-section body template and mapping guide](references/template.md)
- [Storage format conversion rules and MCP API](references/storage-format.md)
- [Step-by-step procedure, config, error handling](references/procedure.md)
