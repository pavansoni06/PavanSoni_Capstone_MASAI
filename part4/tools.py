import requests
from langchain_core.tools import tool

# ============================================================
# Tool 1: LIVE EXTERNAL API — calls a real, free, keyless API.
# Good-tool properties:
#   - Clear name: get_random_advice
#   - Honest description (below, in the docstring)
#   - Atomic: does ONE thing (fetch one piece of advice)
#   - Safe: returns errors as data, never raises/crashes the agent
# ============================================================
@tool
def get_random_advice() -> str:
    """Fetches a single piece of random life advice from a live public API.
    Use this when the user asks for advice, a tip, or words of wisdom.
    Takes no arguments."""
    try:
        response = requests.get("https://api.adviceslip.com/advice", timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["slip"]["advice"]
    except Exception as e:
        # Return the error as data so the agent can handle it gracefully.
        return f"ERROR: could not fetch advice ({e})"


# ============================================================
# Tool 2: LOCAL / MOCK DATA — reads from a local dictionary.
# Good-tool properties:
#   - Clear name: lookup_order_status
#   - Honest description
#   - Atomic: looks up ONE order's status
#   - Safe: returns a friendly message for unknown orders, never crashes
# ============================================================
_MOCK_ORDERS = {
    "A101": "shipped, expected delivery in 2 days",
    "B202": "delivered on 2024-05-01",
    "C303": "processing, not yet shipped",
    "D404": "canceled by customer",
}

@tool
def lookup_order_status(order_id: str) -> str:
    """Looks up the delivery status of a customer order by its order ID.
    Use this when the user asks about the status of a specific order.
    The argument 'order_id' is a short code like 'A101'."""
    order_id = order_id.strip().upper()
    if order_id in _MOCK_ORDERS:
        return f"Order {order_id}: {_MOCK_ORDERS[order_id]}"
    return f"Order {order_id} was not found in our system."


# Quick standalone test (no agent, no LLM — just checks the tools work)
if __name__ == "__main__":
    print("Testing get_random_advice:")
    print(" ", get_random_advice.invoke({}))
    print("\nTesting lookup_order_status:")
    print(" ", lookup_order_status.invoke({"order_id": "A101"}))
    print(" ", lookup_order_status.invoke({"order_id": "Z999"}))


    