# Mock Accuracy Guards

These are the most common causes of false-positive tests (tests that pass but miss real bugs):

| Trap | Correct Pattern |
|------|----------------|
| Single `return_value` for cursor with multiple queries | Use `side_effect = [result1, result2]` |
| Missing thread/lock ownership setup | Set `_lock_owner_tid = threading.get_ident()` or equivalent |
| Patching at wrong module path | Patch where the name is USED, not where it's DEFINED |
| Mock that's too permissive (accepts anything) | Configure mock to reject unexpected calls with `spec=True` |
| Assert only return value, not side effects | Also assert state changes, method calls, cleanup |
| Patching logger to suppress noise | Do NOT patch loggers unless the scenario explicitly asserts on log output. Noisy stderr is acceptable; silent mock hides real call failures |

## Scenario Ownership

When a scenario ID appears in multiple sections (e.g., S04b listed under D5 but also referenced by RT-FC3):
- Implement it in the domain where the SCENARIOS file places it
- If placement is ambiguous, implement in the domain of the METHOD being tested
- Do NOT create duplicate tests in multiple files for the same scenario

## Anti-Patterns

- Do NOT generate all domains at once — domain-by-domain with verification
- Do NOT skip golden sample — even if you "know" pytest/jest patterns
- Do NOT weaken assertions to make tests pass
- Do NOT add `# type: ignore` or `@SuppressWarnings` to silence mock issues
- Do NOT delete or modify existing test assertions
