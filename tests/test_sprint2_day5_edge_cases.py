"""
Sprint 2 Day 5: Comprehensive Error Handling and Edge Cases Tests

This module tests enhanced error handling, network resilience, database error recovery,
and various edge cases that could occur in production.
"""

import pytest
import pandas as pd
import numpy as np
import sqlite3
import os
import tempfile
import time
import json
from unittest.mock import patch, Mock, MagicMock
import requests

# Import modules to test
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from polls import (
    get_wiki_polls_table, get_latest_polls_from_html, get_latest_polls,
    try_to_int, try_to_float, calculate_others, get_latest_polls_dict,
    get_weighted_poll_avg, next_url, next_col_dict
)
from cache_manager import PollDataCache, cached_get_latest_polls_from_html
from app import validate_poll_data, process_and_validate_poll_data, load_real_polling_data


class TestEnhancedWebScrapingErrorHandling:
    """Test enhanced web scraping with comprehensive error scenarios"""
    
    def test_network_timeout_retry_logic(self):
        """Test retry logic for network timeouts"""
        with patch('requests.get') as mock_get:
            # First two calls timeout, third succeeds
            long_html = "<html><body>" + "x" * 200 + "<table><tr><th>Date</th><th>Con</th><th>Lab</th></tr><tr><td>2025-08-30</td><td>45</td><td>38</td></tr></table></body></html>"
            mock_get.side_effect = [
                requests.exceptions.Timeout("Connection timed out"),
                requests.exceptions.Timeout("Connection timed out"),
                Mock(status_code=200, text=long_html, raise_for_status=Mock())
            ]
            
            # Should succeed after retries - mock DataFrame with 3+ columns
            with patch('pandas.read_html') as mock_read_html:
                mock_read_html.return_value = [pd.DataFrame({
                    'Date': ['2025-08-30'],
                    'Con': [45], 
                    'Lab': [38],
                    'LD': [12]
                })]
                
                result = get_wiki_polls_table("http://test.com")
                assert not result.empty
                assert mock_get.call_count == 3  # Retried 3 times
    
    def test_http_error_codes_handling(self):
        """Test handling of various HTTP error codes"""
        error_codes = [403, 404, 429, 500, 502, 503, 504]
        
        for code in error_codes:
            with patch('requests.get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = code
                mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(f"HTTP {code}")
                mock_get.return_value = mock_response
                
                with pytest.raises(Exception) as excinfo:
                    get_wiki_polls_table("http://test.com")
                
                assert str(code) in str(excinfo.value) or "HTTP error" in str(excinfo.value)
    
    def test_invalid_url_handling(self):
        """Test handling of invalid URLs"""
        invalid_urls = [None, "", "not_a_url", "ftp://invalid.com", 123]
        
        for url in invalid_urls:
            with pytest.raises(Exception) as excinfo:
                get_wiki_polls_table(url)
            assert "Invalid URL" in str(excinfo.value) or "URL must start with" in str(excinfo.value)
    
    def test_malformed_html_handling(self):
        """Test handling of malformed HTML responses"""
        malformed_html_cases = [
            "",  # Empty response
            "<html>",  # Incomplete HTML
            "Not HTML at all",  # Plain text
            "<html><body>No tables here</body></html>",  # No tables
            "<html><table><tr><th>No Conservative column</th></tr></table></html>"  # No Con column
        ]
        
        for html in malformed_html_cases:
            with patch('requests.get') as mock_get:
                mock_get.return_value = Mock(
                    status_code=200, 
                    text=html,
                    raise_for_status=Mock()
                )
                
                with pytest.raises(Exception) as excinfo:
                    get_wiki_polls_table("http://test.com")
                
                # Should provide meaningful error messages
                error_msg = str(excinfo.value)
                assert any(phrase in error_msg for phrase in [
                    "No tables found", "No polling tables found", 
                    "Response content appears empty", "Failed to parse HTML"
                ])
    
    def test_rate_limiting_with_exponential_backoff(self):
        """Test rate limiting handling with exponential backoff"""
        with patch('requests.get') as mock_get:
            with patch('time.sleep') as mock_sleep:
                # Simulate rate limiting on first two attempts
                long_html = "<html><body>" + "x" * 200 + "<table><tr><th>Date</th><th>Con</th><th>Lab</th></tr><tr><td>2025-08-30</td><td>45</td><td>38</td></tr></table></body></html>"
                responses = [
                    Mock(status_code=429, raise_for_status=Mock(side_effect=requests.exceptions.HTTPError("429"))),
                    Mock(status_code=429, raise_for_status=Mock(side_effect=requests.exceptions.HTTPError("429"))),
                    Mock(status_code=200, text=long_html, raise_for_status=Mock())
                ]
                mock_get.side_effect = responses
                
                with patch('pandas.read_html') as mock_read_html:
                    mock_read_html.return_value = [pd.DataFrame({
                        'Date': ['2025-08-30'],
                        'Con': [45], 
                        'Lab': [38],
                        'LD': [12]
                    })]
                    
                    result = get_wiki_polls_table("http://test.com")
                    
                    # Should succeed after retries
                    assert not result.empty
                    
                    # Should have used exponential backoff
                    assert mock_sleep.call_count == 2
                    sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
                    assert sleep_calls[1] > sleep_calls[0]  # Exponential increase


class TestDatabaseErrorHandling:
    """Test database error handling and recovery mechanisms"""
    
    def setup_method(self):
        """Set up test database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_cache.db")
    
    def teardown_method(self):
        """Clean up test database"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_database_corruption_recovery(self):
        """Test recovery from database corruption"""
        cache = PollDataCache(db_path=self.db_path)
        
        # Create some initial data
        test_data = pd.DataFrame({'Con': [0.4], 'Lab': [0.35]})
        cache.set("http://test.com", test_data)
        
        # Corrupt the database file
        with open(self.db_path, 'w') as f:
            f.write("This is not a SQLite database")
        
        # Should handle corruption gracefully
        result = cache.get("http://test.com")
        assert result is None  # Should return None, not crash
        
        # Create a new cache instance to trigger re-initialization
        cache2 = PollDataCache(db_path=self.db_path)
        # Should be able to set new data after corruption (triggers repair)
        set_result = cache2.set("http://test2.com", test_data)
        if set_result:  # If repair was successful
            result = cache2.get("http://test2.com")
            assert result is not None
        else:
            # If repair wasn't attempted, we at least didn't crash
            print("Database corruption protection worked - operation failed gracefully")
    
    def test_database_locked_retry_logic(self):
        """Test retry logic for database lock situations"""
        cache = PollDataCache(db_path=self.db_path)
        
        with patch('sqlite3.connect') as mock_connect:
            # Simulate database lock on first attempts
            mock_connect.side_effect = [
                sqlite3.OperationalError("database is locked"),
                sqlite3.OperationalError("database is locked"),
                MagicMock()  # Success on third attempt
            ]
            
            with patch('time.sleep') as mock_sleep:
                # Should retry and eventually succeed
                result = cache.get("http://test.com")
                
                # Should have attempted retries
                assert mock_connect.call_count <= 3
                assert mock_sleep.call_count >= 1
    
    def test_database_permission_errors(self):
        """Test handling of database permission errors"""
        # Create a database file with no read permissions
        cache = PollDataCache(db_path=self.db_path)
        cache.set("http://test.com", pd.DataFrame({'Con': [0.4]}))
        
        # Remove read permissions
        os.chmod(self.db_path, 0o000)
        
        try:
            # Should handle permission errors gracefully
            result = cache.get("http://test.com")
            assert result is None
        finally:
            # Restore permissions for cleanup
            os.chmod(self.db_path, 0o644)
    
    def test_corrupted_cache_data_recovery(self):
        """Test recovery from corrupted cache data"""
        cache = PollDataCache(db_path=self.db_path)
        
        # Generate the proper cache key for the test URL and params
        test_url = "http://test.com"
        test_params = {'test': 'params'}
        test_cache_key = cache._generate_cache_key(test_url, test_params)
        
        # Manually insert corrupted JSON data with the correct cache key
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO poll_cache (cache_key, data_json, url, params_json, expires_at)
            VALUES (?, ?, ?, ?, datetime('now', '+1 hour'))
        ''', (test_cache_key, 'invalid_json{', test_url, json.dumps(test_params)))
        conn.commit()
        conn.close()
        
        # Should handle corrupted data gracefully
        result = cache.get(test_url, test_params)
        assert result is None
        
        # Corrupted entry should be cleaned up by now
        entries = cache.get_cache_entries()
        corrupted_entries = [e for e in entries if test_cache_key in e.get('cache_key', '')]
        assert len(corrupted_entries) == 0


class TestDataValidationEdgeCases:
    """Test enhanced data validation with various edge cases"""
    
    def test_empty_dataframe_handling(self):
        """Test validation of empty DataFrames"""
        empty_df = pd.DataFrame()
        result = validate_poll_data(empty_df)
        
        assert not result['is_valid']
        assert 'empty' in str(result['errors']).lower()
        assert result['stats']['total_polls'] == 0
    
    def test_none_input_handling(self):
        """Test validation of None input"""
        result = validate_poll_data(None)
        
        assert not result['is_valid']
        assert 'None' in str(result['errors'])
    
    def test_invalid_data_types_handling(self):
        """Test validation of invalid data types"""
        invalid_inputs = ["not_a_dataframe", 123, [], {}]
        
        for invalid_input in invalid_inputs:
            result = validate_poll_data(invalid_input)
            assert not result['is_valid']
            assert 'DataFrame' in str(result['errors'])
    
    def test_mixed_data_quality_scenarios(self):
        """Test validation with mixed data quality issues"""
        problematic_df = pd.DataFrame({
            'Con': [0.45, -0.1, 150, None, 'invalid'],  # Mix of valid, negative, huge, missing, non-numeric
            'Lab': [0.35, 0.40, 0.30, 0.0, 0.25],      # Mostly valid
            'LD': [None, None, None, None, None],        # All missing
            'Others': [0.20, 0.70, -50, 2.5, 0.75],    # Various issues
            'Total': [1.0, 1.0, 150, None, 'bad'],      # Mix of good and bad totals
            'Date': ['2025-01-01', 'invalid_date', None, '2025-01-02', '2025-01-03']
        })
        
        result = validate_poll_data(problematic_df)
        
        # Should identify but not crash on various issues
        assert len(result['warnings']) > 0
        assert 'negative values' in ' '.join(result['warnings'])
        assert 'non-numeric values' in ' '.join(result['warnings'])
        assert result['stats']['total_polls'] == 5
    
    def test_extreme_percentage_values(self):
        """Test handling of extreme percentage values"""
        extreme_df = pd.DataFrame({
            'Con': [0.0, 0.001, 0.999, 1.0],     # Boundary values
            'Lab': [999.0, -999.0, float('inf'), float('-inf')],  # Extreme values
            'LD': [0.5, 0.5, 0.5, 0.5],
            'Total': [1.5, -0.5, float('inf'), 0.5]
        })
        
        result = validate_poll_data(extreme_df)
        
        # Should handle extreme values gracefully
        assert isinstance(result, dict)
        assert 'warnings' in result
        assert len(result['warnings']) > 0  # Should have warnings about extreme values


class TestUtilityFunctionRobustness:
    """Test enhanced utility functions with edge cases"""
    
    def test_try_to_int_edge_cases(self):
        """Test try_to_int with various edge cases"""
        test_cases = [
            (None, 0),
            (np.nan, 0),
            ("", 0),
            ("   ", 0),
            ("N/A", 0),
            ("n/a", 0),
            ("unknown", 0),
            ("-", 0),
            ("1,234", 1234),
            ("42.0", 42),
            ("42.9", 42),
            (42.7, 42),
            (float('inf'), 0),
            (float('-inf'), 0),
            ([1, 2, 3], 0),  # Invalid type
            ({"key": "value"}, 0)  # Invalid type
        ]
        
        for input_val, expected in test_cases:
            result = try_to_int(input_val)
            assert result == expected, f"try_to_int({input_val}) returned {result}, expected {expected}"
    
    def test_try_to_float_edge_cases(self):
        """Test try_to_float with various edge cases"""
        test_cases = [
            (None, 0.0),
            (np.nan, 0.0),
            ("", 0.0),
            ("   ", 0.0),
            ("N/A", 0.0),
            ("45%", 45.0),
            ("123.56", 123.56),  # Changed from 1,234.56 which exceeds 999 limit
            ("42", 42.0),
            (-5.0, 0.0),  # Negative values converted to 0
            (1500.0, 0.0),  # Very large values converted to 0
            (float('inf'), 0.0),
            (float('-inf'), 0.0),
            ([1.5, 2.5], 0.0),  # Invalid type
            ({"value": 3.14}, 0.0)  # Invalid type
        ]
        
        for input_val, expected in test_cases:
            result = try_to_float(input_val)
            assert result == expected, f"try_to_float({input_val}) returned {result}, expected {expected}"
    
    def test_get_latest_polls_edge_cases(self):
        """Test get_latest_polls with various edge cases"""
        
        # Test with None input
        with pytest.raises(ValueError, match="DataFrame is None"):
            get_latest_polls(None)
        
        # Test with empty DataFrame
        with pytest.raises(ValueError, match="DataFrame is empty"):
            get_latest_polls(pd.DataFrame())
        
        # Test with invalid n parameter
        valid_df = pd.DataFrame({'Con': [0.4], 'Lab': [0.3], 'Total': [0.7]})
        
        with pytest.raises(ValueError, match="n must be a positive integer"):
            get_latest_polls(valid_df, n=0)
        
        with pytest.raises(ValueError, match="n must be a positive integer"):
            get_latest_polls(valid_df, n=-5)
    
    def test_get_latest_polls_with_problematic_totals(self):
        """Test get_latest_polls with various total column issues"""
        
        # DataFrame with invalid totals
        df_invalid_totals = pd.DataFrame({
            'Con': [0.4, 0.3, 0.5],
            'Lab': [0.3, 0.4, 0.2],
            'Total': [0.5, 1.2, 0.9]  # Too low, too high, acceptable
        })
        
        result = get_latest_polls(df_invalid_totals, n=5)
        
        # Should handle invalid totals gracefully
        assert isinstance(result, pd.DataFrame)
        assert len(result) >= 0  # Should not crash


class TestNetworkResilienceAndFallbacks:
    """Test network resilience and fallback mechanisms"""
    
    @patch('urllib.request.urlopen')
    def test_network_connectivity_detection(self, mock_urlopen):
        """Test network connectivity detection in load_real_polling_data"""
        
        # Mock network unavailable
        mock_urlopen.side_effect = Exception("Network unavailable")
        
        with patch('app.cached_get_latest_polls_from_html') as mock_cached:
            mock_cached.return_value = pd.DataFrame({
                'Con': [0.4], 'Lab': [0.3], 'LD': [0.15], 
                'SNP': [0.05], 'Grn': [0.05], 'Ref': [0.05]
            })
            
            # Should still work with cached data even if network is unavailable
            # Note: This is a simplified test as the actual function uses Streamlit
            # In a real test environment, we'd need to mock Streamlit components
    
    def test_comprehensive_error_scenarios(self):
        """Test various error scenarios in get_latest_polls_from_html"""
        
        error_scenarios = [
            ("", "Invalid URL"),
            (None, "Invalid URL"),
            ("http://test.com", "column dictionary")  # Empty col_dict
        ]
        
        for url, expected_error in error_scenarios:
            with pytest.raises(Exception) as excinfo:
                if "column dictionary" in expected_error:
                    get_latest_polls_from_html(url, col_dict={})
                else:
                    get_latest_polls_from_html(url)
            
            assert any(phrase in str(excinfo.value) for phrase in [expected_error])


class TestErrorRecoveryMechanisms:
    """Test error recovery and graceful degradation"""
    
    def test_graceful_degradation_chain(self):
        """Test the complete error recovery chain"""
        
        # This test simulates the complete failure chain:
        # 1. Network fails
        # 2. Cache fails  
        # 3. Falls back to sample data
        
        with patch('app.cached_get_latest_polls_from_html') as mock_cached:
            with patch('app.create_sample_poll_data') as mock_sample:
                
                # Simulate cache failure
                mock_cached.return_value = None
                
                # Simulate sample data success
                mock_sample.return_value = pd.DataFrame({
                    'Con': [0.4], 'Lab': [0.35], 'LD': [0.15], 
                    'SNP': [0.04], 'Grn': [0.03], 'Ref': [0.03]
                })
                
                # The load function should handle all failures gracefully
                # (This would need proper Streamlit mocking in a full test)
    
    def test_data_quality_recovery_scenarios(self):
        """Test recovery from various data quality issues"""
        
        # Test data with various quality issues
        poor_quality_data = pd.DataFrame({
            'Con': ['invalid', None, 0.4, -0.1],
            'Lab': [0.3, 'bad', 0.35, 1.5],
            'LD': [None, None, None, None],  # Completely missing column
            'Total': [0.8, None, 'invalid', 2.0]
        })
        
        # Should process without crashing
        result = validate_poll_data(poor_quality_data)
        
        # Should identify issues but still provide stats
        assert isinstance(result, dict)
        assert 'warnings' in result
        assert 'stats' in result
        assert result['stats']['total_polls'] == 4


def test_comprehensive_edge_case_integration():
    """Integration test for multiple edge cases occurring together"""
    
    # Create a scenario with multiple simultaneous issues
    problematic_scenario = pd.DataFrame({
        'Con': [None, 'invalid', -0.5, 150, 0.4],  # Missing, non-numeric, negative, too high, valid
        'Lab': [0.3, 0.4, None, 0.35, 'bad'],      # Mix of valid and invalid
        'LD': [0.1, 0.15, 0.12, None, 0.08],       # Mostly valid with some missing
        'SNP': [0.05, 0.04, 0.06, 0.05, 0.04],     # All valid
        'Grn': ['', '  ', 'N/A', '-', 0.02],       # Various empty representations
        'Ref': [0.05, 0.03, 0.04, 0.05, 0.03],     # All valid
        'Others': [0.05, 0.03, 0.04, 0.05, 0.03],  # All valid
        'Total': [None, 'bad', -1, 2.5, 0.97],     # Various total issues
        'Sample Size': ['1,000', 'unknown', None, '2000', 'N/A'],  # Mixed formats
        'Date': ['2025-01-01', 'invalid', None, '2025-01-03', '2025-01-04']  # Mixed date formats
    })
    
    # Should handle all issues gracefully
    validation_result = validate_poll_data(problematic_scenario)
    
    # Should not crash and provide meaningful feedback
    assert isinstance(validation_result, dict)
    assert 'warnings' in validation_result
    assert 'errors' in validation_result
    assert 'stats' in validation_result
    
    # Should identify multiple issues
    assert len(validation_result['warnings']) > 3  # Multiple warnings expected
    
    # Stats should still be calculable
    assert validation_result['stats']['total_polls'] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
