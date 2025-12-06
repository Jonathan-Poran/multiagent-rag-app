"""
Tavily API Playground
Explore and test Tavily API functionality to understand what it returns and how it works.

To run this script:
python src/scripts/tavily_playground.py
"""

import sys
import json
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Lazy imports to avoid circular dependencies
def _get_settings():
    """Get settings without triggering circular imports."""
    from src.config.settings import settings
    return settings

def _get_tavily_client():
    """Get Tavily client using lazy import."""
    from tavily import TavilyClient
    settings = _get_settings()
    
    if not settings.tavily_api_key:
        print("⚠️  TAVILY_API_KEY not configured in .env file")
        return None
    
    try:
        return TavilyClient(api_key=settings.tavily_api_key)
    except Exception as e:
        print(f"✗ Failed to initialize Tavily client: {e}")
        return None

def _search_tavily(query: str, max_results: int = 5):
    """Search Tavily using lazy import."""
    client = _get_tavily_client()
    if not client:
        return []
    
    try:
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced"
        )
        return response.get("results", [])
    except Exception as e:
        print(f"✗ Tavily search failed: {e}")
        return []


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_tavily_connection():
    """Test if Tavily client can be initialized."""
    
    settings = _get_settings()
    client = _get_tavily_client()
    if client:
        print("✓ Tavily client initialized successfully")
        print(f"  API Key configured: {'Yes' if settings.tavily_api_key else 'No'}")
        return True
    else:
        print("✗ Failed to initialize Tavily client")
        print("  Check your TAVILY_API_KEY in .env file")
        return False


def test_basic_search(query: str = "latest AI developments 2024"):
    """Test basic Tavily search functionality."""
    print_section(f"Basic Search: '{query}'")
    
    results = _search_tavily(query, max_results=3)
    
    if not results:
        print("✗ No results returned")
        return
    
    print(f"Found {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"  Title: {result.get('title', 'N/A')}")
        print(f"  URL: {result.get('url', 'N/A')}")
        print(f"  Content: {result.get('content', 'N/A')[:200]}...")
        print(f"  Score: {result.get('score', 'N/A')}")
        print()


def test_search_with_topic(topic: str = "tech", details: str = "machine learning"):
    """Test search with specific topic and details."""
    print_section(f"Topic-Based Search: {topic} - {details}")
    
    query = f"{topic} {details}"
    results = _search_tavily(query, max_results=5)
    
    if not results:
        print("✗ No results returned")
        return
    
    print(f"Query: '{query}'")
    print(f"Found {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.get('title', 'N/A')}")
        print(f"   {result.get('url', 'N/A')}")
        print()


def test_extract_core_text(url: str, topic: str = "tech"):
    """Test Tavily's extract functionality to get core text from a URL."""
    print_section(f"Extract Core Text from URL: {url}")
    
    client = _get_tavily_client()
    if not client:
        print("✗ Tavily client not available")
        return
    
    try:
        # Tavily extract API call
        response = client.extract(
            url=url,
            query=topic,
        )
        
        print(f"Extracted content for topic '{topic}':\n")
        print(f"Content: {response.get('content', 'N/A')[:500]}...")
        print(f"Title: {response.get('title', 'N/A')}")
        print(f"URL: {response.get('url', 'N/A')}")
        
    except Exception as e:
        print(f"✗ Error during extraction: {e}")


def test_fact_verification(claim: str):
    """Test Tavily's fact verification functionality."""
    print_section(f"Fact Verification: '{claim}'")
    
    client = _get_tavily_client()
    if not client:
        print("✗ Tavily client not available")
        return
    
    try:
        # Tavily search for fact verification
        response = client.search(
            query=claim,
            search_depth="advanced",
            max_results=5,
        )
        
        results = response.get('results', [])
        print(f"Found {len(results)} sources to verify the claim:\n")
        
        for i, result in enumerate(results, 1):
            print(f"Source {i}:")
            print(f"  Title: {result.get('title', 'N/A')}")
            print(f"  URL: {result.get('url', 'N/A')}")
            print(f"  Content snippet: {result.get('content', 'N/A')[:150]}...")
            print(f"  Score: {result.get('score', 'N/A')}")
            print()
            
    except Exception as e:
        print(f"✗ Error during fact verification: {e}")


def test_search_different_topics():
    """Test searches across different predefined topics."""
    print_section("Testing Different Topics")
    
    topics = [
        ("sports", "football european league"),
        ("tech", "new langgraph tools"),
        ("fashion", "sustainable fashion trends"),
        ("food", "Italian pasta recipes"),
    ]
    
    for topic, details in topics:
        print(f"\n--- {topic.upper()}: {details} ---")
        results = _search_tavily(f"{topic} {details}", max_results=2)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result.get('title', 'N/A')}")
        else:
            print("  No results")


