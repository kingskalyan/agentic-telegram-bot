from duckduckgo_search import DDGS
import json
from src.logger import get_logger

logger = get_logger("news_search")

def search_latest_news(query: str, max_results: int = 5) -> str:
    """
    Search the web for the latest news related to a given query.
    
    Args:
        query: The topic or keywords to search for news about.
        max_results: The maximum number of news articles to return (default 5).
        
    Returns:
        A JSON string containing a list of news articles with title, body, date, url, and source.
    """
    logger.info("searching_news", query=query, max_results=max_results)
    
    try:
        results = []
        with DDGS() as ddgs:
            # Use DDG news search capabilities
            ddgs_news_gen = ddgs.news(keywords=query, max_results=max_results)
            for r in ddgs_news_gen:
                results.append({
                    "title": r.get('title', ''),
                    "snippet": r.get('body', ''),
                    "date": r.get('date', ''),
                    "url": r.get('url', ''),
                    "source": r.get('source', '')
                })
        
        logger.info("news_search_success", result_count=len(results))
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        logger.error("news_search_error", error=str(e))
        return json.dumps({"error": f"Failed to retrieve news: {str(e)}"})
