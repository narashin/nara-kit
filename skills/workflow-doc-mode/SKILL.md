---
name: workflow-doc-mode
description: >-
  Run documentation-first workflow producing specs, RFCs, design docs, or planning artifacts through structured gates from SoT localization through design shaping.
  USE FOR: "doc mode", "기획 모드", "spec 작성", "RFC", "설계 문서".
  DO NOT USE FOR: direct code implementation, bug fixes, test writing.
---

# Workflow Doc Mode

Run documentation-first workflow after router classifies request as `doc`.

## Use when

- output is spec, RFC, design doc, proposal, architecture note, or planning artifact
- user asks for planning before coding
- request mixes planning and implementation but design intent is not stable yet

## Do not use when

- user asks for direct code, config, test, or bugfix work with stable requirements
- request is purely operational with no design artifact needed

## Decision rules

1. Confirm request belongs to documentation-first workflow.
2. Identify artifact type: `spec`, `rfc`, `design`, or `plan`.
3. Check if external requirements need localization first.
4. Check if design ambiguity needs discovery or product framing.
5. Route in same turn when unambiguous. Hand to `workflow-dev-mode` for implementation.

## Execution

- External SoT exists -> `prep` before design shaping
- Scope or audience unclear -> `ooo interview`
- Trade-off framing matters -> `ooo pm`
- Design must be locked -> `ooo seed`
- Architectural decision point -> `adr`
- Artifact complete -> offer `publish-spec` (dry-run -> confirm -> publish to Confluence)
- Implementation requested -> route to `workflow-dev-mode`

**Load** [references/doc-workflow-details.md](references/doc-workflow-details.md) for routing table, output contract, examples, and hallucination guards.
