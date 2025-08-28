#!/usr/bin/env python3
"""
Sprint 1 Verification Script
Verifies that all Sprint 1, Day 1 deliverables are working correctly
"""

import sys
import os
import requests
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_app_imports():
    """Test that the main app can be imported successfully"""
    try:
        import app
        print("✅ App module imports successfully")
        
        # Test key functions exist
        assert hasattr(app, 'main'), "Missing main() function"
        assert hasattr(app, 'create_sample_poll_data'), "Missing create_sample_poll_data() function"
        print("✅ Key functions are available")
        
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

def test_sample_data_generation():
    """Test sample data generation"""
    try:
        import app
        df = app.create_sample_poll_data()
        
        assert len(df) > 0, "No data generated"
        assert 'Conservative' in df.columns, "Missing Conservative column"
        assert 'Labour' in df.columns, "Missing Labour column"
        assert df['Sample Size'].min() > 0, "Invalid sample sizes"
        
        print("✅ Sample data generation works correctly")
        print(f"   Generated {len(df)} poll records")
        print(f"   Covering {df['Pollster'].nunique()} pollsters")
        
        return True
    except Exception as e:
        print(f"❌ Sample data generation failed: {e}")
        return False

def check_file_structure():
    """Check that all required files exist"""
    required_files = [
        'src/app.py',
        'requirements.txt',
        'Dockerfile',
        'tests/conftest.py',
        'tests/test_basic_app.py',
        '.streamlit/config.toml',
        'README.md'
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            all_exist = False
    
    return all_exist

def main():
    """Main verification function"""
    print("🗳️  UK Election Simulator - Sprint 1, Day 1 Verification")
    print("=" * 60)
    
    # Test file structure
    print("\n📁 Checking file structure...")
    files_ok = check_file_structure()
    
    # Test imports
    print("\n📦 Testing imports...")
    imports_ok = test_app_imports()
    
    # Test data generation
    print("\n📊 Testing data generation...")
    data_ok = test_sample_data_generation()
    
    # Summary
    print("\n" + "=" * 60)
    if all([files_ok, imports_ok, data_ok]):
        print("🎉 ALL TESTS PASSED - Sprint 1, Day 1 Complete!")
        print("\nNext steps:")
        print("1. Run: streamlit run src/app.py")
        print("2. Visit: http://localhost:8501")
        print("3. Verify the UI works in your browser")
        return 0
    else:
        print("❌ Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
