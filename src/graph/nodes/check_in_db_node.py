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
    Check if topic exists in the DB (Contemporary history).
    Sets 'topic_in_db' True/False
    """
    topic = state.get("topic", "")
    collection = get_collection()
    if not topic or collection is None:
        return {"topic_in_db": False, "messages": []}

    # Check for existing records in last 3 months
    now = datetime.utcnow()
    cutoff = now - timedelta(days=LOOKBACK_DAYS)

    doc = collection.find_one({"topic": topic, "date": {"$gte": cutoff}})
    if doc:
        state["topic_in_db"] = True
        state["db_content"] = doc.get("content", "")
    else:
        state["topic_in_db"] = False

    return {"topic_in_db": state["topic_in_db"], "messages": []}
