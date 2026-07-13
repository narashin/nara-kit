# Phases 4–7: Aggregate, Filter, Fix Loop & Report

## Phase 4: Aggregate & Filter

After all agents complete:

1. Include only findings with **confidence >= threshold** (default 80)
2. If multiple agents flag the same location for the same issue -> boost confidence & merge
3. Sort by severity: critical -> warning -> suggestion
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
- **Clean**: No critical or warning findings with confidence >= threshold -> code is clean
- **Max rounds reached**: Hit the iteration limit (default 3)
- **No progress**: Same issues keep reappearing across rounds (fix is not resolving them) -> stop and report as manual-fix-needed
- **Only suggestions remain**: No critical/warning, only low-severity suggestions

If not converged, go back to Phase 5 for the next round.

### Phase 7: Final Report (Korean output + file save)

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
