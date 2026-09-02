#!/usr/bin/env python3
"""Append a worklog timestamp event for the Jira ticket of the current branch.

Reads the Claude Code hook payload on stdin, derives the ticket key from the
git branch at the payload's cwd, and appends one JSONL event to
~/.claude/worklog/<TICKET>.jsonl.

Wired to UserPromptSubmit (ev=prompt) and Stop (ev=turn_end). Those two
bracket every turn, so the span between the first prompt and the last turn end
is the actual interaction window -- see skills/nara-worklog/assets/worklog.py
for the span reducer that consumes this ledger.

Contract: writes NOTHING to stdout and always exits 0. UserPromptSubmit hook
stdout is injected into the model's context, and a non-zero exit blocks the
turn; bookkeeping must never do either.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

TICKET_RE = re.compile(r"([A-Z][A-Z0-9_]+-\d+)")
LEDGER_DIR = os.environ.get(
    "NARA_WORKLOG_DIR", os.path.expanduser("~/.claude/worklog")
)
EVENT_MAP = {"UserPromptSubmit": "prompt", "Stop": "turn_end"}


def main() -> None:
    payload = json.load(sys.stdin)
    event = EVENT_MAP.get(payload.get("hook_event_name", ""))
    if event is None:
        return

    cwd = payload.get("cwd") or os.getcwd()
    branch = subprocess.run(
        ["git", "-C", cwd, "branch", "--show-current"],
        capture_output=True,
        text=True,
        timeout=5,
    ).stdout.strip()

    match = TICKET_RE.search(branch)
    if not match:
        return  # no ticket key in the branch name -> nothing to attribute time to

    record = {
        "ts": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "ev": event,
        "session": (payload.get("session_id") or "")[:8],
        "branch": branch,
        "cwd": cwd,
    }
    os.makedirs(LEDGER_DIR, exist_ok=True)
    path = os.path.join(LEDGER_DIR, f"{match.group(1)}.jsonl")
    # One short line per append keeps concurrent worktrees from interleaving.
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # never block or pollute a turn on bookkeeping failure
    sys.exit(0)
