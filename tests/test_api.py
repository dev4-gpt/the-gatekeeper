"""API-level tests for the FastAPI qualification service."""
import unittest

from fastapi.testclient import TestClient

from api.app import app

client = TestClient(app)


class HealthTests(unittest.TestCase):
    def test_health_returns_200(self) -> None:
        resp = client.get("/health")
        self.assertEqual(resp.status_code, 200)

    def test_health_returns_ok(self) -> None:
        resp = client.get("/health")
        data = resp.json()
        self.assertEqual(data.get("status"), "ok")
        self.assertEqual(data.get("service"), "gatekeeper")


class QualifyTests(unittest.TestCase):
    def test_strong_fit_returns_book_ae(self) -> None:
        payload = {
            "need": "retention and burnout",
            "authority": "i sign off",
            "budget": "we have budget allocated",
            "timeline": "this quarter",
        }
        resp = client.post("/qualify", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["decision"], "book_ae")
        self.assertEqual(data["reason"], "strong_fit")
        self.assertIn("scores_labels", data)
        self.assertIsNotNone(data.get("lead_id"))

    def test_red_budget_returns_disqualify(self) -> None:
        payload = {
            "need": "retention",
            "authority": "i sign off",
            "budget": "no budget for this",
            "timeline": "this quarter",
        }
        resp = client.post("/qualify", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["decision"], "disqualify")
        self.assertEqual(data["reason"], "red_budget_or_authority_or_need")
        self.assertIn("scores_labels", data)

    def test_qualify_returns_score_and_confidence(self) -> None:
        payload = {
            "need": "retention",
            "authority": "i sign off",
            "budget": "we have budget allocated",
            "timeline": "this quarter",
        }
        resp = client.post("/qualify", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("score", data)
        self.assertIn("confidence_band", data)
        self.assertGreaterEqual(data["score"], 0)
        self.assertLessEqual(data["score"], 100)
