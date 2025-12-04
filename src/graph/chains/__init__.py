"""
Chains package for LangChain prompt chains.
Contains topic extraction, relevance rating, and content generation chains.
"""

from .chains import (
    # New chains
    topic_extraction_chain,
    relevance_rating_chain,
    linkedin_generation_chain,
    instagram_tiktok_generation_chain,
    # Legacy chains (for backward compatibility)
    generation_chain,
    reflection_chain,
    # Prompts
    topic_extraction_prompt,
    relevance_rating_prompt,
    linkedin_generation_prompt,
    instagram_tiktok_generation_prompt,
    # LLM instances
    llm,
    llm_structured,
    llm_relevance,
    # Models
    ContentStructure,
    RelevanceScore,
)

__all__ = [
    # New chains
    "topic_extraction_chain",
    "relevance_rating_chain",
    "linkedin_generation_chain",
    "instagram_tiktok_generation_chain",
    # Legacy chains
    "generation_chain",
    "reflection_chain",
    # Prompts
    "topic_extraction_prompt",
    "relevance_rating_prompt",
    "linkedin_generation_prompt",
    "instagram_tiktok_generation_prompt",
    # LLM instances
    "llm",
    "llm_structured",
    "llm_relevance",
    # Models
    "ContentStructure",
    "RelevanceScore",
]

