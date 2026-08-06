import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()
_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def call_llm(prompt, temperature=0.2, max_tokens=800, json_mode=False):
    """
    Task 2: Reusable LLM wrapper.
      - Loads the API key from an environment variable (never hardcoded).
      - Sends the prompt with the given temperature and max_tokens.
      - Returns the model's text response.
      - json_mode=True forces the model to return a valid JSON object.

    Task 3: Retries up to 3 times on failure before logging an error.
    """
    config = {
        "temperature": temperature,
        "max_output_tokens": max_tokens,
    }
    if json_mode:
        config["response_mime_type"] = "application/json"

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            response = _client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt,
                config=config,
            )
            return response.text
        except Exception as e:
            # If it's a rate-limit error, wait longer (free tier = 5 req/min)
            wait = 20 * attempt
            print(f"  [call_llm] attempt {attempt}/{max_retries} failed: {str(e)[:80]}")
            if attempt < max_retries:
                print(f"  [call_llm] waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                print(f"  [call_llm] all {max_retries} attempts failed. Giving up.")
                return None


if __name__ == "__main__":
    print("Testing call_llm() with JSON mode...")
    result = call_llm('Return JSON: {"label":"positive","confidence":"high","reason":"test"}',
                      json_mode=True)
    print("Response:", result)


