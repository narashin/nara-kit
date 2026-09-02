"""Tests for the nara-worklog span reducer.

Run: python3 -m pytest skills/nara-worklog/assets/test_worklog.py -q
"""

import importlib.util
import json
import os
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


def run(tmp_path: Path, *args: str, gap: int = 30) -> dict:
    # --gap-minutes is passed explicitly, never left to the environment: the
    # skill documents NARA_WORKLOG_GAP_MINUTES as a user knob, and inheriting it
    # made five tests fail for a developer who had it exported.
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--ledger-dir",
            str(tmp_path),
            "--gap-minutes",
            str(gap),
            *args,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


def day_spans(day: dict) -> list[dict]:
    """All spans of a day, ignoring ticket attribution.

    Deliberately does NOT re-sort. Chronological emission order is part of the
    contract (bucket `spans[0]` feeds `jira_started`), and sorting here masked a
    reversed-emission regression that the pre-bucket assertions used to catch.
    """
    return [s for b in day["tickets"] for s in b["spans"]]


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
    assert [s["duration"] for s in day_spans(day)] == ["53m", "34m"]
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
    assert [s["duration"] for s in day_spans(out["days"][0])] == ["10m", "15m"]


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
    # The span is 30m30s; the total reports the floored per-day minutes because
    # that is what actually gets posted to Jira.
    assert out["days"][0]["seconds"] == 1830
    assert out["total_seconds"] == 1800
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


# --- regressions found by review 2026-09-02 ------------------------------


def test_total_matches_the_sum_actually_posted_to_jira(tmp_path):
    # Jira is written once per day, so the total must be the sum of the FLOORED
    # per-day values. Summing raw seconds revived the discarded remainders and
    # claimed 3m where only 2m gets posted.
    write_ledger(
        tmp_path,
        "PROJ-431",
        [
            ev("2026-09-02T09:00:00", "prompt"),
            ev("2026-09-02T09:01:30", "turn_end"),
            ev("2026-09-03T09:00:00", "prompt"),
            ev("2026-09-03T09:01:30", "turn_end"),
        ],
    )
    out = run(tmp_path, "spans", "PROJ-431")
    assert [d["time_spent"] for d in out["days"]] == ["1m", "1m"]
    assert out["total_time_spent"] == "2m"


def test_unpostable_day_is_excluded_from_the_total_and_listed(tmp_path):
    write_ledger(
        tmp_path,
        "PROJ-431",
        [
            ev("2026-09-02T09:00:00", "prompt"),
            ev("2026-09-02T09:20:00", "turn_end"),
            ev("2026-09-03T09:00:00", "prompt"),
            ev("2026-09-03T09:00:20", "turn_end"),
        ],
    )
    out = run(tmp_path, "spans", "PROJ-431")
    assert out["total_time_spent"] == "20m"
    assert out["unpostable"] == ["2026-09-03 PROJ-431"]


def test_jira_started_is_wired_to_each_days_first_span(tmp_path):
    # The unit test on jira_started() passed even when aggregate() was rewired to
    # the last span's end, or replaced with a constant. Pin the wiring.
    write_ledger(
        tmp_path,
        "PROJ-431",
        [ev("2026-09-02T23:40:00"), ev("2026-09-03T00:10:00")],
    )
    out = run(tmp_path, "spans", "PROJ-431")
    assert [d["tickets"][0]["jira_started"] for d in out["days"]] == [
        "2026-09-02T23:40:00.000+0900",
        "2026-09-03T00:00:00.000+0900",
    ]


def test_record_rejects_a_through_without_an_offset(tmp_path):
    # The ledger is append-only, so a naive watermark cannot be taken back and
    # would raise TypeError on every later run -- for every ticket, since list
    # walks the whole directory.
    write_ledger(
        tmp_path, "PROJ-431", [ev("2026-09-02T09:00:00"), ev("2026-09-02T09:20:00")]
    )
    before = (tmp_path / "PROJ-431.jsonl").read_text(encoding="utf-8")
    proc = subprocess.run(
        [
            sys.executable, str(SCRIPT), "--ledger-dir", str(tmp_path),
            "record", "PROJ-431", "--through", "2026-09-02", "--seconds", "1200",
        ],
        capture_output=True, text=True,
    )
    assert proc.returncode == 1
    assert "offset" in proc.stderr
    assert (tmp_path / "PROJ-431.jsonl").read_text(encoding="utf-8") == before


