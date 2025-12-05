"""
OpenAI API service for LLM operations.
"""

from typing import Optional, Any, Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field
from src.config.logger import get_logger
from src.config.settings import settings
from src.graph.consts import PREDEFINED_TOPICS

logger = get_logger("OpenAI")

# Token limits: roughly 1 token = 4 characters
MAX_SOURCE_CONTENT_LENGTH = 24000

_openai_client: Optional[ChatOpenAI] = None
_openai_structured_client: Optional[Any] = None
_openai_relevance_client: Optional[Any] = None


class ContentStructure(BaseModel):
    """Structure for organizing social media content requests."""
    topic: str = Field(description="General topic category (e.g., fashion, sports, tech, food, travel, health, entertainment, business, education)")
    details: str = Field(description="Specific sub-topic or detailed content description (e.g., 'football, european league' for sports, 'new langgraph tools' for tech)")


class RelevanceScore(BaseModel):
    """Structure for relevance rating output."""
    relevance_score: float = Field(description="Relevance score from 0.0 to 1.0", ge=0.0, le=1.0)
    explanation: str = Field(description="Brief explanation of the relevance score")


def get_openai_client() -> Optional[ChatOpenAI]:
    """
    Get or create OpenAI client instance.
    Uses singleton pattern to reuse the same client instance.
    
    Returns:
        ChatOpenAI client instance or None if API key is not configured.
    """
    global _openai_client
    
    if _openai_client is not None:
        return _openai_client
    
    if not settings.openai_api_key:
        logger.warning("OPENAI_API_KEY not configured")
        return None
    
    try:
        _openai_client = ChatOpenAI(api_key=settings.openai_api_key, model="gpt-4")
        logger.info("OpenAI client initialized successfully")
        return _openai_client
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}", exc_info=True)
        return None


def get_openai_structured_client() -> Optional[Any]:
    """
    Get or create OpenAI client with structured output support.
    
    Returns:
        ChatOpenAI client with structured output or None if API key is not configured.
    """
    global _openai_structured_client
    
    if _openai_structured_client is not None:
        return _openai_structured_client
    
    if not settings.openai_api_key:
        logger.warning("OPENAI_API_KEY not configured")
        return None
    
    try:
        llm = ChatOpenAI(api_key=settings.openai_api_key)
        _openai_structured_client = llm.with_structured_output(ContentStructure)
        logger.info("OpenAI structured client initialized successfully")
        return _openai_structured_client
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI structured client: {e}", exc_info=True)
        return None


def truncate_source_content(source_content: str, max_length: int = MAX_SOURCE_CONTENT_LENGTH) -> str:
    """
    Truncate source content to fit within token limits.
    
    Args:
        source_content: The source content to truncate
        max_length: Maximum character length (default: 24,000 chars ≈ 6,000 tokens)
    
    Returns:
        Truncated source content
    """
    if len(source_content) <= max_length:
        return source_content
    
    # Truncate and add indicator
    truncated = source_content[:max_length]
    # Try to cut at a sentence boundary
    last_period = truncated.rfind('.')
    last_newline = truncated.rfind('\n')
    cut_point = max(last_period, last_newline)
    
    if cut_point > max_length * 0.9:  # Only use cut point if it's not too early
        truncated = truncated[:cut_point + 1]
    
    logger.warning(f"Source content truncated from {len(source_content)} to {len(truncated)} characters to fit token limits")
    return truncated + "\n\n[Content truncated due to length limits...]"


def get_openai_relevance_client() -> Optional[Any]:
    """
    Get or create OpenAI client for relevance rating with structured output.
    
    Returns:
        ChatOpenAI client with RelevanceScore structured output or None if API key is not configured.
    """
    global _openai_relevance_client
    
    if _openai_relevance_client is not None:
        return _openai_relevance_client
    
    if not settings.openai_api_key:
        logger.warning("OPENAI_API_KEY not configured")
        return None
    
    try:
        llm = ChatOpenAI(api_key=settings.openai_api_key)
        _openai_relevance_client = llm.with_structured_output(RelevanceScore)
        logger.info("OpenAI relevance client initialized successfully")
        return _openai_relevance_client
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI relevance client: {e}", exc_info=True)
        return None


