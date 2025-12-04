"""
Routing function after topic extraction.
Routes based on whether topic was successfully extracted.
"""

from ..state import MessageGraph
from ..consts import TOPIC_EXTRACTION, FIND_URL


def route_after_topic_extraction(state: MessageGraph) -> str:
    """
    Route after topic extraction.
    If topic is empty, loop back to topic extraction.
    If topic is valid, continue to find_url_node.
    
    Args:
        state: The current graph state.
    
    Returns:
        str: Next node name (TOPIC_EXTRACTION or FIND_URL).
    """
    topic = state.get("topic", "")
    
    # Check if topic is empty or just whitespace
    if not topic or topic.strip() == "":
        # Loop back to topic extraction to wait for more specific input
        return TOPIC_EXTRACTION
    else:
        # Topic is valid, continue to find URLs
        return FIND_URL

