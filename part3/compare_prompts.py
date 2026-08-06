import json
import time
import pandas as pd
from prompts import TEMPLATES
from llm_client import call_llm

# ------------------------------------------------------------
# Load reviews and pick 5 real records with non-empty messages.
# ------------------------------------------------------------
df = pd.read_csv("olist_order_reviews_dataset.csv")
df = df.dropna(subset=["review_comment_message"])
df = df[df["review_comment_message"].str.strip() != ""]

sample = df.head(5).reset_index(drop=True)
reviews = sample["review_comment_message"].tolist()

print(f"Selected {len(reviews)} reviews for the comparison.\n")
for i, r in enumerate(reviews, 1):
    print(f"Review {i}: {r[:70]}")

# ------------------------------------------------------------
# Task 4: 3 templates x 5 reviews = 15 calls, using JSON mode.
# Space calls ~13s apart to respect the 5-requests-per-minute free tier.
# ------------------------------------------------------------
valid_counts = {name: 0 for name in TEMPLATES}
DELAY = 2   # seconds between calls (free tier is strict)

print("\n" + "=" * 60)
print("RUNNING 15 CALLS (3 templates x 5 reviews)")
print("This is paced for the free tier, so it takes ~3-4 minutes.")
print("=" * 60)

for template_name, template_func in TEMPLATES.items():
    print(f"\n--- Template: {template_name} ---")
    for i, review in enumerate(reviews, 1):
        prompt = template_func(review)
        raw = call_llm(prompt, json_mode=True)   # force clean JSON

        try:
            parsed = json.loads(raw) if raw else None
            if parsed and "label" in parsed:
                valid_counts[template_name] += 1
                print(f"  Review {i}: VALID -> {parsed.get('label')}, {parsed.get('confidence')}")
            else:
                print(f"  Review {i}: INVALID -> template={template_name}, missing fields")
        except (json.JSONDecodeError, TypeError):
            print(f"  Review {i}: INVALID -> template={template_name}, could not parse")

        time.sleep(DELAY)   # pace to stay under the rate limit

# ------------------------------------------------------------
# Report which template was most reliable.
# ------------------------------------------------------------
print("\n" + "=" * 60)
print("RESULTS: valid JSON responses out of 5 per template")
print("=" * 60)
for name, count in valid_counts.items():
    print(f"  {name}: {count}/5 valid")

best = max(valid_counts, key=valid_counts.get)
print(f"\nMost reliable template: {best} ({valid_counts[best]}/5 valid JSON)")


