#!/usr/bin/env python3
"""
Verification script for Issues I1 and I2 resolution
Sprint 2 Day 2: Issue Resolution Verification
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from polls import get_latest_polls_from_html, next_url, next_col_dict
from app import format_poll_data_for_display
import pandas as pd
from datetime import datetime

def verify_issue_1_date_parsing():
    """Verify that I1 (date parsing) has been resolved"""
    print("🔍 Verifying Issue I1 (Date Parsing) Resolution...")
    
    try:
        # Get real polling data
        raw_df = get_latest_polls_from_html(next_url, col_dict=next_col_dict, n=5)
        
        print(f"✅ Successfully fetched {len(raw_df)} polls from Wikipedia")
        
        # Check raw date format
        print("\n📅 Raw Wikipedia dates:")
        for i, date in enumerate(raw_df['Dates conducted'].head()):
            print(f"  {i+1}. {date}")
        
        # Format for display
        formatted_df = format_poll_data_for_display(raw_df)
        
        # Verify dates are properly parsed
        print("\n📅 Parsed dates and days ago:")
        for i, (date, days_ago, pollster) in enumerate(zip(
            formatted_df['Date'].head(),
            formatted_df['Days Ago'].head(),
            formatted_df['Pollster'].head()
        )):
            date_str = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
            print(f"  {i+1}. {date_str} ({days_ago} days ago) - {pollster}")
        
        # Verify dates are different (not all 2025-08-30)
        unique_dates = formatted_df['Date'].dt.strftime('%Y-%m-%d').unique()
        if len(unique_dates) > 1:
            print(f"\n✅ ISSUE I1 RESOLVED: Found {len(unique_dates)} unique dates")
            return True
        else:
            print(f"\n❌ ISSUE I1 NOT RESOLVED: Only found {len(unique_dates)} unique date")
            return False
            
    except Exception as e:
        print(f"\n❌ Error verifying Issue I1: {e}")
        return False

def verify_issue_2_streamlit_deprecation():
    """Verify that I2 (Streamlit deprecation) has been resolved"""
    print("\n🔍 Verifying Issue I2 (Streamlit Deprecation) Resolution...")
    
    try:
        # Read the app.py file and check for deprecated parameters
        with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'app.py'), 'r') as f:
            content = f.read()
        
        # Count occurrences of deprecated parameter
        use_container_width_count = content.count('use_container_width=True')
        width_none_count = content.count('width=None')
        
        print(f"📊 Code analysis:")
        print(f"  - Deprecated 'use_container_width=True': {use_container_width_count} occurrences")
        print(f"  - Updated 'width=None': {width_none_count} occurrences")
        
        if use_container_width_count == 0 and width_none_count > 0:
            print(f"\n✅ ISSUE I2 RESOLVED: No deprecated parameters found, {width_none_count} updated calls")
            return True
        else:
            print(f"\n❌ ISSUE I2 NOT RESOLVED: Still found {use_container_width_count} deprecated calls")
            return False
            
    except Exception as e:
        print(f"\n❌ Error verifying Issue I2: {e}")
        return False

def main():
    """Main verification function"""
    print("🚀 Election Models UKGE - Issue Resolution Verification")
    print("=" * 60)
    
    # Verify both issues
    issue1_resolved = verify_issue_1_date_parsing()
    issue2_resolved = verify_issue_2_streamlit_deprecation()
    
    print("\n" + "=" * 60)
    print("📋 VERIFICATION SUMMARY:")
    
    if issue1_resolved and issue2_resolved:
        print("✅ ALL ISSUES RESOLVED SUCCESSFULLY!")
        print("  • I1: Date parsing now works correctly with Wikipedia formats")
        print("  • I2: Streamlit deprecation warnings eliminated")
        return 0
    else:
        print("❌ SOME ISSUES REMAIN:")
        if not issue1_resolved:
            print("  • I1: Date parsing still needs attention")
        if not issue2_resolved:
            print("  • I2: Streamlit deprecation warnings still present")
        return 1

if __name__ == "__main__":
    exit(main())
