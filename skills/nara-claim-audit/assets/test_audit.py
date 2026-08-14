"""Unit tests for the claim-audit marker parser and CSV measurement.

Determinism is the point of this module: the same document + same CSVs must
produce byte-identical results, so every rule here is mechanical. Anything the
grammar does not cover is rejected loudly instead of guessed.
"""

import os
import unittest

import audit

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


class ParseExpressionTest(unittest.TestCase):
    def test_count_rows(self):
        expr = audit.parse_expression("users.csv | count rows")
        self.assertEqual(expr.source, "users.csv")
        self.assertEqual(expr.agg, "count")
        self.assertIsNone(expr.column)
        self.assertEqual(expr.filters, [])

    def test_distinct_column(self):
        expr = audit.parse_expression("users.csv | distinct team")
        self.assertEqual(expr.agg, "distinct")
        self.assertEqual(expr.column, "team")

    def test_single_filter(self):
        expr = audit.parse_expression("users.csv | count rows where status=active")
        self.assertEqual(expr.filters, [("status", "=", "active")])

    def test_multiple_filters_with_and(self):
        expr = audit.parse_expression(
            "users.csv | count rows where status=active and score>=50"
        )
        self.assertEqual(
            expr.filters, [("status", "=", "active"), ("score", ">=", "50")]
        )

    def test_unit_conversion_divide(self):
        expr = audit.parse_expression("latency.csv | avg response_ms / 1000")
        self.assertEqual(expr.agg, "avg")
        self.assertEqual(expr.divisor, 1000.0)

    def test_all_six_aggregates_accepted(self):
        for agg in ("count", "distinct", "sum", "avg", "max", "min"):
            target = "rows" if agg == "count" else "score"
            expr = audit.parse_expression("users.csv | %s %s" % (agg, target))
            self.assertEqual(expr.agg, agg)

    # --- rejection: the grammar must never guess ---

    def test_natural_language_rejected(self):
        with self.assertRaises(audit.SyntaxRejected):
            audit.parse_expression("users.csv (활성 사용자 수)")

    def test_join_rejected(self):
        with self.assertRaises(audit.SyntaxRejected):
            audit.parse_expression("users.csv | count rows join teams on id")

    def test_subquery_rejected(self):
        with self.assertRaises(audit.SyntaxRejected):
            audit.parse_expression(
                "users.csv | count rows where id in (select id from x)"
            )

    def test_or_filter_rejected(self):
        with self.assertRaises(audit.SyntaxRejected):
            audit.parse_expression(
                "users.csv | count rows where status=active or status=idle"
            )

    def test_unknown_aggregate_rejected(self):
        with self.assertRaises(audit.SyntaxRejected):
            audit.parse_expression("users.csv | median score")

    def test_missing_source_rejected(self):
        with self.assertRaises(audit.SyntaxRejected):
            audit.parse_expression("count rows")


class MeasureTest(unittest.TestCase):
    def measure(self, expression):
        return audit.measure(audit.parse_expression(expression), FIXTURES)

    def test_count_rows_with_filter(self):
        # fixture has 12 rows, 2 of them inactive (verified with awk)
        self.assertEqual(self.measure("users.csv | count rows where status=active"), 10)

    def test_distinct(self):
        self.assertEqual(self.measure("users.csv | distinct team"), 3)

    def test_sum(self):
        self.assertEqual(self.measure("users.csv | sum score"), 780)

    def test_avg_with_unit_conversion(self):
        self.assertEqual(self.measure("latency.csv | avg response_ms / 1000"), 2.0)

    def test_max_min(self):
        self.assertEqual(self.measure("users.csv | max score"), 120)
        self.assertEqual(self.measure("users.csv | min score"), 10)

    def test_numeric_comparison_is_numeric_not_lexical(self):
        # "9" > "100" lexically but not numerically; the filter must use numbers
        self.assertEqual(self.measure("users.csv | count rows where score>=100"), 3)

    def test_unknown_column_raises_mapping_failure(self):
        with self.assertRaises(audit.MappingFailure):
            self.measure("users.csv | count rows where role=admin")

    def test_missing_file_raises_mapping_failure(self):
        with self.assertRaises(audit.MappingFailure):
            self.measure("nope.csv | count rows")


class ExtractClaimsTest(unittest.TestCase):
    def setUp(self):
        self.doc = os.path.join(FIXTURES, "spec-sample.md")
        self.claims = audit.extract_claims(self.doc)

    def test_extracts_only_marked_numbers(self):
        # 7 markers exist in the fixture; unmarked numbers are not claims here
        self.assertEqual(len(self.claims), 7)

    def test_claim_value_is_number_before_marker(self):
        first = self.claims[0]
        self.assertEqual(first.value, "10")
        self.assertEqual(first.line, 7)

    def test_decimal_claim_value_preserved(self):
        avg = [c for c in self.claims if "latency" in c.expression][0]
        self.assertEqual(avg.value, "2.0")

    def test_unmarked_numbers_are_not_claims(self):
        for claim in self.claims:
            self.assertNotIn("5000", claim.value)


class AuditTest(unittest.TestCase):
    def setUp(self):
        self.report = audit.audit_document(
            os.path.join(FIXTURES, "spec-sample.md"), FIXTURES
        )
        self.by_verdict = {}
        for row in self.report.rows:
            self.by_verdict.setdefault(row.verdict, []).append(row)

    def test_each_verdict_present(self):
        self.assertEqual(len(self.by_verdict.get("match", [])), 4)
        self.assertEqual(len(self.by_verdict.get("mismatch", [])), 1)
        self.assertEqual(len(self.by_verdict.get("mapping_failure", [])), 1)
        self.assertEqual(len(self.by_verdict.get("syntax_error", [])), 1)

    def test_mismatch_carries_both_values(self):
        row = self.by_verdict["mismatch"][0]
        self.assertEqual(row.claimed, "5")
        self.assertEqual(row.measured, 3)

    def test_report_records_csv_mtime(self):
        self.assertTrue(self.report.sources)
        for meta in self.report.sources.values():
            self.assertIn("-", meta["mtime"])  # ISO-8601 date portion

    def test_document_is_not_modified(self):
        path = os.path.join(FIXTURES, "spec-sample.md")
        with open(path, "rb") as handle:
            before = handle.read()
        audit.audit_document(path, FIXTURES)
        with open(path, "rb") as handle:
            self.assertEqual(before, handle.read())

    def test_deterministic_across_runs(self):
        again = audit.audit_document(
            os.path.join(FIXTURES, "spec-sample.md"), FIXTURES
        )
        self.assertEqual(audit.render_text(self.report), audit.render_text(again))


if __name__ == "__main__":
    unittest.main()
