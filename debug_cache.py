#!/usr/bin/env python3
"""
Debug script for cache expiration issue
"""

import sys
import os
import tempfile
import pandas as pd
import time
import sqlite3
from datetime import datetime, timedelta

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cache_manager import PollDataCache

def debug_cache_expiration():
    """Debug the cache expiration issue"""
    print("🔍 Debugging cache expiration...")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        cache = PollDataCache(db_path=tmp.name)
        
        test_data = pd.DataFrame({
            'Date': ['2025-08-30'],
            'Pollster': ['DebugTest'],
            'Con': [25],
            'Lab': [45]
        })
        
        url = "https://test.com/debug"
        
        # Set data with short TTL
        cache.set(url, test_data, {"id": "expire"}, ttl=2)
        
        # Check database directly
        conn = sqlite3.connect(tmp.name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT expires_at, CURRENT_TIMESTAMP FROM poll_cache WHERE cache_key = ?', 
                      (cache._generate_cache_key(url, {"id": "expire"}),))
        result = cursor.fetchone()
        
        if result:
            expires_at, current_time = result
            print(f"📅 Expires at: {expires_at}")
            print(f"🕒 Current time: {current_time}")
            print(f"🔢 Comparison: {expires_at} > {current_time} = {expires_at > current_time}")
        
        # Wait and check again
        print("⏳ Waiting 3 seconds...")
        time.sleep(3)
        
        cursor.execute('SELECT expires_at, CURRENT_TIMESTAMP FROM poll_cache WHERE cache_key = ?', 
                      (cache._generate_cache_key(url, {"id": "expire"}),))
        result = cursor.fetchone()
        
        if result:
            expires_at, current_time = result
            print(f"📅 Expires at: {expires_at}")
            print(f"🕒 Current time: {current_time}")
            print(f"🔢 Comparison: {expires_at} > {current_time} = {expires_at > current_time}")
            
            # Test the exact query used in get()
            cursor.execute('''
                SELECT data_json, expires_at, access_count
                FROM poll_cache 
                WHERE cache_key = ? AND expires_at > CURRENT_TIMESTAMP
            ''', (cache._generate_cache_key(url, {"id": "expire"}),))
            
            get_result = cursor.fetchone()
            print(f"📋 Query result: {get_result is not None}")
        
        conn.close()
        
        # Test cache.get()
        cached_result = cache.get(url, {"id": "expire"})
        print(f"🎯 Cache get result: {cached_result is not None}")
        
        # Cleanup
        os.unlink(tmp.name)

if __name__ == "__main__":
    debug_cache_expiration()
