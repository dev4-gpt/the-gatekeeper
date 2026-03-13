"""FastAPI service for the Gatekeeper qualification engine."""
from __future__ import annotations

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from gatekeeper.engine import compute_lead_score, run as engine_run
from gatekeeper.storage import init_db, save_lead

from .schemas import QualifyRequest, QualifyResponse, build_qualify_response

app = FastAPI(
    title="Gatekeeper Qualification API",
    description="BANT lead qualification service. POST BANT answers to get a decision, score, and next step.",
    version="0.1.0",
)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    """Service readiness check."""
    return {"status": "ok", "service": "gatekeeper"}


@app.post("/qualify", response_model=QualifyResponse)
def qualify(request: QualifyRequest) -> QualifyResponse:
    """
    Qualify a lead from BANT answers.

    Returns decision (book_ae, nurture, disqualify), lead score, confidence band,
    and per-dimension scores. Persists the lead when a final outcome is reached.
    """
    answers = {
        "need": request.need,
        "authority": request.authority,
        "budget": request.budget,
        "timeline": request.timeline,
    }

    result = engine_run(answers)
    scores = result.get("scores", {})
    lead_score, confidence_band = compute_lead_score(scores)
    action = result.get("action", "")
    outcome = result.get("outcome")
    reason = result.get("reason", "")
    message = result.get("message", "")

    lead_id: int | None = None

    if action == "done" and outcome:
        lead_id = save_lead(
            answers=answers,
            scores=scores,
            outcome=outcome,
            reason=reason,
            lead_score=lead_score,
            confidence_band=confidence_band,
        )

    return build_qualify_response(
        outcome=outcome,
        reason=reason,
        scores=scores,
        message=message,
        lead_score=lead_score,
        confidence_band=confidence_band,
        lead_id=lead_id,
    )
