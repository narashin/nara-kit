#!/usr/bin/env python3
"""Validate the qa-data block of a generated QA sheet.

Checks the data only: it does not open a browser, so it says nothing about
whether checks and notes persist at runtime.

Usage: check_sheet.py <sheet.html>
Exit 0 = clean, 1 = problems found, 2 = cannot read the sheet.
"""

import json
import re
import sys

STATES = {"manual", "partial", "auto-verified"}
PROVENANCES = {"observed", "code-only", "spec-only", "user-provided"}
BLOCK = re.compile(
    r'<script type="application/json" id="qa-data">(.*?)</script>', re.S
)


def check(data):
    problems = []
    if data.get("sample") or data.get("storageKey") == "qa-sample":
        problems.append("template sample data was not replaced")
    if not data.get("storageKey"):
        problems.append("storageKey is missing")
    target = data.get("target") or {}
    for field in ("repo", "base", "head"):
        if not target.get(field):
            problems.append(f"target.{field} is missing")
    if not isinstance(data.get("limitations", []), list):
        problems.append("limitations must be a list")

    seen = set()
    total = 0
    for area in data.get("areas") or []:
        for screen in area.get("screens") or []:
            where = screen.get("title") or screen.get("route") or "<untitled screen>"
            if not (screen.get("title") or screen.get("route")):
                problems.append("a screen has neither title nor route")
            for item in screen.get("checks") or []:
                total += 1
                cid = item.get("id")
                if not cid:
                    problems.append(f"{where}: a check has no id")
                elif cid in seen:
                    problems.append(f"duplicate check id: {cid}")
                seen.add(cid)
                state = item.get("state")
                prov = item.get("provenance")
                if state not in STATES:
                    problems.append(f"{cid}: invalid state {state!r}")
                if prov not in PROVENANCES:
                    problems.append(f"{cid}: invalid provenance {prov!r}")
                for field in ("trigger", "expect"):
                    if not item.get(field):
                        problems.append(f"{cid}: {field} is empty")
                if state in ("auto-verified", "partial") and not item.get("evidence"):
                    problems.append(f"{cid}: {state} needs evidence")
                if state == "auto-verified" and prov in ("code-only", "spec-only"):
                    problems.append(f"{cid}: auto-verified cannot be {prov}")
    if total == 0:
        problems.append("the sheet has no checks")
    return problems, total


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as handle:
            html = handle.read()
    except OSError as error:
        print(f"cannot read {argv[1]}: {error}", file=sys.stderr)
        return 2
    match = BLOCK.search(html)
    if not match:
        print("qa-data block not found", file=sys.stderr)
        return 2
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as error:
        print(f"qa-data is not valid JSON: {error}", file=sys.stderr)
        return 2
    problems, total = check(data)
    for problem in problems:
        print(f"FAIL {problem}")
    if problems:
        return 1
    print(f"ok: {total} checks")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
