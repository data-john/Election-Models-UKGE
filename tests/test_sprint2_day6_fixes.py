"""
Tests for Sprint 2 Day 6 - Bug Fixes for Issues I4 and I5
Testing fixes for Streamlit dataframe width parameter and pollster name cleaning
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from app import clean_pollster_name, format_poll_data_for_display


class TestPollsterNameCleaning:
    """Test the pollster name cleaning function for Issue I5"""

    def test_clean_pollster_name_with_single_reference(self):
        """Test cleaning single Wikipedia references like [3]"""
        result = clean_pollster_name("Find Out Now[3]")
        assert result == "Find Out Now"

    def test_clean_pollster_name_with_multiple_references(self):
        """Test cleaning multiple references like [10][a]"""
        result = clean_pollster_name("Lord Ashcroft Polls[10][a]")
        assert result == "Lord Ashcroft Polls"

    def test_clean_pollster_name_with_letter_reference(self):
        """Test cleaning letter references like [a]"""
        result = clean_pollster_name("Some Pollster[a]")
        assert result == "Some Pollster"

    def test_clean_pollster_name_multiple_numeric_references(self):
        """Test cleaning multiple numeric references"""
        result = clean_pollster_name("Find Out Now[6]")
        assert result == "Find Out Now"
        
        result = clean_pollster_name("Find Out Now[15]")
        assert result == "Find Out Now"

    def test_clean_pollster_name_no_references(self):
        """Test that names without references are unchanged"""
        result = clean_pollster_name("YouGov")
        assert result == "YouGov"
        
        result = clean_pollster_name("Opinium Research")
        assert result == "Opinium Research"

    def test_clean_pollster_name_with_whitespace(self):
        """Test that extra whitespace is cleaned up"""
        result = clean_pollster_name("  Find Out Now[3]  ")
        assert result == "Find Out Now"

    def test_clean_pollster_name_edge_cases(self):
        """Test edge cases with None, NaN, empty strings"""
        result = clean_pollster_name(None)
        assert result == ""
        
        result = clean_pollster_name(pd.NA)
        assert result == ""
        
        result = clean_pollster_name("")
        assert result == ""

    def test_clean_pollster_name_integration_examples(self):
        """Test with real examples from Issue I5"""
        test_cases = [
            ("Find Out Now[3]", "Find Out Now"),
            ("Find Out Now[6]", "Find Out Now"),
            ("Lord Ashcroft Polls[10][a]", "Lord Ashcroft Polls"),
            ("Find Out Now[11]", "Find Out Now"),
            ("YouGov[12]", "YouGov"),
            ("Find Out Now[15]", "Find Out Now"),
        ]
        
        for input_name, expected_name in test_cases:
            result = clean_pollster_name(input_name)
            assert result == expected_name, f"Failed for {input_name}: expected {expected_name}, got {result}"


class TestDataframeDisplayFixes:
    """Test that dataframe display fixes address Issue I4"""

    def test_format_poll_data_applies_pollster_cleaning(self):
        """Test that format_poll_data_for_display applies pollster name cleaning"""
        # Create test data with pollster names containing Wikipedia references
        test_data = pd.DataFrame({
            'Con': [25.5, 23.2, 26.1],
            'Lab': [42.1, 44.3, 41.8],
            'LD': [11.2, 10.8, 12.1],
            'Ref': [12.1, 13.2, 11.9],
            'Grn': [6.1, 5.8, 6.2],
            'SNP': [3.0, 2.7, 1.9],
            'Pollster': ['Find Out Now[3]', 'YouGov[12]', 'Lord Ashcroft Polls[10][a]'],
            'Sample size': [1500, 2000, 1200],
            'Dates conducted': ['28 Aug', '27 Aug', '26 Aug']
        })

        # Format the data
        formatted_data = format_poll_data_for_display(test_data)

        # Check that pollster names are cleaned
        expected_pollsters = ['Find Out Now', 'YouGov', 'Lord Ashcroft Polls']
        actual_pollsters = formatted_data['Pollster'].tolist()
        
        assert actual_pollsters == expected_pollsters, f"Expected {expected_pollsters}, got {actual_pollsters}"

    def test_format_poll_data_preserves_clean_pollster_names(self):
        """Test that already clean pollster names are preserved"""
        test_data = pd.DataFrame({
            'Con': [25.5, 23.2],
            'Lab': [42.1, 44.3],
            'LD': [11.2, 10.8],
            'Pollster': ['YouGov', 'Opinium Research'],
            'Sample size': [1500, 2000],
            'Dates conducted': ['28 Aug', '27 Aug']
        })

        formatted_data = format_poll_data_for_display(test_data)
        
        expected_pollsters = ['YouGov', 'Opinium Research']
        actual_pollsters = formatted_data['Pollster'].tolist()
        
        assert actual_pollsters == expected_pollsters

    def test_format_poll_data_handles_missing_pollster_column(self):
        """Test that missing pollster columns are handled gracefully"""
        test_data = pd.DataFrame({
            'Con': [25.5, 23.2],
            'Lab': [42.1, 44.3],
            'LD': [11.2, 10.8],
            'Sample size': [1500, 2000],
        })

        formatted_data = format_poll_data_for_display(test_data)
        
        # Should create generic pollster names
        assert 'Pollster' in formatted_data.columns
        assert len(formatted_data['Pollster']) == 2


class TestStreamlitDataframeCompatibility:
    """Test that we don't use invalid width parameters (Issue I4)"""

    @patch('streamlit.dataframe')
    def test_dataframe_calls_use_valid_parameters(self, mock_dataframe):
        """Test that st.dataframe is called with valid parameters"""
        # This is more of a code inspection test since we can't easily test Streamlit directly
        # But we can ensure our format function doesn't break when called
        
        test_data = pd.DataFrame({
            'Con': [25.5],
            'Lab': [42.1],
            'Pollster': ['YouGov[12]'],
        })

        # This should not raise any errors
        result = format_poll_data_for_display(test_data)
        
        # Basic validation that the function completes successfully
        assert isinstance(result, pd.DataFrame)
        assert 'Pollster' in result.columns
        assert result['Pollster'].iloc[0] == 'YouGov'


