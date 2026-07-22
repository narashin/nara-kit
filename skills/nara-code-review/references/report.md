# Phase 8: Final Report (Korean, file save)

**Save the report as a markdown file:**
- Directory: `./docs/review/`
- Filename: `YYMMDD-<short-description>.md` (e.g., `260722-fix-auth-validation.md`)
- Print the file path at the end. `--no-save` → console only.
- Console response follows the shared output contract (receipt, not full artifact) —
  the file holds the full report.

```
╔══════════════════════════════════════════════════╗
║          🔍 CODE REVIEW REPORT                   ║
║   Evidence-Based Multi-Agent Review & Fix        ║
╠══════════════════════════════════════════════════╣
║ 대상: {baseline_commit}..{head_commit}            ║
║ 변경 파일: {N}개 (untracked {M}개 포함)            ║
║ 리뷰어: core 4 + conditional {list}               ║
║ 게이트: evidence ≥ E2 AND 신뢰도 ≥ {threshold}    ║
║ 라운드: {current}/{max} ({converged/stopped})     ║
║ specification: {available | unavailable}          ║
╚══════════════════════════════════════════════════╝

📊 요약
━━━━━━
🔴 Critical: N건  🟠 Major: N건  🟡 Minor: N건  💡 Suggestion: N건
⚖️ Judge: confirmed N / downgraded N / rejected N / needs-context N
✅ 수정 verified: N건  ⏳ unverified: N건  ❌ mismatched: N건
🔄 라운드: {N}회 (수렴: {✅ Clean / 🖐 Manual-only / ⚠️ Max rounds / 🔁 No progress})

🔄 라운드별 이력
━━━━━━━━━━━━━━━
Round 1: 발견 N → confirmed N → 수정 N → verified N
Round 2: ...
Final baseline review: {실행됨/스킵(수정 없음)} — 신규 발견 N건

✅ 수정 완료 (verified만 — proof 포함)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[BEH-001] {invariant 한 줄} (Round {N}, {fix_risk})
  📍 {path}::{symbol} ({lines})
  📝 {무엇을 어떻게 수정}
  🔬 proof: {observed hunk} + {validation/테스트 결과}

🔴 CRITICAL — 수동 수정 필요 (R2/R3 또는 fix 실패)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[SEC-001] {invariant}
  📍 {path}::{symbol} | ⚖️ {verdict} | E{n} | 신뢰도 {N} | {fix_risk}
  📝 preconditions / failure_path 요약
  💥 영향: {impact}
  ✏️ 수정안: {suggested_fix}
  🧪 검증 방법: {validation}

🟠 MAJOR / 🟡 MINOR / 💡 SUGGESTION — 동일 형식 (suggestion은 자동 수정 대상 아님)

⏭️ SKIP (Judge rejected)
━━━━━━━━━━━━━━━━━━━━━━━
[XXX-nnn] {제목} — 사유: {Judge reason}

🚫 suppressed-by-project-exception
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[XXX-nnn] {rule} — exception: {scope} / {reason} / expires {date}

❓ 미검토 리스크 / 확인 질문 (E0·E1 + needs-context)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- {질문/리스크} — 필요한 컨텍스트: {missing_context}

📋 리뷰어별 통계 (실행된 에이전트만)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| Reviewer | 발견 | 게이트 통과 | confirmed | 수정 | verified |
|---|---|---|---|---|---|

🔕 게이트 미달 (E1 이하 또는 신뢰도 <{threshold}): N건 (--show-all로 열람)
```

## Trailing status (contract gate — 없으면 리뷰 미완료)

```
overrides: applied (.claude/overrides/code-review.md) | none
fix-ledger: match | MISMATCH (<n> claimed-but-unchanged, <m> changed-but-unclaimed, <k> changed-but-unresolved)
fix-verification: {N} verified, {N} unverified, {N} mismatched
scope-integrity: match | MISMATCH (<외부 변경 파일>)
validation: pass | fail (<command>) | unavailable
```

`--fix=none` runs print `fix-ledger: n/a` and `fix-verification: n/a`.
Fix-enabled runs that applied ZERO fixes (nothing eligible) print `fix-ledger: match`
and `fix-verification: 0 verified, 0 unverified, 0 mismatched`; `validation` reflects
whatever actually ran (`unavailable` if no validation was executed). Empty-scope
stops: see scope.md (all `n/a`).

## Adversarial review (manual follow-up)

After the report, suggest the user run `/nara-adversarial-review` (native: refuter +
blind hunter + rigor auditor, appends to this report) and/or
`/codex:adversarial-review` (cannot be auto-invoked — `disable-model-invocation`).
Both challenge findings: missed issues, false positives, overly generous
assessments. If the user declines, note "adversarial review skipped".
