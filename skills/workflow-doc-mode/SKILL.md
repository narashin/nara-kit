---
name: workflow-doc-mode
description: Use when request is for planning, specification, RFC, design, proposal, or other documentation-first workflow output.
version: 0.1.0
---

# Workflow Doc Mode

## Purpose

Run documentation-first workflow after router classifies request as `doc`.

<prompt-contract>
Input arrives from top-level router after `doc` classification.
Output starts with `### Workflow Intake`, then `### Gate Status`, then `### Next Action` before any routed skill/tool invocation.
Do not emit implementation-only gates unless user explicitly asks to bridge from doc work into dev work.
</prompt-contract>

## Use when

- requested output is spec, RFC, design doc, proposal, architecture note, planning artifact, or decision memo
- user asks for planning before coding
- request mixes planning and implementation, but design intent is not stable yet
- external source-of-truth must be localized before design decisions

## Do not use when

- user asks for direct code, config, test, or bugfix work with stable requirements
- user wants one-shot explanation only
- request is purely operational and does not need design artifact

## Required sequence

1. Confirm documentation goal, audience, and scope
2. Localize source-of-truth when requirements are external or scattered
3. Clarify constraints, success criteria, and open questions
4. Shape design or product framing before locking recommendation
5. Produce accepted approach summary or documentation artifact
6. Route to ADR or RFC step only when decision record is warranted
7. **Offer `publish-spec`** — ask user whether to publish the artifact to Confluence (dry-run → confirm → publish)
8. Stop before implementation unless user explicitly asks to enter dev workflow

## Decision rules

<thinking-sequence>
1. Confirm request belongs to documentation-first workflow.
2. Identify exact artifact needed: spec, RFC, proposal, design note, or planning doc.
3. Check whether external requirements must be localized first.
4. Check whether design ambiguity needs discovery or product framing.
5. Choose next skill/tool and invoke it in same turn when unambiguous.
6. If implementation becomes next step, hand back to dev workflow instead of continuing inline.
</thinking-sequence>

### Artifact type
- `spec`: implementation-shaping document with acceptance boundaries
- `rfc`: decision memo with alternatives and recommendation
- `design`: architecture or flow description
- `plan`: planning artifact before implementation begins

### Mandatory routing table
- external or scattered requirements -> `prep`
- design ambiguity -> `ooo interview`
- product framing or option comparison -> `ooo pm`
- design snapshot needed -> `ooo seed`
- architectural decision record needed -> `adr`
- documentation artifact complete -> `publish-spec` (offer to user, not forced)
- implementation requested after design stabilizes -> `workflow-dev-mode`

## Output contract

Before routing onward, produce:

### Workflow Intake
- Mode: `doc`
- Artifact type
- Scope
- Reasoning bullets

### Gate Status
- source-of-truth localization status
- clarification status
- design shaping status
- documentation artifact status
- **confluence publish status**
- implementation handoff status

### Next Action
- exact skill/command to invoke next
- why now

## Execution behavior

- If external source-of-truth exists, invoke `prep` before design shaping.
- If scope or audience is unclear, invoke `ooo interview`.
- If trade-off framing matters, invoke `ooo pm`.
- If design must be locked into stable artifact, invoke `ooo seed`.
- If work reaches architectural decision point, invoke `adr`.
- If user asks to proceed into implementation after design stabilizes, route to `workflow-dev-mode` instead of embedding dev workflow here.
- After documentation artifact is produced, offer `publish-spec` to publish to Confluence. If user declines, skip silently.

## Hallucination guards

- If required facts are not verified from current inputs, mark them `[UNVERIFIED: requires source confirmation]`.
- If requested artifact type is ambiguous, ask instead of choosing silently.
- If current environment does not confirm skill or command availability, say `[UNVERIFIED: skill or command availability not confirmed]`.
- If design recommendation depends on unstated constraints, surface those constraints explicitly.
- Do not claim implementation readiness unless acceptance criteria and scope boundaries are explicit.

## Stop conditions

- stop and ask when artifact type is unclear
- stop and ask when audience materially changes document shape
- stop and ask when external requirements are missing
- continue without asking only when next documentation gate is unambiguous

## Examples

### Example 1
User: `Write design doc for replacing session storage.`
Route: doc -> `ooo interview` -> design artifact -> optional `adr`.

### Example 2
User: `Draft RFC for tenant-aware auth migration.`
Route: doc -> `prep` when requirements are scattered -> `ooo pm` -> `ooo seed` -> RFC.

### Example 3
User: `Help me plan feature rollout before we code.`
Route: doc -> `ooo interview` -> planning artifact -> handoff to `workflow-dev-mode` only after design stabilizes.

### Example 4
User: `기획문서 써줘. 승인 후 날짜 수정 기능.`
Route: doc -> codebase exploration -> spec artifact -> offer `publish-spec` (dry-run → confirm → publish to Confluence) -> done.
