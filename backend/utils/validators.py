"""Input validation and sanitization utilities."""
import re
from typing import Optional
from urllib.parse import urlparse
import config


def sanitize_query(query: str) -> str:
    """Sanitize user query input.
    
    Args:
        query: Raw user query
        
    Returns:
        Sanitized query string
    """
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string")
    
    # Remove excessive whitespace
    query = " ".join(query.split())
    
    # Limit length
    if len(query) > 500:
        query = query[:500]
    
    return query.strip()


def validate_url(url: str) -> bool:
    """Validate URL format and scheme.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        # Only allow http and https
        if result.scheme not in ['http', 'https']:
            return False
        # Must have netloc (domain)
        if not result.netloc:
            return False
        return True
    except Exception:
        return False


def sanitize_url(url: str) -> Optional[str]:
    """Sanitize and validate URL.
    
    Args:
        url: URL string
        
    Returns:
        Sanitized URL if valid, None otherwise
    """
    url = url.strip()
    if not url:
        return None
    
    # Add scheme if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    if validate_url(url):
        return url
    return None


def extract_numbers(text: str) -> list[float]:
    """Extract numeric values from text.
    
    Args:
        text: Text containing numbers
        
    Returns:
        List of extracted numbers
    """
    # Pattern to match integers and decimals
    pattern = r'-?\d+\.?\d*'
    matches = re.findall(pattern, text)
    
    numbers = []
    for match in matches:
        try:
            num = float(match)
            numbers.append(num)
        except ValueError:
            continue
    
    return numbers

