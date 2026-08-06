import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableBranch
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0,
)

# ============================================================
# A conditional workflow, SEPARATE from the main agent loop.
#
# Step 1: classify the user's message as "complaint" or "praise".
# Step 2: RunnablePassthrough.assign accumulates that classification
#         into the state alongside the original input.
# Step 3: RunnableBranch routes to one of two different reply chains
#         depending on the classification.
# ============================================================

# --- Step 1: a classifier chain ---
classify_prompt = ChatPromptTemplate.from_messages([
    ("system", "Classify the user's message as exactly one word: "
               "'complaint' or 'praise'. Reply with only that word, lowercase."),
    ("human", "{input}"),
])
classifier = classify_prompt | llm | StrOutputParser()

# --- Two downstream chains to route between ---
complaint_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "You are an apologetic support agent. Write a short, "
                   "empathetic apology addressing the user's complaint."),
        ("human", "{input}"),
    ]) | llm | StrOutputParser()
)

praise_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "You are a cheerful support agent. Write a short, warm "
                   "thank-you responding to the user's praise."),
        ("human", "{input}"),
    ]) | llm | StrOutputParser()
)

# --- Step 2: accumulate state — keep 'input', add 'category' ---
# RunnablePassthrough.assign runs the classifier and stores its result
# in a new 'category' key, WITHOUT losing the original 'input'.
with_category = RunnablePassthrough.assign(
    category=lambda x: classifier.invoke({"input": x["input"]}).strip().lower()
)

# --- Step 3: RunnableBranch routes based on the accumulated 'category' ---
branch = RunnableBranch(
    (lambda x: "complaint" in x["category"], complaint_chain),
    praise_chain,   # default route (else)
)

# Full workflow: accumulate category, then branch.
workflow = with_category | branch


if __name__ == "__main__":
    print("=" * 60)
    print("CONDITIONAL WORKFLOW (RunnablePassthrough + RunnableBranch)")
    print("=" * 60)

    # Input A — should trigger the COMPLAINT route
    input_a = "My order arrived broken and nobody has helped me!"
    print(f"\n[Input A] {input_a}")
    cat_a = with_category.invoke({"input": input_a})
    print(f"  Classified as: {cat_a['category']}")
    print(f"  Reply: {workflow.invoke({'input': input_a})}")

    # Input B — should trigger the PRAISE route
    input_b = "Your service was amazing and delivery was super fast, thank you!"
    print(f"\n[Input B] {input_b}")
    cat_b = with_category.invoke({"input": input_b})
    print(f"  Classified as: {cat_b['category']}")
    print(f"  Reply: {workflow.invoke({'input': input_b})}")


    