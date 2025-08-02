# DataForSEO Keyword Research Pipeline - Enhanced Version

A production-ready Python pipeline for comprehensive keyword research using DataForSEO APIs. This enhanced version includes improved error handling, rate limiting, keyword difficulty scoring, seasonal analysis, and smarter clustering.

---

## 🚀 Implementation Progress

**Last Updated**: August 2, 2025  
**GitHub Repository**: https://github.com/DV0x/Keyword_research

### ✅ Completed Steps

| Step | Description | Status | Details |
|------|-------------|--------|---------|
| **Step 1** | Check Python Installation | ✅ **COMPLETE** | Python 3.13.2 installed and working |
| **Step 2** | Set Up Project Environment | ✅ **COMPLETE** | Virtual environment, directory structure created |
| **Step 3** | Install Dependencies | ✅ **COMPLETE** | All packages installed (pandas, requests, scikit-learn, etc.) |
| **Step 4** | Get DataForSEO Credentials | ✅ **COMPLETE** | API credentials configured and secured |
| **Step 5** | Configure Your Campaign | ✅ **COMPLETE** | Config.py created with mortgage industry focus |
| **Step 6** | Create Main Script Structure | ✅ **COMPLETE** | keyword_research.py with full pipeline scaffolding |
| **Step 7** | Test API Connection | ✅ **COMPLETE** | API connection verified (94 locations available) |
| **Step 8** | Implement Keyword Generation | ✅ **COMPLETE** | 3,438 unique keywords generated from multiple sources |

### 🔄 Current Status
- **Location**: Canada (Code: 2124) 
- **Target Industry**: Mortgage/Finance (Private lending, bad credit solutions)
- **API Status**: ✅ Connected and authenticated
- **Keywords Generated**: ✅ 3,438 unique keywords from 9 sources
- **Pipeline**: Step 8 complete, ready for Step 9 (Keyword Enrichment)

### 📋 Next Steps (In Order)
| Step | Description | Priority | Estimated Time |
|------|-------------|----------|----------------|
| **Step 9** | Add Keyword Enrichment | **HIGH** | 20-30 min |
| **Step 10** | Implement Competitor Analysis | **MEDIUM** | 45-60 min |
| **Step 11** | Add Filtering & Clustering | **MEDIUM** | 30-45 min |
| **Step 12** | Create Export System | **HIGH** | 20-30 min |

### 🛠️ Technical Implementation
- **Main Script**: `keyword_research.py` (420+ lines, Step 8 implemented)
- **Configuration**: `config.py` (mortgage industry settings)
- **Security**: `.env` credentials (excluded from Git)
- **Dependencies**: All installed in virtual environment
- **Logging**: File and console logging configured
- **Rate Limiting**: 30 req/sec protection implemented
- **Data Output**: `data/seed_keywords.csv` (3,438 keywords with metrics)

### 🎯 Ready to Run
The pipeline structure is complete and can be executed with:
```bash
source venv/bin/activate
python keyword_research.py
```

**Current output**: Generates 3,438 mortgage-related keywords with search volume, CPC, and intent data, saves to CSV

---

## Features

1. **Discover seed keywords** from scratch with multiple data sources
2. **Expand & qualify** with search volume, CPC, competition, and difficulty metrics
3. **Analyze competitors** and extract their successful keywords
4. **Smart filtering** with intent classification and semantic deduplication
5. **Advanced clustering** with multiple algorithms and scoring methods
6. **Geographic analysis** with province-level data for local campaigns
7. **Export campaign-ready** ad groups with difficulty tiers and negatives

---

## Step-by-Step Implementation Guide

### Step 1: Check Python Installation

**Windows:**
1. Open Command Prompt (Win+R, type `cmd`, press Enter)
2. Type `python --version` or `python3 --version`
3. If not installed, download from https://python.org/downloads/
   - Choose Python 3.8 or newer
   - Check "Add Python to PATH" during installation

**Mac:**
1. Open Terminal (Cmd+Space, type "Terminal")
2. Type `python3 --version`
3. If not installed:
   - Install Homebrew first: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
   - Then install Python: `brew install python3`

**Linux:**
1. Open Terminal
2. Type `python3 --version`
3. If not installed: `sudo apt update && sudo apt install python3 python3-pip`

### Step 2: Set Up Project Environment

1. **Create project directory:**
   ```bash
   mkdir keyword_research_project
   cd keyword_research_project
   ```

