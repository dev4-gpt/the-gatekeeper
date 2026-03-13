import unittest

from gatekeeper.engine import run, OUTCOME_BOOK_AE, OUTCOME_DISQUALIFY, OUTCOME_NURTURE


class EngineTests(unittest.TestCase):
    def test_strong_fit_books_ae(self) -> None:
        answers = {
            "need": "retention and burnout",
            "authority": "i sign off",
            "budget": "we have budget allocated",
            "timeline": "this quarter",
        }
        result = run(answers)
        self.assertEqual(result["outcome"], OUTCOME_BOOK_AE)
        self.assertEqual(result["reason"], "strong_fit")

    def test_red_budget_disqualifies(self) -> None:
        answers = {
            "need": "retention",
            "authority": "i sign off",
            "budget": "no budget for this",
            "timeline": "this quarter",
        }
        result = run(answers)
        self.assertEqual(result["outcome"], OUTCOME_DISQUALIFY)
        self.assertEqual(result["reason"], "red_budget_or_authority_or_need")

    def test_not_sure_budget_is_yellow(self) -> None:
        answers = {
            "need": "retention",
            "authority": "i sign off",
            "budget": "not sure yet, would need approval",
            "timeline": "this quarter",
        }
        result = run(answers)
        self.assertEqual(result["outcome"], OUTCOME_NURTURE)
        self.assertEqual(result["reason"], "soft_fit")


if __name__ == "__main__":
    unittest.main()

