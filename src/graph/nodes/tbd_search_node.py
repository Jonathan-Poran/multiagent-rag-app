"""
TBD search node - placeholder for additional search sources (blogs, news, forums).
"""

from langchain_core.messages import AIMessage
from ..state import MessageGraph
from src.services.tavily_service import search_tavily


def tbd_search_node(state: MessageGraph) -> dict:
    """
    Search additional sources (TBD) for content related to topic and details.
    
    Args:
        state: The current graph state with topic and details.
    
    Returns:
        dict: Updated state with search results.
    """
    topic = state.get("topic", "")
    details = state.get("details", "")
    query = f"{topic} {details}"
    
    # Use Tavily for additional search
    results = search_tavily(query, max_results=5)
    urls = [result.get("url", "") for result in results if result.get("url")]
    
    return {
        "messages": [AIMessage(content=f"Found {len(urls)} additional sources")]
    }

