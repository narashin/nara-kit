"""Tests for check-layout.py — the design-vs-implementation layout diff.

Run: python3 -m pytest assets/runtime/test_check_layout.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_spec = importlib.util.spec_from_file_location("check_layout", Path(__file__).with_name("check-layout.py"))
assert _spec and _spec.loader
check_layout = importlib.util.module_from_spec(_spec)
sys.modules["check_layout"] = check_layout          # @dataclass resolves annotations via sys.modules
_spec.loader.exec_module(check_layout)


def contract(*sections: dict) -> dict:
    return {"version": 1, "label": "t", "url": "http://x", "sections": list(sections)}


def section(index: int, name: str, **kw) -> dict:
    return {
        "index": index,
        "name": name,
        "title": kw.get("title"),
        "tabs": kw.get("tabs", []),
        "tables": [{"columns": c} for c in kw.get("tables", [])],
        "fields": kw.get("fields", []),
        "rows": kw.get("rows", []),
        "actions": [{"text": t, "align": a} for t, a in kw.get("actions", [])],
    }


def write(tmp_path: Path, name: str, data: dict) -> str:
    p = tmp_path / name
    p.write_text(json.dumps(data), encoding="utf-8")
    return str(p)


TEAMS_DESIGN = contract(
    section(1, "add team button", actions=[("Add Team", "right")]),
    section(2, "team filter panel", fields=["Name", "Owner", "Opera", "LAI"],
            actions=[("Clear", "right"), ("Search", "right")]),
    section(3, "teams table", tables=[["Name", "Owner", "CI Type", "CI Name"]]),
)


def run(tmp_path: Path, design: dict, impl: dict) -> int:
    return check_layout.run(write(tmp_path, "d.json", design), write(tmp_path, "i.json", impl), 0.2)


def test_identical_layout_passes(tmp_path):
    assert run(tmp_path, TEAMS_DESIGN, TEAMS_DESIGN) == 0


def test_section_names_need_not_match(tmp_path):
    """The app has no data-studio-label, so its sections are named "section N" — content aligns them."""
    impl = contract(
        section(1, "section 1", actions=[("Add Team", "right")]),
        section(2, "section 2", fields=["Name", "Owner", "Opera", "LAI"],
                actions=[("Clear", "right"), ("Search", "right")]),
        section(3, "section 3", tables=[["Name", "Owner", "CI Type", "CI Name"]]),
    )
    assert run(tmp_path, TEAMS_DESIGN, impl) == 0


def test_reordered_columns_fail(tmp_path, capsys):
    impl = json.loads(json.dumps(TEAMS_DESIGN))
    impl["sections"][2]["tables"][0]["columns"] = ["Owner", "Name", "CI Type", "CI Name"]
    assert run(tmp_path, TEAMS_DESIGN, impl) == 1
    assert "reordered" in capsys.readouterr().out


def test_missing_column_fails(tmp_path, capsys):
    impl = json.loads(json.dumps(TEAMS_DESIGN))
    impl["sections"][2]["tables"][0]["columns"] = ["Name", "Owner", "CI Type"]
    assert run(tmp_path, TEAMS_DESIGN, impl) == 1
    assert "missing `CI Name`" in capsys.readouterr().out


def test_extra_column_fails(tmp_path, capsys):
    impl = json.loads(json.dumps(TEAMS_DESIGN))
    impl["sections"][2]["tables"][0]["columns"] = ["Name", "Owner", "CI Type", "CI Name", "Show"]
    assert run(tmp_path, TEAMS_DESIGN, impl) == 1
    assert "unexpected `Show`" in capsys.readouterr().out


def test_action_moved_to_the_other_side_fails(tmp_path, capsys):
    impl = json.loads(json.dumps(TEAMS_DESIGN))
    impl["sections"][0]["actions"][0]["align"] = "left"
    assert run(tmp_path, TEAMS_DESIGN, impl) == 1
    assert "design sits right, impl sits left" in capsys.readouterr().out


def test_missing_section_fails(tmp_path, capsys):
    impl = contract(TEAMS_DESIGN["sections"][0], TEAMS_DESIGN["sections"][2])
    assert run(tmp_path, TEAMS_DESIGN, impl) == 1
    assert "MISSING in the implementation" in capsys.readouterr().out


def test_extra_section_fails(tmp_path, capsys):
    impl = contract(*TEAMS_DESIGN["sections"], section(4, "promo banner", title="Try the new thing"))
    assert run(tmp_path, TEAMS_DESIGN, impl) == 1
    assert "NOT IN THE DESIGN" in capsys.readouterr().out


def test_reordered_sections_fail(tmp_path, capsys):
    s = TEAMS_DESIGN["sections"]
    impl = contract(
        {**json.loads(json.dumps(s[2])), "index": 1},
        {**json.loads(json.dumps(s[1])), "index": 2},
        {**json.loads(json.dumps(s[0])), "index": 3},
    )
    assert run(tmp_path, TEAMS_DESIGN, impl) == 1
    assert "different order" in capsys.readouterr().out


def test_case_and_whitespace_are_not_drift(tmp_path):
    impl = json.loads(json.dumps(TEAMS_DESIGN))
    impl["sections"][2]["tables"][0]["columns"] = ["name", "  Owner ", "CI Type", "CI Name"]
    assert run(tmp_path, TEAMS_DESIGN, impl) == 0


def test_truncation_ellipsis_is_not_drift(tmp_path):
    """The extractor truncates long text with an ellipsis; that must not read as a difference."""
    design = contract(section(1, "s", fields=["A very long field label that got…"]))
    impl = contract(section(1, "section 1", fields=["A very long field label that got"]))
    assert run(tmp_path, design, impl) == 0


def test_unknown_align_is_not_reported(tmp_path):
    """A contract captured from a hidden/zero-width container has align=None — not a finding."""
    impl = json.loads(json.dumps(TEAMS_DESIGN))
    impl["sections"][0]["actions"][0]["align"] = None
    assert run(tmp_path, TEAMS_DESIGN, impl) == 0


def test_rejects_non_contract_json(tmp_path):
    p = write(tmp_path, "bad.json", {"nope": 1})
    with pytest.raises(SystemExit):
        check_layout.load(p)
