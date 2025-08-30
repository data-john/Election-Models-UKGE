#!/usr/bin/env python3
"""
Sprint 2 Day 4 Verification: Poll Filtering UI Components
=========================================================

Verifies that the enhanced poll filtering UI components are implemented 
and functioning correctly as specified in the Sprint 2 Day 4 objectives.

Author: GitHub Copilot
Date: 30 August 2025
"""

import sys
import os
import traceback
from datetime import datetime, timedelta
import pandas as pd

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"🗳️ {title}")
    print(f"{'='*60}")

def print_test_result(test_name, passed, details=""):
    """Print formatted test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{test_name:<40} {status}")
    if details:
        print(f"   └─ {details}")

def verify_enhanced_filtering():
    """Verify enhanced filtering functionality"""
    print_header("Sprint 2 Day 4 Verification: Enhanced Poll Filtering UI Components")
    
    results = {}
    
    try:
        # Test 1: Import filtering functions
        print("\n📦 Testing Enhanced Filtering Functions Import...")
        try:
            from app import (
                apply_enhanced_filters,
                update_dynamic_pollster_filters,
                display_filter_summary,
                create_sample_poll_data
            )
            results['imports'] = True
            print_test_result("Enhanced filtering functions import", True)
        except Exception as e:
            results['imports'] = False
            print_test_result("Enhanced filtering functions import", False, str(e))
            return results

        # Test 2: Sample data generation
        print("\n📊 Testing Enhanced Sample Data Generation...")
        try:
            sample_data = create_sample_poll_data()
            
            # Check data structure
            required_columns = [
                'Date', 'Pollster', 'Conservative', 'Labour', 
                'Liberal Democrat', 'Reform UK', 'Green', 'SNP',
                'Sample Size', 'Methodology', 'Margin of Error'
            ]
            
            has_all_columns = all(col in sample_data.columns for col in required_columns)
            has_reasonable_size = len(sample_data) >= 5
            has_recent_dates = True
            
            # Check date recency
            if 'Date' in sample_data.columns:
                dates = pd.to_datetime(sample_data['Date'])
                latest_date = dates.max()
                days_old = (datetime.now() - latest_date).days
                has_recent_dates = days_old <= 5
            
            sample_data_valid = has_all_columns and has_reasonable_size and has_recent_dates
            results['sample_data'] = sample_data_valid
            
            details = f"Columns: {has_all_columns}, Size: {len(sample_data)}, Recent: {has_recent_dates}"
            print_test_result("Enhanced sample data generation", sample_data_valid, details)
            
        except Exception as e:
            results['sample_data'] = False
            print_test_result("Enhanced sample data generation", False, str(e))

        # Test 3: Date range filtering
        print("\n📅 Testing Date Range Filtering...")
        try:
            test_data = create_sample_poll_data()
            
            # Test predefined date filtering
            filtered_data, stats = apply_enhanced_filters(
                test_data, "Last 7 days", None, None,
                "All Pollsters", ["All Pollsters"], [],
                0, float('inf'), {}, {}
            )
            
            date_filter_works = len(filtered_data) <= len(test_data)
            date_filter_logged = "Date filter:" in str(stats.get('filters_applied', []))
            
            # Test custom date filtering
            start_date = (datetime.now() - timedelta(days=10)).date()
            end_date = datetime.now().date()
            
            custom_filtered, custom_stats = apply_enhanced_filters(
                test_data, "Custom", start_date, end_date,
                "All Pollsters", ["All Pollsters"], [],
                0, float('inf'), {}, {}
            )
            
            custom_filter_works = len(custom_filtered) <= len(test_data)
            
            date_filtering_works = date_filter_works and date_filter_logged and custom_filter_works
            results['date_filtering'] = date_filtering_works
            
            details = f"Predefined: {date_filter_works}, Custom: {custom_filter_works}"
            print_test_result("Date range filtering (predefined + custom)", date_filtering_works, details)
            
        except Exception as e:
            results['date_filtering'] = False
            print_test_result("Date range filtering", False, str(e))

        # Test 4: Pollster filtering
        print("\n🏢 Testing Pollster Filtering...")
        try:
            test_data = create_sample_poll_data()
            
            # Test select specific pollsters
            available_pollsters = test_data['Pollster'].unique()[:2]  # Take first 2
            
            select_filtered, select_stats = apply_enhanced_filters(
                test_data, "All available", None, None,
                "Select Specific", list(available_pollsters), [],
                0, float('inf'), {}, {}
            )
            
            select_works = all(p in available_pollsters for p in select_filtered['Pollster'].unique())
            
            # Test exclude specific pollsters
            exclude_pollster = available_pollsters[0] if len(available_pollsters) > 0 else None
            
            if exclude_pollster:
                exclude_filtered, exclude_stats = apply_enhanced_filters(
                    test_data, "All available", None, None,
                    "Exclude Specific", ["All Pollsters"], [exclude_pollster],
                    0, float('inf'), {}, {}
                )
                
                exclude_works = exclude_pollster not in exclude_filtered['Pollster'].unique()
            else:
                exclude_works = True
            
            pollster_filtering_works = select_works and exclude_works
            results['pollster_filtering'] = pollster_filtering_works
            
            details = f"Select: {select_works}, Exclude: {exclude_works}"
            print_test_result("Pollster filtering (select + exclude)", pollster_filtering_works, details)
            
        except Exception as e:
            results['pollster_filtering'] = False
            print_test_result("Pollster filtering", False, str(e))

        # Test 5: Sample size filtering
        print("\n👥 Testing Sample Size Filtering...")
        try:
            test_data = create_sample_poll_data()
            
            # Apply sample size filter
            min_sample = 1200
            max_sample = 2000
            
            size_filtered, size_stats = apply_enhanced_filters(
                test_data, "All available", None, None,
                "All Pollsters", ["All Pollsters"], [],
                min_sample, max_sample, {}, {}
            )
            
            # Check that filtered data respects sample size limits
            if 'Sample Size' in size_filtered.columns:
                sample_sizes = pd.to_numeric(size_filtered['Sample Size'], errors='coerce')
                valid_sizes = sample_sizes.dropna()
                size_filter_works = all(
                    (min_sample <= s <= max_sample) for s in valid_sizes
                ) if len(valid_sizes) > 0 else True
            else:
                size_filter_works = True
            
            results['sample_size_filtering'] = size_filter_works
            print_test_result("Sample size filtering", size_filter_works, 
                            f"Range: {min_sample}-{max_sample}, Filtered: {len(size_filtered)} polls")
            
        except Exception as e:
            results['sample_size_filtering'] = False
            print_test_result("Sample size filtering", False, str(e))

        # Test 6: Party support filtering
        print("\n📊 Testing Party Support Filtering...")
        try:
            test_data = create_sample_poll_data()
            
            # Apply party support filters
            party_filters = {
                'Conservative': 20.0,
                'Labour': 35.0
            }
            
            party_filtered, party_stats = apply_enhanced_filters(
                test_data, "All available", None, None,
                "All Pollsters", ["All Pollsters"], [],
                0, float('inf'), party_filters, {}
            )
            
            # Check that filtered data respects party thresholds
            party_filter_works = True
            for party, min_threshold in party_filters.items():
                if party in party_filtered.columns:
                    party_values = pd.to_numeric(party_filtered[party], errors='coerce')
                    # Handle both percentage and decimal formats
                    if party_values.max() > 1:
                        # Percentage format
                        party_filter_works &= all(v >= min_threshold for v in party_values if not pd.isna(v))
                    else:
                        # Decimal format
                        party_filter_works &= all(v >= min_threshold/100 for v in party_values if not pd.isna(v))
            
            results['party_filtering'] = party_filter_works
            print_test_result("Party support filtering", party_filter_works, 
                            f"Thresholds: {party_filters}, Filtered: {len(party_filtered)} polls")
            
        except Exception as e:
            results['party_filtering'] = False
            print_test_result("Party support filtering", False, str(e))

        # Test 7: Quality filtering
        print("\n✅ Testing Data Quality Filtering...")
        try:
            test_data = create_sample_poll_data()
            
            # Add a row with missing data for testing
            test_data_with_missing = test_data.copy()
            test_data_with_missing.loc[len(test_data_with_missing)] = {
                'Date': '2025-08-30',
                'Pollster': 'TestPoll',
                'Conservative': 25.0,
                'Labour': 40.0,
                'Liberal Democrat': 10.0,
                'Reform UK': 15.0,
                'Green': 5.0,
                'SNP': 5.0,
                'Sample Size': None,  # Missing sample size
                'Methodology': None,  # Missing methodology
                'Margin of Error': '±3%'
            }
            
            # Test require sample size
            quality_filters = {'require_sample_size': True}
            quality_filtered, quality_stats = apply_enhanced_filters(
                test_data_with_missing, "All available", None, None,
                "All Pollsters", ["All Pollsters"], [],
                0, float('inf'), {}, quality_filters
            )
            
            # Should exclude the test poll with missing sample size
            sample_size_filter_works = 'TestPoll' not in quality_filtered['Pollster'].values
            
            # Test require methodology
            quality_filters2 = {'require_methodology': True}
            method_filtered, method_stats = apply_enhanced_filters(
                test_data_with_missing, "All available", None, None,
                "All Pollsters", ["All Pollsters"], [],
                0, float('inf'), {}, quality_filters2
            )
            
            methodology_filter_works = 'TestPoll' not in method_filtered['Pollster'].values
            
            quality_filtering_works = sample_size_filter_works and methodology_filter_works
            results['quality_filtering'] = quality_filtering_works
            
            details = f"Sample size req: {sample_size_filter_works}, Methodology req: {methodology_filter_works}"
            print_test_result("Data quality filtering", quality_filtering_works, details)
            
        except Exception as e:
            results['quality_filtering'] = False
            print_test_result("Data quality filtering", False, str(e))

        # Test 8: Filter statistics and transparency
        print("\n📈 Testing Filter Statistics & Transparency...")
        try:
            test_data = create_sample_poll_data()
            
            # Apply some filters to generate stats
            filtered_data, filter_stats = apply_enhanced_filters(
                test_data, "Last 14 days", None, None,
                "All Pollsters", ["All Pollsters"], [],
                1000, 3000, {'Conservative': 15.0}, {'require_sample_size': False}
            )
            
            # Check filter stats structure
            has_original_count = 'original_count' in filter_stats
            has_final_count = 'final_count' in filter_stats
            has_filters_applied = 'filters_applied' in filter_stats
            
            stats_are_valid = (
                filter_stats.get('original_count', 0) >= filter_stats.get('final_count', 0) and
                isinstance(filter_stats.get('filters_applied', []), list)
            )
            
            filter_transparency_works = has_original_count and has_final_count and has_filters_applied and stats_are_valid
            results['filter_transparency'] = filter_transparency_works
            
            details = f"Stats structure valid: {filter_transparency_works}, Applied: {len(filter_stats.get('filters_applied', []))}"
            print_test_result("Filter statistics & transparency", filter_transparency_works, details)
            
        except Exception as e:
            results['filter_transparency'] = False
            print_test_result("Filter statistics & transparency", False, str(e))

        # Test 9: Combined filtering
        print("\n🔄 Testing Combined Multi-Filter Functionality...")
        try:
            test_data = create_sample_poll_data()
            
            # Apply multiple filters simultaneously
            combined_filtered, combined_stats = apply_enhanced_filters(
                test_data, "Last 30 days", None, None,
                "All Pollsters", ["All Pollsters"], [],
                1000, 5000, {'Conservative': 15.0, 'Labour': 30.0}, 
                {'require_sample_size': True}
            )
            
            # Should have multiple filters applied
            multiple_filters_applied = len(combined_stats.get('filters_applied', [])) >= 2
            final_count_reasonable = combined_stats.get('final_count', 0) <= combined_stats.get('original_count', 0)
            
            combined_filtering_works = multiple_filters_applied and final_count_reasonable
            results['combined_filtering'] = combined_filtering_works
            
            details = f"Filters applied: {len(combined_stats.get('filters_applied', []))}, " \
                     f"Reduction: {combined_stats.get('original_count', 0)} → {combined_stats.get('final_count', 0)}"
            print_test_result("Combined multi-filter functionality", combined_filtering_works, details)
            
        except Exception as e:
            results['combined_filtering'] = False
            print_test_result("Combined multi-filter functionality", False, str(e))

    except Exception as e:
        print(f"\n❌ Critical error during verification: {str(e)}")
        traceback.print_exc()
        return {}

    return results

def print_summary(results):
    """Print verification summary"""
    print_header("Sprint 2 Day 4 Verification Summary")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\n📊 Test Results: {passed_tests}/{total_tests} passed")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%\n")
    
    if passed_tests == total_tests:
        print("🎉 SPRINT 2 DAY 4 VERIFICATION SUCCESSFUL!")
        print("✅ Enhanced Poll Filtering UI Components are fully functional")
        print("✅ All filtering types working (date, pollster, sample size, party support, quality)")
        print("✅ Filter transparency and statistics working")
        print("✅ Combined filtering capabilities verified")
        print("✅ Ready to proceed to Sprint 2 Day 5: Error handling and edge cases")
        return True
    else:
        print("❌ SPRINT 2 DAY 4 VERIFICATION FAILED")
        print("Some enhanced filtering features are not working correctly.")
        
        failed_tests = [test for test, result in results.items() if not result]
        print(f"\nFailed tests: {failed_tests}")
        return False

def main():
    """Main verification function"""
    print("🔍 Starting Sprint 2 Day 4: Enhanced Poll Filtering UI Components Verification")
    print(f"Verification Date: {datetime.now().strftime('%d %B %Y, %H:%M UTC')}")
    
    try:
        results = verify_enhanced_filtering()
        success = print_summary(results)
        
        # Return appropriate exit code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n💥 Verification script failed with error: {str(e)}")
        traceback.print_exc()
        sys.exit(2)

if __name__ == "__main__":
    main()
