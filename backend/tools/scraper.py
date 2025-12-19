"""Web scraping tool for extracting clean text from webpages."""
from typing import Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from readability import Document
from tenacity import retry, stop_after_attempt, wait_exponential
import config
from backend.utils.validators import validate_url, sanitize_url
from backend.storage.cache import JSONCache


class WebScraperTool:
    """Tool for scraping and extracting clean text from webpages."""
    
    def __init__(self):
        """Initialize scraper with cache."""
        self.cache = JSONCache()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    @retry(
        stop=stop_after_attempt(config.MAX_RETRIES),
        wait=wait_exponential(multiplier=config.RETRY_DELAY, min=1, max=5)
    )
    def scrape(
        self,
        url: str,
        use_cache: bool = True,
        max_length: Optional[int] = None
    ) -> Dict[str, Any]:
        """Scrape and extract clean text from a webpage.
        
        Args:
            url: URL to scrape
            max_length: Maximum text length. Defaults to config.MAX_SCRAPE_LENGTH
            use_cache: Whether to use cached content if available
            
        Returns:
            Dictionary with:
            - url: Original URL
            - title: Page title
            - text: Clean extracted text
            - length: Text length
            - success: Whether scraping succeeded
        """
        max_length = max_length or config.MAX_SCRAPE_LENGTH
        
        # Validate and sanitize URL
        url = sanitize_url(url) or url
        if not validate_url(url):
            return {
                'url': url,
                'title': '',
                'text': '',
                'length': 0,
                'success': False,
                'error': 'Invalid URL'
            }
        
        # Check cache
        if use_cache:
            cached = self.cache.get(f"scrape:{url}")
            if cached:
                return cached
        
        try:
            # Fetch webpage
            response = self.session.get(
                url,
                timeout=config.SCRAPER_TIMEOUT,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()
            
            # Try using readability for better extraction
            try:
                doc = Document(response.content)
                clean_html = doc.summary()
                soup = BeautifulSoup(clean_html, 'html.parser')
            except Exception:
                pass  # Fall back to basic extraction
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ''
            
            # Extract main text
            # Try to find main content area
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=lambda x: x and ('content' in x.lower() or 'main' in x.lower()))
            
            if main_content:
                text = main_content.get_text(separator=' ', strip=True)
            else:
                # Fallback to body text
                body = soup.find('body')
                text = body.get_text(separator=' ', strip=True) if body else ''
            
            # Clean up text
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            text = ' '.join(lines)
            
            # Limit length
            if len(text) > max_length:
                text = text[:max_length] + '...'
            
            result = {
                'url': url,
                'title': title_text,
                'text': text,
                'length': len(text),
                'success': True
            }
            
            # Cache result
            if use_cache:
                self.cache.set(f"scrape:{url}", result)
            
            return result
            
        except requests.RequestException as e:
            return {
                'url': url,
                'title': '',
                'text': '',
                'length': 0,
                'success': False,
                'error': f'Request error: {str(e)}'
            }
        except Exception as e:
            return {
                'url': url,
                'title': '',
                'text': '',
                'length': 0,
                'success': False,
                'error': f'Scraping error: {str(e)}'
            }

