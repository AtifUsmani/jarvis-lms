from langchain_core.prompts import PromptTemplate

# react_prompt = PromptTemplate.from_template("""
# You are a helpful and intelligent assistant.
# You have access to the following tools:
#
# {tools}
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

# react_prompt = PromptTemplate.from_template("""
# You are a helpful and intelligent assistant.
# You have access to the following tools:
#
# {tools}
#
# ----------------------------------
#
# Chat History:
# {chat_history}
#
# Rules for reasoning:
# - Always think carefully before acting.
# - If the user mentions any personal fact (like their name, preferences, devices, car model, or projects), store it using your memory tools immediately.
# - If you need context or prior knowledge, use memory retrieval tools before answering.
# - Always store facts you learn and retrieve relevant facts whenever necessary.
# - Do not guess; base your answers on observations or memory.
#
# Use the following format for every question:
#
# Question: the input question you must answer
# Thought: reason about what to do next
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

Rules for reasoning:
- If the user asks anything about him, use memory retrieval tools before answering.
- Always think carefully before acting.
- If the user mentions any personal fact (like their name, preferences, devices, car model, or projects), store it using your memory tools immediately.
- If you need context or prior knowledge, use memory retrieval tools before answering.
- Always store facts you learn and retrieve relevant facts whenever necessary.
- Do not guess; base your answers on observations or memory.

Use the following format for every question:

Question: the input question you must answer  
Thought: reason about what to do next
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action  
Observation: the result of the action  
... (this Thought/Action/Action Input/Observation can repeat N times)  
Thought: I now know the final answer  
Final Answer: the final answer to the original input question

Begin!

# Startup step
Thought: I should load all memories first
Action: retrieve_all_memories
Action Input:
Observation: {{all_memories}}   # <- escaped, so it won't cause KeyError

Question: {input}  
{agent_scratchpad}
""")

# - On startup, retrieve all stored memories so you know all facts about the user.