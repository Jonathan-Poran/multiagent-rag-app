"""
Tests for Reddit service.
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Mock modules to avoid circular imports before importing anything
mock_graph = MagicMock()
mock_nodes = MagicMock()
mock_youtube_node = MagicMock()

sys.modules['src.graph'] = MagicMock()
sys.modules['src.graph.graph'] = mock_graph
sys.modules['src.graph.nodes'] = mock_nodes
sys.modules['src.graph.nodes.youtube_search_node'] = mock_youtube_node
sys.modules['src.config.setup_server'] = MagicMock()
sys.modules['src.api'] = MagicMock()
sys.modules['src.api.routes'] = MagicMock()
sys.modules['src.services.graph_service'] = MagicMock()

# Now import the Reddit service
from src.services.reddit_service import get_reddit_client, search_reddit_posts, get_subreddit_posts, get_post_comments


class TestGetRedditClient:
    """Tests for get_reddit_client function."""
    
    def test_client_success(self):
        """Test can get client by env params using real Reddit credentials."""
        # Reset the global client cache
        import src.services.reddit_service
        src.services.reddit_service._reddit_client = None
        
        # Get real Reddit credentials from environment
        real_client_id = os.environ.get("REDDIT_CLIENT_ID", "")
        real_client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")
        
        if not real_client_id or not real_client_secret:
            pytest.skip("REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET not set in environment - skipping real client test")
        
        # Update settings directly with real credentials (settings already reads from env, but we ensure it's set)
        import src.services.reddit_service
        from src.config.settings import settings
        settings.reddit_client_id = real_client_id
        settings.reddit_client_secret = real_client_secret
        
        # Execute - this tests the real path that uses settings from environment
        client = get_reddit_client()
        
        # Assert - client should be created successfully with real credentials
        assert client is not None
        
        # Actually test the Reddit credentials by making a real API call
        try:
            # Access a public subreddit (doesn't require authentication, but validates client setup)
            subreddit = client.subreddit("test")
            # Try to get basic info - this validates the client is working
            _ = subreddit.display_name
            # If we get here, the credentials are valid and client works
            assert True
        except Exception as e:
            # If API call fails, the credentials might be invalid
            pytest.fail(f"Reddit API credentials validation failed: {e}")
    
    def test_no_api_key(self):
        """Test that if there's no API key, the right message is raised (returns None)."""
        # Reset the global client cache
        import src.services.reddit_service
        src.services.reddit_service._reddit_client = None
        
        with patch('src.services.reddit_service.settings') as mock_settings:
            # Setup - no client ID
            mock_settings.reddit_client_id = ""
            mock_settings.reddit_client_secret = "test_secret"
            
            # Execute
            client = get_reddit_client()
            
            # Assert - should return None when no client ID
            assert client is None
    
    def test_client_singleton(self):
        """Test that 2 get client calls return the same instance."""
        # Reset the global client cache
        import src.services.reddit_service
        src.services.reddit_service._reddit_client = None
        
        with patch('src.services.reddit_service.settings') as mock_settings, \
             patch('praw.Reddit') as mock_reddit_class:
            
            # Setup
            mock_settings.reddit_client_id = "test_client_id"
            mock_settings.reddit_client_secret = "test_client_secret"
            mock_settings.reddit_user_agent = "test_user_agent"
            
            mock_client_instance = MagicMock()
            mock_reddit_class.return_value = mock_client_instance
            
            # Execute - call twice
            client1 = get_reddit_client()
            client2 = get_reddit_client()
            
            # Assert - should be the same instance and Reddit should only be called once
            assert client1 is not None
            assert client2 is not None
            assert client1 is client2
            assert mock_reddit_class.call_count == 1

