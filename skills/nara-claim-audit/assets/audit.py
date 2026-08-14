#!/usr/bin/env python3
"""claim-audit — compare numeric claims in a spec document against CSV snapshots.

The whole point of this module is determinism. A large document can carry
hundreds of numeric claims, so mismatches are corrected automatically; that is
only safe if measurement never guesses. Therefore:

  * the marker grammar is a fixed mini-DSL, and anything outside it is rejected
    loudly (SyntaxRejected) instead of interpreted;
  * a column or file that does not exist is a mapping failure, never a zero;
  * the same document plus the same CSVs always produce the same report.

Standard library only (csv, re, argparse) — no new dependencies.
"""

import argparse
import csv
import datetime
import json
import os
import re
import sys

AGGREGATES = ("count", "distinct", "sum", "avg", "max", "min")
OPERATORS = ("<=", ">=", "!=", "=", "<", ">")

# `<number> <!-- src: <expression> -->` — the claim is the last number before the marker.
MARKER_RE = re.compile(r"<!--\s*src:\s*(?P<expr>.+?)\s*-->")
NUMBER_RE = re.compile(r"(?P<num>-?\d+(?:\.\d+)?)(?!.*-?\d)")
INTENTIONAL_RE = re.compile(r"<!--\s*intentional:\s*(?P<reason>.+?)\s*-->")

# Constructs that must never be silently interpreted. Matched on word boundaries.
FORBIDDEN_WORDS = ("join", "select", "group", "having", "or", "union")
# A unit conversion must be spaced (`avg ms / 1000`), otherwise a filter value like
# `day=2026/01/02` would be shredded into a filter plus a bogus division.
SCALE_RE = re.compile(r"\s+(?P<op>[/*])\s+(?P<value>\d+(?:\.\d+)?)\s*$")


class SyntaxRejected(Exception):
    """The marker expression is outside the supported grammar."""


class MappingFailure(Exception):
    """The expression is well-formed but cannot be resolved against the data."""


class UnsafeSnapshotDir(Exception):
    """Snapshots would land in a tracked path, so recovery is not guaranteed."""


class Expression(object):
    def __init__(self, source, agg, column, filters, divisor, multiplier):
        self.source = source
        self.agg = agg
        self.column = column
        self.filters = filters
        self.divisor = divisor
        self.multiplier = multiplier

    @property
    def raw(self):
        parts = ["%s | %s %s" % (self.source, self.agg, self.column or "rows")]
        if self.filters:
            parts.append(
                "where " + " and ".join("%s%s%s" % f for f in self.filters)
            )
        return " ".join(parts)


class Claim(object):
    def __init__(self, line, value, expression, intentional, ambiguous=False, span=None):
        self.line = line
        self.value = value
        self.expression = expression
        self.intentional = intentional
        # More than one number sits between this marker and the previous one, so
        # which one the marker refers to is a guess. Guessing here rewrites an
        # unrelated fact ("10명 (전체 50명 중)" -> the 50 gets replaced), so the
        # claim is reported and never auto-replaced.
        self.ambiguous = ambiguous
        self.span = span


class Row(object):
    def __init__(self, claim, verdict, measured=None, detail=""):
        self.line = claim.line
        self.claimed = claim.value
        self.expression = claim.expression
        self.verdict = verdict
        self.measured = measured
        self.detail = detail
        self.span = claim.span


class Report(object):
    def __init__(self, document, rows, sources):
        self.document = document
        self.rows = rows
        self.sources = sources

    def counts(self):
        out = {}
        for row in self.rows:
            out[row.verdict] = out.get(row.verdict, 0) + 1
        return out


