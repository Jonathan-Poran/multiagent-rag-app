import os
from dotenv import load_dotenv
from pymongo import MongoClient, errors
from server.config.logger import get_logger

load_dotenv()

logger = get_logger("mongo")

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
        logger.info("Connected to MongoDB successfully")
        return _collection
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}", exc_info=True)
        return None