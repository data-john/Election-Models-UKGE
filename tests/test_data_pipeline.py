"""
Test suite for Sprint 2 Day 2: Data Processing and Validation Pipeline
Tests for Wikipedia polling data integration and validation
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import (
    process_and_validate_poll_data,
    validate_poll_data,
    format_poll_data_for_display
)


class TestDataValidationPipeline:
    """Test the data validation pipeline components"""
    
    def test_validate_poll_data_with_valid_data(self):
        """Test validation with properly formatted poll data"""
        # Create valid test data
        valid_data = pd.DataFrame({
            'Con': [0.22, 0.24, 0.21],
            'Lab': [0.44, 0.42, 0.45],
            'LD': [0.11, 0.12, 0.10],
            'SNP': [0.03, 0.04, 0.03],
            'Grn': [0.06, 0.05, 0.07],
            'Ref': [0.12, 0.11, 0.13],
            'Others': [0.02, 0.02, 0.01],
            'Total': [1.00, 1.00, 1.00]
        })
        
        result = validate_poll_data(valid_data)
        
        assert result['is_valid'] == True
        assert len(result['warnings']) == 0
        assert result['stats']['total_polls'] == 3
    
    def test_validate_poll_data_with_invalid_percentages(self):
        """Test validation with invalid percentage values"""
        # Create invalid test data
        invalid_data = pd.DataFrame({
            'Con': [1.22, 0.24, -0.05],  # Invalid values > 1 and < 0
            'Lab': [0.44, 0.42, 0.45],
            'LD': [0.11, 0.12, 0.10],
            'SNP': [0.03, 0.04, 0.03],
            'Grn': [0.06, 0.05, 0.07],
            'Ref': [0.12, 0.11, 0.13],
            'Others': [0.02, 0.02, 0.01],
            'Total': [2.00, 1.00, 0.85]  # Invalid totals
        })
        
        result = validate_poll_data(invalid_data)
        
        assert len(result['warnings']) > 0
        # Should have warnings about invalid percentages and totals
        warning_text = ' '.join(result['warnings'])
        assert 'Invalid percentages' in warning_text
        assert 'Invalid poll totals' in warning_text
    
    def test_validate_poll_data_with_missing_columns(self):
        """Test validation with missing required columns"""
        # Create data missing required columns
        incomplete_data = pd.DataFrame({
            'Con': [0.22, 0.24],
            'Lab': [0.44, 0.42],
            # Missing other required columns
        })
        
        result = validate_poll_data(incomplete_data)
        
        assert result['is_valid'] == False
        assert len(result['warnings']) > 0
        assert 'Missing columns' in result['warnings'][0]


class TestDataFormattingPipeline:
    """Test the data formatting pipeline components"""
    
    def test_format_poll_data_for_display(self):
        """Test formatting raw poll data for display"""
        # Create raw data (percentages as decimals)
        raw_data = pd.DataFrame({
            'Con': [0.22, 0.24, 0.21],
            'Lab': [0.44, 0.42, 0.45],
            'LD': [0.11, 0.12, 0.10],
            'SNP': [0.03, 0.04, 0.03],
            'Grn': [0.06, 0.05, 0.07],
            'Ref': [0.12, 0.11, 0.13],
            'Others': [0.02, 0.02, 0.01]
        })
        
        formatted_data = format_poll_data_for_display(raw_data)
        
        # Check that percentages are converted to display format (multiplied by 100)
        assert formatted_data['Con'].iloc[0] == 22.0
        assert formatted_data['Lab'].iloc[0] == 44.0
        
        # Check that required columns are added
        assert 'Pollster' in formatted_data.columns
        assert 'Sample Size' in formatted_data.columns
        assert 'Days Ago' in formatted_data.columns
        assert 'Methodology' in formatted_data.columns
        assert 'Margin of Error' in formatted_data.columns
    
    def test_format_poll_data_preserves_existing_metadata(self):
        """Test that existing metadata is preserved during formatting"""
        # Create data with existing metadata
        data_with_metadata = pd.DataFrame({
            'Con': [0.22, 0.24],
            'Lab': [0.44, 0.42],
            'LD': [0.11, 0.12],
            'SNP': [0.03, 0.04],
            'Grn': [0.06, 0.05],
            'Ref': [0.12, 0.11],
            'Others': [0.02, 0.02],
            'Pollster': ['YouGov', 'Opinium'],
            'Sample Size': [2000, 1500]
        })
        
        formatted_data = format_poll_data_for_display(data_with_metadata)
        
        # Check that existing metadata is preserved
        assert formatted_data['Pollster'].iloc[0] == 'YouGov'
        assert formatted_data['Pollster'].iloc[1] == 'Opinium'
        assert formatted_data['Sample Size'].iloc[0] == 2000
        assert formatted_data['Sample Size'].iloc[1] == 1500


class TestDataPipelineIntegration:
    """Test the complete data pipeline integration"""
    
    def test_process_and_validate_poll_data_complete_pipeline(self):
        """Test the complete processing and validation pipeline"""
        # Create realistic raw poll data
        raw_data = pd.DataFrame({
            'Con': [0.22, 0.24, 0.21],
            'Lab': [0.44, 0.42, 0.45],
            'LD': [0.11, 0.12, 0.10],
            'SNP': [0.03, 0.04, 0.03],
            'Grn': [0.06, 0.05, 0.07],
            'Ref': [0.12, 0.11, 0.13],
            'Others': [0.02, 0.02, 0.01],
            'Total': [1.00, 1.00, 1.00]
        })
        
        # Process through the complete pipeline
        processed_data = process_and_validate_poll_data(raw_data)
        
        # Check that data is properly processed
        assert not processed_data.empty
        assert len(processed_data) == 3
        
        # Check that percentages are converted to display format
        assert all(processed_data['Con'] >= 20)  # Should be in percentage format
        assert all(processed_data['Con'] <= 25)
        
        # Check that all required columns exist
        required_columns = ['Con', 'Lab', 'LD', 'SNP', 'Grn', 'Ref', 'Others', 
                          'Pollster', 'Sample Size', 'Methodology', 'Margin of Error']
        for col in required_columns:
            assert col in processed_data.columns
    
    def test_pipeline_handles_edge_cases(self):
        """Test that the pipeline handles edge cases gracefully"""
        # Empty DataFrame
        empty_data = pd.DataFrame()
        
        try:
            result = validate_poll_data(empty_data)
            # Should not crash and should return warnings
            assert len(result['warnings']) >= 0
        except Exception as e:
            pytest.fail(f"Pipeline should handle empty data gracefully, but got: {e}")
    
    def test_pipeline_error_handling(self):
        """Test that the pipeline handles errors gracefully"""
        # Create data that might cause processing errors
        problematic_data = pd.DataFrame({
            'Con': ['invalid', 0.24, None],  # Mixed invalid types
            'Lab': [0.44, 'also_invalid', 0.45],
        })
        
        # The validation should handle this gracefully
        result = validate_poll_data(problematic_data)
        
        # Should return with warnings rather than crashing
        assert 'warnings' in result
        assert isinstance(result['warnings'], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