2. **Create virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   
   # Activate virtual environment:
   # Windows:
   venv\Scripts\activate
   
   # Mac/Linux:
   source venv/bin/activate
   ```

3. **Create project structure:**
   ```bash
   mkdir data exports logs
   touch keyword_research.py config.py requirements.txt
   ```

### Step 3: Install Dependencies

1. **Create requirements.txt file with these contents:**
   ```
   requests>=2.31.0
   pandas>=2.0.0
   numpy>=1.24.0
   scikit-learn>=1.3.0
   tqdm>=4.65.0
   pyyaml>=6.0
   python-dotenv>=1.0.0
   openpyxl>=3.1.0
   sentence-transformers>=2.2.0
   ```

2. **Install all dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Step 4: Get DataForSEO Credentials

1. **Sign up for DataForSEO:**
   - Go to https://app.dataforseo.com/register
   - Complete registration
   - Verify email

2. **Get API credentials:**
   - Log in to https://app.dataforseo.com/
   - Go to API Access section
   - Copy your login and password

3. **Set up credentials securely:**
   - Create `.env` file in project root
   - Add credentials (never commit this file):
   ```
   DATAFORSEO_LOGIN=your_login_here
   DATAFORSEO_PASSWORD=your_password_here
   ```

### Step 5: Configure Your Campaign

1. **Copy the configuration template from Cell 2**
2. **Customize for your business:**
   - Change country/language
   - Replace seed keywords with your industry terms
   - Adjust filters (volume, CPC, difficulty)
   - Set competitor domains (optional)
   - Configure export preferences

### Step 6: Create Main Script Structure

1. **Create `keyword_research.py` with this structure:**
   ```python
   # Import configuration
   from config import CONFIG
   
   # Import all functions from Cell 3
   # Import API wrappers from Cell 5
   # Import analysis functions
   
   def main():
       # Step 1: Initialize and verify credentials
       # Step 2: Get location codes (Cell 4)
       # Step 3: Generate seed keywords (Cell 6)
       # Step 4: Enrich with metrics (Cell 7)
       # Step 5: Competitor analysis (Cells 8-9)
       # Step 6: Filter and merge (Cell 10)
       # Step 7: Analyze seasonality (Cell 11)
       # Step 8: Clustering (implement from notes)
       # Step 9: Scoring and export
       
   if __name__ == "__main__":
       main()
   ```

### Step 7: Run the Pipeline

1. **Test API connection first:**
   ```python
   # Create test_connection.py
   import requests
   from config import CONFIG
   import base64
   
   auth = base64.b64encode(
       f'{CONFIG["dataforseo"]["login"]}:{CONFIG["dataforseo"]["password"]}'.encode()
   ).decode()
   
   response = requests.get(
       "https://api.dataforseo.com/v3/dataforseo_labs/locations_and_languages",
       headers={"Authorization": f"Basic {auth}"}
   )
   print(f"Status: {response.status_code}")
   ```

2. **Run the test:**
   ```bash
   python test_connection.py
   # Should return Status: 200
   ```

3. **Run full pipeline:**
   ```bash
   python keyword_research.py
   ```

### Step 8: Monitor Progress

1. **Expected timeline:**
   - Initial setup: 30-60 minutes
   - First run: 15-30 minutes (depending on keywords)
   - Subsequent runs: 10-20 minutes

2. **Watch for:**
   - Progress bars showing API calls
   - Intermediate results printing
   - Log messages for any errors
   - Final export confirmation

### Step 9: Review Results

1. **Check exports directory for:**
   - `ad_groups_tier1.csv` - Start with these keywords
   - `ad_groups_tier2.csv` - Secondary campaigns
   - `negative_keywords.csv` - Upload to exclude irrelevant traffic
   - `keyword_analytics.xlsx` - Full analysis report

2. **Validate results:**
   - Open CSV files in Excel/Google Sheets
   - Check keyword relevance
   - Review difficulty scores
   - Verify search volumes make sense

### Step 10: Customize and Iterate

1. **Common customizations:**
   - Adjust minimum search volume if too few/many keywords
   - Add more exclude patterns for your industry
   - Modify clustering parameters
   - Change scoring weights

2. **Optimization tips:**
   - Start with 5-10 seed keywords
   - Run for one location first
   - Use conservative filters initially
   - Expand gradually

### Troubleshooting Guide

**Common Issues:**

1. **"Module not found" error:**
   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

2. **API authentication fails:**
   - Double-check credentials in .env file
   - Ensure no extra spaces in login/password
   - Verify account is active

3. **Rate limit errors:**
   - Reduce rate_limit in CONFIG (try 20 instead of 30)
   - Add longer delays between calls

4. **Memory errors with large datasets:**
   - Process in smaller batches
   - Reduce limit parameters
   - Increase filtering thresholds

5. **No keywords returned:**
   - Check if seed keywords are too specific
   - Verify location/language settings
   - Lower minimum search volume

### Cost Estimation

- **Small campaign (5K keywords):** ~$10-20
- **Medium campaign (20K keywords):** ~$40-60
- **Large campaign (50K keywords):** ~$80-120
- **Monthly monitoring:** ~$20-30

### Best Practices

1. **Start small:** Test with 1-2 seed keywords first
2. **Version control:** Save different configurations
3. **Document changes:** Keep notes on what works
4. **Regular updates:** Run weekly/monthly for fresh data
5. **Backup exports:** Archive results before each run

---

## 0) High-level pipeline

```
Config  ➜  Enhanced Helpers (auth, rate limiting, retry logic)
       ➜  Get all location codes (country + provinces)
       ➜  Generate seed keywords (ideas/suggestions/keywords_for_site)
       ➜  Enrich with keyword overview & difficulty scores
       ➜  Analyze historical trends & seasonality
       ➜  Discover competitors via SERP analysis
       ➜  Extract competitor keywords & identify gaps
       ➜  Merge, dedupe, smart filtering (semantic + intent)
       ➜  Advanced clustering (categories/KMeans/hierarchical)
       ➜  Multi-factor scoring with difficulty weighting
       ➜  Geographic expansion (province-level analysis)
       ➜  Export: tiered ad groups, smart negatives, full analytics
