#!/usr/bin/env bash
# Deterministic Tier-1 regression harness for nara-memory-audit/scripts/audit.sh.
#
# This is the code grader for the skill's mechanical half: audit.sh is a bash
# script, so its correctness is asserted directly rather than through a subagent.
# Every case builds its own throwaway repo + memory dir, so runs are hermetic
# and order-independent.
#
# Usage: regress.sh            # run all cases
#        regress.sh -v         # also print each JSON result
# Exit 0 = all pass. Requires: jq, git, bash 3.2+ (macOS default).

set -uo pipefail

AUDIT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../skills/nara-memory-audit/scripts" && pwd)/audit.sh"
[[ -x "$AUDIT" ]] || { echo "FATAL: audit.sh not executable at $AUDIT"; exit 1; }

VERBOSE=0
[[ "${1:-}" == "-v" ]] && VERBOSE=1

PASS=0
FAIL=0
ROOT="$(mktemp -d)"
trap 'rm -rf "$ROOT"' EXIT

# ---- helpers ----------------------------------------------------------------

# new_repo <name> -> prints repo path. Git repo, no skills/ dir (consuming app).
new_repo() {
  local d="$ROOT/$1"
  mkdir -p "$d"
  git -C "$d" init -q .
  git -C "$d" config user.email t@example.test
  git -C "$d" config user.name test
  printf '%s\n' "$d"
}

# new_mem <case> <name> <heredoc-on-stdin> -> prints memory file path
new_mem() {
  local d="$ROOT/$1/mem"
  mkdir -p "$d"
  cat > "$d/$2.md"
  printf '%s\n' "$d/$2.md"
}

# assert_jq <case> <label> <json> <jq-filter> <expected>
assert_jq() {
  local case_id="$1" label="$2" json="$3" filter="$4" want="$5"
  local got
  got=$(printf '%s' "$json" | jq -r "$filter" 2>/dev/null)
  if [[ "$got" == "$want" ]]; then
    PASS=$((PASS + 1))
    printf '  \033[32mPASS\033[0m %s :: %s\n' "$case_id" "$label"
  else
    FAIL=$((FAIL + 1))
    printf '  \033[31mFAIL\033[0m %s :: %s\n        want %s=%s\n        got  %s=%s\n' \
      "$case_id" "$label" "$filter" "$want" "$filter" "$got"
    printf '        json: %s\n' "$json"
  fi
}

# Age is not under test here, and a fixed fixture date would cross the 90-day
# threshold as time passes. Disable signal 1 so cases stay time-independent.
run_audit() {
  local out
  out=$(THRESHOLD_AGE_DAYS=999999 "$@" 2>&1) || true
  [[ $VERBOSE -eq 1 ]] && printf '    > %s\n' "$out" >&2
  printf '%s' "$out"
}

# ---- R1: live skill ref, consuming repo has no skills/ dir ------------------
# Friction 1. The skill's own docs say "run from the repo the memories are
# ABOUT". A consuming app repo has no skills/ dir, so resolving only against
# $CLAUDE_PROJECT_DIR marked every real skill broken.
r1() {
  local repo mem json roots
  repo=$(new_repo r1)
  # Stand in for the agent skill roots. Declared explicitly rather than relying on
  # the real $HOME: an ambient-state case passes on the author's laptop and fails
  # everywhere else, and asserting only the ABSENCE of `broken` would let the
  # unknown verdict satisfy it without any resolution having happened.
  roots="$ROOT/r1/agent-root"
  mkdir -p "$roots/nara-gap" "$roots/nara-implement"
  mem=$(new_mem r1 live-skill <<'EOF'
---
name: live-skill
description: cites two skills that really do exist under an agent skill root
metadata:
  type: project
  verified_at: 2026-01-01
  ref_paths: []
---
Run /nara-gap, then /nara-implement.
EOF
)
  json=$(run_audit env CLAUDE_PROJECT_DIR="$repo" NARA_SKILLS_DIRS="$roots" "$AUDIT" "$mem")
  assert_jq R1 "live skill refs are not reported broken" "$json" \
    '.details.skill_refs_broken | length' 0
  assert_jq R1 "live skill refs actually RESOLVED (not merely unobserved)" "$json" \
    '.details.skill_refs_unknown | length' 0
  assert_jq R1 "no skill_ref_broken signal" "$json" \
    '[.signals[] | select(. == "skill_ref_broken")] | length' 0
  assert_jq R1 "no signals at all" "$json" '.signals | length' 0
  assert_jq R1 "score stays 0" "$json" '.score' 0
}

