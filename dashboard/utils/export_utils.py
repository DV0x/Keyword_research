"""Export utilities for different formats"""
import pandas as pd
from datetime import datetime
from typing import List, Optional

def export_to_google_ads(
    df: pd.DataFrame, 
    campaign_name: str,
    match_type: str = "Phrase",
    keyword_col: str = "keyword"
) -> pd.DataFrame:
    """Format keywords for Google Ads Editor import"""
    export_df = pd.DataFrame()
    export_df['Campaign'] = campaign_name
    export_df['Ad Group'] = df.get('cluster_name', campaign_name)
    export_df['Keyword'] = df[keyword_col]
    export_df['Match Type'] = match_type
    if 'cpc' in df.columns:
        export_df['Max CPC'] = (df['cpc'] * 1.2).round(2)  # 20% above average
    export_df['Status'] = 'Enabled'
    
    return export_df

def export_to_microsoft_ads(
    df: pd.DataFrame,
    campaign_name: str,
    keyword_col: str = "keyword"
) -> pd.DataFrame:
    """Format keywords for Microsoft Ads import"""
    export_df = pd.DataFrame()
    export_df['Campaign'] = campaign_name
    export_df['Ad group'] = df.get('cluster_name', campaign_name)
    export_df['Keyword'] = df[keyword_col]
    export_df['Match type'] = 'Phrase'
    if 'cpc' in df.columns:
        export_df['Bid'] = (df['cpc'] * 1.2).round(2)
    export_df['Status'] = 'Active'
    
    return export_df

def export_clustered_keywords(
    df: pd.DataFrame,
    cluster_summaries: pd.DataFrame,
    keyword_col: str = "keyword"
) -> dict:
    """Export keywords organized by clusters"""
    export_data = {
        'export_date': datetime.now().isoformat(),
        'total_clusters': len(cluster_summaries),
        'total_keywords': len(df),
        'clusters': {}
    }
    
    for cluster_id in df['cluster'].unique():
        cluster_df = df[df['cluster'] == cluster_id]
        cluster_name = cluster_summaries.loc[cluster_id, 'Cluster Name'] if cluster_id in cluster_summaries.index else f"Cluster {cluster_id}"
        
        cluster_data = {
            'keywords': cluster_df[keyword_col].tolist(),
            'keyword_count': len(cluster_df)
        }
        
        # Add optional metrics if available
        if 'search_volume' in cluster_df.columns:
            cluster_data['total_volume'] = int(cluster_df['search_volume'].sum())
        if 'cpc' in cluster_df.columns:
            cluster_data['avg_cpc'] = float(cluster_df['cpc'].mean())
        if 'keyword_difficulty' in cluster_df.columns:
            cluster_data['avg_difficulty'] = float(cluster_df['keyword_difficulty'].mean())
        
        export_data['clusters'][cluster_name] = cluster_data
    
    return export_data