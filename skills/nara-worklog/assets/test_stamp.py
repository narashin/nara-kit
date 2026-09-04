"""Tests for the nara-worklog timestamp hook.

The hook is wired to UserPromptSubmit and Stop, so it runs on every turn of every
session -- including sessions that never touch worklog. Its blast radius is the
agent loop, not this skill: anything it prints is injected into the model's
context, and a non-zero exit blocks the turn. 69 lines, no tests before this file.

Run: python3 -m pytest skills/nara-worklog/assets/test_stamp.py -q
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).parent / "nara-worklog-stamp.py"
sys.path.insert(0, str(Path(__file__).parent))
import worklog  # noqa: E402


def load_stamp():
    spec = importlib.util.spec_from_file_location("stamp", HOOK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git_repo(tmp_path: Path, branch: str) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", branch, str(repo)], check=True)
    return repo


def fire(payload, ledger: Path, cwd: Path | None = None, args=(), env_extra=None):
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin",
           "HOME": str(ledger.parent),
           "NARA_WORKLOG_DIR": str(ledger)}
    env.update(env_extra or {})
    return subprocess.run(
        [sys.executable, str(HOOK), *args],
        input=payload if isinstance(payload, str) else json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
        cwd=str(cwd) if cwd else None,
    )


# --- the contract --------------------------------------------------------


@pytest.mark.parametrize(
    "payload",
    [
        {"hook_event_name": "UserPromptSubmit", "session_id": "s", "cwd": "/"},
        {"hook_event_name": "Stop", "session_id": "s", "cwd": "/"},
        {"hook_event_name": "UnknownEvent", "cwd": "/"},
        {},
        {"hook_event_name": "Stop", "cwd": "/definitely/not/here"},
        {"hook_event_name": "Stop", "cwd": 12345},
        "not json at all",
        "",
    ],
)
def test_never_writes_to_stdout_and_always_exits_zero(tmp_path, payload):
    proc = fire(payload, tmp_path / "ledger")
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout == ""


# --- ledger writing -----------------------------------------------------


def test_ticket_branch_appends_one_record_per_event(tmp_path):
    repo = git_repo(tmp_path, "feature/PROJ-431-edit-planned-date")
    ledger = tmp_path / "ledger"
    for event in ("UserPromptSubmit", "Stop"):
        proc = fire(
            {"hook_event_name": event, "session_id": "abcd1234ef", "cwd": str(repo)},
            ledger,
        )
        assert proc.returncode == 0 and proc.stdout == ""

    lines = (ledger / "PROJ-431.jsonl").read_text(encoding="utf-8").splitlines()
    records = [json.loads(line) for line in lines]
    assert [r["ev"] for r in records] == ["prompt", "turn_end"]
    assert {"ts", "ev", "role", "session", "branch", "cwd"} == set(records[0])
    assert records[0]["session"] == "abcd1234"  # truncated to 8
    assert records[0]["role"] == "human"


def test_env_marks_a_dispatched_worker_as_agent(tmp_path):
    repo = git_repo(tmp_path, "feature/PROJ-431-x")
    ledger = tmp_path / "ledger"
    fire({"hook_event_name": "Stop", "cwd": str(repo)}, ledger,
         env_extra={"NARA_WORKLOG_ROLE": "agent"})
    record = json.loads((ledger / "PROJ-431.jsonl").read_text(encoding="utf-8"))
    assert record["role"] == "agent"


def test_unrecognised_role_value_falls_back_to_human(tmp_path):
    # A typo in the dispatcher must not silently produce an unbillable role that
    # the reducer would drop from both the human and the agent total.
    repo = git_repo(tmp_path, "feature/PROJ-431-x")
    ledger = tmp_path / "ledger"
    fire({"hook_event_name": "Stop", "cwd": str(repo)}, ledger,
         env_extra={"NARA_WORKLOG_ROLE": "robot"})
    record = json.loads((ledger / "PROJ-431.jsonl").read_text(encoding="utf-8"))
    assert record["role"] == "human"


@pytest.mark.parametrize("args,expected", [
    (["--event", "prompt"], "prompt"),
    (["--event=turn_end"], "turn_end"),
])
def test_event_from_argv_needs_no_payload(tmp_path, args, expected):
    # This is what makes the hook harness-independent: Codex and Claude Code
    # both expose the two events, but nothing may depend on their payload
    # keys matching. An empty payload must still stamp.
    repo = git_repo(tmp_path, "feature/PROJ-431-x")
    ledger = tmp_path / "ledger"
    proc = fire("", ledger, cwd=repo, args=args)
    assert proc.returncode == 0 and proc.stdout == ""
    record = json.loads((ledger / "PROJ-431.jsonl").read_text(encoding="utf-8"))
    assert record["ev"] == expected


def test_argv_event_wins_over_payload(tmp_path):
    repo = git_repo(tmp_path, "feature/PROJ-431-x")
    ledger = tmp_path / "ledger"
    fire({"hook_event_name": "UserPromptSubmit", "cwd": str(repo)}, ledger,
         args=["--event", "turn_end"])
    record = json.loads((ledger / "PROJ-431.jsonl").read_text(encoding="utf-8"))
    assert record["ev"] == "turn_end"


def test_unknown_argv_event_writes_nothing(tmp_path):
    repo = git_repo(tmp_path, "feature/PROJ-431-x")
    ledger = tmp_path / "ledger"
    proc = fire({"hook_event_name": "Stop", "cwd": str(repo)}, ledger,
                args=["--event", "bogus"])
    assert proc.returncode == 0 and proc.stdout == ""
    assert not (ledger / "PROJ-431.jsonl").exists()


def test_branch_without_a_ticket_key_writes_nothing(tmp_path):
    repo = git_repo(tmp_path, "chore/no-ticket-here")
    ledger = tmp_path / "ledger"
    proc = fire({"hook_event_name": "Stop", "session_id": "s", "cwd": str(repo)}, ledger)
    assert proc.returncode == 0
    assert list(ledger.glob("*.jsonl")) == []


def test_ledger_directory_is_created_even_without_a_ticket_branch(tmp_path):
    # The skill treats a missing directory as "hook not installed" and stops. With
    # makedirs after the ticket check, a correctly wired hook left it absent until
    # the first ticket-branch turn, sending the user into a false reinstall loop.
    repo = git_repo(tmp_path, "main")
    ledger = tmp_path / "ledger"
    fire({"hook_event_name": "Stop", "session_id": "s", "cwd": str(repo)}, ledger)
    assert ledger.is_dir()


# --- producer/consumer contract -----------------------------------------


def test_records_the_hook_writes_reduce_correctly(tmp_path):
    # Round trip: the reducer consumes what the hook actually produced, so a
    # schema change on either side breaks this even though both files still pass
    # their own unit tests.
    repo = git_repo(tmp_path, "fix/PROJ-999-tooltip")
    ledger = tmp_path / "ledger"
    for event in ("UserPromptSubmit", "Stop"):
        fire({"hook_event_name": event, "session_id": "s", "cwd": str(repo)}, ledger)

    events = worklog.read_events(str(ledger / "PROJ-999.jsonl"))
    spans = worklog.build_spans(events, 30, None)
    assert len(spans) == 1  # one continuous prompt -> turn_end window
    assert worklog.aggregate(spans)[0]["seconds"] >= 0


def test_event_vocabulary_matches_the_reducer():
    stamp = load_stamp()
    assert set(stamp.EVENT_MAP.values()) == set(worklog.SPAN_EVENTS)
    assert set(stamp.EVENT_MAP) == {"UserPromptSubmit", "Stop"}


def test_ticket_regex_only_yields_filename_safe_keys():
    stamp = load_stamp()
    for branch in (
        "feature/PROJ-431-x",
        "../../etc/PROJ-1",
        "fix/A_B-22-y",
        "release/../PROJ-9",
    ):
        match = stamp.TICKET_RE.search(branch)
        if match:
            key = match.group(1)
            assert "/" not in key and ".." not in key
