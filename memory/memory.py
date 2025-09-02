import chromadb
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
from uuid import uuid4
import yaml

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Init embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# ChromaDB setup
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection("memory")

# MongoDB setup
mongo_client = MongoClient(config["DB"]["MONGO_URI"])
mongo_db = mongo_client["jarvis"]
profile_collection = mongo_db["profile"]

# ----- ChromaDB Memory -----
def save_to_vector_memory(user_input, assistant_output):
    text = f"User: {user_input}\nAssistant: {assistant_output}"
    embedding = embedder.encode(text).tolist()
    collection.add(documents=[text], embeddings=[embedding], ids=[str(uuid4())])

def retrieve_similar_memories(query, top_k=3):
    embedding = embedder.encode(query).tolist()
    results = collection.query(query_embeddings=[embedding], n_results=top_k)
    return results["documents"][0] if results["documents"] else []

# ----- MongoDB Profile Memory -----
def save_user_profile(key, value):
    profile_collection.update_one({"_id": "user"}, {"$set": {key: value}}, upsert=True)

def get_user_profile(key):
    doc = profile_collection.find_one({"_id": "user"})
    return doc.get(key) if doc else None
