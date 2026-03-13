"""Pydantic models for the qualification API."""
from __future__ import annotations

from typing import Dict

from pydantic import BaseModel, Field


def _score_to_label(score: int) -> str:
    if score == 2:
        return "green"
    if score == 1:
        return "yellow"
    return "red"


class QualifyRequest(BaseModel):
    """BANT answers for a single lead."""

    need: str = Field(default="", description="What's driving the prospect to look")
    authority: str = Field(default="", description="Who signs off on the partnership")
    budget: str = Field(default="", description="Budget status or amount")
    timeline: str = Field(default="", description="When they want something in place")


class QualifyResponse(BaseModel):
    """Full qualification result with decision and explainability."""

    decision: str = Field(description="Outcome: book_ae, nurture, disqualify, or need_more_info")
    reason: str = Field(description="Machine-readable reason code")
    score: int = Field(description="Lead score 0-100")
    confidence_band: str = Field(description="low, medium, or high")
    scores_numeric: Dict[str, int] = Field(default_factory=dict, description="Per-dimension 0/1/2")
    scores_labels: Dict[str, str] = Field(default_factory=dict, description="Per-dimension green/yellow/red")
    message: str = Field(description="Human-readable next step or clarification prompt")
    lead_id: int | None = Field(default=None, description="Stored lead ID when persisted")


def build_qualify_response(
    outcome: str | None,
    reason: str,
    scores: Dict[str, int],
    message: str,
    lead_score: int,
    confidence_band: str,
    lead_id: int | None = None,
) -> QualifyResponse:
    """Build API response from engine result and computed metrics."""
    scores_labels = {k: _score_to_label(v) for k, v in scores.items()}
    return QualifyResponse(
        decision=outcome or "need_more_info",
        reason=reason,
        score=lead_score,
        confidence_band=confidence_band,
        scores_numeric=scores,
        scores_labels=scores_labels,
        message=message,
        lead_id=lead_id,
    )
