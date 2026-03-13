from __future__ import annotations

from typing import Dict


def _label(score: int) -> str:
    if score == 2:
        return "green"
    if score == 1:
        return "yellow"
    return "red"


def build_recap(answers: Dict[str, str], scores: Dict[str, int]) -> str:
    parts: list[str] = ["Here's how I'm reading what you shared:"]
    for dim in ("need", "authority", "budget", "timeline"):
        raw = (answers.get(dim) or "").strip()
        if not raw:
            continue
        score = scores.get(dim, 1)
        parts.append(f"- {dim.capitalize()}: \"{raw}\" → {_label(score)}")
    return "\n".join(parts)


def describe_outcome(outcome: str | None, reason: str) -> str:
    if outcome == "book_ae":
        return (
            "Given that signal, I'm treating this as a strong fit and near-term timing.\n"
            "Next step: I'll hand this off to our sales team and get time booked with an Account Executive."
        )
    if outcome == "nurture":
        return (
            "It sounds like you're still in exploration mode.\n"
            "Next step: we'll send a short overview and a couple of relevant resources, then follow up later instead of booking time right away."
        )
    if outcome == "disqualify":
        return (
            "Based on what you shared, this isn't the right fit right now—usually because of budget, authority, or what you're looking for.\n"
            "Next step: we won't push for a meeting, but you can always come back if your situation changes."
        )
    if reason == "escalation_requested":
        return (
            "You asked to talk with a human.\n"
            "Next step: I'll pass this thread and your answers so far to the right person on our team."
        )
    # fallback
    return "I'll capture what you've shared and pass it along so our team can review it."