def test_naive_watermark_already_on_disk_does_not_break_the_reduce(tmp_path):
    # Defence in depth for ledgers written before the guard above existed.
    path = write_ledger(
        tmp_path, "PROJ-431", [ev("2026-09-02T09:00:00"), ev("2026-09-02T09:20:00")]
    )
    with path.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps({"ts": "x", "ev": "logged", "through": "2026-09-02T09:20:00"})
            + "\n"
        )
    out = run(tmp_path, "spans", "PROJ-431")
    assert out["days"] == []
    assert run(tmp_path, "list")["unlogged"] == []


def test_one_poisoned_ledger_does_not_break_list_for_other_tickets(tmp_path):
    write_ledger(
        tmp_path, "PROJ-431", [ev("2026-09-02T09:00:00"), ev("2026-09-02T09:20:00")]
    )
    bad = write_ledger(tmp_path, "PROJ-999", [ev("2026-09-02T09:00:00")])
    with bad.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"ev": "logged", "through": "not-a-timestamp"}) + "\n")
    out = run(tmp_path, "list")
    assert [t["ticket"] for t in out["unlogged"]] == ["PROJ-431"]


def test_flags_work_on_either_side_of_the_subcommand(tmp_path):
    write_ledger(
        tmp_path, "PROJ-431", [ev("2026-09-02T09:00:00"), ev("2026-09-02T09:20:00")]
    )
    after = json.loads(
        subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "spans", "PROJ-431", "--ledger-dir", str(tmp_path), "--gap-minutes", "7",
            ],
            capture_output=True, text=True, check=True,
        ).stdout
    )
    before = json.loads(
        subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "--ledger-dir", str(tmp_path), "--gap-minutes", "7", "spans", "PROJ-431",
            ],
            capture_output=True, text=True, check=True,
        ).stdout
    )
    # Both positions must reach the same ledger; a subparser default used to
    # clobber the root value and silently read the real home directory.
    assert after["gap_minutes"] == before["gap_minutes"] == 7
    assert after["days"] == before["days"] != []


def test_hook_and_reducer_agree_on_the_default_ledger_directory():
    # The two files define the path independently. If one moves, the hook writes
    # somewhere the reducer never reads and the loss is silent.
    spec = importlib.util.spec_from_file_location(
        "stamp", Path(__file__).parent / "nara-worklog-stamp.py"
    )
    stamp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(stamp)
    assert stamp.LEDGER_DIR == worklog.DEFAULT_LEDGER_DIR
    assert set(stamp.EVENT_MAP.values()) == set(worklog.SPAN_EVENTS)


# --- subtask attribution via switch markers ------------------------------


def sw(ts: str, ticket: str) -> dict:
    return {"ts": f"{ts}{TZ}", "ev": "switch", "ticket": ticket}


def test_no_marker_attributes_everything_to_the_branch_ticket(tmp_path):
    write_ledger(
        tmp_path, "PROJ-431", [ev("2026-09-02T09:00:00"), ev("2026-09-02T09:20:00")]
    )
    out = run(tmp_path, "spans", "PROJ-431")
    assert out["tickets"] == ["PROJ-431"]
    assert out["days"][0]["tickets"][0]["time_spent"] == "20m"


def test_marker_splits_one_span_between_two_subtasks(tmp_path):
    write_ledger(
        tmp_path,
        "PROJ-431",
        [
            ev("2026-09-02T09:00:00", "prompt"),
            sw("2026-09-02T09:30:00", "PROJ-500"),
            ev("2026-09-02T10:00:00", "turn_end"),
        ],
    )
    out = run(tmp_path, "spans", "PROJ-431")
    buckets = {b["ticket"]: b["time_spent"] for b in out["days"][0]["tickets"]}
    assert buckets == {"PROJ-431": "30m", "PROJ-500": "30m"}
    assert out["total_time_spent"] == "1h"


