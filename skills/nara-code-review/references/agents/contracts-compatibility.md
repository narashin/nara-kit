# Core Agent: contracts-compatibility (ID prefix: CON)

**Always runs.** Focus: types, nullability, API/DTO/serialization contracts, and
backward compatibility. Read-only — never edit code.

## Checks

**Type safety (runtime-crash oriented)**
- TypeScript: `any` abuse, unsafe `as` assertions, missing optional chaining.
- Java: NullPointerException risks, raw types, boxing/unboxing hazards.
- Python: unexpected dynamic type conversions.
- Unhandled parse failures (JSON.parse, parseInt, Number(), date parsing).
- Array/object access without existence check.
- Incomplete union/enum handling (missing exhaustive check).
- Generic type parameter misuse.
- Stringly-typed code: raw strings where constants, enums, string unions, or branded
  types already exist in the codebase.
- Type duplication: new type defined when an existing type (or a mapped/partial
  variant) already covers the same shape.

**Contracts**
- API response type vs actual usage type mismatch.
- DTO/serialization contract changes: renamed/removed fields, optionality flips,
  format changes (date, number precision, casing) that break existing consumers.
- Cross-layer type precision: DB column type vs ORM type vs application logic
  (e.g., MySQL `DATETIME` second precision vs Python `datetime` microsecond —
  equality comparison may silently fail).
- Nullability contract: a field consumers treat as always-present becoming nullable
  (or vice versa) without every consumer updated.

**Backward compatibility**
- Public API signature changes breaking existing callers (search callers before
  claiming safe).
- Wire-format/persisted-data compatibility: old serialized data still deserializable
  after the change.
- Docstring/JSDoc return types vs actual return types; comments describing contracts
  that no longer match the code.

## Not yours

Business-logic correctness → behavior-state. Exception/transaction handling →
resilience-data-integrity. README/config alignment → operations-config.
