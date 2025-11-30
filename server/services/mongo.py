import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient, errors
from server.config.logger import get_logger

load_dotenv()

logger = get_logger("Mongo")

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


def save_user_input(user_text: str) -> bool:
    """
    Save user input to MongoDB with timestamp.
    
    Args:
        user_text (str): The user input text to save.
    
    Returns:
        bool: True if saved successfully, False if collection not available.
    
    Raises:
        Exception: If insertion fails.
    """
    collection = get_collection()
    
    try:
        if collection is not None:
            document = {
                "input": user_text,
                "timestamp": datetime.utcnow(),
                "created_at": datetime.utcnow().isoformat()
            }
            collection.insert_one(document)
            logger.info(f"User input saved to MongoDB at {document['created_at']}")
            return True
        else:
            logger.warning("MongoDB collection not available, skipping save")
            return False
    except Exception as e:
        logger.error(f"MongoDB insertion failed: {e}", exc_info=True)
        raise