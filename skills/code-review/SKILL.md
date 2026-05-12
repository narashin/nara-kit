---
name: code-review
description: >
  Multi-agent parallel code review + auto-fix for local commits.
  5 independent specialist agents (logic, type-safety, error-handling, architecture, security/performance)
  analyze code in parallel, filter findings by confidence score, and auto-fix issues.
  Use when: "리뷰해줘", "코드 검수", "버그 찾아줘", "review code", "check for bugs",
  "audit code", "cleanup", or after finishing code changes before committing.
  Supports all stacks: Next.js, React, Node.js, Java/Spring, Python, etc.
---

# Code Review — 5-Agent Iterative Review & Auto-Fix

5 independent specialist agents review code in parallel, fix issues, then **re-review the fixes** in an iterative loop until the code converges to a clean state (or max rounds reached).

**IMPORTANT: All report output MUST be in Korean (한국어). Internal analysis can be in any language, but the final report shown to the user must be entirely in Korean.**

See `references/stack-specific.md` for per-stack checklists.

---

## Phase 1: Collect Changes

```bash
git diff HEAD~1 --stat
git diff HEAD~1
git diff HEAD~1 --name-only
git log HEAD~1..HEAD --pretty=format:"%H %s"
```

If staged changes exist, use `git diff HEAD` instead.
If no git changes found, review files the user mentioned or files edited earlier in this conversation.

**If `$ARGUMENTS` is `help` or `--help`, skip all phases and print the following usage guide in Korean, then stop:**

```
🔍 /code-review — 5-Agent Iterative Code Review & Auto-Fix

사용법:
  /code-review                    최근 1커밋 리뷰 + 자동 수정 (기본)
  /code-review 3                  최근 3커밋 리뷰
  /code-review main               main 브랜치 대비 리뷰
  /code-review help               이 도움말 출력

옵션:
  --report-only                   수정 없이 리포트만 출력
  --show-all                      신뢰도 필터 없이 전체 이슈 출력
  --threshold=N                   신뢰도 기준 변경 (기본: 80)
  --max-rounds=N                  리뷰-수정 반복 횟수 (기본: 3, 최대: 5)
  --focus=<agent>                 특정 에이전트만 실행
  --no-save                       파일 저장 없이 콘솔 출력만

에이전트 목록 (--focus에 사용):
  logic                           로직 오류 & 엣지 케이스
  type-safety                     타입 안전성 & 런타임 에러
  error-handling                  에러 핸들링 & ACID & 복원력
  architecture                    아키텍처 & 호환성 & 코드 재활용
  security-performance            보안 & 성능

출력:
  리포트는 ./docs/review/YYMMDD-<설명>.md 로 자동 저장됨
  --no-save로 저장 없이 콘솔만 출력 가능

조합 예시:
  /code-review --report-only --show-all       전체 이슈 리포트만 (수정 없음)
  /code-review 5 --threshold=60               최근 5커밋, 낮은 기준으로 폭넓게
  /code-review main --focus=error-handling    main 대비 에러 핸들링만 집중 리뷰
  /code-review --max-rounds=5                 최대 5라운드 반복으로 꼼꼼하게
  /code-review --no-save                      파일 저장 없이 빠른 리뷰
```

---

Argument parsing:
- Empty `$ARGUMENTS`: `HEAD~1` (last 1 commit)
- Number: `HEAD~N` (last N commits)
- Branch name: `main..HEAD` etc.
- `--show-all`: show all findings regardless of confidence
- `--threshold=N`: change confidence threshold (default 80)
- `--focus=<agent>`: run only a specific agent
- `--report-only`: report only, no auto-fix
- `--max-rounds=N`: max review-fix iterations (default 3, hard cap 5)
- `--no-save`: skip saving report to file, console output only

## Phase 2: Gather Context

