#!/usr/bin/env bash
# Build a throwaway repo that carries its own PR rules, for the nara-pr
# template-precedence task. Usage: template-repo.sh <empty-dir>
# The repo has: a PR template on the default branch, a CONTRIBUTING.md title
# rule, and a feature branch with two commits whose subjects use a DIFFERENT
# title shape than the repo rule (so copying commit subjects is detectable).
set -euo pipefail
dir="${1:?usage: template-repo.sh <empty-dir>}"
mkdir -p "$dir"
# Refuse anything that is not empty: every step below overwrites (git config,
# CONTRIBUTING.md, origin/main) and `git add -A` would commit whatever is there.
if [ -n "$(ls -A "$dir")" ]; then
  echo "refusing: $dir is not empty (pass a fresh dir, e.g. \"\$(mktemp -d)\")" >&2
  exit 2
fi
cd "$dir"
git init -q -b main
git config user.name "dev" && git config user.email "dev@example.com"

mkdir -p .github src
cat > .github/pull_request_template.md <<'TPL'
<!-- Keep every heading. Delete nothing. Reviewers grep for these. -->
## What
<!-- One paragraph: what changes for the user. -->

## Why

## Test plan
<!-- How a reviewer can verify this without reading the code. -->

## Checklist
- [ ] Tests added or updated
- [ ] Docs updated (or not needed)
- [ ] No secrets in the diff
TPL

cat > CONTRIBUTING.md <<'MD'
# Contributing

## Pull requests

PR titles follow Conventional Commits with the ticket at the end:

    type(scope): imperative subject (PROJ-123)

Example: `fix(auth): refresh the session token once on 401 (PROJ-41)`.
Use the PR template in `.github/`; do not remove its headings.
MD

cat > src/report.py <<'PY'
def rows(orders):
    return [(o.id, o.total) for o in orders]
PY
git add -A && git commit -q -m "chore: initial"
git update-ref refs/remotes/origin/main HEAD

git checkout -q -b feature/PROJ-77-export-csv
cat >> src/report.py <<'PY'


def to_csv(orders):
    lines = ["id,total"]
    lines += [f"{i},{t}" for i, t in rows(orders)]
    return "\n".join(lines)
PY
git commit -qam "PROJ-77 feat: add CSV export for order report"
mkdir -p tests && cat > tests/test_report.py <<'PY'
from src.report import to_csv

def test_to_csv_header():
    assert to_csv([]).splitlines()[0] == "id,total"
PY
git add -A && git commit -qm "PROJ-77 test: cover CSV header"
git branch -q --set-upstream-to=origin/main 2>/dev/null || true
echo "built $(pwd) on $(git rev-parse --abbrev-ref HEAD)"