def parse_expression(text):
    """Parse a marker expression into an Expression, or reject it."""
    lowered = text.lower()
    # Word boundaries, not substrings: a column named `joined_at`, `selected` or
    # `union_id` is legitimate and must not be mistaken for JOIN / SELECT / UNION.
    for token in FORBIDDEN_WORDS:
        if re.search(r"(?<![a-z0-9_])%s(?![a-z0-9_])" % token, lowered):
            raise SyntaxRejected("forbidden construct %r in %r" % (token, text))
    if "(" in text or ")" in text:
        raise SyntaxRejected("parentheses are not supported in %r" % text)

    if "|" not in text:
        raise SyntaxRejected("expected '<file>.csv | <aggregate>' in %r" % text)

    source, _, body = text.partition("|")
    source = source.strip()
    body = body.strip()
    if not source.endswith(".csv"):
        raise SyntaxRejected("source must be a .csv file, got %r" % source)

    divisor = None
    multiplier = None
    scale = SCALE_RE.search(body)
    if scale:
        value = float(scale.group("value"))
        if value == 0:
            raise SyntaxRejected("unit conversion by zero")
        if scale.group("op") == "/":
            divisor = value
        else:
            multiplier = value
        body = body[: scale.start()].strip()

    filters = []
    if " where " in (" " + body):
        body, _, filter_text = body.partition(" where ")
        filters = _parse_filters(filter_text.strip())
        body = body.strip()

    parts = body.split()
    if not parts:
        raise SyntaxRejected("missing aggregate in %r" % text)
    agg = parts[0].lower()
    if agg not in AGGREGATES:
        raise SyntaxRejected(
            "unsupported aggregate %r (allowed: %s)" % (agg, ", ".join(AGGREGATES))
        )
    if len(parts) > 2:
        raise SyntaxRejected("unexpected trailing tokens in %r" % body)

    column = parts[1] if len(parts) == 2 else None
    if agg == "count":
        if column not in (None, "rows"):
            raise SyntaxRejected("count takes 'rows', got %r" % column)
        column = None
    elif column is None:
        raise SyntaxRejected("%s requires a column" % agg)

    return Expression(source, agg, column, filters, divisor, multiplier)


def _parse_filters(text):
    filters = []
    for chunk in re.split(r"\s+and\s+", text):
        chunk = chunk.strip()
        if not chunk:
            raise SyntaxRejected("empty filter clause")
        for op in OPERATORS:
            if op in chunk:
                column, _, value = chunk.partition(op)
                column = column.strip()
                value = value.strip().strip("'\"")
                if not column or not value:
                    raise SyntaxRejected("malformed filter %r" % chunk)
                filters.append((column, op, value))
                break
        else:
            raise SyntaxRejected("filter needs a comparison operator: %r" % chunk)
    return filters


def _compare(cell, op, wanted):
    """Compare numerically when the filter value is numeric, lexically otherwise.

    The numeric/lexical decision is made from the FILTER value, not per row.
    Deciding per row silently mixes two orderings inside one filter: with
    `amount>50`, a cell of "1,200" would fall back to string comparison and be
    excluded while "100" is included.
    """
    try:
        right = float(wanted)
    except (TypeError, ValueError):
        left, right = ("" if cell is None else cell), wanted
    else:
        if cell is None:
            return False  # ragged row: absent value never satisfies a numeric filter
        try:
            left = float(cell)
        except (TypeError, ValueError):
            raise MappingFailure(
                "non-numeric cell %r compared against numeric filter %r" % (cell, wanted)
            )
    if op == "=":
        return left == right
    if op == "!=":
        return left != right
    if op == "<":
        return left < right
    if op == ">":
        return left > right
    if op == "<=":
        return left <= right
    return left >= right


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise MappingFailure("csv has no header: %s" % path)
        return list(reader), list(reader.fieldnames)


