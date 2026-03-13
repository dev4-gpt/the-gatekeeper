# Logic Tree

How the agent moves from one step to the next. Written flow first, then a compact visual.

## Written flow

1. **Inbound**  
   Prospect hits the site (demo request, chat, form). Agent starts conversation and confirms context (org type, role, what they’re looking for).

2. **If context missing or unclear**  
   Ask: “What kind of organization are you with?” / “What’s your role?” / “What are you hoping this product could help with?”  
   Don’t run BANT until we know who they are and why they’re here.

3. **Run BANT**  
   Ask Budget, Authority, Need, Timeline (order can vary; we often do Need first so it feels conversational).  
   For each answer: classify as green, yellow, or red per the Qualification Framework.

4. **If prospect objects mid-BANT**  
   - “I don’t want to share budget” → “No problem. Are you the one who’d sign off on a program like this, or would others be involved?” (pivot to Authority or Timeline).  
   - “I just want to talk to someone” → Route to human.  
   - “We’re not ready yet” → Yellow; add to nurture, don’t push for a meeting.

5. **If answer is incomplete or vague**  
   Ask the follow-up from the framework once. If still vague, store what we have and either ask one more clarifying question or treat as yellow and nurture.

6. **After BANT**  
   - **All green (or 3 green + 1 yellow on timeline):** “I’d love to get you on a call with our team. [Book AE].”  
   - **Mostly yellow, no red:** “Sounds like you’re still exploring. We’ll send you some resources and check back in [timeframe]. Would that work?” → Nurture.  
   - **Any red on Budget / Authority / Need:** “Based on what you shared, it doesn’t sound like we’re the right fit right now. If that changes, you can always reach out.” → Disqualify, stop engaging for a meeting.

7. **If they ask for a human**  
   Escalate. No need to finish BANT first.

8. **If they go silent**  
   Don’t over-message. Follow nurture rules (see Human Escalation); we don’t chase forever.

---

## Visual (compact)

```
Inbound
   │
   ▼
Context clear? ──No──► Ask role / org / what they need
   │
   Yes
   ▼
Run BANT (Budget, Authority, Need, Timeline)
   │
   ├─ Objection (“want to talk to someone”) ──► Escalate to human
   ├─ Incomplete answer ──► Ask follow-up once, then treat as yellow or move on
   │
   ▼
Score: Green / Yellow / Red
   │
   ├─ Green (or 3G + 1Y timeline) ──► Book AE
   ├─ Yellow (nurture) ──► Add to sequence, no AE meeting
   └─ Red (B/A/N) ──► Disqualify, stop pushing for meeting
```
