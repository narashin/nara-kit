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
║ 모델: 판단 {opus|fable|session fallback} · Verifier sonnet ║
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

Stats table rules: unadjudicated findings show `-(unadjudicated)` in the confirmed
column. Fingerprint-merged findings count ONCE under the merge representative's row;
co-reporters keep their 발견 count with the merge noted in their row.

## Trailing status (contract gate — 없으면 리뷰 미완료)

```
overrides: applied (<path>) | none (<확인 명령> → <결과>) | unverifiable (<이유>)
fix-ledger: match (<n> claimed, <n> changed, 0 unclaimed) | MISMATCH (<n> claimed-but-unchanged, <m> changed-but-unclaimed, <k> changed-but-unresolved)
fix-verification: {N} verified, {N} unverified, {N} mismatched
scope-integrity: match (scope <n> → touched <n>) | expanded (scope <n> → touched <m>: <파일> — <사유>, 승인) | MISMATCH (scope <n> → touched <m>: <외부 변경 파일>)
validation: pass (<cmd> → exit <code>[, baseline <base> → exit <code>]; …) | fail (<cmd> → exit <code>; …) | unavailable (<이유>)
```

**These five lines are claims about what was executed, so each must carry its own
evidence.** A bare verdict is a contract violation even when the verdict is right:

- `validation` — name every command that ran and quote **its exit status**, not a
  prose summary of its output. A non-zero exit is `fail` **unless** the same command
  at the baseline produced it too and that run is quoted (`git show <base>:<path> | …`,
  or the command at the baseline commit) — then it is `pass`, and the non-zero code
  stays on the line beside the baseline code. Never drop the exit codes to make `pass`
  look clean: `pass (… → exit 0)` and `pass (… → exit 2, baseline abc123d → exit 2)`
  are different claims and the second is the one with evidence. With no baseline run,
  write `fail` and say the baseline is unmeasured — a failure that merely *looks*
  pre-existing is not measured. `unavailable` means no validation command ran — say why.
- **Every verdict carries evidence, the clean ones included.** There is no bare-word
  form of any of the five lines — not `match`, not `none`. `scope-integrity` quotes the
  counts on both sides even when they agree (a single count cannot show agreement);
  `fix-ledger: match` quotes claimed, changed, and the zero unclaimed it is asserting;
  `overrides: none` quotes the check that found nothing, because `none` claims the file
  was looked for while `unverifiable` says it was not. A clean line with no evidence is
  the easiest place for an unmeasured claim to hide.
- `scope-integrity` — an expansion is `expanded` only when **all three** hold: a per-file reason, disclosed
  to the user **before** the fix was applied, and explicitly approved. Name each extra
  file with its reason on the line. Miss any one of the three — reason absent, disclosed
  only afterwards, approval assumed — and it is `MISMATCH`. Approval after the fact does
  not convert a MISMATCH; the point of disclosing first is that the user could still say
  no.

  `expanded` is **not** a MISMATCH: it takes no `→ ESCALATE:`, and the run is reported as
  applied. MISMATCH means the reader was never told, which is the failure this line
  exists to catch — folding a controlled expansion into it destroys that signal, and
  `match` is equally wrong because the touched set is not the frozen set.
- **`→ ESCALATE:` goes directly under the block**, one line per escalating verdict, so
  it travels with the status whether or not a report body was produced.
- **When the evidence for a line does not exist**, write
  `unverifiable (<무엇이 없는지>)`. This applies to **any** of the five lines,
  `overrides` included — a run that never checked for the override file reports
  `unverifiable`, not `none`, because `none` asserts the file was looked for. The
  common case is a fix phase that ran outside this session: it leaves no per-finding
  claim ledger, so `fix-ledger` and `fix-verification` have nothing to count. Never
  fill the numeric slots by inference; an invented `0 verified, 0 unverified,
  0 mismatched` reads as a measurement that was taken.

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
