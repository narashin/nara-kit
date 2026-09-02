#!/usr/bin/env python3
"""Validate that an eval suite's graders discriminate correct from incorrect output.

`waza run` cannot execute nara-kit skills here: the `copilot-sdk` engine needs a
Copilot seat, and the `mock` engine never invokes the skill -- it echoes the
prompt, task description and fixture text, so grading its output measures the
eval against itself. Every suite therefore carries a `real_run` provenance gate
that fails under mock on purpose.

What is still measurable without an engine is the graders themselves. Feed them a
hand-written correct output and a hand-written incorrect one; a suite whose
graders cannot tell those apart cannot measure a skill either, and that is worth
knowing before trusting any score.

    tools/eval-fixture.py probe    nara-gap
    tools/eval-fixture.py fill     nara-gap --side right
    tools/eval-fixture.py validate nara-gap

`validate` runs the whole loop and reports discrimination. Expected outcome:
right passes every task, wrong passes none. Anything else is a grader defect --
a wrong-side pass means the assertion is satisfiable by incorrect output, and a
right-side failure means it is unsatisfiable by correct output.

The RIGHT/WRONG table lives in `evals/<skill>/validation.yaml`:

    right:
      basic-usage-001: |
        <what a correct run of this skill outputs>
    wrong:
      basic-usage-001: |
        <observed incorrect behaviour -- reproduce a real failure, do not invent one>

Populate `wrong` from behaviour the skill actually produced. Invented failures are
easy to discriminate and prove nothing.
"""

import argparse
import copy
import json
import pathlib
import subprocess
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")

ROOT = pathlib.Path(__file__).resolve().parent.parent
MOCK_MARKER = "Mock response for:"


def paths(skill: str) -> dict:
    base = ROOT / "evals" / skill
    return {
        "eval": base / "eval.yaml",
        "table": base / "validation.yaml",
        "probe": ROOT / "results" / f"{skill}-probe.json",
        "right": ROOT / "results" / f"{skill}-right.json",
        "wrong": ROOT / "results" / f"{skill}-wrong.json",
    }


def waza(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["waza", *args], cwd=ROOT, capture_output=True, text=True)


def cmd_probe(args: argparse.Namespace) -> int:
    """Capture the output-JSON shape via a mock run. Scores here are meaningless."""
    p = paths(args.skill)
    p["probe"].parent.mkdir(parents=True, exist_ok=True)
    # Delete first, then require the file back. results/ is not cleaned between
    # runs, so an existence check alone passed on a previous run's file and
    # validate then reported "N/N discriminate" over a stale task list.
    #
    # A non-zero exit is NOT an error here: the mock run fails every task by
    # design (the real_run provenance gate), and this step only wants the shape
    # of the output JSON. The freshness guarantee comes from the unlink.
    p["probe"].unlink(missing_ok=True)
    proc = waza("run", args.skill, "--output", str(p["probe"]))
    if not p["probe"].exists():
        sys.stderr.write(
            f"waza run wrote no probe (rc={proc.returncode}):\n{proc.stdout}{proc.stderr}"
        )
        return 1
    tasks = json.loads(p["probe"].read_text())["tasks"]
    print(f"probe written: {p['probe'].relative_to(ROOT)} ({len(tasks)} tasks)")
    print("task ids:", ", ".join(t["test_id"] for t in tasks))
    return 0


def cmd_fill(args: argparse.Namespace) -> int:
    """Swap each task's final_output for the table's text for one side."""
    p = paths(args.skill)
    if not p["probe"].exists():
        sys.stderr.write(f"no probe yet -- run: eval-fixture.py probe {args.skill}\n")
        return 1
    if not p["table"].exists():
        sys.stderr.write(f"missing table: {p['table'].relative_to(ROOT)}\n")
        return 1

    table = (yaml.safe_load(p["table"].read_text(encoding="utf-8")) or {}).get(
        args.side
    ) or {}
    probe = json.loads(p["probe"].read_text())
    doc = copy.deepcopy(probe)

    missing = []
    for task in doc["tasks"]:
        tid = task["test_id"]
        if tid not in table:
            missing.append(tid)
            continue
        run = task["runs"][0]
        run["final_output"] = table[tid]
        # Filled in so the record reads like a real run rather than a zero-cost
        # mock echo. Note no grader currently reads either field -- waza passes
        # only `output` to graders -- so the effective provenance defence is the
        # MOCK_MARKER check below, not these values.
        run["duration_ms"] = 1000
        run.setdefault("session_digest", {})["tool_call_count"] = 4
        if MOCK_MARKER in table[tid]:
            sys.stderr.write(f"table entry for {tid} contains the mock marker\n")
            return 1

    if missing:
        sys.stderr.write(f"table[{args.side}] missing entries: {missing}\n")
        return 1

    p[args.side].write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    print(f"{args.side} written: {p[args.side].relative_to(ROOT)}")
    return 0


def grade(skill: str, side: str) -> dict:
    p = paths(skill)
    proc = waza(
        "grade", str(p["eval"].relative_to(ROOT)), "--results", str(p[side])
    )
    # find() returns -1 when there is no JSON, and stdout[-1:] is the last
    # character rather than "" -- so the `if not blob` guard never fired and
    # waza's actual error message was replaced by a bare JSONDecodeError.
    start = proc.stdout.find("{")
    if start < 0:
        raise RuntimeError(
            f"waza grade produced no JSON (rc={proc.returncode}):\n"
            f"{proc.stdout}{proc.stderr}"
        )
    return json.loads(proc.stdout[start:]).get("tasks", {})


def cmd_validate(args: argparse.Namespace) -> int:
    if cmd_probe(args) != 0:
        return 1
    for side in ("right", "wrong"):
        args.side = side
        if cmd_fill(args) != 0:
            return 1

    results = {side: grade(args.skill, side) for side in ("right", "wrong")}
    ids = sorted(results["right"])
    if not ids:
        # Grading nothing is not a pass. A tool whose whole job is catching
        # assertions that survive wrong output must not survive zero output.
        sys.stderr.write("no tasks were graded -- nothing was validated\n")
        return 1
    print(f"\n{'task':40} {'right':>7} {'wrong':>7}  verdict")
    print("-" * 74)

    defects = []
    for tid in ids:
        r = bool(results["right"].get(tid, {}).get("passed"))
        w = bool(results["wrong"].get(tid, {}).get("passed"))
        if r and not w:
            verdict = "discriminates"
        elif not r:
            verdict = "DEFECT: correct output fails"
            defects.append(tid)
        else:
            verdict = "DEFECT: incorrect output passes"
            defects.append(tid)
        print(f"{tid[:38]:40} {'pass' if r else 'FAIL':>7} {'pass' if w else 'fail':>7}  {verdict}")

    print(f"\n{len(ids) - len(defects)}/{len(ids)} tasks discriminate")
    if defects:
        print("grader defects:", ", ".join(defects))
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_probe = sub.add_parser("probe", help="capture the output-JSON shape (mock)")
    p_probe.add_argument("skill")
    p_probe.set_defaults(func=cmd_probe)

    p_fill = sub.add_parser("fill", help="write one side's results JSON")
    p_fill.add_argument("skill")
    p_fill.add_argument("--side", choices=("right", "wrong"), required=True)
    p_fill.set_defaults(func=cmd_fill)

    p_val = sub.add_parser("validate", help="probe + fill both sides + grade + report")
    p_val.add_argument("skill")
    p_val.set_defaults(func=cmd_validate)
    return parser


if __name__ == "__main__":
    parsed = build_parser().parse_args()
    sys.exit(parsed.func(parsed))
