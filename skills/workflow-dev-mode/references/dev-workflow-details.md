# Dev Mode — Workflow Details

> **Migration note (2026-05)**: thin one-line intent (외부 SoT 없음) is now handled by `ac-draft` instead of `ooo interview`. `ac-draft` writes `docs/requirements.md` directly (no prep needed). `ooo interview` references below remain valid as manual escape when ambiguity exceeds AC scope (e.g. FR ambiguity even with external SoT).

## Required sequence

1. Confirm implementation goal, scope, and acceptance criteria
2. Localize source-of-truth when requirements are external or scattered
3. Run discovery and clarification before code changes when ambiguity remains
4. Perform integration review against existing code and patterns
5. Run gap analysis when current-state vs target-state delta matters
6. Create written implementation plan before execution
7. **Implementation Notes Gate**: Execute 진입 시 `docs/implementation-notes.md` 생성. 모든 변경 응답에 trailing `📝 notes:` 출력. (SKILL.md 참조)
8. Enforce TDD for behavior-changing work where practical
9. Run verification before claiming completion. **verify는 implementation-notes.md 비어 있으면 reject.**
10. Route to evaluation, review, reflect (notes 흡수), ADR, and finish only after prior gates pass

## Mandatory routing table

- external or scattered requirements -> `prep`
- design ambiguity -> `ooo interview`
- product framing or option comparison -> `ooo pm`
- design snapshot needed -> `ooo seed`
- current-state vs target-state delta matters -> `gap`
- implementation about to start -> written implementation plan artifact
- phased or broader execution -> `superpowers:subagent-driven-development`
- lighter fallback execution intentionally chosen -> `ooo run`
- inline-style fallback explicitly chosen -> `ooo auto`
- before completion claim -> `ooo evaluate`, then `code-review`
- architectural decision happened -> `adr`
- test scenario discovery needed -> `test-discover`
- existing scenarios need review -> `test-verify`
- work fully verified and branch-ready -> branch finish workflow

## Output contract

Before routing onward, produce:

### Workflow Intake
- Mode: `dev`
- Scope
- Reasoning bullets

### Gate Status
- source-of-truth localization status
- discovery status
- integration review status
- gap status
- planning status
- **implementation-notes status (file existence, total entries, last trailing status)**
- TDD status
- verification status

### Next Action
- exact skill/command to invoke next
- why now

## Hallucination guards

- If acceptance criteria are missing, do not infer them silently.
- If codebase fit is unknown, inspect before endorsing new abstraction.
- If verification cannot be executed, state missing proof explicitly.
- If automated test is not practical, state why TDD exception applies.
- If workflow gate is skipped by user choice, name skipped gate and risk explicitly.
- If current environment does not confirm skill or command availability, say `[UNVERIFIED: skill or command availability not confirmed]`.

## Stop conditions

- stop and ask when success criteria are unclear
- stop and ask when doc and dev paths are both plausible and materially different
- stop and ask when required external input or credential is missing
- **stop when verify is requested but `docs/implementation-notes.md` is missing/empty** — instruct user to fill notes first
- continue without asking only when next implementation gate is unambiguous

## Examples

### Example 1
User: `Fix API rate-limit bug from analysis to code fix.`
Route: dev -> medium -> `ooo interview` -> written implementation plan artifact -> TDD -> `superpowers:subagent-driven-development` -> `ooo evaluate`.

### Example 2
User: `Add audit log export API.`
Route: dev -> `gap` -> written implementation plan artifact -> `superpowers:subagent-driven-development` -> verification.

### Example 3
User: `Implement multi-tenant rollout across services.`
Route: dev -> large -> stronger `ooo interview` / `ooo pm` discovery -> phased plan -> `superpowers:subagent-driven-development`.