def measure(expression, data_dir):
    path = os.path.join(data_dir, expression.source)
    if not os.path.isfile(path):
        raise MappingFailure("csv not found: %s" % expression.source)
    rows, headers = load_csv(path)
    if not rows:
        # A header-only file means the export failed. Reporting 0 here would put a
        # confident wrong number into the document, which is the bug this tool exists for.
        raise MappingFailure("csv has no data rows: %s" % expression.source)

    for column, _, _ in expression.filters:
        if column not in headers:
            raise MappingFailure(
                "column %r not in %s (headers: %s)"
                % (column, expression.source, ", ".join(headers))
            )
    if expression.column and expression.column not in headers:
        raise MappingFailure(
            "column %r not in %s (headers: %s)"
            % (expression.column, expression.source, ", ".join(headers))
        )

    for column, op, wanted in expression.filters:
        rows = [r for r in rows if _compare(r[column], op, wanted)]

    if not rows:
        # Filters that match nothing are almost always a typo in the value
        # ("status=churn" vs "churned"). Reporting 0 would write a confident wrong
        # number, so this is a mapping failure like a missing column.
        raise MappingFailure(
            "no rows match the filter for %s — check the filter values" % expression.raw
        )

    if expression.agg == "count":
        value = len(rows)
    elif expression.agg == "distinct":
        value = len({r[expression.column] for r in rows})
    else:
        numbers = []
        for r in rows:
            try:
                numbers.append(float(r[expression.column]))
            except ValueError:
                raise MappingFailure(
                    "non-numeric value %r in column %r"
                    % (r[expression.column], expression.column)
                )
        if not numbers:
            raise MappingFailure("no rows left to aggregate for %s" % expression.raw)
        if expression.agg == "sum":
            value = sum(numbers)
        elif expression.agg == "avg":
            value = sum(numbers) / len(numbers)
        elif expression.agg == "max":
            value = max(numbers)
        else:
            value = min(numbers)

    if expression.divisor:
        value = value / expression.divisor
    if expression.multiplier:
        value = value * expression.multiplier
    return _normalize(value)


def _normalize(value):
    if isinstance(value, float):
        value = round(value, 6)
        if value.is_integer():  # round first: 99.9999999 must become 100, not 100.0
            return int(value)
    return value


def extract_claims(document):
    claims = []
    in_code_block = False
    with open(document, encoding="utf-8", newline="") as handle:
        for index, raw in enumerate(handle, start=1):
            line = raw.rstrip("\r\n")
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                # A spec that documents this very syntax must not have its examples rewritten.
                continue

            cursor = 0
            for marker in MARKER_RE.finditer(line):
                segment = line[cursor : marker.start()]
                cursor = marker.end()
                numbers = list(CANDIDATE_RE.finditer(segment))
                if not numbers:
                    continue
                chosen = numbers[-1]
                intentional = INTENTIONAL_RE.search(line)
                claims.append(
                    Claim(
                        line=index,
                        value=chosen.group(0),
                        expression=marker.group("expr"),
                        intentional=intentional.group("reason") if intentional else None,
                        ambiguous=len(numbers) > 1,
                        span=(
                            marker.start() - len(segment) + chosen.start(),
                            marker.start() - len(segment) + chosen.end(),
                        ),
                    )
                )
    return claims


def _values_agree(claimed, measured):
    """Compare at the precision the document actually wrote."""
    try:
        claimed_number = float(claimed)
    except ValueError:
        return False
    if "." in claimed:
        places = len(claimed.split(".")[1])
        return round(float(measured), places) == round(claimed_number, places)
    return float(measured) == claimed_number


def audit_document(document, data_dir):
    rows = []
    sources = {}
    for claim in extract_claims(document):
        try:
            expression = parse_expression(claim.expression)
        except SyntaxRejected as error:
            rows.append(Row(claim, "syntax_error", detail=str(error)))
            continue

        path = os.path.join(data_dir, expression.source)
        if os.path.isfile(path) and expression.source not in sources:
            stamp = datetime.datetime.fromtimestamp(os.path.getmtime(path))
            sources[expression.source] = {"mtime": stamp.isoformat(timespec="seconds")}

        try:
            measured = measure(expression, data_dir)
        except MappingFailure as error:
            rows.append(Row(claim, "mapping_failure", detail=str(error)))
            continue

        if claim.intentional:
            rows.append(
                Row(claim, "intentional", measured, detail=claim.intentional)
            )
        elif claim.ambiguous and not _values_agree(claim.value, measured):
            rows.append(
                Row(
                    claim,
                    "ambiguous",
                    measured,
                    detail="여러 숫자가 마커 앞에 있어 어느 것이 주장인지 확정 불가 — 마커를 그 수치 바로 뒤로 옮길 것",
                )
            )
        elif _values_agree(claim.value, measured):
            rows.append(Row(claim, "match", measured))
        else:
            rows.append(Row(claim, "mismatch", measured))
    return Report(document, rows, sources)


