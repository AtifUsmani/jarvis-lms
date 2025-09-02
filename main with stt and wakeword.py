# main.py
import re
from langchain.agents import create_react_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from tools.tools_list import tools
from react_prompt import react_prompt
from tts.tts import speak
from tools.tools import recall_fact
from memory.memory_utils import auto_remember_from_input
from memory.memory import save_to_vector_memory, retrieve_similar_memories
import yaml
from stt.test_stt import record_and_transcribe
from faster_whisper import WhisperModel
from stt.wakeword import wait_for_wake_word_vosk

USE_STT = True

# ✅ Toggle to switch between memory systems
USE_LANGCHAIN_MEMORY = True  # 🔁 Switch between LangChain or Custom memory

# ✅ Short-term memory using LangChain's ConversationBufferWindowMemory
short_term_memory = ConversationBufferWindowMemory(return_messages=True, memory_key="chat_history")

# Load the YAML config
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# ✅ Optional LangChain Vector Memory
if USE_LANGCHAIN_MEMORY:
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain.memory import VectorStoreRetrieverMemory

    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(
        collection_name="jarvis_memories",
        embedding_function=embedding_model,
        persist_directory="./chroma_db"
    )
    long_term_memory = VectorStoreRetrieverMemory(
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        memory_key="relevant_memories"
    )

# ✅ Set up LM Studio model (Qwen or any compatible)
model = ChatOpenAI(
    base_url=config["LLM"]["BASE_URL"],
    api_key=config["LLM"]["API_KEY"],
    model=config["LLM"]["MODEL_NAME"],
    streaming=True,
)

# ✅ Create the ReAct agent
agent = create_react_agent(
    llm=model,
    tools=tools,
    prompt=react_prompt
)

# ✅ Agent Executor with short-term memory
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    streaming=True,
    handle_parsing_errors=True,
    memory=short_term_memory,
)

# ✅ Stream and speak logic
def stream_and_speak(user_input):
    print("\nAssistant: ", end='', flush=True)

    # Auto-remember input
    auto_remember_from_input(user_input)

    # 🔁 Retrieve long-term memory
    if USE_LANGCHAIN_MEMORY:
        try:
            memory_contexts = long_term_memory.load_memory_variables({"input": user_input}).get("relevant_memories", "")
            if memory_contexts:
                print("\n[LangChain Memory Recall]:")
                print(memory_contexts.strip())
                print()
        except Exception as e:
            print(f"[LangChain Memory Error]: {e}")
    else:
        memory_contexts = retrieve_similar_memories(user_input)
        if memory_contexts:
            print("\n[Custom Memory Recall]:")
            for m in memory_contexts:
                print(f" - {m}")
            print()

    # Auto-recall structured facts
    recall_match = re.search(r"(?:what|which) is my (?P<key>[\w\s]+)[?]?", user_input, re.IGNORECASE)
    if recall_match:
        key = recall_match.group("key").strip().lower()
        try:
            value = recall_fact(key)
            if value:
                print(f"[Auto-Recall] You told me your {key} is {value}.")
        except Exception:
            pass

    # Get full LLM output in one go
    full_output = ""
    for chunk in agent_executor.stream({"input": user_input}):
        if isinstance(chunk, dict) and "output" in chunk:
            token = chunk["output"]
            print(token, end='', flush=True)
            full_output += token

    print()  # newline after printing

    # Speak the entire output at once
    if full_output.strip():
        speak(full_output.strip(), filename="llm_response.wav")

    # Save to memory
    if USE_LANGCHAIN_MEMORY:
        try:
            long_term_memory.save_context({"input": user_input}, {"output": full_output.strip()})
        except Exception as e:
            print(f"[Memory Save Error] {e}")
    else:
        save_to_vector_memory(user_input, full_output.strip())

def main():
    model = WhisperModel("base.en", device="cpu", compute_type="float32")

    while True:
        # ------------------------------
        # Wake word detection (Vosk)
        # ------------------------------
        wait_for_wake_word_vosk(model_path=r"stt/vosk-model-small-en-us-0.15", wake_word="jarvis")
        print("Jarvis activated! Listening for command...")

        # ------------------------------
        # Record & Transcribe
        # ------------------------------
        if USE_STT:
            result = record_and_transcribe(model)
            print(f"Got: '{result}'")
            user_input = result.strip()
        else:
            user_input = input("\nYou: ").strip()

        # ------------------------------
        # Exit handling
        # ------------------------------
        if user_input.lower() in ("exit", "quit"):
            if USE_LANGCHAIN_MEMORY:
                vectorstore.persist()
            break

        # ------------------------------
        # Process command
        # ------------------------------
        stream_and_speak(user_input)

if __name__ == "__main__":
    main()
