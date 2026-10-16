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

    tools/eval-fixture.py generate nara-gap --task basic-usage-001
    tools/eval-fixture.py validate nara-gap --right-from gen

`generate` is the one path to a REAL model output without a Copilot seat: it runs
`claude -p` hermetically (no settings, no MCP, no tools) with the skill body plus
its references appended to the system prompt, and the task prompt plus inlined
fixtures on stdin. Because tools are off, a skill that must call git or gh only
narrates what it would do -- so this is a source of real text for grader
validation, not a skill benchmark. A skill whose first step scans the codebase
often does not narrate but emits a pseudo tool call (`<invoke name=...>`) and
stops; generate rejects that output instead of saving it as a run. Each generation bills the headless quota.
Outputs land in results/<skill>-gen/<task>.json (gitignored) and `--right-from gen`
lets validate use them in place of the hand-written `right` entries.

Three limits to keep in mind. Settings are skipped, so the model is the CLI's
built-in default unless `--model` pins one (the record stores what answered).
Only the skill's own `references/*.md` are appended: sibling links into another
skill and nested reference dirs are not followed. And a generation outlives the
SKILL.md it came from; `--right-from gen` warns when the two have drifted.
"""

import argparse
import copy
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")

ROOT = pathlib.Path(__file__).resolve().parent.parent
MOCK_MARKER = "Mock response for:"
GEN_TIMEOUT = int(os.environ.get("BENCH_GEN_TIMEOUT", "300"))
FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.S)


def paths(skill: str) -> dict:
    base = ROOT / "evals" / skill
    return {
        "eval": base / "eval.yaml",
        "table": base / "validation.yaml",
        "tasks": base / "tasks",
        "fixtures": base / "fixtures",
        "skill_dir": ROOT / "skills" / skill,
        "probe": ROOT / "results" / f"{skill}-probe.json",
        "right": ROOT / "results" / f"{skill}-right.json",
        "wrong": ROOT / "results" / f"{skill}-wrong.json",
        "gen": ROOT / "results" / f"{skill}-gen",
    }


def skill_system_prompt(skill: str) -> str:
    """SKILL.md body (frontmatter stripped) followed by every references/*.md.

    References are concatenated because the hermetic run has no Read tool; a
    SKILL.md that loads them at runtime would otherwise run without them.
    """
    d = paths(skill)["skill_dir"]
    body = FRONTMATTER.sub("", (d / "SKILL.md").read_text(encoding="utf-8"), count=1)
    parts = [body.strip()]
    for ref in sorted((d / "references").glob("*.md")) if (d / "references").is_dir() else []:
        parts.append(f"\n\n# references/{ref.name}\n\n{ref.read_text(encoding='utf-8').strip()}")
    return "".join(parts)


def load_tasks(skill: str) -> dict:
    out = {}
    for f in sorted(paths(skill)["tasks"].glob("*.yaml")):
        t = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        if "id" in t:
            out[t["id"]] = t
    return out


def task_user_prompt(skill: str, task: dict) -> str:
    """The task prompt with each declared fixture inlined after it."""
    p = paths(skill)
    parts = [task["inputs"]["prompt"]]
    for entry in task.get("inputs", {}).get("files") or []:
        rel = entry["path"] if isinstance(entry, dict) else str(entry)
        fx = p["fixtures"] / rel
        if not fx.exists():
            raise FileNotFoundError(f"fixture missing: {fx.relative_to(ROOT)}")
        parts.append(f"\n\n--- {rel} ---\n{fx.read_text(encoding='utf-8').strip()}")
    return "".join(parts)


def generate_one(system_prompt: str, user_prompt: str, model: "str | None" = None) -> dict:
    """One hermetic `claude -p` run. Returns the parsed --output-format json.

    Settings are skipped, so the model is the CLI's built-in default unless
    `model` pins one; the record stores whichever model actually answered.
    """
    cmd = [
        "claude", "-p",
        "--setting-sources", "",
        "--strict-mcp-config",
        "--tools", "",
        "--permission-mode", "dontAsk",
        "--output-format", "json",
        "--append-system-prompt", system_prompt,
    ]
    if model:
        cmd += ["--model", model]
    with tempfile.TemporaryDirectory(prefix="nara-gen-") as scratch:
        proc = subprocess.run(
            cmd, input=user_prompt, capture_output=True, text=True,
            timeout=GEN_TIMEOUT, cwd=scratch,
        )
    if proc.returncode != 0:
        raise RuntimeError(f"claude -p failed (rc={proc.returncode}): {proc.stderr.strip()[:400]}")
    start = proc.stdout.find("{")
    if start < 0:
        raise RuntimeError(f"claude -p produced no JSON:\n{proc.stdout[:400]}")
    return json.loads(proc.stdout[start:])


def cmd_generate(args: argparse.Namespace) -> int:
    p = paths(args.skill)
    tasks = load_tasks(args.skill)
    wanted = args.task or sorted(tasks)
    unknown = [t for t in wanted if t not in tasks]
    if unknown:
        sys.stderr.write(f"unknown task ids: {unknown}\n")
        return 1
    system_prompt = skill_system_prompt(args.skill)
    p["gen"].mkdir(parents=True, exist_ok=True)
    print(f"system prompt: {len(system_prompt)} chars (SKILL.md + references)")
    print(f"{'task':40} {'chars':>6} {'turns':>5} {'usd':>7}  file")
    print("-" * 80)
    for tid in wanted:
        res = generate_one(system_prompt, task_user_prompt(args.skill, tasks[tid]), args.model)
        text = res.get("result", "")
        if not isinstance(text, str) or not text.strip():
            sys.stderr.write(f"{tid}: empty result (is_error={res.get('is_error')})\n")
            return 1
        if is_pseudo_tool_call(text):
            sys.stderr.write(
                f"{tid}: output is a pseudo tool call, not an answer -- tools are off "
                "here, so this skill cannot be generated by this command. Not saved. "
                "Write its right side from a fresh tool-enabled subagent run into "
                "validation.yaml instead (see the header of "
                "evals/nara-ac-draft/validation.yaml).\n"
            )
            return 1
        record = {
            "task": tid,
            "output": text,
            # Lets `--right-from gen` notice when the skill changed after generation.
            "system_prompt_sha": prompt_sha(system_prompt),
            "model": (res.get("modelUsage") and next(iter(res["modelUsage"]), None)),
            "num_turns": res.get("num_turns"),
            "total_cost_usd": res.get("total_cost_usd"),
            "duration_ms": res.get("duration_ms"),
            "session_id": res.get("session_id"),
        }
        out = p["gen"] / f"{tid}.json"
        out.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        cost = record["total_cost_usd"]
        print(f"{tid[:38]:40} {len(text):>6} {str(record['num_turns']):>5} "
              f"{cost if cost is None else f'{cost:.4f}':>7}  {out.relative_to(ROOT)}")
    return 0


def prompt_sha(system_prompt: str) -> str:
    return hashlib.sha256(system_prompt.encode("utf-8")).hexdigest()[:12]


def generated_outputs(skill: str) -> dict:
    """Generations on disk. Warns per task when the skill changed since then:
    results/ persists across runs, and validating against text the current
    skill never produced is the same stale-fixture trap the probe unlink guards."""
    d = paths(skill)["gen"]
    if not d.is_dir():
        return {}
    current = prompt_sha(skill_system_prompt(skill))
    out = {}
    for f in sorted(d.glob("*.json")):
        rec = json.loads(f.read_text(encoding="utf-8"))
        if rec.get("system_prompt_sha") != current:
            sys.stderr.write(
                f"warning: {f.relative_to(ROOT)} was generated from a different "
                f"SKILL.md/references ({rec.get('system_prompt_sha')} != {current}); regenerate\n"
            )
        out[rec["task"]] = rec["output"]
    return out


def waza(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["waza", *args], cwd=ROOT, capture_output=True, text=True)


def probe_errors(tasks: list) -> list:
    """(task id, message) for every probe run the engine itself failed.

    A mock run fails tasks on purpose (the real_run gate) with status `failed`;
    that is expected. Status `error` or an `error_msg` means the engine never
    produced output -- `executor: copilot-sdk` without a seat ends this way with
    "Failed to list models" or "No model available. Check policy enablement..."
    (both observed) -- and every task then grades empty text. validate
    used to report that as "DEFECT: correct output fails" on every task, which
    blames the assertions for an engine failure.
    """
    out = []
    for t in tasks:
        for run in t.get("runs") or []:
            msg = run.get("error_msg")
            if run.get("status") == "error" or msg:
                out.append((t.get("test_id", "?"), msg or "status: error"))
                break
    return out


PSEUDO_TOOL_CALL = re.compile(r"<(invoke|function_calls)\b")


def is_pseudo_tool_call(text: str) -> bool:
    """True when a tools-off generation emitted a tool call instead of an answer."""
    return PSEUDO_TOOL_CALL.search(text) is not None


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
    errors = probe_errors(tasks)
    if errors:
        # Remove the probe so a later `fill` cannot pick it up as input: the
        # existence check in cmd_fill would otherwise accept a run that graded
        # empty output on every task.
        p["probe"].unlink(missing_ok=True)
        tid, msg = errors[0]
        sys.stderr.write(
            f"probe engine failed on {len(errors)}/{len(tasks)} task(s), first {tid}: {msg}\n"
            "graders would see empty output. copilot-sdk has no seat in this repo, so "
            "do not chase the engine's settings advice; set `executor: mock` in "
            f"{p['eval'].relative_to(ROOT)} (config.model stays required).\n"
        )
        return 1
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
    probe = json.loads(p["probe"].read_text())
    # cmd_probe now deletes an engine-failed probe, but a file left by an older
    # run of this tool still exists on disk; existence alone is not validity.
    errors = probe_errors(probe.get("tasks") or [])
    if errors:
        sys.stderr.write(
            f"probe has {len(errors)} engine-failed task(s), first {errors[0][0]}: "
            f"{errors[0][1]} -- re-run: eval-fixture.py probe {args.skill}\n"
        )
        return 1

    table = (yaml.safe_load(p["table"].read_text(encoding="utf-8")) or {}).get(
        args.side
    ) or {}
    if args.side == "right" and getattr(args, "right_from", "table") == "gen":
        # Real model outputs override the hand-written entries where they exist;
        # tasks without a generation fall back to the table.
        gen = generated_outputs(args.skill)
        if not gen:
            sys.stderr.write(f"no generations yet -- run: eval-fixture.py generate {args.skill}\n")
            return 1
        table = {**table, **gen}
        print(f"right side: {len(gen)} task(s) from results/{args.skill}-gen, "
              f"{len(table) - len(gen)} from table")
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
    p_fill.add_argument("--right-from", choices=("table", "gen"), default="table",
                        help="right side source: validation.yaml or results/<skill>-gen")
    p_fill.set_defaults(func=cmd_fill)

    p_val = sub.add_parser("validate", help="probe + fill both sides + grade + report")
    p_val.add_argument("skill")
    p_val.add_argument("--right-from", choices=("table", "gen"), default="table",
                       help="right side source: validation.yaml or results/<skill>-gen")
    p_val.set_defaults(func=cmd_validate)

    p_gen = sub.add_parser("generate", help="real output via hermetic `claude -p` (bills quota)")
    p_gen.add_argument("skill")
    p_gen.add_argument("--task", action="append", help="task id; repeatable; default all")
    p_gen.add_argument("--model", help="pin a model; default is the CLI built-in (settings are skipped)")
    p_gen.set_defaults(func=cmd_generate)
    return parser


if __name__ == "__main__":
    parsed = build_parser().parse_args()
    sys.exit(parsed.func(parsed))
