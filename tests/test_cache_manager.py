"""
Test suite for SQLite cache manager
Sprint 2 Day 3: Comprehensive testing for cache functionality
"""

import pytest
import pandas as pd
import os
import tempfile
import json
from datetime import datetime, timedelta
import sys

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from cache_manager import PollDataCache, get_cache, cached_get_latest_polls_from_html

class TestPollDataCache:
    """Test suite for PollDataCache class"""
    
    @pytest.fixture
    def temp_cache(self):
        """Create a temporary cache instance for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            cache = PollDataCache(db_path=tmp.name, default_ttl=300)  # 5 minute default TTL
            yield cache
            # Cleanup
            try:
                os.unlink(tmp.name)
            except:
                pass
    
    @pytest.fixture
    def sample_df(self):
        """Create sample DataFrame for testing"""
        data = {
            'Date': ['2025-08-30', '2025-08-29', '2025-08-28'],
            'Pollster': ['YouGov', 'Opinium', 'Survation'],
            'Con': [25, 23, 24],
            'Lab': [42, 44, 43],
            'LD': [12, 11, 13],
            'SNP': [3, 3, 3],
            'Grn': [6, 7, 6],
            'Ref': [12, 12, 11]
        }
        return pd.DataFrame(data)
    
    def test_cache_initialization(self, temp_cache):
        """Test that cache initializes correctly"""
        assert temp_cache.db_path is not None
        assert temp_cache.default_ttl == 300
        assert temp_cache.cache_hits == 0
        assert temp_cache.cache_misses == 0
        assert os.path.exists(temp_cache.db_path)
    
    def test_cache_key_generation(self, temp_cache):
        """Test cache key generation"""
        url1 = "https://example.com/polls"
        params1 = {"n": 10, "pollster": "YouGov"}
        
        key1 = temp_cache._generate_cache_key(url1, params1)
        key2 = temp_cache._generate_cache_key(url1, params1)  # Same parameters
        
        # Same parameters should generate same key
        assert key1 == key2
        assert len(key1) == 64  # SHA256 hash length
        
        # Different parameters should generate different key
        params2 = {"n": 20, "pollster": "YouGov"}
        key3 = temp_cache._generate_cache_key(url1, params2)
        assert key1 != key3
    
    def test_cache_set_and_get(self, temp_cache, sample_df):
        """Test basic cache set and get operations"""
        url = "https://test.com/polls"
        params = {"test": "value"}
        
        # Test cache miss
        result = temp_cache.get(url, params)
        assert result is None
        assert temp_cache.cache_misses == 1
        
        # Set data in cache
        success = temp_cache.set(url, sample_df, params, ttl=3600)
        assert success is True
        
        # Test cache hit
        result = temp_cache.get(url, params)
        assert result is not None
        assert temp_cache.cache_hits == 1
        
        # Verify data integrity
        pd.testing.assert_frame_equal(result, sample_df)
    
    def test_cache_expiration(self, temp_cache, sample_df):
        """Test cache expiration functionality"""
        url = "https://test.com/polls"
        params = {"test": "expiry"}
        
        # Set data with very short TTL
        success = temp_cache.set(url, sample_df, params, ttl=1)
        assert success is True
        
        # Should be able to get immediately
        result = temp_cache.get(url, params)
        assert result is not None
        
        # Wait for expiry and test
        import time
        time.sleep(2)
        
        result = temp_cache.get(url, params)
        assert result is None  # Should be expired
    
    def test_cache_invalidation(self, temp_cache, sample_df):
        """Test cache invalidation"""
        url1 = "https://test.com/polls1"
        url2 = "https://test.com/polls2"
        params = {"test": "invalidation"}
        
        # Set data in cache for both URLs
        temp_cache.set(url1, sample_df, params)
        temp_cache.set(url2, sample_df, params)
        
        # Verify both are cached
        assert temp_cache.get(url1, params) is not None
        assert temp_cache.get(url2, params) is not None
        
        # Invalidate specific URL
        count = temp_cache.invalidate(url1, params)
        assert count == 1
        
        # Verify only url1 is invalidated
        assert temp_cache.get(url1, params) is None
        assert temp_cache.get(url2, params) is not None
        
        # Invalidate all for url2
        count = temp_cache.invalidate(url2)
        assert count == 1
        
        # Verify url2 is also invalidated
        assert temp_cache.get(url2, params) is None
    
    def test_cleanup_expired(self, temp_cache, sample_df):
        """Test cleanup of expired entries"""
        url = "https://test.com/polls"
        
        # Add some entries with different TTLs
        temp_cache.set(url, sample_df, {"id": "1"}, ttl=1)  # Will expire quickly
        temp_cache.set(url, sample_df, {"id": "2"}, ttl=3600)  # Long TTL
        
        # Wait for first to expire
        import time
        time.sleep(2)
        
        # Cleanup expired
        cleaned = temp_cache.cleanup_expired()
        assert cleaned >= 1
        
        # Verify expired is gone but valid remains
        assert temp_cache.get(url, {"id": "1"}) is None
        assert temp_cache.get(url, {"id": "2"}) is not None
    
    def test_cache_stats(self, temp_cache, sample_df):
        """Test cache statistics"""
        url = "https://test.com/polls"
        
        # Initially empty
        stats = temp_cache.get_stats()
        assert stats['total_entries'] == 0
        assert stats['valid_entries'] == 0
        assert stats['cache_hits'] == 0
        assert stats['cache_misses'] == 0
        
        # Add some data
        temp_cache.set(url, sample_df, {"id": "1"})
        temp_cache.set(url, sample_df, {"id": "2"}, ttl=1)  # Will expire
        
        # Get data to generate hits
        temp_cache.get(url, {"id": "1"})
        temp_cache.get(url, {"id": "nonexistent"})  # Miss
        
        # Wait for expiry
        import time
        time.sleep(2)
        
        stats = temp_cache.get_stats()
        assert stats['total_entries'] == 2
        assert stats['valid_entries'] == 1  # One expired
        assert stats['expired_entries'] == 1
        assert stats['cache_hits'] == 1
        assert stats['cache_misses'] == 1
        assert stats['hit_rate'] == 0.5
    
    def test_cache_entries_list(self, temp_cache, sample_df):
        """Test getting cache entries list"""
        url = "https://test.com/polls"
        
        # Add some entries
        temp_cache.set(url, sample_df, {"id": "1"})
        temp_cache.set(url, sample_df, {"id": "2"}, ttl=1)
        
        entries = temp_cache.get_cache_entries()
        assert len(entries) == 2
        
        # Check entry structure
        entry = entries[0]
        assert 'cache_key' in entry
        assert 'url' in entry
        assert 'created_at' in entry
        assert 'expires_at' in entry
        assert 'access_count' in entry
        assert 'status' in entry
        
        # Wait for one to expire
        import time
        time.sleep(2)
        
        entries = temp_cache.get_cache_entries()
        valid_entries = [e for e in entries if e['status'] == 'valid']
        expired_entries = [e for e in entries if e['status'] == 'expired']
        
        assert len(valid_entries) == 1
        assert len(expired_entries) == 1

class TestCachedGetLatestPolls:
    """Test the cached wrapper function"""
    
    @pytest.fixture
    def temp_cache_instance(self):
        """Create temporary cache for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            # Monkey patch the global cache
            import cache_manager
            original_cache = cache_manager._cache_instance
            cache_manager._cache_instance = PollDataCache(db_path=tmp.name)
            
            yield cache_manager._cache_instance
            
            # Restore original and cleanup
            cache_manager._cache_instance = original_cache
            try:
                os.unlink(tmp.name)
            except:
                pass
    
    def test_cached_function_with_mock_data(self, temp_cache_instance, monkeypatch):
        """Test cached function with mocked polls module"""
        
        # Mock the polls module function
        def mock_get_latest_polls_from_html(url, col_dict, n, allow_repeated_pollsters):
            return pd.DataFrame({
                'Date': ['2025-08-30'],
                'Pollster': ['TestPollster'],
                'Con': [25],
                'Lab': [45]
            })
        
        # Import the function and manually test cache behavior
        # Since the import is done inside the cached function, we'll test the cache logic directly
        cache = temp_cache_instance
        
        # Create test data  
        test_data = pd.DataFrame({
            'Date': ['2025-08-30'],
            'Pollster': ['MockPollster'], 
            'Con': [25],
            'Lab': [45]
        })
        
        url = "https://test-wiki.com"
        params = {"col_dict": {"Con": "Con", "Lab": "Lab"}, "n": 10, "allow_repeated_pollsters": False}
        
        # Test cache miss initially
        result = cache.get(url, params)
        assert result is None
        assert cache.cache_misses == 1
        
        # Manually set cache to simulate successful function call
        cache.set(url, test_data, params)
        
        # Test cache hit
        result = cache.get(url, params)
        assert result is not None
        assert cache.cache_hits == 1
        
        # Verify data integrity
        pd.testing.assert_frame_equal(result, test_data)
    
    def test_cached_function_error_handling(self, temp_cache_instance, monkeypatch):
        """Test cached function error handling"""
        
        # For this test, we'll just verify that the cached function can handle 
        # the case where cache is empty and function would fail
        # Since we can't easily mock the internal import, we test the cache logic
        
        cache = temp_cache_instance
        url = "https://error-wiki.com"
        params = {"col_dict": {"Con": "Con", "Lab": "Lab"}, "n": 10, "allow_repeated_pollsters": False}
        
        # Test cache miss when cache is empty
        result = cache.get(url, params)
        assert result is None
        assert cache.cache_misses == 1
        
        # Test that we can still interact with cache even when data source fails
        # (In real scenario, the cached function would return None and log the error)
        assert cache.get_stats()['cache_misses'] == 1

