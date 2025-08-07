import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

CONFIG = {
    "campaign_name": "Private lending",  # Campaign organization name
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
        "language": "en",  # Use ISO language code
        "provinces": ["Ontario,Canada", "British Columbia,Canada", "Alberta,Canada", "Quebec,Canada", "Saskatchewan,Canada", "Manitoba,Canada", "New Brunswick,Canada", "Newfoundland and Labrador,Canada", "Nova Scotia,Canada", "Prince Edward Island,Canada", "Northwest Territories,Canada", "Nunavut,Canada", "Yukon,Canada"],
        "analyze_provinces": True  # Set False to skip province-level analysis
    },
    "seed": {
        "business_terms": [
            "private mortgage",
            "bridge loan",
            "short-term financing" # Professional minimal seed approach
        ],
        "competitor_domains": [
            
        ],  # Known Canadian mortgage competitors for discovery
        "your_domain": "https://www.theratefinder.ca/",  # Your domain for gap analysis (enables domain competitor discovery)
        "enable_competitor_analysis": True,  # Auto-discover competitors from SERP analysis
        "enable_deep_analysis": True,  # Enable ranked keywords & subdomain analysis
        "max_competitors": 5,  # Reduced for testing
        "max_subdomains": 2,  # Reduced for testing
        "auto_discover_competitors": True,  # Enable automatic competitor discovery
        "max_auto_competitors": 30,         # Limit for auto-discovered competitors
        "competitor_discovery_keywords": [  # Keywords for finding competitors
            "private mortgage canada",
            "bridge loan canada",
            "alternative mortgage lender"
        ],
        "keyword_generation_strategy": {
            "primary_method": "keyword_ideas",      # Use category-based expansion
            "enable_trending": True,                # Include top_searches
            "enable_suggestions": True,             # Long-tail variants
            "max_depth_related": 1,                 # Reduce semantic depth
            "early_filtering": True                 # Filter before enrichment
        }
    },
    "filters": {
        "min_search_volume": 50,   # Lowered from 200 to capture more opportunities
        "max_search_volume": 50000,  # Avoid overly broad terms
        "min_cpc_cad": 0.10,  # Lowered from 0.50 to include more keywords
        "max_cpc_cad": 50.0,
        "max_keyword_difficulty": 70,  # 0-100 scale
        "exclude_patterns": [
            r"\b(jobs?|careers?|salary|salaries|hiring|employment)\b",
            r"\b(definition|meaning|what is|what are|how to become)\b",
            r"\b(course|training|certification|school|university)\b",
            r"\b(free|diy|yourself)\b"
        ],
        "allowed_intents": ["commercial", "transactional", "navigational"],  # Include navigational for minimal seed discovery
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
        "volume_weight": 0.30,      # Search volume importance
        "intent_weight": 0.25,      # Commercial intent value  
        "difficulty_weight": 0.20,  # Ranking difficulty (inverse)
        "cpc_weight": 0.15,         # CPC value optimization
        "seasonality_weight": 0.10  # Current season relevance
    },
    "export": {
        "dir": f"exports/{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "formats": ["csv", "parquet", "json"],
        "difficulty_tiers": {
            "easy": (0, 30),
            "medium": (30, 60),
            "hard": (60, 100)
        }
    },
    "discovery_settings": {
        "min_seeds": 1,
        "max_seeds": 3,
        "keywords_per_seed": 3000,  # Increased from 2000 for better discovery
        "enable_progressive_expansion": True,
        "expansion_rounds": 2
    },
    "campaign": {
        "landing_page": "https://yourmortgagesite.com",  # Default landing page
        "business_name": "Your Mortgage Company",
        "min_daily_budget_cad": 20.0,  # Minimum daily budget per campaign
        "max_daily_budget_cad": 70.0,  # Maximum daily budget per campaign
        "target_impression_share": 0.10,  # 10% impression share target for new campaigns
        "target_ctr": 0.02  # 2% CTR assumption for budget calculations
    }
}