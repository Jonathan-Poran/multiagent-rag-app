"""
Core text extraction node - extracts relevant text from transcripts using Tavily.
"""

from langchain_core.messages import AIMessage
from ..state import MessageGraph
from src.services.tavily_service import extract_core_text


def core_text_extraction_node(state: MessageGraph) -> dict:
    """
    Extract core relevant text from transcripts.
    
    Args:
        state: The current graph state with transcripts, topic, and details.
    
    Returns:
        dict: Updated state with core texts.
    """
    transcripts = state.get("transcripts", [])
    topic = state.get("topic", "")
    details = state.get("details", "")
    
    core_texts = []
    for transcript in transcripts:
        core_text = extract_core_text(transcript, topic, details)
        core_texts.append(core_text)
    
    return {
        "core_texts": core_texts,
        "messages": [AIMessage(content=f"Extracted core text from {len(core_texts)} sources")]
    }