For each changed file:
1. Read full file content (diff alone is insufficient)
2. Check imported modules and type definitions
3. Read project CLAUDE.md and .claude/rules/ if present
4. Check related test files
5. **Search for reusable existing code** — scan utility directories, shared modules, and adjacent files with `grep -r`
6. Detect tech stack, then read the relevant section from `references/stack-specific.md`

## Phase 3: Launch 5 Review Agents in Parallel

**Use the Agent tool to launch all 5 agents concurrently in a single message.**
Pass each agent the full diff and gathered context.

All agents output findings in this format:

```json
{
  "reviewer": "agent-id",
  "severity": "critical | warning | suggestion",
  "confidence": 0-100,
  "file": "filepath",
  "line_range": "start-end",
  "title": "issue title",
  "description": "why this is a problem",
  "impact": "possible incident scenario",
  "suggestion": "concrete fix code",
  "auto_fixable": true | false
}
```

**Confidence rules**: 80+ only for defects directly verifiable in code. Speculative concerns stay at 50 or below.

---

### 🔴 Agent 1: Logic & Edge Case Analyst (reviewer: "logic")

Focus: **logical errors and missing edge cases only.**

Check for:
- Business logic matches commit intent
- Boundary values: null, undefined, empty array/string, 0, negative, MAX_INT
- Off-by-one errors
- Incomplete branching (missing else/default/exhaustive switch)
- Async race conditions
- Loop termination
- Data transformation loss/corruption
- Implicit type coercion
- **Cross-layer type precision**: DB column type vs ORM type vs application logic (e.g., MySQL `DATETIME` second precision vs Python `datetime` microsecond — equality comparison may silently fail)
- **TOCTOU**: pre-checking file/resource existence before operating — should operate directly and handle the error instead
- **Missing change-detection guard**: triggering updates when nothing actually changed — add early return on same value

---

### 🟡 Agent 2: Type Safety & Runtime Error Hunter (reviewer: "type-safety")

Focus: **type issues that will crash at runtime.**

Check for:
- TypeScript: `any` abuse, unsafe `as` assertions, missing optional chaining
- Java: NullPointerException risks, raw types, boxing/unboxing hazards
- Python: unexpected dynamic type conversions
- API response type vs actual usage type mismatch
- Unhandled parse failures (JSON.parse, parseInt, etc.)
- Array/object access without existence check
- Incomplete union/enum handling (missing exhaustive check)
- Generic type parameter misuse
- **Stringly-typed code**: using raw strings where constants, enums, string unions, or branded types already exist in the codebase

---

### 🟢 Agent 3: Error Handling & Resilience Auditor (reviewer: "error-handling")

Focus: **graceful error handling verification.**

Check for:
- try-catch scope appropriateness (too broad or too narrow)
- Swallowed errors (empty catch, console.log-only catch)
- Missing network/IO error handling
- DB transaction rollback on failure
- ACID violations:
  - Atomicity: partial failure breaks consistency
  - Consistency: data integrity constraint violations
  - Isolation: dirty read / phantom read under concurrent access
  - Durability: data loss after commit
- Retry logic necessity (idempotency guarantee)
- User-facing error messages vs internal log separation
- Missing finally/cleanup (resource release)
- Spring: @Transactional propagation, missing rollbackFor
- Promise/async error propagation path
- **Same-reference return ignored**: wrapper function takes reducer/updater callback but ignores the callback's "no change" signal (same reference return), triggering unnecessary updates

---

### 🔵 Agent 4: Architecture & Compatibility Guardian (reviewer: "architecture")

Focus: **codebase compatibility and design quality.**

**Code Reuse (top priority)**:
- Search if similar utilities/helpers/components already exist in the project
- Scan utility directories, shared modules, adjacent files
- Detect inline logic replaceable by existing utils: hand-rolled string manipulation, manual path handling, custom env checks, ad-hoc type guards
- Flag new functions that duplicate existing functionality — suggest the existing one