def extract_topic_and_details(messages: list) -> ContentStructure:
    """
    Extract topic and details from user messages using OpenAI.
    
    Args:
        messages: List of LangChain messages (HumanMessage, AIMessage, etc.)
    
    Returns:
        ContentStructure with topic and details
    """
    logger.info("Extracting topic and details from user messages")
    
    structured_client = get_openai_structured_client()
    if not structured_client:
        raise ValueError("OpenAI structured client not available - OPENAI_API_KEY not configured")
    
    TOPICS_LIST = ", ".join(PREDEFINED_TOPICS)
    
    topic_extraction_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""You are a social media content organizer. Your task is to analyze user messages and extract:
                1. The general topic - MUST be one of these predefined topics: {TOPICS_LIST}
                - If the user's message doesn't clearly match any of these topics, return an empty string for topic
                - Map the user's intent to the closest matching topic from the list above
                - Use the exact topic name from the list (e.g., "tech", "sports", "fashion")
                
                2. The specific details or sub-topics - provide specific information about what aspect of the topic they want to cover
                - Examples: for sports: "football, european league", for tech: "AI and machine learning", for food: "Italian pasta recipes"
                - If no specific details are mentioned, return an empty string

                IMPORTANT: 
                - Only return a topic if you can confidently map it to one of the predefined topics above
                - If the message is unclear, nonsensical, or doesn't match any topic, return empty string for topic
                - Be specific and accurate in categorizing the user's request

                Return a JSON structure with "topic" and "details" fields."""
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    
    chain = topic_extraction_prompt | structured_client
    result = chain.invoke({"messages": messages})
    
    logger.info(f"Extracted topic: {result.topic}, details: {result.details}")
    return result


def rate_relevance(user_request: str, core_text: str) -> RelevanceScore:
    """
    Rate how well core text matches user request using OpenAI.
    
    Args:
        user_request: The user's original request
        core_text: The core text to evaluate
    
    Returns:
        RelevanceScore with relevance score and explanation
    """
    logger.info("Rating relevance of core text to user request")
    
    relevance_client = get_openai_relevance_client()
    if not relevance_client:
        raise ValueError("OpenAI relevance client not available - OPENAI_API_KEY not configured")
    
    relevance_rating_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a content relevance evaluator. Your task is to rate how well a piece of core text matches a user's content request.
                Rate the relevance on a scale from 0.0 (completely irrelevant) to 1.0 (highly relevant).
                Consider:
                - How well the text addresses the user's topic and details
                - The quality and depth of information
                - The usefulness for creating social media content
                
                Return a relevance score and a brief explanation."""
            ),
            (
                "user",
                "User Request: {user_request}\n\nCore Text: {core_text}"
            ),
        ]
    )
    
    chain = relevance_rating_prompt | relevance_client
    result = chain.invoke({
        "user_request": user_request,
        "core_text": core_text
    })
    
    logger.info(f"Relevance score: {result.relevance_score}")
    return result


def generate_linkedin_content(topic: str, details: str, source_content: str) -> str:
    """
    Generate LinkedIn post content using OpenAI.
    
    Args:
        topic: General topic category
        details: Specific details or sub-topics
        source_content: Source content to base the post on
    
    Returns:
        Generated LinkedIn post content
    """
    logger.info(f"Generating LinkedIn content for topic: {topic}, details: {details}")
    
    client = get_openai_client()
    if not client:
        raise ValueError("OpenAI client not available - OPENAI_API_KEY not configured")
    
    # Truncate source content to fit within token limits
    truncated_content = truncate_source_content(source_content)
    
    linkedin_generation_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert LinkedIn content creator. Create a professional, engaging LinkedIn post based on the provided topic, details, and source content.
                The post should be:
                - Professional yet engaging
                - Well-structured with clear sections
                - Include relevant insights and value
                - Optimized for LinkedIn's audience
                - Between 200-300 words
                
                Use the source content to inform your post, but make it original and compelling."""
            ),
            (
                "user",
                "Topic: {topic}\nDetails: {details}\n\nSource Content:\n{source_content}"
            ),
        ]
    )
    
    chain = linkedin_generation_prompt | client
    result = chain.invoke({
        "topic": topic,
        "details": details,
        "source_content": truncated_content
    })
    
    content = result.content if hasattr(result, 'content') else str(result)
    logger.info("LinkedIn content generated successfully")
    return content


def generate_video_script(topic: str, details: str, source_content: str) -> str:
    """
    Generate Instagram/TikTok video script using OpenAI.
    
    Args:
        topic: General topic category
        details: Specific details or sub-topics
        source_content: Source content to base the script on
    
    Returns:
        Generated Instagram/TikTok video script
    """
    logger.info(f"Generating Instagram/TikTok script for topic: {topic}, details: {details}")
    
    client = get_openai_client()
    if not client:
        raise ValueError("OpenAI client not available - OPENAI_API_KEY not configured")
    
    # Truncate source content to fit within token limits
    truncated_content = truncate_source_content(source_content)
    
    instagram_tiktok_generation_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert social media script writer for Instagram and TikTok. Create a detailed video script based on the provided topic, details, and source content.
                The script should be:
                - Engaging and attention-grabbing from the first second
                - Structured with clear hooks, main content, and call-to-action
                - Include specific talking points and visual cues
                - Optimized for short-form video (30-60 seconds)
                - Include timestamps and scene descriptions
                
                Format the script with clear sections and visual cues."""
            ),
            (
                "user",
                "Topic: {topic}\nDetails: {details}\n\nSource Content:\n{source_content}"
            ),
        ]
    )
    
    chain = instagram_tiktok_generation_prompt | client
    result = chain.invoke({
        "topic": topic,
        "details": details,
        "source_content": truncated_content
    })
    
    content = result.content if hasattr(result, 'content') else str(result)
    logger.info("Instagram/TikTok script generated successfully")
    return content

