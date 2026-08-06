import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from tools import get_random_advice, lookup_order_status

load_dotenv()


def clean_output(output):
    """LangChain 1.x may return output as a list of content blocks.
    Extract just the text for clean printing."""
    if isinstance(output, list):
        return " ".join(b.get("text", "") for b in output if isinstance(b, dict))
    return output


# ------------------------------------------------------------
# The LLM that powers the agent's reasoning and tool-selection.
# ------------------------------------------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0,
)

tools = [get_random_advice, lookup_order_status]

# ------------------------------------------------------------
# Prompt scaffold. The MessagesPlaceholder blocks let us inject
# conversation history (for memory) and the agent's scratchpad.
# ------------------------------------------------------------
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful customer-service assistant. "
               "Use the available tools when they are relevant to the user's request."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Build the tool-calling agent and its executor (bounded iterations).
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=False,
    max_iterations=5,                 # bounded so the loop cannot run away
    return_intermediate_steps=True,   # so we can inspect tool calls
)


def log_tool_calls(result):
    """Extract the {tool, arguments} decision from LangChain's OWN native
    mechanism (intermediate_steps), not by parsing raw text.
    Each step is (AgentAction, observation)."""
    steps = result.get("intermediate_steps", [])
    if not steps:
        print("   (no tools were called)")
    for action, observation in steps:
        decision = {"tool": action.tool, "arguments": action.tool_input}
        print("   TOOL CALL:", json.dumps(decision))
        print("   RESULT   :", observation)


# ============================================================
# DEMO 1 & 2: two-turn conversation showing MEMORY.
# Turn 1 looks up an order. Turn 2 refers to "that order" without
# repeating the ID — the agent must reuse turn-1 info.
# ============================================================
print("=" * 60)
print("MEMORY DEMO (2 turns)")
print("=" * 60)

chat_history = []

# --- Turn 1 ---
q1 = "What is the status of order A101?"
print(f"\n[Turn 1] User: {q1}")
r1 = agent_executor.invoke({"input": q1, "chat_history": chat_history})
print(f"[Turn 1] Agent: {clean_output(r1['output'])}")
log_tool_calls(r1)

# Save this turn into history so turn 2 has context
chat_history.append(HumanMessage(content=q1))
chat_history.append(AIMessage(content=clean_output(r1["output"])))

# --- Turn 2 (refers back without repeating the order ID) ---
q2 = "Is that order going to arrive soon?"
print(f"\n[Turn 2] User: {q2}")
r2 = agent_executor.invoke({"input": q2, "chat_history": chat_history})
print(f"[Turn 2] Agent: {clean_output(r2['output'])}")
log_tool_calls(r2)

# ============================================================
# DEMO 3: a third distinct query exercising the OTHER tool.
# ============================================================
print("\n" + "=" * 60)
print("THIRD QUERY (advice tool)")
print("=" * 60)

q3 = "I'm feeling stressed about work. Can you give me a piece of advice?"
print(f"\n[Query 3] User: {q3}")
r3 = agent_executor.invoke({"input": q3, "chat_history": []})
print(f"[Query 3] Agent: {clean_output(r3['output'])}")
log_tool_calls(r3)


