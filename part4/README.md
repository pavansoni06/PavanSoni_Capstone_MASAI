# Part 4 — Agentic AI System: Tool-Using Agent with LangChain

## Overview

This part builds an autonomous **LangChain** agent (Option A) powered by Google
Gemini. The agent is given real tools, decides which to call, executes them, and
produces answers. It also includes a separate conditional workflow built from
LangChain Runnables.

**Option chosen:** Option A (LangChain single autonomous agent) — chosen for its
simpler single-agent setup and direct demonstration of tool-calling, memory, and
Runnable-based routing.

## Environment variable required

The agent's LLM loads its API key from an environment variable, never hardcoded.
To run this code, set:

GEMINI_API_KEY=your_google_gemini_api_key


Store it in a `.env` file in this folder. The `.env` file is excluded via
`.gitignore`, so no key appears in the repository.

## Files

- `tools.py` — the two agent tools.
- `agent.py` — the tool-calling agent, memory demo, tool-call logging, 3 queries.
- `workflow.py` — the RunnablePassthrough + RunnableBranch conditional workflow.

## How to run

python3 tools.py # test the two tools directly
python3 agent.py # run the agent: memory demo + 3 queries + tool-call logs
python3 workflow.py # run the conditional workflow (both routes)


## Tools — contract table

Both tools follow the four good-tool properties: **Clear name, Honest description,
Atomic (one job), Safe (returns errors as data, never crashes the agent).**

| Tool | Description | Parameters | Read/Write |
|------|-------------|------------|------------|
| `get_random_advice` | Fetches one piece of random advice from a live public API (`api.adviceslip.com`) | none | Read |
| `lookup_order_status` | Looks up the delivery status of an order by its ID from local data | `order_id` (string) | Read |

`get_random_advice` calls a **real, live, keyless external API**. Both tools are
read-only (no write tools), and both catch failures internally and return the error
as a string so the agent never crashes.

## Agent construction

The agent is built with `create_tool_calling_agent` combined with an
`AgentExecutor`, configured with `max_iterations=5` so the reasoning loop is bounded
and cannot run away. The underlying chat model is Gemini (`gemini-flash-latest`).

## {tool, arguments} logging

For every tool call, the resolved decision is extracted from LangChain's **own
native mechanism** — the executor's `intermediate_steps` (each an `AgentAction`
carrying `.tool` and `.tool_input`) — not by parsing raw text. Real examples
captured during a run:

TOOL CALL: {"tool": "lookup_order_status", "arguments": {"order_id": "A101"}}
RESULT : Order A101: shipped, expected delivery in 2 days

TOOL CALL: {"tool": "get_random_advice", "arguments": {}}
RESULT : Just because you are offended, doesn't mean you are right.


## Demonstrated queries (the end-to-end loop)

**Query 1 (Turn 1):** "What is the status of order A101?"
- Tool called: `lookup_order_status({"order_id": "A101"})`
- Final answer: "Order A101 has been shipped and is expected to be delivered in 2 days."

**Query 2 (Turn 2 — memory):** "Is that order going to arrive soon?"
- The user did **not** repeat the order ID. The agent reused "A101" from the
  conversation history (passed via `chat_history`) and answered:
  "Yes, order A101 is scheduled to arrive soon — expected in 2 days."
- This demonstrates conversation memory across two turns.

**Query 3:** "I'm feeling stressed about work. Can you give me a piece of advice?"
- Tool called: `get_random_advice({})` (the live external API)
- Final answer: returned a real piece of fetched advice plus supportive suggestions.

## Conditional workflow (RunnablePassthrough + RunnableBranch)

Separate from the main agent loop, `workflow.py` implements a conditional chain:

1. A classifier chain labels the input as `complaint` or `praise`.
2. `RunnablePassthrough.assign` accumulates that label into the state as a
   `category` field, without discarding the original input.
3. `RunnableBranch` routes to one of two downstream chains based on `category`:
   an apologetic reply chain (complaint) or a cheerful thank-you chain (praise).

Both routes were exercised:

- **Input A** ("My order arrived broken and nobody has helped me!") → classified
  as `complaint` → apologetic reply chain.
- **Input B** ("Your service was amazing and delivery was super fast, thank you!")
  → classified as `praise` → thank-you reply chain.

## API key security

The API key is loaded from the `GEMINI_API_KEY` environment variable via a `.env`
file that is excluded by `.gitignore`. No key appears anywhere in the repository.