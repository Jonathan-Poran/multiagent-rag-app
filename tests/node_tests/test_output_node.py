"""
Tests for output node.
"""

import pytest
from langchain_core.messages import AIMessage
from src.graph.nodes.output_node import output_node
from src.graph.state import MessageGraph


@pytest.fixture
def sample_state():
    """Create a sample state with generated content."""
    return {
        "generated_content": {
            "linkedin": "This is a LinkedIn post about AI.",
            "instagram_tiktok": "This is an Instagram/TikTok script about AI.",
        },
        "topic": "tech",
        "details": "AI and machine learning",
    }


def test_output_node_success(sample_state):
    """Test successful output formatting."""
    result = output_node(sample_state)
    
    # Verify output structure
    assert "messages" in result
    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], AIMessage)
    
    # Verify content includes all fields
    content = result["messages"][0].content
    assert "LinkedIn Post" in content
    assert "Instagram/TikTok Script" in content
    assert "This is a LinkedIn post about AI." in content
    assert "This is an Instagram/TikTok script about AI." in content
    assert "tech" in content
    assert "AI and machine learning" in content


def test_output_node_missing_content():
    """Test output node with missing generated content."""
    state = {
        "generated_content": {},
        "topic": "tech",
        "details": "AI",
    }
    
    result = output_node(state)
    
    content = result["messages"][0].content
    # Should handle missing content gracefully
    assert "LinkedIn Post" in content
    assert "Instagram/TikTok Script" in content
    assert "tech" in content
    assert "AI" in content


def test_output_node_partial_content():
    """Test output node with partial content."""
    state = {
        "generated_content": {
            "linkedin": "LinkedIn post only",
        },
        "topic": "tech",
        "details": "AI",
    }
    
    result = output_node(state)
    
    content = result["messages"][0].content
    assert "LinkedIn post only" in content
    # Instagram/TikTok should be empty
    assert "Instagram/TikTok Script" in content


def test_output_node_missing_topic_details():
    """Test output node with missing topic/details."""
    state = {
        "generated_content": {
            "linkedin": "Post",
            "instagram_tiktok": "Script",
        },
    }
    
    result = output_node(state)
    
    content = result["messages"][0].content
    # Should handle missing topic/details gracefully
    assert "Post" in content
    assert "Script" in content
    assert "Topic:" in content
    assert "Details:" in content


def test_output_node_empty_state():
    """Test output node with completely empty state."""
    state = {}
    
    result = output_node(state)
    
    # Should still produce output message
    assert "messages" in result
    assert len(result["messages"]) == 1
    content = result["messages"][0].content
    assert "LinkedIn Post" in content
    assert "Instagram/TikTok Script" in content

