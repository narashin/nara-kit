# Test Discover Pipeline

## Stage 0: Context Collection

Automatically scan the project to build execution context. Do NOT ask the user.

| Target | What to extract |
|--------|----------------|
| `package.json`, `pyproject.toml`, `pom.xml` | Language, framework, test tools |
| `__tests__/`, `tests/`, `e2e/`, `cypress/`, `playwright/` | Existing test patterns, naming conventions |
| `openapi.yaml`, `*.graphql`, GraphQL schema files | API endpoints, entities, request/response shapes |
| `README.md`, `docs/` | Domain terms, feature descriptions |
| `.env.example` | Runtime env vars, external dependencies |
| `docs/test-scenarios/*.md` | Existing scenarios (avoid duplication) |

If a scan target does not exist, mark `[NOT FOUND]` -- do not infer contents.

Output (internal): language/framework, test tooling, domain terms, API surface, existing coverage.

## Stage 1: Domain Decomposition

### Decision Sequence

1. Does the target contain UI components, page routes, or browser-facing code?
2. Does the project include cypress/playwright/selenium or other E2E tools?
3. Did the user explicitly specify E2E, unit, or integration scope?
4. If all unclear -> default to non-E2E, tag E2E candidates separately.

### E2E Decomposition Output

- **Screen tree**: page hierarchy with routes
- **Interaction inventory**: per-screen user actions (click, input, navigate, upload, etc.)
- **User journeys**: end-to-end flows crossing multiple screens
- **Permission x screen matrix**: which roles access which screens/actions
- **UI-observable state machine**: states visible to user (loading, empty, error, success, disabled)

### Non-E2E Decomposition Output

- **Module/package structure**: key files and responsibilities
- **Function/method signatures**: public API surface
- **Input/output domains**: valid/invalid ranges, expected output shapes
- **External dependencies**: DB, APIs, message queues, file system
- **Business rules/invariants**: domain constraints that must hold

If ambiguous between E2E and non-E2E, output BOTH and ask user to select.

## Stage 2: Scenario Candidate Discovery (S2)

Intentionally over-generate. Target: 1.5x-2.5x the expected final count.

Tag each candidate: **Category** (`Happy`|`Sad`|`Edge`|`Error`), **Scope** (`frontend`|`backend`|`e2e`), **CRUD** (`Create`|`Read`|`Update`|`Delete`|`N/A`).

Internal format:
```
S2-001 [Happy] [backend] [Create] description
S2-002 [Sad]   [backend] [Create] description
```

## Stage 3: Selection (S2 -> S3)

### Selection Sequence

1. Remove DUPLICATE (overlapping verification area)
2. Remove LOWER_LAYER_BETTER (unit test sufficient)
3. Remove OUT_OF_SCOPE (outside change boundary)
4. Apply IMPACT x FEASIBILITY matrix to remaining
5. NEEDS_DISCUSSION items -> separate section

### Exclusion Reason Codes

| Code | Meaning |
|------|---------|
| `LOWER_LAYER_BETTER` | Unit/integration test covers this more efficiently |
| `DUPLICATE` | Another scenario already verifies this behavior |
| `LOW_IMPACT` | Business impact too low |
| `INFEASIBLE` | Cannot prepare environment/data |
| `RARE_PATH` | Occurrence frequency extremely low |
| `OUT_OF_SCOPE` | Outside target feature's change boundary |
| `NEEDS_DISCUSSION` | Cannot determine without human judgment |

**Target ratio**: S3/S2 = 0.4-0.6. If outside range, re-evaluate.

If business impact cannot be assessed, classify as `NEEDS_DISCUSSION` -- never guess impact.

## Stage 4: Batch Detailing + Consistency Pass

### 4-A: Batch Detailing

Process S3 scenarios in chunks of 5-10. See references/conventions.md for mandatory fields and step conventions.

### 4-B: Consistency Pass

After all chunks, scan for:
- Inconsistent ID numbering
- Mismatched dependency references
- Missing verification markers
- Inconsistent data token prefixes
- Missing wait times on E2E scenarios

Auto-fix obvious issues. Flag ambiguous items with `[REVIEW: ...]`.

If entry path or URL cannot be confirmed from code, mark with `[UNVERIFIED: requires manual confirmation]`.
