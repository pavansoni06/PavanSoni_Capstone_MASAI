import json
import time
import os
from llm_client import call_llm

ASPECT_CACHE = "aspect_cache.json"   # from Task 5
REPLY_CACHE = "reply_cache.json"

# ------------------------------------------------------------
# Task 6: Feed the structured aspect output into a SECOND prompt
# that drafts a personalized, empathetic reply to that specific review.
# ------------------------------------------------------------

def reply_prompt(review_text, aspect_data):
    return f"""Act as a customer support representative for a Brazilian
e-commerce company. Write a short (3-4 sentences), warm, professional,
and empathetic reply to the customer review below.

Address the SPECIFIC points raised. Here is the structured analysis of
the review to guide you:
{json.dumps(aspect_data, ensure_ascii=False)}

Rules:
- Do NOT use a generic template. Refer to the actual product/delivery points.
- If a sentiment is negative, apologize and offer a next step.
- If positive, thank them warmly.
- Write in English.

Original review: "{review_text}"

Write only the reply text, no preamble.
"""

# Load the Task 5 results (the aspect analysis feeds this task)
if not os.path.exists(ASPECT_CACHE):
    print("ERROR: aspect_cache.json not found. Run aspect_sentiment.py first.")
    raise SystemExit

with open(ASPECT_CACHE, "r", encoding="utf-8") as f:
    aspect_results = json.load(f)

# Load/save reply cache for resumability
if os.path.exists(REPLY_CACHE):
    with open(REPLY_CACHE, "r", encoding="utf-8") as f:
        cache = json.load(f)
else:
    cache = {}

def save_cache():
    with open(REPLY_CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

DELAY = 2

print("=" * 60)
print("TASK 6: AUTO-DRAFTED REPLIES")
print("=" * 60)

# Draft replies for the first 3 valid records (task needs at least 3)
count = 0
for key, entry in aspect_results.items():
    if count >= 3:
        break
    if not entry.get("valid"):
        continue

    if key in cache:
        print(f"\nRecord {key}: cached reply (skip)")
        count += 1
        continue

    review = entry["review"]
    aspect_data = entry["parsed"]
    reply = call_llm(reply_prompt(review, aspect_data), temperature=0.4, max_tokens=1500)

    cache[key] = {"review": review, "aspect_data": aspect_data, "reply": reply}
    save_cache()

    print(f"\n--- Record {key} ---")
    print(f"Review: {review}")
    print(f"Reply:  {reply}")

    count += 1
    time.sleep(DELAY)

print("\n\n--- FORMATTED FOR README ---\n")
for key, entry in cache.items():
    print(f"**Review {key}:** {entry['review']}\n")
    print(f"**Auto-drafted reply:** {entry['reply']}\n")
    print("---\n")

    