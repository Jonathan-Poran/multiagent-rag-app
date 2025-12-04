"""
YouTube search node - searches for recent and viral videos.
"""

from langchain_core.messages import AIMessage
from ..state import MessageGraph
from src.services.youtube import search_youtube_videos


def youtube_search_node(state: MessageGraph) -> dict:
    """
    Search YouTube for videos related to topic and details.
    
    Args:
        state: The current graph state with topic and details.
    
    Returns:
        dict: Updated state with video URLs.
    """
    topic = state.get("topic", "")
    details = state.get("details", "")
    
    video_urls = search_youtube_videos(topic, details, max_results=5)
    
    return {
        "video_urls": video_urls,
        "messages": [AIMessage(content=f"Found {len(video_urls)} YouTube videos")]
    }