# ---- R2: bracketed filename in ref_paths, file present ---------------------
# Friction 2. Dynamic-route filenames legitimately contain [ ]; the sanitizer
# stripped them from the value, so the existence check queried a path that was
# never declared.
r2() {
  local repo mem json
  repo=$(new_repo r2)
  mkdir -p "$repo/app/[locale]"
  echo 'export default function P(){}' > "$repo/app/[locale]/page.tsx"
  git -C "$repo" add -A && git -C "$repo" commit -qm init
  mem=$(new_mem r2 bracket-present <<'EOF'
---
name: bracket-present
description: anchors a dynamic-route file that exists on disk
metadata:
  type: project
  verified_at: 2026-01-01
  ref_paths: [app/[locale]/page.tsx]
---
Locale route body.
EOF
)
  json=$(run_audit env CLAUDE_PROJECT_DIR="$repo" "$AUDIT" "$mem")
  assert_jq R2 "bracketed path resolves" "$json" '.details.validity_pct' 100
  assert_jq R2 "no ref_validity signal" "$json" \
    '[.signals[] | select(. == "ref_validity")] | length' 0
}

# ---- R3: genuinely broken skill ref must still fire ------------------------
# Guards against fixing R1 by making the check unconditionally pass.
r3() {
  local repo mem json roots
  repo=$(new_repo r3)
  roots="$ROOT/r3/agent-root"
  mkdir -p "$roots/nara-gap"
  mem=$(new_mem r3 dead-skill <<'EOF'
---
name: dead-skill
description: cites a skill that exists in no root
metadata:
  type: project
  verified_at: 2026-01-01
  ref_paths: []
---
Run /nara-this-skill-does-not-exist-anywhere.
EOF
)
  json=$(run_audit env CLAUDE_PROJECT_DIR="$repo" NARA_SKILLS_DIRS="$roots" "$AUDIT" "$mem")
  assert_jq R3 "dead skill ref still reported broken" "$json" \
    '.details.skill_refs_broken | length' 1
  assert_jq R3 "reported under the invocation identifier, not a skills/ path" "$json" \
    '.details.skill_refs_broken[0]' '/nara-this-skill-does-not-exist-anywhere'
  assert_jq R3 "skill_ref_broken signal fires" "$json" \
    '[.signals[] | select(. == "skill_ref_broken")] | length' 1
}

# ---- R4: no discoverable skills root -> unknown, not broken ---------------
# An unresolvable check must not be scored as a failure.
r4() {
  local repo mem json
  repo=$(new_repo r4)
  mem=$(new_mem r4 unknowable <<'EOF'
---
name: unknowable
description: cites a skill while no skills root is discoverable
metadata:
  type: project
  verified_at: 2026-01-01
  ref_paths: []
---
Run /nara-gap.
EOF
)
  json=$(run_audit env CLAUDE_PROJECT_DIR="$repo" \
    NARA_SKILLS_DIRS="$ROOT/r4/no-such-root" "$AUDIT" "$mem")
  assert_jq R4 "emits skill_ref_unknown" "$json" \
    '[.signals[] | select(. == "skill_ref_unknown")] | length' 1
  assert_jq R4 "does NOT emit skill_ref_broken" "$json" \
    '[.signals[] | select(. == "skill_ref_broken")] | length' 0
  assert_jq R4 "unknown scores 0" "$json" '.score' 0
}

# ---- R5: nara-kit repo mode keeps original behavior -----------------------
# Pre-migration name skills/jira-triage/ must still be flagged when the repo
# itself carries the live skills/ tree.
r5() {
  local repo mem json
  repo=$(new_repo r5)
  mkdir -p "$repo/skills/nara-jira-triage"
  touch "$repo/skills/nara-jira-triage/SKILL.md"
  git -C "$repo" add -A && git -C "$repo" commit -qm init
  mem=$(new_mem r5 premigration <<'EOF'
---
name: premigration
description: cites the pre-migration unprefixed skill dir
metadata:
  type: project
  verified_at: 2026-01-01
  ref_paths: []
---
See skills/jira-triage/ for the queue contract.
EOF
)
  json=$(run_audit env CLAUDE_PROJECT_DIR="$repo" "$AUDIT" "$mem")
  assert_jq R5 "pre-migration dir still flagged" "$json" \
    '.details.skill_refs_broken | index("skills/jira-triage") | type' 'number'
}

