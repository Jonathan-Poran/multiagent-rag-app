from datetime import datetime, timedelta
from langchain_core.messages import AIMessage
from src.services.mongo_service import get_collection
from src.graph.consts import FIND_URL
from src.config.logger import get_logger
from src.dto.graph_dto import MessageGraph

logger = get_logger("CheckRecentURLs")

LOOKBACK_DAYS = 90

def check_db_node(state: MessageGraph) -> dict:
    """
    Check if topic exists in the DB (Topic and data).
    Sets 'topic_in_db' True/False and stores db_content and date if found.
    Combines all core_text from multiple URLs into a single content string.
    """
    from src.services.mongo_service import get_collection
    
    topic = state.get("topic", "")
    collection = get_collection("Topic and data")
    if not topic or collection is None:
        return {"topic_in_db": False}

    # Check for existing records in last 3 months
    now = datetime.utcnow()
    cutoff = now - timedelta(days=LOOKBACK_DAYS)

    # Find all documents for this topic within the lookback period
    docs = list(collection.find({"topic": topic, "date": {"$gte": cutoff}}).sort("date", -1))
    
    if docs:
        # Combine all core_text from multiple URLs into a single content string
        core_texts = [doc.get("core_text", "") for doc in docs if doc.get("core_text")]
        combined_content = "\n\n".join(core_texts) if core_texts else ""
        
        # Get the most recent date
        most_recent_date = docs[0].get("date")
        
        if combined_content:
            logger.info(f"Found {len(docs)} existing records for topic '{topic}' in DB")
            logger.info(f"Setting topic_in_db=True, db_content length: {len(combined_content)} chars, date: {most_recent_date}")
            return {
                "topic_in_db": True,
                "db_content": combined_content,
                "date": most_recent_date
            }
    
    logger.info(f"No existing records found for topic '{topic}' in DB")
    return {"topic_in_db": False}
