#!/usr/bin/env python3
"""Reduce a nara-worklog event ledger into per-day Jira worklog proposals.

The ledger is append-only JSONL written by the `nara-worklog-stamp.py` hook:

    {"ts": "...", "ev": "prompt",   "session": "...", "branch": "...", "cwd": "..."}
    {"ts": "...", "ev": "turn_end", ...}
    {"ts": "...", "ev": "logged", "through": "...", "seconds": 5216, ...}

`spans` groups prompt/turn_end events into interaction windows, splitting on
idle gaps and on local midnight, then aggregates per calendar day. `record`
appends the `logged` watermark after a Jira write succeeds, which is what makes
re-running the skill idempotent.

Time arithmetic lives here, not in the model: an official worklog is a number
the team reads, so it must be reproducible from the ledger alone.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, time as dtime

DEFAULT_LEDGER_DIR = os.environ.get(
    "NARA_WORKLOG_DIR", os.path.expanduser("~/.claude/worklog")
)
SPAN_EVENTS = ("prompt", "turn_end")


def ledger_path(ledger_dir: str, ticket: str) -> str:
    return os.path.join(ledger_dir, f"{ticket}.jsonl")


def read_events(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    events = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # a torn concurrent append must not break the reduction
    return events


def watermark(events: list[dict]) -> datetime | None:
    stamps = [
        datetime.fromisoformat(e["through"])
        for e in events
        if e.get("ev") == "logged" and e.get("through")
    ]
    return max(stamps) if stamps else None


def split_at_midnight(
    start: datetime, end: datetime
) -> list[tuple[datetime, datetime]]:
    out = []
    cursor = start
    while cursor.date() != end.date():
        boundary = datetime.combine(
            cursor.date() + timedelta(days=1), dtime.min, tzinfo=cursor.tzinfo
        )
        if boundary >= end:
            break
        out.append((cursor, boundary))
        cursor = boundary
    out.append((cursor, end))
    return out


def build_spans(
    events: list[dict], gap_minutes: int, since: datetime | None
) -> list[tuple[datetime, datetime]]:
    stamps = sorted(
        (datetime.fromisoformat(e["ts"]), e["ev"])
        for e in events
        if e.get("ev") in SPAN_EVENTS and e.get("ts")
    )
    if since is not None:
        stamps = [s for s in stamps if s[0] > since]
    if not stamps:
        return []

    gap = timedelta(minutes=gap_minutes)
    groups: list[list[datetime]] = [[stamps[0][0]]]
    prev_ts, prev_ev = stamps[0]
    for ts, event in stamps[1:]:
        # A long prompt -> turn_end interval is the agent working, not idle time,
        # so it never splits. Every other long interval means nobody was here:
        # turn_end -> prompt is the human away, and prompt -> prompt without an
        # intervening turn_end is a session that died mid-turn.
        working = prev_ev == "prompt" and event == "turn_end"
        if ts - prev_ts > gap and not working:
            groups.append([ts])
        else:
            groups[-1].append(ts)
        prev_ts, prev_ev = ts, event

    spans = []
    for group in groups:
        spans.extend(split_at_midnight(group[0], group[-1]))
    return spans


def fmt_duration(seconds: float) -> str:
    # Floor, never round: an official worklog must not claim a minute that was
    # not spent, and flooring also dodges banker's rounding on exact half-minutes.
    minutes = int(seconds // 60)
    hours, minutes = divmod(minutes, 60)
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    return " ".join(parts) or "0m"


def jira_started(dt: datetime) -> str:
    """Jira worklog `started` wants milliseconds and a colonless UTC offset."""
    return dt.strftime("%Y-%m-%dT%H:%M:%S.000%z")


def aggregate(spans: list[tuple[datetime, datetime]]) -> list[dict]:
    days: dict[str, dict] = {}
    for start, end in spans:
        key = start.date().isoformat()
        day = days.setdefault(key, {"date": key, "spans": [], "seconds": 0})
        seconds = (end - start).total_seconds()
        day["spans"].append(
            {
                "start": start.isoformat(timespec="seconds"),
                "end": end.isoformat(timespec="seconds"),
                "seconds": int(seconds),
                "duration": fmt_duration(seconds),
            }
        )
        day["seconds"] += int(seconds)

    out = []
    for key in sorted(days):
        day = days[key]
        day["time_spent"] = fmt_duration(day["seconds"])
        day["jira_started"] = jira_started(
            datetime.fromisoformat(day["spans"][0]["start"])
        )
        # A day that rounds to 0m cannot be posted: Jira rejects a zero worklog.
        day["postable"] = day["seconds"] >= 60
        out.append(day)
    return out


def cmd_spans(args: argparse.Namespace) -> int:
    events = read_events(ledger_path(args.ledger_dir, args.ticket))
    mark = watermark(events)
    spans = build_spans(events, args.gap_minutes, mark)
    days = aggregate(spans)
    total = sum(d["seconds"] for d in days)
    json.dump(
        {
            "ticket": args.ticket,
            "gap_minutes": args.gap_minutes,
            "watermark": mark.isoformat(timespec="seconds") if mark else None,
            "days": days,
            "total_seconds": total,
            "total_time_spent": fmt_duration(total),
            "latest_event": spans[-1][1].isoformat(timespec="seconds")
            if spans
            else None,
        },
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    sys.stdout.write("\n")
    return 0


def cmd_record(args: argparse.Namespace) -> int:
    path = ledger_path(args.ledger_dir, args.ticket)
    if not os.path.exists(path):
        sys.stderr.write(f"no ledger for {args.ticket}: {path}\n")
        return 1
    record = {
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "ev": "logged",
        "through": datetime.fromisoformat(args.through).isoformat(timespec="seconds"),
        "seconds": args.seconds,
        "time_spent": fmt_duration(args.seconds),
        "worklog_ids": args.worklog_id or [],
    }
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    json.dump({"recorded": record}, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    out = []
    if os.path.isdir(args.ledger_dir):
        for name in sorted(os.listdir(args.ledger_dir)):
            if not name.endswith(".jsonl"):
                continue
            ticket = name[: -len(".jsonl")]
            events = read_events(os.path.join(args.ledger_dir, name))
            spans = build_spans(events, args.gap_minutes, watermark(events))
            total = sum(int((e - s).total_seconds()) for s, e in spans)
            if total >= 60:
                out.append(
                    {
                        "ticket": ticket,
                        "unlogged_seconds": total,
                        "unlogged_time_spent": fmt_duration(total),
                        "days": len({s.date() for s, _ in spans}),
                    }
                )
    json.dump({"unlogged": out}, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger-dir", default=DEFAULT_LEDGER_DIR)
    parser.add_argument(
        "--gap-minutes",
        type=int,
        default=int(os.environ.get("NARA_WORKLOG_GAP_MINUTES", "30")),
        help="idle gap that splits one interaction window from the next",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_spans = sub.add_parser("spans", help="propose unlogged per-day worklogs")
    p_spans.add_argument("ticket")
    p_spans.set_defaults(func=cmd_spans)

    p_record = sub.add_parser("record", help="append the logged watermark")
    p_record.add_argument("ticket")
    p_record.add_argument("--through", required=True)
    p_record.add_argument("--seconds", type=int, required=True)
    p_record.add_argument("--worklog-id", action="append")
    p_record.set_defaults(func=cmd_record)

    p_list = sub.add_parser("list", help="tickets carrying unlogged time")
    p_list.set_defaults(func=cmd_list)
    return parser


if __name__ == "__main__":
    parsed = build_parser().parse_args()
    sys.exit(parsed.func(parsed))