# --- bootstrap path: candidates in unmarked documents ------------------------

# On a real spec roughly 70-80% of numeric tokens are not claims at all, so the
# filters below are what make this path usable. They are deliberately mechanical:
# a candidate is a proposal for a human to mark, never a measured verdict.
DATE_RE = re.compile(r"\b\d{4}[-/.]\d{1,2}(?:[-/.]\d{1,2})?\b")
VERSION_RE = re.compile(r"\bv?\d+\.\d+(?:\.\d+)+\b")
SECTION_REF_RE = re.compile(r"§\s*\d+(?:\.\d+)*")
ORDERED_ITEM_RE = re.compile(r"^\s*\d+[.)]\s")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
PATH_RE = re.compile(r"[\w./-]*/[\w./-]*\d[\w./-]*")
CANDIDATE_RE = re.compile(r"-?\d+(?:\.\d+)?")


class Candidate(object):
    def __init__(self, line, value, text):
        self.line = line
        self.value = value
        self.text = text


def extract_candidates(document):
    """Return numeric tokens that plausibly are claims, with the noise removed."""
    candidates = []
    in_code_block = False
    with open(document, encoding="utf-8") as handle:
        for index, raw in enumerate(handle, start=1):
            line = raw.rstrip("\n")
            stripped = line.strip()

            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue
            if stripped.startswith("#"):
                continue  # heading numbers are structure, not claims
            if ORDERED_ITEM_RE.match(line):
                continue  # list ordinals
            if MARKER_RE.search(line):
                continue  # already marked — the audit path owns these
            # Blockquote lines are NOT skipped: real specs put source counts there
            # ("> 데이터: ... 메시지 175건"). Dates inside them are removed below.

            scrubbed = INLINE_CODE_RE.sub(" ", line)
            scrubbed = DATE_RE.sub(" ", scrubbed)
            scrubbed = VERSION_RE.sub(" ", scrubbed)
            scrubbed = SECTION_REF_RE.sub(" ", scrubbed)
            scrubbed = PATH_RE.sub(" ", scrubbed)

            for match in CANDIDATE_RE.finditer(scrubbed):
                candidates.append(Candidate(index, match.group(0), line))
    return candidates


def fact_cards(data_dir):
    """Summarise every CSV so unmarked numbers can be matched against reality."""
    cards = {}
    if not os.path.isdir(data_dir):
        return cards
    for name in sorted(os.listdir(data_dir)):
        if not name.endswith(".csv"):
            continue
        try:
            rows, headers = load_csv(os.path.join(data_dir, name))
        except (MappingFailure, OSError, UnicodeDecodeError):
            continue
        distinct = {h: len({r[h] for r in rows}) for h in headers}
        sums = {}
        for header in headers:
            numbers = []
            for row in rows:
                try:
                    numbers.append(float(row[header]))
                except (TypeError, ValueError):
                    numbers = []
                    break
            if numbers:
                sums[header] = _normalize(sum(numbers))
        cards[name] = {"rows": len(rows), "distinct": distinct, "sums": sums}
    return cards


def suggest_sources(value, cards):
    """Return (file, description, value) triples whose fact equals this number."""
    try:
        wanted = float(value)
    except ValueError:
        return []
    hits = []
    for name in sorted(cards):
        card = cards[name]
        if float(card["rows"]) == wanted:
            hits.append((name, "count rows", card["rows"]))
        for column in sorted(card["distinct"]):
            if float(card["distinct"][column]) == wanted:
                hits.append((name, "distinct %s" % column, card["distinct"][column]))
        for column in sorted(card["sums"]):
            if float(card["sums"][column]) == wanted:
                hits.append((name, "sum %s" % column, card["sums"][column]))
    return hits


