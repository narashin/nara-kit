# Test Implementation Pipeline

## Pipeline Overview

```dot
digraph pipeline {
  rankdir=LR;
  detect [label="Phase 0\nDetect"];
  golden [label="Phase 1\nGolden Sample"];
  implement [label="Phase 2\nImplement\n(per domain)"];
  verify [label="Phase 3\nVerify\n(per domain)"];
  
  detect -> golden -> implement -> verify;
  verify -> implement [label="fail\n(fix + retry)"];
}
```

## Phase 0: Detection

Auto-detect from project files. Do NOT ask user.

| Signal | Extract |
|--------|---------|
| `package.json` scripts.test | jest, vitest, mocha, playwright |
| `pyproject.toml`, `requirements*.txt`, `pytest.ini` | pytest |
| `pom.xml`, `build.gradle` | junit, testng |
| `tsconfig.json`, `jest.config.*`, `vitest.config.*` | TS test config |
| Existing test files (glob: `*test*`, `*spec*`, `*Test*`) | naming pattern, directory structure |

Output (internal): `{ language, framework, testRunner, testCommand, testFilePattern, testDir }`

## Phase 1: Golden Sample Extraction

Read 2-3 existing test files from the project. Extract:

1. **File structure**: imports, class/describe grouping, setup/teardown pattern
2. **Mock pattern**: how mocks are created (unittest.mock, jest.mock, Mockito, etc.)
3. **Fixture pattern**: shared data setup (pytest fixtures, beforeEach, @BeforeEach)
4. **Assertion style**: assert vs expect vs assertThat
5. **Instantiation pattern**: how SUT is created without dependencies (e.g., `object.__new__()`)

If scenarios file has "Implementation Notes" or "구현 주의사항" section, load it as **mandatory guards**.

## Phase 2: Domain-by-Domain Implementation

### Priority Order

1. Parse scenario file for priority groups (🔴 High → 🟡 Medium → 🟢 Low)
2. Within each priority, check dependency chains — implement dependencies first regardless of priority
3. Process ONE domain at a time

### Per Domain

For each domain:

1. **Read scenarios** for this domain from the scenarios file
2. **Decide target file**:
   - If existing test file covers this domain → modify it (add new test class/describe block)
   - If new domain → create new file following golden sample naming pattern
3. **Generate test code** following golden sample patterns exactly:
   - Same import style
   - Same mock/fixture patterns
   - Same assertion style
   - Same class/function naming convention
4. **Apply mandatory guards** from scenarios file (mock accuracy warnings, setup gotchas)

### Existing File Rules

When modifying existing test files:
- Re-read the file immediately before editing (context decay protection)
- Add new test classes/blocks — do NOT modify existing tests
- Re-run ALL tests in the file after modification (not just new ones)
- If any existing test breaks → revert and investigate

## Phase 3: Per-Domain Verification

After generating/modifying tests for ONE domain:

1. Run test command for that specific file
2. **All tests pass** → mark domain complete, proceed to next
3. **Any test fails** → analyze error, fix, re-run (max 3 attempts)
4. **3 failures** → report to user with error details, ask before continuing

```dot
digraph verify {
  run [label="Run tests"];
  pass [label="Pass?" shape=diamond];
  fix [label="Fix"];
  count [label="Attempt ≤ 3?" shape=diamond];
  done [label="Domain\ncomplete"];
  ask [label="Ask user"];
  
  run -> pass;
  pass -> done [label="yes"];
  pass -> count [label="no"];
  count -> fix [label="yes"];
  count -> ask [label="no"];
  fix -> run;
}
```

## Completion

After all domains pass:

1. Run full test suite (all test files, not just new ones)
2. Report summary: domains implemented, tests added, tests passing
3. If any regression in existing tests → fix before reporting done
