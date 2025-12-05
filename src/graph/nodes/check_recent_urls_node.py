from datetime import datetime, timedelta
from langchain_core.messages import AIMessage
from src.services.mongo_service import get_collection
from src.graph.consts import FIND_URL
from src.config.logger import get_logger

logger = get_logger("CheckRecentURLs")

# Lookback period: last 3 months
LOOKBACK_DAYS = 90

def check_recent_urls_node(state: dict) -> dict:
    """
    Node executed after topic extraction.
    Checks MongoDB for URLs about the topic in the last 3 months.
    If URLs exist, responds to the user asking confirmation.
    If no URLs, automatically continues to FIND_URL.
    """
    topic = state.get("topic")
    if not topic:
        logger.error("Topic not found in state, graph isnt configured correctly")
        return {
            "messages": [AIMessage(content="Topic not found in state, graph isnt configured correctly")],
            "next": FIND_URL
        }

    collection = get_collection()
    if collection is None:
        logger.error("Database unavailable, cannot check URLs.")
        return {
            "messages": [AIMessage(content="Database unavailable, cannot check URLs.")],
            "next": FIND_URL
        }

    now = datetime.utcnow()
    cutoff = now - timedelta(days=LOOKBACK_DAYS)

    # Query URLs for the topic
    docs = list(collection.find({
        "topic": topic,
        "urls": {"$exists": True, "$ne": []}
    }))

    # Collect recent URLs
    recent_urls = []
    for doc in docs:
        for url_info in doc.get("urls", []):
            date_str = url_info.get("date")
            try:
                url_date = datetime.fromisoformat(date_str)
            except Exception as e:
                logger.error(f"Could not parse date {date_str}: {e}")
                continue
            if url_date >= cutoff:
                recent_urls.append((url_info["url"], url_date))

    if not recent_urls:
        # No recent URLs → automatically go to FIND_URL
        logger.debug(f"No recent URLs found for topic: {topic}, automatically going to FIND_URL")
        return {"messages": [], "next": FIND_URL}

    # Sort URLs by date
    recent_urls.sort(key=lambda x: x[1])
    oldest = recent_urls[0][1].strftime("%Y-%m-%d")
    newest = recent_urls[-1][1].strftime("%Y-%m-%d")
    url_list = "\n".join([url for url, _ in recent_urls])

    msg = (
        f"I have resources about '{topic}' from {oldest} to {newest}:\n"
        f"{url_list}\n"
        "Is it good enough for you or do you want me to fetch new ones? (yes/no)"
    )
    logger.debug(f"Found recent URLs for topic: {topic}, urls: {url_list}")

    return {
        "messages": [AIMessage(content=msg)],
        "next": "__await_input__"  # pause for user confirmation
    }
