"""
BANT questions and how we score answers. Matches docs/01-qualification-framework.md.
"""

import re
from typing import Tuple

# order we prefer to ask (need first keeps it conversational)
BANT_ORDER = ("need", "authority", "budget", "timeline")

QUESTIONS = {
    "need": (
        "What's driving you to look at something like this right now—retention, burnout, culture, or something else?",
        "How are you handling that today, and what's not working?",
    ),
    "authority": (
        "Are you the person who would sign off on a partnership like this, or would you be bringing in other decision-makers?",
        "Who else would need to be in the room for a decision?",
    ),
    "budget": (
        "Do you have budget allocated for mental fitness or wellbeing programs this year, or would this need to be approved?",
        "Roughly—are we talking about a line item that already exists, or something you'd need to get sign-off on?",
    ),
    "timeline": (
        "When would you ideally want to have something in place—this quarter, next quarter, or still exploring?",
        "Any hard deadline—board meeting, new school year, fiscal year?",
    ),
}

# Each dimension: list of (pattern_substring, score). First match wins. score: 2 = green, 1 = yellow, 0 = red.
# Lowercased and stripped before match. We keep it simple so the engine is transparent.
BUDGET_GREEN = ("have budget", "allocated", "already approved", "line item", "yes")
BUDGET_YELLOW = ("need to get approval", "not sure", "would need approval", "exploring")
BUDGET_RED = ("no budget", "don't spend", "no money", "can't afford", "no")

AUTHORITY_GREEN = ("i sign off", "decision maker", "i would", "i'm the one", "yes i am")
AUTHORITY_YELLOW = ("bring in", "other decision", "need to check", "influencer")
AUTHORITY_RED = ("not my department", "just a student", "vendor", "no influence")

NEED_GREEN = ("retention", "burnout", "culture", "wellbeing", "mental fitness", "alignment", "clarity", "resilience")
NEED_YELLOW = ("exploring", "just looking", "seeing what's out there", "maybe")
NEED_RED = ("therapy", "clinical", "one-off", "wrong product", "not a fit")

TIMELINE_GREEN = ("this quarter", "next quarter", "q1", "q2", "q3", "q4", "next month", "fall", "spring", "fiscal year")
TIMELINE_YELLOW = ("exploring", "no rush", "not sure", "later", "next year")
TIMELINE_RED = ("not this year", "just researching", "no timeline")


def normalize_answer(text: str) -> str:
    if not text:
        return text
    t = text.strip().lower()

    if t in {"yes", "yeah", "yep", "sure"}:
        return "yes i am"

    if t in {"now", "now!", "asap", "right away"}:
        return "this quarter"

    return t


def _contains(text: str, phrase: str) -> bool:
    """
    Return True if phrase is present in text using a slightly stricter check
    than raw substring for short words like "no".
    """
    if not phrase:
        return False
    # For simple alphabetic tokens without spaces, use word boundaries.
    if phrase.isalpha() and " " not in phrase:
        return bool(re.search(rf"\\b{re.escape(phrase)}\\b", text))
    return phrase in text


def _score_wordlist(text: str, green: Tuple[str, ...], yellow: Tuple[str, ...], red: Tuple[str, ...]) -> int:
    """Returns 2=green, 1=yellow, 0=red. First match wins."""
    if not text or not text.strip():
        return 1  # vague = yellow
    t = normalize_answer(text)
    for phrase in red:
        if _contains(t, phrase):
            return 0
    for phrase in green:
        if _contains(t, phrase):
            return 2
    for phrase in yellow:
        if _contains(t, phrase):
            return 1
    # default: if they said something substantive, treat as yellow so we don't over-red
    return 1 if len(t) > 3 else 1


def score_budget(answer: str) -> int:
    # First, see if they mentioned a concrete amount.
    if answer:
        nums = re.findall(r"\\d+(?:\\.\\d+)?", answer.replace(",", ""))
        if nums:
            try:
                amount = float(nums[0])
            except ValueError:
                amount = 0.0
            # Very rough heuristic: below this, it's unlikely to be a fit.
            MIN_BUDGET = 500.0
            if amount and amount < MIN_BUDGET:
                return 0
            if amount >= MIN_BUDGET:
                return 2
    return _score_wordlist(answer, BUDGET_GREEN, BUDGET_YELLOW, BUDGET_RED)


def score_authority(answer: str) -> int:
    return _score_wordlist(answer, AUTHORITY_GREEN, AUTHORITY_YELLOW, AUTHORITY_RED)


def score_need(answer: str) -> int:
    return _score_wordlist(answer, NEED_GREEN, NEED_YELLOW, NEED_RED)


def score_timeline(answer: str) -> int:
    return _score_wordlist(answer, TIMELINE_GREEN, TIMELINE_YELLOW, TIMELINE_RED)


SCORERS = {
    "budget": score_budget,
    "authority": score_authority,
    "need": score_need,
    "timeline": score_timeline,
}
