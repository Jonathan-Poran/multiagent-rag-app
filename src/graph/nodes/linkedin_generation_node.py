"""
LinkedIn generation node - generates LinkedIn post content.
"""

from langchain_core.messages import AIMessage
from ..state import MessageGraph
from src.services.openai_service import generate_linkedin_content


def linkedin_generation_node(state: MessageGraph) -> dict:
    """
    Generate LinkedIn post content based on topic, details, and verified texts.
    
    Args:
        state: The current graph state with topic, details, and verified texts.
    
    Returns:
        dict: Updated state with generated LinkedIn content.
    """
    topic = state.get("topic", "")
    details = state.get("details", "")
    verified_texts = state.get("verified_texts", [])
    
    # Combine verified texts as source content
    source_content = "\n\n".join(verified_texts) if verified_texts else ""
    
    if not source_content:
        return {
            "generated_content": {"linkedin": ""},
            "messages": [AIMessage(content="No verified content available for LinkedIn generation")]
        }
    
    try:
        linkedin_content = generate_linkedin_content(topic, details, source_content)
        
        generated_content = state.get("generated_content", {})
        generated_content["linkedin"] = linkedin_content
        
        return {
            "generated_content": generated_content,
            "messages": [AIMessage(content=f"Generated LinkedIn post for topic: {topic}")]
        }
    except Exception as e:
        return {
            "generated_content": state.get("generated_content", {}),
            "messages": [AIMessage(content=f"Error generating LinkedIn content: {str(e)}")]
        }

