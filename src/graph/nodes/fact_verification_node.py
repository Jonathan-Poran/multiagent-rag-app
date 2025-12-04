"""
Fact verification node - verifies factual correctness using Tavily.
"""

from langchain_core.messages import AIMessage
from ..state import MessageGraph
from src.services.tavily_service import verify_facts


def fact_verification_node(state: MessageGraph) -> dict:
    """
    Verify factual correctness of core texts.
    
    Args:
        state: The current graph state with core texts, topic, and details.
    
    Returns:
        dict: Updated state with verified texts.
    """
    core_texts = state.get("core_texts", [])
    topic = state.get("topic", "")
    details = state.get("details", "")
    
    verified_texts = []
    for core_text in core_texts:
        verification = verify_facts(core_text, topic, details)
        if verification.get("verified", False):
            verified_texts.append(core_text)
    
    return {
        "verified_texts": verified_texts,
        "messages": [AIMessage(content=f"Verified {len(verified_texts)} texts")]
    }

