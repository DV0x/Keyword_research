"""
DataForSEO API client with rate limiting and error handling
"""
import base64
import json
import time
import requests
import logging
import pandas as pd
from typing import List, Dict
from .rate_limiter import rate_limited
from .data_processor import flatten_task_result

logger = logging.getLogger(__name__)


class DataForSEOClient:
    """DataForSEO API client with built-in rate limiting and error handling"""
    
    def __init__(self, config: dict):
        self.config = config
        self.base_url = config["dataforseo"]["base"]
        self.auth_header = {
            "Authorization": "Basic " + base64.b64encode(
                f'{config["dataforseo"]["login"]}:{config["dataforseo"]["password"]}'.encode()
            ).decode(),
            "Content-Type": "application/json"
        }
        # Apply rate limiting to the method
        rate_limit = config["dataforseo"]["rate_limit"]
        self.post_dfslabs = rate_limited(rate_limit)(self._post_dfslabs_impl)
    
    def _post_dfslabs_impl(self, endpoint: str, payload: List[dict], retries: int = None) -> dict:
        """Enhanced API call with retry logic and rate limiting"""
        if retries is None:
            retries = self.config["dataforseo"]["retries"]
        
        url = f"{self.base_url}/dataforseo_labs/google/{endpoint}/live"
        
        for attempt in range(retries):
            try:
                response = requests.post(
                    url, 
                    headers=self.auth_header, 
                    json=payload,
                    timeout=self.config["dataforseo"]["timeout"]
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
    
    def get_all_locations(self) -> Dict[str, int]:
        """Get all available location codes"""
        url = f"{self.base_url}/dataforseo_labs/locations_and_languages"
        response = requests.get(url, headers=self.auth_header, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        if data.get("status_code") != 20000:
            raise RuntimeError("Could not fetch locations")
        
        locations = {}
        for task in data.get("tasks", []):
            for loc in task.get("result", []):
                locations[loc["location_name"]] = loc["location_code"]
        
        return locations
    
    def keyword_ideas(self, seeds: List[str], location_code: int, language_name: str, limit=500):
        """Get keyword ideas from seed terms"""
        try:
            payload = [{
                "keywords": seeds[:200],  # max 200 per call
                "location_code": location_code,
                "language_code": language_name,  # Changed to language_code
                "limit": limit,
                "include_seed_keyword": True,
                "include_serp_info": False
            }]
            result = self.post_dfslabs("keyword_ideas", payload)
            if result is None:
                return pd.DataFrame()
            return flatten_task_result(result)
        except Exception as e:
            logger.warning(f"keyword_ideas API failed: {e}")
            return pd.DataFrame()
    
    def keyword_suggestions(self, seed: str, location_code: int, language_name: str, limit=500):
        """Get keyword suggestions containing the seed phrase"""
        payload = [{
            "keyword": seed,
            "location_code": location_code,
            "language_code": language_name,  # Changed to language_code
            "limit": limit,
            "include_seed_keyword": True
        }]
        return flatten_task_result(self.post_dfslabs("keyword_suggestions", payload))
    
    def keyword_overview(self, keywords: List[str], location_code: int, language_name: str):
        """Get comprehensive keyword metrics including SERP features"""
        payload = [{
            "keywords": keywords[:700],  # max 700 per call
            "location_code": location_code,
            "language_name": language_name,
            "include_serp_info": True,
            "include_clickstream_data": False  # Set True if you have access
        }]
        return flatten_task_result(self.post_dfslabs("keyword_overview", payload))
    
    def keywords_for_site(self, domain: str, location_code: int, language_name: str, limit=1000):
        """Get keywords a domain ranks for"""
        payload = [{
            "target": domain,
            "location_code": location_code,
            "language_code": language_name,  # Expects language_code with ISO code like "en"
            "limit": limit,
            "include_subdomains": True
        }]
        
        result = self.post_dfslabs("keywords_for_site", payload)
        
        # Check for task-level errors
        if result and result.get('tasks'):
            task = result['tasks'][0]
            if task.get('status_code') != 20000:
                logger.warning(f"Task error for {domain}: {task.get('status_code')} - {task.get('status_message')}")
                return pd.DataFrame()  # Return empty DataFrame for task errors
        
        return flatten_task_result(result)
    
    def bulk_keyword_difficulty(self, keywords: List[str], location_code: int, language_name: str):
        """Get keyword difficulty scores"""
        payload = [{
            "keywords": keywords[:1000],  # max 1000 per call
            "location_code": location_code,
            "language_name": language_name
        }]
        return flatten_task_result(self.post_dfslabs("bulk_keyword_difficulty", payload))
    
    def historical_keyword_data(self, keywords: List[str], location_code: int, language_name: str):
        """Get historical search volume data"""
        payload = [{
            "keywords": keywords[:700],
            "location_code": location_code,
            "language_name": language_name
        }]
        return flatten_task_result(self.post_dfslabs("historical_keyword_data", payload))
    
    def related_keywords(self, keyword: str, location_code: int, language_name: str, depth: int = 2, limit: int = 1000):
        """Get related keywords using depth-first search"""
        logger.info(f"🔍 Finding related keywords for '{keyword}'...")
        
        payload = [{
            "keyword": keyword,
            "location_code": location_code,
            "language_code": language_name,  # Changed to language_code
            "depth": depth,  # 0-4, higher = more related terms
            "limit": limit,
            "include_seed_keyword": True
        }]
        
        try:
            return flatten_task_result(self.post_dfslabs("related_keywords", payload))
        except Exception as e:
            logger.error(f"❌ Related keywords failed for '{keyword}': {e}")
            import pandas as pd
            return pd.DataFrame()
    
    def top_searches(self, location_code: int, language_name: str, limit: int = 1000):
        """Get top trending searches in location"""
        logger.info(f"🔍 Getting top searches for location {location_code}...")
        
        payload = [{
            "location_code": location_code,
            "language_code": language_name,  # Changed to language_code
            "limit": limit
        }]
        
        try:
            result = self.post_dfslabs("top_searches", payload)
            if result is None:
                return pd.DataFrame()
            return flatten_task_result(result)
        except Exception as e:
            logger.warning(f"top_searches API failed: {e}")
            return pd.DataFrame()
    
    def serp_competitors(self, keywords: List[str], location_code: int, language_name: str):
        """Find domains competing for the same keywords in SERP"""
        logger.info(f"🔍 Finding SERP competitors for {len(keywords)} keywords...")
        
        # Limit to top keywords to manage API costs
        selected_keywords = keywords[:200] if len(keywords) > 200 else keywords
        
        payload = [{
            "keywords": selected_keywords,
            "location_code": location_code,
            "language_code": language_name,  # Changed to language_code
            "filters": [["median_position", "<=", 20]],  # Top 20 positions
            "limit": 100
        }]
        
        try:
            data = self.post_dfslabs("serp_competitors", payload)
            
            # Check if data is None or empty
            if not data or not isinstance(data, dict):
                logger.warning("⚠️ No data returned from SERP competitors API")
                import pandas as pd
                return pd.DataFrame()
                
            competitors_data = []
            tasks = data.get("tasks", [])
            
            # Ensure tasks is iterable
            if not tasks:
                logger.warning("⚠️ No tasks found in SERP competitors response")
                import pandas as pd
                return pd.DataFrame()
            
            for task in tasks:
                if not task or not isinstance(task, dict):
                    continue
                    
                results = task.get("result", [])
                if not results:
                    continue
                    
                for result in results:
                    if not result or not isinstance(result, dict):
                        continue
                        
                    items = result.get("items", [])
                    if not items:
                        continue
                        
                    for item in items:
                        if item:  # Only add non-None items
                            competitors_data.append(item)
            
            if competitors_data:
                import pandas as pd
                competitors_df = pd.DataFrame(competitors_data)
                logger.info(f"✅ Found {len(competitors_df)} competitor entries")
                return competitors_df
            else:
                logger.warning("⚠️ No SERP competitors found")
                import pandas as pd
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"❌ SERP competitors analysis failed: {e}")
            import pandas as pd
            return pd.DataFrame()
    
    def ranked_keywords(self, domain: str, location_code: int, language_name: str, limit: int = 5000):
        """Get keywords a domain ranks for"""
        # Clean domain - remove www prefix and protocol
        clean_domain = domain.replace('https://', '').replace('http://', '').replace('www.', '').strip().rstrip('/')
        logger.info(f"🔍 Extracting ranked keywords for {domain} (cleaned: {clean_domain})...")
        
        payload = [{
            "target": clean_domain,
            "location_code": location_code,
            "language_code": language_name,  # Changed to language_code
            "limit": limit,
            "filters": [
                ["keyword_data.keyword_info.search_volume", ">=", 10]    # Filter for keywords with decent volume
            ]
        }]
        
        try:
            result = flatten_task_result(self.post_dfslabs("ranked_keywords", payload))
            logger.info(f"✅ Retrieved {len(result)} ranked keywords for {clean_domain}")
            return result
        except Exception as e:
            logger.error(f"❌ Failed to get ranked keywords for {domain}: {e}")
            import pandas as pd
            return pd.DataFrame()
    
    def domain_intersection(self, domain1: str, domain2: str, location_code: int, language_name: str):
        """Find keyword gaps between domains (keywords domain2 has but domain1 doesn't)"""
        logger.info(f"🔍 Finding keyword gaps between {domain1} and {domain2}...")
        
        payload = [{
            "target1": domain1,
            "target2": domain2,
            "location_code": location_code,
            "language_name": language_name,
            "intersections": False,  # Keywords domain2 has but domain1 doesn't
            "limit": 1000
        }]
        
        try:
            return flatten_task_result(self.post_dfslabs("domain_intersection", payload))
        except Exception as e:
            logger.error(f"❌ Domain intersection analysis failed: {e}")
            import pandas as pd
            return pd.DataFrame()
    
    def domain_rank_overview(self, domain: str, location_code: int, language_name: str):
        """Get domain strength metrics and ranking overview"""
        logger.info(f"🔍 Getting domain overview for {domain}...")
        
        payload = [{
            "target": domain,
            "location_code": location_code,
            "language_name": language_name
        }]
        
        try:
            return flatten_task_result(self.post_dfslabs("domain_rank_overview", payload))
        except Exception as e:
            logger.error(f"❌ Domain rank overview failed for {domain}: {e}")
            import pandas as pd
            return pd.DataFrame()
    
    def competitors_domain(self, domain: str, location_code: int, language_name: str, limit: int = 100):
        """Find competitor domains and their shared keywords"""
        logger.info(f"🔍 Finding domain competitors for {domain}...")
        
        payload = [{
            "target": domain,
            "location_code": location_code,
            "language_name": language_name,
            "limit": limit,
            "exclude_top_domains": True,  # Exclude Google, Amazon etc
            "filters": [
                ["metrics.organic.count", ">=", 100],  # Domains with substantial keywords
                "and",
                ["metrics.organic.etv", ">=", 1000]    # Minimum estimated traffic
            ]
        }]
        
        try:
            return flatten_task_result(self.post_dfslabs("competitors_domain", payload))
        except Exception as e:
            logger.error(f"❌ Domain competitors analysis failed for {domain}: {e}")
            import pandas as pd
            return pd.DataFrame()
    
    def page_intersection(self, pages: List[str], location_code: int, language_name: str, limit: int = 1000):
        """Find keywords that specific pages rank for"""
        logger.info(f"🔍 Analyzing page intersection for {len(pages)} pages...")
        
        payload = [{
            "pages": pages[:20],  # Max 20 pages per request
            "location_code": location_code,
            "language_name": language_name,
            "intersection_mode": "union",  # All keywords any page ranks for
            "limit": limit,
            "filters": [
                ["keyword_data.keyword_info.search_volume", ">=", 10]
            ]
        }]
        
        try:
            return flatten_task_result(self.post_dfslabs("page_intersection", payload))
        except Exception as e:
            logger.error(f"❌ Page intersection analysis failed: {e}")
            import pandas as pd
            return pd.DataFrame()
    
    def subdomains_analysis(self, domain: str, location_code: int, language_name: str, limit: int = 100):
        """Analyze subdomains and their keyword performance"""
        logger.info(f"🔍 Analyzing subdomains for {domain}...")
        
        payload = [{
            "target": domain,
            "location_code": location_code,
            "language_name": language_name,
            "limit": limit,
            "filters": [
                ["metrics.organic.count", ">", 50],  # Only subdomains with keywords
                "and",
                ["metrics.organic.etv", ">", 100]    # Minimum estimated traffic
            ]
        }]
        
        try:
            return flatten_task_result(self.post_dfslabs("subdomains", payload))
        except Exception as e:
            logger.error(f"❌ Subdomains analysis failed for {domain}: {e}")
            import pandas as pd
            return pd.DataFrame()
    
    def categories_for_keywords(self, keywords: List[str], language_name: str):
        """Get category IDs for keywords to understand categorization"""
        logger.info(f"🔍 Getting categories for {len(keywords)} keywords...")
        
        payload = [{
            "keywords": keywords[:1000],  # Max 1000 keywords
            "language_name": language_name
        }]
        
        try:
            return flatten_task_result(self.post_dfslabs("categories_for_keywords", payload))
        except Exception as e:
            logger.error(f"❌ Categories for keywords failed: {e}")
            import pandas as pd
            return pd.DataFrame()
    
    def serp_competitors_auto(self, keywords: List[str], location_code: int, 
                             language_name: str, exclude_domains: List[str] = None):
        """Enhanced SERP competitors with automatic filtering"""
        # Get initial competitors data
        competitors_df = self.serp_competitors(keywords, location_code, language_name)
        
        if not competitors_df.empty and exclude_domains:
            # Filter out major platforms and specified domains
            default_exclude = ['google.com', 'facebook.com', 'wikipedia.org', 
                              'youtube.com', 'amazon.com', 'linkedin.com',
                              'indeed.com', 'glassdoor.com', 'reddit.com']
            all_exclude = default_exclude + (exclude_domains or [])
            
            # Check if 'domain' column exists
            if 'domain' in competitors_df.columns:
                competitors_df = competitors_df[
                    ~competitors_df['domain'].str.lower().isin([d.lower() for d in all_exclude])
                ]
                logger.info(f"✅ Filtered competitors: {len(competitors_df)} domains remaining")
            else:
                logger.warning("⚠️ No 'domain' column found in competitors data")
        
        return competitors_df