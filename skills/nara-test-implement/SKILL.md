---
name: nara-test-implement
description: >-
  Implement production-grade test code from a test scenarios document, matching existing project conventions.
  USE FOR: "테스트 코드 짜줘", "시나리오 구현해", "implement test scenarios", "write tests from scenarios", "generate test code".
  DO NOT USE FOR: discovering test scenarios (use nara-test-discover), reviewing test quality (use nara-test-verify).
---

# Test Scenario Implementation

Senior test engineer converting scenario docs into production test code, matching existing project conventions.

**Input**: scenarios file path. **Output**: test files matching conventions, all passing.

## Core Rules

1. **Domain-by-domain**: implement ONE domain, verify pass, then next.
2. **Golden sample first**: read 2-3 existing test files for import/mock/fixture/assertion patterns before coding.
3. **Auto-detect tooling**: scan project files (package.json, pyproject.toml, pom.xml, existing tests).
4. **Priority order**: High -> Medium -> Low, dependencies first regardless of priority.
5. **Existing file safety**: re-read before editing, add new blocks (preserve existing tests), run ALL tests after.
6. **Max 3 retries per domain**: 3 fails -> report and ask user.
7. **Keep assertions strict** — resolve type errors at source, avoid suppressions (`# type: ignore`, `@SuppressWarnings`).

## Pre-execution gate

골든 샘플 읽은 직후, 첫 테스트 코드 작성 전 plan 출력 + AskUserQuestion 승인. [상세](references/pre-execution.md).

## After all domains pass

Run full test suite, report summary (domains, tests added, passing), fix regressions before reporting done.

## References

- [Pipeline (4 phases)](references/pipeline.md)
- [Mock guards + anti-patterns](references/mock-guards.md)
- [Pre-execution gate](references/pre-execution.md)
