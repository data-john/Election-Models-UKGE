"""
UK Election Simulator - SQLite Cache Manager
Sprint 2 Day 3: SQLite caching implementation

This module provides persistent caching for polling data using SQLite database.
Replaces/complements Streamlit's in-memory cache with disk-based persistence.
"""

import sqlite3
import pandas as pd
import json
import hashlib
from datetime import datetime, timedelta
import os
import logging
from typing import Optional, Dict, Any, List, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PollDataCache:
    """
    SQLite-based cache manager for polling data
    
    Features:
    - Persistent storage across sessions
    - Configurable TTL (time-to-live)
    - Automatic cache invalidation
    - Data integrity checks
    - Performance metrics
    """
    
    def __init__(self, db_path: str = "data/poll_cache.db", default_ttl: int = 3600):
        """
        Initialize cache manager
        
        Args:
            db_path: Path to SQLite database file
            default_ttl: Default TTL in seconds (default: 1 hour)
        """
        self.db_path = db_path
        self.default_ttl = default_ttl
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Performance tracking
        self.cache_hits = 0
        self.cache_misses = 0
        
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create cache table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS poll_cache (
                    cache_key TEXT PRIMARY KEY,
                    data_json TEXT NOT NULL,
                    url TEXT,
                    params_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index for faster expiry checks
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_expires_at ON poll_cache(expires_at)
            ''')
            
            # Create metadata table for cache statistics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"Cache database initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize cache database: {e}")
            raise
    
    def _generate_cache_key(self, url: str, params: Dict[str, Any]) -> str:
        """Generate unique cache key from URL and parameters"""
        # Create reproducible hash from url and sorted parameters
        param_str = json.dumps(params, sort_keys=True)
        key_data = f"{url}:{param_str}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def get(self, url: str, params: Dict[str, Any] = None) -> Optional[pd.DataFrame]:
        """
        Retrieve cached data
        
        Args:
            url: Source URL for the data
            params: Additional parameters used for caching key
            
        Returns:
            Cached DataFrame if valid, None if not found/expired
        """
        if params is None:
            params = {}
            
        cache_key = self._generate_cache_key(url, params)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if cache entry exists and is not expired
            cursor.execute('''
                SELECT data_json, expires_at, access_count
                FROM poll_cache 
                WHERE cache_key = ? AND expires_at > CURRENT_TIMESTAMP
            ''', (cache_key,))
            
            result = cursor.fetchone()
            
            if result:
                data_json, expires_at, access_count = result
                
                # Update access statistics
                cursor.execute('''
                    UPDATE poll_cache 
                    SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                    WHERE cache_key = ?
                ''', (cache_key,))
                
                conn.commit()
                conn.close()
                
                # Deserialize data
                data_dict = json.loads(data_json)
                df = pd.DataFrame(data_dict)
                
                self.cache_hits += 1
                logger.info(f"Cache HIT for key {cache_key[:8]}... (access #{access_count + 1})")
                return df
            else:
                conn.close()
                self.cache_misses += 1
                logger.info(f"Cache MISS for key {cache_key[:8]}...")
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve from cache: {e}")
            return None
    
    def set(self, url: str, data: pd.DataFrame, params: Dict[str, Any] = None, ttl: int = None) -> bool:
        """
        Store data in cache
        
        Args:
            url: Source URL for the data
            data: DataFrame to cache
            params: Additional parameters used for caching key
            ttl: Time-to-live in seconds (uses default if None)
            
        Returns:
            True if successful, False otherwise
        """
        if params is None:
            params = {}
        if ttl is None:
            ttl = self.default_ttl
            
        cache_key = self._generate_cache_key(url, params)
        
        try:
            # Serialize dataframe
            data_json = data.to_json(orient='records', date_format='iso')
            params_json = json.dumps(params, sort_keys=True)
            
            # Calculate expiry time in UTC to match SQLite CURRENT_TIMESTAMP
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            expires_at_str = expires_at.strftime('%Y-%m-%d %H:%M:%S')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert or replace cache entry
            cursor.execute('''
                INSERT OR REPLACE INTO poll_cache 
                (cache_key, data_json, url, params_json, expires_at, access_count, last_accessed)
                VALUES (?, ?, ?, ?, ?, 0, CURRENT_TIMESTAMP)
            ''', (cache_key, data_json, url, params_json, expires_at_str))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cache SET for key {cache_key[:8]}... (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store in cache: {e}")
            return False
    
    def invalidate(self, url: str = None, params: Dict[str, Any] = None) -> int:
        """
        Invalidate cache entries
        
        Args:
            url: Specific URL to invalidate (all if None)
            params: Specific parameters to invalidate
            
        Returns:
            Number of entries invalidated
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if url and params is not None:
                # Invalidate specific entry
                cache_key = self._generate_cache_key(url, params)
                cursor.execute('DELETE FROM poll_cache WHERE cache_key = ?', (cache_key,))
            elif url:
                # Invalidate all entries for URL
                cursor.execute('DELETE FROM poll_cache WHERE url = ?', (url,))
            else:
                # Invalidate all entries
                cursor.execute('DELETE FROM poll_cache')
            
            count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Cache invalidated {count} entries")
            return count
            
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {e}")
            return 0
    
    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries
        
        Returns:
            Number of entries removed
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM poll_cache WHERE expires_at <= CURRENT_TIMESTAMP')
            count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            if count > 0:
                logger.info(f"Cleaned up {count} expired cache entries")
            
            return count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired cache: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count total entries
            cursor.execute('SELECT COUNT(*) FROM poll_cache')
            total_entries = cursor.fetchone()[0]
            
            # Count expired entries
            cursor.execute('SELECT COUNT(*) FROM poll_cache WHERE expires_at <= CURRENT_TIMESTAMP')
            expired_entries = cursor.fetchone()[0]
            
            # Count valid entries
            valid_entries = total_entries - expired_entries
            
            # Get oldest and newest entries
            cursor.execute('SELECT MIN(created_at), MAX(created_at) FROM poll_cache')
            date_range = cursor.fetchone()
            
            # Get most accessed entry
            cursor.execute('''
                SELECT url, access_count, last_accessed 
                FROM poll_cache 
                ORDER BY access_count DESC 
                LIMIT 1
            ''')
            most_accessed = cursor.fetchone()
            
            # Get database size
            cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            db_size = cursor.fetchone()[0]
            
            conn.close()
            
            stats = {
                'total_entries': total_entries,
                'valid_entries': valid_entries,
                'expired_entries': expired_entries,
                'cache_hits': self.cache_hits,
                'cache_misses': self.cache_misses,
                'hit_rate': self.cache_hits / max(1, self.cache_hits + self.cache_misses),
                'db_size_bytes': db_size,
                'db_size_mb': round(db_size / (1024 * 1024), 2),
                'oldest_entry': date_range[0] if date_range[0] else None,
                'newest_entry': date_range[1] if date_range[1] else None,
            }
            
            if most_accessed:
                stats['most_accessed'] = {
                    'url': most_accessed[0],
                    'access_count': most_accessed[1],
                    'last_accessed': most_accessed[2]
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}
    
    def get_cache_entries(self) -> List[Dict[str, Any]]:
        """
        Get list of all cache entries with metadata
        
        Returns:
            List of cache entry dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT cache_key, url, created_at, expires_at, access_count, last_accessed,
                       CASE WHEN expires_at > CURRENT_TIMESTAMP THEN 'valid' ELSE 'expired' END as status
                FROM poll_cache
                ORDER BY created_at DESC
            ''')
            
            columns = ['cache_key', 'url', 'created_at', 'expires_at', 'access_count', 'last_accessed', 'status']
            entries = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return entries
            
        except Exception as e:
            logger.error(f"Failed to get cache entries: {e}")
            return []

