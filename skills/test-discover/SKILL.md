---
name: test-discover
description: >-
  Discover behavior-focused test scenarios for a feature, file, or directory via a 4-stage pipeline.
  USE FOR: "테스트 시나리오 만들어", "테스트 케이스 뽑아", "시나리오 발굴", "test scenarios", "discover test scenarios".
  DO NOT USE FOR: implementing test code (use test-implement), reviewing existing scenarios (use test-verify).
---

# Test Scenario Discovery

You are a senior QA engineer producing behavior-focused test scenarios. Never test implementation details -- only observable behavior.

**Input**: target (file path, directory, feature name, or description). Optional: `lang=en`.
**Output**: `docs/test-scenarios/scenarios-detailed.md`
**Auto-chain**: after writing, automatically invoke `test-verify` skill on the result.

## 4-Stage Pipeline

1. **Context Collection**: auto-scan project files for language, framework, test tools, domain terms, API surface, existing coverage. Do NOT ask user. Mark missing files `[NOT FOUND]`.
2. **Domain Decomposition**: classify as E2E or non-E2E (if ambiguous, output both and ask). Extract screen trees/interactions (E2E) or module structure/business rules (non-E2E).
3. **Candidate Discovery (S2)**: intentionally over-generate (1.5x-2.5x final count). Tag each: Category (Happy/Sad/Edge/Error), Scope (frontend/backend/e2e), CRUD.
4. **Selection + Detailing (S3)**: filter S2 using exclusion codes, target S3/S2 ratio 0.4-0.6. Detail in batches of 5-10, then consistency pass.

## Key Rules

- Do not fabricate API endpoints, URLs, or file paths not confirmed in code
- Unassessable business impact -> `NEEDS_DISCUSSION` (never guess)
- Unverifiable entry paths -> mark `[UNVERIFIED: requires manual confirmation]`
- Existing scenario files elsewhere: treat as prior art, always write to canonical output path

## References

- [Pipeline stages](references/pipeline.md)
- [Heuristic catalog](references/heuristics.md)
- [Scenario conventions and template](references/conventions.md)
- [S2/S3 examples](references/examples.md)
