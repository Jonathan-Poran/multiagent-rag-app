"""
Routing function after YouTube search.
Routes based on whether videos were found.
"""

from src.dto.graph_dto import MessageGraph
from src.graph.consts import TRANSCRIPT_FETCH, CORE_TEXT_EXTRACTION

def route_after_youtube_search(state: MessageGraph) -> str:
    """
    Route after YouTube search.
    If videos were found, go to transcript fetch.
    Otherwise, go directly to core text extraction.
    
    Args:
        state: The current graph state.
    
    Returns:
        str: Next node name (TRANSCRIPT_FETCH or CORE_TEXT_EXTRACTION).
    """
    video_urls = state.get("video_urls", [])
    return TRANSCRIPT_FETCH if video_urls else CORE_TEXT_EXTRACTION

