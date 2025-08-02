#!/usr/bin/env python3
"""
DataForSEO Keyword Research Pipeline - Enhanced Version
A production-ready Python pipeline for comprehensive keyword research using DataForSEO APIs.

Author: Generated with Claude Code
"""

import base64
import json
import time
import re
from functools import wraps
from typing import List, Dict, Optional, Tuple
import logging
from pathlib import Path

import requests
import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
from collections import defaultdict

from dotenv import load_dotenv
load_dotenv()

from config import CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/keyword_research.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# API Configuration
BASE = CONFIG["dataforseo"]["base"]
AUTH_HEADER = {
    "Authorization": "Basic " + base64.b64encode(
        f'{CONFIG["dataforseo"]["login"]}:{CONFIG["dataforseo"]["password"]}'.encode()
    ).decode(),
    "Content-Type": "application/json"
}

# =============================================
# HELPER FUNCTIONS
# =============================================

def rate_limited(max_per_second):
    """Decorator to rate limit function calls"""
    min_interval = 1.0 / max_per_second
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limited(CONFIG["dataforseo"]["rate_limit"])
def post_dfslabs(endpoint: str, payload: List[dict], retries: int = None) -> dict:
    """Enhanced API call with retry logic and rate limiting"""
    if retries is None:
        retries = CONFIG["dataforseo"]["retries"]
    
    url = f"{BASE}/dataforseo_labs/google/{endpoint}/live"
    
    for attempt in range(retries):
        try:
            response = requests.post(
                url, 
                headers=AUTH_HEADER, 
                data=json.dumps(payload),
                timeout=CONFIG["dataforseo"]["timeout"]
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                wait_time = 2 ** attempt
                logger.warning(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            response.raise_for_status()
            data = response.json()
            
            # DataForSEO success code is 20000
            if data.get("status_code") == 20000:
                return data
            elif data.get("status_code") == 40501:  # No data found
                logger.info(f"No data found for {endpoint}")
                return {"tasks": [{"result": []}]}
            else:
                logger.error(f"API error: {data.get('status_message')}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                    
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise
    
    raise RuntimeError(f"Failed after {retries} attempts")

def get_all_locations() -> Dict[str, int]:
    """Get all available location codes"""
    url = f"{BASE}/dataforseo_labs/locations_and_languages"
    response = requests.get(url, headers=AUTH_HEADER, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    if data.get("status_code") != 20000:
        raise RuntimeError("Could not fetch locations")
    
    locations = {}
    for task in data.get("tasks", []):
        for loc in task.get("result", []):
            locations[loc["location_name"]] = loc["location_code"]
    
    return locations

def flatten_task_result(dfslabs_json: dict) -> pd.DataFrame:
    """Flatten nested API response into DataFrame"""
    rows = []
    for task in dfslabs_json.get("tasks", []):
        for res in task.get("result", []):
            items = res.get("items") or []
            for item in items:
                # Handle both keyword data and SERP data structures
                if isinstance(item, dict):
                    # Flatten nested keyword_data if present
                    if "keyword_data" in item:
                        flat_item = {**item}
                        kw_data = flat_item.pop("keyword_data", {})
                        kw_info = kw_data.get("keyword_info", {})
                        flat_item.update({f"keyword_{k}": v for k, v in kw_info.items()})
                        rows.append(flat_item)
                    else:
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

# =============================================
# API WRAPPER FUNCTIONS
# =============================================

def keyword_ideas(seeds: List[str], location_code: int, language_name: str, limit=500):
    """Get keyword ideas from seed terms"""
    payload = [{
        "keywords": seeds[:200],  # max 200 per call
        "location_code": location_code,
        "language_name": language_name,
        "limit": limit,
        "include_seed_keyword": True,
        "include_serp_info": False
    }]
    return flatten_task_result(post_dfslabs("keyword_ideas", payload))

def keyword_suggestions(seed: str, location_code: int, language_name: str, limit=500):
    """Get keyword suggestions containing the seed phrase"""
    payload = [{
        "keyword": seed,
        "location_code": location_code,
        "language_name": language_name,
        "limit": limit,
        "include_seed_keyword": True
    }]
    return flatten_task_result(post_dfslabs("keyword_suggestions", payload))

def keyword_overview(keywords: List[str], location_code: int, language_name: str):
    """Get comprehensive keyword metrics including SERP features"""
    payload = [{
        "keywords": keywords[:700],  # max 700 per call
        "location_code": location_code,
        "language_name": language_name,
        "include_serp_info": True,
        "include_clickstream_data": False  # Set True if you have access
    }]
    return flatten_task_result(post_dfslabs("keyword_overview", payload))

def keywords_for_site(domain: str, location_code: int, language_name: str, limit=2000):
    """Get keywords a domain ranks for"""
    payload = [{
        "target": domain,
        "location_code": location_code,
        "language_name": language_name,
        "limit": limit,
        "include_subdomains": True
    }]
    return flatten_task_result(post_dfslabs("keywords_for_site", payload))

def bulk_keyword_difficulty(keywords: List[str], location_code: int, language_name: str):
    """Get keyword difficulty scores"""
    payload = [{
        "keywords": keywords[:1000],  # max 1000 per call
        "location_code": location_code,
        "language_name": language_name
    }]
    return flatten_task_result(post_dfslabs("bulk_keyword_difficulty", payload))

def historical_keyword_data(keywords: List[str], location_code: int, language_name: str):
    """Get historical search volume data"""
    payload = [{
        "keywords": keywords[:700],
        "location_code": location_code,
        "language_name": language_name
    }]
    return flatten_task_result(post_dfslabs("historical_keyword_data", payload))

# =============================================
# MAIN PIPELINE FUNCTIONS
# =============================================

def generate_seed_keywords(country_code: int, language_name: str) -> pd.DataFrame:
    """Generate seed keywords from multiple sources"""
    logger.info("📋 Step 3: Generating seed keywords...")
    
    all_keywords = []
    keyword_sources = defaultdict(list)  # Track keyword sources
    
    # 1. Keyword Ideas (category-based expansion)
    logger.info("🔍 Generating keyword ideas...")
    try:
        ideas_df = keyword_ideas(CONFIG["seed"]["business_terms"], country_code, language_name, limit=1000)
        if not ideas_df.empty:
            ideas_df["source"] = "ideas"
            all_keywords.append(ideas_df)
            keyword_sources["ideas"] = ideas_df["keyword"].tolist()
            logger.info(f"   ✅ Found {len(ideas_df)} keyword ideas")
        else:
            logger.warning("   ⚠️ No keyword ideas returned")
    except Exception as e:
        logger.error(f"   ❌ Keyword ideas failed: {e}")
    
    # 2. Keyword Suggestions (phrase-match)
    logger.info("🔍 Generating keyword suggestions...")
    for seed in tqdm(CONFIG["seed"]["business_terms"], desc="Processing seeds"):
        try:
            sug_df = keyword_suggestions(seed, country_code, language_name, limit=500)
            if not sug_df.empty:
                sug_df["source"] = f"suggestions_{seed}"
                sug_df["seed_term"] = seed
                all_keywords.append(sug_df)
                keyword_sources[f"suggestions_{seed}"] = sug_df["keyword"].tolist()
                logger.info(f"   ✅ '{seed}': {len(sug_df)} suggestions")
            else:
                logger.warning(f"   ⚠️ '{seed}': No suggestions returned")
        except Exception as e:
            logger.error(f"   ❌ Failed to get suggestions for '{seed}': {e}")
    
    # 3. Keywords from competitor sites (if available)
    if CONFIG["seed"]["competitor_domains"]:
        logger.info("🔍 Analyzing competitor domains...")
        for domain in tqdm(CONFIG["seed"]["competitor_domains"], desc="Competitor sites"):
            try:
                site_df = keywords_for_site(domain, country_code, language_name, limit=2000)
                if not site_df.empty:
                    site_df["source"] = f"competitor_{domain}"
                    site_df["source_domain"] = domain
                    all_keywords.append(site_df)
                    keyword_sources[f"site_{domain}"] = site_df["keyword"].tolist()
                    logger.info(f"   ✅ {domain}: {len(site_df)} keywords")
                else:
                    logger.warning(f"   ⚠️ {domain}: No keywords returned")
            except Exception as e:
                logger.error(f"   ❌ Failed to get keywords for {domain}: {e}")
    else:
        logger.info("🔍 No competitor domains specified, skipping competitor analysis")
    
    # Combine all keywords
    if all_keywords:
        seed_keywords_df = pd.concat(all_keywords, ignore_index=True)
        
        # Initial deduplication keeping track of sources
        seed_keywords_df = seed_keywords_df.drop_duplicates(subset=["keyword"], keep="first")
        
        logger.info(f"✅ Total unique keywords discovered: {len(seed_keywords_df):,}")
        logger.info("📊 Sources breakdown:")
        source_counts = seed_keywords_df["source"].value_counts().head(10)
        for source, count in source_counts.items():
            logger.info(f"   - {source}: {count:,} keywords")
        
        return seed_keywords_df
    else:
        raise ValueError("No keywords generated. Check your seed terms and API credentials.")

def enrich_keywords(seed_keywords_df: pd.DataFrame, country_code: int, language_name: str) -> pd.DataFrame:
    """Enrich keywords with comprehensive metrics and difficulty scores"""
    logger.info("📋 Step 4: Enriching keywords with comprehensive metrics...")
    
    # First, parse existing data from the CSV
    enriched_df = parse_existing_keyword_data(seed_keywords_df)
    
    # Sort by search volume and take top keywords for additional enrichment
    # Focus on top 1000 keywords for additional API calls to manage costs
    if "search_volume" in enriched_df.columns:
        top_keywords = enriched_df.nlargest(1000, "search_volume")["keyword"].tolist()
    else:
        top_keywords = enriched_df["keyword"].tolist()[:1000]
    
    if not top_keywords:
        logger.warning("No keywords found to enrich")
        return enriched_df
    
    # Step 4.1: Get difficulty scores for keywords without them (most important missing data)
    keywords_without_difficulty = enriched_df[
        enriched_df["keyword_difficulty"].isna() | (enriched_df["keyword_difficulty"] == 0)
    ]["keyword"].tolist()
    
    if keywords_without_difficulty:
        logger.info(f"🔍 Getting difficulty scores for {len(keywords_without_difficulty)} keywords...")
        difficulty_results = []
        
        try:
            for batch in tqdm(list(batch_iterator(keywords_without_difficulty, 1000)), desc="Difficulty scores"):
                try:
                    diff_df = bulk_keyword_difficulty(batch, country_code, language_name)
                    if not diff_df.empty:
                        difficulty_results.append(diff_df)
                        logger.info(f"   ✅ Processed difficulty batch of {len(batch)} keywords")
                    else:
                        logger.warning(f"   ⚠️ Empty difficulty response for batch of {len(batch)} keywords")
                except Exception as e:
                    logger.error(f"   ❌ Difficulty batch failed: {e}")
                    continue
            
            # Merge difficulty data
            if difficulty_results:
                diff_df = pd.concat(difficulty_results, ignore_index=True)
                logger.info(f"📊 Difficulty data collected for {len(diff_df)} keywords")
                
                # Update difficulty scores
                enriched_df = enriched_df.merge(
                    diff_df[["keyword", "keyword_difficulty"]],
                    on="keyword",
                    how="left",
                    suffixes=("", "_new")
                )
                
                # Fill missing difficulty scores
                enriched_df["keyword_difficulty"] = enriched_df["keyword_difficulty"].fillna(
                    enriched_df["keyword_difficulty_new"]
                )
                enriched_df.drop(columns=["keyword_difficulty_new"], inplace=True, errors='ignore')
                logger.info(f"   ✅ Difficulty scores updated successfully")
            else:
                logger.warning("   ⚠️ No difficulty data collected")
                
        except Exception as e:
            logger.error(f"❌ Keyword difficulty enrichment failed: {e}")
    else:
        logger.info("✅ All keywords already have difficulty scores")
    
    # Step 4.2: Calculate enrichment statistics
    total_keywords = len(enriched_df)
    keywords_with_difficulty = enriched_df["keyword_difficulty"].notna().sum()
    keywords_with_cpc = enriched_df["cpc"].notna().sum() if "cpc" in enriched_df.columns else 0
    keywords_with_volume = enriched_df["search_volume"].notna().sum() if "search_volume" in enriched_df.columns else 0
    
    keywords_with_volume_positive = (enriched_df["search_volume"] > 0).sum() if "search_volume" in enriched_df.columns else 0
    keywords_with_intent = enriched_df["main_intent"].notna().sum() if "main_intent" in enriched_df.columns else 0
    
    logger.info("📊 Final Enrichment Summary:")
    logger.info(f"   • Total keywords: {total_keywords:,}")
    logger.info(f"   • With search volume > 0: {keywords_with_volume_positive:,} ({keywords_with_volume_positive/total_keywords*100:.1f}%)")
    logger.info(f"   • With CPC data: {keywords_with_cpc:,} ({keywords_with_cpc/total_keywords*100:.1f}%)")
    logger.info(f"   • With difficulty scores: {keywords_with_difficulty:,} ({keywords_with_difficulty/total_keywords*100:.1f}%)")
    logger.info(f"   • With search intent: {keywords_with_intent:,} ({keywords_with_intent/total_keywords*100:.1f}%)")
    
    # Show intent distribution
    if "main_intent" in enriched_df.columns:
        intent_counts = enriched_df["main_intent"].value_counts()
        logger.info("📊 Search Intent Distribution:")
        for intent, count in intent_counts.head(5).items():
            logger.info(f"   • {intent}: {count:,} keywords ({count/total_keywords*100:.1f}%)")
    
    logger.info("✅ Keyword enrichment completed!")
    return enriched_df

def initialize_directories():
    """Create necessary directories"""
    Path("data").mkdir(exist_ok=True)
    Path("exports").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    logger.info(" Directories initialized")

def verify_credentials():
    """Test API connection"""
    try:
        locations = get_all_locations()
        logger.info(f" API connection successful - {len(locations)} locations available")
        return True
    except Exception as e:
        logger.error(f"❌ API connection failed: {e}")
        return False

def get_location_codes():
    """Resolve location and language codes"""
    logger.info("Resolving location codes...")    
    # Get all locations for target country
    all_locations = get_all_locations()
    target_locations = {k: v for k, v in all_locations.items() 
                       if CONFIG["target"]["country"] in k}
    
    # Get country code
    country_code = target_locations.get(CONFIG["target"]["country"])
    if not country_code:
        raise ValueError(f"Country not found: {CONFIG['target']['country']}")
    
    logger.info(f"Country code: {country_code}")
    
    # Get province codes
    province_codes = {}
    if CONFIG["target"]["analyze_provinces"]:
        for province in CONFIG["target"]["provinces"]:
            if province in target_locations:
                province_codes[province] = target_locations[province]
                logger.info(f"Province '{province}' code: {target_locations[province]}")
            else:
                logger.warning(f"Province not found: {province}")
    
    return country_code, province_codes

def main():
    """Main pipeline execution"""
    logger.info("🚀 Starting DataForSEO Keyword Research Pipeline")
    logger.info("=" * 60)
    
    try:
        # Step 1: Initialize and verify credentials
        logger.info("📋 Step 1: Initializing...")
        initialize_directories()
        
        if not verify_credentials():
            logger.error("❌ Pipeline failed: Invalid API credentials")
            return False
        
        # Step 2: Get location codes
        logger.info("📋 Step 2: Getting location codes...")
        country_code, province_codes = get_location_codes()
        language_name = CONFIG["target"]["language"]
        
        # Step 3: Generate seed keywords
        seed_keywords_df = generate_seed_keywords(country_code, language_name)
        
        # Save intermediate results
        output_file = "data/seed_keywords.csv"
        seed_keywords_df.to_csv(output_file, index=False)
        logger.info(f"💾 Seed keywords saved to {output_file}")
        
        # Step 4: Enrich with metrics
        enriched_keywords_df = enrich_keywords(seed_keywords_df, country_code, language_name)
        
        # Save enriched results
        enriched_output_file = "data/enriched_keywords.csv"
        enriched_keywords_df.to_csv(enriched_output_file, index=False)
        logger.info(f"💾 Enriched keywords saved to {enriched_output_file}")
        
        # Step 5: Competitor analysis (placeholder)
        logger.info("📋 Step 5: Competitor analysis...")
        logger.info("⏳ Coming next: Competitor analysis implementation")
        
        # Step 6: Filter and merge (placeholder)
        logger.info("📋 Step 6: Filtering and merging...")
        logger.info("⏳ Coming next: Filtering implementation")
        
        # Step 7: Analyze seasonality (placeholder)
        logger.info("📋 Step 7: Seasonality analysis...")
        logger.info("⏳ Coming next: Seasonality analysis implementation")
        
        # Step 8: Clustering (placeholder)
        logger.info("📋 Step 8: Clustering...")
        logger.info("⏳ Coming next: Clustering implementation")
        
        # Step 9: Scoring and export (placeholder)
        logger.info("📋 Step 9: Scoring and export...")
        logger.info("⏳ Coming next: Export implementation")
        
        logger.info("✅ Step 9 (Keyword Enrichment) implemented!")
        logger.info("🔧 Ready for Step 10: Competitor Analysis")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("🎉 Pipeline completed successfully!")
    else:
        logger.error("💥 Pipeline failed!")
        exit(1)