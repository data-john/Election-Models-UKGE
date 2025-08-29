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

# Enhanced CSS for improved styling and mobile responsiveness
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    color: #1f4e79;
    text-align: center;
    margin-bottom: 2rem;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
}

.subheader {
    font-size: 1.5rem;
    color: #2c5f8a;
    margin-bottom: 1rem;
    border-bottom: 2px solid #e6f2ff;
    padding-bottom: 0.5rem;
}

.poll-table {
    margin: 2rem 0;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.sidebar-content {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
    border: 1px solid #e6f2ff;
}

.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    border-radius: 8px;
    text-align: center;
    margin: 0.5rem 0;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.party-metric {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 6px;
    padding: 0.75rem;
    margin: 0.25rem;
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
}

.party-metric:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.12);
}

.error-message {
    background-color: #f8d7da;
    color: #721c24;
    padding: 1rem;
    border-radius: 6px;
    border: 1px solid #f5c6cb;
    margin: 1rem 0;
}

.success-message {
    background-color: #d4edda;
    color: #155724;
    padding: 1rem;
    border-radius: 6px;
    border: 1px solid #c3e6cb;
    margin: 1rem 0;
}

.info-box {
    background-color: #e7f3ff;
    border-left: 4px solid #0066cc;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 0 6px 6px 0;
}

.fade-in {
    animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
    0% { opacity: 0; transform: translateY(-10px); }
    100% { opacity: 1; transform: translateY(0); }
}

/* Enhanced button styling */
.stButton > button {
    background: linear-gradient(135deg, #0066cc, #004499);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: 500;
    transition: transform 0.2s, box-shadow 0.2s;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,102,204,0.3);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
    .main-header {
        font-size: 2rem;
        margin-bottom: 1rem;
    }

    .subheader {
        font-size: 1.2rem;
    }

    .metric-card, .party-metric {
        margin: 0.25rem 0;
        padding: 0.75rem;
    }
}

/* Polling table enhancements */
.poll-row-recent {
    background-color: #f0f8ff;
    border-left: 3px solid #0066cc;
}

.poll-row-old {
    opacity: 0.8;
}

