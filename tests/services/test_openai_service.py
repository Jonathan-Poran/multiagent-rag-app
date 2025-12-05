"""
Tests for OpenAI service.
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage

# Mock modules to avoid circular imports before importing anything
mock_graph = MagicMock()
mock_nodes = MagicMock()
mock_consts = MagicMock()
mock_consts.PREDEFINED_TOPICS = ["tech", "sports", "fashion", "food", "travel"]

sys.modules['src.graph'] = MagicMock()
sys.modules['src.graph.graph'] = mock_graph
sys.modules['src.graph.nodes'] = mock_nodes
sys.modules['src.graph.consts'] = mock_consts
sys.modules['src.config.setup_server'] = MagicMock()
sys.modules['src.api'] = MagicMock()
sys.modules['src.api.routes'] = MagicMock()
sys.modules['src.services.graph_service'] = MagicMock()

# Now import the OpenAI service
from src.services.openai_service import (
    get_openai_client,
    get_openai_structured_client,
    get_openai_relevance_client,
    extract_topic_and_details,
    rate_relevance,
    generate_linkedin_content,
    generate_video_script
)


class TestGetOpenAIClient:
    """Tests for get_openai_client function."""
    
    def test_client_success(self):
        """Test can get client by env params using real API key."""
        # Reset the global client cache
        import src.services.openai_service
        src.services.openai_service._openai_client = None
        
        # Get real API key from environment
        real_api_key = os.environ.get("OPENAI_API_KEY", "")
        
        if not real_api_key:
            pytest.skip("OPENAI_API_KEY not set in environment - skipping real client test")
        
        # Update settings directly with real API key
        from src.config.settings import settings
        settings.openai_api_key = real_api_key
        
        # Execute - this tests the real path that uses settings from environment
        client = get_openai_client()
        
        # Assert - client should be created successfully with real API key
        assert client is not None
        
        # Actually test the API key by making a real API call
        try:
            from langchain_core.messages import HumanMessage
            response = client.invoke([HumanMessage(content="Say 'test' and nothing else")])
            # If we get here, the API key is valid
            assert response is not None
            assert hasattr(response, 'content') or hasattr(response, 'text')
        except Exception as e:
            # If API call fails, the key might be invalid
            pytest.fail(f"OpenAI API key validation failed: {e}")
    
    def test_no_api_key(self):
        """Test that if there's no API key, the right message is raised (returns None)."""
        # Reset the global client cache
        import src.services.openai_service
        src.services.openai_service._openai_client = None
        
        with patch('src.services.openai_service.settings') as mock_settings:
            # Setup - no API key
            mock_settings.openai_api_key = ""
            
            # Execute
            client = get_openai_client()
            
            # Assert - should return None when no API key
            assert client is None
    
    def test_client_singleton(self):
        """Test that 2 get client calls return the same instance."""
        # Reset the global client cache
        import src.services.openai_service
        src.services.openai_service._openai_client = None
        
        with patch('src.services.openai_service.settings') as mock_settings, \
             patch('src.services.openai_service.ChatOpenAI') as mock_chat_openai:
            
            # Setup
            mock_settings.openai_api_key = "test_api_key"
            mock_client_instance = MagicMock()
            mock_chat_openai.return_value = mock_client_instance
            
            # Execute - call twice
            client1 = get_openai_client()
            client2 = get_openai_client()
            
            # Assert - should be the same instance and ChatOpenAI should only be called once
            assert client1 is not None
            assert client2 is not None
            assert client1 is client2
            assert mock_chat_openai.call_count == 1


