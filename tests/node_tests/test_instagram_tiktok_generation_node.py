"""
Tests for Instagram/TikTok generation node.
"""

import pytest
from unittest.mock import patch, Mock
from langchain_core.messages import AIMessage
from src.graph.nodes.instagram_tiktok_generation_node import instagram_tiktok_generation_node
from src.graph.state import MessageGraph


@pytest.fixture
def sample_state():
    """Create a sample state with verified texts, topic, and details."""
    return {
        "verified_texts": [
            "Verified fact 1 about AI",
            "Verified fact 2 about machine learning",
        ],
        "topic": "tech",
        "details": "AI and machine learning",
        "generated_content": {"linkedin": "LinkedIn post"},
    }


@pytest.fixture
def mock_instagram_tiktok_result():
    """Mock result from Instagram/TikTok generation chain."""
    mock = Mock()
    mock.content = """[0:00-0:05] Hook: Did you know AI is transforming everything?
[0:05-0:30] Main content: Here's what you need to know...
[0:30-0:45] Call to action: Follow for more tech insights!"""
    return mock


def test_instagram_tiktok_generation_node_success(sample_state, mock_instagram_tiktok_result):
    """Test successful Instagram/TikTok generation."""
    with patch("src.graph.nodes.instagram_tiktok_generation_node.instagram_tiktok_generation_chain") as mock_chain:
        mock_chain.invoke.return_value = mock_instagram_tiktok_result
        
        result = instagram_tiktok_generation_node(sample_state)
        
        # Verify chain was called with correct parameters
        call_args = mock_chain.invoke.call_args[0][0]
        assert call_args["topic"] == "tech"
        assert call_args["details"] == "AI and machine learning"
        assert "Verified fact 1" in call_args["source_content"]
        
        # Verify output
        assert "generated_content" in result
        assert "messages" in result
        assert result["generated_content"]["instagram_tiktok"] == mock_instagram_tiktok_result.content
        assert "Instagram/TikTok script generated" in result["messages"][0].content
        # Should preserve existing LinkedIn content
        assert result["generated_content"]["linkedin"] == "LinkedIn post"


def test_instagram_tiktok_generation_node_existing_content(sample_state, mock_instagram_tiktok_result):
    """Test Instagram/TikTok generation with existing generated_content."""
    with patch("src.graph.nodes.instagram_tiktok_generation_node.instagram_tiktok_generation_chain") as mock_chain:
        mock_chain.invoke.return_value = mock_instagram_tiktok_result
        
        result = instagram_tiktok_generation_node(sample_state)
        
        # Should preserve existing LinkedIn content
        assert "linkedin" in result["generated_content"]
        assert result["generated_content"]["linkedin"] == "LinkedIn post"
        assert "instagram_tiktok" in result["generated_content"]


def test_instagram_tiktok_generation_node_empty_verified_texts():
    """Test Instagram/TikTok generation with empty verified texts."""
    state = {
        "verified_texts": [],
        "topic": "tech",
        "details": "AI",
        "generated_content": {},
    }
    
    with patch("src.graph.nodes.instagram_tiktok_generation_node.instagram_tiktok_generation_chain") as mock_chain:
        mock_result = Mock()
        mock_result.content = "Video script"
        mock_chain.invoke.return_value = mock_result
        
        result = instagram_tiktok_generation_node(state)
        
        # Should still generate content with empty source
        assert mock_chain.invoke.call_args[0][0]["source_content"] == ""
        assert result["generated_content"]["instagram_tiktok"] == "Video script"

