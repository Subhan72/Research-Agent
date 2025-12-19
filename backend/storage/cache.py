"""JSON-based caching system for tool results."""
import json
import hashlib
from pathlib import Path
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import config


class JSONCache:
    """Simple file-based JSON cache with expiration."""
    
    def __init__(self, cache_dir: Optional[Path] = None, ttl_hours: int = 24):
        """Initialize cache.
        
        Args:
            cache_dir: Directory for cache files. Defaults to config.CACHE_DIR
            ttl_hours: Time-to-live in hours. Defaults to 24
        """
        self.cache_dir = cache_dir or config.CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
    
    def _get_cache_key(self, key: str) -> str:
        """Generate cache key hash.
        
        Args:
            key: Original key string
            
        Returns:
            Hashed key string
        """
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """Get file path for cache key.
        
        Args:
            key: Cache key
            
        Returns:
            Path to cache file
        """
        cache_key = self._get_cache_key(key)
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get value from cache if not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check expiration
            cached_time = datetime.fromisoformat(data.get('timestamp', ''))
            if datetime.now() - cached_time > self.ttl:
                cache_path.unlink()  # Delete expired cache
                return None
            
            return data.get('value')
        except Exception:
            # If cache file is corrupted, delete it
            if cache_path.exists():
                cache_path.unlink()
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Store value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
        """
        cache_path = self._get_cache_path(key)
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'value': value
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            # Silently fail if cache write fails
            pass
    
    def clear(self, key: Optional[str] = None) -> None:
        """Clear cache entry or all cache.
        
        Args:
            key: Specific key to clear. If None, clears all cache
        """
        if key:
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()
        else:
            # Clear all cache files
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache and is not expired.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists and is valid
        """
        return self.get(key) is not None

