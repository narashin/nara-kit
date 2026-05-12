---
name: workflow-doc-mode
description: >-
  Run documentation-first workflow producing specs, RFCs, design docs, or planning artifacts.
  Routes by requirement clarity: clear → brainstorming → prep → spec, vague → ooo interview → prep → spec.
  USE FOR: "doc mode", "기획 모드", "spec 작성", "RFC", "설계 문서".
  DO NOT USE FOR: direct code implementation, bug fixes, test writing.
---

# Workflow Doc Mode

Documentation-first workflow after router classifies request as `doc`.

## Clarity Gate

Before routing, assess requirement clarity:

| Signal | Clear | Vague |
|--------|-------|-------|
| User describes feature with acceptance criteria | ✓ | |
| External SoT available (Jira, Figma, PRD) | ✓ | |
| User says "뭔가 만들고 싶은데" / "아이디어 단계" | | ✓ |
| No concrete scope, audience, or constraints | | ✓ |

## Routes

**Clear path** (requirements stable):
1. External SoT exists → `prep` first
2. `superpowers:brainstorming` — explore design options
3. `prep` — persist brainstorm output to `docs/requirements.md`
4. Produce artifact (spec/RFC/design/plan)

**Vague path** (requirements need discovery):
1. `ooo interview` — clarify scope, audience, constraints
2. `prep` — persist interview output to `docs/requirements.md`
3. `ooo pm` — product framing (if trade-off comparison needed)
4. `ooo seed` — lock design snapshot (if design must be frozen)
5. Produce artifact

**Both paths converge**: `prep` always persists to `docs/requirements.md` before artifact creation.

## Post-artifact

- Architectural decision → `adr`
- Publish to wiki → offer `publish-spec` (dry-run → confirm → publish)
- Implementation requested → handoff to `workflow-dev-mode`
- Session end → `reflect`

**Load** [references/doc-workflow-details.md](references/doc-workflow-details.md) for routing table, output contract, examples, and hallucination guards.
