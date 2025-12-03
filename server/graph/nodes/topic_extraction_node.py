"""
Topic extraction node - extracts topic and details from user message.
"""

import json
from langchain_core.messages import AIMessage
from ..chains import topic_extraction_chain
from ..state import MessageGraph


def topic_extraction_node(state: MessageGraph) -> dict:
    """
    Extract topic and details from user's message.
    
    Args:
        state: The current graph state containing messages.
    
    Returns:
        dict: Updated state with topic and details.
    """
    result = topic_extraction_chain.invoke({"messages": state["messages"]})
    
    return {
        "topic": result.topic,
        "details": result.details,
        "messages": [AIMessage(content=f"Extracted topic: {result.topic}, details: {result.details}")]
    }

