# Node Tests

This directory contains comprehensive tests for all graph nodes in the content generation workflow.

## Test Files

- `test_topic_extraction_node.py` - Tests for topic extraction from user messages
- `test_youtube_search_node.py` - Tests for YouTube video search
- `test_tbd_search_node.py` - Tests for additional source search (Tavily)
- `test_transcript_fetch_node.py` - Tests for fetching video transcripts
- `test_core_text_extraction_node.py` - Tests for extracting core text from transcripts
- `test_relevance_rating_node.py` - Tests for rating text relevance
- `test_fact_verification_node.py` - Tests for fact verification
- `test_linkedin_generation_node.py` - Tests for LinkedIn post generation
- `test_instagram_tiktok_generation_node.py` - Tests for Instagram/TikTok script generation
- `test_output_node.py` - Tests for final output formatting

## Running Tests

Run all node tests:
```bash
pytest tests/node_tests/
```

Run a specific test file:
```bash
pytest tests/node_tests/test_topic_extraction_node.py
```

Run with verbose output:
```bash
pytest tests/node_tests/ -v
```

Run with coverage:
```bash
pytest tests/node_tests/ --cov=src.graph.nodes
```

## Test Strategy

All tests use:
- **Mocks/Patches** for external dependencies (Tavily, YouTube, OpenAI chains)
- **Fixtures** for common test data (sample states, mock results)
- **Edge case testing** (empty inputs, missing fields, failures)
- **Output validation** (structure, content, message types)

## Test Coverage

Each node test covers:
1. Successful execution with valid inputs
2. Handling of empty/missing inputs
3. Edge cases (partial failures, empty results)
4. Output structure validation
5. Message type validation (AIMessage, HumanMessage)