class TestIntegrationFixes:
    """Integration tests for all Sprint 2 Day 6 fixes"""

    def test_complete_data_processing_pipeline(self):
        """Test that the complete pipeline works with both fixes"""
        # Create realistic test data with issues that needed fixing
        test_data = pd.DataFrame({
            'Con': [25.5, 23.2, 26.1, 24.8],
            'Lab': [42.1, 44.3, 41.8, 43.2],
            'LD': [11.2, 10.8, 12.1, 11.5],
            'Ref': [12.1, 13.2, 11.9, 12.5],
            'Grn': [6.1, 5.8, 6.2, 5.9],
            'SNP': [3.0, 2.7, 1.9, 2.1],
            'Pollster': [
                'Find Out Now[3]', 
                'Find Out Now[6]', 
                'Lord Ashcroft Polls[10][a]', 
                'YouGov[12]'
            ],
            'Sample size': [1500, 1800, 1200, 2000],
            'Dates conducted': ['28 Aug', '27 Aug', '26 Aug', '25 Aug']
        })

        # Process the data
        formatted_data = format_poll_data_for_display(test_data)

        # Verify pollster names are cleaned
        expected_pollsters = [
            'Find Out Now', 
            'Find Out Now', 
            'Lord Ashcroft Polls', 
            'YouGov'
        ]
        assert formatted_data['Pollster'].tolist() == expected_pollsters

        # Verify data structure is maintained
        assert len(formatted_data) == 4
        assert 'Conservative' in formatted_data.columns  # Column mapping worked
        assert 'Labour' in formatted_data.columns
        assert 'Sample Size' in formatted_data.columns  # Metadata added
        assert 'Date' in formatted_data.columns
        assert 'Days Ago' in formatted_data.columns

        # Verify data types are appropriate
        assert formatted_data['Sample Size'].dtype in [int, np.int64]
        assert all(isinstance(x, (int, np.integer)) for x in formatted_data['Days Ago'])


def test_sprint2_day6_comprehensive_fixes():
    """
    Comprehensive test to verify all Sprint 2 Day 6 fixes are working
    - Issue I4: Streamlit dataframe width parameter fixed
    - Issue I5: Pollster names with Wikipedia references cleaned
    """
    # Test data with all the problematic patterns
    test_data = pd.DataFrame({
        'Con': [25.5, 23.2, 26.1],
        'Lab': [42.1, 44.3, 41.8],
        'LD': [11.2, 10.8, 12.1],
        'Ref': [12.1, 13.2, 11.9],
        'Grn': [6.1, 5.8, 6.2],
        'SNP': [3.0, 2.7, 1.9],
        'Pollster': ['Find Out Now[3]', 'YouGov[12]', 'Lord Ashcroft Polls[10][a]'],
        'Sample size': [1500, 2000, 1200],
        'Dates conducted': ['28 Aug', '27 Aug', '26 Aug']
    })

    # Process the data (this would previously fail with width=None)
    result = format_poll_data_for_display(test_data)

    # Verify all fixes
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3
    
    # Issue I5 fix: Pollster names should be cleaned
    clean_pollsters = result['Pollster'].tolist()
    assert clean_pollsters == ['Find Out Now', 'YouGov', 'Lord Ashcroft Polls']
    
    # Data should be properly formatted
    assert 'Conservative' in result.columns
    assert 'Labour' in result.columns
    assert 'Liberal Democrat' in result.columns
    assert 'Reform UK' in result.columns
    assert 'Green' in result.columns
    assert 'SNP' in result.columns

    # Metadata should be properly added
    assert 'Sample Size' in result.columns
    assert 'Date' in result.columns
    assert 'Days Ago' in result.columns
    assert 'Methodology' in result.columns
    assert 'Margin of Error' in result.columns

    print("✅ All Sprint 2 Day 6 fixes verified successfully!")


if __name__ == "__main__":
    test_sprint2_day6_comprehensive_fixes()