# --- auto-replace path -------------------------------------------------------

# Below this count a proportional gate is meaningless (2 -> 3 is a 50% move but
# perfectly ordinary), so the ratio check only applies to larger numbers.
SMALL_NUMBER_FLOOR = 10
COLLAPSE_RATIO = 0.1
EXPLOSION_RATIO = 10
LARGE_MOVE_RATIO = 0.5


class ApplyResult(object):
    def __init__(self):
        self.replaced = 0
        self.held = 0
        self.intentional = 0
        self.unresolved = 0
        self.matched = 0
        self.snapshot = None
        self.changes = []
        self.holds = []


def sanity_hold(claimed, measured):
    """Return a reason string when a replacement looks like data corruption."""
    try:
        claimed_number = float(claimed)
    except ValueError:
        return "claimed value is not numeric: %r" % claimed
    measured_number = float(measured)

    if claimed_number == 0:
        if measured_number != 0:
            return "claimed 0 but measured %s — ratio undefined" % measured
        return None
    if measured_number == 0:
        # Reaching here means a legitimately empty aggregate; writing 0 over a real
        # number is the failure this tool exists to prevent, so never do it silently.
        return "measured 0 against claimed %s — refusing to write a zero" % claimed
    if abs(claimed_number) < SMALL_NUMBER_FLOOR and abs(measured_number) < SMALL_NUMBER_FLOOR:
        # Both small: a ratio test is meaningless (2 -> 3 is +50%), but a big
        # proportional move on fractions still matters, so guard sub-1 values.
        if abs(claimed_number) < 1 or abs(measured_number) < 1:
            ratio = measured_number / claimed_number
            if ratio <= COLLAPSE_RATIO or ratio >= EXPLOSION_RATIO:
                return "fractional value moved %sx (claimed %s, measured %s)" % (
                    round(ratio, 3),
                    claimed,
                    measured,
                )
        return None

    # A truncated export (LIMIT 1000 over 5000 rows) sits at ratio 0.2 and would sail
    # through a collapse-only test. Any correction that moves a number by more than
    # half is suspicious enough to hand back to a human — being wrong by >50% is rare
    # for a real spec, common for a broken query.
    relative_move = abs(measured_number - claimed_number) / abs(claimed_number)
    if relative_move > LARGE_MOVE_RATIO:
        return "measured %s moves claimed %s by %d%% — verify the export is complete" % (
            measured,
            claimed,
            round(relative_move * 100),
        )

    ratio = measured_number / claimed_number
    if ratio <= COLLAPSE_RATIO:
        return "measured %s is a collapse from claimed %s (suspect empty or over-filtered csv)" % (
            measured,
            claimed,
        )
    if ratio >= EXPLOSION_RATIO:
        return "measured %s is %dx claimed %s (suspect wrong source)" % (
            measured,
            int(ratio),
            claimed,
        )
    return None


def _is_git_ignored(path):
    """Ask git about the ABSOLUTE probe path from a directory that exists.

    Both halves matter: a relative probe combined with a cwd inside the snapshot
    tree makes git answer about a different path entirely, and pointing cwd at a
    directory that has not been created yet makes the call raise, which the
    caller reads as "not ignored" and refuses forever.
    """
    import subprocess

    absolute = os.path.abspath(path)
    probe = os.path.join(absolute, ".probe")
    cwd = absolute
    while not os.path.isdir(cwd):
        parent = os.path.dirname(cwd)
        if parent == cwd:
            return False
        cwd = parent
    try:
        result = subprocess.run(
            ["git", "check-ignore", "-q", probe], cwd=cwd, capture_output=True
        )
    except OSError:
        return False
    return result.returncode == 0


def _replace_on_line(line, old_value, new_value):
    """Replace only the number that precedes the src marker on this line."""
    marker = MARKER_RE.search(line)
    if not marker:
        return line
    head, tail = line[: marker.start()], line[marker.start() :]
    number = NUMBER_RE.search(head)
    if not number or number.group("num") != old_value:
        return line
    patched = head[: number.start("num")] + new_value + head[number.end("num") :]
    return patched + tail