**Design Quality**:
- Consistency with existing code patterns/conventions
- Dependency direction (circular dependency detection)
- Separation of concerns (SRP violations)
- API contract changes breaking backward compatibility
- Over-abstraction / over-engineering
- File/folder structure convention violations

**Hacky Pattern Detection**:
- Redundant state: state duplicating existing state, cached values derivable from other state, observers/effects that could be direct calls
- Parameter sprawl: adding parameters instead of generalizing/restructuring
- Copy-paste with slight variation: near-duplicate blocks that should be unified
- Leaky abstractions: exposing internals or breaking existing abstraction boundaries
- Unnecessary JSX nesting: wrapper elements adding no layout value — check if inner component props already handle it

**Infra & Documentation Consistency**:
- Dockerfile: directories created by `mkdir` must match paths actually used in application code (env var defaults, config output dirs)
- README/docs: architecture descriptions (directory structure, file patterns, import paths) must match actual code behavior — flag outdated or unimplemented designs documented as current
- Helm/K8s: env vars in values.yaml must correspond to `os.getenv()` calls in code; port numbers must match `EXPOSE` and listen addresses
- .gitignore: must not exclude files that are tracked and needed (or vice versa)

**Stack-specific**:
- Spring: Bean scope misuse, circular dependencies
- React: component split granularity, props drilling vs context

---

### 🟣 Agent 5: Security & Performance Sentinel (reviewer: "security-performance")

Focus: **security vulnerabilities and performance bottlenecks.**

**Security**:
- Injection attacks: SQL Injection, XSS, CSRF, Command Injection
- Missing auth/authorization on API endpoints
- Sensitive data exposure (logs, error messages, hardcoded secrets)
- Missing input validation/sanitization

**Performance — Unnecessary Work**:
- Redundant computations, repeated file reads, duplicate network/API calls, N+1 patterns
- **Missed concurrency**: independent sequential operations that could run in parallel (Promise.all, CompletableFuture, etc.)
- **Hot-path bloat**: blocking work added to startup or per-request/per-render hot paths
- **Recurring no-op updates**: unconditional state updates in polling loops, intervals, event handlers — add change-detection guard
- **Overly broad operations**: reading entire files/lists when only a portion is needed

**Memory**:
- Unbounded data structures, missing cleanup, event listener leaks, unreturned connections
- Unnecessary re-renders (React)
- OOM risk on large data processing

**Other**:
- Caching strategy appropriateness
- Bundle size impact
- Java: Stream abuse, excessive synchronized, GC pressure patterns
- DB: missing index usage, full table scan risk

---

## Phase 4: Aggregate & Filter

After all agents complete:

1. Include only findings with **confidence ≥ threshold** (default 80)
2. If multiple agents flag the same location for the same issue → boost confidence & merge
3. Sort by severity: critical → warning → suggestion
4. **False positive handling**: if a finding is a false positive or not worth fixing, skip it and note the reason briefly. Do not argue with the finding — just skip.

## Phase 5–7: Iterative Fix-Review Loop

This skill uses an iterative convergence loop. After fixing issues, the code is re-reviewed to catch regressions or new issues introduced by the fixes. The loop repeats until the code is clean or the max iteration limit is reached.

**Max iterations**: 3 (override with `--max-rounds=N`, hard cap at 5)

### Phase 5: Auto-Fix (per round)

Unless `--report-only` is set, directly fix issues where `auto_fixable: true`.

Fix order:
1. **Critical** first
2. **Warning** next
3. **Suggestion** — only fix when clearly beneficial. If uncertain, leave in report only.

Fix principles:
- Match existing code style/conventions
- Run lint/typecheck after fixes if available
- Scope fixes to the issue only — no unrelated refactoring
- **Track every fix** with file path, line, and what changed for the final report

### Phase 6: Re-Review (convergence check)

After all fixes in the current round are applied:

