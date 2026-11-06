---
name: nara-test-implement
description: >-
  Implement production-grade test code from a test scenarios document, matching existing project conventions.
  USE FOR: "테스트 코드 짜줘", "시나리오 구현해", "implement test scenarios", "write tests from scenarios", "generate test code".
  DO NOT USE FOR: discovering test scenarios (use nara-test-discover), reviewing test quality (use nara-test-verify).
---

# Test Scenario Implementation

> 출력 형식은 [nara-kit 출력 계약](../nara-now/references/output-contract.md)을 따른다. 이 본문이 다르게 정한 곳은 본문이 우선한다. 파일이 없으면(단독 설치) 이 줄은 건너뛴다.

**Input**: scenarios file path. **Output**: runnable test files mapped to scenarios. Red is reported, never forced green.

## Core Rules

1. **Domain-by-domain**: implement ONE domain, verify it runs, then next.
2. **Golden sample first**: read 2-3 existing tests for import/mock/fixture/assertion patterns.
3. **Auto-detect tooling** from project files (package.json, pyproject.toml, pom.xml).
4. **Priority order**: High -> Medium -> Low, dependencies first.
5. **Existing file safety**: re-read before editing, add blocks without changing existing tests, run ALL tests after.
6. **Max 3 retries per domain, test-code errors only**. A failing test is recorded red; never edit production code or loosen the test to make it green.
7. **Keep assertions strict** — resolve type errors at source, avoid suppressions (`# type: ignore`, `@SuppressWarnings`).
8. **Append `## Test Mapping` to the scenarios file**, one row per scenario; unimplementable ones as `[BLOCKED: 이유]`.

## Pre-execution gate

골든 샘플을 읽은 뒤 첫 테스트 작성 전에 plan을 내고 승인을 기다린다. [상세](references/pre-execution.md).

## After all domains are verified

Full suite, mapping table, stage the test files (no commit), report red / green / blocked: [steps](references/pipeline.md#completion).

## References

[Pipeline](references/pipeline.md) · [Mock guards](references/mock-guards.md) · [Pre-execution](references/pre-execution.md)
