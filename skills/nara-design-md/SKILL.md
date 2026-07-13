---
name: nara-design-md
description: >-
  Adopt, update, or audit a DESIGN.md — AI-readable design spec (Stitch format).
  USE FOR: "design.md 만들어줘", "디자인 스펙 생성", "DESIGN.md 갱신", "디자인 감사",
  "adopt design.md", "update design spec", "audit design drift".
  DO NOT USE FOR: code implementation (use brainstorming → plan), component library creation.
---

# design-md

**UTILITY SKILL** — maintain DESIGN.md as AI's design source of truth.

Install: `npx getdesign@latest add <name>` ([gallery](https://getdesign.md/))

## Modes

| Mode | Trigger | Output |
|------|---------|--------|
| **adopt** | No DESIGN.md, "design.md 만들어줘" | Template → customize → `DESIGN.md` |
| **update** | "Figma 변경", "디자인 갱신" | Partial update existing `DESIGN.md` |
| **audit** | "디자인 드리프트 확인" | Drift report — [format](references/audit-format.md) |

## Adopt

1. Scan project (tailwind config, CSS, component library)
2. Browse [getdesign.md](https://getdesign.md/) for templates. Never guess names
3. User selects → install → replace tokens — [procedure](references/adopt-procedure.md)
4. Validate refs, Completeness Score — [scoring](references/scoring.md)

Format ref: [template](references/design-md-template.md)

## Update

1. Identify change source (Figma, description, diff)
2. Update changed sections only, preserve rest
3. Append to Known Gaps (create if missing). Confirm before overwrite

## Audit

1. Parse DESIGN.md tokens. Scan code usage
2. Report: Undocumented / Unused / Deviated / Don't violations / Ambiguous (검증 불가 → `[UNVERIFIED]`, Score 분모 제외)

## Rules

- Observable values only. No guessing
- Figma = to-be, code = as-is when conflicting
- Token refs (`{colors.name}`) in body, never raw hex
- Confirm before overwriting existing DESIGN.md
- Audit: match by hex value. Name mismatches = "Deviated"
- Update: change inline hex annotations alongside frontmatter
