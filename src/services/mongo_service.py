import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient, errors
from bson import ObjectId
from fastapi import HTTPException
from src.config.logger import get_logger
from src.config.settings import settings

load_dotenv()

logger = get_logger("Mongo")

_client = None
_collection = None

def get_collection():
    global _client, _collection

    if _collection is not None:
        return _collection

    try:
        _client = MongoClient(settings.mongodb_uri)
        db = _client[settings.mongodb_db_name]
        _collection = db["inputs"]
        logger.info("Connected to MongoDB successfully")
        return _collection
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}", exc_info=True)
        return None


def generate_conversation_id() -> str:
    """
    Generate a new unique conversation ID.
    
    Returns:
        str: A new unique conversation ID.
    """
    conversation_id = str(ObjectId())
    logger.info(f"Generated new conversation ID: {conversation_id}")
    return conversation_id


def save_user_input(user_text: str) -> None:
    """
    Save user input to MongoDB with timestamp and error handling.
    
    Args:
        user_text (str): The user input text to save.
    
    Raises:
        HTTPException: If MongoDB insertion fails.
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
        else:
            logger.warning("MongoDB collection not available, skipping save")
            # Don't raise error if collection is not available, just log warning
    except Exception as e:
        logger.error(f"MongoDB insertion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"MongoDB insertion failed: {e}")