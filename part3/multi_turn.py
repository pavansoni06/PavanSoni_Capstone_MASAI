import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ------------------------------------------------------------
# Task 7: 2-turn conversation. The second turn must reuse info
# supplied in the first turn, and we print the full history object.
# ------------------------------------------------------------

MODEL = "gemini-flash-latest"

print("=" * 60)
print("TASK 7: MULTI-TURN CONVERSATION")
print("=" * 60)

# --- Turn 1: give the model a fact it must remember ---
# We tell it about a specific customer complaint.
turn1_user = ("A customer named Maria complained that her order arrived "
              "10 days late and the box was damaged. Summarize her main issue "
              "in one sentence.")

# The conversation history is a list of role/content messages.
history = [
    {"role": "user", "parts": [{"text": turn1_user}]}
]

response1 = client.models.generate_content(model=MODEL, contents=history)
turn1_reply = response1.text
print("\n--- TURN 1 ---")
print("User:", turn1_user)
print("Model:", turn1_reply)

# Append the model's reply to the history so turn 2 has context
history.append({"role": "model", "parts": [{"text": turn1_reply}]})

# --- Turn 2: ask something that ONLY works if it remembers turn 1 ---
# We do NOT repeat Maria's name or her problem.
turn2_user = ("Based on what you know, what is the customer's name and "
              "what compensation would you offer her?")
history.append({"role": "user", "parts": [{"text": turn2_user}]})

response2 = client.models.generate_content(model=MODEL, contents=history)
turn2_reply = response2.text
print("\n--- TURN 2 ---")
print("User:", turn2_user)
print("Model:", turn2_reply)

# Append final reply to complete the history object
history.append({"role": "model", "parts": [{"text": turn2_reply}]})

# --- Show the full conversation history object (required by the task) ---
print("\n--- FULL CONVERSATION HISTORY OBJECT ---")
import json
print(json.dumps(history, indent=2, ensure_ascii=False))



