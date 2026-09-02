#!/usr/bin/env python3
"""Reduce a nara-worklog event ledger into per-day Jira worklog proposals.

The ledger is append-only JSONL written by the `nara-worklog-stamp.py` hook:

    {"ts": "...", "ev": "prompt",   "session": "...", "branch": "...", "cwd": "..."}
    {"ts": "...", "ev": "turn_end", ...}
    {"ts": "...", "ev": "logged", "through": "...", "seconds": 5216, ...}

`spans` groups prompt/turn_end events into interaction windows, splitting on
idle gaps and on local midnight, then aggregates per (day, ticket) bucket.
`record`
appends the `logged` watermark after a Jira write succeeds, which is what makes
re-running the skill idempotent.

Time arithmetic lives here, not in the model: an official worklog is a number
the team reads, so it must be reproducible from the ledger alone.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, time as dtime

DEFAULT_LEDGER_DIR = os.environ.get(
    "NARA_WORKLOG_DIR", os.path.expanduser("~/.claude/worklog")
)
SPAN_EVENTS = ("prompt", "turn_end")
SWITCH_EVENT = "switch"
# Same shape the hook uses to derive a ledger file from a branch name.
TICKET_RE = re.compile(r"([A-Z][A-Z0-9_]+-\d+)")
# A day totalling under a minute cannot be posted -- Jira rejects a zero worklog.
# Shared by aggregate() and cmd_list() so the threshold cannot drift between the
# two commands; the literal 60 in fmt_duration is a unit conversion, not this.
MIN_POSTABLE_SECONDS = 60
# Idle gap that ends one work window. 90, not 30: measured against a real day,
# 30 cut a 62m spec-review gap and a 55m gap out of billable time, while 90
# keeps them and still drops the 707m overnight gap that no model should bill.
DEFAULT_GAP_MINUTES = 90


def as_aware(stamp: datetime) -> datetime:
    """Attach the local offset to a naive timestamp.

    build_spans, watermark and read_switches all compare timestamps against each
    other, so all three must agree on this. One naive record on disk would
    otherwise raise TypeError and, because the ledger is append-only, break that
    ticket permanently.
    """
    return stamp if stamp.tzinfo else stamp.astimezone()


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
        stamps.append(as_aware(stamp))
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
    # Promote naive timestamps like watermark() and read_switches() do. Without
    # it a naive ts on disk plus any marker raises TypeError in attribute(), and
    # the ledger is append-only so that ticket could never be reduced again.
    stamps = sorted(
        (as_aware(datetime.fromisoformat(e["ts"])), e["ev"])
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


def read_switches(events: list[dict]) -> list[tuple[datetime, str]]:
    """Oldest-first (timestamp, ticket) markers written by `mark`.

    A marker means "from here on, this ticket". Without any marker every span
    belongs to the branch ticket, which is the original behaviour.
    """
    out = []
    for event in events:
        if event.get("ev") != SWITCH_EVENT or not event.get("ticket"):
            continue
        try:
            stamp = datetime.fromisoformat(event["ts"])
        except (KeyError, TypeError, ValueError):
            continue  # unreadable marker: ignore rather than crash the reduce
        out.append((as_aware(stamp), event["ticket"]))
    return sorted(out, key=lambda x: x[0])


def attribute(
    spans: list[tuple[datetime, datetime]],
    switches: list[tuple[datetime, str]],
    default_ticket: str,
) -> list[tuple[str, datetime, datetime]]:
    """Cut each span at every marker inside it and tag the pieces.

    A marker subdivides work that already happened; it never creates or destroys
    time, so the attributed seconds always sum to the input seconds.
    """
    if not switches:
        return [(default_ticket, start, end) for start, end in spans]

    out = []
    for start, end in spans:
        cuts = [t for t, _ in switches if start < t < end]
        edges = [start, *cuts, end]
        for left, right in zip(edges, edges[1:]):
            if right <= left:
                continue
            # The owner is the last marker at or before this piece's start.
            owner = default_ticket
            for stamp, ticket in switches:
                if stamp <= left:
                    owner = ticket
                else:
                    break
            out.append((owner, left, right))
    return out


def aggregate(
    spans: list[tuple[datetime, datetime]],
    switches: list[tuple[datetime, str]] | None = None,
    default_ticket: str = "",
) -> list[dict]:
    """Group work into (date, ticket) buckets -- one Jira worklog per bucket."""
    pieces = attribute(spans, switches or [], default_ticket)
    days: dict[str, dict] = {}
    for ticket, start, end in pieces:
        date = start.date().isoformat()
        day = days.setdefault(date, {"date": date, "tickets": {}, "seconds": 0})
        bucket = day["tickets"].setdefault(
            ticket, {"ticket": ticket, "spans": [], "seconds": 0}
        )
        seconds = int((end - start).total_seconds())
        bucket["spans"].append(
            {
                "start": start.isoformat(timespec="seconds"),
                "end": end.isoformat(timespec="seconds"),
                "seconds": seconds,
                "duration": fmt_duration(seconds),
            }
        )
        bucket["seconds"] += seconds
        day["seconds"] += seconds

    out = []
    for date in sorted(days):
        day = days[date]
        buckets = []
        # Sort on the parsed datetime, not the ISO string: mixed offsets in one
        # ledger (container TZ=UTC + host KST) make string order != time order,
        # which would invert the documented ascending write order.
        for bucket in sorted(
            day["tickets"].values(),
            key=lambda b: datetime.fromisoformat(b["spans"][0]["start"]),
        ):
            bucket["time_spent"] = fmt_duration(bucket["seconds"])
            bucket["jira_started"] = jira_started(
                datetime.fromisoformat(bucket["spans"][0]["start"])
            )
            bucket["postable"] = bucket["seconds"] >= MIN_POSTABLE_SECONDS
            buckets.append(bucket)
        day["tickets"] = buckets
        day["time_spent"] = fmt_duration(day["seconds"])
        # A day is postable if any of its buckets is; per-bucket is what gates writes.
        day["postable"] = any(b["postable"] for b in buckets)
        out.append(day)
    return out


def cmd_spans(args: argparse.Namespace) -> int:
    events = read_events(ledger_path(args.ledger_dir, args.ticket))
    mark = watermark(events)
    spans = build_spans(events, args.gap_minutes, mark)
    days = aggregate(spans, read_switches(events), args.ticket)
    # Jira is written once per (date, ticket) bucket, so the total sums the
    # FLOORED per-bucket minutes -- anything coarser reports time that no write
    # will actually carry.
    buckets = [b for d in days for b in d["tickets"] if b["postable"]]
    total = sum(b["seconds"] // 60 * 60 for b in buckets)
    json.dump(
        {
            "ticket": args.ticket,
            "gap_minutes": args.gap_minutes,
            "watermark": mark.isoformat(timespec="seconds") if mark else None,
            "days": days,
            "total_seconds": total,
            "total_time_spent": fmt_duration(total),
            "unpostable": [
                f"{d['date']} {b['ticket']}"
                for d in days
                for b in d["tickets"]
                if not b["postable"]
            ],
            "tickets": sorted({b["ticket"] for d in days for b in d["tickets"]}),
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


def branch_ticket(cwd: str | None = None) -> str | None:
    """Ticket key of the current branch -- the same rule the hook uses to pick
    the ledger file, so `mark` always lands in the ledger being written."""
    proc = subprocess.run(
        ["git", "-C", cwd or os.getcwd(), "branch", "--show-current"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    match = TICKET_RE.search(proc.stdout.strip())
    return match.group(1) if match else None


def cmd_mark(args: argparse.Namespace) -> int:
    """Append a switch marker: from now on this work belongs to <ticket>.

    The marker goes into the BRANCH ticket's ledger, because that is the file the
    hook appends to. Marking a subtask therefore subdivides the parent's ledger
    rather than starting a second one.
    """
    ledger_ticket = args.ledger_ticket or branch_ticket()
    if not ledger_ticket:
        sys.stderr.write(
            "no ticket key in the current branch; pass --ledger-ticket <PARENT>\n"
        )
        return 1

    path = ledger_path(args.ledger_dir, ledger_ticket)
    if not os.path.exists(path):
        sys.stderr.write(f"no ledger for {ledger_ticket}: {path}\n")
        return 1
    if not TICKET_RE.fullmatch(args.ticket):
        sys.stderr.write(f"not a ticket key: {args.ticket!r}\n")
        return 1

    record = {
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "ev": SWITCH_EVENT,
        "ticket": args.ticket,
        "ledger": ledger_ticket,
    }
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    json.dump({"marked": record}, sys.stdout, ensure_ascii=False, indent=2)
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
        type=parse_gap,
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

    p_mark = sub.add_parser(
        "mark", parents=[common], help="attribute following work to a subtask"
    )
    p_mark.add_argument("ticket", help="subtask key the work now belongs to")
    p_mark.add_argument(
        "--ledger-ticket",
        help="ledger to append to (default: ticket key of the current branch)",
    )
    p_mark.set_defaults(func=cmd_mark)

    p_list = sub.add_parser(
        "list", parents=[common], help="tickets carrying unlogged time"
    )
    p_list.set_defaults(func=cmd_list)
    return parser


def parse_gap(raw: str) -> int:
    """Idle threshold in minutes, >= 1.

    Validated because it silently changes an official worklog: 0 or a negative
    value splits every interval except prompt->turn_end, dropping all reading and
    review time from the billed total with no error at all.
    """
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError(
            f"gap minutes must be an integer >= 1, got {raw!r}"
        ) from None
    if value < 1:
        raise argparse.ArgumentTypeError(
            f"gap minutes must be >= 1, got {value}"
        )
    return value


def apply_defaults(parsed: argparse.Namespace) -> argparse.Namespace:
    """Fill options the user left off either side of the subcommand."""
    if not hasattr(parsed, "ledger_dir"):
        parsed.ledger_dir = DEFAULT_LEDGER_DIR
    if not hasattr(parsed, "gap_minutes"):
        parsed.gap_minutes = parse_gap(
            os.environ.get("NARA_WORKLOG_GAP_MINUTES", str(DEFAULT_GAP_MINUTES))
        )
    return parsed


if __name__ == "__main__":
    try:
        parsed = apply_defaults(build_parser().parse_args())
    except argparse.ArgumentTypeError as exc:
        # argparse only formats errors it raises itself; a bad env value reaches
        # here and must not surface as a traceback.
        sys.stderr.write(f"NARA_WORKLOG_GAP_MINUTES: {exc}\n")
        sys.exit(2)
    sys.exit(parsed.func(parsed))
