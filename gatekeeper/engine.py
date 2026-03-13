"""
Qualification engine: given BANT answers, returns outcome and next action.
No I/O—just state in, state out. Matches docs/02-logic-tree and 03-human-escalation-rules.
"""
from __future__ import annotations

import os
from typing import Dict, TypedDict

from . import criteria

HAS_LLM = bool(os.environ.get("GOOGLE_API_KEY"))

# outcome after we have enough info
OUTCOME_BOOK_AE = "book_ae"
OUTCOME_NURTURE = "nurture"
OUTCOME_DISQUALIFY = "disqualify"

# what the agent should do next
ACTION_ASK = "ask"
ACTION_ESCALATE = "escalate"
ACTION_DONE = "done"


class EngineResult(TypedDict):
    outcome: str | None  # book_ae | nurture | disqualify when decided
    action: str  # ask | escalate | done
    next_question: str | None  # key into criteria.QUESTIONS
    follow_up: bool  # true = use second question for that dimension
    message: str  # what to show the prospect (or internal note)
    scores: Dict[str, int]  # per-dimension scores so callers can explain decisions
    reason: str  # short machine-readable reason code (e.g. red_budget, strong_fit, soft_fit, escalation_requested)


def _scores(answers: dict[str, str]) -> dict[str, int]:
    # First pass: rules
    rule_scores: Dict[str, int] = {}
    for dim, ans in answers.items():
        if dim in criteria.SCORERS and ans:
            rule_scores[dim] = criteria.SCORERS[dim](ans)

    if not HAS_LLM:
        return rule_scores

    # Count how many dimensions are yellow or red (0 or 1)
    uncertain_dims = sum(1 for v in rule_scores.values() if v in (0, 1))
    if uncertain_dims < 2:
        # Rules are confident enough; skip LLM
        return rule_scores

    # Fall back to Gemini when at least 2 dimensions are uncertain
    try:
        from .llm_classifier import classify_bant_with_gemini

        return classify_bant_with_gemini(answers)
    except Exception:
        # On any LLM error, stay with rule-based scores
        return rule_scores
        

def compute_lead_score(scores: Dict[str, int]) -> tuple[int, str]:
    """
    Turn BANT scores into a 0–100 lead score and a coarse confidence band.

    scores: mapping of dimension -> 0 (red), 1 (yellow), 2 (green)
    """
    need = scores.get("need", 1)
    authority = scores.get("authority", 1)
    budget = scores.get("budget", 1)
    timeline = scores.get("timeline", 1)

    # weights sum to 1.0
    w_need = 0.35
    w_authority = 0.30
    w_budget = 0.20
    w_timeline = 0.15

    raw = (
        need * w_need
        + authority * w_authority
        + budget * w_budget
        + timeline * w_timeline
    )  # 0–2 range

    score = int(round((raw / 2.0) * 100))
    if score <= 40:
        band = "low"
    elif score <= 70:
        band = "medium"
    else:
        band = "high"

    return score, band


def run(answers: dict[str, str], escalation_requested: bool = False) -> EngineResult:
    """
    answers: dict of dimension -> raw answer string (e.g. {"need": "burnout and retention", "authority": "i sign off"})
    escalation_requested: prospect asked to talk to a human.
    """
    if escalation_requested:
        return EngineResult(
            outcome=None,
            action=ACTION_ESCALATE,
            next_question=None,
            follow_up=False,
            message="Prospect asked for a human. Escalate with context.",
            scores={},
            reason="escalation_requested",
        )

    scores = _scores(answers)
    missing = [d for d in criteria.BANT_ORDER if d not in scores or not (answers.get(d) or "").strip()]

    if missing:
        # ask first missing dimension; use follow-up only if we already have an answer for it that was vague
        next_dim = missing[0]
        prev_ans = answers.get(next_dim, "").strip()
        follow_up = False
        # if we have a partial answer (e.g. they said "not sure") we could ask follow-up, but for simplicity we only do one question per dimension unless we add state for "asked follow-up"
        q_key = next_dim
        primary, follow = criteria.QUESTIONS[next_dim]
        question_text = follow if follow_up else primary
        return EngineResult(
            outcome=None,
            action=ACTION_ASK,
            next_question=q_key,
            follow_up=follow_up,
            message=question_text,
            scores=scores,
            reason="need_more_info",
        )

    # all four scored
    b, a, n, t = scores.get("budget", 1), scores.get("authority", 1), scores.get("need", 1), scores.get("timeline", 1)

    # red on B, A, or N -> disqualify
    if b == 0 or a == 0 or n == 0:
        return EngineResult(
            outcome=OUTCOME_DISQUALIFY,
            action=ACTION_DONE,
            next_question=None,
            follow_up=False,
            message="Based on what you shared, it doesn't sound like we're the right fit right now. If that changes, you can always reach out.",
            scores=scores,
            reason="red_budget_or_authority_or_need",
        )

    # green = 2. Book AE if: 4 green, or 3 green and the only yellow is timeline
    greens = sum(1 for v in (b, a, n, t) if v == 2)
    ban_green = (b == 2) + (a == 2) + (n == 2)
    if greens >= 3 and (t == 2 or (ban_green == 3 and t == 1)):
        return EngineResult(
            outcome=OUTCOME_BOOK_AE,
            action=ACTION_DONE,
            next_question=None,
            follow_up=False,
            message="I'd love to get you on a call with our team. [Book AE]",
            scores=scores,
            reason="strong_fit",
        )

    # else nurture – soft fit, probably still exploring
    return EngineResult(
        outcome=OUTCOME_NURTURE,
        action=ACTION_DONE,
        next_question=None,
        follow_up=False,
        message="Sounds like you're still exploring. We'll send you some resources and check back in. Would that work?",
        scores=scores,
        reason="soft_fit",
    )
