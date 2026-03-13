import random
from dotenv import load_dotenv
load_dotenv()  # pull GOOGLE_API_KEY (and others) from .env into os.environ
from gatekeeper.engine import compute_lead_score, run as engine_run

NEED_OPTIONS = [
    "retention and burnout issues",
    "improve culture and wellbeing",
    "just exploring options",
    "one-off event support",
]

AUTHORITY_OPTIONS = [
    "I sign off",
    "I influence but don't sign",
    "just researching for my director",
    "student looking for information",
]

BUDGET_OPTIONS = [
    "$200",
    "$1500",
    "we have budget allocated",
    "need to get approval",
    "no budget for this",
]

TIMELINE_OPTIONS = [
    "this quarter",
    "next quarter",
    "next year",
    "not this year",
    "just exploring",
]


def random_answers() -> dict[str, str]:
    return {
        "need": random.choice(NEED_OPTIONS),
        "authority": random.choice(AUTHORITY_OPTIONS),
        "budget": random.choice(BUDGET_OPTIONS),
        "timeline": random.choice(TIMELINE_OPTIONS),
    }


def main() -> None:
    n = 1000
    counts = {"book_ae": 0, "nurture": 0, "disqualify": 0, "other": 0}
    escalations = 0
    scores = []

    for _ in range(n):
        answers = random_answers()
        result = engine_run(answers)
        outcome = result.get("outcome")
        scores_dict = result.get("scores", {})
        lead_score, _ = compute_lead_score(scores_dict)
        scores.append(lead_score)

        if outcome in counts:
            counts[outcome] += 1
        else:
            counts["other"] += 1

        if outcome == "escalate_for_review":
            escalations += 1

    print("Simulation Results")
    print("------------------")
    for key in ("book_ae", "nurture", "disqualify", "other"):
        v = counts[key]
        print(f"{key}: {v} ({v / n:.1%})")
    print(f"Escalations: {escalations} ({escalations / n:.1%})")
    avg_score = sum(scores) / len(scores) if scores else 0
    print(f"Average lead score: {avg_score:.1f}")


if __name__ == "__main__":
    main()