def _format_measured(claimed, measured):
    """Keep the document's own precision so 2.0 does not become 2."""
    if "." in claimed:
        places = len(claimed.split(".")[1])
        return ("%%.%df" % places) % float(measured)
    return str(measured)


def apply_fixes(
    document, data_dir, snapshot_dir, dry_run=False, require_ignored=True
):
    report = audit_document(document, data_dir)
    result = ApplyResult()

    pending = []
    for row in report.rows:
        if row.verdict == "match":
            result.matched += 1
        elif row.verdict == "intentional":
            result.intentional += 1
        elif row.verdict in ("mapping_failure", "syntax_error", "ambiguous"):
            # Ambiguous counts as unresolved: the publish gate must block on it,
            # otherwise an unverified number ships looking verified.
            result.unresolved += 1
        elif row.verdict == "mismatch":
            reason = sanity_hold(row.claimed, row.measured)
            if reason:
                result.held += 1
                result.holds.append((row.line, row.claimed, row.measured, reason))
            else:
                pending.append(row)

    result.replaced = len(pending)
    result.changes = [
        (r.line, r.claimed, _format_measured(r.claimed, r.measured)) for r in pending
    ]
    if dry_run or not pending:
        return result

    if require_ignored and not _is_git_ignored(snapshot_dir):
        raise UnsafeSnapshotDir(
            "snapshot dir is not gitignored: %s — recovery would not be guaranteed"
            % snapshot_dir
        )

    # One directory per run. A flat basename would let the second run overwrite the
    # snapshot with output of the first, destroying the only copy of the original —
    # exactly when a user is trying to undo a bad run.
    run_dir = os.path.join(snapshot_dir, _run_stamp())
    os.makedirs(run_dir, exist_ok=True)
    # Never overwrite an existing recovery copy, but never refuse to run either:
    # two runs inside the same second are ordinary, a lost original is not.
    base = os.path.basename(document)
    candidate = os.path.join(run_dir, base)
    suffix = 1
    while os.path.exists(candidate):
        stem, extension = os.path.splitext(base)
        candidate = os.path.join(run_dir, "%s-%d%s" % (stem, suffix, extension))
        suffix += 1
    result.snapshot = os.path.abspath(candidate)
    shutil_copy(document, result.snapshot)

    # Replace by (line, span) so a second marker on the same line keeps its own claim,
    # and so the exact token the audit judged is the token that gets rewritten.
    wanted = {}
    for row in pending:
        wanted.setdefault(row.line, []).append(
            (row.span, row.claimed, _format_measured(row.claimed, row.measured))
        )
    with open(document, encoding="utf-8", newline="") as handle:
        lines = handle.readlines()
    for index in sorted(wanted):
        line = lines[index - 1]
        ending = ""
        for candidate in ("\r\n", "\n", "\r"):
            if line.endswith(candidate):
                ending = candidate
                line = line[: -len(candidate)]
                break
        for span, old, new in sorted(wanted[index], key=lambda item: item[0][0], reverse=True):
            start, end = span
            if line[start:end] != old:
                continue  # document changed under us; leave it alone
            line = line[:start] + new + line[end:]
        lines[index - 1] = line + ending
    with open(document, "w", encoding="utf-8", newline="") as handle:
        handle.writelines(lines)
    return result


def _run_stamp():
    import time

    return time.strftime("%Y%m%d-%H%M%S")


def shutil_copy(src, dst):
    import shutil

    shutil.copy2(src, dst)


