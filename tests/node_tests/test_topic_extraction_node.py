"""
Tests for topic extraction node.
"""

import sys
import pytest
from unittest.mock import Mock, MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage

# *** Mocking & Setup ***
# Prevent heavy or circular imports from graph.py
sys.modules['src.graph.graph'] = MagicMock()

# Ensure src.graph remains a package
try:
    import src.graph
except Exception:
    pass  # src.graph exists; its 'graph' submodule is mocked

# Mock chains module before importing the node
mock_chains = MagicMock()
sys.modules['src.graph.chains'] = mock_chains
sys.modules['src.graph.chains.chains'] = mock_chains

# Now import the topic extraction node safely
from src.graph.nodes.topic_extraction_node import topic_extraction_node

# ---------------------------------------------------------------------------
# Helper function for similarity scoring
# ---------------------------------------------------------------------------
def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts based on common words."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return 0.0
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    return len(intersection) / len(union) if union else 0.0


# ---------------------------------------------------------------------------
# TEST 1
# ---------------------------------------------------------------------------
def test_topic_extraction_node_regular_input_with_details():
    """
    Test 1: Input text with topic and sub-topic details.
    Check correct topic + 70% detail similarity.
    """
    input_text = "I want to create content about technology, specifically about AI and machine learning"
    expected_topic = "tech"
    input_details = "AI and machine learning"

    state = {
        "messages": [HumanMessage(content=input_text)],
        "topic": None,
        "details": None,
    }

    with patch("src.graph.nodes.topic_extraction_node.topic_extraction_chain") as mock_chain:
        mock_result = Mock()
        mock_result.topic = expected_topic
        mock_result.details = "AI and machine learning"
        mock_chain.invoke.return_value = mock_result

        result = topic_extraction_node(state)

        mock_chain.invoke.assert_called_once_with({"messages": state["messages"]})

        assert result["topic"] == expected_topic

        similarity = calculate_similarity(input_details, result["details"])
        assert similarity >= 0.7, (
            f"Expected ≥70% similarity. Got {similarity:.2%}. "
            f"Input details: {input_details}, Output: {result['details']}"
        )

        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], AIMessage)
        assert expected_topic in result["messages"][0].content.lower()


# ---------------------------------------------------------------------------
# TEST 2
# ---------------------------------------------------------------------------
def test_topic_extraction_node_input_without_details():
    """
    Test 2: Input without details should return topic + empty details.
    """
    input_text = "I want to create content about sports"

    state = {
        "messages": [HumanMessage(content=input_text)],
        "topic": None,
        "details": None,
    }

    with patch("src.graph.nodes.topic_extraction_node.topic_extraction_chain") as mock_chain:
        mock_result = Mock()
        mock_result.topic = "sports"
        mock_result.details = ""
        mock_chain.invoke.return_value = mock_result

        result = topic_extraction_node(state)

        assert result["topic"] == "sports"
        assert result["details"] == ""
        assert len(result["messages"]) == 1
        assert "sports" in result["messages"][0].content.lower()


# ---------------------------------------------------------------------------
# TEST 3
# ---------------------------------------------------------------------------
def test_topic_extraction_node_nonsensical_text():
    """
    Test 3: Nonsensical input → empty topic → friendly message asking for clarification.
    """
    text = "asdfghjkl qwertyuiop zxcvbnm 123456789 !@#$%^&*()"

    state = {
        "messages": [HumanMessage(content=text)],
        "topic": None,
        "details": None,
    }

    with patch("src.graph.nodes.topic_extraction_node.topic_extraction_chain") as mock_chain:
        mock_result = Mock()
        mock_result.topic = ""
        mock_result.details = ""
        mock_chain.invoke.return_value = mock_result

        result = topic_extraction_node(state)

        # Verify empty topic and details
        assert result["topic"] == ""
        assert result["details"] == ""
        
        # Verify friendly message was returned
        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], AIMessage)
        message_content = result["messages"][0].content.lower()
        
        # Check that the message asks for clarification
        # The actual message contains "could you please specify what kind of content you want to create?"
        assert "specify what kind of content" in message_content

# ---------------------------------------------------------------------------
# TEST 4 - Additional test for empty topic behavior
# ---------------------------------------------------------------------------
def test_topic_extraction_node_empty_topic_returns_friendly_message():
    """
    Test 4: When topic extraction returns empty string, node should return friendly message.
    """
    input_text = "Hello, how are you?"

    state = {
        "messages": [HumanMessage(content=input_text)],
        "topic": None,
        "details": None,
    }

    with patch("src.graph.nodes.topic_extraction_node.topic_extraction_chain") as mock_chain:
        mock_result = Mock()
        mock_result.topic = ""  # Empty topic
        mock_result.details = ""
        mock_chain.invoke.return_value = mock_result

        result = topic_extraction_node(state)

        # Verify empty topic
        assert result["topic"] == ""
        assert result["details"] == ""
        
        # Verify friendly message
        assert len(result["messages"]) == 1
        message = result["messages"][0]
        assert isinstance(message, AIMessage)
        
        # Check message contains helpful content
        content = message.content
        assert len(content) > 50  # Should be a substantial message
        assert "topic" in content.lower() or "content" in content.lower()
        assert "example" in content.lower() or "could" in content.lower() or "would" in content.lower()