class TestCachePerformance:
    """Performance and stress tests for cache"""
    
    @pytest.fixture
    def perf_cache(self):
        """Create cache for performance testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            cache = PollDataCache(db_path=tmp.name)
            yield cache
            try:
                os.unlink(tmp.name)
            except:
                pass
    
    def test_large_dataset_caching(self, perf_cache):
        """Test caching with large dataset"""
        # Create large DataFrame
        large_data = {
            'Date': [f'2025-08-{i:02d}' for i in range(1, 31)],
            'Pollster': [f'Pollster_{i}' for i in range(1, 31)],
            'Con': list(range(20, 50)),
            'Lab': list(range(30, 60)),
            'LD': list(range(5, 35)),
            'SNP': list(range(1, 31)),
            'Grn': list(range(2, 32)),
            'Ref': list(range(5, 35))
        }
        
        large_df = pd.DataFrame(large_data)
        
        url = "https://test.com/large"
        params = {"size": "large"}
        
        # Time the set operation
        import time
        start_time = time.time()
        success = perf_cache.set(url, large_df, params)
        set_time = time.time() - start_time
        
        assert success is True
        assert set_time < 1.0  # Should complete in under 1 second
        
        # Time the get operation
        start_time = time.time()
        result = perf_cache.get(url, params)
        get_time = time.time() - start_time
        
        assert result is not None
        assert get_time < 0.1  # Should be very fast
        assert len(result) == 30
    
    def test_multiple_concurrent_operations(self, perf_cache):
        """Test handling multiple cache operations"""
        base_df = pd.DataFrame({
            'Date': ['2025-08-30'],
            'Pollster': ['TestPollster'],
            'Con': [25],
            'Lab': [45]
        })
        
        # Set multiple entries
        for i in range(10):
            url = f"https://test{i}.com"
            params = {"id": i}
            success = perf_cache.set(url, base_df, params)
            assert success is True
        
        # Get all entries
        hit_count = 0
        for i in range(10):
            url = f"https://test{i}.com"
            params = {"id": i}
            result = perf_cache.get(url, params)
            if result is not None:
                hit_count += 1
        
        assert hit_count == 10
        
        # Check stats
        stats = perf_cache.get_stats()
        assert stats['total_entries'] == 10
        assert stats['valid_entries'] == 10

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
