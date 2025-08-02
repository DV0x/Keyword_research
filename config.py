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
        "min_search_volume": 200,
        "max_search_volume": 50000,  # Avoid overly broad terms
        "min_cpc_cad": 0.5,  # Minimum CPC (too low = low commercial intent)
        "max_cpc_cad": 20.0,
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