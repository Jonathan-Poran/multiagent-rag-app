from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from src.config.settings import settings


class ContentStructure(BaseModel):
    """Structure for organizing social media content requests."""
    topic: str = Field(description="General topic category (e.g., fashion, sports, tech, food, travel, health, entertainment, business, education)")
    details: str = Field(description="Specific sub-topic or detailed content description (e.g., 'football, european league' for sports, 'new langgraph tools' for tech)")


class RelevanceScore(BaseModel):
    """Structure for relevance rating output."""
    relevance_score: float = Field(description="Relevance score from 0.0 to 1.0", ge=0.0, le=1.0)
    explanation: str = Field(description="Brief explanation of the relevance score")


# Predefined topics list for the prompt
# Import from consts to keep topics centralized
from ..consts import PREDEFINED_TOPICS

TOPICS_LIST = ", ".join(PREDEFINED_TOPICS)

# Topic Extraction Chain
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

# Relevance Rating Chain
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

# LinkedIn Generation Chain
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

# Instagram/TikTok Generation Chain
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

llm = ChatOpenAI(api_key=settings.openai_api_key, model="gpt-4")
llm_structured = ChatOpenAI(api_key=settings.openai_api_key).with_structured_output(ContentStructure)
llm_relevance = ChatOpenAI(api_key=settings.openai_api_key).with_structured_output(RelevanceScore)

# Chains
topic_extraction_chain = topic_extraction_prompt | llm_structured
relevance_rating_chain = relevance_rating_prompt | llm_relevance
linkedin_generation_chain = linkedin_generation_prompt | llm
instagram_tiktok_generation_chain = instagram_tiktok_generation_prompt | llm

# Legacy chains (kept for backward compatibility)
generation_chain = topic_extraction_chain

# Reflection chain (deprecated but kept for backward compatibility)
# Note: This is a placeholder - reflection functionality is not part of the new workflow
reflection_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a content reviewer. Review the provided content and provide feedback."""
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
reflection_chain = reflection_prompt | llm