def test_markers_never_create_or_destroy_time(tmp_path):
    write_ledger(
        tmp_path,
        "PROJ-431",
        [
            ev("2026-09-02T09:00:00", "prompt"),
            sw("2026-09-02T09:10:00", "PROJ-500"),
            sw("2026-09-02T09:25:00", "PROJ-501"),
            sw("2026-09-02T09:40:00", "PROJ-502"),
            ev("2026-09-02T10:00:00", "turn_end"),
        ],
    )
    out = run(tmp_path, "spans", "PROJ-431")
    day = out["days"][0]
    assert sum(b["seconds"] for b in day["tickets"]) == day["seconds"] == 3600
    assert [b["ticket"] for b in day["tickets"]] == [
        "PROJ-431", "PROJ-500", "PROJ-501", "PROJ-502",
    ]
    assert [b["time_spent"] for b in day["tickets"]] == ["10m", "15m", "15m", "20m"]


def test_marker_carries_across_a_later_span(tmp_path):
    # A marker is not scoped to one span: it stays in force until the next one.
    write_ledger(
        tmp_path,
        "PROJ-431",
        [
            ev("2026-09-02T09:00:00", "prompt"),
            sw("2026-09-02T09:05:00", "PROJ-500"),
            ev("2026-09-02T09:20:00", "turn_end"),
            ev("2026-09-02T11:00:00", "prompt"),  # new span after an idle gap
            ev("2026-09-02T11:30:00", "turn_end"),
        ],
    )
    out = run(tmp_path, "spans", "PROJ-431")
    buckets = {b["ticket"]: b["time_spent"] for b in out["days"][0]["tickets"]}
    assert buckets == {"PROJ-431": "5m", "PROJ-500": "45m"}


def test_marker_inside_an_idle_gap_is_not_billed(tmp_path):
    # The marker lands between two spans, so it owns no time of its own -- it
    # only decides who owns the next span.
    write_ledger(
        tmp_path,
        "PROJ-431",
        [
            ev("2026-09-02T09:00:00", "prompt"),
            ev("2026-09-02T09:20:00", "turn_end"),
            sw("2026-09-02T10:00:00", "PROJ-500"),
            ev("2026-09-02T11:00:00", "prompt"),
            ev("2026-09-02T11:30:00", "turn_end"),
        ],
    )
    out = run(tmp_path, "spans", "PROJ-431")
    buckets = {b["ticket"]: b["time_spent"] for b in out["days"][0]["tickets"]}
    assert buckets == {"PROJ-431": "20m", "PROJ-500": "30m"}


def test_each_bucket_gets_its_own_jira_started(tmp_path):
    write_ledger(
        tmp_path,
        "PROJ-431",
        [
            ev("2026-09-02T09:00:00", "prompt"),
            sw("2026-09-02T09:30:00", "PROJ-500"),
            ev("2026-09-02T10:00:00", "turn_end"),
        ],
    )
    out = run(tmp_path, "spans", "PROJ-431")
    started = {b["ticket"]: b["jira_started"] for b in out["days"][0]["tickets"]}
    assert started == {
        "PROJ-431": "2026-09-02T09:00:00.000+0900",
        "PROJ-500": "2026-09-02T09:30:00.000+0900",
    }


def test_sub_minute_bucket_is_unpostable_but_its_day_survives(tmp_path):
    write_ledger(
        tmp_path,
        "PROJ-431",
        [
            ev("2026-09-02T09:00:00", "prompt"),
            sw("2026-09-02T09:19:40", "PROJ-500"),
            ev("2026-09-02T09:20:00", "turn_end"),
        ],
    )
    out = run(tmp_path, "spans", "PROJ-431")
    assert out["unpostable"] == ["2026-09-02 PROJ-500"]
    assert out["total_time_spent"] == "19m"  # the 20s bucket floors to 0m
    assert out["days"][0]["postable"] is True  # the day itself survives


