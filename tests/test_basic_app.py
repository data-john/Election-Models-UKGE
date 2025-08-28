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
    """Test enhanced sample poll data generation"""
    from app import create_sample_poll_data
    
    # Generate sample data
    df = create_sample_poll_data()
    
    # Basic structure tests
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    
    # Check required columns (updated for enhanced version)
    required_columns = [
        'Date', 'Pollster', 'Sample Size', 'Methodology', 'Margin of Error',
        'Conservative', 'Labour', 'Liberal Democrat', 
        'Reform UK', 'Green', 'SNP', 'Others', 'Days Ago'
    ]
    
    for col in required_columns:
        assert col in df.columns, f"Missing required column: {col}"
    
    # Check data types and ranges
    assert df['Sample Size'].dtype in ['int64', 'int32']
    assert df['Sample Size'].min() >= 100  # Reasonable sample size
    
    # Check new enhanced columns
    assert df['Methodology'].isin(['Online', 'Phone', 'Online/Phone']).all()
    assert df['Days Ago'].min() >= 0
    assert df['Margin of Error'].str.contains('±').all()
    
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

def test_enhanced_data_fields():
    """Test enhanced data fields are properly generated"""
    from app import create_sample_poll_data
    
    df = create_sample_poll_data()
    
    # Test enhanced fields
    assert 'Methodology' in df.columns
    assert 'Margin of Error' in df.columns
    assert 'Days Ago' in df.columns
    
    # Verify methodology values
    valid_methodologies = ['Online', 'Phone', 'Online/Phone']
    assert all(method in valid_methodologies for method in df['Methodology'].unique())
    
    # Verify margin of error format
    assert all(error.startswith('±') and error.endswith('%') for error in df['Margin of Error'])
    
    # Verify days ago is non-negative
    assert all(days >= 0 for days in df['Days Ago'])

def test_error_handling():
    """Test that error handling works properly"""
    from app import create_sample_poll_data
    import pandas as pd
    
    # This should not raise an exception even if something goes wrong
    df = create_sample_poll_data()
    
    # Should return a valid DataFrame even in error conditions
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0

if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
