"""Data loading and caching utilities"""
import streamlit as st
import pandas as pd
import json
from pathlib import Path
from typing import Dict, Optional

@st.cache_data(ttl=300)
def discover_campaigns() -> Dict:
    """Discover all available campaigns"""
    campaigns = {}
    # Look for campaigns directory in parent directory (from dashboard/)
    campaign_dir = Path("../campaigns")
    
    if not campaign_dir.exists():
        return campaigns
    
    for campaign_path in campaign_dir.iterdir():
        if campaign_path.is_dir():
            campaign_name = campaign_path.name
            latest = campaign_path / "latest"
            
            if latest.exists():
                campaigns[campaign_name] = {
                    'path': latest,
                    'name': campaign_name
                }
    
    return campaigns

@st.cache_data
def load_campaign_data(campaign_path: Path) -> Dict:
    """Load all data files for a campaign"""
    data = {}
    
    # Load scored keywords (main dataset)
    scored_file = campaign_path / "data" / "scored_keywords_v2.csv"
    if scored_file.exists():
        data['keywords'] = pd.read_csv(scored_file)
    
    # Load competitor keywords
    competitor_file = campaign_path / "data" / "competitor_keywords_v2.csv"
    if competitor_file.exists():
        data['competitor_keywords'] = pd.read_csv(competitor_file)
        # Map columns for compatibility
        if 'keyword_search_volume' in data['competitor_keywords'].columns:
            data['competitor_keywords']['search_volume'] = data['competitor_keywords']['keyword_search_volume']
        if 'keyword_cpc' in data['competitor_keywords'].columns:
            data['competitor_keywords']['cpc'] = data['competitor_keywords']['keyword_cpc']
        if 'keyword_competition' in data['competitor_keywords'].columns:
            data['competitor_keywords']['keyword_difficulty'] = data['competitor_keywords']['keyword_competition'] * 100
    
    # Load metadata
    metadata_file = campaign_path / "run_metadata.json"
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            data['metadata'] = json.load(f)
    
    # Load recommendations
    rec_file = campaign_path / "data" / "campaign_recommendations_v2.json"
    if rec_file.exists():
        with open(rec_file, 'r') as f:
            data['recommendations'] = json.load(f)
    
    # Load export summary
    summary_file = campaign_path / "data" / "export_summary_v2.json"
    if summary_file.exists():
        with open(summary_file, 'r') as f:
            data['export_summary'] = json.load(f)
    
    return data

def get_available_columns(df: pd.DataFrame) -> Dict[str, list]:
    """Get available columns categorized by type"""
    return {
        'metrics': [col for col in df.columns if any(
            term in col.lower() for term in ['volume', 'cpc', 'difficulty', 'score']
        )],
        'categorical': [col for col in df.columns if any(
            term in col.lower() for term in ['intent', 'tier', 'cluster', 'category']
        )],
        'text': [col for col in df.columns if 'keyword' in col.lower()],
        'all': df.columns.tolist()
    }