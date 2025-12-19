"""Tavily web search tool."""
from typing import List, Dict, Any, Optional
from tavily import TavilyClient
from tenacity import retry, stop_after_attempt, wait_exponential
import config
from backend.storage.cache import JSONCache


class WebSearchTool:
    """Tool for searching the web using Tavily API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Tavily client.
        
        Args:
            api_key: Tavily API key. If None, uses config.TAVILY_API_KEY
        """
        self.api_key = api_key or config.TAVILY_API_KEY
        self.client = TavilyClient(api_key=self.api_key)
        self.cache = JSONCache()
    
    @retry(
        stop=stop_after_attempt(config.MAX_RETRIES),
        wait=wait_exponential(multiplier=config.RETRY_DELAY, min=1, max=10)
    )
    def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Search the web for a query.
        
        Args:
            query: Search query string
            max_results: Maximum number of results. Defaults to config.MAX_SEARCH_RESULTS
            use_cache: Whether to use cached results if available
            
        Returns:
            Dictionary with search results containing:
            - results: List of search results with title, url, snippet, score
            - query: Original query
            - total_results: Number of results
        """
        max_results = max_results or config.MAX_SEARCH_RESULTS
        
        # Check cache
        if use_cache:
            cached = self.cache.get(f"search:{query}")
            if cached:
                return cached
        
        try:
            # Perform search (use basic depth for faster results)
            try:
                response = self.client.search(
                    query=query,
                    max_results=max_results,
                    search_depth="basic"  # Changed from "advanced" for speed
                )
            except Exception as e:
                # Fallback to basic search if advanced fails
                response = self.client.search(
                    query=query,
                    max_results=max_results,
                    search_depth="basic"
                )
            
            # Format results
            results = []
            for result in response.get('results', []):
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'snippet': result.get('content', ''),
                    'score': result.get('score', 0.0)
                })
            
            output = {
                'results': results,
                'query': query,
                'total_results': len(results)
            }
            
            # Cache results
            if use_cache:
                self.cache.set(f"search:{query}", output)
            
            return output
            
        except Exception as e:
            # Return empty results on error
            return {
                'results': [],
                'query': query,
                'total_results': 0,
                'error': str(e)
            }

