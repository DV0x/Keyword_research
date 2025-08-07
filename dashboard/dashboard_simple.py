"""
Simplified Dashboard with Robust Error Handling
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root to path for accessing campaigns/ directory
sys.path.append(str(Path(__file__).parent.parent))

# Page configuration
st.set_page_config(
    page_title="Keyword Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_data():
    """Load campaign data with error handling"""
    try:
        from utils.data_loader import discover_campaigns, load_campaign_data
        
        campaigns = discover_campaigns()
        if not campaigns:
            st.error("No campaigns found. Please run keyword_research.py first.")
            return None, None, None
        
        selected_campaign = st.sidebar.selectbox(
            "Select Campaign",
            options=list(campaigns.keys()),
            help="Choose a campaign to analyze"
        )
        
        campaign_data = load_campaign_data(campaigns[selected_campaign]['path'])
        
        if 'keywords' not in campaign_data:
            st.error(f"No keyword data found for {selected_campaign}")
            return selected_campaign, None, None
        
        df = campaign_data['keywords'].copy()
        
        # Basic filtering
        if 'search_volume' in df.columns:
            vol_min, vol_max = st.sidebar.slider(
                "Search Volume Range",
                min_value=int(df['search_volume'].min()),
                max_value=int(df['search_volume'].max()),
                value=(100, 10000)
            )
            df = df[(df['search_volume'] >= vol_min) & (df['search_volume'] <= vol_max)]
        
        return selected_campaign, campaign_data, df
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None

def render_overview_tab(df):
    """Simple overview tab"""
    st.header("📊 Overview")
    
    if df is None or df.empty:
        st.warning("No data available")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Keywords", len(df))
    
    with col2:
        if 'search_volume' in df.columns:
            st.metric("Total Volume", f"{df['search_volume'].sum():,}")
    
    with col3:
        if 'cpc' in df.columns:
            st.metric("Avg CPC", f"${df['cpc'].mean():.2f}")
    
    # Simple table
    st.subheader("Top Keywords")
    
    # Find keyword column
    keyword_col = None
    for col in ['keyword', 'keywords', 'term', 'search_term', 'query']:
        if col in df.columns:
            keyword_col = col
            break
    
    if keyword_col:
        display_cols = [keyword_col]
        if 'search_volume' in df.columns:
            display_cols.append('search_volume')
        if 'cpc' in df.columns:
            display_cols.append('cpc')
        if 'keyword_difficulty' in df.columns:
            display_cols.append('keyword_difficulty')
        
        top_keywords = df.nlargest(20, 'search_volume' if 'search_volume' in df.columns else keyword_col)
        st.dataframe(
            top_keywords[display_cols],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No keyword column found")

def render_clustering_tab(df, campaign_name):
    """Simple clustering tab"""
    st.header("🧩 Clustering")
    
    if df is None or df.empty:
        st.warning("No data available")
        return
    
    # Find keyword column
    keyword_col = None
    for col in ['keyword', 'keywords', 'term', 'search_term', 'query']:
        if col in df.columns:
            keyword_col = col
            break
    
    if keyword_col is None:
        st.warning(f"No keyword column found. Available: {list(df.columns)}")
        return
    
    if len(df) < 5:
        st.warning("Need at least 5 keywords for clustering")
        return
    
    try:
        from utils.clustering_engine import (
            prepare_text_features, calculate_similarity_matrix,
            perform_kmeans_clustering, get_cluster_summaries
        )
        
        # Clustering controls
        n_clusters = st.slider(
            "Number of Clusters",
            min_value=2,
            max_value=min(10, len(df) // 2),
            value=min(5, len(df) // 5)
        )
        
        with st.spinner("Clustering keywords..."):
            # Limit data size for performance
            work_df = df.head(50).copy().reset_index(drop=True)
            
            # Perform clustering
            tfidf_matrix, vectorizer = prepare_text_features(work_df[keyword_col])
            clusters = perform_kmeans_clustering(tfidf_matrix, n_clusters)
            work_df['cluster'] = clusters
            
            # Show results
            st.success(f"Created {len(set(clusters))} clusters from {len(work_df)} keywords")
            
            # Cluster summaries
            summaries = get_cluster_summaries(work_df, keyword_col)
            st.dataframe(summaries, use_container_width=True)
            
            # Keywords by cluster
            for cluster_id in sorted(work_df['cluster'].unique()):
                cluster_df = work_df[work_df['cluster'] == cluster_id]
                cluster_name = f"Cluster {cluster_id}"
                
                if cluster_id in summaries.index and 'Cluster Name' in summaries.columns:
                    cluster_name = summaries.loc[cluster_id, 'Cluster Name']
                
                with st.expander(f"📁 {cluster_name} ({len(cluster_df)} keywords)"):
                    display_cols = [keyword_col]
                    if 'search_volume' in cluster_df.columns:
                        display_cols.append('search_volume')
                    if 'cpc' in cluster_df.columns:
                        display_cols.append('cpc')
                    
                    st.dataframe(
                        cluster_df[display_cols].head(10),
                        use_container_width=True,
                        hide_index=True
                    )
    
    except Exception as e:
        st.error(f"Clustering failed: {e}")
        st.exception(e)

def main():
    """Main application"""
    st.title("🎯 Keyword Research Dashboard")
    st.markdown("Simplified dashboard for keyword analysis")
    
    # Load data
    selected_campaign, campaign_data, df = load_data()
    
    if df is None:
        st.stop()
    
    # Show data info
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Data Info:**")
    st.sidebar.write(f"Campaign: {selected_campaign}")
    st.sidebar.write(f"Keywords: {len(df):,}")
    st.sidebar.write(f"Columns: {len(df.columns)}")
    
    # Tabs
    tab1, tab2 = st.tabs(["📊 Overview", "🧩 Clustering"])
    
    with tab1:
        render_overview_tab(df)
    
    with tab2:
        render_clustering_tab(df, selected_campaign)

if __name__ == "__main__":
    main()