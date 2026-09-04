#!/usr/bin/env python3
"""Append a worklog timestamp event for the Jira ticket of the current branch.

Derives the ticket key from the git branch at the session's cwd and appends one
JSONL event to ~/.claude/worklog/<TICKET>.jsonl. Wired to the prompt-submit and
stop hooks of every agent harness in use; those two bracket a turn, so the span
between the first prompt and the last turn end is the interaction window. The
span reducer that consumes this ledger is worklog.py in this directory.

Harness independence: the event name is taken from `--event` when given, and
only falls back to the stdin payload's `hook_event_name`. Claude Code and Codex
both expose UserPromptSubmit/Stop, but nothing here should depend on their
payloads staying identical — passing the event explicitly in the hook command
makes the payload optional, so a schema change in either harness cannot
silently stop the clock.

Roles: a dispatched agent working on a ticket branch is not the human spending
time on it. Every event carries `role`, and only `human` events reach a Jira
worklog (see worklog.py). Events written before roles existed have no field and
are read as `human`, which is what they were.

Contract: writes NOTHING to stdout and always exits 0. Prompt-submit hook stdout
is injected into the model's context, and a non-zero exit blocks the turn;
bookkeeping must never do either.
"""

from __future__ import annotations  # keeps `str | None` readable on python 3.9

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
VALID_EVENTS = frozenset(EVENT_MAP.values())

# Dispatched workers run under this root (see multica-dispatch.py). The env var
# is the primary signal because the dispatcher sets it explicitly; the path is a
# backstop for a worker started by hand in the same tree.
AGENT_WORKSPACE_ROOT = os.path.expanduser("~/orca/workspaces")


def read_payload() -> dict:
    """Parse the hook payload, tolerating a harness that sends nothing useful."""
    try:
        data = json.load(sys.stdin)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def resolve_event(argv: list[str], payload: dict) -> str | None:
    for index, arg in enumerate(argv):
        if arg == "--event" and index + 1 < len(argv):
            candidate = argv[index + 1]
            return candidate if candidate in VALID_EVENTS else None
        if arg.startswith("--event="):
            candidate = arg.split("=", 1)[1]
            return candidate if candidate in VALID_EVENTS else None
    return EVENT_MAP.get(payload.get("hook_event_name", ""))


def resolve_role(cwd: str) -> str:
    role = os.environ.get("NARA_WORKLOG_ROLE", "").strip().lower()
    if role in ("human", "agent"):
        return role
    try:
        inside = os.path.commonpath(
            [os.path.realpath(cwd), os.path.realpath(AGENT_WORKSPACE_ROOT)]
        ) == os.path.realpath(AGENT_WORKSPACE_ROOT)
    except (ValueError, OSError):
        inside = False
    return "agent" if inside else "human"


def main() -> None:
    payload = read_payload()
    event = resolve_event(sys.argv[1:], payload)
    if event is None:
        return

    # Create the ledger directory before the ticket check, not after. The skill
    # treats a missing directory as "hook not installed" and stops; with this
    # after the early return, a correctly wired hook left it absent until the
    # first ticket-branch turn, sending the user into a false reinstall loop.
    os.makedirs(LEDGER_DIR, exist_ok=True)

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
        "role": resolve_role(cwd),
        "session": (payload.get("session_id") or "")[:8],
        "branch": branch,
        "cwd": cwd,
    }
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
