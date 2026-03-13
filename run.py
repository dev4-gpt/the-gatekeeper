#!/usr/bin/env python3
"""
CLI for the Gatekeeper qualification flow. Asks BANT questions, runs the engine, prints outcome.
Usage: python run.py
"""
import sys
from dotenv import load_dotenv
load_dotenv()  # pull GOOGLE_API_KEY (and others) from .env into os.environ
from gatekeeper import criteria
from gatekeeper.engine import compute_lead_score, run as engine_run
from gatekeeper import messages
from gatekeeper.storage import init_db, save_lead

def _maybe_clarify_answer(question_key: str, raw: str) -> str:
    """
    Light-weight clarification for obviously vague responses.
    We keep this small and readable; the goal is to show how we'd tighten
    the conversation, not to cover every NLP edge case.
    """
    text = raw.lower().strip()
    if question_key == "timeline" and text in {"just exploring", "exploring", "not sure"}:
        follow = criteria.QUESTIONS["timeline"][1]
        print(f"Agent: {follow}")
        second = input("Prospect: ").strip()
        return second or raw
    if question_key == "budget" and text in {"not sure", "no idea"}:
        follow = criteria.QUESTIONS["budget"][1]
        print(f"Agent: {follow}")
        second = input("Prospect: ").strip()
        return second or raw
    return raw


def main():
    init_db()
    answers: dict[str, str] = {}
    print("Gatekeeper – BANT qualification. Answer as a prospect would (or type 'human' to escalate, 'quit' to exit).\n")

    while True:
        result = engine_run(answers, escalation_requested=False)

        if result["action"] == "escalate":
            print("\n[Escalate to human]\n")
            print(messages.describe_outcome(result["outcome"], result["reason"]))
            break

        if result["action"] == "ask":
            q_key = result["next_question"]
            primary, _ = criteria.QUESTIONS[q_key]
            print(f"Agent: {primary}")
            raw = input("Prospect: ").strip()
            lowered = raw.lower()
            if lowered in ("human", "talk to someone", "speak to someone"):
                # prospect explicitly wants a person
                escalate = engine_run(answers, escalation_requested=True)
                print("\n[Escalate to human]\n")
                print(messages.describe_outcome(escalate["outcome"], escalate["reason"]))
                break
            if lowered in ("quit", "exit"):
                sys.exit(0)

            raw = _maybe_clarify_answer(q_key, raw)
            answers[q_key] = raw
            continue

        if result["action"] == "done":
            print(f"\nAgent: {result['message']}\n")
            # recap how we interpreted their answers
            recap = messages.build_recap(answers, result["scores"])
            print(recap)
            print()
            print(messages.describe_outcome(result["outcome"], result["reason"]))
            print()
            confirm = input("Agent: Does that sound right? (yes/no) ").strip().lower()
            scores = result["scores"]
            if confirm in {"yes", "y", "yeah"}:
                final_outcome = result["outcome"] or ""
                final_reason = result["reason"]
                print(f"Outcome: {final_outcome}\n")
            else:
                final_outcome = "escalate_for_review"
                final_reason = "low_confidence_cli"
                print(
                    "\nAgent: Got it. I'll flag this for a human to review instead of making a final call right now.\n"
                )
                print(f"Outcome: {final_outcome}\n")

            lead_score, confidence_band = compute_lead_score(scores)
            save_lead(
                answers=answers,
                scores=scores,
                outcome=final_outcome,
                reason=final_reason,
                lead_score=lead_score,
                confidence_band=confidence_band,
            )
            break

    return 0


if __name__ == "__main__":
    sys.exit(main())
