import json
import os
from typing import Dict

from google import genai

LABEL_TO_SCORE = {"red": 0, "yellow": 1, "green": 2}


def _get_model():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set")
    client = genai.Client(api_key=api_key)
    # Use a recent, free-tier-friendly Gemini model
    return client.generative_model("gemini-2.5-flash")


PROMPT_TEMPLATE = """
You are a sales qualification assistant. You receive BANT answers:

Need: {need}
Authority: {authority}
Budget: {budget}
Timeline: {timeline}

For each dimension, classify it as:
- green: strong buying signal
- yellow: some interest but unclear or weak
- red: not a fit or no buying intent

Respond with ONLY valid JSON, no commentary, no markdown fences, with this exact shape:

{{
  "need": {{"label": "green|yellow|red", "reason": "..." }},
  "authority": {{ "label": "green|yellow|red", "reason": "..." }},
  "budget": {{ "label": "green|yellow|red", "reason": "..." }},
  "timeline": {{ "label": "green|yellow|red", "reason": "..." }}
}}
""".strip()


def classify_bant_with_gemini(answers: Dict[str, str]) -> Dict[str, int]:
    model = _get_model()
    prompt = PROMPT_TEMPLATE.format(
        need=answers.get("need", ""),
        authority=answers.get("authority", ""),
        budget=answers.get("budget", ""),
        timeline=answers.get("timeline", ""),
    )

    resp = model.generate_content(prompt)
    text = (resp.text or "").strip()

    data = json.loads(text)
    scores: Dict[str, int] = {}

    for dim in ("need", "authority", "budget", "timeline"):
        label = data.get(dim, {}).get("label", "yellow").lower().strip()
        scores[dim] = LABEL_TO_SCORE.get(label, 1)

    return scores

