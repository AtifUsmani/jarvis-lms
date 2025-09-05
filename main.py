# main.py
from langchain.agents import create_react_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from tools.tools_list import tools
from react_prompt import react_prompt
from tts.tts import speak
import yaml
from stt.test_stt import record_and_transcribe, push_to_talk
from faster_whisper import WhisperModel
from stt.wakeword import wait_for_wake_word_vosk

USE_STT = False
USE_TTS = False
USE_WAKEWORD = False

# ✅ Short-term memory using LangChain's ConversationBufferWindowMemory
short_term_memory = ConversationBufferWindowMemory(return_messages=True, memory_key="chat_history", output_key="output")

# Load the YAML config
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# ✅ Set up LM Studio model (Qwen or any compatible)
model = ChatOpenAI(
    base_url=config["LLM"]["BASE_URL"],
    api_key=config["LLM"]["API_KEY"],
    model=config["LLM"]["MODEL_NAME"],
    streaming=True,
    temperature=0.6,
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

    # Get full LLM output in one go
    full_output = ""
    for chunk in agent_executor.stream({"input": user_input}):
        if isinstance(chunk, dict) and "output" in chunk:
            token = chunk["output"]
            print(token, end='', flush=True)
            full_output += token

    print()  # newline after printing

    if USE_TTS:
        # Speak the entire output at once
        if full_output.strip():
            try:
                speak(full_output.strip(), filename="llm_response.wav")
            except Exception as e:
                print(e)


def main():
    global user_input
    model = WhisperModel("base.en", device="cpu", compute_type="float32")

    while True:
        # ------------------------------
        # Wake word detection (Vosk)
        # ------------------------------
        if USE_WAKEWORD:
            try:
                wait_for_wake_word_vosk(model_path=r"stt/vosk-model-small-en-us-0.15", wake_word="jarvis")
                print("Jarvis activated! Listening for command...")
            except Exception as e:
                print(e)

        # ------------------------------
        # Record & Transcribe
        # ------------------------------
        if USE_WAKEWORD and USE_STT:
            try:
                result = record_and_transcribe(model)
                print(f"Got: '{result}'")
                user_input = result.strip()
            except Exception as e:
                print(e)

        elif USE_STT and not USE_WAKEWORD:
            try:
                result = push_to_talk(model)
                print(f"Got: '{result}'")
                user_input = result.strip()
            except Exception as e:
                print(e)
        else:
            user_input = input("\nYou: ").strip()

        # ------------------------------
        # Exit handling
        # ------------------------------
        if user_input.lower() in ("exit", "quit"):
            break

        # ------------------------------
        # Process command
        # ------------------------------
        stream_and_speak(user_input)

if __name__ == "__main__":
    main()
