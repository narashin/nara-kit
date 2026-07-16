# Workflow Orchestrator — Routing Details

## Use when

- user asks to "handle this properly", "follow workflow", "take this from requirements to implementation", or similar end-to-end requests
- user says things like "이거 제대로 진행해줘", "설계부터 검증까지 밟아줘", "바로 코딩 말고 절차대로 해줘"
- request needs workflow routing instead of direct ad hoc execution

## Do not use when

- user asks for tiny one-off answer with no workflow expectation
- user explicitly asks for a single isolated action only
- user already chose and invoked a narrower workflow skill for exact next step
- user only wants direct explanation, lookup, or one-shot edit with no workflow routing

## Routing table

- documentation-first request -> `nara-workflow-doc-mode`
- implementation-first request -> `nara-workflow-dev-mode`
- mixed request with unstable design -> `nara-workflow-doc-mode`
- mixed request with stable design and explicit implementation ask -> `nara-workflow-dev-mode`

### Terminal outcomes (route may refuse)

- external SoT not yet localized -> `need-sot`: recommend `/nara-prep` first (promotes the "source-of-truth localization status" gate to a labeled outcome)
- blocking decision unresolved (owner/product judgment, alternatives not chosen) -> `decision`: recommend owner decision or `nara-grill`; do not force a workflow
- no matching nara-kit skill/mode -> recommend direct execution (no-force-fit); never force a request into doc/dev

## Output contract

Before routing onward, produce:

### Workflow Intake
- Mode
- Scope
- Reasoning bullets

### Gate Status
- source-of-truth localization status
- mode-specific workflow selection status
- ambiguity status
- handoff readiness status

### Next Action
- exact skill/command to invoke
- why now

## Stop conditions

- stop and ask when success criteria are unclear
- stop and ask when `doc` and `dev` are both plausible and choice materially changes work
- stop and ask when required external input or credential is missing
- continue without asking only when route is unambiguous

## Hallucination guards

- If mode is unclear, ask instead of guessing.
- If artifact or implementation intent is unclear, ask one focused question.
- If current environment does not confirm skill or command availability, say `[UNVERIFIED: skill or command availability not confirmed]`.
- If current repo state conflicts with remembered workflow context, trust current repo state and update recommendation.

## Examples

### Example 1
User: `Take this API rate-limit bug from analysis to fix.`
Route: classify `dev` -> `nara-workflow-dev-mode`.

### Example 2
User: `I need a design doc for replacing session storage.`
Route: classify `doc` -> `nara-workflow-doc-mode`.

### Example 3
User: `Plan multi-tenant rollout, then implement it.`
Route: classify mixed request -> start with `nara-workflow-doc-mode`, then hand off to `nara-workflow-dev-mode` after design stabilizes.
