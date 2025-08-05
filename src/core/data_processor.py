"""
Data processing utilities for keyword research pipeline
"""
import pandas as pd
import numpy as np
import logging
from typing import List

logger = logging.getLogger(__name__)


def flatten_task_result(dfslabs_json: dict) -> pd.DataFrame:
    """Flatten nested API response into DataFrame"""
    if not dfslabs_json or not isinstance(dfslabs_json, dict):
        return pd.DataFrame()
    
    rows = []
    tasks = dfslabs_json.get("tasks", [])
    if not tasks:
        return pd.DataFrame()
    
    for task in tasks:
        if not task or not isinstance(task, dict):
            continue
        
        results = task.get("result", [])
        if not results:
            continue
        
        for res in results:
            if not res or not isinstance(res, dict):
                continue
                
            items = res.get("items")
            if not items:
                continue
                
            for item in items:
                if not item or not isinstance(item, dict):
                    continue
                    
                # Handle both keyword data and SERP data structures
                if "keyword_data" in item:
                    # Handle nested keyword_data structure (e.g., from keyword_ideas)
                    flat_item = {**item}
                    kw_data = flat_item.pop("keyword_data", {})
                    
                    # Extract keyword at the top level of keyword_data
                    if "keyword" in kw_data:
                        flat_item["keyword"] = kw_data["keyword"]
                    
                    # Extract keyword_info data with keyword_ prefix
                    kw_info = kw_data.get("keyword_info", {})
                    flat_item.update({f"keyword_{k}": v for k, v in kw_info.items()})
                    
                    # Also include other keyword_data fields
                    for k, v in kw_data.items():
                        if k not in ["keyword", "keyword_info"]:
                            flat_item[f"keyword_{k}"] = v
                    
                    rows.append(flat_item)
                elif "keyword" in item and "keyword_info" in item:
                    # Handle direct keyword structure (e.g., from keywords_for_site)
                    flat_item = {**item}
                    
                    # Extract keyword_info data
                    kw_info = flat_item.get("keyword_info", {})
                    if kw_info:
                        # Add common fields from keyword_info
                        flat_item["search_volume"] = kw_info.get("search_volume", 0)
                        flat_item["cpc"] = kw_info.get("cpc")
                        flat_item["competition"] = kw_info.get("competition")
                        flat_item["competition_level"] = kw_info.get("competition_level")
                        flat_item["monthly_searches"] = kw_info.get("monthly_searches")
                    
                    rows.append(flat_item)
                else:
                    # Handle any other structure
                    rows.append(item)
    
    return pd.DataFrame(rows)


def batch_iterator(items: List, batch_size: int = 1000):
    """Yield batches from a list"""
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


def normalize_series(s: pd.Series) -> pd.Series:
    """Normalize a pandas series to 0-1 range"""
    s = s.fillna(0)
    if s.max() == s.min():
        return pd.Series([0.5] * len(s), index=s.index)
    return (s - s.min()) / (s.max() - s.min())


def parse_existing_keyword_data(df: pd.DataFrame) -> pd.DataFrame:
    """Parse existing keyword data from JSON strings in the CSV"""
    logger.info("🔧 Parsing existing keyword data from CSV...")
    
    parsed_df = df.copy()
    
    # Parse keyword_info JSON if it exists
    if 'keyword_info' in parsed_df.columns:
        def extract_keyword_info(info_str):
            if pd.isna(info_str) or info_str == '':
                return {}
            try:
                return eval(info_str) if isinstance(info_str, str) else info_str
            except:
                return {}
        
        # Extract keyword info data
        keyword_info_data = parsed_df['keyword_info'].apply(extract_keyword_info)
        
        # Extract specific fields
        parsed_df['search_volume'] = keyword_info_data.apply(lambda x: x.get('search_volume') if x else None)
        parsed_df['cpc'] = keyword_info_data.apply(lambda x: x.get('cpc') if x else None)
        parsed_df['competition'] = keyword_info_data.apply(lambda x: x.get('competition') if x else None)
        parsed_df['competition_level'] = keyword_info_data.apply(lambda x: x.get('competition_level') if x else None)
        parsed_df['monthly_searches'] = keyword_info_data.apply(lambda x: x.get('monthly_searches') if x else None)
        parsed_df['categories'] = keyword_info_data.apply(lambda x: x.get('categories') if x else None)
        
        logger.info(f"   ✅ Extracted basic keyword metrics")
    
    # Parse keyword_properties JSON if it exists
    if 'keyword_properties' in parsed_df.columns:
        def extract_keyword_properties(props_str):
            if pd.isna(props_str) or props_str == '':
                return {}
            try:
                return eval(props_str) if isinstance(props_str, str) else props_str
            except:
                return {}
        
        # Extract keyword properties data
        keyword_props_data = parsed_df['keyword_properties'].apply(extract_keyword_properties)
        
        # Extract difficulty score
        parsed_df['keyword_difficulty'] = keyword_props_data.apply(lambda x: x.get('keyword_difficulty') if x else None)
        
        logger.info(f"   ✅ Extracted keyword difficulty scores")
    
    # Parse search_intent_info JSON if it exists
    if 'search_intent_info' in parsed_df.columns:
        def extract_search_intent(intent_str):
            if pd.isna(intent_str) or intent_str == '':
                return {}
            try:
                return eval(intent_str) if isinstance(intent_str, str) else intent_str
            except:
                return {}
        
        # Extract search intent data
        intent_data = parsed_df['search_intent_info'].apply(extract_search_intent)
        
        # Extract intent information
        parsed_df['main_intent'] = intent_data.apply(lambda x: x.get('main_intent') if x else None)
        parsed_df['foreign_intent'] = intent_data.apply(lambda x: x.get('foreign_intent') if x else None)
        
        logger.info(f"   ✅ Extracted search intent data")
    
    # Clean up null values
    parsed_df['search_volume'] = pd.to_numeric(parsed_df['search_volume'], errors='coerce').fillna(0)
    parsed_df['cpc'] = pd.to_numeric(parsed_df['cpc'], errors='coerce')
    parsed_df['keyword_difficulty'] = pd.to_numeric(parsed_df['keyword_difficulty'], errors='coerce')
    
    # Create summary stats
    total_keywords = len(parsed_df)
    with_volume = (parsed_df['search_volume'] > 0).sum()
    with_cpc = parsed_df['cpc'].notna().sum()
    with_difficulty = parsed_df['keyword_difficulty'].notna().sum()
    
    logger.info("📊 Parsed Data Summary:")
    logger.info(f"   • Total keywords: {total_keywords:,}")
    logger.info(f"   • With search volume > 0: {with_volume:,} ({with_volume/total_keywords*100:.1f}%)")
    logger.info(f"   • With CPC data: {with_cpc:,} ({with_cpc/total_keywords*100:.1f}%)")
    logger.info(f"   • With difficulty scores: {with_difficulty:,} ({with_difficulty/total_keywords*100:.1f}%)")
    
    return parsed_df