```

---

## 1) Prerequisites

**Python 3.8+** recommended

**Required libraries**:
```bash
pip install requests pandas numpy scikit-learn tqdm pyyaml python-dotenv
pip install sentence-transformers  # For semantic deduplication (optional)
```

**DataForSEO Account**: Get credentials at https://app.dataforseo.com/api-access

---

## 2) Notebook skeleton

### **Cell 1 — Install deps (if needed)**

```python
%pip install requests pandas numpy scikit-learn tqdm pyyaml
```

### **Cell 2 — Configuration**

```python
import os
from datetime import datetime

CONFIG = {
    "dataforseo": {
        "login": os.getenv("DATAFORSEO_LOGIN", "<YOUR_LOGIN>"),
        "password": os.getenv("DATAFORSEO_PASSWORD", "<YOUR_PASSWORD>"),
        "base": "https://api.dataforseo.com/v3",
        "rate_limit": 30,  # requests per second (2000/min = 33/sec, use 30 for safety)
        "timeout": 30,  # request timeout in seconds
        "retries": 3  # retry attempts for failed requests
    },
    "target": {
        "country": "Canada",
        "language": "English",
        "provinces": ["Ontario, Canada", "British Columbia, Canada", "Alberta, Canada"],
        "analyze_provinces": True  # Set False to skip province-level analysis
    },
    "seed": {
        "business_terms": [
            "private mortgage",
            "bad credit mortgage",
            "bridge financing",
            "second mortgage",
            "home equity loan",
            "fast mortgage approval",
            "mortgage broker",
            "alternative mortgage lenders"
        ],
        "competitor_domains": [],  # Add as you discover them
        "your_domain": ""  # Your domain for gap analysis
    },
    "filters": {
        "min_search_volume": 20,
        "max_search_volume": 50000,  # Avoid overly broad terms
        "min_cpc_cad": 0.5,  # Minimum CPC (too low = low commercial intent)
        "max_cpc_cad": 8.0,
        "max_keyword_difficulty": 70,  # 0-100 scale
        "exclude_patterns": [
            r"\b(jobs?|careers?|salary|salaries|hiring|employment)\b",
            r"\b(definition|meaning|what is|what are|how to become)\b",
            r"\b(course|training|certification|school|university)\b",
            r"\b(free|diy|yourself)\b"
        ],
        "allowed_intents": ["commercial", "transactional"],
        "min_word_count": 2,  # Minimum words in keyword
        "max_word_count": 6   # Maximum words (avoid overly specific)
    },
    "clustering": {
        "method": "hybrid",  # "category", "kmeans", or "hybrid"
        "k_range": (8, 20),  # Range for optimal K detection
        "min_cluster_size": 5,  # Minimum keywords per cluster
        "similarity_threshold": 0.85  # For semantic deduplication
    },
    "scoring": {
        "volume_weight": 0.3,
        "cpc_weight": 0.2,
        "difficulty_weight": 0.3,
        "trend_weight": 0.2
    },
    "export": {
        "dir": f"exports/{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "formats": ["csv", "parquet", "json"],
        "difficulty_tiers": {
            "easy": (0, 30),
            "medium": (30, 60),
            "hard": (60, 100)
        }
    }
}
```

### **Cell 3 — Enhanced imports & helpers**

```python
import base64
import json
import time
import re
from functools import wraps
from typing import List, Dict, Optional, Tuple
import logging

import requests
import pandas as pd
import numpy as np
from tqdm import tqdm
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
from collections import defaultdict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration
BASE = CONFIG["dataforseo"]["base"]
AUTH_HEADER = {
    "Authorization": "Basic " + base64.b64encode(
        f'{CONFIG["dataforseo"]["login"]}:{CONFIG["dataforseo"]["password"]}'.encode()
    ).decode(),
    "Content-Type": "application/json"
}