# ---- R6: genuinely missing bracketed path must still fire -----------------
# Guards against fixing R2 by making ref_validity unconditionally pass.
r6() {
  local repo mem json
  repo=$(new_repo r6)
  git -C "$repo" commit -q --allow-empty -m init
  mem=$(new_mem r6 bracket-absent <<'EOF'
---
name: bracket-absent
description: anchors a dynamic-route file that is NOT on disk
metadata:
  type: project
  verified_at: 2026-01-01
  ref_paths: [app/[locale]/deleted.tsx]
---
Locale route body.
EOF
)
  json=$(run_audit env CLAUDE_PROJECT_DIR="$repo" "$AUDIT" "$mem")
  assert_jq R6 "missing bracketed path still invalid" "$json" '.details.validity_pct' 0
  assert_jq R6 "ref_validity signal fires" "$json" \
    '[.signals[] | select(. == "ref_validity")] | length' 1
}

# ---- R7: quoting + explicit-empty forms unchanged -------------------------
r7() {
  local repo mem json
  repo=$(new_repo r7)
  mkdir -p "$repo/src"
  echo x > "$repo/src/a.ts"
  echo x > "$repo/src/b.ts"
  git -C "$repo" add -A && git -C "$repo" commit -qm init
  mem=$(new_mem r7 quoted <<'EOF'
---
name: quoted
description: quoted inline list entries
metadata:
  type: project
  verified_at: 2026-01-01
  ref_paths: ["src/a.ts", 'src/b.ts']
---
Body.
EOF
)
  json=$(run_audit env CLAUDE_PROJECT_DIR="$repo" "$AUDIT" "$mem")
  assert_jq R7 "quotes stripped, both resolve" "$json" '.details.validity_pct' 100

  local mem2 json2
  mem2=$(new_mem r7 empty <<'EOF'
---
name: empty
description: explicitly empty ref_paths
metadata:
  type: project
  verified_at: 2026-01-01
  ref_paths: []
---
Body with no anchors.
EOF
)
  json2=$(run_audit env CLAUDE_PROJECT_DIR="$repo" "$AUDIT" "$mem2")
  assert_jq R7 "empty list scores 100 (nothing to disprove)" "$json2" \
    '.details.validity_pct' 100
}

# ---- R8: block-list form with a bracketed entry ---------------------------
r8() {
  local repo mem json
  repo=$(new_repo r8)
  mkdir -p "$repo/app/[id]"
  echo x > "$repo/app/[id]/route.ts"
  git -C "$repo" add -A && git -C "$repo" commit -qm init
  mem=$(new_mem r8 blocklist <<'EOF'
---
name: blocklist
description: multi-line YAML list carrying a bracketed filename
metadata:
  type: project
  verified_at: 2026-01-01
  ref_paths:
    - app/[id]/route.ts
---
Body.
EOF
)
  json=$(run_audit env CLAUDE_PROJECT_DIR="$repo" "$AUDIT" "$mem")
  assert_jq R8 "block-list bracketed path resolves" "$json" '.details.validity_pct' 100
}

# ---- R9: Form A path claim in a repo with no skills/ tree -----------------
# `skills/<name>/` is a repo-relative PATH claim, so only the repo can answer
# it. A consuming repo has no skills/ tree, so the claim is unresolvable —
# report unknown, never broken.
r9() {
  local repo mem json roots
  repo=$(new_repo r9)
  roots="$ROOT/r9/agent-root"
  mkdir -p "$roots/nara-gap"
  mem=$(new_mem r9 formA-unresolvable <<'EOF'
---
name: formA-unresolvable
description: repo-relative skill path claim, audited from a repo with no skills tree
metadata:
  type: project
  verified_at: 2026-01-01
  ref_paths: []
---
Contract lives in skills/nara-gap/references/.
EOF
)
  json=$(run_audit env CLAUDE_PROJECT_DIR="$repo" NARA_SKILLS_DIRS="$roots" "$AUDIT" "$mem")
  assert_jq R9 "Form A without a repo skills tree, skill exists elsewhere -> unknown" "$json" \
    '[.signals[] | select(. == "skill_ref_unknown")] | length' 1
  assert_jq R9 "Form A is not called broken" "$json" \
    '[.signals[] | select(. == "skill_ref_broken")] | length' 0
  assert_jq R9 "the path token is not silently cleared either" "$json" \
    '.details.skill_refs_unknown[0]' 'skills/nara-gap'
  # Form B must not be manufactured out of a path token: `/nara-gap` appears
  # inside `skills/nara-gap/` only as a path segment, never as an invocation.
  assert_jq R9 "no Form B verdict invented from the path segment" "$json" \
    '[(.details.skill_refs_broken + .details.skill_refs_unknown)[] | select(startswith("/"))] | length' 0
}

