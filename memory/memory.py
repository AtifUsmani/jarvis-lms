from mem0 import Memory
from langchain_openai import ChatOpenAI
import yaml

# Load the YAML config
with open(r"C:\path\to\jarvis\config.yaml", "r") as file:  # change this to absolute location of file
    config = yaml.safe_load(file)

model = ChatOpenAI(
    base_url=config["LLM"]["BASE_URL"],
    api_key=config["LLM"]["API_KEY"],
    model=config["LLM"]["MODEL_NAME"],
    streaming=False,
)

memory_config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "test",
            "host": config["DB"]["QDRANT_HOST"],
            "port": 6333,
            "embedding_model_dims": config["DB"]["EMBEDDINGMODELDIMS"],
            # Change this according to your local model's dimensions
        },
    },
    "llm": {
        "provider": "langchain",
        "config": {
            "model": model
        },
    },
    "embedder": {
        "provider": "lmstudio",
        "config": {
            "model": "text-embedding-nomic-embed-text-v1.5",
            "lmstudio_base_url": config["LLM"]["BASE_URL"],  # default LM Studio API URL
            # "lmstudio_response_format": {"type": "json_schema", "json_schema": {"type": "object", "schema": {}}},
        }
    },
}

# Initialize Memory with the configuration
m = Memory.from_config(memory_config)

def search_memories(query: str) -> str:
    try:
        # Get related memories from your memory system
        related_memories = m.search(query=query, user_id=config["USER_ID"])

        # Sort by score descending
        sorted_results = sorted(related_memories["results"], key=lambda x: x["score"], reverse=True)

        # Format all results into a single string
        formatted = "\n".join([f"Memory: {item['memory']} | Score: {item['score']}" for item in sorted_results])

        return formatted if formatted else "No related memories found."

    except Exception as e:
        return f"An error occurred: {e}"

def get_all_memories(_: str) -> str:
    try:
        all_user_memories = m.get_all(user_id=config["USER_ID"])

        # Collect all memories in a list
        memories = [item["memory"] for item in all_user_memories["results"]]

        # Join them into a single string
        return "\n".join(memories)

    except Exception as e:
        return f"An error occurred: {e}"

def add_memory(query: str) -> str:
    try:
        m.add(query, user_id=config["USER_ID"])
        return "Memory added!"
    except Exception as e:
        return f"An error occurred: {e}"
