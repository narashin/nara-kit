#!/usr/bin/env python3
"""Diff a design's layout contract against the implemented page's.

The parity bar for a design is layout, not pixels: which sections exist, in what order, a table's
columns in order, a form's fields in order, and which side each action sits on. Both sides are read
by the same extractor (`layout-contract.js`), so this is a mechanical diff rather than someone
comparing screenshots by eye. Generic — no design-system or product specifics.

    # design side  — studio: Export → "Layout contract (JSON)"
    # impl side    — on the running implemented page, in the DevTools console:
    #     <paste layout-contract.js>
    #     copy(JSON.stringify(window.LAYOUT_CONTRACT.extract(), null, 2))

    python3 check-layout.py design.layout.json impl.layout.json

Exit code 0 = layouts match, 1 = drift found, 2 = bad input. Section names differ across the two
sides (the design labels regions, the app does not), so sections are aligned by CONTENT overlap —
column names, field labels, action text — not by name.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------- model


@dataclass
class Section:
    index: int
    name: str
    title: str | None = None
    tabs: list[str] = field(default_factory=list)
    tables: list[list[str]] = field(default_factory=list)
    fields: list[str] = field(default_factory=list)
    rows: list[str] = field(default_factory=list)
    actions: list[tuple[str, str | None]] = field(default_factory=list)

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> "Section":
        return cls(
            index=int(raw.get("index", 0)),
            name=str(raw.get("name", "")),
            title=raw.get("title"),
            tabs=[str(t) for t in raw.get("tabs", [])],
            tables=[[str(c) for c in t.get("columns", [])] for t in raw.get("tables", [])],
            fields=[str(f) for f in raw.get("fields", [])],
            rows=[str(r) for r in raw.get("rows", [])],
            actions=[(str(a.get("text", "")), a.get("align")) for a in raw.get("actions", [])],
        )

    def signature(self) -> set[str]:
        """Texts that survive the design -> implementation trip: real labels, columns, button copy.

        Section names do not (the design labels regions; the app does not), so they stay out.
        """
        out: set[str] = set()
        if self.title:
            out.add(norm(self.title))
        out.update(norm(t) for t in self.tabs)
        for cols in self.tables:
            out.update(norm(c) for c in cols)
        out.update(norm(f) for f in self.fields)
        out.update(norm(r) for r in self.rows)
        out.update(norm(t) for t, _ in self.actions)
        out.discard("")
        return out

    def label(self) -> str:
        return f"{self.index}. {self.name}"


def norm(s: str) -> str:
    """Case- and whitespace-insensitive, and blind to the ellipsis the extractor adds when truncating."""
    return " ".join(s.split()).rstrip("…").strip().lower()


def load(path: str) -> list[Section]:
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"❌ cannot read {path}: {exc}")
    if not isinstance(data, dict) or "sections" not in data:
        raise SystemExit(f"❌ {path} is not a layout contract (no `sections` key)")
    return [Section.from_json(s) for s in data["sections"]]


# ---------------------------------------------------------------- alignment


def overlap(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def align(design: list[Section], impl: list[Section], threshold: float) -> list[tuple[Section | None, Section | None, float]]:
    """Greedy best-overlap matching: strongest pairs first, so a weak partial match can't steal a
    section that another one matches cleanly."""
    scored = sorted(
        (
            (overlap(d.signature(), i.signature()), di, ii)
            for di, d in enumerate(design)
            for ii, i in enumerate(impl)
        ),
        key=lambda t: (-t[0], t[1], t[2]),
    )
    d_taken: dict[int, int] = {}
    i_taken: dict[int, int] = {}
    for score, di, ii in scored:
        if score < threshold or di in d_taken or ii in i_taken:
            continue
        d_taken[di] = ii
        i_taken[ii] = di

    pairs: list[tuple[Section | None, Section | None, float]] = []
    for di, d in enumerate(design):
        if di in d_taken:
            ii = d_taken[di]
            pairs.append((d, impl[ii], overlap(d.signature(), impl[ii].signature())))
        else:
            pairs.append((d, None, 0.0))
    for ii, i in enumerate(impl):
        if ii not in i_taken:
            pairs.append((None, i, 0.0))
    return pairs


# ---------------------------------------------------------------- comparison


def seq_diff(kind: str, want: list[str], got: list[str]) -> list[str]:
    """Ordered list comparison — order IS the contract, so a reorder is a finding, not a nit."""
    if [norm(x) for x in want] == [norm(x) for x in got]:
        return []
    wset, gset = {norm(x) for x in want}, {norm(x) for x in got}
    missing = [x for x in want if norm(x) not in gset]
    extra = [x for x in got if norm(x) not in wset]
    out = []
    if missing:
        out.append(f"{kind}: missing {fmt(missing)}")
    if extra:
        out.append(f"{kind}: unexpected {fmt(extra)}")
    if not missing and not extra:
        out.append(f"{kind}: reordered — design {fmt(want)}, impl {fmt(got)}")
    return out


def fmt(items: list[str]) -> str:
    return ", ".join(f"`{i}`" for i in items) if items else "—"


def compare_pair(d: Section, i: Section) -> list[str]:
    issues: list[str] = []

    if d.title and i.title and norm(d.title) != norm(i.title):
        issues.append(f'title: design "{d.title}", impl "{i.title}"')
    elif d.title and not i.title:
        issues.append(f'title: missing "{d.title}"')

    issues += seq_diff("tabs", d.tabs, i.tabs)

    if len(d.tables) != len(i.tables):
        issues.append(f"tables: design has {len(d.tables)}, impl has {len(i.tables)}")
    for n, (dt, it) in enumerate(zip(d.tables, i.tables), start=1):
        prefix = "columns" if len(d.tables) == 1 else f"table {n} columns"
        issues += seq_diff(prefix, dt, it)

    issues += seq_diff("fields", d.fields, i.fields)
    issues += seq_diff("rows", d.rows, i.rows)

    issues += seq_diff("actions", [t for t, _ in d.actions], [t for t, _ in i.actions])
    impl_align = {norm(t): a for t, a in i.actions}
    for text, want_align in d.actions:
        got_align = impl_align.get(norm(text))
        if got_align is None or want_align is None:
            continue
        if got_align != want_align:
            issues.append(f"action `{text}`: design sits {want_align}, impl sits {got_align}")

    return issues


def run(design_path: str, impl_path: str, threshold: float) -> int:
    design, impl = load(design_path), load(impl_path)
    pairs = align(design, impl, threshold)

    findings: list[str] = []
    matched: list[tuple[Section, Section]] = []

    for d, i, score in pairs:
        if d is not None and i is not None:
            matched.append((d, i))
            for issue in compare_pair(d, i):
                findings.append(f"[{d.label()}] {issue}")
        elif d is not None:
            findings.append(f"[{d.label()}] MISSING in the implementation")
        elif i is not None:
            findings.append(f"[impl {i.label()}] NOT IN THE DESIGN")

    order_design = [d.index for d, i in matched]
    order_impl = [i.index for d, i in matched]
    if sorted(order_impl) != order_impl:
        seq = " → ".join(f"{d.name}" for d, _ in sorted(matched, key=lambda p: p[1].index))
        findings.append(f"[order] sections appear in a different order in the implementation: {seq}")

    print(f"design : {design_path}  ({len(design)} sections)")
    print(f"impl   : {impl_path}  ({len(impl)} sections)")
    print(f"matched: {len(matched)}")
    print()
    if not findings:
        print("✅ layout matches — section order, columns, fields and action placement all agree.")
        return 0
    print(f"❌ {len(findings)} layout difference(s):")
    for f in findings:
        print(f"  - {f}")
    print()
    print("Each line is a design decision the implementation changed. Fix the implementation, or")
    print("re-export the design if the change was agreed — do not leave the two disagreeing.")
    return 1


def main() -> int:
    p = argparse.ArgumentParser(description="Diff a design layout contract against the implemented page's.")
    p.add_argument("design", help="layout contract JSON exported from the studio")
    p.add_argument("impl", help="layout contract JSON captured from the implemented page")
    p.add_argument(
        "--threshold",
        type=float,
        default=0.2,
        help="minimum content overlap for two sections to be considered the same one (default: 0.2)",
    )
    args = p.parse_args()
    try:
        return run(args.design, args.impl, args.threshold)
    except SystemExit as exc:
        print(exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