/* Loading animation */
.loading-spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #0066cc;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
</style>
""", unsafe_allow_html=True)


def create_sample_poll_data():
    """Create enhanced sample polling data with additional metadata"""

    try:
        # Create sample polls with realistic UK political parties
        np.random.seed(42)  # For reproducible sample data

        pollsters = [
            {"name": "YouGov", "methodology": "Online", "typical_size": (1500, 2500)},
            {"name": "Opinium", "methodology": "Online", "typical_size": (1800, 2200)},
            {"name": "Survation", "methodology": "Online/Phone", "typical_size": (1000, 2000)},
            {"name": "Redfield & Wilton", "methodology": "Online", "typical_size": (1200, 1800)},
            {"name": "Deltapoll", "methodology": "Online", "typical_size": (1000, 1600)},
            {"name": "Ipsos", "methodology": "Phone", "typical_size": (800, 1200)},
            {"name": "BMG", "methodology": "Online", "typical_size": (1200, 1800)}
        ]

        # Generate dates for the last 45 days with more variation
        end_date = datetime.now()
        dates = []
        for i in range(45):
            # More realistic polling frequency - not every day
            if np.random.random() < 0.3:  # 30% chance of poll on any given day
                dates.append(end_date - timedelta(days=i))

        dates = sorted(dates, reverse=True)

        polls = []

        for date in dates:
            # 1-3 polls per polling day (realistic for UK)
            num_polls = np.random.choice([1, 2, 3], p=[0.6, 0.3, 0.1])
            selected_pollsters = np.random.choice(pollsters, size=num_polls, replace=False)

            for pollster in selected_pollsters:
                # Generate more realistic polling numbers with trends
                days_ago = (end_date - date).days
                trend_factor = 1 + (days_ago * 0.002)  # Slight trend over time

                # Base percentages with some variation
                base_con = np.random.normal(22 * trend_factor, 3)
                base_lab = np.random.normal(44 / trend_factor, 4)
                base_lib = np.random.normal(11, 2)
                base_ref = np.random.normal(15, 3)
                base_grn = np.random.normal(6, 2)
                base_snp = np.random.normal(3, 1)

                # Ensure positive values
                parties = [
                    max(1, val) for val in
                    [base_con, base_lab, base_lib, base_ref, base_grn, base_snp]
                ]

                # Add others and normalize to roughly 100%
                others = max(1, np.random.normal(2, 0.5))
                total = sum(parties) + others

                # Generate sample size based on pollster
                min_size, max_size = pollster["typical_size"]
                sample_size = np.random.randint(min_size, max_size)

                # Calculate margin of error
                margin_of_error = round(1.96 * np.sqrt(0.25 / sample_size) * 100, 1)

                poll = {
                    "Date": date.strftime("%Y-%m-%d"),
                    "Pollster": pollster["name"],
                    "Methodology": pollster["methodology"],
                    "Sample Size": sample_size,
                    "Margin of Error": f"±{margin_of_error}%",
                    "Conservative": round(parties[0] * 100 / total, 1),
                    "Labour": round(parties[1] * 100 / total, 1),
                    "Liberal Democrat": round(parties[2] * 100 / total, 1),
                    "Reform UK": round(parties[3] * 100 / total, 1),
                    "Green": round(parties[4] * 100 / total, 1),
                    "SNP": round(parties[5] * 100 / total, 1),
                    "Others": round(others * 100 / total, 1),
                    "Days Ago": days_ago
                }
                polls.append(poll)

        return pd.DataFrame(polls).sort_values("Date", ascending=False).reset_index(drop=True)

    except Exception as e:
        st.error(f"Error generating sample data: {str(e)}")
        # Return minimal fallback data
        return pd.DataFrame({
            "Date": [datetime.now().strftime("%Y-%m-%d")],
            "Pollster": ["Sample Data"],
            "Conservative": [25.0],
            "Labour": [40.0],
            "Liberal Democrat": [10.0],
            "Reform UK": [15.0],
            "Green": [6.0],
            "SNP": [3.0],
            "Others": [1.0]
        })


def display_poll_summary(df):
    """Display enhanced summary statistics for the polls"""

    try:
        if df.empty:
            st.warning("No polling data available to display summary.")
            return        # Enhanced metrics with better styling
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                f"""<div class="metric-card">
                    <h3>📊 Total Polls</h3>
                    <h2>{len(df)}</h2>
                </div>""",
                unsafe_allow_html=True
            )

        with col2:
            unique_pollsters = df['Pollster'].nunique()
            st.markdown(
                f"""<div class="metric-card">
                    <h3>🏢 Pollsters</h3>
                    <h2>{unique_pollsters}</h2>
                </div>""",
                unsafe_allow_html=True
            )

        with col3:
            latest_date = pd.to_datetime(df['Date']).max().strftime("%d %b")
            st.markdown(
                f"""<div class="metric-card">
                    <h3>📅 Latest Poll</h3>
                    <h2>{latest_date}</h2>
                </div>""",
                unsafe_allow_html=True
            )

        with col4:
            if 'Sample Size' in df.columns:
                avg_sample = int(df['Sample Size'].mean())
                st.markdown(
                    f"""<div class="metric-card">
                        <h3>👥 Avg Sample</h3>
                        <h2>{avg_sample:,}</h2>
                    </div>""",
                    unsafe_allow_html=True
                )

        # Additional summary info
        st.markdown("---")

        # Data freshness indicator
        latest_poll_age = (datetime.now() - pd.to_datetime(df['Date'].max())).days
        if latest_poll_age <= 3:
            freshness_color = "#28a745"
            freshness_text = "Very Fresh"
        elif latest_poll_age <= 7:
            freshness_color = "#ffc107"
            freshness_text = "Fresh"
        else:
            freshness_color = "#dc3545"
            freshness_text = "Stale"

        st.markdown(
            f"""<div class="info-box">
                <strong>Data Freshness:</strong>
                <span style="color: {freshness_color};">●</span>
                {freshness_text} (Latest poll: {latest_poll_age} days ago)
            </div>""",
            unsafe_allow_html=True
        )

    except Exception as e:
        st.error(f"Error displaying poll summary: {str(e)}")
        st.info("Please try refreshing the data or contact support if the issue persists.")


def display_latest_averages(df):
    """Display enhanced latest polling averages with confidence intervals"""

    try:
        if df.empty:
            st.warning("No polling data available for averages calculation.")
            return

        party_columns = ["Conservative", "Labour", "Liberal Democrat", "Reform UK", "Green", "SNP"]

        # Calculate averages from the latest polls (adaptive number based on data availability)
        num_recent_polls = min(10, len(df))
        latest_polls = df.head(num_recent_polls)

        if len(latest_polls) < 3:
            st.warning("Insufficient recent polls for reliable averages (need at least 3).")
            return

        averages = latest_polls[party_columns].mean().round(1)
        std_devs = latest_polls[party_columns].std().round(1)

        st.markdown('<h2 class="subheader">📊 Latest Polling Averages</h2>', unsafe_allow_html=True)

        # Info about the calculation
        date_range = f"{latest_polls['Date'].min()} to {latest_polls['Date'].max()}"
        st.markdown(
            f"""<div class="info-box">
                <strong>Based on {len(latest_polls)} most recent polls</strong><br>
                Period: {date_range}<br>
                Pollsters: {', '.join(latest_polls['Pollster'].unique()[:5])}
                {' + others' if latest_polls['Pollster'].nunique() > 5 else ''}
            </div>""",
            unsafe_allow_html=True
        )        # Create enhanced party metrics display
        cols = st.columns(3)  # 3 columns for better mobile layout

        party_colors = {
            "Conservative": "#0087DC",
            "Labour": "#E4003B",
            "Liberal Democrat": "#FAA61A",
            "Reform UK": "#12B6CF",
            "Green": "#6AB023",
            "SNP": "#FDF23B"
        }

        for i, party in enumerate(party_columns):
            col_index = i % 3
            with cols[col_index]:
                avg_val = averages[party]
                std_val = std_devs[party] if not pd.isna(std_devs[party]) else 0

                # Calculate confidence interval (rough estimate)
                margin = 1.96 * std_val / np.sqrt(len(latest_polls))
                lower_bound = max(0, avg_val - margin)
                upper_bound = avg_val + margin

                # Determine trend (simplified)
                if len(df) >= 20:
                    older_polls = df.iloc[10:20]
                    if not older_polls.empty:
                        older_avg = older_polls[party].mean()
                        if avg_val > older_avg + 0.5:
                            trend = "↗️"
                        elif avg_val < older_avg - 0.5:
                            trend = "↘️"
                        else:
                            trend = "→"
                    else:
                        trend = "→"
                else:
                    trend = "→"

                st.markdown(
                    f"""<div class="party-metric"
                             style="border-left: 4px solid {party_colors[party]};">
                        <strong>{party}</strong><br>
                        <span style="font-size: 1.5em; color: {party_colors[party]};">
                            {avg_val}% {trend}
                        </span><br>
                        <small style="color: #666;">
                            95% CI: {lower_bound:.1f}% - {upper_bound:.1f}%<br>
                            σ = {std_val:.1f}%
                        </small>
                    </div>""",
                    unsafe_allow_html=True
                )        # Show polling average chart
        st.markdown("### 📈 Polling Average Trend")

        # Create trend data for last 20 polls
        trend_data = df.head(20)[["Date"] + party_columns].copy()
        trend_data["Date"] = pd.to_datetime(trend_data["Date"])
        trend_data = trend_data.sort_values("Date")

        # Calculate rolling average
        for party in party_columns:
            trend_data[f"{party}_avg"] = (
                trend_data[party].rolling(window=3, min_periods=1).mean()
            )

        # Display chart
        chart_data = trend_data.set_index("Date")[
            [f"{party}_avg" for party in party_columns]
        ]
        chart_data.columns = party_columns  # Clean column names for chart

        st.line_chart(chart_data, height=400)

    except Exception as e:
        st.error(f"Error calculating polling averages: {str(e)}")
        st.info(
            "Unable to calculate averages. This might be due to insufficient or malformed data."
        )


def main():
    """Enhanced main application function with better error handling"""

    # Header with enhanced styling
    st.markdown('<h1 class="main-header">🗳️ UK Election Simulator</h1>', unsafe_allow_html=True)
    st.markdown(
        '''<p style="text-align: center; font-size: 1.2rem; color: #666;
        margin-bottom: 2rem;">
        Predict UK General Election outcomes with customizable parameters<br>
        <small style="color: #999;">
        Sprint 1: Production-Ready Sample Data Display with Bug Fixes
        </small>
        </p>''',
        unsafe_allow_html=True
    )

    # Enhanced sidebar with better organization
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.title("⚙️ Controls")

        # Sprint status
        st.markdown("### 🚀 Development Status")
        st.markdown("**Sprint 1, Day 5** - Bug Fixes & Enhanced Styling")
        st.info("Real poll integration coming in Sprint 2")

        # Enhanced display options
        st.markdown("### 📊 Display Options")

        # Data display controls
        col1, col2 = st.columns(2)
        with col1:
            show_sample_size = st.checkbox("Sample Size", value=True)
            show_methodology = st.checkbox("Methodology", value=False)
        with col2:
            show_margin_error = st.checkbox("Margin of Error", value=True)
            show_days_ago = st.checkbox("Days Ago", value=True)

        max_polls = st.slider(
            "Maximum Polls",
            min_value=5,
            max_value=50,
            value=25,
            help="Number of recent polls to display in the table"
        )

        # Filter options
        st.markdown("### 🔍 Filters")

        # Date range filter
        date_range = st.selectbox(
            "Time Period",
            ["Last 7 days", "Last 14 days", "Last 30 days", "All available"],
            index=2
        )

        # Pollster filter
        try:
            all_pollsters = ["All Pollsters"]  # Will be populated after data load
            selected_pollsters = st.multiselect(
                "Pollsters",
                all_pollsters,
                default=all_pollsters[:1]
            )
        except Exception:
            selected_pollsters = ["All Pollsters"]

        st.markdown('</div>', unsafe_allow_html=True)

        # Additional info
        with st.expander("ℹ️ About This Data"):
            st.markdown("""
            **Sample Data Information:**
            - Generated with realistic UK polling distributions
            - Based on major UK pollsters and methodologies
            - Includes margin of error calculations
            - Simulates natural polling variation

            **Note:** This is demonstration data for development purposes.
            Real polling data will be integrated in Sprint 2.
            """)

    # Main content with enhanced error handling
    try:
        # Load and process sample data
        with st.spinner("🔄 Loading enhanced polling data..."):
            poll_data = create_sample_poll_data()

        if poll_data.empty:
            st.error("No polling data could be generated. Please refresh the page.")
            return

        # Update pollster filter options
        if 'Pollster' in poll_data.columns:
            # Note: In a real app, we'd update the sidebar dynamically here
            pass

        # Apply filters
        filtered_data = poll_data.copy()

        # Date range filtering
        if date_range != "All available":
            days_map = {"Last 7 days": 7, "Last 14 days": 14, "Last 30 days": 30}
            days_limit = days_map[date_range]
            cutoff_date = datetime.now() - timedelta(days=days_limit)
            filtered_data = filtered_data[pd.to_datetime(filtered_data['Date']) >= cutoff_date]

        # Pollster filtering
        if selected_pollsters and "All Pollsters" not in selected_pollsters:
            filtered_data = filtered_data[filtered_data['Pollster'].isin(selected_pollsters)]

        if filtered_data.empty:
            st.warning("No polls match your current filters. Try adjusting your selection.")
            return

        # Success message for data load
        st.markdown(
            f'''<div class="success-message">
                ✅ Successfully loaded {len(filtered_data)} polls from
                {filtered_data['Pollster'].nunique()} pollsters
            </div>''',
            unsafe_allow_html=True
        )        # Display enhanced summary metrics
        display_poll_summary(filtered_data)

        st.markdown("---")

        # Display enhanced latest averages
        display_latest_averages(filtered_data)

        st.markdown("---")

        # Enhanced poll table display
        st.markdown('<h2 class="subheader">📋 Recent Polling Data</h2>', unsafe_allow_html=True)

        # Prepare display data based on user settings
        display_data = filtered_data.head(max_polls).copy()

        # Dynamic column selection based on user preferences
        columns_to_show = ["Date", "Pollster"]

        if show_methodology and "Methodology" in display_data.columns:
            columns_to_show.append("Methodology")
        if show_sample_size and "Sample Size" in display_data.columns:
            columns_to_show.append("Sample Size")
        if show_margin_error and "Margin of Error" in display_data.columns:
            columns_to_show.append("Margin of Error")
        if show_days_ago and "Days Ago" in display_data.columns:
            columns_to_show.append("Days Ago")

        # Add party columns
        party_columns = ["Conservative", "Labour", "Liberal Democrat",
                         "Reform UK", "Green", "SNP", "Others"]
        columns_to_show.extend([
            col for col in party_columns if col in display_data.columns
        ])

        # Filter columns
        display_data = display_data[columns_to_show]

        # Enhanced table display with styling
        st.dataframe(
            display_data,
            width='stretch',
            hide_index=True,
            height=400
        )

        # Data export option
        if st.button("📥 Download Data as CSV"):
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="💾 Save Polling Data",
                data=csv,
                file_name=f"uk_polls_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.markdown(
            f'''<div class="error-message">
                ❌ <strong>Application Error:</strong> {str(e)}<br>
                <small>If this error persists, please refresh the page or contact support.</small>
            </div>''',
            unsafe_allow_html=True
        )

        # Fallback display
        st.info("Attempting to load minimal data...")
        try:
            fallback_data = pd.DataFrame({
                "Date": [datetime.now().strftime("%Y-%m-%d")],
                "Pollster": ["Demo Data"],
                "Conservative": [25.0],
                "Labour": [40.0],
                "Liberal Democrat": [12.0],
                "Reform UK": [15.0],
                "Green": [6.0],
                "SNP": [2.0]
            })
            st.dataframe(fallback_data, width='stretch')
        except Exception as fallback_error:
            st.error("Unable to load any data. Please refresh the page.")
            st.error(f"Error details: {str(fallback_error)}")    # Additional analysis section
    with st.expander("📊 Advanced Analysis", expanded=False):
        try:
            st.markdown("### Poll Quality Metrics")

            col1, col2, col3 = st.columns(3)

            with col1:
                # Sample size analysis
                if 'Sample Size' in filtered_data.columns:
                    avg_sample = filtered_data['Sample Size'].mean()
                    if avg_sample > 1500:
                        sample_quality = "High"
                    elif avg_sample > 1000:
                        sample_quality = "Medium"
                    else:
                        sample_quality = "Low"
                    st.metric(
                        "Average Sample Size",
                        f"{avg_sample:.0f}",
                        help=f"Quality: {sample_quality}"
                    )

            with col2:
                # Pollster diversity
                pollster_count = filtered_data['Pollster'].nunique()
                if pollster_count >= 5:
                    diversity = "High"
                elif pollster_count >= 3:
                    diversity = "Medium"
                else:
                    diversity = "Low"
                st.metric(
                    "Pollster Diversity",
                    pollster_count,
                    help=f"Diversity: {diversity}"
                )

            with col3:
                # Data recency
                latest_poll_days = (
                    datetime.now() - pd.to_datetime(filtered_data['Date'].max())
                ).days
                if latest_poll_days <= 3:
                    recency = "Fresh"
                elif latest_poll_days <= 7:
                    recency = "Moderate"
                else:
                    recency = "Stale"
                st.metric(
                    "Data Freshness",
                    f"{latest_poll_days} days",
                    help=f"Status: {recency}"
                )

            # Pollster comparison
            if len(filtered_data) >= 5:
                st.markdown("### 🏢 Pollster Comparison")

                party_columns = [
                    "Conservative", "Labour", "Liberal Democrat",
                    "Reform UK", "Green", "SNP"
                ]
                pollster_avg = (
                    filtered_data.groupby('Pollster')[party_columns].mean().round(1)
                )

                if not pollster_avg.empty:
                    st.dataframe(pollster_avg, width='stretch')

                    # Show which pollster is most favorable to each party
                    st.markdown("**Most Favorable Pollsters:**")
                    for party in party_columns:
                        if party in pollster_avg.columns:
                            max_pollster = pollster_avg[party].idxmax()
                            max_value = pollster_avg[party].max()
                            st.markdown(
                                f"- **{party}**: {max_pollster} ({max_value}%)"
                            )
        except Exception as analysis_error:
            st.info("Advanced analysis unavailable with current data filters.")
            st.error(f"Analysis error: {str(analysis_error)}")

    # Enhanced footer with version info
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; color: #666; margin-top: 2rem; padding: 1rem;
                    background: #f8f9fa; border-radius: 8px;
                    border: 1px solid #e9ecef;'>
            <p><strong>UK Election Simulator v0.3.0 - Sprint 1, Day 5</strong><br>
            Production-Ready Bug Fixes & Enhanced Styling | Built with Streamlit<br>
            <a href='https://github.com/data-john/Election-Models-UKGE'
               target='_blank' style='color: #0066cc; text-decoration: none;'>
               📚 Source Code</a> |
            <a href='#' style='color: #0066cc; text-decoration: none;'>
               📖 Documentation</a><br>
            <small>Last updated: {datetime.now().strftime('%d %B %Y, %H:%M UTC')}</small>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