# Rate limiting decorator
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

# Enhanced API call with retry logic
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
```

### **Cell 4 — Resolve location & language codes**

```python
# Get all locations for Canada
all_locations = get_all_locations()
canada_locations = {k: v for k, v in all_locations.items() if "Canada" in k}

# Get country code
country_code = canada_locations.get(CONFIG["target"]["country"])
if not country_code:
    raise ValueError(f"Country not found: {CONFIG['target']['country']}")
print(f"Country code: {country_code}")

# Get province codes
province_codes = {}
if CONFIG["target"]["analyze_provinces"]:
    for province in CONFIG["target"]["provinces"]:
        if province in canada_locations:
            province_codes[province] = canada_locations[province]
            print(f"Province '{province}' code: {canada_locations[province]}")
        else:
            logger.warning(f"Province not found: {province}")

language_name = CONFIG["target"]["language"]
print(f"Language: {language_name}")
print(f"Total locations to analyze: {1 + len(province_codes)}")
```

---

## 3) Enhanced seed generation with multiple sources

We'll use complementary data sources for comprehensive keyword discovery:

1. **Keyword Ideas** — category-level expansion
2. **Keyword Suggestions** — phrase-match variations
3. **Keyword Overview** — comprehensive metrics with SERP features
4. **Keywords For Site** — domain-specific keywords

### **Cell 5 — API wrapper functions**

```python
# Core API functions
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
```

### **Cell 6 — Generate seed keywords**

```python
all_keywords = []
keyword_sources = defaultdict(list)  # Track keyword sources

# 1. Keyword Ideas (category-based expansion)
print("Generating keyword ideas...")
ideas_df = keyword_ideas(CONFIG["seed"]["business_terms"], country_code, language_name, limit=1000)
if not ideas_df.empty:
    ideas_df["source"] = "ideas"
    all_keywords.append(ideas_df)
    keyword_sources["ideas"] = ideas_df["keyword"].tolist()

# 2. Keyword Suggestions (phrase-match)
print("Generating keyword suggestions...")
for seed in tqdm(CONFIG["seed"]["business_terms"], desc="Suggestions"):
    try:
        sug_df = keyword_suggestions(seed, country_code, language_name, limit=500)
        if not sug_df.empty:
            sug_df["source"] = f"suggestions_{seed}"
            sug_df["seed_term"] = seed
            all_keywords.append(sug_df)
            keyword_sources[f"suggestions_{seed}"] = sug_df["keyword"].tolist()
    except Exception as e:
        logger.error(f"Failed to get suggestions for '{seed}': {e}")

# 3. Keywords from competitor sites (if available)
if CONFIG["seed"]["competitor_domains"]:
    print("Analyzing competitor domains...")
    for domain in tqdm(CONFIG["seed"]["competitor_domains"], desc="Competitor sites"):
        try:
            site_df = keywords_for_site(domain, country_code, language_name, limit=2000)
            if not site_df.empty:
                site_df["source"] = f"competitor_{domain}"
                site_df["source_domain"] = domain
                all_keywords.append(site_df)
                keyword_sources[f"site_{domain}"] = site_df["keyword"].tolist()
        except Exception as e:
            logger.error(f"Failed to get keywords for {domain}: {e}")

# Combine all keywords
if all_keywords:
    seed_keywords_df = pd.concat(all_keywords, ignore_index=True)
    
    # Initial deduplication keeping track of sources
    seed_keywords_df = seed_keywords_df.drop_duplicates(subset=["keyword"], keep="first")
    
    print(f"\nTotal unique keywords discovered: {len(seed_keywords_df)}")
    print(f"Sources breakdown:")
    print(seed_keywords_df["source"].value_counts().head(10))
else:
    raise ValueError("No keywords generated. Check your seed terms and API credentials.")
```

### **Cell 7 — Enrich keywords with comprehensive metrics**

```python
# Get keyword overview for top keywords
print("\nEnriching keywords with comprehensive metrics...")

# Sort by volume and take top keywords for enrichment
top_keywords = seed_keywords_df.nlargest(2000, "search_volume")["keyword"].tolist()

# Get keyword overview in batches
overview_results = []
for batch in tqdm(list(batch_iterator(top_keywords, 700)), desc="Keyword overview"):
    try:
        overview_df = keyword_overview(batch, country_code, language_name)
        overview_results.append(overview_df)
    except Exception as e:
        logger.error(f"Overview batch failed: {e}")

if overview_results:
    overview_df = pd.concat(overview_results, ignore_index=True)
    
    # Merge overview data back to main dataframe
    seed_keywords_df = seed_keywords_df.merge(
        overview_df[["keyword", "keyword_difficulty", "serp_features", "monthly_searches"]],
        on="keyword",
        how="left"
    )

