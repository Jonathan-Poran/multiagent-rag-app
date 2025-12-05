"""
Find URL node - finds 2 viral URLs from the last month from each service (Tavily, YouTube, Reddit).
"""

from datetime import datetime, timedelta
from langchain_core.messages import AIMessage
from src.graph.state import MessageGraph
from src.services.youtube_service import get_youtube_client
from src.services.tavily_service import get_tavily_client, search_tavily
from src.services.reddit_service import get_reddit_client, search_reddit_posts
from src.config.logger import get_logger


logger = get_logger("FindURL")


def _get_last_month_timestamp() -> str:
    """
    Get timestamp for one month ago

    Returns:
        formatted timestamp string
    """
    one_month_ago = datetime.utcnow() - timedelta(days=30)
    return one_month_ago.strftime("%Y-%m-%dT%H:%M:%SZ")


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
    logger.info(f"Searching YouTube for viral videos: {topic}, {details}")
    
    youtube = get_youtube_client()
    if not youtube:
        logger.warning("YouTube client not available")
        return []
    
    try:
        # Combine topic and details for search query
        query = f"{topic} {details}".strip() if details else topic
        
        # Get timestamp for last month
        published_after = _get_last_month_timestamp()
        
        # Search for videos from last month, ordered by view count (viral)
        search_response = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            order="viewCount",  # Order by view count (viral/popular)
            publishedAfter=published_after,  # Filter by date
            maxResults=limit * 3,  # Get more to filter for best ones
            videoDefinition="high",  # Prefer high quality videos
            videoDuration="medium",  # Medium length videos tend to be more viral
        ).execute()
        
        video_urls = []
        for item in search_response.get("items", []):
            video_id = item["id"]["videoId"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_urls.append(video_url)
            logger.debug(f"Found video: {item['snippet']['title']} - {video_url}")
            
            if len(video_urls) >= limit:
                break
        
        logger.info(f"Found {len(video_urls)} YouTube URLs from last month")
        return video_urls[:limit]
        
    except Exception as e:
        logger.error(f"Error searching YouTube: {e}", exc_info=True)
        return []


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
    logger.info(f"Searching Tavily for viral content: {topic}, {details}")
    
    client = get_tavily_client()
    if not client:
        logger.warning("Tavily client not available")
        return []
    
    try:
        # Combine topic and details for search query
        query = f"{topic} {details} viral trending".strip() if details else f"{topic} viral trending"
        
        # Search Tavily - it typically returns recent/viral content
        results = search_tavily(query, max_results=limit * 3)
        
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
        
        logger.info(f"Found {len(urls)} Tavily URLs")
        return urls[:limit]
        
    except Exception as e:
        logger.error(f"Error searching Tavily: {e}", exc_info=True)
        return []


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
    Find 2 viral URLs from the last month from each service (Tavily, YouTube, Reddit).
    
    Args:
        state: The current graph state containing topic and details.
    
    Returns:
        dict: Updated state with URLs from each service.
    """
    topic = state.get("topic", "")
    details = state.get("details", "")
    
    if not topic:
        logger.warning("No topic found in state, cannot search for URLs")
        return {
            "tavily_urls": [],
            "youtube_urls": [],
            "reddit_urls": [],
            "messages": [AIMessage(content="No topic found, cannot search for URLs")]
        }
    
    logger.info(f"Finding viral URLs for topic: {topic}, details: {details}")
    
    # Get URLs from each service (2 from each)
    tavily_urls = _get_tavily_urls(topic, details, limit=2)
    youtube_urls = _get_youtube_urls(topic, details, limit=2)
    reddit_urls = _get_reddit_urls(topic, details, limit=2)
    
    # Combine all URLs
    all_urls = {
        "tavily": tavily_urls,
        "youtube": youtube_urls,
        "reddit": reddit_urls
    }
    
    total_urls = len(tavily_urls) + len(youtube_urls) + len(reddit_urls)
    
    logger.info(f"Found {total_urls} total URLs: {len(tavily_urls)} from Tavily, {len(youtube_urls)} from YouTube, {len(reddit_urls)} from Reddit")
    
    # Format URLs for user response
    url_message = f"Found {total_urls} viral URLs from the last month:\n\n"
    if tavily_urls:
        url_message += f"**Tavily ({len(tavily_urls)} URLs):**\n"
        for url in tavily_urls:
            url_message += f"- {url}\n"
    if youtube_urls:
        url_message += f"\n**YouTube ({len(youtube_urls)} URLs):**\n"
        for url in youtube_urls:
            url_message += f"- {url}\n"
    if reddit_urls:
        url_message += f"\n**Reddit ({len(reddit_urls)} URLs):**\n"
        for url in reddit_urls:
            url_message += f"- {url}\n"
    
    return {
        "tavily_urls": tavily_urls,
        "youtube_urls": youtube_urls,
        "reddit_urls": reddit_urls,
        "messages": [AIMessage(content=url_message)]
    }

