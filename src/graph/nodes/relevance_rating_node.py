from datetime import datetime
from langchain_core.messages import AIMessage
from src.dto.graph_dto import MessageGraph
from src.services.openai_service import rate_relevance
from src.services.mongo_service import save_relevance_data
from src.config.logger import get_logger

logger = get_logger("RelevanceRating")

def relevance_rating_node(state: MessageGraph) -> dict:
    """
    Rate relevance of core texts to user request.
    Keep top 2 most relevant URLs for content generation.
    Save topic, details, urls, core_text, and date to DB for each URL/core_text combination.
    """
    core_texts = state.get("core_texts", [])
    urls = state.get("urls", [])
    topic = state.get("topic", "")
    details = state.get("details", "")
    
    user_message = ""
    for msg in state.get("messages", []):
        if hasattr(msg, "content"):
            user_message = msg.content
            break

    scored_texts = []
    for text in core_texts:
        score = rate_relevance(user_message, text).relevance_score
        scored_texts.append({"text": text, "score": score})

    # Sort by score descending
    scored_texts.sort(key=lambda x: x["score"], reverse=True)
    top_texts = [x["text"] for x in scored_texts[:2]]

    # Save to DB: for each URL and core_text combination
    # Save one record per URL with its corresponding core_text
    current_date = datetime.utcnow()
    
    if urls and top_texts:
        # Combine all top texts into one core_text (since extraction returns combined text)
        combined_core_text = "\n\n".join(top_texts) if len(top_texts) > 1 else (top_texts[0] if top_texts else "")
        
        # Save one record per URL, each with the combined core_text
        for url in urls:
            try:
                save_relevance_data(
                    topic=topic,
                    details=details,
                    url=url,
                    core_text=combined_core_text,
                    date=current_date
                )
                logger.info(f"Saved relevance data to DB: topic='{topic}', url={url}")
            except Exception as e:
                logger.error(f"Failed to save relevance data for URL {url}: {e}", exc_info=True)
                # Continue with other URLs even if one fails

    msg = AIMessage(content=f"Kept top {len(top_texts)} relevant texts for content generation.")
    return {"core_texts": top_texts, "messages": [msg]}