# Get difficulty scores for keywords without them
keywords_without_difficulty = seed_keywords_df[
    seed_keywords_df["keyword_difficulty"].isna()
]["keyword"].tolist()

if keywords_without_difficulty:
    print(f"\nGetting difficulty scores for {len(keywords_without_difficulty)} keywords...")
    difficulty_results = []
    
    for batch in tqdm(list(batch_iterator(keywords_without_difficulty, 1000)), desc="Difficulty scores"):
        try:
            diff_df = bulk_keyword_difficulty(batch, country_code, language_name)
            difficulty_results.append(diff_df)
        except Exception as e:
            logger.error(f"Difficulty batch failed: {e}")
    
    if difficulty_results:
        diff_df = pd.concat(difficulty_results, ignore_index=True)
        # Update difficulty scores
        seed_keywords_df = seed_keywords_df.merge(
            diff_df[["keyword", "keyword_difficulty"]],
            on="keyword",
            how="left",
            suffixes=("", "_new")
        )
        seed_keywords_df["keyword_difficulty"] = seed_keywords_df["keyword_difficulty"].fillna(
            seed_keywords_df["keyword_difficulty_new"]
        )
        seed_keywords_df.drop(columns=["keyword_difficulty_new"], inplace=True)

print(f"\nEnriched keywords: {len(seed_keywords_df)}")
print(f"Keywords with difficulty scores: {seed_keywords_df['keyword_difficulty'].notna().sum()}")
```

---

## 4) Advanced competitor discovery & analysis

### **Cell 8 — Discover SERP competitors**

```python
def serp_competitors(keywords: List[str], location_code: int, language_name: str):
    """Find domains competing for the same keywords"""
    payload = [{
        "keywords": keywords[:200],  # max 200
        "location_code": location_code,
        "language_name": language_name,
        "filters": [["metrics.organic.pos_1", ">", 0]],  # Has #1 rankings
        "limit": 100
    }]
    data = post_dfslabs("serp_competitors", payload)
    rows = []
    for task in data["tasks"]:
        for res in task.get("result", []):
            for item in res.get("items", []):
                rows.append(item)
    return pd.DataFrame(rows)

def domain_rank_overview(domain: str, location_code: int, language_name: str):
    """Get domain strength metrics"""
    payload = [{
        "target": domain,
        "location_code": location_code,
        "language_name": language_name
    }]
    return flatten_task_result(post_dfslabs("domain_rank_overview", payload))

# Select high-value keywords for competitor discovery
high_value_keywords = seed_keywords_df[
    (seed_keywords_df["search_volume"] > 100) & 
    (seed_keywords_df["cpc"] > 2.0)
].nlargest(200, "search_volume")["keyword"].tolist()

if not high_value_keywords:
    # Fallback to top volume keywords
    high_value_keywords = seed_keywords_df.nlargest(200, "search_volume")["keyword"].tolist()

print(f"Finding competitors for {len(high_value_keywords)} high-value keywords...")
competitors_df = serp_competitors(high_value_keywords, country_code, language_name)

if not competitors_df.empty:
    # Exclude your own domain if specified
    if CONFIG["seed"]["your_domain"]:
        competitors_df = competitors_df[
            ~competitors_df["domain"].str.contains(CONFIG["seed"]["your_domain"], case=False)
        ]
    
    # Exclude generic domains
    exclude_domains = ["google.com", "youtube.com", "facebook.com", "amazon.com", "wikipedia.org"]
    competitors_df = competitors_df[~competitors_df["domain"].isin(exclude_domains)]
    
    # Score competitors by multiple factors
    competitors_df["competitor_score"] = (
        normalize_series(competitors_df["etv"]) * 0.4 +
        normalize_series(competitors_df["count"]) * 0.3 +
        normalize_series(competitors_df["metrics.organic.pos_1"]) * 0.3
    )
    
    # Select top competitors
    top_competitors = competitors_df.nlargest(15, "competitor_score")
    
    print(f"\nTop {len(top_competitors)} competitors identified:")
    print(top_competitors[["domain", "etv", "count", "competitor_score"]].head(10))
    
    comp_domains = top_competitors["domain"].tolist()
else:
    print("No competitors found. Using manual competitor list...")
    comp_domains = CONFIG["seed"]["competitor_domains"]
```

### **Cell 9 — Extract competitor keywords with gap analysis**

```python
def ranked_keywords(domain: str, location_code: int, language_name: str, limit=10000):
    """Get keywords a domain ranks for"""
    payload = [{
        "target": domain,
        "location_code": location_code,
        "language_name": language_name,
        "limit": limit,
        "filters": [
            ["ranked_serp_element.serp_item.rank_group", "<=", 20],  # Top 20 only
            "and",
            ["keyword_data.keyword_info.search_volume", ">=", 10]
        ]
    }]
    return flatten_task_result(post_dfslabs("ranked_keywords", payload))

