"""Tests for the auto-replace path and its safety net.

Auto-replace is the default because a human cannot count hundreds of claims.
That is only defensible if a corrupted CSV can never rewrite the document, and
if every write is recoverable. These tests pin both halves.
"""

import os
import shutil
import tempfile
import unittest

import audit

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")

def read_text(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def read_bytes(path):
    with open(path, "rb") as handle:
        return handle.read()



class SanityGateTest(unittest.TestCase):
    def test_normal_correction_passes(self):
        self.assertIsNone(audit.sanity_hold("5", 3))

    def test_collapse_to_near_zero_is_held(self):
        # a header-only or wrongly-filtered CSV shows up as a huge drop
        self.assertIsNotNone(audit.sanity_hold("175", 0))

    def test_ninety_percent_drop_is_held(self):
        self.assertIsNotNone(audit.sanity_hold("1000", 50))

    def test_tenfold_increase_is_held(self):
        self.assertIsNotNone(audit.sanity_hold("10", 100))

    def test_claimed_zero_with_nonzero_measurement_is_held(self):
        self.assertIsNotNone(audit.sanity_hold("0", 42))

    def test_small_absolute_numbers_are_not_held(self):
        # 2 -> 3 is a 50% move; small counts must stay correctable
        self.assertIsNone(audit.sanity_hold("2", 3))


class EmptyCsvTest(unittest.TestCase):
    def test_header_only_csv_is_mapping_failure_not_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "empty.csv"), "w", encoding="utf-8") as fh:
                fh.write("id,status\n")
            expr = audit.parse_expression("empty.csv | count rows where status=active")
            with self.assertRaises(audit.MappingFailure):
                audit.measure(expr, tmp)


class ApplyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.doc = os.path.join(self.tmp, "spec.md")
        shutil.copy(os.path.join(FIXTURES, "spec-sample.md"), self.doc)
        for name in ("users.csv", "latency.csv"):
            shutil.copy(os.path.join(FIXTURES, name), os.path.join(self.tmp, name))
        self.snapshots = os.path.join(self.tmp, "runs")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def apply(self, dry_run=False):
        return audit.apply_fixes(
            self.doc,
            self.tmp,
            self.snapshots,
            dry_run=dry_run,
            require_ignored=False,
        )

    def test_mismatch_is_replaced_without_per_item_approval(self):
        result = self.apply()
        self.assertEqual(result.replaced, 1)
        text = read_text(self.doc)
        self.assertIn("코어 팀원 3명", text)
        self.assertNotIn("코어 팀원 5명", text)

    def test_unmarked_numbers_untouched(self):
        self.apply()
        text = read_text(self.doc)
        self.assertIn("2026-07-08", text)  # date
        self.assertIn("예상 트래픽 5000 rpm", text)  # unmarked claim
        self.assertIn("## 1. 현황", text)  # heading number

    def test_matching_claims_are_left_alone(self):
        before = read_text(self.doc)
        self.apply()
        after = read_text(self.doc)
        self.assertEqual(before.count("활성 사용자 10명"), after.count("활성 사용자 10명"))

    def test_mapping_failure_never_written(self):
        self.apply()
        text = read_text(self.doc)
        self.assertIn("관리자 2명", text)  # unresolved marker keeps its value

    def test_snapshot_created_and_restores_original(self):
        original = read_bytes(self.doc)
        result = self.apply()
        self.assertTrue(os.path.isfile(result.snapshot))
        self.assertNotEqual(original, read_bytes(self.doc))
        shutil.copy(result.snapshot, self.doc)
        self.assertEqual(original, read_bytes(self.doc))

    def test_dry_run_writes_nothing(self):
        original = read_bytes(self.doc)
        result = self.apply(dry_run=True)
        self.assertEqual(original, read_bytes(self.doc))
        self.assertEqual(result.replaced, 1)  # still reports what it would do
        self.assertIsNone(result.snapshot)

    def test_intentional_marker_blocks_replacement(self):
        with open(self.doc, "a", encoding="utf-8") as fh:
            fh.write(
                "\n- 코어 팀원 9명 <!-- src: users.csv | count rows where team=core -->"
                " <!-- intentional: 1차 범위 -->\n"
            )
        result = self.apply()
        text = read_text(self.doc)
        self.assertIn("코어 팀원 9명", text)
        self.assertEqual(result.intentional, 1)

    def test_held_claim_is_not_written(self):
        # rewrite the CSV so the measurement collapses; the gate must stop it
        with open(os.path.join(self.tmp, "users.csv"), "w", encoding="utf-8") as fh:
            fh.write("id,name,status,team,score\n1,alice,inactive,ops,10\n")
        result = self.apply()
        text = read_text(self.doc)
        self.assertIn("활성 사용자 10명", text)  # 10 -> 0 would be a collapse
        self.assertGreaterEqual(result.held, 1)

    def test_refuses_when_snapshot_dir_is_tracked(self):
        with self.assertRaises(audit.UnsafeSnapshotDir):
            audit.apply_fixes(
                self.doc, self.tmp, self.snapshots, require_ignored=True
            )


if __name__ == "__main__":
    unittest.main()
