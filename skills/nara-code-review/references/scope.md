# Phase 1: Scope — Git Collection, Review Manifest, Arguments

## Scope selection

```
working tree dirty  → staged + unstaged + untracked 전체 리뷰
working tree clean  → HEAD~1..HEAD
숫자 N              → HEAD~N..HEAD
branch 이름          → <branch>..HEAD
```

Explicit baseline (number/branch) reviews baseline→HEAD; worktree changes are
included only with `--worktree` (and excluded with `--no-worktree` when dirty-default
would include them).

```bash
git status --porcelain                      # dirty check + untracked
git diff --stat && git diff                 # unstaged
git diff --cached                           # staged
git ls-files --others --exclude-standard    # untracked files — read directly
git log <range> --pretty=format:"%H %s"     # commit messages → context-map
```

If no git changes found at all, review files the user mentioned or files edited
earlier in this conversation, and record that in the manifest.

## Review manifest (frozen at start)

Fix the scope BEFORE any agent runs. All later phases refer to this manifest, never
re-derive scope.

```yaml
baseline_commit: abc123
head_commit: def456
include_worktree: true
include_untracked: true
initial_files:
  - src/a.ts
  - src/b.ts
file_hashes:                 # git hash-object per initial file — Verifier baseline
  src/a.ts: 9a3f...
```

If a file changes during the review that neither the Fixer nor the manifest accounts
for (another process touched it), treat it as **scope mismatch**: do not fix or
re-review it silently — escalate in the report and set `scope-integrity: MISMATCH`.

## Arguments

- Empty: default scope rule above
- Number: `HEAD~N..HEAD` / Branch name: `<branch>..HEAD`
- `--fix=none|safe|selected|all` — fix policy (default `safe`), see [fix-policy](fix-policy.md)
- `--report-only` — alias of `--fix=none` (kept for compatibility)
- `--worktree` / `--no-worktree` — include/exclude working-tree changes with explicit baseline
- `--show-all` — show all findings regardless of confidence/evidence gate
- `--threshold=N` — confidence threshold (default 80)
- `--focus=<agent>` — run only a specific reviewer agent. Legacy aliases:
  logic→behavior-state, type-safety→contracts-compatibility,
  error-handling→resilience-data-integrity, architecture→architecture-reuse,
  security-performance→security-privacy+performance-resources
- `--max-rounds=N` — max fix-verify rounds (default 3, hard cap 5)
- `--no-save` — console output only, skip report file

## Help

**If `$ARGUMENTS` is `help` or `--help`, skip all phases, print this in Korean, stop:**

```
🔍 /nara-code-review — Evidence-Based Multi-Agent Review & Controlled Fix

사용법:
  /nara-code-review                    기본 스코프 리뷰 (dirty→워킹트리 전체, clean→최근 1커밋)
  /nara-code-review 3                  최근 3커밋 리뷰
  /nara-code-review main               main 브랜치 대비 리뷰
  /nara-code-review help               이 도움말 출력

옵션:
  --fix=none|safe|selected|all    수정 정책 (기본 safe: R0 + 검증 가능한 R1만)
  --report-only                   --fix=none 별칭
  --show-all                      evidence/신뢰도 필터 없이 전체 출력
  --threshold=N                   신뢰도 기준 변경 (기본: 80)
  --max-rounds=N                  수정-검증 반복 횟수 (기본: 3, 최대: 5)
  --focus=<agent>                 특정 리뷰어만 실행
  --worktree / --no-worktree      명시 baseline 지정 시 워킹트리 변경 포함/제외
  --no-save                       파일 저장 없이 콘솔 출력만

리뷰어 (--focus에 사용):
  코어(항상): behavior-state | contracts-compatibility |
              resilience-data-integrity | tests-regression
  조건부:     security-privacy | performance-resources | architecture-reuse |
              frontend-ux-a11y | database-migration | operations-config

출력:
  리포트는 ./docs/review/YYMMDD-<설명>.md 로 자동 저장됨
```