# ---- R16: an anchor whose path contains a SPACE ---------------------------
# The reported symptom was brackets, but the live victims were spaces: the old
# sanitizer stripped a character class that included ' ', so an absolute anchor
# under a directory like "Mobile Documents" was mangled and a present file read
# as missing. Guarded separately from the bracket cases — re-adding space
# stripping alone leaves every bracket case green.
r16() {
  local repo mem json ext
  repo=$(new_repo r16)
  # Absolute anchor outside the repo, directory name containing a space.
  ext="$ROOT/r16/Mobile Documents/vault"
  mkdir -p "$ext"
  echo x > "$ext/note file.md"
  git -C "$repo" commit -q --allow-empty -m init
  mem=$(new_mem r16 space-path <<EOF
---
name: space-path
description: absolute anchor whose directory and filename both contain spaces
metadata:
  type: project
  verified_at: 2026-01-01
  ref_paths:
    - $ext/note file.md
---
Body.
EOF
)
  json=$(run_audit env CLAUDE_PROJECT_DIR="$repo" "$AUDIT" "$mem")
  assert_jq R16 "space-bearing absolute anchor resolves" "$json" '.details.validity_pct' 100
  assert_jq R16 "no ref_validity signal" "$json" \
    '[.signals[] | select(. == "ref_validity")] | length' 0

  # Inline flow form, quoted, space in both directory and filename.
  local mem2 json2
  mem2=$(new_mem r16 space-inline <<EOF
---
name: space-inline
description: same anchor declared inline and quoted
metadata:
  type: project
  verified_at: 2026-01-01
  ref_paths: ["$ext/note file.md"]
---
Body.
EOF
)
  json2=$(run_audit env CLAUDE_PROJECT_DIR="$repo" "$AUDIT" "$mem2")
  assert_jq R16 "inline quoted space anchor resolves" "$json2" '.details.validity_pct' 100

  # Control: a space-bearing anchor that is genuinely absent must still fail,
  # so the case cannot be satisfied by making ref_validity unconditionally 100.
  local mem3 json3
  mem3=$(new_mem r16 space-absent <<EOF
---
name: space-absent
description: space-bearing anchor that does not exist
metadata:
  type: project
  verified_at: 2026-01-01
  ref_paths:
    - $ext/deleted file.md
---
Body.
EOF
)
  json3=$(run_audit env CLAUDE_PROJECT_DIR="$repo" "$AUDIT" "$mem3")
  assert_jq R16 "missing space-bearing anchor still invalid" "$json3" \
    '.details.validity_pct' 0
}

# ---- R17: absolute anchors resolve at all (signal 2 keeps its as-given try) --
# Three real memories anchor an external notes vault by absolute path. Dropping
# the as-given existence check would zero their validity silently.
r17() {
  local repo mem json ext
  repo=$(new_repo r17)
  ext="$ROOT/r17/outside"
  mkdir -p "$ext"
  echo x > "$ext/ref.md"
  git -C "$repo" commit -q --allow-empty -m init
  mem=$(new_mem r17 absolute <<EOF
---
name: absolute
description: anchor living outside any repo
metadata:
  type: project
  verified_at: 2026-01-01
  ref_paths:
    - $ext/ref.md
---
Body.
EOF
)
  json=$(run_audit env CLAUDE_PROJECT_DIR="$repo" "$AUDIT" "$mem")
  assert_jq R17 "absolute anchor outside the repo resolves" "$json" \
    '.details.validity_pct' 100
  # Documented blindness: signal 3 cannot see outside the repo.
  assert_jq R17 "signal 3 stays blind to it (documented)" "$json" \
    '.details.drift_commits' 0
}

# ---- R18: `/nara-kit` is the repo, not a skill ----------------------------
r18() {
  local repo mem json roots
  repo=$(new_repo r18)
  roots="$ROOT/r18/agent-root"
  mkdir -p "$roots/nara-gap"
  mem=$(new_mem r18 repo-name <<'EOF'
---
name: repo-name
description: mentions the repo by its slash name, which is not a skill
metadata:
  type: project
  verified_at: 2026-01-01
  ref_paths: []
---
Installed from /nara-kit. Also run /nara-gap.
EOF
)
  json=$(run_audit env CLAUDE_PROJECT_DIR="$repo" NARA_SKILLS_DIRS="$roots" "$AUDIT" "$mem")
  assert_jq R18 "/nara-kit is not reported as a skill" "$json" '.signals | length' 0
}

