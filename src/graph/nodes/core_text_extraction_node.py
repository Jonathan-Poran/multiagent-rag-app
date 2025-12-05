"""
Core text extraction node - extracts relevant text from URLs using Tavily.
"""

from src.dto.graph_dto import MessageGraph
from src.services.tavily_service import extract_core_text_from_urls
from src.config.logger import get_logger
from langchain_core.messages import AIMessage

logger = get_logger("CoreTextExtraction")


def core_text_extraction_node(state: MessageGraph) -> dict:
    """
    Extract core relevant text from URLs.
    
    Args:
        state: The current graph state with URLs, topic, and details.
    
    Returns:
        dict: Updated state with core texts.
    """
    urls = state.get("urls", [])
    topic = state.get("topic", "")
    details = state.get("details", "")

    if not urls:
        logger.warning("No URLs found in state, cannot extract core text")
        return {
            "core_texts": []
        }
    
    logger.info(f"Extracting core text from {len(urls)} URLs for topic: {topic}, details: {details}")
    
    # Extract core text from all URLs
    core_text = extract_core_text_from_urls(urls, topic, details)
    
    # Store the extracted text in core_texts list
    core_texts = [core_text] if core_text else []

    return {
        "urls": urls,
        "topic": topic,
        "details": details,
        "core_texts": core_texts
    }