# Global cache instance
_cache_instance = None

def get_cache() -> PollDataCache:
    """Get global cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = PollDataCache()
    return _cache_instance

def cached_get_latest_polls_from_html(url: str, col_dict: Dict[str, str], n: int = 10, 
                                    allow_repeated_pollsters: bool = False, ttl: int = 3600) -> Optional[pd.DataFrame]:
    """
    Cached version of get_latest_polls_from_html with SQLite persistence
    
    Args:
        url: Wikipedia URL to scrape
        col_dict: Column mapping dictionary
        n: Number of polls to return
        allow_repeated_pollsters: Whether to allow repeated pollsters
        ttl: Cache TTL in seconds
        
    Returns:
        DataFrame with polling data or None if failed
    """
    cache = get_cache()
    
    # Create cache parameters
    params = {
        'col_dict': col_dict,
        'n': n,
        'allow_repeated_pollsters': allow_repeated_pollsters
    }
    
    # Try to get from cache first
    cached_data = cache.get(url, params)
    if cached_data is not None:
        return cached_data
    
    # If not in cache, fetch from source
    try:
        from polls import get_latest_polls_from_html
        data = get_latest_polls_from_html(url, col_dict, n, allow_repeated_pollsters)
        
        # Store in cache
        cache.set(url, data, params, ttl)
        
        return data
        
    except Exception as e:
        logger.error(f"Failed to fetch and cache polling data: {e}")
        return None
