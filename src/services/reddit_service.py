"""
Reddit API service for searching Reddit posts and comments.
"""

from typing import List, Optional, Dict, Any
from src.config.logger import get_logger
from src.config.settings import settings

logger = get_logger("Reddit")

_reddit_client: Optional[Any] = None


def get_reddit_client() -> Optional[Any]:
    """
    Get or create Reddit API client instance.
    Uses singleton pattern to reuse the same client instance.
    
    Returns:
        Reddit API client instance (praw.Reddit) or None if credentials are not configured.
    """
    global _reddit_client
    
    if _reddit_client is not None:
        return _reddit_client
    
    # Check if Reddit credentials are configured
    if not settings.reddit_client_id or not settings.reddit_client_secret:
        logger.warning("REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET not configured")
        return None
    
    try:
        import praw
        _reddit_client = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent or "multiagent-rag-app/1.0"
        )
        logger.info("Reddit client initialized successfully")
        return _reddit_client
    except ImportError:
        logger.error("praw not installed. Install with: pip install praw")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Reddit client: {e}", exc_info=True)
        return None


def search_reddit_posts(query: str, subreddit: Optional[str] = None, limit: int = 10, sort: str = "hot") -> List[Dict[str, Any]]:
    """
    Search Reddit for posts matching the query.
    
    Args:
        query: Search query string
        subreddit: Optional subreddit name to search within (e.g., "python", "technology")
        limit: Maximum number of posts to return
        sort: Sort order - "hot", "new", "top", "relevance", "comments"
    
    Returns:
        List of dictionaries containing post information (title, url, score, num_comments, selftext, etc.)
    """
    logger.info(f"Searching Reddit for: {query}, subreddit: {subreddit or 'all'}")
    
    reddit = get_reddit_client()
    
    if not reddit:
        logger.warning("Reddit client not available - Reddit search disabled")
        logger.info("To enable Reddit search, add REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET to your .env file")
        logger.info("Get your credentials from: https://www.reddit.com/prefs/apps")
        return []
    
    try:
        posts = []
        
        if subreddit:
            # Search within a specific subreddit
            subreddit_obj = reddit.subreddit(subreddit)
            if sort == "hot":
                results = subreddit_obj.hot(limit=limit)
            elif sort == "new":
                results = subreddit_obj.new(limit=limit)
            elif sort == "top":
                results = subreddit_obj.top(limit=limit, time_filter="all")
            else:
                # Use search for other sort options
                results = subreddit_obj.search(query, sort=sort, limit=limit)
        else:
            # Search all of Reddit
            results = reddit.subreddit("all").search(query, sort=sort, limit=limit)
        
        for post in results:
            post_data = {
                "title": post.title,
                "url": post.url,
                "permalink": f"https://www.reddit.com{post.permalink}",
                "score": post.score,
                "num_comments": post.num_comments,
                "selftext": post.selftext[:500] if post.selftext else "",  # Limit text length
                "subreddit": post.subreddit.display_name,
                "created_utc": post.created_utc,
                "author": str(post.author) if post.author else "[deleted]",
            }
            posts.append(post_data)
            logger.debug(f"Found post: {post.title[:50]}...")
        
        logger.info(f"Successfully found {len(posts)} Reddit posts")
        return posts
        
    except Exception as e:
        logger.error(f"Error searching Reddit: {e}", exc_info=True)
        return []


def get_subreddit_posts(subreddit: str, limit: int = 10, sort: str = "hot") -> List[Dict[str, Any]]:
    """
    Get posts from a specific subreddit.
    
    Args:
        subreddit: Subreddit name (e.g., "python", "technology")
        limit: Maximum number of posts to return
        sort: Sort order - "hot", "new", "top"
    
    Returns:
        List of dictionaries containing post information
    """
    logger.info(f"Fetching posts from r/{subreddit}, sort: {sort}")
    
    reddit = get_reddit_client()
    
    if not reddit:
        logger.warning("Reddit client not available")
        return []
    
    try:
        subreddit_obj = reddit.subreddit(subreddit)
        
        if sort == "hot":
            results = subreddit_obj.hot(limit=limit)
        elif sort == "new":
            results = subreddit_obj.new(limit=limit)
        elif sort == "top":
            results = subreddit_obj.top(limit=limit, time_filter="all")
        else:
            results = subreddit_obj.hot(limit=limit)  # Default to hot
        
        posts = []
        for post in results:
            post_data = {
                "title": post.title,
                "url": post.url,
                "permalink": f"https://www.reddit.com{post.permalink}",
                "score": post.score,
                "num_comments": post.num_comments,
                "selftext": post.selftext[:500] if post.selftext else "",
                "subreddit": post.subreddit.display_name,
                "created_utc": post.created_utc,
                "author": str(post.author) if post.author else "[deleted]",
            }
            posts.append(post_data)
        
        logger.info(f"Successfully fetched {len(posts)} posts from r/{subreddit}")
        return posts
        
    except Exception as e:
        logger.error(f"Error fetching subreddit posts: {e}", exc_info=True)
        return []


def get_post_comments(post_url: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get comments from a Reddit post.
    
    Args:
        post_url: Reddit post URL or permalink
        limit: Maximum number of top-level comments to return
    
    Returns:
        List of dictionaries containing comment information
    """
    logger.info(f"Fetching comments from post: {post_url}")
    
    reddit = get_reddit_client()
    
    if not reddit:
        logger.warning("Reddit client not available")
        return []
    
    try:
        submission = reddit.submission(url=post_url)
        submission.comments.replace_more(limit=0)  # Remove "more comments" placeholders
        
        comments = []
        for comment in submission.comments.list()[:limit]:
            if hasattr(comment, 'body'):  # Skip deleted/removed comments
                comment_data = {
                    "body": comment.body[:500] if comment.body else "",  # Limit text length
                    "score": comment.score,
                    "author": str(comment.author) if comment.author else "[deleted]",
                    "created_utc": comment.created_utc,
                }
                comments.append(comment_data)
        
        logger.info(f"Successfully fetched {len(comments)} comments")
        return comments
        
    except Exception as e:
        logger.error(f"Error fetching post comments: {e}", exc_info=True)
        return []

