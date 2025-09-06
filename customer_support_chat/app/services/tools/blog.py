# customer_support_chat/app/services/tools/blog.py

import httpx
import urllib.parse
from langchain_core.tools import tool
from customer_support_chat.app.core.settings import get_settings
from typing import List, Dict

settings = get_settings()

@tool
def search_blog_posts(keyword: str, limit: int = 5) -> List[Dict]:
    """Search for blog posts based on a keyword.
    
    Args:
        keyword: The keyword to search for in blog posts.
        limit: Maximum number of posts to return (default: 5).
        
    Returns:
        A list of blog post dictionaries with title, excerpt, and link.
    """
    if not settings.BLOG_SEARCH_API_URL:
        raise ValueError("Blog search API URL is not configured.")
    
    # Encode the keyword for URL
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"{settings.BLOG_SEARCH_API_URL}?search={encoded_keyword}"
    
    # If the blog requires authentication (like WooCommerce REST API), add it here
    # For now, we'll assume it's a public WordPress REST API endpoint
    auth = None
    if settings.WOOCOMMERCE_CONSUMER_KEY and settings.WOOCOMMERCE_CONSUMER_SECRET:
        auth = httpx.BasicAuth(settings.WOOCOMMERCE_CONSUMER_KEY, settings.WOOCOMMERCE_CONSUMER_SECRET)
    
    with httpx.Client() as client:
        try:
            response = client.get(
                url,
                auth=auth
            )
            response.raise_for_status()
            posts = response.json()
            
            # Extract key information
            simplified_posts = []
            for post in posts[:limit]:
                simplified_posts.append({
                    "id": post.get("id"),
                    "title": post.get("title", {}).get("rendered", "No Title"),
                    "excerpt": post.get("excerpt", {}).get("rendered", "")[:200] + "...",
                    "link": post.get("link"),
                    "date": post.get("date"),
                })
            
            return simplified_posts
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error occurred while searching blog posts: {e}")
        except Exception as e:
            raise Exception(f"An error occurred while searching blog posts: {e}")