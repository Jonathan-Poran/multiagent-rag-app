"""
Find URL node - finds 2 viral URLs from the last month from each service (Tavily, YouTube, Reddit).
"""

from datetime import datetime, timedelta
from src.dto.graph_dto import MessageGraph
from src.services.youtube_service import get_viral_urls_from_last_month
from src.services.tavily_service import get_viral_urls_from_last_month
from src.services.reddit_service import get_reddit_client, search_reddit_posts
from src.config.logger import get_logger


logger = get_logger("FindURL")


def _is_within_last_month(timestamp: float) -> bool:
    """
    Check if a Unix timestamp is within the last month.
    
    Args:
        timestamp: Unix timestamp (seconds since epoch)
    
    Returns:
        True if timestamp is within last 30 days
    """
    one_month_ago = datetime.utcnow() - timedelta(days=30)
    timestamp_dt = datetime.utcfromtimestamp(timestamp)
    return timestamp_dt >= one_month_ago


def _get_youtube_urls(topic: str, details: str, limit: int = 2) -> list[str]:
    """
    Get viral YouTube URLs from the last month.
    
    Args:
        topic: General topic category
        details: Specific details or sub-topics
        limit: Number of URLs to return
    
    Returns:
        List of YouTube video URLs
    """
    return get_viral_urls_from_last_month(topic, details, limit)


def _get_tavily_urls(topic: str, details: str, limit: int = 2) -> list[str]:
    """
    Get viral Tavily URLs from the last month.
    
    Args:
        topic: General topic category
        details: Specific details or sub-topics
        limit: Number of URLs to return
    
    Returns:
        List of URLs from Tavily search results
    """
    return get_viral_urls_from_last_month(topic, details, limit)


def _get_reddit_urls(topic: str, details: str, limit: int = 2) -> list[str]:
    """
    Get viral Reddit URLs from the last month.
    
    Args:
        topic: General topic category
        details: Specific details or sub-topics
        limit: Number of URLs to return
    
    Returns:
        List of Reddit post URLs (external URLs from posts, not Reddit permalinks)
    """
    logger.info(f"Searching Reddit for viral posts: {topic}, {details}")
    
    reddit = get_reddit_client()
    if not reddit:
        logger.warning("Reddit client not available")
        return []
    
    try:
        # Combine topic and details for search query
        query = f"{topic} {details}".strip() if details else topic
        
        # Search Reddit posts, sorted by hot (viral) or top
        posts = search_reddit_posts(query, limit=limit * 5, sort="hot")
        
        # Filter posts from last month and prioritize by score (viral)
        urls = []
        for post in posts:
            # Check if post is from last month
            created_utc = post.get("created_utc", 0)
            if not _is_within_last_month(created_utc):
                continue
            
            # Get external URL (not Reddit permalink)
            url = post.get("url", "")
            if url and "reddit.com" not in url and url not in urls:
                # Prioritize high-scoring posts (viral)
                score = post.get("score", 0)
                num_comments = post.get("num_comments", 0)
                
                # Only include posts with some engagement (viral indicators)
                if score > 10 or num_comments > 5:
                    urls.append(url)
                    logger.debug(f"Found Reddit URL: {url} (score: {score}, comments: {num_comments})")
                    
                    if len(urls) >= limit:
                        break
        
        logger.info(f"Found {len(urls)} Reddit URLs from last month")
        return urls[:limit]
        
    except Exception as e:
        logger.error(f"Error searching Reddit: {e}", exc_info=True)
        return []


def find_url_node(state: MessageGraph) -> dict:
    """
    Find 3 viral URLs from the last month from each service (Tavily, YouTube, Reddit).
    
    Args:
        state: The current graph state containing topic and details.
    
    Returns:
        dict: Updated state with combined URLs list.
    """

    MAX_URLS = 2
    topic = state.get("topic", "")
    details = state.get("details", "")
    
    if not topic:
        logger.warning("No topic found in state, cannot search for URLs")
        return {
            "urls": []
        }
    
    logger.info(f"Finding viral URLs for topic: {topic}, details: {details}")
    
    # Get URLs from each service (2 from each)
    tavily_urls = _get_tavily_urls(topic, details, limit=MAX_URLS)
    youtube_urls = _get_youtube_urls(topic, details, limit=MAX_URLS)
    reddit_urls = _get_reddit_urls(topic, details, limit=MAX_URLS)
    
    # Combine all URLs into a single list
    all_urls = tavily_urls + youtube_urls + reddit_urls
    
    total_urls = len(all_urls)
    
    logger.info(f"Found {total_urls} total URLs: {len(tavily_urls)} from Tavily, {len(youtube_urls)} from YouTube, {len(reddit_urls)} from Reddit")
    
    return {
        "urls": all_urls
    }

