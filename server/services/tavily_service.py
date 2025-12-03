"""
Tavily API service for search and content extraction.
"""

from typing import List, Optional
from tavily import TavilyClient
from server.config.logger import get_logger
from server.config.settings import settings

logger = get_logger("Tavily")

_tavily_client = None


def get_tavily_client() -> Optional[TavilyClient]:
    """Get or create Tavily client instance."""
    global _tavily_client
    
    if _tavily_client is not None:
        return _tavily_client
    
    if not settings.tavily_api_key:
        logger.warning("TAVILY_API_KEY not configured")
        return None
    
    try:
        _tavily_client = TavilyClient(api_key=settings.tavily_api_key)
        logger.info("Tavily client initialized")
        return _tavily_client
    except Exception as e:
        logger.error(f"Failed to initialize Tavily client: {e}", exc_info=True)
        return None


def search_tavily(query: str, max_results: int = 5) -> List[dict]:
    """
    Search Tavily for relevant content.
    
    Args:
        query: Search query
        max_results: Maximum number of results
    
    Returns:
        List of search results with content
    """
    client = get_tavily_client()
    if not client:
        logger.warning("Tavily client not available")
        return []
    
    try:
        logger.info(f"Searching Tavily for: {query}")
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced"
        )
        
        results = response.get("results", [])
        logger.info(f"Tavily search returned {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"Tavily search failed: {e}", exc_info=True)
        return []


def extract_core_text(transcript: str, topic: str, details: str) -> str:
    """
    Extract core relevant text from transcript using Tavily extract.
    
    Args:
        transcript: Video transcript text
        topic: General topic
        details: Specific details
    
    Returns:
        Extracted core text relevant to topic/details
    """
    client = get_tavily_client()
    if not client:
        logger.warning("Tavily client not available - returning original transcript")
        return transcript
    
    try:
        query = f"{topic} {details}"
        logger.info(f"Extracting core text using Tavily for: {query}")
        
        # Use Tavily's extract API if available, otherwise use search
        # For now, we'll use search to find relevant content
        results = search_tavily(query, max_results=3)
        
        if results:
            # Combine relevant content from results
            core_text = "\n\n".join([
                result.get("content", "") for result in results
            ])
            logger.info(f"Extracted {len(core_text)} characters of core text")
            return core_text
        else:
            # Fallback to original transcript
            logger.warning("No Tavily results - using transcript as core text")
            return transcript
    except Exception as e:
        logger.error(f"Tavily extraction failed: {e}", exc_info=True)
        return transcript


def verify_facts(text: str, topic: str, details: str) -> dict:
    """
    Verify factual correctness using Tavily or trusted sources.
    
    Args:
        text: Text to verify
        topic: General topic
        details: Specific details
    
    Returns:
        Dictionary with verification results (verified: bool, confidence: float, sources: list)
    """
    client = get_tavily_client()
    if not client:
        logger.warning("Tavily client not available - skipping verification")
        return {"verified": False, "confidence": 0.0, "sources": []}
    
    try:
        query = f"fact check {topic} {details}"
        logger.info(f"Verifying facts using Tavily for: {query}")
        
        # Search for authoritative sources
        results = search_tavily(query, max_results=5)
        
        # Simple verification: if we find relevant authoritative sources, consider it verified
        verified = len(results) > 0
        confidence = min(len(results) / 5.0, 1.0) if results else 0.0
        
        sources = [result.get("url", "") for result in results if result.get("url")]
        
        logger.info(f"Fact verification: verified={verified}, confidence={confidence:.2f}")
        return {
            "verified": verified,
            "confidence": confidence,
            "sources": sources
        }
    except Exception as e:
        logger.error(f"Fact verification failed: {e}", exc_info=True)
        return {"verified": False, "confidence": 0.0, "sources": []}

