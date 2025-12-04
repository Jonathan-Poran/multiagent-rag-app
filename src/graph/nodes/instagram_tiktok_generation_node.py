"""
Instagram/TikTok generation node - generates video script content.
"""

from langchain_core.messages import AIMessage
from ..state import MessageGraph
from src.services.openai_service import generate_instagram_tiktok_script


def instagram_tiktok_generation_node(state: MessageGraph) -> dict:
    """
    Generate Instagram/TikTok video script based on topic, details, and verified texts.
    
    Args:
        state: The current graph state with topic, details, and verified texts.
    
    Returns:
        dict: Updated state with generated Instagram/TikTok script.
    """
    topic = state.get("topic", "")
    details = state.get("details", "")
    verified_texts = state.get("verified_texts", [])
    
    # Combine verified texts as source content
    source_content = "\n\n".join(verified_texts) if verified_texts else ""
    
    if not source_content:
        return {
            "generated_content": {"instagram_tiktok": ""},
            "messages": [AIMessage(content="No verified content available for Instagram/TikTok generation")]
        }
    
    try:
        instagram_tiktok_script = generate_instagram_tiktok_script(topic, details, source_content)
        
        generated_content = state.get("generated_content", {})
        generated_content["instagram_tiktok"] = instagram_tiktok_script
        
        return {
            "generated_content": generated_content,
            "messages": [AIMessage(content=f"Generated Instagram/TikTok script for topic: {topic}")]
        }
    except Exception as e:
        return {
            "generated_content": state.get("generated_content", {}),
            "messages": [AIMessage(content=f"Error generating Instagram/TikTok script: {str(e)}")]
        }

