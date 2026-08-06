# Part 3 — GenAI-Powered Text Analytics: Prompt Engineering & LLM API Integration

## Overview

This part uses Google Gemini to automate sentiment analysis of customer reviews.
It compares three prompting strategies, wraps the LLM in a reusable API function
with retry handling, performs aspect-based sentiment extraction, auto-drafts
customer replies, and demonstrates multi-turn context.

**Dataset:** Olist customer reviews (`olist_order_reviews_dataset.csv`), using the
free-text `review_comment_message` field (200+ non-empty records, mostly Portuguese).

## Environment variable required

The API key is loaded from an environment variable and is **never** committed.
To run this code, set:

GEMINI_API_KEY=your_google_gemini_api_key

Store it in a `.env` file in this folder. The `.env` file is excluded via `.gitignore`.

## Files

- `prompts.py` — the three prompt templates (Task 1).
- `llm_client.py` — reusable `call_llm()` with retry logic (Tasks 2 & 3).
- `compare_prompts.py` — 15-call template comparison (Task 4).
- `aspect_sentiment.py` — aspect-based sentiment on 10 records (Task 5).
- `draft_replies.py` — chained reply-drafting prompt (Task 6).
- `multi_turn.py` — 2-turn conversation demo (Task 7).

## Task 1 — Three prompt templates

Three templates are defined in `prompts.py`, all locked to the same JSON schema
with three required fields: `label`, `confidence`, `reason`.

- **Zero-shot** — instruction only, no examples.
- **Few-shot** — same instruction plus 3 worked examples (positive/negative/neutral).
- **Role-prompted** — opens with a persona ("Act as a senior customer-insights
  analyst…") and applies the Three Cs: Clarity (the task), Context (Brazilian
  e-commerce reviews), and Constraint (judge only from the text, cap the reason length).

## Task 2 — Reusable API wrapper

`call_llm(prompt, temperature, max_tokens)` in `llm_client.py`:
- Loads the API key from the `GEMINI_API_KEY` environment variable (never hardcoded).
- Sends the prompt with the given temperature and max_tokens.
- Returns the model's text response.
- Supports a `json_mode` option that forces schema-valid JSON output.

## Task 3 — Retry-on-failure

`call_llm()` retries up to **3 times** on any failure (network error, rate limit,
or error response). It waits longer between each attempt (exponential-style backoff)
and, after 3 failures, logs a descriptive error and returns `None` instead of
crashing the run. This path was exercised during development whenever the API rate
limit was hit, and the retries recovered the calls.

## Task 4 — 15-call template comparison

All three templates were run on the **same 5 reviews** (15 calls total). Each
response was parsed as JSON; failures would be logged per template/record.

| Template     | Valid JSON (out of 5) |
|--------------|-----------------------|
| zero_shot    | 5                     |
| few_shot     | 5                     |
| role_prompt  | 5                     |

**Most reliable template:** All three templates produced 5/5 valid, schema-conformant
JSON — a three-way tie at 100%. This is because `call_llm()` enforces
`response_mime_type: "application/json"` (JSON mode), which guarantees well-formed
output regardless of prompt style. When JSON validity is forced at the API level,
prompt strategy no longer affects schema conformance; the templates instead differ
in the *quality* of their classifications (e.g. role_prompt gives more nuanced reasons).

## Task 5 — Aspect-based sentiment (10 records)

The best-performing template was extended to return, per record, a sentiment label
for two aspects (**product** and **delivery**) plus one short actionable phrase
(3–6 words) per aspect.

