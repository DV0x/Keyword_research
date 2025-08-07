"""Keyword clustering visualization and analysis"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
from utils.clustering_engine import (
    prepare_text_features,
    calculate_similarity_matrix,
    perform_kmeans_clustering,
    create_cluster_network,
    get_cluster_summaries,
    reduce_dimensions_for_viz
)

def render(df: pd.DataFrame, campaign_name: str):
    """Render clustering analysis tab"""
    st.header("🎯 Keyword Clustering Analysis")
    
    if df.empty:
        st.warning("No data available for clustering")
        return
    
    # Find the keyword column (could have different names)
    keyword_col = None
    possible_keyword_cols = ['keyword', 'keywords', 'term', 'search_term', 'query']
    for col in possible_keyword_cols:
        if col in df.columns:
            keyword_col = col
            break
    
    if keyword_col is None:
        st.warning(f"No keyword column found. Available columns: {df.columns.tolist()}")
        st.info("Expected one of: keyword, keywords, term, search_term, query")
        return
    
    # Show data info
    st.info(f"Using column '{keyword_col}' for clustering ({len(df)} keywords)")
    
    # Check minimum data requirements
    if len(df) < 5:
        st.warning("Need at least 5 keywords for meaningful clustering analysis")
        return
    
    # Clustering controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        clustering_method = st.selectbox(
            "Clustering Method",
            options=["K-Means", "Hierarchical", "Semantic"],
            help="Choose clustering algorithm"
        )
    
    with col2:
        # Calculate valid range for clusters
        max_clusters = max(3, min(20, len(df) // 5)) if len(df) > 15 else 3
        default_clusters = max(3, min(10, len(df) // 10)) if len(df) > 30 else 3
        
        n_clusters = st.slider(
            "Number of Clusters",
            min_value=2,
            max_value=max_clusters,
            value=default_clusters,
            help="Adjust number of keyword groups"
        )
    
    with col3:
        viz_type = st.selectbox(
            "Visualization Type",
            options=["Network Graph", "Scatter Plot", "Dendrogram", "Bubble Chart"],
            help="Choose how to visualize clusters"
        )
    
    # Perform clustering
    with st.spinner("Clustering keywords..."):
        # Reset index to ensure proper alignment
        df_work = df.copy().reset_index(drop=True)
        
        # Prepare features using dynamic keyword column
        tfidf_matrix, vectorizer = prepare_text_features(df_work[keyword_col])
        similarity_matrix = calculate_similarity_matrix(tfidf_matrix)
        
        # Perform clustering
        if clustering_method == "K-Means":
            clusters = perform_kmeans_clustering(tfidf_matrix, n_clusters)
        else:
            clusters = perform_kmeans_clustering(tfidf_matrix, n_clusters)  # Default to K-means for now
        
        df_work['cluster'] = clusters
        
        # Get cluster summaries
        cluster_summaries = get_cluster_summaries(df_work, keyword_col)
    
    # Display visualizations
    st.subheader(f"📊 {viz_type}")
    
    if viz_type == "Network Graph":
        fig = create_network_visualization(df_work, similarity_matrix, keyword_col)
        st.plotly_chart(fig, use_container_width=True)
    
    elif viz_type == "Scatter Plot":
        fig = create_scatter_visualization(df_work, tfidf_matrix, keyword_col)
        st.plotly_chart(fig, use_container_width=True)
    
    elif viz_type == "Bubble Chart":
        fig = create_bubble_visualization(cluster_summaries)
        st.plotly_chart(fig, use_container_width=True)
    
    else:  # Dendrogram
        st.info("Dendrogram visualization coming soon")
    
    # Cluster details
    st.subheader("📋 Cluster Details")
    
    # Summary table
    st.dataframe(
        cluster_summaries,
        use_container_width=True,
        column_config={
            "Total Volume": st.column_config.NumberColumn(format="%d"),
            "Avg Volume": st.column_config.NumberColumn(format="%.0f"),
            "Avg CPC": st.column_config.NumberColumn(format="$%.2f"),
            "Avg Difficulty": st.column_config.NumberColumn(format="%.1f")
        }
    )
    
    # Expandable cluster details
    st.subheader("🔍 Keywords by Cluster")
    
    for cluster_id in sorted(df_work['cluster'].unique()):
        cluster_df = df_work[df_work['cluster'] == cluster_id]
        cluster_name = cluster_summaries.loc[cluster_id, 'Cluster Name'] if cluster_id in cluster_summaries.index else f"Cluster {cluster_id}"
        
        with st.expander(f"📁 {cluster_name} ({len(cluster_df)} keywords)"):
            # Top keywords in cluster
            display_cols = [keyword_col]
            if 'search_volume' in cluster_df.columns:
                display_cols.append('search_volume')
            if 'cpc' in cluster_df.columns:
                display_cols.append('cpc')
            if 'keyword_difficulty' in cluster_df.columns:
                display_cols.append('keyword_difficulty')
            
            sort_col = 'search_volume' if 'search_volume' in cluster_df.columns else display_cols[0]
            display_df = cluster_df.nlargest(10, sort_col)[display_cols].copy()
            
            # Rename columns for display
            col_names = ['Keyword']
            if 'search_volume' in display_cols:
                col_names.append('Volume')
            if 'cpc' in display_cols:
                col_names.append('CPC ($)')
            if 'keyword_difficulty' in display_cols:
                col_names.append('Difficulty')
            
            display_df.columns = col_names[:len(display_df.columns)]
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("**Cluster Stats:**")
                if 'search_volume' in cluster_df.columns:
                    st.write(f"Total Volume: {cluster_df['search_volume'].sum():,}")
                if 'cpc' in cluster_df.columns:
                    st.write(f"Avg CPC: ${cluster_df['cpc'].mean():.2f}")
                if 'keyword_difficulty' in cluster_df.columns:
                    st.write(f"Avg Difficulty: {cluster_df['keyword_difficulty'].mean():.0f}")
                
                # Export cluster
                csv = cluster_df.to_csv(index=False)
                st.download_button(
                    f"📥 Export Cluster",
                    csv,
                    f"{campaign_name}_cluster_{cluster_id}.csv",
                    "text/csv"
                )
    
    # Export all clusters
    st.subheader("📥 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Export with clusters
        export_df = df_work.copy()
        export_df['cluster_name'] = export_df['cluster'].map(
            lambda x: cluster_summaries.loc[x, 'Cluster Name'] if x in cluster_summaries.index else f"Cluster {x}"
        )
        csv = export_df.to_csv(index=False)
        st.download_button(
            "📊 Export All with Clusters",
            csv,
            f"{campaign_name}_clustered_keywords.csv",
            "text/csv"
        )
    
    with col2:
        # Export for Google Ads
        from utils.export_utils import export_to_google_ads
        google_df = export_to_google_ads(export_df, campaign_name, keyword_col=keyword_col)
        csv = google_df.to_csv(index=False)
        st.download_button(
            "🔍 Google Ads Format",
            csv,
            f"{campaign_name}_google_ads_clusters.csv",
            "text/csv"
        )
    
    with col3:
        # Export cluster summary
        csv = cluster_summaries.to_csv()
        st.download_button(
            "📈 Cluster Summary",
            csv,
            f"{campaign_name}_cluster_summary.csv",
            "text/csv"
        )

def create_network_visualization(df: pd.DataFrame, similarity_matrix, keyword_col: str = 'keyword') -> go.Figure:
    """Create interactive network graph visualization"""
    # Create network
    G = create_cluster_network(df, similarity_matrix, threshold=0.3, keyword_col=keyword_col)
    
    # Handle empty graph
    if len(G.nodes()) == 0:
        fig = go.Figure()
        fig.update_layout(
            title="No network connections found (try lowering similarity threshold)",
            height=400,
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        return fig
    
    # Get layout
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    
    # Extract node positions
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_size = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_data = G.nodes[node]
        
        # Safely access node attributes with defaults
        keyword = node_data.get('keyword', f'Node {node}')
        volume = node_data.get('volume', 0)
        cpc = node_data.get('cpc', 0.0)
        cluster = node_data.get('cluster', 0)
        
        node_text.append(
            f"{keyword}<br>"
            f"Volume: {volume:,}<br>"
            f"CPC: ${cpc:.2f}<br>"
            f"Cluster: {cluster}"
        )
        node_color.append(cluster)
        node_size.append(max(10, min(50, volume / 1000)) if volume > 0 else 10)
    
    # Extract edge positions
    edge_x = []
    edge_y = []
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    # Create figure
    fig = go.Figure()
    
    # Add edges
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines',
        showlegend=False
    ))
    
    # Add nodes
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            showscale=True,
            colorscale='Viridis',
            size=node_size,
            color=node_color,
            colorbar=dict(
                thickness=15,
                title="Cluster",
                xanchor="left"
            ),
            line_width=2
        )
    ))
    
    fig.update_layout(
        title="Keyword Cluster Network",
        showlegend=False,
        height=600,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    
    return fig

def create_scatter_visualization(df: pd.DataFrame, tfidf_matrix, keyword_col: str = 'keyword') -> go.Figure:
    """Create 2D scatter plot of clusters"""
    # Make a copy to avoid modifying original
    df_plot = df.copy()
    
    # Reduce dimensions
    coords = reduce_dimensions_for_viz(tfidf_matrix, n_components=2)
    
    df_plot['x'] = coords[:, 0]
    df_plot['y'] = coords[:, 1]
    
    # Build hover data dynamically
    hover_cols = [keyword_col]
    if 'search_volume' in df_plot.columns:
        hover_cols.append('search_volume')
    if 'cpc' in df_plot.columns:
        hover_cols.append('cpc')
    if 'keyword_difficulty' in df_plot.columns:
        hover_cols.append('keyword_difficulty')
    
    # Size column - use search_volume if available, otherwise constant size
    size_col = 'search_volume' if 'search_volume' in df_plot.columns else None
    
    fig = px.scatter(
        df_plot,
        x='x',
        y='y',
        color='cluster',
        size=size_col,
        hover_data=hover_cols,
        title='Keyword Clusters (2D Projection)',
        labels={'x': 'Component 1', 'y': 'Component 2'},
        height=600,
        color_continuous_scale='Viridis'
    )
    
    fig.update_traces(marker=dict(line=dict(width=1, color='white')))
    
    return fig

def create_bubble_visualization(cluster_summaries: pd.DataFrame) -> go.Figure:
    """Create bubble chart of clusters"""
    if cluster_summaries.empty:
        return go.Figure()
    
    fig = px.scatter(
        cluster_summaries,
        x='Avg Difficulty',
        y='Avg CPC',
        size='Total Volume',
        color='Keywords',
        hover_data=['Cluster Name', 'Total Volume', 'Keywords'],
        title='Cluster Analysis: Value vs Difficulty',
        labels={
            'Avg Difficulty': 'Average Difficulty',
            'Avg CPC': 'Average CPC ($)'
        },
        height=500,
        color_continuous_scale='Blues'
    )
    
    # Add quadrant lines
    fig.add_hline(y=cluster_summaries['Avg CPC'].median(), line_dash="dash", opacity=0.5)
    fig.add_vline(x=50, line_dash="dash", opacity=0.5)
    
    # Add quadrant labels
    fig.add_annotation(x=25, y=cluster_summaries['Avg CPC'].max() * 0.9, text="Easy & Valuable", showarrow=False)
    fig.add_annotation(x=75, y=cluster_summaries['Avg CPC'].max() * 0.9, text="Hard & Valuable", showarrow=False)
    
    return fig