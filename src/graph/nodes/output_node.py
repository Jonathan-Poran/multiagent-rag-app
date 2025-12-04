"""
Output node - collects all generated content and formats final response.
"""

import json
from langchain_core.messages import AIMessage
from ..state import MessageGraph


def output_node(state: MessageGraph) -> dict:
    """
    Collect all generated content and format final response.
    
    Args:
        state: The current graph state with all generated content.
    
    Returns:
        dict: Updated state with formatted output message.
    """
    generated_content = state.get("generated_content", {})
    
    # Format output as structured JSON
    output = {
        "linkedin": generated_content.get("linkedin", ""),
        "instagram_tiktok": generated_content.get("instagram_tiktok", ""),
        "topic": state.get("topic", ""),
        "details": state.get("details", "")
    }
    
    output_message = f"""Here's your generated social media content:

**LinkedIn Post:**
{output['linkedin']}

**Instagram/TikTok Script:**
{output['instagram_tiktok']}

**Topic:** {output['topic']}
**Details:** {output['details']}
"""
    
    return {
        "messages": [AIMessage(content=output_message)]
    }

