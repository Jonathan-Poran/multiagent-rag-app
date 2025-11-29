import os
from dotenv import load_dotenv
from pymongo import MongoClient, errors

load_dotenv()

_client = None
_collection = None

def get_collection():
    global _client, _collection

    if _collection is not None:
        return _collection

    try:
        _client = MongoClient(os.getenv("MONGODB_URI"))
        db = _client[os.getenv("MONGODB_DB_NAME")]
        _collection = db["inputs"]
        print("Connected to MongoDB")
        return _collection
    except Exception as e:
        print("MongoDB connection failed:", e)
        return None