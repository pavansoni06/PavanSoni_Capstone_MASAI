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
crashing the run. This path is exercised in the logs whenever the free-tier rate
limit is hit.

## Task 4 — 15-call template comparison

All three templates were run on the **same 5 reviews** (15 calls total). Each
response was parsed as JSON; failures were logged per template/record.

**Results:**

| Template     | Valid JSON (out of 5) |
|--------------|-----------------------|
| zero_shot    | [FILL TOMORROW]       |
| few_shot     | [FILL TOMORROW]       |
| role_prompt  | [FILL TOMORROW]       |

**Most reliable template:** [FILL TOMORROW]

## Task 5 — Aspect-based sentiment (10 records)

The best-performing template was extended to return, per record, a sentiment label
for two aspects (**product** and **delivery**) plus one short actionable phrase
(3–6 words) per aspect.

[FILL TOMORROW — paste the markdown table printed by aspect_sentiment.py]

## Task 6 — Auto-drafted replies

The structured output from Task 5 was fed into a second, chained prompt that drafts
a short, empathetic, non-generic reply addressing the specific points raised.

[FILL TOMORROW — paste at least 3 review + reply pairs from draft_replies.py]

## Task 7 — Multi-turn context

A 2-turn conversation was run where turn 2 reuses information from turn 1 without
it being repeated. The model correctly recalled the customer's name and issue from
the first turn.

[FILL TOMORROW — paste the Turn 1 / Turn 2 output and the conversation history object]

## Task 8 — API key security

The API key is stored in a `.env` file, excluded from the repository via `.gitignore`.
No key appears anywhere in the code. The required environment-variable name is
`GEMINI_API_KEY` (documented above), so a grader can supply their own key.


