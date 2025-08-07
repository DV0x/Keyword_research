"""KPI metrics row component"""
import streamlit as st
import pandas as pd

def render_metrics_row(df: pd.DataFrame):
    """Render top-level KPI metrics"""
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Total Keywords", f"{len(df):,}")
    
    with col2:
        if 'keyword_difficulty' in df.columns:
            avg_diff = df['keyword_difficulty'].mean()
            st.metric("Avg Difficulty", f"{avg_diff:.0f}")
    
    with col3:
        if 'search_volume' in df.columns:
            total_vol = df['search_volume'].sum()
            st.metric("Total Volume", f"{total_vol:,}")
    
    with col4:
        if 'cpc' in df.columns:
            avg_cpc = df['cpc'].mean()
            st.metric("Avg CPC", f"${avg_cpc:.2f}")
    
    with col5:
        # Quick wins
        if 'keyword_difficulty' in df.columns and 'search_volume' in df.columns:
            quick_wins = df[
                (df['keyword_difficulty'] < 30) & 
                (df['search_volume'] > 500)
            ]
            st.metric("Quick Wins", len(quick_wins))
    
    with col6:
        # High value
        if 'cpc' in df.columns and 'search_volume' in df.columns:
            high_value = df[
                (df['cpc'] > df['cpc'].quantile(0.75)) &
                (df['search_volume'] > 100)
            ]
            st.metric("High Value", len(high_value))