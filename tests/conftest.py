"""
Test configuration for the UK Election Simulator
"""

import pytest
import sys
import os

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def sample_poll_data():
    """Fixture providing sample poll data for testing"""
    import pandas as pd
    
    return pd.DataFrame({
        'Date': ['2025-08-28', '2025-08-27', '2025-08-26'],
        'Pollster': ['YouGov', 'Opinium', 'Survation'],
        'Sample Size': [1500, 1200, 1000],
        'Conservative': [22.0, 23.5, 21.8],
        'Labour': [44.0, 43.2, 45.1],
        'Liberal Democrat': [11.0, 10.8, 11.5],
        'Reform UK': [15.0, 14.9, 15.2],
        'Green': [6.0, 5.8, 6.2],
        'SNP': [3.0, 2.8, 3.1],
        'Others': [2.0, 2.0, 2.0]
    })
