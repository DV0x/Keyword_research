"""
Modular Keyword Research Dashboard
Main orchestrator that brings all components together
"""
import streamlit as st
import sys
from pathlib import Path

# Add project root to path for accessing campaigns/ directory
sys.path.append(str(Path(__file__).parent.parent))

# Import components
from components.sidebar import render_sidebar
from components.metrics import render_metrics_row

# Import pages
from pages import overview, actionable, clustering, data_table

# Page configuration
st.set_page_config(
    page_title="Keyword Campaign Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main dashboard application"""
    # Title
    st.title("🎯 Keyword Campaign Analytics Dashboard")
    st.markdown("Analyze keyword research data and get actionable insights for ad campaigns")
    
    # Render sidebar and get filtered data
    result = render_sidebar()
    
    if result[0] is None:
        st.error("No campaigns found. Please run keyword_research.py first.")
        st.stop()
    
    selected_campaign, campaign_data, filtered_df, data_source = result
    
    # Display metrics
    st.markdown("---")
    render_metrics_row(filtered_df)
    st.markdown("---")
    
    # Create tabs based on available data
    tab_names = ["📊 Overview", "🎯 Actionable", "📋 Data Table"]
    tab_modules = [overview, actionable, data_table]
    
    # Add clustering tab
    tab_names.append("🧩 Clustering")
    tab_modules.append(clustering)
    
    # Create tabs
    tabs = st.tabs(tab_names)
    
    # Render each tab
    for tab, module, name in zip(tabs, tab_modules, tab_names):
        with tab:
            if "Overview" in name:
                module.render(filtered_df, campaign_data)
            elif "Actionable" in name:
                module.render(filtered_df, selected_campaign)
            elif "Data Table" in name:
                module.render(filtered_df, selected_campaign)
            elif "Clustering" in name:
                module.render(filtered_df, selected_campaign)

if __name__ == "__main__":
    main()