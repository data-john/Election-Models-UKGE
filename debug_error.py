#!/usr/bin/env python3
"""
Debug script to isolate the string to integer conversion error
"""

import sys
import os
import traceback
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from app import load_real_polling_data, format_poll_data_for_display, display_poll_summary
    from polls import get_wiki_polls_table
    print("✅ Successfully imported modules")
except Exception as e:
    print(f"❌ Import error: {e}")
    traceback.print_exc()
    sys.exit(1)

def debug_data_pipeline():
    """Debug the data processing pipeline step by step"""
    
    print("\n🔍 Step 1: Loading raw Wikipedia data...")
    try:
        url = "https://en.wikipedia.org/wiki/Opinion_polling_for_the_next_United_Kingdom_general_election"
        raw_data = get_wiki_polls_table(url)
        print(f"✅ Raw data loaded: {len(raw_data)} rows")
        print(f"Raw columns: {list(raw_data.columns)}")
        print(f"Raw data types:\n{raw_data.dtypes}")
        
        # Check sample size column specifically
        if 'Sample size' in raw_data.columns:
            sample_col = raw_data['Sample size']
            print(f"\nSample size values: {sample_col.iloc[:, 0].head().tolist()}")
            print(f"Sample size data type: {sample_col.iloc[:, 0].dtype}")
        
        # Print raw data structure
        print(f"\nRaw data shape: {raw_data.shape}")
        print(f"Raw data sample:")
        # Handle multi-level columns
        for i, (col_name, _) in enumerate(raw_data.columns[:5]):  # First 5 columns
            print(f"{col_name}: {raw_data.iloc[0, i]}")
            
        print(f"\nFirst few rows of raw data (shape):")
        print(f"Data shape: {raw_data.shape}")
        
    except Exception as e:
        print(f"❌ Error loading raw data: {e}")
        traceback.print_exc()
        return
    
    print("\n🔍 Step 2: Formatting data for display...")
    try:
        formatted_data = format_poll_data_for_display(raw_data.copy())
        print(f"✅ Formatted data: {len(formatted_data)} rows")
        print(f"Formatted columns: {list(formatted_data.columns)}")
        print(f"Formatted data types:\n{formatted_data.dtypes}")
        
        # Check specific problematic columns
        for col in ['Sample Size', 'Days Ago']:
            if col in formatted_data.columns:
                print(f"\n{col} values: {formatted_data[col].head().tolist()}")
                print(f"{col} data type: {formatted_data[col].dtype}")
                
                # Try to identify problematic values
                try:
                    numeric_col = pd.to_numeric(formatted_data[col], errors='coerce')
                    nan_count = numeric_col.isna().sum()
                    if nan_count > 0:
                        print(f"⚠️  {col} has {nan_count} non-numeric values:")
                        non_numeric = formatted_data[formatted_data[col].isna() | (pd.to_numeric(formatted_data[col], errors='coerce').isna())][col]
                        print(non_numeric.tolist()[:5])  # Show first 5 problematic values
                except Exception as inner_e:
                    print(f"❌ Error checking {col}: {inner_e}")
        
        print(f"\nFirst few rows of formatted data:")
        print(formatted_data.head())
        
    except Exception as e:
        print(f"❌ Error formatting data: {e}")
        traceback.print_exc()
        return
    
    print("\n🔍 Step 3: Testing display function...")
    try:
        # Create a mock streamlit environment
        class MockStreamlit:
            def error(self, msg):
                print(f"STREAMLIT ERROR: {msg}")
            def warning(self, msg):
                print(f"STREAMLIT WARNING: {msg}")
            def dataframe(self, *args, **kwargs):
                print(f"STREAMLIT DATAFRAME: {args[0].shape if args else 'No data'}")
        
        # Temporarily replace streamlit import
        import sys
        sys.modules['streamlit'] = MockStreamlit()
        
        # Try the display function with a small subset
        test_data = formatted_data.head(3).copy()
        print(f"Testing with {len(test_data)} rows")
        
        # This should trigger the error if it exists
        display_poll_summary(test_data)
        
        print("✅ Display function completed without errors")
        
    except Exception as e:
        print(f"❌ Error in display function: {e}")
        traceback.print_exc()
        
        # Print more detailed error information
        print(f"\nError type: {type(e)}")
        print(f"Error args: {e.args}")
        
        # Try to identify which line caused the issue
        tb = traceback.extract_tb(e.__traceback__)
        for frame in tb:
            if 'app.py' in frame.filename:
                print(f"Error in app.py at line {frame.lineno}: {frame.line}")

if __name__ == "__main__":
    print("🔬 Debugging Election Models Data Pipeline")
    print("=" * 50)
    debug_data_pipeline()
    print("\n🔬 Debug complete")
