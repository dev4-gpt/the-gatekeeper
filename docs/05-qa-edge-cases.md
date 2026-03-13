# QA Edge Cases – Gatekeeper (Internal)

This file is for **internal testing**, not for the written submission. The goal is to beat up the Gatekeeper logic with messy, real-world conversations and tighten it before it ever talks to a prospect.

## How to use this doc

For each scenario below:

1. Write a short back-and-forth between **Agent** and **Prospect** (3–10 turns).
2. Decide what the agent *should* do next:
   - Ask a follow-up
   - Clarify
   - Nurture
   - Disqualify
   - Route to Account Executive
   - Escalate to human
3. Compare that with what the current system actually does.
4. Note any logic failures and sketch the fixed response you’d want in production.

Use this to stress-test the agent before shipping.

## Scenarios to cover

1. **Partial BANT** – Prospect gives a strong Need but dodges Budget twice.  
   “Yes, we definitely need something like this for our school fundraising but I’m not sure about budget yet.”

2. **Non-decision-maker** – “I’m just researching tools for my director.”

3. **Fake urgency** – Starts with “We need something ASAP” but later says “we’ll probably review options next year.”

4. **Pricing-first** – Prospect keeps asking “What does this cost?” before sharing Need or Authority.

5. **Wrong or fringe segment** – Restaurant owner or solo freelancer; we mostly serve schools and nonprofits.

6. **Extremely qualified lead** – Clear role, numbers, and this-quarter timeline by the second turn.

7. **Vague / hedge words** – Answers like “maybe,” “it depends,” “we’ll see,” especially to Budget and Timeline.

8. **Avoidant behavior** – Repeated “just exploring” when asked about timing or budget.

9. **Budget shock** – “We only have $200.”

10. **Aggressive or impatient** – “Stop asking questions and just show me the demo.”

11. **Multi-stakeholder** – “I’ll need to involve our board / superintendent / pastor.”

12. **Non-buyer persona** – Student, vendor, competitor, or academic researcher.

After running these, summarize for yourself:

- Where the system asked too many questions.
- Where it qualified too quickly.
- Where it misclassified (e.g. nurture vs book AE).
- Where it failed to explain the decision.

Then feed those findings back into the logic tree and escalation rules so the Gatekeeper behaves like a production system instead of a happy-path demo.

