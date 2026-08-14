"""Tests for the bootstrap path: finding claim candidates in unmarked documents.

Existing specs have no markers, so this path proposes where to put them. Its
only job is to shrink a document's numbers down to the handful that are actually
claims — measured on a real spec, roughly 70-80% of numeric tokens are dates,
heading numbers and list ordinals. It proposes; it never judges or replaces.
"""

import os
import unittest

import audit

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


class NoiseFilterTest(unittest.TestCase):
    def setUp(self):
        self.candidates = audit.extract_candidates(
            os.path.join(FIXTURES, "noisy-spec.md")
        )
        self.values = [c.value for c in self.candidates]

    def test_dates_excluded(self):
        for token in ("2026", "07", "08", "02"):
            self.assertNotIn(token, self.values)

    def test_heading_numbers_excluded(self):
        # "## 3. 분석" must not offer 3 as a claim
        for candidate in self.candidates:
            self.assertFalse(candidate.text.strip().startswith("#"))

    def test_ordered_list_ordinals_excluded(self):
        for candidate in self.candidates:
            self.assertNotIn("절차 스텝", candidate.text)

    def test_section_references_excluded(self):
        for candidate in self.candidates:
            self.assertNotIn("§", candidate.text)

    def test_code_block_contents_excluded(self):
        for candidate in self.candidates:
            self.assertNotIn("timeout_seconds", candidate.text)

    def test_version_and_path_numbers_excluded(self):
        for candidate in self.candidates:
            self.assertNotIn("v1.2.3", candidate.text)

    def test_already_marked_numbers_excluded(self):
        for candidate in self.candidates:
            self.assertNotIn("src:", candidate.text)

    def test_real_claims_are_kept(self):
        # counts, percentages and plain quantities in prose survive the filter
        self.assertIn("175", self.values)
        self.assertIn("44", self.values)
        self.assertIn("12", self.values)

    def test_candidate_count_is_small(self):
        # the fixture holds 3 real claims among ~20 numeric tokens
        self.assertLessEqual(len(self.candidates), 6)


class FactCardTest(unittest.TestCase):
    def setUp(self):
        self.cards = audit.fact_cards(FIXTURES)

    def test_card_per_csv(self):
        self.assertIn("users.csv", self.cards)
        self.assertIn("latency.csv", self.cards)

    def test_card_reports_row_count(self):
        self.assertEqual(self.cards["users.csv"]["rows"], 12)

    def test_card_reports_distinct_per_column(self):
        self.assertEqual(self.cards["users.csv"]["distinct"]["team"], 3)

    def test_card_skips_unreadable_csv(self):
        # a directory with no csv yields an empty mapping, not an exception
        self.assertEqual(audit.fact_cards(os.path.dirname(FIXTURES)), {})


class SuggestTest(unittest.TestCase):
    def test_matching_fact_is_offered_as_candidate_source(self):
        cards = audit.fact_cards(FIXTURES)
        hits = audit.suggest_sources("12", cards)
        self.assertTrue(any(h[0] == "users.csv" for h in hits))

    def test_no_false_certainty_for_unknown_number(self):
        cards = audit.fact_cards(FIXTURES)
        self.assertEqual(audit.suggest_sources("99999", cards), [])


if __name__ == "__main__":
    unittest.main()
