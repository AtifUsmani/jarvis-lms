from pathlib import Path
import requests
import os
# import chromadb
import datetime
import json
import psutil
import json
from pathlib import Path
from memory.memory import get_user_profile, save_user_profile
from pymongo import MongoClient
import yaml

chat_history = []
conversation_log = []

# Initialize ChromaDB
# chroma_client = chromadb.PersistentClient(path="./chroma_memory")
# collection = chroma_client.get_or_create_collection("conversation_memory")

# Load environment variables from .env file

# Load the YAML config
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Load Home Assistant configuration from env vars
HASS_URL = config["HA"]["HASS_URL"]
HASS_TOKEN = config["HA"]["HASS_TOKEN"]
LIGHT_ENTITY = config["HA_TOOLS"]["LIGHT_ENTITY"]
TEMPERATURE_ENTITY = config["HA_TOOLS"]["TEMPERATURE_ENTITY"]
HUMIDITY_ENTITY = config["HA_TOOLS"]["HUMIDITY_ENTITY"]
AMBIENT_LIGHT_ENTITY = config["HA_TOOLS"]["AMBIENT_LIGHT_ENTITY"]
SOUND_LEVEL_ENTITY = config["HA_TOOLS"]["SOUND_LEVEL_ENTITY"]
HEADERS = {"Authorization": f"Bearer {HASS_TOKEN}", "Content-Type": "application/json"}

# def retrieve_memory(query: str, top_k: int = 5):
#     """
#     Searches ChromaDB for the most relevant past memories.
#     """
#     results = collection.query(
#         query_texts=[query],
#         n_results=top_k
#     )
#     return [doc for doc in results["documents"][0]] if results["documents"] else []
#
# def memory_lookup(query: str):
#     """Retrieves relevant memory from ChromaDB."""
#     return retrieve_memory(query)

def get_date_time():
    """Returns the current date and time."""
    now = datetime.datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S")
    }

# MongoDB setup
mongo_client = MongoClient(config["DB"]["MONGO_URI"])
mongo_db = mongo_client["jarvis"]
profile_collection = mongo_db["profile"]

# ✅ Helper: Normalize key
def normalize_key(key: str) -> str:
    return key.strip().lower().replace(" ", "_")

def remember_fact(input_str: str) -> str:
    try:
        key, value = map(str.strip, input_str.split(":", 1))
        if not value or value.lower() == "none":
            return "⚠️ I can't store an empty value. Please provide a valid fact."

        norm_key = normalize_key(key)
        profile_collection.update_one(
            {"_id": "user"},
            {"$set": {norm_key: value}},
            upsert=True
        )
        return f"I'll remember that your {key} is {value}."
    except Exception as e:
        return f"⚠️ Failed to store the fact: {e}"

def recall_fact(key: str) -> str:
    norm_key = normalize_key(key)
    doc = profile_collection.find_one({"_id": "user"})

    value = doc.get(norm_key) if doc else None
    if value is None:
        return "⛔️NOT_FOUND"
    return value


def extract_from_json():
    """Retrieves data from a json file."""
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    return data

def get_system_resources():
    """Provides system information such as CPU, RAM, and disk usage."""
    return {
        "cpu_usage": f"{psutil.cpu_percent(interval=1)}%",
        "ram_usage": f"{psutil.virtual_memory().percent}%",
        "disk_usage": f"{psutil.disk_usage('/').percent}%"
    }

def now():
    return datetime.datetime.now().isoformat()

CONVO_FILE = Path("conversation.json")