def test_unreadable_marker_is_ignored_not_fatal(tmp_path):
    path = write_ledger(
        tmp_path,
        "PROJ-431",
        [ev("2026-09-02T09:00:00", "prompt"), ev("2026-09-02T09:20:00", "turn_end")],
    )
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"ev": "switch", "ticket": "PROJ-500"}) + "\n")  # no ts
        handle.write(json.dumps({"ev": "switch", "ts": "nope", "ticket": "X-1"}) + "\n")
        handle.write(json.dumps({"ev": "switch", "ts": f"2026-09-02T09:00:00{TZ}"}) + "\n")
    out = run(tmp_path, "spans", "PROJ-431")
    assert out["tickets"] == ["PROJ-431"]
    assert out["total_time_spent"] == "20m"


def test_mark_appends_to_the_branch_ledger(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(
        ["git", "init", "-q", "-b", "feature/PROJ-431-x", str(repo)], check=True
    )
    write_ledger(tmp_path, "PROJ-431", [ev("2026-09-02T09:00:00")])
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--ledger-dir", str(tmp_path), "mark", "PROJ-500"],
        capture_output=True, text=True, cwd=str(repo),
    )
    assert proc.returncode == 0, proc.stderr
    last = json.loads(
        (tmp_path / "PROJ-431.jsonl").read_text(encoding="utf-8").splitlines()[-1]
    )
    assert last["ev"] == "switch" and last["ticket"] == "PROJ-500"
    assert last["ledger"] == "PROJ-431"


def test_mark_rejects_a_non_ticket_argument(tmp_path):
    write_ledger(tmp_path, "PROJ-431", [ev("2026-09-02T09:00:00")])
    proc = subprocess.run(
        [
            sys.executable, str(SCRIPT), "--ledger-dir", str(tmp_path),
            "mark", "not-a-ticket", "--ledger-ticket", "PROJ-431",
        ],
        capture_output=True, text=True,
    )
    assert proc.returncode == 1
    assert (tmp_path / "PROJ-431.jsonl").read_text(encoding="utf-8").count("switch") == 0


# --- regressions found by the focused review 2026-09-03 ------------------


def test_bucket_spans_stay_chronological_and_pin_jira_started(tmp_path):
    # A bucket owning TWO spans is the only shape that distinguishes "first span"
    # from "last span". Without it, emitting spans in reverse order passed the
    # whole suite while shifting Jira's `started` by hours.
    write_ledger(
        tmp_path,
        "PROJ-431",
        [
            ev("2026-09-02T09:12:00", "prompt"),
            sw("2026-09-02T09:20:00", "PROJ-500"),
            ev("2026-09-02T10:05:00", "turn_end"),
            ev("2026-09-02T12:56:00", "prompt"),
            ev("2026-09-02T13:30:00", "turn_end"),
        ],
    )
    out = run(tmp_path, "spans", "PROJ-431")
    bucket = next(b for b in out["days"][0]["tickets"] if b["ticket"] == "PROJ-500")
    assert [s["duration"] for s in bucket["spans"]] == ["45m", "34m"]
    assert bucket["jira_started"] == "2026-09-02T09:20:00.000+0900"


def test_naive_switch_marker_on_disk_does_not_break_the_reduce(tmp_path):
    # Mirrors the watermark case: cmd_mark always writes aware timestamps, so
    # this guard exists for hand-edited or older ledgers.
    path = write_ledger(
        tmp_path,
        "PROJ-431",
        [ev("2026-09-02T09:00:00", "prompt"), ev("2026-09-02T10:00:00", "turn_end")],
    )
    with path.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps({"ts": "2026-09-02T09:30:00", "ev": "switch",
                        "ticket": "PROJ-500"}) + "\n"
        )
    out = run(tmp_path, "spans", "PROJ-431")
    assert out["tickets"] == ["PROJ-431", "PROJ-500"]
    assert out["total_time_spent"] == "1h"