# ---- R11: removed skill exists in NO root -> broken, even without a repo tree
# The unknown downgrade must not swallow live drift. A skill removed from the
# toolkit is absent everywhere, so the claim is refutable from any repo; calling
# it unknown made removed skills read healthy in the prescribed scenario.
r11() {
  local repo mem json roots
  repo=$(new_repo r11)
  roots="$ROOT/r11/agent-root"
  mkdir -p "$roots/nara-gap"
  mem=$(new_mem r11 removed-skill <<'EOF'
---
name: removed-skill
description: path claim naming a skill that was deleted from the toolkit
metadata:
  type: project
  verified_at: 2026-01-01
  ref_paths: []
---
Flow is documented in skills/nara-workflow-orchestrator/.
EOF
)
  json=$(run_audit env CLAUDE_PROJECT_DIR="$repo" NARA_SKILLS_DIRS="$roots" "$AUDIT" "$mem")
  assert_jq R11 "skill absent from every root is broken, not unknown" "$json" \
    '.details.skill_refs_broken[0]' 'skills/nara-workflow-orchestrator'
  assert_jq R11 "not downgraded to unknown" "$json" \
    '.details.skill_refs_unknown | length' 0
  assert_jq R11 "contributes to the score" "$json" '.score' 1
}

# ---- R12: a Form B mention must not clear a false Form A path claim ---------
# The removed cross-form shortcut cleared any path token whose name also appeared
# as a resolvable invocation, which re-opened exactly the widening the Form split
# exists to prevent: adding `/nara-x` to a file erased the verdict on an
# unchanged, still-false `skills/nara-x/` claim.
r12() {
  local repo mem json roots
  repo=$(new_repo r12)
  mkdir -p "$repo/skills/nara-other"
  git -C "$repo" add -A && git -C "$repo" commit -qm init
  roots="$ROOT/r12/agent-root"
  mkdir -p "$roots/nara-installed"
  mem=$(new_mem r12 cross-form <<'EOF'
---
name: cross-form
description: false repo path claim accompanied by a resolvable invocation
metadata:
  type: project
  verified_at: 2026-01-01
  ref_paths: []
---
See skills/nara-installed/ and invoke it with /nara-installed.
EOF
)
  json=$(run_audit env CLAUDE_PROJECT_DIR="$repo" \
    NARA_SKILLS_DIRS="$repo/skills:$roots" "$AUDIT" "$mem")
  assert_jq R12 "path claim stays broken despite the resolvable invocation" "$json" \
    '.details.skill_refs_broken | index("skills/nara-installed") | type' 'number'
  assert_jq R12 "the invocation itself is not flagged" "$json" \
    '[(.details.skill_refs_broken)[] | select(. == "/nara-installed")] | length' 0
}

# ---- R13: NARA_SKILLS_DIRS is honored beyond its first entry --------------
r13() {
  local repo mem json
  repo=$(new_repo r13)
  mkdir -p "$ROOT/r13/a" "$ROOT/r13/b" "$ROOT/r13/c/nara-third"
  mem=$(new_mem r13 third-root <<'EOF'
---
name: third-root
description: skill lives under the third declared root
metadata:
  type: project
  verified_at: 2026-01-01
  ref_paths: []
---
Run /nara-third.
EOF
)
  json=$(run_audit env CLAUDE_PROJECT_DIR="$repo" \
    NARA_SKILLS_DIRS="$ROOT/r13/a:$ROOT/r13/b:$ROOT/r13/c" "$AUDIT" "$mem")
  assert_jq R13 "every declared root is probed, not just the first" "$json" \
    '.signals | length' 0
}

