"""
Topic extraction node - extracts topic and details from user message.
"""
from langchain_core.messages import AIMessage, HumanMessage
from src.graph.state import MessageGraph
from src.graph.consts import PREDEFINED_TOPICS
from src.services.openai_service import extract_topic_and_details


def topic_extraction_node(state: MessageGraph) -> dict:
    """
    Extract topic and details from user's message.
    If topic is empty, return a friendly message asking for more specificity.
    
    Args:
        state: The current graph state containing messages.
    
    Returns:
        dict: Updated state with topic and details, or a message asking for clarification.
    """
    result = extract_topic_and_details(state["messages"])
    
    # If topic is empty, return a friendly message asking for more specificity
    if not result.topic or result.topic.strip() == "":
        # Get the user's original message for context
        user_message = ""
        for msg in state["messages"]:
            if isinstance(msg, HumanMessage):
                user_message = msg.content
                break
        
        # Create a friendly message with examples of topics we can handle
        topics_examples = ", ".join(PREDEFINED_TOPICS[:5])  # Show first 10 as examples
        topic_extracted_failure_message = f"""I'd be happy to help you create social media content! 

        However, I need a bit more clarity on what topic you'd like to focus on. Could you please specify what kind of content you want to create?
        Here are some topics I can help with: {topics_examples}, and more!

        For example, you could say:
        - "I want to create content about technology and AI"
        - "Help me create sports content about the latest football news"
        """
        
        return {
            "topic": "",
            "details": "",
            "messages": [AIMessage(content=topic_extracted_failure_message)]
        }
    
    # Normal case: topic was extracted successfully
    return {
        "topic": result.topic,
        "details": result.details,
        "messages": [AIMessage(content=f"Topic: {result.topic}, details: {result.details}")]
    }

