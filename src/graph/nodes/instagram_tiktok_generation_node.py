"""
Instagram/TikTok content generation node - generates video script.
"""

from langchain_core.messages import AIMessage
from ..state import MessageGraph
from ..chains import instagram_tiktok_generation_chain


def instagram_tiktok_generation_node(state: MessageGraph) -> dict:
    """
    Generate Instagram/TikTok video script.
    
    Args:
        state: The current graph state with verified texts, topic, and details.
    
    Returns:
        dict: Updated state with Instagram/TikTok content.
    """
    verified_texts = state.get("verified_texts", [])
    topic = state.get("topic", "")
    details = state.get("details", "")
    
    combined_text = "\n\n".join(verified_texts)
    
    result = instagram_tiktok_generation_chain.invoke({
        "topic": topic,
        "details": details,
        "source_content": combined_text
    })
    
    generated_content = state.get("generated_content", {})
    generated_content["instagram_tiktok"] = result.content
    
    return {
        "generated_content": generated_content,
        "messages": [AIMessage(content="Instagram/TikTok script generated")]
    }

