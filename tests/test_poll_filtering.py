"""
Test Suite for Sprint 2 Day 4: Poll Filtering UI Components
Tests the enhanced poll filtering functionality and UI components
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import (
    apply_enhanced_filters,
    update_dynamic_pollster_filters,
    create_sample_poll_data,
    display_filter_summary
)


class TestEnhancedFiltering:
    """Test the enhanced poll filtering functionality"""

    @pytest.fixture
    def sample_poll_data(self):
        """Create sample poll data for testing"""
        return pd.DataFrame({
            'Date': [
                '2025-08-30', '2025-08-29', '2025-08-25', '2025-08-20', 
                '2025-08-15', '2025-08-10', '2025-08-05', '2025-07-30'
            ],
            'Pollster': [
                'YouGov', 'Opinium', 'YouGov', 'Survation', 
                'Ipsos', 'YouGov', 'BMG', 'Survation'
            ],
            'Conservative': [22.0, 24.0, 21.0, 25.0, 23.0, 20.0, 26.0, 28.0],
            'Labour': [42.0, 40.0, 44.0, 38.0, 41.0, 45.0, 37.0, 35.0],
            'Liberal Democrat': [12.0, 11.0, 13.0, 10.0, 12.0, 14.0, 9.0, 11.0],
            'Reform UK': [15.0, 16.0, 14.0, 17.0, 15.0, 13.0, 18.0, 16.0],
            'Green': [6.0, 6.0, 5.0, 7.0, 6.0, 5.0, 7.0, 6.0],
            'SNP': [3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 4.0],
            'Sample Size': [1500, 1800, 1600, 1200, 800, 1500, 1400, 1000],
            'Methodology': ['Online', 'Online', 'Online', 'Phone', 'Phone', 'Online', 'Online', 'Phone']
        })

    def test_date_range_filtering_predefined(self, sample_poll_data):
        """Test predefined date range filtering"""
        filtered_data, stats = apply_enhanced_filters(
            sample_poll_data, 
            "Last 7 days", None, None,
            "All Pollsters", ["All Pollsters"], [],
            0, float('inf'), {}, {}
        )
        
        # Should only include polls from last 7 days
        cutoff_date = datetime.now() - timedelta(days=7)
        expected_polls = sample_poll_data[
            pd.to_datetime(sample_poll_data['Date']) >= cutoff_date
        ]
        
        assert len(filtered_data) == len(expected_polls)
        assert "Date filter: Last 7 days" in stats['filters_applied']

    def test_date_range_filtering_custom(self, sample_poll_data):
        """Test custom date range filtering"""
        start_date = datetime(2025, 8, 15)
        end_date = datetime(2025, 8, 25)
        
        filtered_data, stats = apply_enhanced_filters(
            sample_poll_data,
            "Custom", start_date.date(), end_date.date(),
            "All Pollsters", ["All Pollsters"], [],
            0, float('inf'), {}, {}
        )
        
        # Should include polls within the custom range
        assert len(filtered_data) >= 1  # At least the polls in range
        custom_filter_applied = any(
            "Custom date range" in f for f in stats['filters_applied']
        )
        assert custom_filter_applied

    def test_pollster_filtering_select_specific(self, sample_poll_data):
        """Test selecting specific pollsters"""
        selected_pollsters = ['YouGov', 'Opinium']
        
        filtered_data, stats = apply_enhanced_filters(
            sample_poll_data,
            "All available", None, None,
            "Select Specific", selected_pollsters, [],
            0, float('inf'), {}, {}
        )
        
        # Should only include selected pollsters
        assert all(p in selected_pollsters for p in filtered_data['Pollster'].unique())
        assert "Selected pollsters: 2" in stats['filters_applied']

    def test_pollster_filtering_exclude_specific(self, sample_poll_data):
        """Test excluding specific pollsters"""
        excluded_pollsters = ['YouGov']
        
        filtered_data, stats = apply_enhanced_filters(
            sample_poll_data,
            "All available", None, None,
            "Exclude Specific", ["All Pollsters"], excluded_pollsters,
            0, float('inf'), {}, {}
        )
        
        # Should not include excluded pollsters
        assert 'YouGov' not in filtered_data['Pollster'].unique()
        assert "Excluded pollsters: 1" in stats['filters_applied']

    def test_sample_size_filtering(self, sample_poll_data):
        """Test sample size filtering"""
        min_sample = 1000
        max_sample = 1600
        
        filtered_data, stats = apply_enhanced_filters(
            sample_poll_data,
            "All available", None, None,
            "All Pollsters", ["All Pollsters"], [],
            min_sample, max_sample, {}, {}
        )
        
        # Should only include polls within sample size range
        sample_sizes = pd.to_numeric(filtered_data['Sample Size'], errors='coerce')
        assert all(min_sample <= s <= max_sample for s in sample_sizes if not pd.isna(s))
        
        sample_filter_applied = any(
            "Sample size:" in f for f in stats['filters_applied']
        )
        assert sample_filter_applied

    def test_party_support_filtering(self, sample_poll_data):
        """Test party support threshold filtering"""
        party_filters = {
            'Conservative': 25.0,  # Should exclude polls with Con < 25%
            'Labour': 40.0         # Should exclude polls with Lab < 40%
        }
        
        filtered_data, stats = apply_enhanced_filters(
            sample_poll_data,
            "All available", None, None,
            "All Pollsters", ["All Pollsters"], [],
            0, float('inf'), party_filters, {}
        )
        
        # Should only include polls meeting party thresholds
        for index, row in filtered_data.iterrows():
            assert row['Conservative'] >= 25.0
            assert row['Labour'] >= 40.0
        
        # Should have filter applied messages
        party_filter_applied = any(
            "Conservative >=" in f or "Labour >=" in f 
            for f in stats['filters_applied']
        )
        assert party_filter_applied

    def test_quality_filtering_sample_size_required(self, sample_poll_data):
        """Test quality filter requiring sample size data"""
        # Add a row with missing sample size
        test_data = sample_poll_data.copy()
        test_data.loc[len(test_data)] = {
            'Date': '2025-08-31',
            'Pollster': 'TestPoll',
            'Conservative': 25.0,
            'Labour': 40.0,
            'Liberal Democrat': 12.0,
            'Reform UK': 15.0,
            'Green': 6.0,
            'SNP': 2.0,
            'Sample Size': None,  # Missing sample size
            'Methodology': 'Online'
        }
        
        quality_filters = {'require_sample_size': True}
        
        filtered_data, stats = apply_enhanced_filters(
            test_data,
            "All available", None, None,
            "All Pollsters", ["All Pollsters"], [],
            0, float('inf'), {}, quality_filters
        )
        
        # Should exclude the poll with missing sample size
        assert 'TestPoll' not in filtered_data['Pollster'].values
        assert "Require sample size data" in stats['filters_applied']

    def test_quality_filtering_methodology_required(self, sample_poll_data):
        """Test quality filter requiring methodology data"""
        # Add a row with missing methodology
        test_data = sample_poll_data.copy()
        test_data.loc[len(test_data)] = {
            'Date': '2025-08-31',
            'Pollster': 'TestPoll',
            'Conservative': 25.0,
            'Labour': 40.0,
            'Liberal Democrat': 12.0,
            'Reform UK': 15.0,
            'Green': 6.0,
            'SNP': 2.0,
            'Sample Size': 1500,
            'Methodology': None  # Missing methodology
        }
        
        quality_filters = {'require_methodology': True}
        
        filtered_data, stats = apply_enhanced_filters(
            test_data,
            "All available", None, None,
            "All Pollsters", ["All Pollsters"], [],
            0, float('inf'), {}, quality_filters
        )
        
        # Should exclude the poll with missing methodology
        assert 'TestPoll' not in filtered_data['Pollster'].values
        assert "Require methodology data" in stats['filters_applied']

    def test_outlier_filtering(self, sample_poll_data):
        """Test statistical outlier filtering"""
        # Add an extreme outlier
        test_data = sample_poll_data.copy()
        test_data.loc[len(test_data)] = {
            'Date': '2025-08-31',
            'Pollster': 'OutlierPoll',
            'Conservative': 80.0,  # Extreme outlier
            'Labour': 5.0,         # Extreme outlier
            'Liberal Democrat': 12.0,
            'Reform UK': 2.0,
            'Green': 1.0,
            'SNP': 0.0,
            'Sample Size': 1500,
            'Methodology': 'Online'
        }
        
        quality_filters = {'exclude_outliers': True}
        
        filtered_data, stats = apply_enhanced_filters(
            test_data,
            "All available", None, None,
            "All Pollsters", ["All Pollsters"], [],
            0, float('inf'), {}, quality_filters
        )
        
        # Should exclude the outlier poll
        assert 'OutlierPoll' not in filtered_data['Pollster'].values
        
        # Should have outlier removal message
        outlier_filter_applied = any(
            "outliers" in f.lower() for f in stats['filters_applied']
        )
        assert outlier_filter_applied

    def test_combined_filtering(self, sample_poll_data):
        """Test multiple filters applied together"""
        filtered_data, stats = apply_enhanced_filters(
            sample_poll_data,
            "Last 14 days", None, None,
            "Select Specific", ["YouGov", "Opinium"], [],
            1000, 2000, {'Conservative': 20.0}, {'require_sample_size': True}
        )
        
        # Should have multiple filters applied
        assert len(stats['filters_applied']) >= 3
        assert stats['final_count'] <= stats['original_count']

    def test_filter_stats_structure(self, sample_poll_data):
        """Test that filter stats have correct structure"""
        filtered_data, stats = apply_enhanced_filters(
            sample_poll_data,
            "All available", None, None,
            "All Pollsters", ["All Pollsters"], [],
            0, float('inf'), {}, {}
        )
        
        assert 'original_count' in stats
        assert 'filters_applied' in stats
        assert 'final_count' in stats
        assert stats['original_count'] == len(sample_poll_data)
        assert stats['final_count'] == len(filtered_data)


class TestDynamicPollsterFilters:
    """Test dynamic pollster filter functionality"""

    @pytest.fixture
    def sample_poll_data(self):
        """Sample data with various pollsters"""
        return pd.DataFrame({
            'Pollster': ['YouGov', 'Opinium', 'YouGov', 'Survation', 'Ipsos'],
            'Conservative': [22.0, 24.0, 21.0, 25.0, 23.0],
            'Labour': [42.0, 40.0, 44.0, 38.0, 41.0]
        })

    def test_update_dynamic_filters_empty_data(self):
        """Test behavior with empty data"""
        empty_data = pd.DataFrame()
        selected, excluded = update_dynamic_pollster_filters(empty_data, "All Pollsters")
        
        assert selected == ["All Pollsters"]
        assert excluded == []

    def test_update_dynamic_filters_missing_pollster_column(self):
        """Test behavior when Pollster column is missing"""
        data_no_pollster = pd.DataFrame({'Conservative': [22.0], 'Labour': [42.0]})
        selected, excluded = update_dynamic_pollster_filters(data_no_pollster, "All Pollsters")
        
        assert selected == ["All Pollsters"]
        assert excluded == []


class TestSampleDataGeneration:
    """Test sample poll data generation"""

    def test_create_sample_poll_data_structure(self):
        """Test that sample data has correct structure"""
        sample_data = create_sample_poll_data()
        
        assert not sample_data.empty
        
        # Check required columns exist
        required_columns = [
            'Date', 'Pollster', 'Conservative', 'Labour',
            'Liberal Democrat', 'Reform UK', 'Green', 'SNP'
        ]
        for col in required_columns:
            assert col in sample_data.columns, f"Missing column: {col}"

    def test_create_sample_poll_data_content_quality(self):
        """Test sample data quality and realism"""
        sample_data = create_sample_poll_data()
        
        # Check party percentages are reasonable
        for party in ['Conservative', 'Labour', 'Liberal Democrat']:
            party_values = pd.to_numeric(sample_data[party], errors='coerce')
            assert party_values.min() >= 0, f"{party} has negative values"
            assert party_values.max() <= 100, f"{party} has values over 100%"

    def test_create_sample_poll_data_dates(self):
        """Test that sample data has reasonable dates"""
        sample_data = create_sample_poll_data()
        
        dates = pd.to_datetime(sample_data['Date'])
        
        # Should have recent dates
        latest_date = dates.max()
        earliest_date = dates.min()
        
        # Should be within last ~60 days (allow up to 5 days for test tolerance)
        assert (datetime.now() - latest_date).days <= 5
        assert (datetime.now() - earliest_date).days <= 60

    def test_create_sample_poll_data_pollsters(self):
        """Test that sample data has realistic pollsters"""
        sample_data = create_sample_poll_data()
        
        expected_pollsters = ['YouGov', 'Opinium', 'Survation', 'Redfield & Wilton', 'Deltapoll', 'Ipsos', 'BMG']
        actual_pollsters = sample_data['Pollster'].unique()
        
        # Should include some of the expected pollsters
        assert len(set(actual_pollsters) & set(expected_pollsters)) >= 3


class TestFilterIntegration:
    """Test integration of filtering components"""

    def test_filtering_preserves_data_types(self):
        """Test that filtering preserves correct data types"""
        sample_data = create_sample_poll_data()
        
        filtered_data, stats = apply_enhanced_filters(
            sample_data,
            "Last 30 days", None, None,
            "All Pollsters", ["All Pollsters"], [],
            0, float('inf'), {}, {}
        )
        
        # Check that numeric columns remain numeric
        numeric_columns = ['Conservative', 'Labour', 'Liberal Democrat']
        for col in numeric_columns:
            if col in filtered_data.columns:
                assert pd.api.types.is_numeric_dtype(filtered_data[col])

    def test_filtering_edge_cases(self):
        """Test filtering with edge cases"""
        # Create data with edge cases
        edge_case_data = pd.DataFrame({
            'Date': ['2025-08-30', '2025-08-29'],
            'Pollster': ['Test1', 'Test2'],
            'Conservative': [0.0, 100.0],  # Edge values
            'Labour': [50.0, 0.0],
            'Liberal Democrat': [25.0, 0.0],
            'Reform UK': [25.0, 0.0],
            'Green': [0.0, 0.0],
            'SNP': [0.0, 0.0],
            'Sample Size': [1, 50000]  # Edge sample sizes
        })
        
        # Should handle edge cases without crashing
        filtered_data, stats = apply_enhanced_filters(
            edge_case_data,
            "All available", None, None,
            "All Pollsters", ["All Pollsters"], [],
            0, float('inf'), {}, {}
        )
        
        assert len(filtered_data) == len(edge_case_data)  # No filters applied
        assert stats['final_count'] == stats['original_count']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