def domain_intersection(domain1: str, domain2: str, location_code: int, language_name: str):
    """Find keyword gaps between domains"""
    payload = [{
        "target1": domain1,
        "target2": domain2,
        "location_code": location_code,
        "language_name": language_name,
        "intersections": False,  # Keywords domain2 has but domain1 doesn't
        "limit": 1000
    }]
    return flatten_task_result(post_dfslabs("domain_intersection", payload))

# Extract keywords from each competitor
comp_kw_frames = []
print(f"\nExtracting keywords from {len(comp_domains)} competitors...")

for domain in tqdm(comp_domains, desc="Analyzing competitors"):
    try:
        # Get their ranked keywords
        df = ranked_keywords(domain, country_code, language_name, limit=5000)
        if not df.empty:
            df["source"] = f"competitor_{domain}"
            df["source_domain"] = domain
            comp_kw_frames.append(df)
        
        # If you have your own domain, find gaps
        if CONFIG["seed"]["your_domain"] and len(comp_kw_frames) < 5:  # Limit gap analysis
            try:
                gap_df = domain_intersection(
                    CONFIG["seed"]["your_domain"],
                    domain,
                    country_code,
                    language_name
                )
                if not gap_df.empty:
                    gap_df["source"] = f"gap_{domain}"
                    gap_df["source_domain"] = domain
                    gap_df["is_gap"] = True
                    comp_kw_frames.append(gap_df)
            except Exception as e:
                logger.error(f"Gap analysis failed for {domain}: {e}")
                
    except Exception as e:
        logger.error(f"Failed to analyze competitor {domain}: {e}")

# Combine competitor keywords
if comp_kw_frames:
    competitor_kw_df = pd.concat(comp_kw_frames, ignore_index=True)
    
    # Add competitor count per keyword
    keyword_competitor_count = competitor_kw_df.groupby("keyword")["source_domain"].nunique()
    competitor_kw_df = competitor_kw_df.merge(
        keyword_competitor_count.rename("competitor_count"),
        left_on="keyword",
        right_index=True,
        how="left"
    )
    
    print(f"\nTotal competitor keywords found: {len(competitor_kw_df)}")
    print(f"Keywords multiple competitors target: {(competitor_kw_df['competitor_count'] > 1).sum()}")
    
    # Show top gap opportunities if found
    if "is_gap" in competitor_kw_df.columns:
        gap_keywords = competitor_kw_df[competitor_kw_df["is_gap"] == True]
        print(f"Gap keywords found: {len(gap_keywords)}")
else:
    competitor_kw_df = pd.DataFrame()
    print("No competitor keywords found.")
```

---

## 5) Advanced merge, deduplication, and filtering

### **Cell 10 — Merge and enhance all keywords**

```python
# Combine all keyword sources
all_dfs = [seed_keywords_df]
if 'competitor_kw_df' in locals() and not competitor_kw_df.empty:
    all_dfs.append(competitor_kw_df)

master_df = pd.concat(all_dfs, ignore_index=True, sort=False)

# Keep track of all sources for each keyword
source_tracking = master_df.groupby("keyword")["source"].apply(list).to_dict()

# Smart deduplication - keep the row with most data
master_df = master_df.sort_values(
    ["keyword", "search_volume", "keyword_difficulty"], 
    ascending=[True, False, True]
).drop_duplicates(subset=["keyword"], keep="first")

# Add source count
master_df["source_count"] = master_df["keyword"].map(
    lambda x: len(set(source_tracking.get(x, [])))
)

print(f"Total unique keywords before filtering: {len(master_df)}")

# Advanced filtering
def apply_pattern_filters(text: str, patterns: List[str]) -> bool:
    """Check if text matches any exclude patterns"""
    text_lower = text.lower()
    for pattern in patterns:
        if re.search(pattern, text_lower):
            return True
    return False

# Word count filter
master_df["word_count"] = master_df["keyword"].str.split().str.len()

# Apply all filters
filters = CONFIG["filters"]
filtered_df = master_df[
    # Volume filters
    (master_df["search_volume"].fillna(0) >= filters["min_search_volume"]) &
    (master_df["search_volume"].fillna(0) <= filters["max_search_volume"]) &
    
    # CPC filters
    (master_df["cpc"].fillna(0) >= filters["min_cpc_cad"]) &
    (master_df["cpc"].fillna(0) <= filters["max_cpc_cad"]) &
    
    # Difficulty filter
    ((master_df["keyword_difficulty"].isna()) | 
     (master_df["keyword_difficulty"] <= filters["max_keyword_difficulty"])) &
    
    # Word count filters
    (master_df["word_count"] >= filters["min_word_count"]) &
    (master_df["word_count"] <= filters["max_word_count"]) &
    
    # Pattern exclusions
    (~master_df["keyword"].apply(lambda x: apply_pattern_filters(x, filters["exclude_patterns"])))
].copy()

