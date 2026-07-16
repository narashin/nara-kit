# Dev Mode — Workflow Details

Thin one-line intent (외부 SoT 없음) is handled by `nara-ac-draft`, which writes `docs/requirements.md` directly (no prep needed).

## Required sequence

1. Confirm implementation goal, scope, and acceptance criteria
2. Localize source-of-truth when requirements are external or scattered
3. Run discovery and clarification before code changes when ambiguity remains
4. Perform integration review against existing code and patterns
5. Run gap analysis when current-state vs target-state delta matters
6. Create written implementation plan before execution
7. **Implementation Notes Gate (scope-scaled)**: `medium`/`large`만 — Execute 진입 시 `docs/implementation-notes.md` 생성 + 변경 응답에 trailing `📝 notes:`. `small`은 skip. (SKILL.md 참조)
8. Enforce TDD for behavior-changing work where practical
9. Run verification before claiming completion. **verify는 (medium/large) implementation-notes.md 비어 있으면 reject. small scope는 notes gate 미적용.**
10. Route to review, reflect (notes 흡수), ADR (구조 결정 시만), and finish only after prior gates pass. (evaluation step removed — AI-as-judge anti-pattern.)

## Mandatory routing table

- external or scattered requirements -> `nara-prep`
- design ambiguity (large/greenfield) -> `nara-grill` (조건부)
- current-state vs target-state delta matters -> `nara-gap`
- implementation about to start -> `nara-plan` (`docs/plan.md` 수직 작업 단위)
- phased or broader execution -> `nara-implement` (delegated 모드)
- before completion claim -> `nara-code-review`
- architectural decision happened -> `nara-adr`
- test scenario discovery needed -> `nara-test-discover`
- existing scenarios need review -> `nara-test-verify`
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
- **implementation-notes status (scope; medium/large: file existence, total entries, last trailing status; small: skipped)**
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
- **stop when verify is requested (medium/large) but `docs/implementation-notes.md` is missing/empty** — instruct user to fill notes first. (small scope: no stop.)
- continue without asking only when next implementation gate is unambiguous

## Examples

### Example 1
User: `Fix API rate-limit bug from analysis to code fix.`
Route: dev -> medium -> `nara-ac-draft` -> `nara-plan` -> TDD -> `nara-implement` -> `nara-code-review`.

### Example 2
User: `Add audit log export API.`
Route: dev -> `nara-gap` -> `nara-plan` -> `nara-implement` -> verification.

### Example 3
User: `Implement multi-tenant rollout across services.`
Route: dev -> large -> stronger `nara-ac-draft` discovery -> `nara-plan` (phased) -> `nara-implement` (delegated).
