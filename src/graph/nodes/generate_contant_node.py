"""
Content generation node - generates both LinkedIn posts and Instagram/TikTok video scripts.
"""

from langchain_core.messages import AIMessage
from src.graph.state import MessageGraph
from src.services.openai_service import generate_linkedin_content, generate_video_script


def generate_contant_node(state: MessageGraph) -> dict:
    """
    Generate both LinkedIn post and Instagram/TikTok video script based on topic, details, and core texts.
    
    Args:
        state: The current graph state with topic, details, and core texts.
    
    Returns:
        dict: Updated state with generated LinkedIn post and Instagram/TikTok script.
    """
    topic = state.get("topic", "")
    details = state.get("details", "")
    core_texts = state.get("core_texts", [])
    
    # Combine core texts as source content
    source_content = "\n\n".join(core_texts) if core_texts else ""
    
    if not source_content:
        return {
            "generated_content": state.get("generated_content", {}),
            "messages": [AIMessage(content="No core text available for content generation")]
        }
    
    try:
        # Generate both LinkedIn content and video script
        linkedin_content = generate_linkedin_content(topic, details, source_content)
        instagram_tiktok_script = generate_video_script(topic, details, source_content)
        
        # Update generated content
        generated_content = state.get("generated_content", {})
        generated_content["linkedin"] = linkedin_content
        generated_content["instagram_tiktok"] = instagram_tiktok_script
        
        # Format the final message with both LinkedIn post and viral video script
        final_message = f"LinkedIn Post: \n{linkedin_content}\n\n\nViral Video Script: \n{instagram_tiktok_script}"
        
        return {
            "generated_content": generated_content,
            "messages": [AIMessage(content=final_message)]
        }

    except Exception as e:
        return {
            "generated_content": state.get("generated_content", {}),
            "messages": [AIMessage(content=f"Error generating content: {str(e)}")]
        }