def show_raw_response(query: str = "Python programming"):
    """Show the raw JSON response from Tavily to understand the data structure."""
    print_section(f"Raw Response Structure: '{query}'")
    
    client = _get_tavily_client()
    if not client:
        print("✗ Tavily client not available")
        return
    
    try:
        response = client.search(
            query=query,
            max_results=2,
        )
        
        print("Raw JSON Response:")
        print(json.dumps(response, indent=2, default=str))
        
    except Exception as e:
        print(f"✗ Error: {e}")


def interactive_search():
    """Interactive mode to test custom searches."""
    print_section("Interactive Search Mode")
    
    print("Enter search queries (type 'quit' to exit):\n")
    
    while True:
        query = input("Search query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if not query:
            continue
        
        print(f"\nSearching for: '{query}'...\n")
        results = _search_tavily(query, max_results=3)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"{i}. {result.get('title', 'N/A')}")
                print(f"   {result.get('url', 'N/A')}")
                print(f"   {result.get('content', 'N/A')[:150]}...")
                print()
        else:
            print("No results found.\n")


def main():
    """Run all playground functions."""
    print("\n" + "=" * 80)
    print("  TAVILY API PLAYGROUND")
    print("=" * 80)
    
    # Test connection
    if not test_tavily_connection():
        print("\n⚠️  Cannot proceed without Tavily connection. Check your API key.")
        return
    
    # Basic search test
    #test_basic_search("latest AI developments 2024")
    
    # Topic-based search
    #test_search_with_topic("tech", "machine learning")
    
    # Different topics
    #test_search_different_topics()
    
    # Extract core text (if you have a URL)
    # Uncomment and provide a URL to test:
    # test_extract_core_text("https://example.com/article", "tech")
    
    # Fact verification
    #test_fact_verification("Python is a programming language")
    
    # Show raw response structure
    #show_raw_response("Python programming")
    
    # Interactive mode (uncomment to enable)
    # interactive_search()

    results = _search_tavily("give me the latest youtube videos about tips for coping with ADHD", max_results=3)
    if results:
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.get('title', 'N/A')}")
            print(f"   {result.get('url', 'N/A')}")
            print(f"   {result.get('content', 'N/A')[:150]}...")
            print()
        
        # Extract and summarize tips for handling ADHD disturbances during the day
        print_section("Extracting Tips for Handling ADHD Disturbances During the Day")
        
        # Use the first result's URL
        if results and results[0].get('url'):
            url = results[0].get('url')
            print(f"Extracting from: {url}\n")
            
            client = _get_tavily_client()
            if client:
                try:
                    # Use Tavily extract API to get relevant content
                    extract_query = "tips for handling ADHD disturbances during the day, coping strategies, daily management"
                    response = client.extract(
                        url=url,
                        query=extract_query,
                    )
                    
                    print("Extracted Summary:\n")
                    print("=" * 80)
                    content = response.get('content', 'N/A')
                    if content and content != 'N/A':
                        print(content)
                    else:
                        print("No content extracted. Trying alternative extraction method...")
                        # Fallback: use search with the URL and query
                        search_response = client.search(
                            query=f"ADHD disturbances during day tips {extract_query}",
                            max_results=3,
                            search_depth="advanced"
                        )
                        if search_response.get('results'):
                            print("\nAlternative results found:")
                            for i, alt_result in enumerate(search_response.get('results', [])[:3], 1):
                                print(f"\n{i}. {alt_result.get('title', 'N/A')}")
                                print(f"   {alt_result.get('url', 'N/A')}")
                                print(f"   {alt_result.get('content', 'N/A')[:300]}...")
                    print("=" * 80)
                    
                except Exception as e:
                    print(f"✗ Error during extraction: {e}")
                    print(f"   Trying to extract from search results content instead...\n")
                    # Fallback: summarize from the search result content
                    if results[0].get('content'):
                        content = results[0].get('content')
                        print("Content from search result:")
                        print("=" * 80)
                        # Look for tips or strategies in the content
                        if 'tip' in content.lower() or 'strategy' in content.lower() or 'coping' in content.lower():
                            print(content[:1000] + "..." if len(content) > 1000 else content)
                        else:
                            print(content[:500] + "...")
                        print("=" * 80)
            else:
                print("✗ Tavily client not available for extraction")
        else:
            print("✗ No URL found in search results for extraction")
    else:
        print("No results found.\n")

    
    print_section("Playground Complete!")


if __name__ == "__main__":
    main()