def test_naive_span_timestamp_plus_marker_does_not_break_the_reduce(tmp_path):
    # The marker is the trigger: the same naive ledger reduced fine before
    # markers existed, so this crash path was introduced with them.
    path = tmp_path / "PROJ-431.jsonl"
    path.write_text(
        json.dumps({"ts": "2026-09-02T09:00:00", "ev": "prompt"}) + "\n"
        + json.dumps({"ts": "2026-09-02T10:00:00", "ev": "turn_end"}) + "\n"
        + json.dumps({"ts": f"2026-09-02T09:30:00{TZ}", "ev": "switch",
                      "ticket": "PROJ-500"}) + "\n",
        encoding="utf-8",
    )
    out = run(tmp_path, "spans", "PROJ-431")
    assert out["total_time_spent"] == "1h"


def test_markers_written_out_of_order_do_not_overlap_or_invent_time(tmp_path):
    # attribute()'s owner loop breaks early on the assumption that switches are
    # sorted. Unsorted input made the pieces OVERLAP: 60 minutes of input billed
    # as 100, with two subtasks vanishing.
    write_ledger(
        tmp_path,
        "PROJ-431",
        [
            ev("2026-09-02T09:00:00", "prompt"),
            sw("2026-09-02T09:40:00", "PROJ-502"),   # later marker written first
            sw("2026-09-02T09:20:00", "PROJ-501"),
            ev("2026-09-02T10:00:00", "turn_end"),
        ],
    )
    out = run(tmp_path, "spans", "PROJ-431")
    day = out["days"][0]
    assert day["seconds"] == 3600  # exactly the input span, no overlap
    assert [b["ticket"] for b in day["tickets"]] == [
        "PROJ-431", "PROJ-501", "PROJ-502",
    ]
    assert [b["time_spent"] for b in day["tickets"]] == ["20m", "20m", "20m"]


def test_out_of_order_span_events_do_not_produce_negative_spans(tmp_path):
    # build_spans sorts defensively; without it a clock step or hand edit yields
    # negative durations and a silently wrong total.
    write_ledger(
        tmp_path,
        "PROJ-431",
        [
            ev("2026-09-02T10:00:00", "turn_end"),
            ev("2026-09-02T09:10:00", "prompt"),
        ],
    )
    out = run(tmp_path, "spans", "PROJ-431")
    assert out["total_time_spent"] == "50m"
    assert all(s["seconds"] > 0 for s in day_spans(out["days"][0]))


def test_default_gap_is_90_minutes_without_any_flag(tmp_path):
    # Nothing pinned this: 90 -> 30 or -> 999999 both passed the whole suite,
    # and every user's billed time moves with it.
    assert worklog.DEFAULT_GAP_MINUTES == 90
    write_ledger(
        tmp_path,
        "PROJ-431",
        [
            ev("2026-09-02T09:00:00", "prompt"),
            ev("2026-09-02T10:29:00", "prompt"),   # 89m gap -> one span
            ev("2026-09-02T10:30:00", "turn_end"),
        ],
    )
    bare = json.loads(
        subprocess.run(
            [sys.executable, str(SCRIPT), "spans", "PROJ-431",
             "--ledger-dir", str(tmp_path)],
            capture_output=True, text=True, check=True,
            env={k: v for k, v in os.environ.items()
                 if k != "NARA_WORKLOG_GAP_MINUTES"},
        ).stdout
    )
    assert bare["gap_minutes"] == 90
    assert len(day_spans(bare["days"][0])) == 1


def test_gap_env_knob_is_honoured(tmp_path):
    write_ledger(
        tmp_path,
        "PROJ-431",
        [
            ev("2026-09-02T09:00:00", "prompt"),
            ev("2026-09-02T09:20:00", "prompt"),   # 20m gap -> splits at gap=10
            ev("2026-09-02T09:25:00", "turn_end"),
        ],
    )
    out = json.loads(
        subprocess.run(
            [sys.executable, str(SCRIPT), "spans", "PROJ-431",
             "--ledger-dir", str(tmp_path)],
            capture_output=True, text=True, check=True,
            env={**os.environ, "NARA_WORKLOG_GAP_MINUTES": "10"},
        ).stdout
    )
    assert out["gap_minutes"] == 10
    assert len(day_spans(out["days"][0])) == 2


