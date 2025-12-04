"""
LinkedIn content generation node - generates professional LinkedIn post.
"""

from langchain_core.messages import AIMessage
from ..state import MessageGraph
from ..chains import linkedin_generation_chain


def linkedin_generation_node(state: MessageGraph) -> dict:
    """
    Generate LinkedIn post content.
    
    Args:
        state: The current graph state with verified texts, topic, and details.
    
    Returns:
        dict: Updated state with LinkedIn content.
    """
    verified_texts = state.get("verified_texts", [])
    topic = state.get("topic", "")
    details = state.get("details", "")
    
    combined_text = "\n\n".join(verified_texts)
    
    result = linkedin_generation_chain.invoke({
        "topic": topic,
        "details": details,
        "source_content": combined_text
    })
    
    generated_content = state.get("generated_content", {})
    generated_content["linkedin"] = result.content
    
    return {
        "generated_content": generated_content,
        "messages": [AIMessage(content="LinkedIn post generated")]
    }

