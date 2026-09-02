"""Tests for the nara-worklog span reducer.

Run: python3 -m pytest skills/nara-worklog/assets/test_worklog.py -q
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import worklog  # noqa: E402

SCRIPT = Path(__file__).parent / "worklog.py"
TZ = "+09:00"


def ev(ts: str, kind: str = "prompt") -> dict:
    return {"ts": f"{ts}{TZ}", "ev": kind, "session": "abcd1234", "branch": "x"}


def write_ledger(tmp_path: Path, ticket: str, events: list[dict]) -> Path:
    path = tmp_path / f"{ticket}.jsonl"
    path.write_text(
        "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in events),
        encoding="utf-8",
    )
    return path


def run(tmp_path: Path, *args: str) -> dict:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--ledger-dir", str(tmp_path), *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


# --- duration formatting -------------------------------------------------


@pytest.mark.parametrize(
    "seconds,expected",
    [
        (0, "0m"),
        (29, "0m"),
        (60, "1m"),
        (1830, "30m"),  # exact half-minute floors down, no banker's rounding
        (3180, "53m"),
        (3599, "59m"),  # floors, never claims the unspent minute
        (3600, "1h"),
        (5220, "1h 27m"),
        (30600, "8h 30m"),
    ],
)
def test_fmt_duration(seconds, expected):
    assert worklog.fmt_duration(seconds) == expected


def test_jira_started_has_millis_and_colonless_offset():
    dt = datetime.fromisoformat("2026-09-02T09:12:04+09:00")
    assert worklog.jira_started(dt) == "2026-09-02T09:12:04.000+0900"


# --- span construction ---------------------------------------------------


def test_idle_gap_splits_spans(tmp_path):
    write_ledger(
        tmp_path,
        "PROJ-431",
        [
            ev("2026-09-02T09:12:00", "prompt"),
            ev("2026-09-02T09:20:00", "turn_end"),
            ev("2026-09-02T09:48:00", "prompt"),  # 28m reading the output, still work
            ev("2026-09-02T10:05:00", "turn_end"),
            # 2h51m away from the desk -> must not be billed
            ev("2026-09-02T12:56:00", "prompt"),
            ev("2026-09-02T13:30:00", "turn_end"),
        ],
    )
    out = run(tmp_path, "spans", "PROJ-431")
    assert len(out["days"]) == 1
    day = out["days"][0]
    assert [s["duration"] for s in day["spans"]] == ["53m", "34m"]
    assert out["total_time_spent"] == "1h 27m"


def test_long_turn_end_to_prompt_gap_splits(tmp_path):
    write_ledger(
        tmp_path,
        "PROJ-431",
        [
            ev("2026-09-02T09:00:00", "prompt"),
            ev("2026-09-02T09:10:00", "turn_end"),
            ev("2026-09-02T11:00:00", "prompt"),  # left the desk for 1h50m
            ev("2026-09-02T11:15:00", "turn_end"),
        ],
    )
    out = run(tmp_path, "spans", "PROJ-431")
    assert [s["duration"] for s in out["days"][0]["spans"]] == ["10m", "15m"]


def test_prompt_to_prompt_gap_splits_dead_session(tmp_path):
    # Session killed mid-turn, so no turn_end ever landed. The dangling prompt
    # must not absorb the hours until the next one.
    write_ledger(
        tmp_path,
        "PROJ-431",
        [
            ev("2026-09-02T09:00:00", "prompt"),
            ev("2026-09-02T14:00:00", "prompt"),
            ev("2026-09-02T14:20:00", "turn_end"),
        ],
    )
    out = run(tmp_path, "spans", "PROJ-431")
    assert out["total_time_spent"] == "20m"


def test_single_prompt_bills_agent_runtime_until_turn_end(tmp_path):
    write_ledger(
        tmp_path,
        "PROJ-431",
        [
            ev("2026-09-02T09:00:00", "prompt"),
            ev("2026-09-02T09:40:00", "turn_end"),
        ],
    )
    out = run(tmp_path, "spans", "PROJ-431")
    assert out["total_time_spent"] == "40m"


def test_span_crossing_midnight_splits_per_day(tmp_path):
    write_ledger(
        tmp_path,
        "PROJ-431",
        [
            ev("2026-09-02T23:40:00"),
            ev("2026-09-03T00:10:00"),
        ],
    )
    out = run(tmp_path, "spans", "PROJ-431")
    assert [d["date"] for d in out["days"]] == ["2026-09-02", "2026-09-03"]
    assert [d["time_spent"] for d in out["days"]] == ["20m", "10m"]


def test_interleaved_worktrees_merge_as_union_not_sum(tmp_path):
    # Two worktrees on one ticket prompting alternately for 30 minutes total.
    # Summing per-session would double-count; the union must stay 30m.
    events = []
    for minute in range(0, 31, 5):
        events.append(
            {"ts": f"2026-09-02T09:{minute:02d}:00{TZ}", "ev": "prompt", "session": "aaa"}
        )
        events.append(
            {"ts": f"2026-09-02T09:{minute:02d}:30{TZ}", "ev": "prompt", "session": "bbb"}
        )
    write_ledger(tmp_path, "PROJ-431", events)
    out = run(tmp_path, "spans", "PROJ-431")
    assert out["total_seconds"] == 1830
    assert out["total_time_spent"] == "30m"


def test_malformed_line_is_skipped(tmp_path):
    path = write_ledger(
        tmp_path, "PROJ-431", [ev("2026-09-02T09:00:00"), ev("2026-09-02T09:20:00")]
    )
    with path.open("a", encoding="utf-8") as handle:
        handle.write('{"ts": "torn-writ\n')
    out = run(tmp_path, "spans", "PROJ-431")
    assert out["total_time_spent"] == "20m"


def test_missing_ledger_yields_empty_proposal(tmp_path):
    out = run(tmp_path, "spans", "NOPE-1")
    assert out["days"] == []
    assert out["total_seconds"] == 0


# --- idempotency ---------------------------------------------------------


def test_record_watermark_makes_rerun_empty(tmp_path):
    write_ledger(
        tmp_path,
        "PROJ-431",
        [ev("2026-09-02T09:00:00"), ev("2026-09-02T09:20:00")],
    )
    first = run(tmp_path, "spans", "PROJ-431")
    assert first["total_seconds"] == 1200

    run(
        tmp_path,
        "record",
        "PROJ-431",
        "--through",
        first["latest_event"],
        "--seconds",
        str(first["total_seconds"]),
        "--worklog-id",
        "10021",
    )

    second = run(tmp_path, "spans", "PROJ-431")
    assert second["days"] == []
    assert second["watermark"] is not None


def test_work_after_watermark_is_still_proposed(tmp_path):
    write_ledger(
        tmp_path,
        "PROJ-431",
        [ev("2026-09-02T09:00:00"), ev("2026-09-02T09:20:00")],
    )
    first = run(tmp_path, "spans", "PROJ-431")
    run(
        tmp_path,
        "record",
        "PROJ-431",
        "--through",
        first["latest_event"],
        "--seconds",
        str(first["total_seconds"]),
    )

    path = tmp_path / "PROJ-431.jsonl"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(ev("2026-09-03T14:00:00", "prompt")) + "\n")
        handle.write(json.dumps(ev("2026-09-03T14:45:00", "turn_end")) + "\n")

    out = run(tmp_path, "spans", "PROJ-431")
    assert [d["date"] for d in out["days"]] == ["2026-09-03"]
    assert out["total_time_spent"] == "45m"


# --- list ----------------------------------------------------------------


def test_list_reports_only_tickets_with_unlogged_time(tmp_path):
    write_ledger(
        tmp_path, "PROJ-431", [ev("2026-09-02T09:00:00"), ev("2026-09-02T09:20:00")]
    )
    write_ledger(
        tmp_path, "PROJ-999", [ev("2026-09-02T09:00:00"), ev("2026-09-02T09:00:10")]
    )
    out = run(tmp_path, "list")
    assert [t["ticket"] for t in out["unlogged"]] == ["PROJ-431"]
    assert out["unlogged"][0]["unlogged_time_spent"] == "20m"


def test_sub_minute_day_is_marked_unpostable(tmp_path):
    write_ledger(
        tmp_path, "PROJ-431", [ev("2026-09-02T09:00:00"), ev("2026-09-02T09:00:20")]
    )
    out = run(tmp_path, "spans", "PROJ-431")
    assert out["days"][0]["postable"] is False
