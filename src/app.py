"""
UK Election Simulator - Main Application
Sprint 1: Basic poll data display with hardcoded sample data
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="UK Election Simulator",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for basic styling
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    color: #1f4e79;
    text-align: center;
    margin-bottom: 2rem;
}

.subheader {
    font-size: 1.5rem;
    color: #2c5f8a;
    margin-bottom: 1rem;
}

.poll-table {
    margin: 2rem 0;
}

.sidebar-content {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

def create_sample_poll_data():
    """Create sample polling data for initial display"""
    
    # Create sample polls with realistic UK political parties
    np.random.seed(42)  # For reproducible sample data
    
    pollsters = ["YouGov", "Opinium", "Survation", "Redfield & Wilton", "Deltapoll", "Ipsos", "BMG"]
    
    # Generate dates for the last 30 days
    end_date = datetime.now()
    dates = [end_date - timedelta(days=i) for i in range(0, 30, 3)]
    dates = sorted(dates)
    
    polls = []
    
    for date in dates:
        for pollster in np.random.choice(pollsters, size=np.random.randint(1, 4), replace=False):
            # Generate realistic polling numbers (roughly based on recent UK trends)
            base_con = np.random.normal(22, 3)
            base_lab = np.random.normal(44, 4)
            base_lib = np.random.normal(11, 2)
            base_ref = np.random.normal(15, 3)
            base_grn = np.random.normal(6, 2)
            base_snp = np.random.normal(3, 1)
            
            # Normalize to roughly 100%
            total = base_con + base_lab + base_lib + base_ref + base_grn + base_snp
            
            poll = {
                "Date": date.strftime("%Y-%m-%d"),
                "Pollster": pollster,
                "Sample Size": np.random.randint(800, 2500),
                "Conservative": max(1, round(base_con * 100 / total, 1)),
                "Labour": max(1, round(base_lab * 100 / total, 1)),
                "Liberal Democrat": max(1, round(base_lib * 100 / total, 1)),
                "Reform UK": max(1, round(base_ref * 100 / total, 1)),
                "Green": max(1, round(base_grn * 100 / total, 1)),
                "SNP": max(1, round(base_snp * 100 / total, 1)),
                "Others": max(1, round(2.0, 1))
            }
            polls.append(poll)
    
    return pd.DataFrame(polls).sort_values("Date", ascending=False).reset_index(drop=True)

def display_poll_summary(df):
    """Display summary statistics for the polls"""
    
    party_columns = ["Conservative", "Labour", "Liberal Democrat", "Reform UK", "Green", "SNP"]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Polls", len(df))
    
    with col2:
        st.metric("Pollsters", df['Pollster'].nunique())
    
    with col3:
        latest_date = df['Date'].max()
        st.metric("Latest Poll", latest_date)

def display_latest_averages(df):
    """Display latest polling averages"""
    
    party_columns = ["Conservative", "Labour", "Liberal Democrat", "Reform UK", "Green", "SNP"]
    
    # Calculate averages from the latest 7 polls
    latest_polls = df.head(7)
    averages = latest_polls[party_columns].mean().round(1)
    
    st.subheader("Latest Polling Average (Last 7 Polls)")
    
    # Create columns for party averages
    cols = st.columns(len(party_columns))
    
    party_colors = {
        "Conservative": "#0087DC",
        "Labour": "#E4003B", 
        "Liberal Democrat": "#FAA61A",
        "Reform UK": "#12B6CF",
        "Green": "#6AB023",
        "SNP": "#FDF23B"
    }
    
    for i, party in enumerate(party_columns):
        with cols[i]:
            st.metric(
                party,
                f"{averages[party]}%",
                help=f"Average from last 7 polls"
            )

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">🗳️ UK Election Simulator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Predict UK General Election outcomes with customizable parameters</p>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.sidebar.title("Settings")
    st.sidebar.markdown("**Sprint 1 - Basic Functionality**")
    st.sidebar.info("Currently displaying sample polling data. Real poll integration coming in Sprint 2.")
    
    # Poll display options
    st.sidebar.subheader("Display Options")
    show_sample_size = st.sidebar.checkbox("Show Sample Size", value=True)
    max_polls = st.sidebar.slider("Maximum Polls to Display", min_value=5, max_value=50, value=20)
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Main content
    try:
        # Load sample data
        with st.spinner("Loading polling data..."):
            poll_data = create_sample_poll_data()
        
        # Display summary metrics
        display_poll_summary(poll_data)
        
        st.markdown("---")
        
        # Display latest averages
        display_latest_averages(poll_data)
        
        st.markdown("---")
        
        # Display poll table
        st.markdown('<h2 class="subheader">Recent Polling Data</h2>', unsafe_allow_html=True)
        
        # Filter data based on user settings
        display_data = poll_data.head(max_polls).copy()
        
        if not show_sample_size:
            display_data = display_data.drop(columns=["Sample Size"])
        
        # Display the table
        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )
        
        # Basic chart
        st.subheader("Polling Trends")
        
        # Create a simple line chart of the main parties
        chart_data = poll_data.head(15)[["Date", "Conservative", "Labour", "Liberal Democrat", "Reform UK"]].copy()
        chart_data["Date"] = pd.to_datetime(chart_data["Date"])
        chart_data = chart_data.set_index("Date")
        
        st.line_chart(chart_data)
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please try refreshing the page.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; margin-top: 2rem;'>
            <p>UK Election Simulator v0.1.0 - Sprint 1<br>
            Built with Streamlit | <a href='https://github.com/data-john/Election-Models-UKGE' target='_blank'>Source Code</a></p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