def load_conversation(CONVO_FILE=CONVO_FILE):
    if os.path.exists(CONVO_FILE):
        with open(CONVO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_conversation(user_input, bot_reply, user_id=None, bot_id=None, context=None, tools_used=None):
    if CONVO_FILE.exists():
        with open(CONVO_FILE, "r", encoding="utf-8") as f:
            conversations = json.load(f)
    else:
        conversations = []

    conversations.append({
        "timestamp": datetime.datetime.now().isoformat(),
        "user": user_input,
        "user_id": user_id,
        "assistant": bot_reply,
        "assistant_id": bot_id,
        "memory_context": context,
        "tools_used": tools_used
    })

    with open(CONVO_FILE, "w", encoding="utf-8") as f:
        json.dump(conversations, f, indent=2, ensure_ascii=False)


def create_file(name: str, content: str):
    """Create a file with the given name and content. Can be used for making python scripts and CSV files."""
    dest_path = Path(name)
    if dest_path.exists():
        return "Error: File already exists."
    try:
        dest_path.write_text(content, encoding="utf-8")
    except Exception as exc:
        return "Error: {exc!r}"
    return "File created."

def get_temperature(_: str) -> str:
    """Retrieves the current room temperature from Home Assistant."""
    url = f"{HASS_URL}/api/states/{TEMPERATURE_ENTITY}"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            temperature = data.get("state", "unknown")
            return f"The room temperature is {temperature}°C."
        else:
            return f"Failed to retrieve temperature: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error retrieving temperature: {str(e)}"

def get_humidity(_: str) -> str:
    """Retrieves the current room humidity from Home Assistant."""
    url = f"{HASS_URL}/api/states/{HUMIDITY_ENTITY}"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            humidity = data.get("state", "unknown")
            return f"The room humidity is {humidity}%."
        else:
            return f"Failed to retrieve humidity: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error retrieving humidity: {str(e)}"

def get_ambient_light():
    url = f"{HASS_URL}/api/states/{AMBIENT_LIGHT_ENTITY}"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            ambient_light = data.get("state", "unknown")
            return f"The ambient light level is {ambient_light}."
        else:
            return f"Failed to retrieve ambient light: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error retrieving ambient light: {str(e)}"

def get_sound_level():
    url = f"{HASS_URL}/api/states/{SOUND_LEVEL_ENTITY}"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            sound_level = data.get("state", "unknown")
            return f"The sound level in the room is {sound_level}."
        else:
            return f"Failed to retrieve sound level: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error retrieving sound level: {str(e)}"

def toggle_wled():
    """Toggles the WLED light on or off using Home Assistant."""
    url = f"{HASS_URL}api/services/light/toggle"
    payload = {"entity_id": LIGHT_ENTITY}

    print(f"🔍 DEBUG: Sending request to {url} with payload: {payload}")
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        print(f"🔍 DEBUG: Response Code: {response.status_code}, Response: {response.text}")
        
        if response.status_code == 200:
            return "WLED toggled successfully!"
        else:
            return f"Failed to toggle WLED: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error toggling WLED: {str(e)}"


def set_wled_effect(effect_name, brightness=None, color=None):
    """
    Set the WLED effect, optionally also setting brightness and RGB color.
    - effect_name: Name of the effect (as string, must be in the effect_list).
    - brightness: Integer (0-255)
    - color: Hex string like "#FFAA00"
    """
    try:
        data = {
            "entity_id": LIGHT_ENTITY,
            "effect": effect_name
        }

        if brightness is not None:
            data["brightness"] = brightness

        if color:
            if not color.startswith("#") or len(color) != 7:
                return "Invalid color format. Use hex format, e.g., #FFAA00."
            data["rgb_color"] = [
                int(color[1:3], 16),
                int(color[3:5], 16),
                int(color[5:7], 16)
            ]

        response = requests.post(
            f"{HASS_URL}services/light/turn_on",
            headers=HEADERS,
            json=data
        )

        if response.status_code == 200:
            return f"WLED effect set to '{effect_name}'" + (
                f", brightness {brightness}" if brightness else ""
            ) + (f", color {color}" if color else "") + "."
        else:
            return f"Failed to update WLED: {response.text}"
    except Exception as e:
        return f"Error setting WLED effect: {str(e)}"

def get_light_state():
    """Checks the current state of the WLED light (on/off)."""
    url = f"{HASS_URL}api/states/{LIGHT_ENTITY}"

    print(f"🔍 DEBUG: Sending GET request to {url}")
    
    try:
        response = requests.get(url, headers=HEADERS)
        # print(f"🔍 DEBUG: Response Code: {response.status_code}, Response: {response.text}")

        if response.status_code == 200:
            data = response.json()
            state = data.get("state", "unknown").lower()
            
            if state == "on":
                return "The lights are currently ON."
            elif state == "off":
                return "The lights are currently OFF."
            else:
                return f"The light's state is {state}."
        else:
            return f"Failed to retrieve light state: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error retrieving light state: {str(e)}"

def web_search(query: str):
    """
    Perform a web search and return a brief summary of results based on a searched query.
    """
    try:
        # Using DuckDuckGo Instant Answer API (no key needed, basic info)
        response = requests.get(
            f"https://api.duckduckgo.com/?q={query}&format=json&no_redirect=1&no_html=1"
        )
        data = response.json()
        abstract = data.get("AbstractText") or "No summary found for this topic."
        return f"Web Search Result for '{query}': {abstract}"
    except Exception as e:
        return f"Web search failed: {str(e)}"