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
# A day totalling under a minute cannot be posted -- Jira rejects a zero worklog.
# Shared by aggregate() and cmd_list() so the threshold cannot drift between the
# two commands; the literal 60 in fmt_duration is a unit conversion, not this.
MIN_POSTABLE_SECONDS = 60


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
    """Latest recorded `through`, always offset-aware.

    A naive value here would raise TypeError against the hook's aware `ts` on
    every later run, and the ledger is append-only -- so a single bad record
    would permanently break this ticket and, via cmd_list, every other one.
    cmd_record rejects naive input; this promotes anything already on disk.
    """
    stamps = []
    for event in events:
        if event.get("ev") != "logged" or not event.get("through"):
            continue
        try:
            stamp = datetime.fromisoformat(event["through"])
        except (TypeError, ValueError):
            continue  # unparseable watermark: ignore rather than crash the reduce
        stamps.append(stamp if stamp.tzinfo else stamp.astimezone())
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
        day["postable"] = day["seconds"] >= MIN_POSTABLE_SECONDS
        out.append(day)
    return out


def cmd_spans(args: argparse.Namespace) -> int:
    events = read_events(ledger_path(args.ledger_dir, args.ticket))
    mark = watermark(events)
    spans = build_spans(events, args.gap_minutes, mark)
    days = aggregate(spans)
    # Sum the per-day FLOORED minutes, not the raw seconds. Jira is written once
    # per day, so a raw-seconds total revives the sub-minute remainders each day
    # already discarded and reports more than what actually gets posted.
    postable = [d for d in days if d["postable"]]
    total = sum(d["seconds"] // 60 * 60 for d in postable)
    json.dump(
        {
            "ticket": args.ticket,
            "gap_minutes": args.gap_minutes,
            "watermark": mark.isoformat(timespec="seconds") if mark else None,
            "days": days,
            "total_seconds": total,
            "total_time_spent": fmt_duration(total),
            "unpostable_days": [d["date"] for d in days if not d["postable"]],
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
    try:
        through = datetime.fromisoformat(args.through)
    except ValueError:
        sys.stderr.write(f"--through is not an ISO timestamp: {args.through!r}\n")
        return 1
    if through.tzinfo is None or through.utcoffset() is None:
        # Refuse rather than normalise. The ledger is append-only, so a naive
        # watermark here cannot be taken back and would raise TypeError against
        # the hook's aware timestamps on every later spans/list run -- including
        # for unrelated tickets, since cmd_list walks the whole directory.
        sys.stderr.write(
            f"--through must carry a UTC offset, got {args.through!r}. "
            "Pass the `latest_event` value from `spans` verbatim.\n"
        )
        return 1

    record = {
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "ev": "logged",
        "through": through.isoformat(timespec="seconds"),
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
            if total >= MIN_POSTABLE_SECONDS:
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
    # Flags live on both the root and every subcommand so they work either side
    # of the verb. Root-only placement rejects `spans TICKET --gap-minutes 60`,
    # the form the skill's own docs lead you to write.
    # SUPPRESS, not a real default: with `parents=`, the same option exists on
    # the root and on each subparser, and a subparser default OVERWRITES what the
    # root already parsed -- so `--ledger-dir X spans T` silently read the default
    # directory. SUPPRESS leaves the attribute unset unless the user passes it,
    # and apply_defaults() fills it in once, after both levels have had their say.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--ledger-dir", default=argparse.SUPPRESS)
    common.add_argument(
        "--gap-minutes",
        type=int,
        default=argparse.SUPPRESS,
        help="idle gap that splits one interaction window from the next",
    )

    parser = argparse.ArgumentParser(description=__doc__, parents=[common])
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_spans = sub.add_parser(
        "spans", parents=[common], help="propose unlogged per-day worklogs"
    )
    p_spans.add_argument("ticket")
    p_spans.set_defaults(func=cmd_spans)

    p_record = sub.add_parser(
        "record", parents=[common], help="append the logged watermark"
    )
    p_record.add_argument("ticket")
    p_record.add_argument("--through", required=True)
    p_record.add_argument("--seconds", type=int, required=True)
    p_record.add_argument("--worklog-id", action="append")
    p_record.set_defaults(func=cmd_record)

    p_list = sub.add_parser(
        "list", parents=[common], help="tickets carrying unlogged time"
    )
    p_list.set_defaults(func=cmd_list)
    return parser


def apply_defaults(parsed: argparse.Namespace) -> argparse.Namespace:
    """Fill options the user left off either side of the subcommand."""
    if not hasattr(parsed, "ledger_dir"):
        parsed.ledger_dir = DEFAULT_LEDGER_DIR
    if not hasattr(parsed, "gap_minutes"):
        parsed.gap_minutes = int(os.environ.get("NARA_WORKLOG_GAP_MINUTES", "30"))
    return parsed


if __name__ == "__main__":
    parsed = apply_defaults(build_parser().parse_args())
    sys.exit(parsed.func(parsed))
