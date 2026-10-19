"""
Scoring checks for single words and dollar amounts.

These guard against a bug where the word-boundary and digit regular expressions had doubled backslashes
(in a raw string, two backslashes plus "b" or "d"), so they matched a literal backslash instead. Every
single-word keyword rule and the amount check silently never fired, while multi-word phrases kept working.
"""

import unittest

from gatekeeper.criteria import _contains, score_authority, score_budget, score_need, score_timeline

GREEN, YELLOW, RED = 2, 1, 0


class WordBoundaryTests(unittest.TestCase):
    def test_single_word_matches_as_a_whole_word(self) -> None:
        self.assertTrue(_contains("no", "no"))
        self.assertTrue(_contains("we have no money", "no"))
        self.assertTrue(_contains("burnout is real", "burnout"))

    def test_single_word_does_not_match_inside_another_word(self) -> None:
        self.assertFalse(_contains("i know we have some", "no"))
        self.assertFalse(_contains("november maybe", "no"))
        self.assertFalse(_contains("yesterday we met", "yes"))

    def test_multi_word_phrases_still_match_as_text(self) -> None:
        self.assertTrue(_contains("we have budget allocated", "have budget"))


class BudgetTests(unittest.TestCase):
    def test_plain_yes_and_no(self) -> None:
        self.assertEqual(score_budget("yes"), GREEN)
        self.assertEqual(score_budget("no"), RED)
        self.assertEqual(score_budget("no budget"), RED)

    def test_dollar_amounts(self) -> None:
        self.assertEqual(score_budget("We have $5000 allocated"), GREEN)
        self.assertEqual(score_budget("$1,200 a year"), GREEN)
        self.assertEqual(score_budget("$500"), GREEN)
        self.assertEqual(score_budget("$100"), RED)
        self.assertEqual(score_budget("about 49.99"), RED)

    def test_unsure_answers_stay_yellow(self) -> None:
        self.assertEqual(score_budget("not sure, need approval"), YELLOW)
        self.assertEqual(score_budget("I know we have some"), YELLOW)
        self.assertEqual(score_budget("November maybe"), YELLOW)
        self.assertEqual(score_budget(""), YELLOW)


class OtherDimensionTests(unittest.TestCase):
    def test_need_words(self) -> None:
        self.assertEqual(score_need("burnout is killing retention"), GREEN)
        self.assertEqual(score_need("just looking"), YELLOW)
        self.assertEqual(score_need("therapy for my team"), RED)

    def test_authority_phrases(self) -> None:
        self.assertEqual(score_authority("I sign off on this"), GREEN)
        self.assertEqual(score_authority("just a student"), RED)

    def test_timeline_phrases(self) -> None:
        self.assertEqual(score_timeline("This quarter"), GREEN)
        self.assertEqual(score_timeline("no rush"), YELLOW)
        self.assertEqual(score_timeline("not this year"), RED)


if __name__ == "__main__":
    unittest.main()
