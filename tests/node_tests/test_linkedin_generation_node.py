"""
Tests for LinkedIn generation node.
"""

import pytest
from unittest.mock import patch, Mock
from langchain_core.messages import AIMessage
from src.graph.nodes.linkedin_generation_node import linkedin_generation_node
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
        "generated_content": {},
    }


@pytest.fixture
def mock_linkedin_result():
    """Mock result from LinkedIn generation chain."""
    mock = Mock()
    mock.content = "This is a professional LinkedIn post about AI and machine learning."
    return mock


def test_linkedin_generation_node_success(sample_state, mock_linkedin_result):
    """Test successful LinkedIn generation."""
    with patch("src.graph.nodes.linkedin_generation_node.linkedin_generation_chain") as mock_chain:
        mock_chain.invoke.return_value = mock_linkedin_result
        
        result = linkedin_generation_node(sample_state)
        
        # Verify chain was called with correct parameters
        call_args = mock_chain.invoke.call_args[0][0]
        assert call_args["topic"] == "tech"
        assert call_args["details"] == "AI and machine learning"
        assert "Verified fact 1" in call_args["source_content"]
        assert "Verified fact 2" in call_args["source_content"]
        
        # Verify output
        assert "generated_content" in result
        assert "messages" in result
        assert result["generated_content"]["linkedin"] == mock_linkedin_result.content
        assert "LinkedIn post generated" in result["messages"][0].content


def test_linkedin_generation_node_existing_content(sample_state, mock_linkedin_result):
    """Test LinkedIn generation with existing generated_content."""
    sample_state["generated_content"] = {"instagram_tiktok": "Some existing content"}
    
    with patch("src.graph.nodes.linkedin_generation_node.linkedin_generation_chain") as mock_chain:
        mock_chain.invoke.return_value = mock_linkedin_result
        
        result = linkedin_generation_node(sample_state)
        
        # Should preserve existing content
        assert "instagram_tiktok" in result["generated_content"]
        assert result["generated_content"]["linkedin"] == mock_linkedin_result.content


def test_linkedin_generation_node_empty_verified_texts():
    """Test LinkedIn generation with empty verified texts."""
    state = {
        "verified_texts": [],
        "topic": "tech",
        "details": "AI",
        "generated_content": {},
    }
    
    with patch("src.graph.nodes.linkedin_generation_node.linkedin_generation_chain") as mock_chain:
        mock_result = Mock()
        mock_result.content = "LinkedIn post"
        mock_chain.invoke.return_value = mock_result
        
        result = linkedin_generation_node(state)
        
        # Should still generate content with empty source
        assert mock_chain.invoke.call_args[0][0]["source_content"] == ""
        assert result["generated_content"]["linkedin"] == "LinkedIn post"


def test_linkedin_generation_node_missing_fields():
    """Test LinkedIn generation with missing fields."""
    state = {
        "verified_texts": ["Some text"],
        "generated_content": {},
    }
    
    with patch("src.graph.nodes.linkedin_generation_node.linkedin_generation_chain") as mock_chain:
        mock_result = Mock()
        mock_result.content = "Post"
        mock_chain.invoke.return_value = mock_result
        
        result = linkedin_generation_node(state)
        
        # Should use empty strings for missing topic/details
        call_args = mock_chain.invoke.call_args[0][0]
        assert call_args["topic"] == ""
        assert call_args["details"] == ""

