"""Regression tests for defects found in the 2026-08-14 code review.

Every case here was reproduced against the pre-fix implementation. They are kept
separate so the review's findings stay legible as a set.
"""

import os
import shutil
import tempfile
import unittest

import audit

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def read(path):
    with open(path, encoding="utf-8", newline="") as handle:
        return handle.read()


class ClaimSelectionTest(unittest.TestCase):
    """C1/S4: the claim was taken as the last number before the marker."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        shutil.copy(os.path.join(FIXTURES, "users.csv"), self.tmp)
        self.doc = os.path.join(self.tmp, "spec.md")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def audit_one(self, line):
        write(self.doc, line + "\n")
        return audit.audit_document(self.doc, self.tmp).rows[0]

    def test_trailing_parenthetical_is_not_replaced(self):
        row = self.audit_one(
            "- 활성 사용자 10명 (전체 50명 중) "
            "<!-- src: users.csv | count rows where status=active -->"
        )
        self.assertEqual(row.verdict, "ambiguous")

    def test_thousands_separator_is_not_mangled(self):
        row = self.audit_one(
            "- 월 1,200건 처리 <!-- src: users.csv | count rows -->"
        )
        self.assertEqual(row.verdict, "ambiguous")

    def test_single_number_line_still_audits(self):
        row = self.audit_one(
            "- 활성 사용자 10명 <!-- src: users.csv | count rows where status=active -->"
        )
        self.assertEqual(row.verdict, "match")

    def test_two_markers_on_one_line_both_audited(self):
        write(
            self.doc,
            "- A 3명 <!-- src: users.csv | count rows where team=core --> / "
            "B 4명 <!-- src: users.csv | count rows where team=platform -->\n",
        )
        rows = audit.audit_document(self.doc, self.tmp).rows
        self.assertEqual(len(rows), 2)
        self.assertEqual([r.verdict for r in rows], ["match", "mismatch"])


class CodeFenceTest(unittest.TestCase):
    """C3/S8: examples inside fenced blocks were rewritten."""

    def test_fenced_marker_is_not_a_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copy(os.path.join(FIXTURES, "users.csv"), tmp)
            doc = os.path.join(tmp, "spec.md")
            write(
                doc,
                "설명:\n\n```markdown\n활성 사용자 99명 "
                "<!-- src: users.csv | count rows where status=active -->\n```\n",
            )
            self.assertEqual(audit.audit_document(doc, tmp).rows, [])


class ZeroResultTest(unittest.TestCase):
    """C2/S3: count/distinct returned 0 for a filter that matched nothing."""

    def test_filter_typo_is_mapping_failure_not_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copy(os.path.join(FIXTURES, "users.csv"), tmp)
            expr = audit.parse_expression(
                "users.csv | count rows where status=churned"
            )
            with self.assertRaises(audit.MappingFailure):
                audit.measure(expr, tmp)

    def test_case_mismatch_is_mapping_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copy(os.path.join(FIXTURES, "users.csv"), tmp)
            expr = audit.parse_expression("users.csv | count rows where team=Core")
            with self.assertRaises(audit.MappingFailure):
                audit.measure(expr, tmp)


class ForbiddenWordTest(unittest.TestCase):
    """M2: substring matching rejected legitimate column names."""

    def test_column_containing_join_is_accepted(self):
        expr = audit.parse_expression("users.csv | count rows where joined_at>2026")
        self.assertEqual(expr.filters, [("joined_at", ">", "2026")])

    def test_column_named_selected_is_accepted(self):
        audit.parse_expression("users.csv | distinct selected")

    def test_union_id_column_is_accepted(self):
        audit.parse_expression("users.csv | distinct union_id")

    def test_actual_join_syntax_still_rejected(self):
        with self.assertRaises(audit.SyntaxRejected):
            audit.parse_expression("users.csv | count rows join teams on id")


class ScaleParsingTest(unittest.TestCase):
    """M5: unit-conversion split ate slashes inside filter values."""

    def test_date_filter_value_is_preserved(self):
        expr = audit.parse_expression("users.csv | count rows where day=2026/01/02")
        self.assertEqual(expr.filters, [("day", "=", "2026/01/02")])
        self.assertIsNone(expr.divisor)

    def test_spaced_conversion_still_parsed(self):
        expr = audit.parse_expression("latency.csv | avg response_ms / 1000")
        self.assertEqual(expr.divisor, 1000.0)


class MixedComparisonTest(unittest.TestCase):
    """M3: numeric vs lexical comparison was decided per row."""

    def test_thousands_separated_cell_raises_instead_of_undercounting(self):
        with tempfile.TemporaryDirectory() as tmp:
            # quoted, otherwise the comma would split into a second CSV field
            write(os.path.join(tmp, "amt.csv"), 'amount\n100\n"1,200"\n80\n')
            expr = audit.parse_expression("amt.csv | count rows where amount>50")
            with self.assertRaises(audit.MappingFailure):
                audit.measure(expr, tmp)

    def test_ragged_row_does_not_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            write(os.path.join(tmp, "short.csv"), "id,status,score\n2,active\n1,a,5\n")
            expr = audit.parse_expression("short.csv | count rows where score>1")
            self.assertEqual(audit.measure(expr, tmp), 1)


class SanityGateTest(unittest.TestCase):
    """S2/S3: truncated exports and fractional values slipped through."""

    def test_truncated_export_is_held(self):
        self.assertIsNotNone(audit.sanity_hold("5000", 1000))

    def test_partial_collapse_is_held(self):
        self.assertIsNotNone(audit.sanity_hold("175", 18))
        self.assertIsNotNone(audit.sanity_hold("12", 2))

    def test_fractional_collapse_is_held(self):
        self.assertIsNotNone(audit.sanity_hold("0.5", 0.02))

    def test_zero_measurement_is_never_written(self):
        self.assertIsNotNone(audit.sanity_hold("9", 0))

    def test_ordinary_correction_still_allowed(self):
        self.assertIsNone(audit.sanity_hold("12", 10))
        self.assertIsNone(audit.sanity_hold("2", 3))


class SnapshotTest(unittest.TestCase):
    """C4/S1: a second run overwrote the only recovery copy."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.doc = os.path.join(self.tmp, "spec.md")
        shutil.copy(os.path.join(FIXTURES, "spec-sample.md"), self.doc)
        for name in ("users.csv", "latency.csv"):
            shutil.copy(os.path.join(FIXTURES, name), os.path.join(self.tmp, name))
        self.snapshots = os.path.join(self.tmp, "runs")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_each_run_gets_its_own_snapshot(self):
        original = read(self.doc)
        first = audit.apply_fixes(
            self.doc, self.tmp, self.snapshots, require_ignored=False
        )
        self.assertEqual(read(first.snapshot), original)
        # a second run must not overwrite the first snapshot
        write(os.path.join(self.tmp, "users.csv"), "id,name,status,team,score\n1,a,active,core,1\n2,b,active,core,2\n3,c,active,core,3\n4,d,active,ops,4\n")
        audit.apply_fixes(self.doc, self.tmp, self.snapshots, require_ignored=False)
        self.assertEqual(read(first.snapshot), original)

    def test_snapshot_path_is_absolute(self):
        result = audit.apply_fixes(
            self.doc, self.tmp, self.snapshots, require_ignored=False
        )
        self.assertTrue(os.path.isabs(result.snapshot))


class LineEndingTest(unittest.TestCase):
    """m4: CRLF documents were rewritten wholesale as LF."""

    def test_crlf_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copy(os.path.join(FIXTURES, "users.csv"), tmp)
            doc = os.path.join(tmp, "spec.md")
            write(
                doc,
                "# spec\r\n- 코어 팀원 5명 "
                "<!-- src: users.csv | count rows where team=core -->\r\n",
            )
            audit.apply_fixes(doc, tmp, os.path.join(tmp, "runs"), require_ignored=False)
            body = read(doc)
            self.assertIn("코어 팀원 3명", body)
            self.assertNotIn("\n\n", body)
            self.assertEqual(body.count("\r\n"), 2)


if __name__ == "__main__":
    unittest.main()
