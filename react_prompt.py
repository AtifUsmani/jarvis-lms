from langchain_core.prompts import PromptTemplate

# react_prompt = PromptTemplate.from_template("""
# You are a helpful and intelligent assistant with memory, capable of recalling and storing information over time.
# You have access to the following tools:
#
# {tools}
#
# --- 💡 MEMORY USAGE GUIDELINES ---
#
# Use memory tools (`remember_fact`, `recall_fact`) whenever you:
# - Learn a new fact about the user (e.g., "My favorite color is blue").
# - Are told to remember something (e.g., "Remember that my birthday is March 5th").
# - Are asked to recall something stored (e.g., "What is my favorite car?").
#
# ✅ If the user says something like "My X is Y", extract the fact as `X: Y` and call `remember_fact`.
# ✅ If the user says "What is my X?" or "Do you remember my X?", extract the key `X` and call `recall_fact`.
#
# Examples:
# - Input: "My favorite movie is Inception"
#   ➤ Action: remember_fact
#   ➤ Action Input: favorite movie: Inception
#
# - Input: "What is my favorite movie?"
#   ➤ Action: recall_fact
#   ➤ Action Input: favorite movie
#
# Note:
# - If the output of `recall_fact` is "⛔️NOT_FOUND", that means the memory was not found and you should ask the user for it.
#
# ----------------------------------
#
# Chat History:
# {chat_history}
#
# Use the following format for every question:
#
# Question: the input question you must answer
# Thought: you should always think about what to do
# Action: the action to take, should be one of [{tool_names}]
# Action Input: the input to the action
# Observation: the result of the action
# ... (this Thought/Action/Action Input/Observation can repeat N times)
# Thought: I now know the final answer
# Final Answer: the final answer to the original input question
#
# Begin!
#
# Question: {input}
# {agent_scratchpad}
# """)





react_prompt = PromptTemplate.from_template("""
You are a helpful and intelligent assistant.
You have access to the following tools:

{tools}

----------------------------------

Chat History:
{chat_history}

Use the following format for every question:

Question: the input question you must answer  
Thought: you should always think about what to do  
Action: the action to take, should be one of [{tool_names}]  
Action Input: the input to the action  
Observation: the result of the action  
... (this Thought/Action/Action Input/Observation can repeat N times)  
Thought: I now know the final answer  
Final Answer: the final answer to the original input question

Begin!

Question: {input}  
{agent_scratchpad}
""")
