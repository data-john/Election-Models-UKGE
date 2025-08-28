"""
Basic tests for the main application functionality
Sprint 1: Test sample data generation and basic app components
"""

import pytest
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_app_imports():
    """Test that the main app module can be imported"""
    try:
        import app
        assert hasattr(app, 'main')
        assert hasattr(app, 'create_sample_poll_data')
    except ImportError as e:
        pytest.fail(f"Failed to import app module: {e}")

def test_create_sample_poll_data():
    """Test sample poll data generation"""
    from app import create_sample_poll_data
    
    # Generate sample data
    df = create_sample_poll_data()
    
    # Basic structure tests
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    
    # Check required columns
    required_columns = [
        'Date', 'Pollster', 'Sample Size', 
        'Conservative', 'Labour', 'Liberal Democrat', 
        'Reform UK', 'Green', 'SNP', 'Others'
    ]
    
    for col in required_columns:
        assert col in df.columns, f"Missing required column: {col}"
    
    # Check data types and ranges
    assert df['Sample Size'].dtype in ['int64', 'int32']
    assert df['Sample Size'].min() >= 100  # Reasonable sample size
    
    # Check polling percentages are reasonable
    party_cols = ['Conservative', 'Labour', 'Liberal Democrat', 'Reform UK', 'Green', 'SNP', 'Others']
    for col in party_cols:
        assert df[col].min() >= 0, f"{col} has negative values"
        assert df[col].max() <= 100, f"{col} has values > 100%"

def test_sample_poll_data_consistency():
    """Test that sample data is internally consistent"""
    from app import create_sample_poll_data
    
    df = create_sample_poll_data()
    
    # Test date format
    pd.to_datetime(df['Date'])  # Should not raise an exception
    
    # Test pollster names are strings
    assert df['Pollster'].dtype == 'object'
    assert all(isinstance(name, str) for name in df['Pollster'])
    
    # Test that we have multiple pollsters
    assert df['Pollster'].nunique() > 1

def test_basic_functionality_with_sample_data(sample_poll_data):
    """Test basic app functionality with fixture data"""
    
    # Test that we can process the sample data
    assert len(sample_poll_data) == 3
    assert 'Conservative' in sample_poll_data.columns
    assert 'Labour' in sample_poll_data.columns
    
    # Test basic statistics
    con_avg = sample_poll_data['Conservative'].mean()
    assert 20 <= con_avg <= 25  # Reasonable range based on sample data

if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
