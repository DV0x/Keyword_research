"""Overview tab with charts and visualizations"""
import streamlit as st
import pandas as pd
from components.visualizations import (
    create_opportunity_scatter,
    create_distribution_pie,
    create_difficulty_histogram
)

def render(df: pd.DataFrame, campaign_data: dict):
    """Render overview tab"""
    st.header("📊 Campaign Overview")
    
    if df.empty:
        st.warning("No data available with current filters")
        return
    
    # Find the keyword column (could have different names)
    keyword_col = None
    possible_keyword_cols = ['keyword', 'keywords', 'term', 'search_term', 'query']
    for col in possible_keyword_cols:
        if col in df.columns:
            keyword_col = col
            break
    
    # Row 1: Main charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Opportunity Map")
        fig = create_opportunity_scatter(df, keyword_col=keyword_col or 'keyword')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Keyword Distribution")
        if 'priority_tier' in df.columns:
            fig = create_distribution_pie(df, 'priority_tier', 'Priority Distribution')
        elif 'main_intent' in df.columns:
            fig = create_distribution_pie(df, 'main_intent', 'Intent Distribution')
        else:
            fig = None
        
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # Row 2: Additional charts
    col1, col2 = st.columns(2)
    
    with col1:
        if 'cpc' in df.columns:
            st.subheader("CPC Distribution")
            import plotly.express as px
            fig = px.histogram(
                df, x='cpc', nbins=30,
                title='Cost Per Click Distribution',
                labels={'cpc': 'CPC ($)', 'count': 'Keywords'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Competition Landscape")
        fig = create_difficulty_histogram(df)
        st.plotly_chart(fig, use_container_width=True)
    
    # Summary stats
    st.subheader("📈 Summary Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Volume Stats**")
        if 'search_volume' in df.columns:
            st.write(f"Total: {df['search_volume'].sum():,}")
            st.write(f"Average: {df['search_volume'].mean():,.0f}")
            st.write(f"Median: {df['search_volume'].median():,.0f}")
    
    with col2:
        st.markdown("**CPC Stats**")
        if 'cpc' in df.columns:
            st.write(f"Average: ${df['cpc'].mean():.2f}")
            st.write(f"Median: ${df['cpc'].median():.2f}")
            st.write(f"Range: ${df['cpc'].min():.2f} - ${df['cpc'].max():.2f}")
    
    with col3:
        st.markdown("**Difficulty Stats**")
        if 'keyword_difficulty' in df.columns:
            st.write(f"Average: {df['keyword_difficulty'].mean():.0f}")
            st.write(f"Easy (<30): {len(df[df['keyword_difficulty'] < 30])}")
            st.write(f"Hard (>70): {len(df[df['keyword_difficulty'] > 70])}")