def render_text(report):
    lines = ["# claim audit — %s" % os.path.basename(report.document), ""]
    for name in sorted(report.sources):
        lines.append("source: %s (mtime %s)" % (name, report.sources[name]["mtime"]))
    lines.append("")
    lines.append("| line | claimed | measured | verdict | detail |")
    lines.append("|---|---|---|---|---|")
    for row in report.rows:
        measured = "" if row.measured is None else str(row.measured)
        lines.append(
            "| %d | %s | %s | %s | %s |"
            % (
                row.line,
                row.claimed,
                measured,
                row.verdict,
                row.detail.replace("|", "\\|"),  # keep the markdown table intact
            )
        )
    counts = report.counts()
    lines.append("")
    lines.append(
        "summary: "
        + ", ".join("%s=%d" % (key, counts[key]) for key in sorted(counts))
    )
    lines.append("결론은 CSV 스냅샷 기준. 게시본·라이브 DB와의 동기화는 검증하지 않음.")
    return "\n".join(lines)


def render_apply(result, dry_run):
    verb = "예정" if dry_run else "완료"
    lines = ["# claim audit — 자동 교체 %s" % verb, ""]
    for line, old, new in result.changes:
        lines.append("- line %d: %s → %s" % (line, old, new))
    for line, claimed, measured, reason in result.holds:
        lines.append("- line %d: 보류 (%s → %s) — %s" % (line, claimed, measured, reason))
    lines.append("")
    lines.append(
        "summary: replaced=%d, held=%d, intentional=%d, unresolved=%d, match=%d"
        % (
            result.replaced,
            result.held,
            result.intentional,
            result.unresolved,
            result.matched,
        )
    )
    if result.snapshot:
        lines.append("snapshot: %s" % result.snapshot)
        lines.append("복구: cp '%s' <원경로>" % result.snapshot)
    lines.append("결론은 CSV 스냅샷 기준. 게시본·라이브 DB와의 동기화는 검증하지 않음.")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Audit numeric claims against CSVs.")
    parser.add_argument("--doc", required=True, help="spec markdown to audit")
    parser.add_argument("--data", required=True, help="directory holding the CSVs")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    parser.add_argument(
        "--apply", action="store_true", help="replace mismatched values in the document"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="with --apply, show changes without writing"
    )
    parser.add_argument(
        "--bootstrap",
        action="store_true",
        help="propose marker candidates for an unmarked document",
    )
    parser.add_argument(
        "--snapshot-dir",
        default=".claims-audit/runs",
        help="gitignored directory for pre-write snapshots",
    )
    args = parser.parse_args(argv)

    if args.bootstrap:
        cards = fact_cards(args.data)
        candidates = extract_candidates(args.doc)
        print("# claim audit — 마커 후보 (제안, 판정 아님)")
        print("")
        print("후보 %d건. 각 후보에 마커를 달면 이후 감사는 전자동." % len(candidates))
        print("")
        print("| line | value | 근접한 CSV 사실 | 문맥 |")
        print("|---|---|---|---|")
        for candidate in candidates:
            hits = suggest_sources(candidate.value, cards)
            hint = "; ".join("%s %s" % (h[0], h[1]) for h in hits) or "-"
            print(
                "| %d | %s | %s | %s |"
                % (candidate.line, candidate.value, hint, candidate.text.strip()[:60])
            )
        print("")
        print("제안일 뿐이다 — 어느 CSV의 어떤 집계인지는 사람이 확정한다.")
        return 0

    if args.apply:
        try:
            result = apply_fixes(
                args.doc, args.data, args.snapshot_dir, dry_run=args.dry_run
            )
        except UnsafeSnapshotDir as error:
            print("→ ESCALATE: %s" % error)
            return 2
        print(render_apply(result, args.dry_run))
        return 1 if (result.unresolved or result.held) else 0

    report = audit_document(args.doc, args.data)
    if args.json:
        print(
            json.dumps(
                {
                    "document": report.document,
                    "sources": report.sources,
                    "rows": [
                        {
                            "line": r.line,
                            "claimed": r.claimed,
                            "measured": r.measured,
                            "verdict": r.verdict,
                            "expression": r.expression,
                            "detail": r.detail,
                        }
                        for r in report.rows
                    ],
                    "summary": report.counts(),
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print(render_text(report))

    counts = report.counts()
    blocking = counts.get("mapping_failure", 0) + counts.get("syntax_error", 0)
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