# ---- R14: bracketed anchor must not glob in the drift query ----------------
# git parses a bare pathspec as wildmatch, so `[locale]` becomes a character
# class and unrelated siblings' commits get attributed to the anchor. Only
# reachable once ref_paths stopped stripping brackets, so the bracket fix opened
# it — the validity assertions in the other cases cannot see it.
r14() {
  local repo mem json
  repo=$(new_repo r14)
  mkdir -p "$repo/app/[locale]" "$repo/app/l"
  echo x > "$repo/app/[locale]/page.tsx"
  echo x > "$repo/app/l/page.tsx"
  git -C "$repo" add -A
  GIT_AUTHOR_DATE="2026-01-05T00:00:00" GIT_COMMITTER_DATE="2026-01-05T00:00:00" \
    git -C "$repo" commit -qm init
  # Churn ONLY the sibling that the bracket expression would glob-match.
  echo y > "$repo/app/l/page.tsx"
  git -C "$repo" add -A
  GIT_AUTHOR_DATE="2026-08-01T00:00:00" GIT_COMMITTER_DATE="2026-08-01T00:00:00" \
    git -C "$repo" commit -qm churn-sibling
  mem=$(new_mem r14 glob-anchor <<'EOF'
---
name: glob-anchor
description: bracketed anchor whose sibling churned after verification
metadata:
  type: project
  verified_at: 2026-06-01
  ref_paths: [app/[locale]/page.tsx]
---
Body.
EOF
)
  json=$(run_audit env CLAUDE_PROJECT_DIR="$repo" "$AUDIT" "$mem")
  assert_jq R14 "anchor still resolves" "$json" '.details.validity_pct' 100
  assert_jq R14 "sibling churn is NOT attributed to the bracketed anchor" "$json" \
    '.details.drift_commits' 0
  assert_jq R14 "no code_drift signal" "$json" \
    '[.signals[] | select(. == "code_drift")] | length' 0
}

# ---- R15: real drift on a bracketed anchor IS still detected --------------
# Guard for R14: fixing the glob must not disable signal 3 for bracketed paths.
r15() {
  local repo mem json
  repo=$(new_repo r15)
  mkdir -p "$repo/app/[locale]"
  echo x > "$repo/app/[locale]/page.tsx"
  git -C "$repo" add -A
  GIT_AUTHOR_DATE="2026-01-05T00:00:00" GIT_COMMITTER_DATE="2026-01-05T00:00:00" \
    git -C "$repo" commit -qm init
  echo y > "$repo/app/[locale]/page.tsx"
  git -C "$repo" add -A
  GIT_AUTHOR_DATE="2026-08-01T00:00:00" GIT_COMMITTER_DATE="2026-08-01T00:00:00" \
    git -C "$repo" commit -qm churn-anchor
  mem=$(new_mem r15 real-drift <<'EOF'
---
name: real-drift
description: the bracketed anchor itself churned after verification
metadata:
  type: project
  verified_at: 2026-06-01
  ref_paths: [app/[locale]/page.tsx]
---
Body.
EOF
)
  json=$(run_audit env CLAUDE_PROJECT_DIR="$repo" "$AUDIT" "$mem")
  assert_jq R15 "real churn on a bracketed anchor is still counted" "$json" \
    '.details.drift_commits' 1
  assert_jq R15 "code_drift signal fires" "$json" \
    '[.signals[] | select(. == "code_drift")] | length' 1
}

# ---- R10: agent-root collision must not clear a stale repo path -----------
# The pre-`nara-` migration names (code-review, jira-triage, commit, gap) collide
# with generically-named skills installed under the agent roots. Widening Form A
# resolution to those roots would silently un-flag the migration drift class,
# which is the highest-value catch this signal has. Form A stays repo-scoped.
r10() {
  local repo mem json
  repo=$(new_repo r10)
  mkdir -p "$repo/skills/nara-code-review"
  touch "$repo/skills/nara-code-review/SKILL.md"
  # Stand in for an agent root that carries the colliding bare name.
  mkdir -p "$ROOT/r10/agent-root/code-review"
  git -C "$repo" add -A && git -C "$repo" commit -qm init
  mem=$(new_mem r10 collision <<'EOF'
---
name: collision
description: pre-migration bare name that also exists under an agent root
metadata:
  type: project
  verified_at: 2026-01-01
  ref_paths: []
---
See skills/code-review/ for the reviewer roster.
EOF
)
  json=$(run_audit env CLAUDE_PROJECT_DIR="$repo" \
    NARA_SKILLS_DIRS="$repo/skills:$ROOT/r10/agent-root" "$AUDIT" "$mem")
  assert_jq R10 "colliding agent-root name does not clear the stale repo path" "$json" \
    '.details.skill_refs_broken | index("skills/code-review") | type' 'number'
}

# ---- run --------------------------------------------------------------------
echo "nara-memory-audit Tier-1 regression"
echo "audit.sh: $AUDIT"
echo
for c in r1 r2 r3 r4 r5 r6 r7 r8 r9 r10 r11 r12 r13 r14 r15 r16 r17 r18; do
  echo "[$c]"
  "$c"
done
echo
printf 'pass=%d fail=%d\n' "$PASS" "$FAIL"
[[ $FAIL -eq 0 ]]
