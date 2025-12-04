"""
Relevance rating node - rates how well core text matches user request.
"""

from langchain_core.messages import AIMessage
from ..state import MessageGraph
from ..chains import relevance_rating_chain


def relevance_rating_node(state: MessageGraph) -> dict:
    """
    Rate relevance of core texts to user request.
    
    Args:
        state: The current graph state with core texts and messages.
    
    Returns:
        dict: Updated state with relevance scores.
    """
    core_texts = state.get("core_texts", [])
    # Get the first user message (original request)
    from langchain_core.messages import HumanMessage
    user_message = ""
    for msg in state["messages"]:
        if isinstance(msg, HumanMessage):
            user_message = msg.content
            break
    
    relevance_scores = []
    for core_text in core_texts:
        # Use relevance rating chain to score each text
        result = relevance_rating_chain.invoke({
            "user_request": user_message,
            "core_text": core_text
        })
        relevance_scores.append(result.relevance_score)
    
    return {
        "relevance_scores": relevance_scores,
        "messages": [AIMessage(content=f"Rated relevance for {len(relevance_scores)} texts")]
    }

