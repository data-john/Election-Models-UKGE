"""
Unit tests for polls.py functions
Tests all polling data processing and analysis functions
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock, Mock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from polls import (
    try_to_int,
    try_to_float,
    calculate_others,
    get_latest_polls,
    wiki_polls_preprocessing,
    get_wiki_polls_table,
    get_latest_polls_from_html,
    get_latest_polls_dict,
    get_weighted_poll_avg,
    next_col_dict,
    col_dict24,
    col_dict19,
    col_dict17,
    col_dict15,
    col_dict10,
    col_dict05
)


class TestUtilityFunctions:
    """Test utility functions for data conversion and calculation"""
    
    def test_try_to_int_valid_string(self):
        """Test try_to_int with valid string numbers"""
        assert try_to_int("42") == 42
        assert try_to_int("0") == 0
        assert try_to_int("-5") == -5
    
    def test_try_to_int_valid_int(self):
        """Test try_to_int with integer input"""
        assert try_to_int(42) == 42
        assert try_to_int(0) == 0
        assert try_to_int(-5) == -5
    
    def test_try_to_int_invalid_input(self):
        """Test try_to_int with invalid input returns 0"""
        assert try_to_int("invalid") == 0
        assert try_to_int("12.5") == 0
        assert try_to_int(None) == 0
        assert try_to_int("") == 0
        assert try_to_int("abc123") == 0
    
    def test_try_to_float_valid_string(self):
        """Test try_to_float with valid string numbers"""
        assert try_to_float("42.5") == 42.5
        assert try_to_float("0") == 0.0
        assert try_to_float("-5.25") == -5.25
        assert try_to_float("100") == 100.0
    
    def test_try_to_float_valid_float(self):
        """Test try_to_float with float input"""
        assert try_to_float(42.5) == 42.5
        assert try_to_float(0.0) == 0.0
        assert try_to_float(-5.25) == -5.25
    
    def test_try_to_float_invalid_input(self):
        """Test try_to_float with invalid input returns 999"""
        assert try_to_float("invalid") == 999
        assert try_to_float(None) == 999
        assert try_to_float("") == 999
        assert try_to_float("abc123") == 999
    
    def test_calculate_others_normal_case(self):
        """Test calculate_others with normal percentage values"""
        # Test case where parties sum to less than 1
        parties = [0.30, 0.25, 0.15, 0.10, 0.05]  # Sum = 0.85
        result = calculate_others(parties)
        assert abs(result - 0.15) < 1e-10
    
    def test_calculate_others_full_coverage(self):
        """Test calculate_others when parties sum to 1"""
        parties = [0.40, 0.35, 0.15, 0.10]  # Sum = 1.00
        result = calculate_others(parties)
        assert abs(result - 0.0) < 1e-10
    
    def test_calculate_others_over_coverage(self):
        """Test calculate_others when parties sum to more than 1"""
        parties = [0.40, 0.35, 0.20, 0.15]  # Sum = 1.10
        result = calculate_others(parties)
        assert abs(result - (-0.10)) < 1e-10
    
    def test_calculate_others_empty_list(self):
        """Test calculate_others with empty list"""
        result = calculate_others([])
        assert result == 1.0


class TestPollDataProcessing:
    """Test functions for processing poll data"""
    
    @pytest.fixture
    def sample_poll_df(self):
        """Create sample poll DataFrame for testing"""
        return pd.DataFrame({
            'Date': ['2025-08-30', '2025-08-29', '2025-08-28', '2025-08-27'],
            'Polling organisation': ['YouGov', 'Opinium', 'Survation', 'YouGov'],
            'Sample size': [1500, 1200, 1000, 1400],
            'Total': [1.0, 0.98, 1.02, 0.99],
            'Con': [0.22, 0.23, 0.21, 0.24],
            'Lab': [0.44, 0.43, 0.45, 0.42],
            'LD': [0.11, 0.12, 0.11, 0.10],
            'SNP': [0.03, 0.03, 0.03, 0.03],
            'Grn': [0.06, 0.05, 0.06, 0.07],
            'Ref': [0.14, 0.14, 0.14, 0.14]
        })
    
    def test_get_latest_polls_basic(self, sample_poll_df):
        """Test get_latest_polls basic functionality"""
        result = get_latest_polls(sample_poll_df, n=2)
        
        assert len(result) == 2
        assert isinstance(result, pd.DataFrame)
        # Should return first 2 rows (most recent)
        assert result.iloc[0]['Date'] == '2025-08-30'
        assert result.iloc[1]['Date'] == '2025-08-29'
    
    def test_get_latest_polls_filter_totals(self):
        """Test get_latest_polls filters out polls with bad totals"""
        bad_df = pd.DataFrame({
            'Date': ['2025-08-30', '2025-08-29', '2025-08-28'],
            'Polling organisation': ['YouGov', 'Opinium', 'Survation'],
            'Total': [1.0, 0.95, 1.05],  # Middle one should be filtered out
            'Con': [0.22, 0.23, 0.21],
        })
        
        result = get_latest_polls(bad_df, n=3)
        
        # Should only return 1 poll (1.05 is outside the 0.97-1.03 range too)
        assert len(result) == 1
        assert result.iloc[0]['Total'] == 1.0
    
    def test_get_latest_polls_no_repeated_pollsters(self, sample_poll_df):
        """Test get_latest_polls removes duplicate pollsters by default"""
        result = get_latest_polls(sample_poll_df, n=4, allow_repeated_pollsters=False)
        
        # Should have only 3 unique pollsters (YouGov appears twice)
        assert len(result) == 3
        pollsters = result['Polling organisation'].tolist()
        assert len(set(pollsters)) == 3  # All unique
        assert 'YouGov' in pollsters
        assert 'Opinium' in pollsters
        assert 'Survation' in pollsters
    
    def test_get_latest_polls_allow_repeated_pollsters(self, sample_poll_df):
        """Test get_latest_polls allows repeated pollsters when specified"""
        result = get_latest_polls(sample_poll_df, n=4, allow_repeated_pollsters=True)
        
        # Should return all 4 rows
        assert len(result) == 4
        pollsters = result['Polling organisation'].tolist()
        assert pollsters.count('YouGov') == 2  # YouGov appears twice


class TestWikiPollsPreprocessing:
    """Test wiki polls preprocessing functionality"""
    
    @pytest.fixture
    def sample_wiki_df(self):
        """Create sample DataFrame mimicking Wikipedia poll table structure"""
        # Create multi-level columns as Wikipedia tables have
        # Use sample sizes without commas since try_to_int doesn't handle them
        df = pd.DataFrame({
            ('Sample size', ''): ['1500', '1200', '1000'],  # No commas
            ('Con', ''): ['22%', '23%', '21%'],
            ('Lab', ''): ['44%', '43%', '45%'],
            ('Lib Dems', ''): ['11%', '12%', '11%'],
            ('SNP', ''): ['3%', '3%', '3%'],
            ('Green', ''): ['6%', '5%', '6%'],
            ('Reform', ''): ['14%', '14%', '14%'],
            ('Others', ''): [9.99, 9.99, 9.99]  # Placeholder values
        })
        df.columns = pd.MultiIndex.from_tuples(df.columns)
        return df
    
    def test_wiki_polls_preprocessing_column_processing(self, sample_wiki_df):
        """Test that wiki_polls_preprocessing correctly processes columns"""
        result = wiki_polls_preprocessing(sample_wiki_df)
        
        # Check that sample size is converted to int
        assert result['Sample size'].dtype in ['int64', 'int32']
        assert result['Sample size'].iloc[0] == 1500
        
        # Check that percentage columns are converted to floats
        assert result['Con'].iloc[0] == 0.22
        assert result['Lab'].iloc[0] == 0.44
        assert result['Lib Dems'].iloc[0] == 0.11
        
        # Check that 'Others' is calculated when it was 9.99 (placeholder)
        assert result['Others'].iloc[0] == calculate_others([0.22, 0.44, 0.11, 0.03, 0.06, 0.14])
    
    def test_wiki_polls_preprocessing_custom_col_names(self, sample_wiki_df):
        """Test wiki_polls_preprocessing with custom column names"""
        custom_dict = {
            "Con": "Con",  # Keep original column name for this test
            "Lab": "Lab",
            "Lib": "Lib Dems",
            "Nat": "SNP",
            "Grn": "Green",
            "Ref": "Reform",
            "Oth": "Others",
        }
        
        result = wiki_polls_preprocessing(sample_wiki_df, col_names=custom_dict)
        
        # Check that columns are processed correctly
        assert 'Con' in result.columns
        assert 'Lab' in result.columns
        assert result['Con'].iloc[0] == 0.22
        assert result['Lab'].iloc[0] == 0.44
    
    def test_wiki_polls_preprocessing_filters_zero_sample_size(self):
        """Test that polls with zero sample size are filtered out"""
        df = pd.DataFrame({
            ('Sample size', ''): ['1500', '0', '1000'],  # No commas
            ('Con', ''): ['22%', '23%', '21%'],
            ('Lab', ''): ['44%', '43%', '45%'],
            ('Lib Dems', ''): ['11%', '12%', '11%'],
            ('SNP', ''): ['3%', '3%', '3%'],
            ('Green', ''): ['6%', '5%', '6%'],
            ('Reform', ''): ['14%', '14%', '14%'],
            ('Others', ''): [9.99, 9.99, 9.99]
        })
        df.columns = pd.MultiIndex.from_tuples(df.columns)
        
        result = wiki_polls_preprocessing(df)
        
        # Should filter out the row with sample size 0
        assert len(result) == 2
        assert 0 not in result['Sample size'].values
    
    def test_wiki_polls_preprocessing_adds_total_column(self, sample_wiki_df):
        """Test that Total column is added correctly"""
        result = wiki_polls_preprocessing(sample_wiki_df)
        
        assert 'Total' in result.columns
        # Check that total is sum of all party percentages
        expected_total = (result['Con'] + result['Lab'] + result['Lib Dems'] + 
                         result['SNP'] + result['Green'] + result['Reform'] + result['Others']).iloc[0]
        assert abs(result['Total'].iloc[0] - expected_total) < 1e-10


class TestMockedWebFunctions:
    """Test functions that require web scraping with mocked data"""
    
    @patch('requests.get')
    @patch('polls.pd.read_html')
    def test_get_wiki_polls_table(self, mock_read_html, mock_requests_get):
        """Test the enhanced get_wiki_polls_table function with HTTP requests"""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><table>Mock table content</table></html>"
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response
        
        # Mock pandas read_html
        mock_table = pd.DataFrame({
            'Date': ['2025-08-30'],
            'Con': ['22%'],
            'Lab': ['44%'],
            'Sample size': ['1500']
        })
        mock_read_html.return_value = [mock_table, pd.DataFrame()]  # Second table without Con column
        
        result = get_wiki_polls_table("http://test.com")
        
        assert isinstance(result, pd.DataFrame)
        assert 'Con' in result.columns
        mock_requests_get.assert_called_once()
        mock_read_html.assert_called_once()
    
    @patch('polls.get_wiki_polls_table')
    def test_get_latest_polls_from_html(self, mock_get_table):
        """Test get_latest_polls_from_html function"""
        # Create mock data that would come from wiki table
        # Use the correct column names that match next_col_dict
        mock_df = pd.DataFrame({
            ('Sample size', ''): ['1500', '1200'],  # No commas
            ('Polling organisation', ''): ['YouGov', 'Opinium'],  # Add polling org column
            ('Con', ''): ['22%', '23%'],
            ('Lab', ''): ['44%', '43%'],
            ('LD', ''): ['11%', '12%'],
            ('SNP', ''): ['3%', '3%'],
            ('Grn', ''): ['6%', '5%'],
            ('Ref', ''): ['14%', '14%'],
            ('Others', ''): [9.99, 9.99]
        })
        mock_df.columns = pd.MultiIndex.from_tuples(mock_df.columns)
        mock_get_table.return_value = mock_df
        
        result = get_latest_polls_from_html("http://test.com", col_dict=next_col_dict, n=2)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) <= 2
        mock_get_table.assert_called_once_with("http://test.com")
    
    @patch('polls.get_latest_polls_from_html')
    def test_get_latest_polls_dict(self, mock_get_polls):
        """Test get_latest_polls_dict function"""
        # Mock the return data
        mock_df = pd.DataFrame({
            'Con': [0.22, 0.23, 0.21],
            'Lab': [0.44, 0.43, 0.45],
            'LD': [0.11, 0.12, 0.11],
            'SNP': [0.03, 0.03, 0.03],
            'Grn': [0.06, 0.05, 0.06],
            'Ref': [0.14, 0.14, 0.14],
            'Others': [0.02, 0.02, 0.02]
        })
        mock_get_polls.return_value = mock_df
        
        result = get_latest_polls_dict(n=3)
        
        assert isinstance(result, dict)
        # Should have 3 polls * 7 parties = 21 entries
        assert len(result) == 21
        
        # Check that keys are properly formatted
        assert 'Con0' in result
        assert 'Lab0' in result
        assert 'Con2' in result
        assert 'Lab2' in result
        
        # Check values
        assert result['Con0'] == 0.22
        assert result['Lab1'] == 0.43
    
    @patch('polls.get_latest_polls_from_html')
    def test_get_weighted_poll_avg(self, mock_get_polls):
        """Test get_weighted_poll_avg function"""
        # Mock returns for both n=3 and n=10 calls
        # Use the actual column names from next_col_dict
        mock_df_3 = pd.DataFrame({
            'Con': [0.22, 0.23, 0.21],
            'Lab': [0.44, 0.43, 0.45],
            'LD': [0.11, 0.12, 0.11],
            'SNP': [0.03, 0.03, 0.03],
            'Grn': [0.06, 0.05, 0.06],
            'Ref': [0.14, 0.14, 0.14],
            'Others': [0.02, 0.02, 0.02]
        })
        
        mock_df_10 = pd.DataFrame({
            'Con': [0.22, 0.23, 0.21, 0.20, 0.24, 0.22, 0.23, 0.21, 0.22, 0.23],
            'Lab': [0.44, 0.43, 0.45, 0.46, 0.42, 0.44, 0.43, 0.45, 0.44, 0.43],
            'LD': [0.11, 0.12, 0.11, 0.10, 0.13, 0.11, 0.12, 0.11, 0.11, 0.12],
            'SNP': [0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03],
            'Grn': [0.06, 0.05, 0.06, 0.06, 0.06, 0.06, 0.05, 0.06, 0.06, 0.05],
            'Ref': [0.14, 0.14, 0.14, 0.14, 0.14, 0.14, 0.14, 0.14, 0.14, 0.14],
            'Others': [0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02]
        })
        
        mock_get_polls.side_effect = [mock_df_3, mock_df_10]
        
        result = get_weighted_poll_avg("http://test.com", next_col_dict)
        
        assert isinstance(result, pd.Series)
        assert 'Con' in result.index
        assert 'Lab' in result.index
        assert 'LD' in result.index
        
        # Verify it was called twice (once for n=3, once for n=10)
        assert mock_get_polls.call_count == 2


class TestConstants:
    """Test that column dictionaries are properly defined"""
    
    def test_column_dictionaries_exist(self):
        """Test that all column dictionaries are defined"""
        assert isinstance(next_col_dict, dict)
        assert isinstance(col_dict24, dict)
        assert isinstance(col_dict19, dict)
        assert isinstance(col_dict17, dict)
        assert isinstance(col_dict15, dict)
        assert isinstance(col_dict10, dict)
        assert isinstance(col_dict05, dict)
    
    def test_column_dictionaries_have_required_keys(self):
        """Test that column dictionaries have required party keys"""
        required_keys = ["Con", "Lab", "Lib", "Oth"]
        
        for col_dict in [next_col_dict, col_dict24, col_dict19, col_dict17]:
            for key in required_keys:
                assert key in col_dict, f"Missing key {key} in column dictionary"
    
    def test_column_dictionaries_values_are_strings(self):
        """Test that all column dictionary values are strings"""
        for col_dict in [next_col_dict, col_dict24, col_dict19, col_dict17, col_dict15, col_dict10, col_dict05]:
            for key, value in col_dict.items():
                assert isinstance(value, str), f"Value for key {key} should be string, got {type(value)}"


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_get_latest_polls_empty_dataframe(self):
        """Test get_latest_polls with empty DataFrame"""
        empty_df = pd.DataFrame()
        # The function will fail on empty DataFrame due to trying to access pollster_cols[0]
        with pytest.raises(IndexError):
            get_latest_polls(empty_df, n=5)
    
    def test_calculate_others_with_negative_values(self):
        """Test calculate_others handles negative percentages"""
        parties = [-0.1, 0.3, 0.4, 0.2]  # Contains negative value
        result = calculate_others(parties)
        # Should still calculate: 1 - sum(parties) = 1 - 0.8 = 0.2
        assert abs(result - 0.2) < 1e-10
    
    def test_try_functions_with_various_types(self):
        """Test utility functions with various input types"""
        # Test with different numeric types
        assert try_to_int(42.0) == 42
        assert try_to_int(np.int32(42)) == 42
        assert try_to_float(np.float32(42.5)) == 42.5
        
        # Test with boolean (Python's int() can convert bool - True becomes 1)
        assert try_to_int(True) == 1  # bool is converted to int
        assert try_to_int(False) == 0  # False becomes 0
        assert try_to_float(True) == 1.0  # bool is converted to float
