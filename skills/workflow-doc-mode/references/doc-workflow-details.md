# Doc Mode — Workflow Details

## Required sequence

1. Confirm documentation goal, audience, and scope
2. Localize source-of-truth when requirements are external or scattered
3. Clarify constraints, success criteria, and open questions
4. Shape design or product framing before locking recommendation
5. Produce accepted approach summary or documentation artifact
6. Route to ADR or RFC step only when decision record is warranted
7. **Offer `publish-spec`** — ask user whether to publish the artifact to Confluence (dry-run -> confirm -> publish)
8. Stop before implementation unless user explicitly asks to enter dev workflow

## Artifact types

- `spec`: implementation-shaping document with acceptance boundaries
- `rfc`: decision memo with alternatives and recommendation
- `design`: architecture or flow description
- `plan`: planning artifact before implementation begins

## Mandatory routing table

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
- confluence publish status
- implementation handoff status

### Next Action
- exact skill/command to invoke next
- why now

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
Route: doc -> codebase exploration -> spec artifact -> offer `publish-spec` (dry-run -> confirm -> publish to Confluence) -> done.
