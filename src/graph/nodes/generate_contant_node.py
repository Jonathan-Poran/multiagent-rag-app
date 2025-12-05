"""
Content generation node - generates both LinkedIn posts and Instagram/TikTok video scripts.
"""

import threading
from langchain_core.messages import AIMessage
from src.dto.graph_dto import MessageGraph
from src.services.openai_service import generate_linkedin_content, generate_video_script, truncate_source_content
from src.config.logger import get_logger

logger = get_logger("GenerateContent")


def generate_contant_node(state: MessageGraph) -> dict:
    """
    Generate both LinkedIn post and Instagram/TikTok video script based on topic, details, and core texts.
    Runs both generations in parallel
    
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
        # Truncate source content once before generating both
        truncated_content = truncate_source_content(source_content)
        
        # Generate both LinkedIn content and video script in parallel using threads
        linkedin_content = None
        instagram_tiktok_script = None
        linkedin_error = None
        instagram_error = None
        
        # Shared variables to store results
        results = {"linkedin": None, "instagram": None, "linkedin_error": None, "instagram_error": None}
        
        def generate_linkedin():
            """Generate LinkedIn content in a separate thread."""
            try:
                results["linkedin"] = generate_linkedin_content(topic, details, truncated_content)
            except Exception as e:
                results["linkedin_error"] = str(e)
                logger.error(f"Error generating LinkedIn content: {e}", exc_info=True)
        
        def generate_instagram():
            """Generate Instagram/TikTok script in a separate thread."""
            try:
                results["instagram"] = generate_video_script(topic, details, truncated_content)
            except Exception as e:
                results["instagram_error"] = str(e)
                logger.error(f"Error generating Instagram/TikTok script: {e}", exc_info=True)
        
        # Create and start both threads
        linkedin_thread = threading.Thread(target=generate_linkedin)
        instagram_thread = threading.Thread(target=generate_instagram)
        
        linkedin_thread.start()
        instagram_thread.start()
        
        # Wait for both threads to complete
        linkedin_thread.join()
        instagram_thread.join()
        
        # Get results
        linkedin_content = results["linkedin"]
        instagram_tiktok_script = results["instagram"]
        linkedin_error = results["linkedin_error"]
        instagram_error = results["instagram_error"]
        
        # Update generated content
        generated_content = state.get("generated_content", {})
        
        if linkedin_content:
            generated_content["linkedin"] = linkedin_content
        if instagram_tiktok_script:
            generated_content["instagram_tiktok"] = instagram_tiktok_script
        
        # Build final message
        message_parts = []
        if linkedin_content:
            message_parts.append(f"LinkedIn Post: \n{linkedin_content}")
        elif linkedin_error:
            message_parts.append(f"LinkedIn Post: Error - {linkedin_error}")
        else:
            message_parts.append("LinkedIn Post: Not generated")
            
        if instagram_tiktok_script:
            message_parts.append(f"Viral Video Script: \n{instagram_tiktok_script}")
        elif instagram_error:
            message_parts.append(f"Viral Video Script: Error - {instagram_error}")
        else:
            message_parts.append("Viral Video Script: Not generated")
        
        final_message = "\n\n\n".join(message_parts)
        logger.debug(f"Final message: {final_message}")
        
        return {
            "generated_content": generated_content,
            "messages": [AIMessage(content=final_message)]
        }

    except Exception as e:
        logger.error(f"Error in content generation node: {e}", exc_info=True)
        return {
            "generated_content": state.get("generated_content", {}),
            "messages": [AIMessage(content=f"Error generating content: {str(e)}")]
        }