print(f"After filtering: {len(filtered_df)} ({len(filtered_df)/len(master_df)*100:.1f}% retained)")

# Analyze filtered out keywords
filtered_out = master_df[~master_df.index.isin(filtered_df.index)]
print("\nFiltered out reasons:")
print(f"- Low volume: {(filtered_out['search_volume'].fillna(0) < filters['min_search_volume']).sum()}")
print(f"- High volume: {(filtered_out['search_volume'].fillna(0) > filters['max_search_volume']).sum()}")
print(f"- CPC out of range: {((filtered_out['cpc'].fillna(0) < filters['min_cpc_cad']) | (filtered_out['cpc'].fillna(0) > filters['max_cpc_cad'])).sum()}")
print(f"- Too difficult: {(filtered_out['keyword_difficulty'] > filters['max_keyword_difficulty']).sum()}")
print(f"- Excluded patterns: {filtered_out['keyword'].apply(lambda x: apply_pattern_filters(x, filters['exclude_patterns'])).sum()}")
```

### **Cell 11 — Seasonal and trend analysis**

```python
def analyze_seasonality(trend_data):
    """Analyze search volume trends for seasonality"""
    if not isinstance(trend_data, list) or len(trend_data) < 12:
        return {
            "seasonal": False,
            "seasonality_score": 0,
            "peak_months": [],
            "low_months": [],
            "trend_direction": "stable"
        }
    
    trend = np.array(trend_data[-12:])  # Last 12 months
    mean_vol = trend.mean()
    std_vol = trend.std()
    
    # Seasonality score (coefficient of variation)
    seasonality_score = std_vol / mean_vol if mean_vol > 0 else 0
    
    # Find peak and low months
    peak_threshold = mean_vol + std_vol
    low_threshold = mean_vol - std_vol
    
    peak_months = [i for i, v in enumerate(trend) if v > peak_threshold]
    low_months = [i for i, v in enumerate(trend) if v < low_threshold]
    
    # Trend direction (comparing first and last quarters)
    q1_avg = trend[:3].mean()
    q4_avg = trend[-3:].mean()
    if q4_avg > q1_avg * 1.2:
        trend_direction = "growing"
    elif q4_avg < q1_avg * 0.8:
        trend_direction = "declining"
    else:
        trend_direction = "stable"
    
    return {
        "seasonal": seasonality_score > 0.3,
        "seasonality_score": round(seasonality_score, 3),
        "peak_months": peak_months,
        "low_months": low_months,
        "trend_direction": trend_direction
    }

# Apply seasonal analysis
if "search_volume_trend" in filtered_df.columns:
    print("Analyzing seasonality patterns...")
    seasonal_data = filtered_df["search_volume_trend"].apply(analyze_seasonality)
    
    # Unpack seasonal data into columns
    filtered_df["is_seasonal"] = seasonal_data.apply(lambda x: x["seasonal"])
    filtered_df["seasonality_score"] = seasonal_data.apply(lambda x: x["seasonality_score"])
    filtered_df["trend_direction"] = seasonal_data.apply(lambda x: x["trend_direction"])
    filtered_df["peak_months"] = seasonal_data.apply(lambda x: x["peak_months"])
    
    # Summary
    print(f"\nSeasonality analysis:")
    print(f"- Seasonal keywords: {filtered_df['is_seasonal'].sum()}")
    print(f"- Growing trends: {(filtered_df['trend_direction'] == 'growing').sum()}")
    print(f"- Declining trends: {(filtered_df['trend_direction'] == 'declining').sum()}")
