#!/usr/bin/env python3
"""
Test script to isolate the Altair chart issue
"""
import sys
import os
sys.path.append('src')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import altair as alt

def test_chart_creation():
    """Test if the Altair chart can be created with sample data"""
    print("🧪 Testing Altair Chart Creation")
    
    # Create sample data similar to what the app uses
    dates = pd.date_range(end=datetime.now(), periods=17, freq='-2D')
    parties = ['Conservative', 'Labour', 'Liberal Democrat', 'Reform UK', 'Green', 'SNP']
    
    # Create sample trend data
    data = []
    for i, date in enumerate(dates):
        row = {'Date': date}
        for party in parties:
            # Generate realistic polling numbers
            base_support = {
                'Conservative': 25, 'Labour': 42, 'Liberal Democrat': 11,
                'Reform UK': 12, 'Green': 6, 'SNP': 3
            }
            # Add some variation
            variation = np.random.normal(0, 1.5)
            row[party] = max(0, base_support[party] + variation)
        data.append(row)
    
    df = pd.DataFrame(data)
    
    print(f"✅ Sample data created: {len(df)} rows, {len(df.columns)} columns")
    print(f"   Date range: {df['Date'].min()} to {df['Date'].max()}")
    
    # Create long format data for Altair
    chart_data_long = pd.melt(
        df,
        id_vars=['Date'],
        value_vars=parties,
        var_name='Party',
        value_name='Support'
    )
    
    print(f"✅ Long format data: {len(chart_data_long)} rows")
    
    # Define party colors
    party_colors = {
        "Conservative": "#0087DC",
        "Labour": "#E4003B", 
        "Liberal Democrat": "#FAA61A",
        "Reform UK": "#12B6CF",
        "Green": "#6AB023",
        "SNP": "#FDF23B"
    }
    
    # Test Altair chart creation
    try:
        color_scale = alt.Scale(
            domain=list(party_colors.keys()),
            range=list(party_colors.values())
        )
        
        party_selection = alt.selection_point(fields=['Party'])
        
        chart = alt.Chart(chart_data_long).mark_line(
            point=True,
            strokeWidth=3
        ).add_params(
            party_selection
        ).encode(
            x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%b %d')),
            y=alt.Y('Support:Q', title='Support %', scale=alt.Scale(domain=[0, 50])),
            color=alt.Color('Party:N', scale=color_scale, title='Party'),
            opacity=alt.condition(
                party_selection,
                alt.value(1.0),
                alt.value(0.7)
            ),
            tooltip=['Date:T', 'Party:N', alt.Tooltip('Support:Q', format='.1f')]
        ).properties(
            width=700,
            height=400,
            title='Polling Average Trend (3-poll rolling average)'
        ).interactive()
        
        # Try to convert to JSON (this is what Streamlit does internally)
        chart_json = chart.to_json()
        print(f"✅ Altair chart created successfully")
        print(f"   Chart JSON length: {len(chart_json)} characters")
        
        # Check if the chart has data
        if 'data' in chart_json:
            print("✅ Chart contains data")
        else:
            print("❌ Chart does not contain data")
            
        return True
        
    except Exception as e:
        print(f"❌ Altair chart creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_altair_version():
    """Check Altair version compatibility"""
    print(f"🔍 Altair version: {alt.__version__}")
    
    # Test if new API methods exist
    try:
        alt.selection_point
        print("✅ selection_point method available")
    except AttributeError:
        print("❌ selection_point method not available (old Altair version)")
        
    try:
        # Test a simple chart
        simple_data = pd.DataFrame({'x': [1, 2, 3], 'y': [1, 4, 2]})
        simple_chart = alt.Chart(simple_data).mark_line().encode(x='x', y='y')
        simple_chart.to_json()
        print("✅ Basic Altair functionality works")
        return True
    except Exception as e:
        print(f"❌ Basic Altair functionality failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Altair Chart Debugging")
    print("=" * 60)
    
    # Test Altair version and basic functionality
    altair_ok = test_altair_version()
    
    print()
    
    if altair_ok:
        # Test chart creation
        chart_ok = test_chart_creation()
        
        print("\n" + "=" * 60)
        if chart_ok:
            print("🎉 All tests passed - Chart should work in Streamlit")
        else:
            print("⚠️  Chart creation failed - there may be an issue")
    else:
        print("⚠️  Altair version issue detected")
    
    print("=" * 60)
