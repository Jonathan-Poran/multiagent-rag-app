from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.services.openai_service import (
    _get_openai_client,
    _get_openai_structured_client,
    ContentStructure,
    RelevanceScore
)


# ContentStructure and RelevanceScore are now imported from openai_service


# Predefined topics list for the prompt
# Import from consts to keep topics centralized
from src.graph.consts import PREDEFINED_TOPICS

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

# Get LLM instances from OpenAI service (lazy initialization)
# Note: These chains are kept for backward compatibility but nodes should use openai_service directly
# The chains will be initialized when first accessed

_llm = None
_llm_structured = None
_llm_relevance = None

def _get_llm():
    """Get OpenAI client (lazy initialization)."""
    global _llm
    if _llm is None:
        _llm = _get_openai_client()
        if _llm is None:
            raise ValueError("OpenAI client not available - OPENAI_API_KEY not configured")
    return _llm

def _get_llm_structured():
    """Get OpenAI structured client (lazy initialization)."""
    global _llm_structured
    if _llm_structured is None:
        _llm_structured = _get_openai_structured_client()
        if _llm_structured is None:
            raise ValueError("OpenAI structured client not available - OPENAI_API_KEY not configured")
    return _llm_structured


# Chains (lazy initialization - will fail if API key not configured)
# These are kept for backward compatibility but nodes should use openai_service directly
# We create wrapper chains that lazily initialize the LLMs
class _LazyChain:
    """Lazy chain wrapper that initializes LLM on first invocation."""
    def __init__(self, prompt, get_llm_func):
        self.prompt = prompt
        self.get_llm = get_llm_func
        self._chain = None
    
    def invoke(self, *args, **kwargs):
        if self._chain is None:
            self._chain = self.prompt | self.get_llm()
        return self._chain.invoke(*args, **kwargs)
    
    def __or__(self, other):
        # Support chain composition
        if self._chain is None:
            self._chain = self.prompt | self.get_llm()
        return self._chain | other

topic_extraction_chain = _LazyChain(topic_extraction_prompt, _get_llm_structured)
relevance_rating_chain = _LazyChain(relevance_rating_prompt, _get_llm_relevance)
linkedin_generation_chain = _LazyChain(linkedin_generation_prompt, _get_llm)
instagram_tiktok_generation_chain = _LazyChain(instagram_tiktok_generation_prompt, _get_llm)

# LLM instances (for backward compatibility - lazy access)
class _LazyLLM:
    """Lazy LLM wrapper."""
    def __init__(self, get_llm_func):
        self.get_llm = get_llm_func
        self._llm = None
    
    def __call__(self, *args, **kwargs):
        if self._llm is None:
            self._llm = self.get_llm()
        return self._llm(*args, **kwargs)
    
    def __getattr__(self, name):
        if self._llm is None:
            self._llm = self.get_llm()
        return getattr(self._llm, name)
    
    def __or__(self, other):
        if self._llm is None:
            self._llm = self.get_llm()
        return self._llm | other

llm = _LazyLLM(_get_llm)
llm_structured = _LazyLLM(_get_llm_structured)
llm_relevance = _LazyLLM(_get_llm_relevance)

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
