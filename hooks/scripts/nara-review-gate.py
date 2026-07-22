#!/usr/bin/env python3
"""
nara-kit review gate (PreToolUse hook).

Blocks a `git commit` that includes source changes when no fresh code-review
artifact exists under docs/review/. Deterministic enforcement of the dev-mode
`code-review` spine step — resistant to the agent rationalizing the gate away
under "small scope" (the failure this hook exists to prevent).

Fires ONLY inside an active nara dev-mode session (repo has docs/gap.md or
docs/plan.md), and ONLY when the staged set touches non-doc / non-test source.
Fails OPEN on any unexpected error (never bricks committing); the one hard-fail
path is "source staged + review missing/stale".

Escape hatches (intentional, for genuine trivia):
  - put `[skip-review]` anywhere in the commit command
  - export NARA_SKIP_REVIEW=1
"""
import glob
import json
import os
import re
import subprocess
import sys

MSG_NONE = (
    "\n🚧 nara review-gate: source changes are staged but no code review exists.\n"
    "   docs/review/ has no report. Run  /nara-code-review  before committing.\n"
    "   (Genuinely trivial? add [skip-review] to the commit message or set NARA_SKIP_REVIEW=1.)\n"
)
MSG_STALE = (
    "\n🚧 nara review-gate: staged source is NEWER than the last code review.\n"
    "   The review in docs/review/ predates your latest edits — it is stale.\n"
    "   Re-run  /nara-code-review , then commit.\n"
    "   (Intentional? add [skip-review] to the commit message or set NARA_SKIP_REVIEW=1.)\n"
)


def allow():
    sys.exit(0)


def block(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)  # exit 2 = PreToolUse deny; stderr is surfaced to the agent


def run(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


_NON_SOURCE_EXT = (
    # docs / text assets
    ".md", ".mdx", ".txt",
    # images / binaries (e.g. PR screenshots) — not reviewable source
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico", ".pdf",
    # lockfiles / snapshots
    ".lock", ".snap",
)


def is_source(path):
    p = path.lower()
    if p.endswith(_NON_SOURCE_EXT):
        return False
    if p.startswith("docs/") or p.startswith(".claude/"):
        return False
    if p.startswith("tests/") or "/tests/" in p or "/__tests__/" in p:
        return False
    if re.search(r"\.(test|spec)\.[jt]sx?$", p):
        return False
    return True


def mtime(path):
    try:
        return os.path.getmtime(path)
    except OSError:
        return 0.0


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        allow()

    if data.get("tool_name") != "Bash":
        allow()

    cmd = ((data.get("tool_input") or {}).get("command") or "")
    # Match `git commit` only at a command position (line start, or after a shell
    # separator / then / do) so mentions inside echo/grep/quoted strings — e.g. a
    # test harness that prints the words "git commit" — do NOT trigger the gate.
    if not re.search(r"(?:^|[\n;&|]|\bthen\b|\bdo\b)\s*git\s+commit\b", cmd):
        allow()
    if "--dry-run" in cmd:
        allow()
    if "[skip-review]" in cmd or os.environ.get("NARA_SKIP_REVIEW") == "1":
        allow()

    cwd = data.get("cwd") or os.getcwd()

    root_res = run(["git", "rev-parse", "--show-toplevel"], cwd)
    if root_res.returncode != 0:
        allow()
    root = root_res.stdout.strip()

    # Only enforce inside an active nara dev-mode session.
    if not (
        os.path.exists(os.path.join(root, "docs", "gap.md"))
        or os.path.exists(os.path.join(root, "docs", "plan.md"))
    ):
        allow()

    staged_res = run(["git", "diff", "--cached", "--name-only"], cwd)
    if staged_res.returncode != 0:
        allow()
    staged = [f for f in staged_res.stdout.splitlines() if f.strip()]
    source_files = [f for f in staged if is_source(f)]
    if not source_files:
        allow()  # docs/test-only commit — nothing to review-gate

    reviews = glob.glob(os.path.join(root, "docs", "review", "*.md"))
    if not reviews:
        block(MSG_NONE)

    newest_review = max(mtime(p) for p in reviews)
    source_mtimes = [
        mtime(os.path.join(root, f))
        for f in source_files
        if os.path.exists(os.path.join(root, f))
    ]
    newest_source = max(source_mtimes) if source_mtimes else 0.0
    if newest_review < newest_source:
        block(MSG_STALE)

    allow()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        # Fail open: a bug in the gate must never block all commits.
        sys.exit(0)
