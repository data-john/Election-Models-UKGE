"""
UK Election Simulator - SQLite Cache Manager
Sprint 2 Day 3: SQLite caching implementation with enhanced error handling
Sprint 2 Day 5: Database resilience and error recovery

This module provides persistent caching for polling data using SQLite database.
Replaces/complements Streamlit's in-memory cache with disk-based persistence.
"""

import sqlite3
import pandas as pd
import json
import hashlib
import time
import os
import logging
from datetime import datetime, timedelta
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
            
        except sqlite3.DatabaseError as e:
            if "file is not a database" in str(e).lower() or "database disk image is malformed" in str(e).lower():
                logger.warning(f"Database corruption detected during initialization: {e}")
                try:
                    # Attempt repair by recreating the database
                    if os.path.exists(self.db_path):
                        backup_path = f"{self.db_path}.corrupt_{int(time.time())}"
                        os.rename(self.db_path, backup_path)
                        logger.info(f"Moved corrupted database to {backup_path}")
                    
                    # Retry initialization with a clean database
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
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
                    
                    cursor.execute('''
                        CREATE INDEX IF NOT EXISTS idx_expires_at ON poll_cache(expires_at)
                    ''')
                    
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS cache_metadata (
                            key TEXT PRIMARY KEY,
                            value TEXT,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    
                    conn.commit()
                    conn.close()
                    logger.info("Database successfully repaired during initialization")
                    
                except Exception as repair_error:
                    logger.error(f"Failed to repair corrupted database: {repair_error}")
                    raise
            else:
                logger.error(f"Failed to initialize cache database: {e}")
                raise
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
        Retrieve cached data with enhanced error handling
        Sprint 2 Day 5: Enhanced database error handling and resilience
        
        Args:
            url: Source URL for the data
            params: Additional parameters used for caching key
            
        Returns:
            Cached DataFrame if valid, None if not found/expired/error
        """
        if params is None:
            params = {}
        
        # Input validation
        if not url or not isinstance(url, str):
            logger.error("Invalid URL provided to cache get()")
            return None
            
        cache_key = self._generate_cache_key(url, params)
        
        # Database connection with retry logic
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                # Check if database file exists and is accessible
                if not os.path.exists(self.db_path):
                    logger.warning(f"Cache database does not exist: {self.db_path}")
                    return None
                
                # Test database file permissions
                if not os.access(self.db_path, os.R_OK):
                    logger.error(f"Cache database is not readable: {self.db_path}")
                    return None
                
                conn = sqlite3.connect(self.db_path, timeout=10.0)
                conn.row_factory = sqlite3.Row  # Enable column access by name
                cursor = conn.cursor()
                
                # Validate database schema
                try:
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='poll_cache'")
                    if not cursor.fetchone():
                        logger.warning("Cache table does not exist, initializing...")
                        conn.close()
                        self._init_db()
                        return None
                except sqlite3.Error as e:
                    logger.error(f"Database schema validation failed: {e}")
                    conn.close()
                    return None
                
                # Check if cache entry exists and is not expired
                cursor.execute('''
                    SELECT data_json, expires_at, access_count
                    FROM poll_cache 
                    WHERE cache_key = ? AND expires_at > CURRENT_TIMESTAMP
                ''', (cache_key,))
                
                result = cursor.fetchone()
                
                if result:
                    data_json, expires_at, access_count = result
                    
                    # Validate data_json is not empty or corrupted
                    if not data_json or data_json.strip() == '':
                        logger.warning(f"Empty data found in cache for key {cache_key[:8]}...")
                        cursor.execute('DELETE FROM poll_cache WHERE cache_key = ?', (cache_key,))
                        conn.commit()
                        conn.close()
                        return None
                    
                    # Update access statistics with error handling
                    try:
                        cursor.execute('''
                            UPDATE poll_cache 
                            SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                            WHERE cache_key = ?
                        ''', (cache_key,))
                        conn.commit()
                    except sqlite3.Error as e:
                        logger.warning(f"Failed to update access statistics: {e}")
                        # Continue with data retrieval even if stats update fails
                    
                    conn.close()
                    
                    # Deserialize data with comprehensive error handling
                    try:
                        data_dict = json.loads(data_json)
                        if not isinstance(data_dict, list):
                            logger.error(f"Invalid data format in cache: expected list, got {type(data_dict)}")
                            return None
                        
                        df = pd.DataFrame(data_dict)
                        
                        # Validate DataFrame
                        if df.empty:
                            logger.warning(f"Empty DataFrame loaded from cache")
                            return None
                        
                        # Basic data type validation
                        if len(df.columns) == 0:
                            logger.error(f"DataFrame has no columns")
                            return None
                        
                        self.cache_hits += 1
                        logger.info(f"Cache HIT for key {cache_key[:8]}... (access #{access_count + 1})")
                        return df
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to deserialize cached data: {e}")
                        # Remove corrupted cache entry
                        try:
                            conn = sqlite3.connect(self.db_path, timeout=5.0)
                            cursor = conn.cursor()
                            cursor.execute('DELETE FROM poll_cache WHERE cache_key = ?', (cache_key,))
                            conn.commit()
                            conn.close()
                        except sqlite3.Error:
                            pass  # Best effort cleanup
                        return None
                        
                    except Exception as e:
                        logger.error(f"Failed to create DataFrame from cached data: {e}")
                        return None
                else:
                    conn.close()
                    self.cache_misses += 1
                    logger.info(f"Cache MISS for key {cache_key[:8]}...")
                    return None
                    
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower() and attempt < max_retries - 1:
                    logger.warning(f"Database locked, retry {attempt + 1}/{max_retries}")
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                logger.error(f"Database operational error: {e}")
                return None
                
            except sqlite3.DatabaseError as e:
                logger.error(f"Database error in cache get(): {e}")
                # For database corruption, try to reinitialize
                if "database disk image is malformed" in str(e).lower():
                    logger.warning("Database appears corrupted, attempting repair...")
                    try:
                        self._repair_database()
                    except Exception:
                        logger.error("Database repair failed")
                return None
                
            except Exception as e:
                logger.error(f"Unexpected error in cache get(): {e}")
                return None
        
        # If we get here, all retries failed
        logger.error(f"Failed to retrieve cache after {max_retries} attempts")
        return None
    
    def set(self, url: str, data: pd.DataFrame, params: Dict[str, Any] = None, ttl: int = None) -> bool:
        """
        Store data in cache with enhanced error handling and recovery
        Sprint 2 Day 5: Enhanced database error handling and recovery
        
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
            
        # Input validation
        if not url or not isinstance(url, str):
            logger.error("Invalid URL provided to cache set()")
            return False
        
        if data is None or not isinstance(data, pd.DataFrame):
            logger.error("Invalid data provided to cache set()")
            return False
        
        if data.empty:
            logger.warning("Empty DataFrame provided to cache set()")
            return False
            
        cache_key = self._generate_cache_key(url, params)
        
        # Retry logic for database operations
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                # Serialize dataframe
                try:
                    data_json = data.to_json(orient='records', date_format='iso')
                    params_json = json.dumps(params, sort_keys=True)
                except Exception as e:
                    logger.error(f"Failed to serialize data: {e}")
                    return False
                
                # Validate serialized data
                if not data_json or data_json.strip() == '':
                    logger.error("Data serialization resulted in empty JSON")
                    return False
                
                # Calculate expiry time in UTC to match SQLite CURRENT_TIMESTAMP
                expires_at = datetime.utcnow() + timedelta(seconds=ttl)
                expires_at_str = expires_at.strftime('%Y-%m-%d %H:%M:%S')
                
                # Database connection with enhanced error handling
                try:
                    conn = sqlite3.connect(self.db_path, timeout=10.0)
                    cursor = conn.cursor()
                    
                    # Verify database schema before attempting insert
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='poll_cache'")
                    if not cursor.fetchone():
                        logger.warning("Cache table does not exist, initializing...")
                        conn.close()
                        self._init_db()
                        # Retry connection after initialization
                        conn = sqlite3.connect(self.db_path, timeout=10.0)
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
                    
                except sqlite3.OperationalError as e:
                    if "database is locked" in str(e).lower() and attempt < max_retries - 1:
                        logger.warning(f"Database locked during set, retry {attempt + 1}/{max_retries}")
                        time.sleep(retry_delay * (attempt + 1))
                        continue
                    elif "file is not a database" in str(e).lower():
                        logger.error("Database file corrupted, attempting repair...")
                        try:
                            self._repair_database()
                            # After repair, try once more
                            if attempt < max_retries - 1:
                                continue
                        except Exception as repair_error:
                            logger.error(f"Database repair failed: {repair_error}")
                    
                    logger.error(f"Database operational error: {e}")
                    return False
                    
                except sqlite3.DatabaseError as e:
                    logger.error(f"Database error in cache set(): {e}")
                    if "database disk image is malformed" in str(e).lower():
                        logger.warning("Database appears corrupted, attempting repair...")
                        try:
                            self._repair_database()
                            if attempt < max_retries - 1:
                                continue
                        except Exception:
                            logger.error("Database repair failed")
                    return False
                    
            except Exception as e:
                logger.error(f"Unexpected error in cache set() attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return False
        
        # If we get here, all retries failed
        logger.error(f"Failed to store in cache after {max_retries} attempts")
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
    
    def _repair_database(self) -> bool:
        """
        Attempt to repair a corrupted database
        Sprint 2 Day 5: Database corruption recovery
        
        Returns:
            True if repair successful, False otherwise
        """
        try:
            # Backup original file
            backup_path = f"{self.db_path}.backup_{int(time.time())}"
            if os.path.exists(self.db_path):
                try:
                    import shutil
                    shutil.copy2(self.db_path, backup_path)
                    logger.info(f"Backed up corrupted database to {backup_path}")
                except Exception as e:
                    logger.warning(f"Failed to backup corrupted database: {e}")
            
            # Remove corrupted database
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
                logger.info("Removed corrupted database file")
            
            # Reinitialize database
            self._init_db()
            logger.info("Reinitialized database after corruption")
            
            return True
            
        except Exception as e:
            logger.error(f"Database repair failed: {e}")
            return False
    
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
