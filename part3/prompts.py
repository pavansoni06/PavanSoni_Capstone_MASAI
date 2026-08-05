# ============================================================
# Task 1: Three prompt templates for sentiment classification.
# All three lock the model into the SAME JSON schema with 3 fields:
#   {"label": "...", "confidence": "...", "reason": "..."}
# ============================================================

# The shared JSON schema instruction reused by all templates.
JSON_SCHEMA_INSTRUCTION = """
Respond ONLY with a valid JSON object in exactly this schema, and nothing else
(no markdown, no code fences, no extra text):
{
  "label": "positive" | "negative" | "neutral",
  "confidence": "low" | "medium" | "high",
  "reason": "a short string explaining the classification"
}
"""

# ---- (a) ZERO-SHOT: instruction only, no examples ----
def zero_shot_prompt(review_text):
    return f"""Classify the sentiment of the following customer review.

{JSON_SCHEMA_INSTRUCTION}

Review: "{review_text}"
"""

# ---- (b) FEW-SHOT: same instruction + worked examples ----
def few_shot_prompt(review_text):
    return f"""Classify the sentiment of the following customer review.

{JSON_SCHEMA_INSTRUCTION}

Here are some examples:

Review: "Produto excelente, chegou antes do prazo!"
{{"label": "positive", "confidence": "high", "reason": "praises product and fast delivery"}}

Review: "Nunca recebi o produto, pessimo."
{{"label": "negative", "confidence": "high", "reason": "product never arrived"}}

Review: "O produto e ok, nada demais."
{{"label": "neutral", "confidence": "medium", "reason": "indifferent, product is just okay"}}

Now classify this one:
Review: "{review_text}"
"""

# ---- (c) ROLE-PROMPTED: persona + Clarity/Context/Constraint ----
def role_prompt(review_text):
    return f"""Act as a senior customer-insights analyst for a Brazilian
e-commerce company.

CONTEXT: You are analyzing customer reviews (often in Portuguese) to help the
operations team understand customer satisfaction. Reviews may mention product
quality, delivery speed, or seller service.

TASK (CLARITY): Determine the overall sentiment of the review below.

CONSTRAINTS:
- Base your judgment only on the review text provided.
- If the review is ambiguous or empty, use "neutral" with "low" confidence.
- Keep the reason under 15 words.

{JSON_SCHEMA_INSTRUCTION}

Review: "{review_text}"
"""

# Convenience: a dict so other scripts can loop over all three by name.
TEMPLATES = {
    "zero_shot": zero_shot_prompt,
    "few_shot": few_shot_prompt,
    "role_prompt": role_prompt,
}

