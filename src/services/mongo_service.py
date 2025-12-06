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

def get_collection(collection_name: str = "inputs"):
    """
    Get MongoDB collection instance.
    
    Args:
        collection_name: Name of the collection. Defaults to "inputs".
    
    Returns:
        MongoDB collection instance or None if connection fails.
    """
    global _client
    
    try:
        if _client is None:
            _client = MongoClient(settings.mongodb_uri)
        
        db = _client[settings.mongodb_db_name]
        collection = db[collection_name]
        logger.info(f"Connected to MongoDB collection '{collection_name}' successfully")
        return collection
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


def save_url_with_topic(url: str, topic: str) -> None:
    """
    Save URL with topic to MongoDB with timestamp and error handling.
    
    Args:
        url (str): The URL to save.
        topic (str): The topic to save.
    """
    collection = get_collection()
    try:
        if collection is not None:
            document = {
                "url": url,
                "topic": topic,
                "timestamp": datetime.utcnow(),
                "created_at": datetime.utcnow().isoformat()
            }
            collection.insert_one(document)
            logger.info(f"URL {url} with topic {topic} saved to MongoDB at {document['created_at']}")
        else:
            logger.warning("MongoDB collection not available, skipping save")
            # Don't raise error if collection is not available, just log warning
    except Exception as e:
        logger.error(f"MongoDB insertion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"MongoDB insertion failed: {e}")


def save_relevance_data(topic: str, details: str, url: str, core_text: str, date: datetime = None) -> None:
    """
    Save relevance data to MongoDB (Topic and data).
    Saves topic, details, url, core_text, and date for each URL/core_text combination.
    
    Args:
        topic (str): The topic.
        details (str): The details.
        url (str): The URL.
        core_text (str): The core text extracted from the URL.
        date (datetime, optional): The date. Defaults to current UTC time.
    """
    # Use "Topic and data" collection as specified
    collection = get_collection("Topic and data")
    if collection is None:
        logger.warning("MongoDB collection not available, skipping save")
        return
    
    if date is None:
        date = datetime.utcnow()
    
    try:
        document = {
            "topic": topic,
            "details": details,
            "url": url,
            "core_text": core_text,
            "date": date,
            "timestamp": datetime.utcnow(),
            "created_at": datetime.utcnow().isoformat()
        }
        collection.insert_one(document)
        logger.info(f"Relevance data saved to 'Topic and data' collection: topic='{topic}', URL: {url}")
    except Exception as e:
        logger.error(f"MongoDB insertion failed for relevance data: {e}", exc_info=True)
        # Don't raise exception, just log error to avoid breaking the workflow