| # | Review (truncated) | Product | Product phrase | Delivery | Delivery phrase |
|---|--------------------|---------|----------------|----------|-----------------|
| 0 | Recebi bem antes do prazo estipulado. | neutral | not mentioned | positive | Delivered well before the deadline |
| 1 | Parabéns lojas lannister adorei comprar | neutral | not mentioned | neutral | not mentioned |
| 2 | aparelho eficiente. no site a marca do a | positive | efficient device with incorrect branding | neutral | not mentioned |
| 3 | Mas um pouco ,travando...pelo valor ta B | positive | freezes slightly but good value | neutral | not mentioned |
| 4 | Vendedor confiável, produto ok e entrega | neutral | product quality was acceptable | positive | delivered earlier than expected |
| 5 | GOSTARIA DE SABER O QUE HOUVE, SEMPRE RE | neutral | not mentioned | negative | order was not received |
| 6 | Péssimo | neutral | not mentioned | neutral | not mentioned |
| 7 | Loja nota 10 | neutral | not mentioned | neutral | not mentioned |
| 8 | obrigado pela atençao amim dispensada | neutral | not mentioned | neutral | not mentioned |
| 9 | A compra foi realizada facilmente. A entrega foi efetuada | positive | product working without any issues | positive | delivered well ahead of schedule |

## Task 6 — Auto-drafted replies

The structured output from Task 5 was fed into a second, chained prompt that drafts
a short, empathetic, non-generic reply addressing the specific points raised.

**Review 0:** Recebi bem antes do prazo estipulado.
**Auto-drafted reply:** Thank you so much for taking the time to share your feedback with us! We are delighted to hear that your order arrived well before the expected delivery date. Getting your packages to you quickly and safely is always a top priority for our team. We hope you enjoy your purchase, and we look forward to serving you again soon!

---

**Review 1:** Parabéns lojas lannister adorei comprar pela Internet seguro e prático Parabéns a todos feliz Páscoa
**Auto-drafted reply:** Thank you so much for your wonderful review and for trusting Lojas Lannister! We are thrilled to hear that you loved your online shopping experience with us and found our platform so safe and practical to use. Our entire team truly appreciates your kind congratulations, and we wish you and your family a very Happy Easter as well!

---

**Review 2:** aparelho eficiente. no site a marca do aparelho esta impresso como 3desinfector e ao chegar esta com outro nome...atualizar com a marca correta uma vez que é o mesmo aparelho
**Auto-drafted reply:** Thank you so much for your feedback and for letting us know that you are pleased with the device's efficiency! We sincerely apologize for the confusion caused by the mismatch between the brand name displayed on our website and the one on the product you received. We truly appreciate your helpful suggestion and have already requested our catalog team to update the listing with the correct brand details immediately. Please feel free to reach out to our support team if you have any further questions about your purchase—we are always here to help!

Each reply references specific content from its source review (the early delivery,
the store name "Lojas Lannister" and Easter greeting, the brand-name mismatch),
confirming they are not generic template responses.

## Task 7 — Multi-turn context

A 2-turn conversation was run where turn 2 reuses information from turn 1 without
it being repeated. The conversation history is a list of role/content messages.

**Turn 1 — User:** "A customer named Maria complained that her order arrived 10 days
late and the box was damaged. Summarize her main issue in one sentence."
**Turn 1 — Model:** "Maria complained that her order arrived ten days late and in a
damaged box."

**Turn 2 — User:** "Based on what you know, what is the customer's name and what
compensation would you offer her?"
**Turn 2 — Model:** "The customer's name is **Maria**. As compensation, I would offer
her: (1) a full/partial refund of shipping fees for the 10-day delay, (2) a store
credit or discount code as a goodwill gesture, and (3) an immediate replacement or
full refund if the product inside the damaged box was also broken."

Turn 2 correctly recalled the customer's name ("Maria") and tied the compensation
directly to her specific issues (the delay and the damaged box) **without those
details being repeated in the second turn** — demonstrating that the model used the
context carried in the conversation history object.

## Task 8 — API key security

The API key is stored in a `.env` file, excluded from the repository via `.gitignore`.
No key appears anywhere in the code. The required environment-variable name is
`GEMINI_API_KEY` (documented above), so a grader can supply their own key.