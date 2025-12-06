"""
Topic extraction node - extracts topic and details from user message.
"""
from langchain_core.messages import AIMessage, HumanMessage
from src.dto.graph_dto import MessageGraph
from src.graph.consts import PREDEFINED_TOPICS
from src.services.openai_service import extract_topic_and_details


def topic_extraction_node(state: MessageGraph) -> dict:
    """
    Extract topic and details from user's message.
    Handles retries up to 2 times if topic is unclear.
    
    Args:
        state: The current graph state containing messages.
    
    Returns:
        dict: Updated state with topic and details, or a message asking for clarification.
    """
    # Get current retry count
    retry_count = state.get("retry_count", 0)
    
    result = extract_topic_and_details(state["messages"])
    
    # If topic is empty, handle retry logic
    if not result.topic or result.topic.strip() == "":
        retry_count += 1
        
        # If we've exceeded retry limit, exit politely
        if retry_count >= 2:
            exit_message = """I apologize, but I'm having trouble understanding the topic you'd like to create content about. 

Please try again later with a clearer request, or feel free to specify one of these topics: tech, sports, fashion, food, travel, health, business, education, science, art, music, gaming, finance, fitness, cooking, photography, design, marketing, startup, career, motivation, productivity, environment, politics, or news.

Thank you for your patience!"""
            
            return {
                "topic": "",
                "details": "",
                "retry_count": retry_count,
                "messages": [AIMessage(content=exit_message)]
            }
        
        # Get the user's original message for context
        user_message = ""
        for msg in state["messages"]:
            if isinstance(msg, HumanMessage):
                user_message = msg.content
                break
        
        # Create a friendly message with examples of topics we can handle
        topics_examples = ", ".join(PREDEFINED_TOPICS[:5])
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
            "retry_count": retry_count,
            "messages": [AIMessage(content=topic_extracted_failure_message)]
        }
    
    # Normal case: topic was extracted successfully
    return {
        "topic": result.topic,
        "details": result.details,
        "retry_count": 0,  # Reset retry count on success
        "messages": [AIMessage(content=f"Topic: {result.topic}, details: {result.details}")]
    }

