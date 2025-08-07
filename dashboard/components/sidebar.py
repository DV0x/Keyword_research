"""Sidebar filters and controls"""
import streamlit as st
import pandas as pd
from typing import Tuple, Dict, Optional
from utils.data_loader import discover_campaigns, load_campaign_data

def render_sidebar() -> Tuple[str, Dict, pd.DataFrame, str]:
    """Render sidebar and return filtered data"""
    st.sidebar.header("🔍 Filters & Controls")
    
    # Campaign selector
    campaigns = discover_campaigns()
    if not campaigns:
        st.sidebar.error("No campaigns found!")
        return None, {}, pd.DataFrame(), "Campaign Keywords"
    
    selected_campaign = st.sidebar.selectbox(
        "Select Campaign",
        options=list(campaigns.keys()),
        help="Choose a campaign to analyze"
    )
    
    # Load campaign data
    campaign_data = load_campaign_data(campaigns[selected_campaign]['path'])
    
    if 'keywords' not in campaign_data:
        st.sidebar.error(f"No keyword data found for {selected_campaign}")
        return selected_campaign, campaign_data, pd.DataFrame(), "Campaign Keywords"
    
    # Data source selector
    st.sidebar.subheader("Data Source")
    data_source = st.sidebar.radio(
        "Select Data Source",
        options=["Campaign Keywords", "Competitor Analysis"],
        help="Choose between your campaign keywords or competitor discovered keywords"
    )
    
    # Load appropriate dataset
    if data_source == "Competitor Analysis" and 'competitor_keywords' in campaign_data:
        df = campaign_data['competitor_keywords'].copy()
        
        # Domain filter for competitor data
        if 'competitor_domain' in df.columns:
            unique_domains = df['competitor_domain'].dropna().unique()
            selected_domains = st.sidebar.multiselect(
                "Filter by Competitor Domain",
                options=sorted(unique_domains),
                default=None,
                help="Select specific competitor domains"
            )
            
            if selected_domains:
                df = df[df['competitor_domain'].isin(selected_domains)]
            
            # Show domain stats
            st.sidebar.markdown("**Top Domains:**")
            domain_counts = df['competitor_domain'].value_counts().head(5)
            for domain, count in domain_counts.items():
                st.sidebar.text(f"• {domain}: {count}")
    else:
        df = campaign_data['keywords'].copy()
    
    # Apply common filters
    st.sidebar.subheader("Filters")
    
    # Volume filter
    if 'search_volume' in df.columns:
        vol_min, vol_max = st.sidebar.slider(
            "Search Volume Range",
            min_value=50,
            max_value=50000,
            value=(50, 50000),
            step=50
        )
        df = df[(df['search_volume'] >= vol_min) & (df['search_volume'] <= vol_max)]
    
    # CPC filter
    if 'cpc' in df.columns:
        cpc_min, cpc_max = st.sidebar.slider(
            "CPC Range ($)",
            min_value=0.1,
            max_value=50.0,
            value=(0.1, 50.0),
            step=0.1
        )
        df = df[(df['cpc'] >= cpc_min) & (df['cpc'] <= cpc_max)]
    
    # Difficulty filter
    if 'keyword_difficulty' in df.columns:
        max_difficulty = st.sidebar.slider(
            "Maximum Difficulty",
            min_value=0,
            max_value=100,
            value=70
        )
        df = df[df['keyword_difficulty'] <= max_difficulty]
    
    # Intent filter
    if 'main_intent' in df.columns:
        intents = df['main_intent'].dropna().unique()
        selected_intents = st.sidebar.multiselect(
            "Search Intent",
            options=intents,
            default=intents.tolist()
        )
        df = df[df['main_intent'].isin(selected_intents)]
    
    # Reset button
    if st.sidebar.button("Reset Filters"):
        st.rerun()
    
    return selected_campaign, campaign_data, df, data_source