@pytest.mark.parametrize("bad", ["abc", "0", "-5", ""])
def test_invalid_gap_value_fails_loudly_not_silently(tmp_path, bad):
    # 0 or negative silently drops all reading/review time from the billed total.
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "list", "--ledger-dir", str(tmp_path)],
        capture_output=True, text=True,
        env={**os.environ, "NARA_WORKLOG_GAP_MINUTES": bad},
    )
    assert proc.returncode != 0
    assert "Traceback" not in proc.stderr
    assert "gap minutes must be" in proc.stderr


def test_mark_refuses_to_create_a_ledger_that_the_hook_does_not_write(tmp_path):
    # An orphan ledger holding only markers means the hook is appending elsewhere
    # and those markers will never re-attribute anything.
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--ledger-dir", str(tmp_path),
         "mark", "PROJ-500", "--ledger-ticket", "PROJ-999"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 1
    assert "no ledger" in proc.stderr
    assert list(tmp_path.glob("*.jsonl")) == []


def test_mark_derives_the_ledger_from_the_branch_not_a_constant(tmp_path):
    # Decoy: a differently-named ledger must stay untouched, so replacing
    # branch_ticket() with a literal cannot pass.
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(
        ["git", "init", "-q", "-b", "feature/PROJ-777-x", str(repo)], check=True
    )
    write_ledger(tmp_path, "PROJ-777", [ev("2026-09-02T09:00:00")])
    decoy = write_ledger(tmp_path, "PROJ-431", [ev("2026-09-02T09:00:00")])
    before = decoy.read_text(encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--ledger-dir", str(tmp_path),
         "mark", "PROJ-500"],
        capture_output=True, text=True, cwd=str(repo),
    )
    assert proc.returncode == 0, proc.stderr
    assert "switch" in (tmp_path / "PROJ-777.jsonl").read_text(encoding="utf-8")
    assert decoy.read_text(encoding="utf-8") == before


def test_top_level_tickets_is_sorted_and_deduplicated(tmp_path):
    # A marker carries across days, so the same ticket appears in several buckets.
    write_ledger(
        tmp_path,
        "PROJ-431",
        [
            ev("2026-09-02T09:00:00", "prompt"),
            sw("2026-09-02T09:10:00", "PROJ-500"),
            ev("2026-09-02T09:30:00", "turn_end"),
            ev("2026-09-03T09:00:00", "prompt"),
            ev("2026-09-03T09:30:00", "turn_end"),
        ],
    )
    out = run(tmp_path, "spans", "PROJ-431")
    assert out["tickets"] == ["PROJ-431", "PROJ-500"]
    assert [d["date"] for d in out["days"]] == ["2026-09-02", "2026-09-03"]


def test_bucket_order_follows_real_time_across_mixed_offsets(tmp_path):
    # Sorting on the ISO string put +00:00 before +09:00 even when the +09:00
    # instant was earlier. One ledger can hold both (container TZ vs host TZ).
    path = tmp_path / "PROJ-431.jsonl"
    path.write_text(
        json.dumps({"ts": "2026-09-02T09:00:00+09:00", "ev": "prompt"}) + "\n"
        + json.dumps({"ts": "2026-09-02T01:00:00+00:00", "ev": "turn_end"}) + "\n"
        + json.dumps({"ts": "2026-09-02T00:30:00+00:00", "ev": "switch",
                      "ticket": "PROJ-500"}) + "\n",
        encoding="utf-8",
    )
    out = run(tmp_path, "spans", "PROJ-431")
    starts = [
        datetime.fromisoformat(b["spans"][0]["start"])
        for d in out["days"] for b in d["tickets"]
    ]
    assert starts == sorted(starts)
