"""
YouTube search and transcript fetching service.
"""

from typing import List, Optional, Any
from datetime import datetime, timedelta
from src.config.logger import get_logger
from src.config.settings import settings

logger = get_logger("YouTube")

_youtube_client: Optional[Any] = None


def get_youtube_client() -> Optional[Any]:
    """
    Get or create YouTube API client instance.
    Uses singleton pattern to reuse the same client instance.
    
    Returns:
        YouTube API client instance or None if API key is not configured.
    """
    global _youtube_client
    
    if _youtube_client is not None:
        return _youtube_client
    
    if not settings.youtube_api_key:
        logger.warning("YOUTUBE_API_KEY not configured")
        return None
    
    try:
        from googleapiclient.discovery import build
        _youtube_client = build("youtube", "v3", developerKey=settings.youtube_api_key)
        logger.info("YouTube client initialized successfully")
        return _youtube_client
    except ImportError:
        logger.error("googleapiclient.discovery not installed. Install with: pip install google-api-python-client")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize YouTube client: {e}", exc_info=True)
        return None


def search_youtube_videos(topic: str, details: str, max_results: int = 5) -> List[str]:
    """
    Search YouTube for recent and viral videos related to the topic.
    
    Args:
        topic: General topic category
        details: Specific details or sub-topics
        max_results: Maximum number of videos to return
    
    Returns:
        List of YouTube video URLs
    """
    logger.info(f"Searching YouTube for topic: {topic}, details: {details}")
    
    # Combine topic and details for search query
    query = f"{topic} {details}".strip() if details else topic
    
    # Get YouTube client
    youtube = get_youtube_client()
    
    if not youtube:
        logger.warning("YouTube client not available - YouTube search disabled")
        logger.info("To enable YouTube search, add YOUTUBE_API_KEY to your .env file")
        logger.info("Get your API key from: https://console.cloud.google.com/apis/credentials")
        return []
    
    try:
        # Search for videos
        search_response = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            order="viewCount",  # Order by view count (viral/popular videos)
            maxResults=max_results
        ).execute()
        
        video_urls = []
        for item in search_response.get("items", []):
            video_id = item["id"]["videoId"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_urls.append(video_url)
            logger.debug(f"Found video: {item['snippet']['title']} - {video_url}")
        
        logger.info(f"Successfully found {len(video_urls)} YouTube videos")
        return video_urls
        
    except Exception as e:
        logger.error(f"Error searching YouTube: {e}", exc_info=True)
        return []


def _get_last_month_timestamp() -> str:
    """
    Get timestamp for one month ago in ISO format for YouTube API.
    
    Returns:
        Formatted timestamp string (YYYY-MM-DDTHH:MM:SSZ)
    """
    one_month_ago = datetime.utcnow() - timedelta(days=30)
    return one_month_ago.strftime("%Y-%m-%dT%H:%M:%SZ")


def get_viral_urls_from_last_month(topic: str, details: str, limit: int = 2) -> List[str]:
    """
    Get viral YouTube URLs from the last month.
    
    Args:
        topic: General topic category
        details: Specific details or sub-topics
        limit: Number of URLs to return
    
    Returns:
        List of YouTube video URLs from the last month
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


def fetch_transcript(video_url: str) -> Optional[str]:
    """
    Fetch transcript for a YouTube video.
    
    Args:
        video_url: YouTube video URL
    
    Returns:
        Transcript text or None if unavailable
    """
    # TODO: Implement transcript fetching using youtube-transcript-api or similar
    logger.info(f"Fetching transcript for video: {video_url}")
    
    logger.warning("Transcript fetching not fully implemented - returning None")
    return None