```

---

## 6) Enhanced Intent Classification

### Key Improvements:
- Use `/search_intent/live` endpoint for ML-based intent detection
- Validate intent with SERP analysis (commercial intent should have shopping/ads)
- Multi-level intent scoring (primary + secondary intents)
- Custom rules for industry-specific intent patterns

### Implementation Notes:
- Batch keywords (1000 per call) for intent classification
- Filter for commercial/transactional intent
- Consider intent probability scores, not just labels
- Cross-reference with SERP features for validation

---

## 7) Advanced Clustering Strategies

### Hybrid Clustering Approach:
1. **Semantic Clustering** - Group keywords by meaning using embeddings
2. **Category-Based** - Leverage DataForSEO category data
3. **Intent-Based** - Group by user intent patterns
4. **Modifier-Based** - Extract and group by modifiers (near me, best, cheap, etc.)

### Key Features:
- Optimal cluster size detection using silhouette analysis
- Minimum cluster size enforcement
- Hierarchical clustering for better ad group structure
- Match type recommendations per cluster
- Negative keyword extraction from clusters

---

## 8) Multi-Factor Scoring System

### Enhanced Scoring Components:
1. **Search Volume** - Weighted by seasonality trends
2. **Competition Metrics** - CPC, difficulty, competitor count
3. **Business Value** - Intent strength, conversion probability
4. **Opportunity Score** - Gap keywords, trending terms
5. **Geographic Relevance** - Province-specific performance

### Scoring Formula:
```
final_score = (
    volume_score * 0.3 +
    competition_score * 0.25 +
    intent_score * 0.25 +
    trend_score * 0.2
) * difficulty_multiplier * seasonal_adjustment
```

### Prioritization Tiers:
- **Tier 1**: High volume, low difficulty, strong commercial intent
- **Tier 2**: Medium metrics but high opportunity (gaps, trends)
- **Tier 3**: Long-tail with good intent but lower volume
- **Test Group**: High difficulty but high value keywords

---

## 9) Enhanced Export System

### Export Deliverables:

#### 1. **Campaign-Ready Files**
- `ad_groups_tier1.csv` - Ready-to-launch high-priority keywords
- `ad_groups_tier2.csv` - Secondary expansion keywords
- `ad_groups_tier3.csv` - Long-tail opportunities
- `negative_keywords.csv` - Comprehensive negative list with categories

#### 2. **Analytics & Insights**
- `keyword_analytics.xlsx` - Multi-sheet workbook with:
  - Cluster summaries and performance metrics
  - Seasonal trends and forecasts
  - Competitor gap analysis
  - Geographic performance breakdown
- `campaign_recommendations.json` - Structured data for automation

#### 3. **Match Type Strategies**
- Exact match for high-competition terms
- Phrase match for medium-tail keywords
- Modified broad for discovery campaigns

#### 4. **Budget Allocation Guide**
- Recommended bid ranges per cluster
- Monthly budget estimates
- ROI projections based on difficulty tiers

---

## 10) Geographic Expansion Strategy

### Provincial Analysis Features:
- Compare keyword performance across Ontario, BC, and Alberta
- Identify province-specific search terms and modifiers
- Adjust bids based on regional competition levels
- Discover local competitor variations

### Implementation Approach:
1. Run full pipeline for each province
2. Compare metrics across regions
3. Identify location-specific opportunities
4. Create geo-targeted campaign structures
5. Track seasonal variations by province

---

## 11) Automated Monitoring & Refresh System

### Continuous Optimization Features:
1. **Weekly Refresh Pipeline**
   - New keyword discovery from trending topics
   - Competitor movement tracking
   - SERP feature changes monitoring
   - Seasonal trend updates

2. **Alert System**
   - New high-opportunity keywords
   - Competitor strategy changes
   - Significant ranking shifts
   - Emerging search trends

3. **Performance Tracking**
   - Keyword graduation system (move successful keywords up tiers)
   - Difficulty score updates
   - ROI tracking integration
   - Campaign performance feedback loop

---

## 12) Implementation Best Practices & Cost Management

### Technical Guardrails:
- **Rate Limiting**: Implement token bucket algorithm (30 req/sec)
- **Error Handling**: Exponential backoff with circuit breaker
- **Data Validation**: Schema validation for API responses
- **Caching Strategy**: Cache responses for 24 hours to reduce costs

### Cost Optimization:
- **Initial Discovery**: ~$50-100 for 50K keywords
- **Weekly Refresh**: ~$20-30 for updates
- **Cost Reduction Tips**:
  - Use aggressive filtering early
  - Cache historical data
  - Batch similar requests
  - Start with top 1000 keywords for enrichment

### Data Quality Assurance:
- Track keyword sources for attribution
- Maintain version history
- Implement data lineage tracking
- Regular quality audits

---

## Summary: Enterprise-Ready Keyword Research System

This enhanced pipeline provides:

1. **Comprehensive Discovery** - Multiple data sources and competitor analysis
2. **Smart Filtering** - Pattern-based exclusions and intent validation  
3. **Advanced Analytics** - Seasonality, trends, and difficulty scoring
4. **Scalable Architecture** - Rate limiting, caching, and error handling
5. **Actionable Outputs** - Tiered ad groups with match type strategies
6. **Continuous Optimization** - Automated monitoring and refresh cycles

### Next Steps:
1. Set up DataForSEO credentials
2. Configure for your specific industry/niche
3. Run initial discovery batch
4. Review and refine clustering
5. Launch test campaigns with Tier 1 keywords
6. Implement weekly refresh automation

### Expected Outcomes:
- 10-50K qualified keywords depending on niche
- 15-30 optimized ad groups
- 30-50% reduction in irrelevant traffic via negatives
- Clear prioritization for budget allocation
- Ongoing discovery of new opportunities