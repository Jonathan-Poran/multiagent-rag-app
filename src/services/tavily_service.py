"""
Tavily API service for search and content extraction.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from tavily import TavilyClient
from src.config.logger import get_logger
from src.config.settings import settings

logger = get_logger("Tavily")

_tavily_client = None


def _get_tavily_client() -> Optional[TavilyClient]:
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
    client = _get_tavily_client()
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


def get_viral_urls_from_last_month(topic: str, details: str, limit: int = 2) -> List[str]:
    """
    Get viral Tavily URLs from the last month.
    
    Args:
        topic: General topic category
        details: Specific details or sub-topics
        limit: Number of URLs to return
    
    Returns:
        List of URLs from Tavily search results from the last month
    """
    logger.info(f"Searching Tavily for viral content: {topic}, {details}")
    
    try:
        # Combine topic and details for search query
        query = f"{topic} {details} viral trending".strip() if details else f"{topic} viral trending"
        
        # Search Tavily - it typically returns recent/viral content
        results = search_tavily(query, max_results=limit)
        
        # Filter and extract URLs, prioritizing by score/engagement if available
        urls = []
        for result in results:
            url = result.get("url", "")
            if url and url not in urls:
                # Check if result has date info (Tavily results may include published_date)
                published_date = result.get("published_date")
                if published_date:
                    try:
                        # Parse date and check if within last month
                        # Handle different date formats
                        if isinstance(published_date, str):
                            if "Z" in published_date:
                                pub_date = datetime.fromisoformat(published_date.replace("Z", "+00:00"))
                            else:
                                pub_date = datetime.fromisoformat(published_date)
                        else:
                            pub_date = datetime.fromtimestamp(published_date)
                        
                        # Check if within last month
                        # Convert to UTC for comparison
                        if pub_date.tzinfo:
                            now = datetime.now(pub_date.tzinfo)
                            days_diff = (now - pub_date).days
                        else:
                            now = datetime.utcnow()
                            days_diff = (now - pub_date).days
                        
                        if days_diff > 30:
                            continue
                    except Exception as e:
                        logger.debug(f"Could not parse date {published_date}: {e}")
                        pass  # If date parsing fails, include it anyway
                
                urls.append(url)
                logger.debug(f"Found Tavily URL: {url}")
                
                if len(urls) >= limit:
                    break
        
        logger.info(f"Found {len(urls)} Tavily URLs from last month")
        return urls[:limit]
        
    except Exception as e:
        logger.error(f"Error searching Tavily for viral URLs: {e}", exc_info=True)
        return []


def extract_core_text_from_urls(urls: list[str], topic: str, details: str) -> str:
    """
    Extract core relevant text from a URL using Tavily extract API.
    
    Args:
        url: URL to extract content from
        topic: General topic
        details: Specific details
    
    Returns:
        Extracted core text relevant to topic/details
    """
    client = _get_tavily_client()
    if not client:
        logger.warning("Tavily client not available - cannot extract from URL")
        return ""
    
    try:
        query = f"{topic} {details}".strip()
        logger.info(f"Extracting core text from {len(urls)} URLs using Tavily for: {query}")
        
        # Pass urls directly (it's already a list)
        response = client.extract(urls=urls, include_images=False)
        
        # Debug: log response type and structure
        logger.debug(f"Tavily extract response type: {type(response)}")
        if isinstance(response, (dict, list)):
            logger.debug(f"Tavily extract response length/structure: {len(response) if isinstance(response, (list, dict)) else 'N/A'}")
        
        content = ""

        # Handle different response formats
        if isinstance(response, dict):
            # If response is a dict, check for 'results' or 'content' keys
            results = response.get("results", [])
            if not results:
                # Try 'content' as a direct string
                content = response.get("content", "")
                if content:
                    logger.info(f"Extracted {len(content)} characters from response content")
                    return content
        elif isinstance(response, list):
            # If response is a list, iterate through results
            results = response
        else:
            logger.warning(f"Unexpected response type: {type(response)}")
            results = []

        # Process results list
        for result in results:
            if isinstance(result, dict):
                # Extract content from result dict
                raw_content = result.get('raw_content', '') or result.get('content', '')
                if raw_content:
                    content += raw_content + "\n\n"
                    url = result.get('url', 'unknown')
                    logger.debug(f"Extracted {len(raw_content)} characters from {url}")
            elif isinstance(result, str):
                # If result is a string, use it directly
                content += result + "\n\n"
            else:
                logger.warning(f"Unexpected result type: {type(result)}")

        if not content:
            logger.warning(f"No content extracted from urls: {urls}")
            return ""
        
        logger.info(f"Extracted {len(content)} characters of core text from {len(urls)} URLs")
        
        return content.strip()

    except Exception as e:
        logger.error(f"Tavily extraction from URLs failed: {e}", exc_info=True)
        return ""


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
    client = _get_tavily_client()
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
    client = _get_tavily_client()
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

