#!/usr/bin/env python3
"""
Source scraping utility using ScrapegraphAI SmartScraperGraph.
Handles URL scraping with caching and error handling for blog content generation.
"""

import os
import sys
import time
from datetime import datetime
from typing import List, Dict, Any
from urllib.parse import urlparse

try:
    from scrapegraphai.graphs import SmartScraperGraph
except ImportError:
    sys.stderr.write("Error: scrapegraphai is required. Install it with `pip install scrapegraphai`.\n")
    sys.exit(1)


def build_llm_env() -> None:
    """
    Configure environment variables for ScrapegraphAI to use the local OpenAI-compatible endpoint.
    Uses the same configuration as 02_generate_blog_drafts.py.
    """
    # Configuration from 02_generate_blog_drafts.py
    OPENAI_HOST_IP = "192.168.8.90"
    OPENAI_PORT = "42069"
    OPENAI_AUTH_KEY = "outsider"
    OPENAI_MODEL = "gpt-oss-120b"
    
    # Set environment variables for ScrapegraphAI
    os.environ["OPENAI_API_KEY"] = OPENAI_AUTH_KEY
    os.environ["OPENAI_BASE_URL"] = f"http://{OPENAI_HOST_IP}:{OPENAI_PORT}/v1"
    # Some versions of openai client use OPENAI_API_BASE instead
    os.environ["OPENAI_API_BASE"] = f"http://{OPENAI_HOST_IP}:{OPENAI_PORT}/v1"


def scrape_url(url: str) -> Dict[str, Any]:
    """
    Scrape a single URL using SmartScraperGraph.
    
    Args:
        url: The URL to scrape
        
    Returns:
        ScrapedSource dict with url, status, text, char_count, last_scraped_at, and optional error
    """
    # Ensure environment is configured
    build_llm_env()
    
    # Create the scraper configuration
    graph_config = {
        "llm": {
            "model": "openai/gpt-oss-120b",
            "api_key": os.environ.get("OPENAI_API_KEY"),
            "base_url": os.environ.get("OPENAI_BASE_URL"),
        },
        "verbose": False,
        "headless": False,
    }
    
    # Generic prompt to extract readable content
    prompt = "Extract the main readable page text, excluding navigation menus, advertisements, comments, and other non-content elements. Return the content as clean markdown or plain text."
    
    try:
        # Create and run the scraper
        smart_scraper_graph = SmartScraperGraph(
            prompt=prompt,
            source=url,
            config=graph_config
        )
        
        result = smart_scraper_graph.run()
        
        # Extract text from result
        if isinstance(result, dict):
            text = result.get("text", "") or result.get("content", "") or str(result)
        elif isinstance(result, str):
            text = result
        else:
            text = str(result) if result else ""
        
        # Clean up the text
        text = text.strip()
        
        if not text:
            return {
                "url": url,
                "status": "error",
                "text": "",
                "char_count": 0,
                "last_scraped_at": datetime.now().isoformat(),
                "error": "No readable content extracted"
            }
        
        return {
            "url": url,
            "status": "ok",
            "text": text,
            "char_count": len(text),
            "last_scraped_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "url": url,
            "status": "error",
            "text": "",
            "char_count": 0,
            "last_scraped_at": datetime.now().isoformat(),
            "error": str(e)
        }


def scrape_urls(urls: List[str]) -> List[Dict[str, Any]]:
    """
    Scrape multiple URLs with retry mechanism and Option A failure policy (continue on errors).
    
    Args:
        urls: List of URLs to scrape
        
    Returns:
        List of ScrapedSource dicts
    """
    results = []
    max_retries = 3
    retry_delay = 1.0  # seconds between retries
    
    for url in urls:
        if not url or not url.strip():
            continue
            
        url = url.strip()
        
        # Basic URL validation
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                results.append({
                    "url": url,
                    "status": "error",
                    "text": "",
                    "char_count": 0,
                    "last_scraped_at": datetime.now().isoformat(),
                    "error": "Invalid URL format"
                })
                continue
        except Exception as e:
            results.append({
                "url": url,
                "status": "error",
                "text": "",
                "char_count": 0,
                "last_scraped_at": datetime.now().isoformat(),
                "error": f"URL parsing error: {str(e)}"
            })
            continue
        
        # Retry mechanism for scraping the URL
        result = None
        for attempt in range(max_retries):
            result = scrape_url(url)
            
            # If successful, break out of retry loop
            if result.get("status") == "ok":
                break
            
            # If this isn't the last attempt, wait before retrying
            if attempt < max_retries - 1:
                print(f"  Scraping attempt {attempt + 1} failed for {url}, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
        
        # Append the final result (success or final failure)
        results.append(result)
        
        # Add a small delay between different URLs to be respectful
        time.sleep(0.5)
    
    return results


if __name__ == "__main__":
    # Simple test functionality
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python scrape_sources.py <url1> [url2] ...")
        sys.exit(1)
    
    urls = sys.argv[1:]
    results = scrape_urls(urls)
    
    for result in results:
        print(f"URL: {result['url']}")
        print(f"Status: {result['status']}")
        if result['status'] == 'ok':
            print(f"Characters: {result['char_count']}")
            print(f"Text preview: {result['text'][:200]}...")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
        print("-" * 50)
