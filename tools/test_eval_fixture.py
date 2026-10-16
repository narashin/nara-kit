#!/usr/bin/env python3
"""Regression tests for tools/eval-fixture.py guards (stdlib unittest).

Each case reproduces a failure seen on 2026-10-16 while validating nara-ac-draft:
a probe whose engine errored was graded as "correct output fails" on every task,
and a tools-off generation saved a pseudo tool call as if it were a run.
Run: python3 -I tools/test_eval_fixture.py
"""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("eval_fixture", ROOT / "tools" / "eval-fixture.py")
if _spec is None or _spec.loader is None:
    raise ImportError("cannot load eval-fixture.py")
ef = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ef)


def task(tid: str, **run: object) -> dict:
    return {"test_id": tid, "runs": [{"run_number": 1, **run}]}


class ProbeErrors(unittest.TestCase):
    def test_mock_failures_are_expected(self) -> None:
        # The real_run gate fails every mock task by design; that is not an engine error.
        tasks = [task("a", status="failed", error_msg=None), task("b", status="failed")]
        self.assertEqual(ef.probe_errors(tasks), [])

    def test_engine_error_is_reported(self) -> None:
        tasks = [
            task("a", status="failed"),
            task("b", status="error", error_msg="session error: Execution failed: Error: Failed to list models"),
        ]
        self.assertEqual(ef.probe_errors(tasks), [("b", "session error: Execution failed: Error: Failed to list models")])

    def test_error_status_without_message(self) -> None:
        self.assertEqual(ef.probe_errors([task("a", status="error")]), [("a", "status: error")])


class PseudoToolCall(unittest.TestCase):
    def test_invoke_block_is_rejected(self) -> None:
        text = '먼저 확인합니다.\n\n<invoke name="Glob">\n<parameter name="pattern">docs/**/*.md</parameter>\n</invoke>'
        self.assertTrue(ef.is_pseudo_tool_call(text))

    def test_answer_mentioning_tools_passes(self) -> None:
        text = "코드 scan 결과 `[NOT FOUND]`. Glob·Grep 도구로 찾을 대상이 없었습니다. invoke 단계는 없습니다."
        self.assertFalse(ef.is_pseudo_tool_call(text))


class CommandTestCase(unittest.TestCase):
    """Runs a cmd_* function against a temp ROOT instead of the repo.

    The guards above are pure helpers; these cases drive the commands that call
    them, because a helper can be correct while its caller ignores the result.
    ROOT is patched too: the commands print paths relative to it.
    """

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="eval-fixture-test-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        results = self.root / "results"
        results.mkdir()
        base = self.root / "evals" / "demo"
        base.mkdir(parents=True)
        self.p = {
            "eval": base / "eval.yaml",
            "table": base / "validation.yaml",
            "tasks": base / "tasks",
            "fixtures": base / "fixtures",
            "skill_dir": self.root / "skills" / "demo",
            "probe": results / "demo-probe.json",
            "right": results / "demo-right.json",
            "wrong": results / "demo-wrong.json",
            "gen": results / "demo-gen",
        }
        for patcher in (
            mock.patch.object(ef, "ROOT", self.root),
            mock.patch.object(ef, "paths", lambda skill: self.p),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

    def run_cmd(self, fn, args: argparse.Namespace) -> "tuple[int, str]":
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            rc = fn(args)
        return rc, err.getvalue()

    def write_probe_via_waza(self, **run: object):
        """A `waza` stand-in that writes a one-task probe to the --output path."""
        def fake_waza(*argv: str):
            out = Path(argv[argv.index("--output") + 1])
            out.write_text(json.dumps({"tasks": [task("t1", **run)]}), encoding="utf-8")
            return mock.Mock(returncode=1, stdout="", stderr="")
        return fake_waza


class CmdProbe(CommandTestCase):
    def test_engine_failed_probe_is_removed(self) -> None:
        # Left on disk, this file was the input of the next `fill`.
        fake = self.write_probe_via_waza(status="error", error_msg="Failed to list models")
        with mock.patch.object(ef, "waza", fake):
            rc, err = self.run_cmd(ef.cmd_probe, argparse.Namespace(skill="demo"))
        self.assertEqual(rc, 1)
        self.assertFalse(self.p["probe"].exists())
        self.assertIn("probe engine failed", err)
        self.assertIn("Failed to list models", err)

    def test_mock_failed_probe_is_kept(self) -> None:
        # Control: the real_run gate failing a mock task is the expected shape.
        fake = self.write_probe_via_waza(status="failed", error_msg=None)
        with mock.patch.object(ef, "waza", fake):
            rc, err = self.run_cmd(ef.cmd_probe, argparse.Namespace(skill="demo"))
        self.assertEqual(rc, 0, err)
        self.assertTrue(self.p["probe"].exists())


class CmdFill(CommandTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.p["table"].write_text("right:\n  t1: ok\nwrong:\n  t1: bad\n", encoding="utf-8")

    def write_probe(self, **run: object) -> None:
        self.p["probe"].write_text(json.dumps({"tasks": [task("t1", **run)]}), encoding="utf-8")

    def test_errored_probe_left_by_older_run_is_refused(self) -> None:
        self.write_probe(status="error", error_msg="Failed to list models")
        rc, err = self.run_cmd(ef.cmd_fill, argparse.Namespace(skill="demo", side="right"))
        self.assertEqual(rc, 1)
        self.assertFalse(self.p["right"].exists())
        self.assertIn("engine-failed", err)

    def test_mock_probe_is_filled(self) -> None:
        # Control: same table, a probe the engine actually ran.
        self.write_probe(status="failed", final_output="Mock response for: x")
        rc, err = self.run_cmd(ef.cmd_fill, argparse.Namespace(skill="demo", side="right"))
        self.assertEqual(rc, 0, err)
        doc = json.loads(self.p["right"].read_text(encoding="utf-8"))
        self.assertEqual(doc["tasks"][0]["runs"][0]["final_output"], "ok")


class CmdGenerate(CommandTestCase):
    def generate(self, result_text: str) -> "tuple[int, str]":
        tasks = {"t1": {"id": "t1", "inputs": {"prompt": "p"}}}
        with mock.patch.object(ef, "load_tasks", lambda skill: tasks), \
                mock.patch.object(ef, "skill_system_prompt", lambda skill: "system"), \
                mock.patch.object(ef, "task_user_prompt", lambda skill, t: "user"), \
                mock.patch.object(ef, "generate_one", lambda *a: {"result": result_text, "total_cost_usd": 0.01}):
            return self.run_cmd(
                ef.cmd_generate, argparse.Namespace(skill="demo", task=None, model=None)
            )

    def test_pseudo_tool_call_is_not_saved(self) -> None:
        rc, err = self.generate('<invoke name="Glob">\n<parameter name="pattern">**</parameter>\n</invoke>')
        self.assertEqual(rc, 1)
        self.assertFalse((self.p["gen"] / "t1.json").exists())
        self.assertIn("pseudo tool call", err)

    def test_answer_is_saved(self) -> None:
        rc, err = self.generate("Score: 80/100. 근거는 아래 표와 같습니다.")
        self.assertEqual(rc, 0, err)
        rec = json.loads((self.p["gen"] / "t1.json").read_text(encoding="utf-8"))
        self.assertEqual(rec["output"], "Score: 80/100. 근거는 아래 표와 같습니다.")


if __name__ == "__main__":
    unittest.main()