1. Run `git diff` on the fixed files to capture what changed in this round
2. **Re-launch the 5 agents in parallel** via `Agent`, passing ONLY the new diff (fixes from this round) plus full file context
3. Agents focus on:
   - Did the fix introduce a NEW bug or regression?
   - Did the fix break something that was working before?
   - Are there remaining issues that were missed in the previous round?
   - Did the fix create new type errors, missing imports, or broken references?
4. Aggregate and filter results (same rules as Phase 4)

**Convergence criteria — the loop STOPS when ANY of these is true:**
- ✅ **Clean**: No critical or warning findings with confidence ≥ threshold → code is clean
- ✅ **Max rounds reached**: Hit the iteration limit (default 3)
- ✅ **No progress**: Same issues keep reappearing across rounds (fix is not resolving them) → stop and report as manual-fix-needed
- ✅ **Only suggestions remain**: No critical/warning, only low-severity suggestions

If not converged, go back to Phase 5 for the next round.

### Phase 7: Final Report (한국어로 출력 + 파일 저장)

**Save the report as a markdown file:**
- Directory: `./docs/review/`
- Filename: `YYMMDD-<short-description>.md` (e.g., `260319-fix-auth-validation.md`)
- Use the same date-based naming convention as PLAN files
- Print the file path at the end so the user can find it
- If `--no-save` flag is set, skip file saving and only print to console

```
╔══════════════════════════════════════════════════╗
║          🔍 CODE REVIEW REPORT                   ║
║          5-Agent Iterative Review & Auto-Fix     ║
╠══════════════════════════════════════════════════╣
║ 대상: {git range}                                ║
║ 변경 파일: {N}개                                  ║
║ 에이전트: 5 agents (parallel)                     ║
║ 신뢰도 기준: ≥{threshold}                         ║
║ 라운드: {current}/{max} ({converged/stopped})     ║
╚══════════════════════════════════════════════════╝

📊 요약
━━━━━━
🔴 Critical: N건  🟡 Warning: N건  💡 Suggestion: N건
✅ 자동 수정: N건  ⏭️ Skip (오탐): N건
🔄 라운드: {N}회 (수렴 여부: {✅ Clean / ⚠️ Max rounds / 🔁 No progress})

🔄 라운드별 이력
━━━━━━━━━━━━━━━
Round 1: 발견 N건 → 수정 N건 → 잔여 N건
Round 2: 발견 N건 → 수정 N건 → 잔여 N건
Round 3: 발견 0건 ✅ Clean

✅ 자동 수정 완료 (전체 라운드 누적)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[F-1] {제목} (Round {N})
  📍 {파일}:{라인}
  🏷️ Agent: {reviewer} | 신뢰도: {N}/100
  📝 {무엇을 어떻게 수정했는지}

🔴 CRITICAL (수동 수정 필요 — 자동 수정 실패 또는 불가)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[C-1] {제목}
  📍 {파일}:{라인}
  🏷️ Agent: {reviewer} | 신뢰도: {N}/100
  📝 {상세 설명}
  💥 영향: {사고 시나리오}
  ✏️ 수정안:
  {코드}

🟡 WARNING (수정 권장)
━━━━━━━━━━━━━━━━━━━━━
(동일 형식)

💡 SUGGESTION (개선 제안)
━━━━━━━━━━━━━━━━━━━━━━━━
(동일 형식)

⏭️ SKIP (오탐 / 수정 불필요)
━━━━━━━━━━━━━━━━━━━━━━━━━━━
[S-1] {제목} — 사유: {skip 이유}

📋 Agent별 통계 (전체 라운드 누적)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| Agent               | 발견 | ≥{threshold} | 수정 | Critical | Warning |
|---------------------|------|--------------|------|----------|---------|
| Logic & Edge Case   |      |              |      |          |         |
| Type Safety         |      |              |      |          |         |
| Error Handling      |      |              |      |          |         |
| Architecture        |      |              |      |          |         |
| Security & Perf     |      |              |      |          |         |

🔕 필터링됨 (신뢰도 <{threshold}): N건
```
