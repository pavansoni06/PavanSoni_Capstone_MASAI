import json
import time
import os
import pandas as pd
from llm_client import call_llm

CACHE_FILE = "aspect_cache.json"

# ------------------------------------------------------------
# Task 5: Aspect-based sentiment on 10 records.
# Extends the best template to return per-aspect sentiment +
# one short actionable phrase (3-6 words) per aspect.
# ------------------------------------------------------------

def aspect_prompt(review_text):
    return f"""Act as a senior customer-insights analyst for a Brazilian
e-commerce company. Analyze the customer review below.

For TWO aspects — "product" and "delivery" — determine:
  - a sentiment label: "positive", "negative", or "neutral"
  - one short actionable phrase (3 to 6 words) describing what was
    liked or disliked about that aspect.

If an aspect is not mentioned, use "neutral" and the phrase "not mentioned".

Respond ONLY with valid JSON in exactly this schema:
{{
  "product": {{"sentiment": "...", "phrase": "..."}},
  "delivery": {{"sentiment": "...", "phrase": "..."}}
}}

Review: "{review_text}"
"""

# Load 10 real reviews with non-empty messages
df = pd.read_csv("olist_order_reviews_dataset.csv")
df = df.dropna(subset=["review_comment_message"])
df = df[df["review_comment_message"].str.strip() != ""]
records = df.head(10).reset_index(drop=True)

# Load cache so we can resume without re-spending quota
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        cache = json.load(f)
else:
    cache = {}

def save_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

DELAY = 6  # seconds between calls (safe under 15 RPM for gemini-2.0-flash)

print("=" * 60)
print("TASK 5: ASPECT-BASED SENTIMENT (10 records)")
print("=" * 60)

for i in range(len(records)):
    key = str(i)
    review = records.loc[i, "review_comment_message"]

    if key in cache and cache[key].get("valid"):
        print(f"\nRecord {i}: cached (skip)")
        continue

    raw = call_llm(aspect_prompt(review), json_mode=True)
    try:
        parsed = json.loads(raw) if raw else None
        valid = bool(parsed and "product" in parsed and "delivery" in parsed)
    except (json.JSONDecodeError, TypeError):
        parsed, valid = None, False

    cache[key] = {"review": review, "parsed": parsed, "valid": valid}
    save_cache()

    print(f"\nRecord {i}: {review[:60]}")
    if valid:
        print(f"  product : {parsed['product']['sentiment']} - {parsed['product']['phrase']}")
        print(f"  delivery: {parsed['delivery']['sentiment']} - {parsed['delivery']['phrase']}")
    else:
        print("  INVALID / no response")

    time.sleep(DELAY)

# Build a markdown table for the README
print("\n\n--- MARKDOWN TABLE FOR README ---\n")
print("| # | Review (truncated) | Product | Product phrase | Delivery | Delivery phrase |")
print("|---|--------------------|---------|----------------|----------|-----------------|")
for i in range(len(records)):
    entry = cache.get(str(i))
    if entry and entry.get("valid"):
        p = entry["parsed"]
        review_short = entry["review"][:40].replace("\n", " ").replace("|", " ")
        print(f"| {i} | {review_short} | {p['product']['sentiment']} | "
              f"{p['product']['phrase']} | {p['delivery']['sentiment']} | "
              f"{p['delivery']['phrase']} |")


        