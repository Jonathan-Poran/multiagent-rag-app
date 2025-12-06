"""
Tests for YouTube service.
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

# Mock the config imports that cause circular dependencies
sys.modules['src.config.setup_server'] = MagicMock()
sys.modules['src.api'] = MagicMock()
sys.modules['src.api.routes'] = MagicMock()
sys.modules['src.services.graph_service'] = MagicMock()

# Now import the YouTube service
from src.services.youtube_service import get_youtube_client, search_youtube_videos, fetch_transcript


class TestGetYouTubeClient:
    """Tests for get_youtube_client function."""
    
    def test_client_success(self):
        """Test can get client by env params using real API key."""
        # Reset the global client cache
        import src.services.youtube_service
        src.services.youtube_service._youtube_client = None
        
        # Get real API key from environment
        real_api_key = os.environ.get("YOUTUBE_API_KEY", "")
        
        if not real_api_key:
            pytest.skip("YOUTUBE_API_KEY not set in environment - skipping real client test")
        
        # Update settings directly with real API key (settings already reads from env, but we ensure it's set)
        import src.services.youtube_service
        from src.config.settings import settings
        settings.youtube_api_key = real_api_key
        
        # Execute - this tests the real path that uses settings from environment
        client = get_youtube_client()
        
        # Assert - client should be created successfully with real API key
        assert client is not None
        
        # Actually test the API key by making a real API call
        try:
            response = client.search().list(
                q="test",
                part="snippet",
                type="video",
                maxResults=1
            ).execute()
            # If we get here, the API key is valid
            assert "items" in response
        except Exception as e:
            # If API call fails, the key might be invalid
            pytest.fail(f"YouTube API key validation failed: {e}")
    
    def test_no_api_key(self):
        """Test that if there's no API key, the right message is raised (returns None)."""
        # Reset the global client cache
        import src.services.youtube_service
        src.services.youtube_service._youtube_client = None
        
        with patch('src.services.youtube_service.settings') as mock_settings:
            # Setup - no API key
            mock_settings.youtube_api_key = ""
            
            # Execute
            client = get_youtube_client()
            
            # Assert - should return None when no API key
            assert client is None
             
    def test_client_singleton(self):
        """Test that 2 get client calls return the same instance."""
        # Reset the global client cache
        import src.services.youtube_service
        src.services.youtube_service._youtube_client = None
        
        with patch('src.services.youtube_service.settings') as mock_settings, \
             patch('googleapiclient.discovery.build') as mock_build:
            
            # Setup
            mock_settings.youtube_api_key = "test_api_key"
            mock_client = MagicMock()
            mock_build.return_value = mock_client
            
            # Execute - call twice
            client1 = get_youtube_client()
            client2 = get_youtube_client()
            
            # Assert - should be the same instance and build should only be called once
            assert client1 is not None
            assert client2 is not None
            assert client1 is client2
            assert mock_build.call_count == 1