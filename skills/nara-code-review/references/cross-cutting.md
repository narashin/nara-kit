# Cross-Cutting Checks

Apply to every agent pass regardless of specialization.

## Log Hygiene

- Duplicate logging: same message logged in multiple places (e.g., helper + caller both log).
- Log level appropriateness: DEBUG for high-frequency, WARNING/ERROR for rare events only.
- Sensitive data in logs: credentials, tokens, connection strings leaking into log output.
- Log noise in loops: per-iteration logging that floods in production.

## Pattern Consistency

- Same file/module using different patterns for the same concern (e.g., mixed error handling styles, inconsistent naming).
- New code diverging from established patterns in surrounding code without justification.
- Constants/defaults that contradict each other across code and config.
- Component design inconsistency: new component deviating from existing structure/naming/prop conventions without justification.
- Reinventing existing components: new component created when an equivalent already exists in the codebase.
- Type duplication: new type defined when an existing type (or a mapped/partial variant) already covers the same shape.
- `as const` overuse: applied where it adds no narrowing benefit — flag if used on mutable structures or where the narrowed literal type is never consumed.
- Magic numbers: numeric literals that should be named constants (thresholds, timeouts, limits, IDs, indices).

## Documentation-Code Alignment

- Default values in code vs. README/CLAUDE.md/config files — must match.
- Docstring return types vs. actual return types.
- Comments describing behavior that no longer matches the code.
- New dependency introduced (package.json, imports of previously unused libraries, new tools/CLIs) without documented justification — flag as Medium if no PR description or comment explains why this library over alternatives.
