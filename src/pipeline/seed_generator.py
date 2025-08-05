"""
Step 3: Seed keyword generation from multiple sources
"""
import pandas as pd
import logging
from collections import defaultdict
from tqdm import tqdm
from typing import Dict

logger = logging.getLogger(__name__)


class SeedGenerator:
    """Generate seed keywords from multiple sources"""
    
    def __init__(self, api_client, config: dict):
        self.api_client = api_client
        self.config = config
    
    def generate_seed_keywords(self, country_code: int, language_name: str) -> pd.DataFrame:
        """Generate seed keywords using professional multi-source discovery"""
        logger.info("📋 Step 3: Professional Multi-Source Keyword Discovery")
        logger.info("=" * 60)
        
        all_keywords = []
        keyword_sources = defaultdict(list)  # Track keyword sources
        
        # 1. Industry Trending Keywords (Professional Method #1)
        logger.info("🔥 Phase 1: Discovering trending industry keywords...")
        try:
            trends_df = self.api_client.top_searches(country_code, language_name, limit=1000)
            if not trends_df.empty:
                # Filter for financial/mortgage related trending terms
                finance_keywords = self._filter_industry_relevant(trends_df, "finance")
                if not finance_keywords.empty:
                    finance_keywords["source"] = "trending_industry"
                    all_keywords.append(finance_keywords)
                    keyword_sources["trending"] = finance_keywords["keyword"].tolist()
                    logger.info(f"   ✅ Found {len(finance_keywords)} trending industry keywords")
                else:
                    logger.info("   ⚠️ No relevant trending keywords found")
            else:
                logger.warning("   ⚠️ No trending data available")
        except Exception as e:
            logger.warning(f"   ⚠️ Trending keywords unavailable: {e}")
        
        # 2. Semantic Expansion (Professional Method #2)
        logger.info("🧠 Phase 2: Semantic keyword expansion...")
        base_terms = ["mortgage", "loan", "lending", "finance", "credit"]
        for base_term in tqdm(base_terms, desc="Semantic expansion"):
            try:
                related_df = self.api_client.related_keywords(
                    base_term, country_code, language_name, depth=2, limit=500
                )
                if not related_df.empty:
                    related_df["source"] = f"semantic_{base_term}"
                    related_df["base_term"] = base_term
                    all_keywords.append(related_df)
                    keyword_sources[f"semantic_{base_term}"] = related_df["keyword"].tolist()
                    logger.info(f"   ✅ '{base_term}': {len(related_df)} semantic keywords")
                else:
                    logger.warning(f"   ⚠️ '{base_term}': No related keywords found")
            except Exception as e:
                logger.error(f"   ❌ Semantic expansion failed for '{base_term}': {e}")
        
        # 3. Seed-Based Discovery (Original Method Enhanced)
        logger.info("🌱 Phase 3: Seed-based keyword discovery...")
        
        # Skip seed-based methods if no business terms provided
        if self.config["seed"]["business_terms"]:
            # 3a. Keyword Ideas (category-based expansion)
            logger.info("🔍 Generating keyword ideas...")
            try:
                ideas_df = self.api_client.keyword_ideas(
                    self.config["seed"]["business_terms"], 
                    country_code, 
                    language_name, 
                    limit=1000
                )
                if not ideas_df.empty:
                    ideas_df["source"] = "ideas"
                    all_keywords.append(ideas_df)
                    keyword_sources["ideas"] = ideas_df["keyword"].tolist()
                    logger.info(f"   ✅ Found {len(ideas_df)} keyword ideas")
                else:
                    logger.warning("   ⚠️ No keyword ideas returned")
            except Exception as e:
                logger.error(f"   ❌ Keyword ideas failed: {e}")
            
            # 3b. Keyword Suggestions (phrase-match)
            logger.info("🔍 Generating keyword suggestions...")
            for seed in tqdm(self.config["seed"]["business_terms"], desc="Processing seeds"):
                try:
                    sug_df = self.api_client.keyword_suggestions(seed, country_code, language_name, limit=500)
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
        else:
            logger.info("🔍 No business terms provided - skipping seed-based discovery")
            logger.info("   💡 Relying on trending keywords, semantic expansion, and competitor analysis")
        
        # 4. Auto-discover competitors from SERP analysis (if enabled)
        logger.info("🏢 Phase 4: Advanced competitor analysis...")
        discovered_competitors = []
        if self.config["seed"].get("enable_competitor_analysis", True):
            logger.info("🔍 Auto-discovering competitors from SERP analysis...")
            discovered_competitors = self._discover_competitors(country_code, language_name)
            
            # 4a. Domain competitors analysis (if we have our own domain)
            your_domain = self.config["seed"].get("your_domain", "")
            if your_domain:
                logger.info(f"🔍 Finding domain competitors for {your_domain}...")
                try:
                    domain_competitors_df = self.api_client.competitors_domain(
                        your_domain, country_code, language_name, limit=50
                    )
                    if not domain_competitors_df.empty and 'target' in domain_competitors_df.columns:
                        domain_competitors = domain_competitors_df['target'].dropna().unique()
                        valid_competitors = [
                            domain for domain in domain_competitors 
                            if self._is_valid_competitor_domain(domain)
                        ]
                        discovered_competitors.extend(valid_competitors)
                        logger.info(f"   ✅ Found {len(valid_competitors)} domain competitors")
                    else:
                        logger.info("   ⚠️ No domain competitors found")
                except Exception as e:
                    logger.error(f"   ❌ Domain competitors analysis failed: {e}")
        else:
            logger.info("🔍 Competitor analysis disabled, skipping auto-discovery")
        
        # Combine manual + discovered competitors
        all_competitor_domains = list(set(
            self.config["seed"]["competitor_domains"] + discovered_competitors
        ))
        
        # 4. Keywords from competitor sites (manual + discovered)
        if all_competitor_domains:
            logger.info(f"🔍 Analyzing {len(all_competitor_domains)} competitor domains...")
            for domain in tqdm(all_competitor_domains, desc="Competitor sites"):
                try:
                    site_df = self.api_client.keywords_for_site(domain, country_code, language_name, limit=2000)
                    if not site_df.empty:
                        source_type = "manual" if domain in self.config["seed"]["competitor_domains"] else "discovered"
                        site_df["source"] = f"competitor_{source_type}_{domain}"
                        site_df["source_domain"] = domain
                        site_df["competitor_type"] = source_type
                        all_keywords.append(site_df)
                        keyword_sources[f"site_{domain}"] = site_df["keyword"].tolist()
                        logger.info(f"   ✅ {domain} ({source_type}): {len(site_df)} keywords")
                    else:
                        logger.warning(f"   ⚠️ {domain}: No keywords returned")
                except Exception as e:
                    logger.error(f"   ❌ Failed to get keywords for {domain}: {e}")
        else:
            logger.info("🔍 No competitor domains available, skipping competitor analysis")
        
        # 5. Deep competitor analysis (if enabled)
        if self.config["seed"].get("enable_deep_analysis", True) and all_competitor_domains:
            logger.info("🏆 Phase 5: Deep competitor keyword extraction...")
            max_competitors = self.config["seed"].get("max_competitors", 5)
            top_competitors = all_competitor_domains[:max_competitors]
            logger.info(f"🔍 Deep analysis of top {len(top_competitors)} competitors...")
            
            for domain in tqdm(top_competitors, desc="Deep competitor analysis"):
                try:
                    # Get all ranked keywords (more comprehensive than keywords_for_site)
                    ranked_df = self.api_client.ranked_keywords(domain, country_code, language_name, limit=3000)
                    if not ranked_df.empty:
                        ranked_df["source"] = f"ranked_keywords_{domain}"
                        ranked_df["source_domain"] = domain
                        all_keywords.append(ranked_df)
                        keyword_sources[f"ranked_{domain}"] = ranked_df["keyword"].tolist()
                        logger.info(f"   ✅ {domain}: {len(ranked_df)} ranked keywords")
                    else:
                        logger.warning(f"   ⚠️ {domain}: No ranked keywords found")
                except Exception as e:
                    logger.error(f"   ❌ Ranked keywords failed for {domain}: {e}")
            
            # 6. Subdomain analysis for comprehensive coverage
            logger.info("🏗️ Phase 6: Subdomain keyword discovery...")
            max_subdomains = self.config["seed"].get("max_subdomains", 3)
            # Analyze subdomains of top competitors
            for domain in top_competitors[:3]:  # Top 3 for subdomain analysis
                try:
                    subdomains_df = self.api_client.subdomains_analysis(domain, country_code, language_name)
                    if not subdomains_df.empty:
                        # Extract keywords from high-performing subdomains
                        if 'subdomain' in subdomains_df.columns:
                            top_subdomains = subdomains_df.head(max_subdomains)['subdomain'].tolist()
                            for subdomain in top_subdomains:
                                try:
                                    sub_keywords_df = self.api_client.keywords_for_site(
                                        subdomain, country_code, language_name, limit=1000
                                    )
                                    if not sub_keywords_df.empty:
                                        sub_keywords_df["source"] = f"subdomain_{subdomain}"
                                        sub_keywords_df["source_domain"] = subdomain
                                        all_keywords.append(sub_keywords_df)
                                        logger.info(f"   ✅ {subdomain}: {len(sub_keywords_df)} keywords")
                                except Exception as e:
                                    logger.error(f"   ❌ Subdomain analysis failed for {subdomain}: {e}")
                        logger.info(f"   ✅ {domain}: Analyzed {len(subdomains_df)} subdomains")
                    else:
                        logger.info(f"   ⚠️ {domain}: No significant subdomains found")
                except Exception as e:
                    logger.error(f"   ❌ Subdomain discovery failed for {domain}: {e}")
        else:
            logger.info("🔍 Deep competitor analysis disabled or no competitors found")
        
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
    
    def _discover_competitors(self, country_code: int, language_name: str, max_competitors: int = 10) -> list:
        """Auto-discover competitor domains from SERP analysis"""
        logger.info("🔍 Discovering competitors from SERP analysis...")
        
        discovered_domains = set()
        
        # Use business terms if available, otherwise use semantic base terms
        if self.config["seed"]["business_terms"]:
            seed_terms = self.config["seed"]["business_terms"][:3]  # Use top 3 terms to avoid over-analysis
        else:
            # Use semantic base terms for competitor discovery when no business terms
            seed_terms = ["mortgage Canada", "private lender", "loan approval"]  # Canadian mortgage context
        
        for seed_term in tqdm(seed_terms, desc="SERP analysis"):
            try:
                # Get SERP competitors for this keyword
                competitors_df = self.api_client.serp_competitors([seed_term], country_code, language_name)
                
                if not competitors_df.empty and 'target' in competitors_df.columns:
                    # Extract domains from competitor analysis
                    competitor_domains = competitors_df['target'].dropna().unique()
                    
                    # Filter for legitimate domains (basic cleaning)
                    for domain in competitor_domains:
                        if isinstance(domain, str) and self._is_valid_competitor_domain(domain):
                            discovered_domains.add(domain)
                            
                    logger.info(f"   ✅ '{seed_term}': Found {len(competitor_domains)} potential competitors")
                else:
                    logger.warning(f"   ⚠️ '{seed_term}': No SERP competitors found")
                    
            except Exception as e:
                logger.error(f"   ❌ SERP analysis failed for '{seed_term}': {e}")
        
        # Limit to top competitors to avoid overwhelming the system
        final_competitors = list(discovered_domains)[:max_competitors]
        
        if final_competitors:
            logger.info(f"🎯 Discovered {len(final_competitors)} competitor domains:")
            for domain in final_competitors:
                logger.info(f"   - {domain}")
        else:
            logger.info("   No valid competitor domains discovered")
            
        return final_competitors
    
    def _is_valid_competitor_domain(self, domain: str) -> bool:
        """Validate if a domain is a legitimate competitor"""
        if not domain or len(domain) < 4:
            return False
            
        # Exclude common non-competitor domains
        excluded_domains = {
            'google.com', 'facebook.com', 'youtube.com', 'linkedin.com', 
            'twitter.com', 'instagram.com', 'wikipedia.org', 'reddit.com',
            'amazon.com', 'ebay.com', 'craigslist.org', 'kijiji.ca'
        }
        
        # Exclude if in common domains list
        if domain.lower() in excluded_domains:
            return False
            
        # Exclude if it's your own domain
        your_domain = self.config["seed"].get("your_domain", "")
        if your_domain and domain.lower() in your_domain.lower():
            return False
            
        # Basic domain format validation
        if '.' not in domain or domain.startswith('.') or domain.endswith('.'):
            return False
            
        return True
    
    def _filter_industry_relevant(self, df: pd.DataFrame, industry: str) -> pd.DataFrame:
        """Filter keywords for industry relevance"""
        if df.empty or 'keyword' not in df.columns:
            return df
        
        # Define industry-specific filter terms
        industry_filters = {
            "finance": [
                "mortgage", "loan", "lend", "credit", "bank", "finance", "debt", 
                "borrow", "payment", "rate", "interest", "refinance", "equity",
                "private", "bridge", "construction", "commercial", "residential",
                "approval", "qualification", "down payment", "amortization"
            ]
        }
        
        if industry not in industry_filters:
            return df
        
        # Create filter pattern
        filter_terms = industry_filters[industry]
        pattern = "|".join([f"\\b{term}\\b" for term in filter_terms])
        
        # Filter keywords that contain industry terms
        mask = df['keyword'].str.contains(pattern, case=False, na=False, regex=True)
        filtered_df = df[mask].copy()
        
        logger.info(f"   📊 Industry filter: {len(filtered_df)}/{len(df)} keywords relevant to {industry}")
        return filtered_df
    
    def generate_seed_keywords_v2(self, country_code: int, language_name: str) -> pd.DataFrame:
        """Improved seed generation with focused discovery"""
        logger.info("🎯 Step 3v2: Focused Intent-Based Keyword Discovery")
        logger.info("=" * 60)
        
        all_keywords = []
        
        # Step 1: Keyword Ideas (Primary Method - Dynamic Limits)
        seed_count = len(self.config["seed"]["business_terms"])
        dynamic_limit = self._calculate_dynamic_limit(seed_count)
        
        logger.info("🎯 Phase 1: Keyword Ideas Discovery...")
        logger.info(f"   📊 Using {seed_count} seed(s) with dynamic limit: {dynamic_limit:,}")
        
        if self.config["seed"]["business_terms"]:
            try:
                ideas_df = self.api_client.keyword_ideas(
                    self.config["seed"]["business_terms"], 
                    country_code, 
                    language_name, 
                    limit=dynamic_limit
                )
                if not ideas_df.empty:
                    ideas_df["source"] = "keyword_ideas_v2"
                    all_keywords.append(ideas_df)
                    logger.info(f"   ✅ Found {len(ideas_df)} keyword ideas")
                else:
                    logger.warning("   ⚠️ No keyword ideas returned")
            except Exception as e:
                logger.error(f"   ❌ Keyword ideas failed: {e}")
        else:
            logger.warning("   ⚠️ No business terms configured - skipping keyword ideas")
        
        # Step 2: Trending Keywords (Enhanced for Minimal Seeds)
        trending_enabled = self.config["seed"]["keyword_generation_strategy"]["enable_trending"]
        # Boost trending discovery when using minimal seeds
        if trending_enabled or seed_count <= 2:
            trending_limit = 2000 if seed_count <= 2 else 1000  # More trending for minimal seeds
            logger.info(f"🔥 Phase 2: Enhanced Trending Keywords (limit: {trending_limit:,})...")
            try:
                trends_df = self.api_client.top_searches(
                    country_code, language_name, limit=trending_limit
                )
                if not trends_df.empty:
                    # Filter for finance-related trending terms
                    trends_df = self._filter_finance_relevant(trends_df)
                    if not trends_df.empty:
                        trends_df["source"] = "trending_v2"
                        all_keywords.append(trends_df)
                        logger.info(f"   ✅ Found {len(trends_df)} relevant trending keywords")
                    else:
                        logger.info("   ⚠️ No finance-relevant trending keywords found")
                else:
                    logger.warning("   ⚠️ No trending data available")
            except Exception as e:
                logger.warning(f"   ⚠️ Trending keywords unavailable: {e}")
        
        # Step 3: Keyword Suggestions (Optional)
        if self.config["seed"]["keyword_generation_strategy"]["enable_suggestions"] and self.config["seed"]["business_terms"]:
            logger.info("🔍 Phase 3: Keyword Suggestions...")
            for seed in self.config["seed"]["business_terms"][:5]:  # Limit to top 5 seeds
                try:
                    sug_df = self.api_client.keyword_suggestions(
                        seed, country_code, language_name, limit=500
                    )
                    if not sug_df.empty:
                        sug_df["source"] = f"suggestions_v2_{seed}"
                        sug_df["seed_term"] = seed
                        all_keywords.append(sug_df)
                        logger.info(f"   ✅ '{seed}': {len(sug_df)} suggestions")
                    else:
                        logger.warning(f"   ⚠️ '{seed}': No suggestions")
                except Exception as e:
                    logger.error(f"   ❌ Suggestions failed for '{seed}': {e}")
        
        # Step 4: Related Keywords (Reduced Depth)
        max_depth = self.config["seed"]["keyword_generation_strategy"]["max_depth_related"]
        if max_depth > 0 and self.config["seed"]["business_terms"]:
            logger.info(f"🧠 Phase 4: Related Keywords (depth={max_depth})...")
            for seed in self.config["seed"]["business_terms"][:3]:  # Limit to top 3
                try:
                    related_df = self.api_client.related_keywords(
                        seed, country_code, language_name, depth=max_depth, limit=500
                    )
                    if not related_df.empty:
                        related_df["source"] = f"related_v2_{seed}"
                        related_df["seed_term"] = seed
                        all_keywords.append(related_df)
                        logger.info(f"   ✅ '{seed}': {len(related_df)} related keywords")
                    else:
                        logger.warning(f"   ⚠️ '{seed}': No related keywords")
                except Exception as e:
                    logger.error(f"   ❌ Related keywords failed for '{seed}': {e}")
        
        # Step 5: SERP-based competitor discovery
        discovered_competitors = []
        if self.config["seed"]["auto_discover_competitors"]:
            logger.info("🏢 Phase 5: Auto-Discover Competitors...")
            # Use seed keywords from phases 1-4 for SERP discovery
            seed_keywords_for_discovery = []
            if all_keywords:
                # Get initial keywords for competitor discovery
                initial_df = pd.concat(all_keywords, ignore_index=True)
                seed_keywords_for_discovery = list(initial_df["keyword"].head(3))
            else:
                # Fallback to business terms
                seed_keywords_for_discovery = self.config["seed"]["business_terms"]
            
            discovered_competitors = self.serp_discover_competitors(seed_keywords_for_discovery, country_code, language_name)
        
        # Step 6: Competitor keywords
        all_competitor_domains = list(set(
            self.config["seed"]["competitor_domains"] + discovered_competitors
        ))
        
        if all_competitor_domains:
            # Enhanced competitor analysis for minimal seeds
            competitor_limit = 2000 if seed_count <= 2 else 1000  # More keywords per competitor for minimal seeds
            max_competitors = 15 if seed_count <= 2 else 10  # Analyze more competitors for minimal seeds
            
            logger.info(f"🔍 Phase 6: Enhanced Competitor Analysis (limit: {competitor_limit:,}/domain)...")
            logger.info(f"   📊 Analyzing {min(len(all_competitor_domains), max_competitors)} competitors for minimal seed approach")
            
            for domain in all_competitor_domains[:max_competitors]:
                try:
                    # Use the improved ranked_keywords method for better results
                    ranked_df = self.api_client.ranked_keywords(domain, country_code, language_name, limit=competitor_limit)
                    if not ranked_df.empty:
                        ranked_df["source"] = f"competitor_v2_{domain}"
                        ranked_df["source_domain"] = domain
                        all_keywords.append(ranked_df)
                        logger.info(f"   ✅ {domain}: {len(ranked_df)} keywords")
                    else:
                        logger.warning(f"   ⚠️ {domain}: No keywords")
                except Exception as e:
                    logger.error(f"   ❌ Failed for {domain}: {e}")
        
        # Combine and process results
        if all_keywords:
            seed_keywords_df = pd.concat(all_keywords, ignore_index=True)
            
            # Apply early filtering if enabled
            if self.config["seed"]["keyword_generation_strategy"]["early_filtering"]:
                seed_keywords_df = self.apply_early_filtering(seed_keywords_df)
            
            # Deduplication
            seed_keywords_df = seed_keywords_df.drop_duplicates(subset=["keyword"], keep="first")
            
            # Enhanced reporting for minimal seed approach
            total_keywords = len(seed_keywords_df)
            keywords_per_seed = total_keywords / seed_count if seed_count > 0 else 0
            
            logger.info(f"✅ Total unique keywords discovered: {total_keywords:,}")
            logger.info(f"🎯 Discovery efficiency: {keywords_per_seed:,.0f} keywords per seed")
            logger.info(f"📈 Dynamic limit used: {dynamic_limit:,} (vs standard 2,000)")
            
            logger.info("📊 Sources breakdown:")
            source_counts = seed_keywords_df["source"].value_counts().head(10)
            for source, count in source_counts.items():
                logger.info(f"   - {source}: {count:,} keywords")
            
            return seed_keywords_df
        else:
            raise ValueError("No keywords generated. Check configuration and API credentials.")
    
    def serp_discover_competitors(self, seed_keywords_list: list, country_code: int, language_name: str):
        """Discover competitors from SERP data using quality seed keywords"""
        logger.info("🔍 Auto-discovering competitors from SERP data...")
        logger.info(f"🔍 Finding SERP competitors for {len(seed_keywords_list)} keywords...")
        
        try:
            # Use seed keywords for SERP competitor discovery
            serp_competitors_df = self.api_client.serp_competitors(seed_keywords_list, country_code, language_name)
            
            if serp_competitors_df.empty:
                logger.warning("   ⚠️ No SERP competitors found")
                return []
            
            logger.info(f"✅ Found {len(serp_competitors_df)} competitor entries")
            
            # Filter out unwanted domains
            exclude_domains = ["google.com", "youtube.com", "facebook.com", "amazon.com", "wikipedia.org", "linkedin.com"]
            your_domain = self.config["seed"].get("your_domain", "")
            
            if your_domain:
                exclude_domains.append(your_domain.lower())
            
            filtered_competitors = serp_competitors_df[
                ~serp_competitors_df.get("domain", pd.Series()).str.lower().isin(exclude_domains)
            ].copy()
            
            logger.info(f"✅ Filtered competitors: {len(filtered_competitors)} domains remaining")
            
            if filtered_competitors.empty:
                logger.warning("   ⚠️ No valid competitors after filtering")
                return []
            
            # Score competitors by multiple factors
            from ..utils.data_processing import normalize_series
            
            if all(col in filtered_competitors.columns for col in ["etv", "count"]):
                filtered_competitors["competitor_score"] = (
                    normalize_series(filtered_competitors["etv"]) * 0.4 +
                    normalize_series(filtered_competitors["count"]) * 0.3 +
                    normalize_series(filtered_competitors.get("metrics.organic.pos_1", pd.Series([0]*len(filtered_competitors)))) * 0.3
                )
            else:
                # Fallback scoring based on available columns
                filtered_competitors["competitor_score"] = normalize_series(filtered_competitors.get("count", pd.Series([1]*len(filtered_competitors))))
            
            # Select top competitors
            max_competitors = self.config["seed"].get("max_auto_competitors", 30)
            top_competitors = filtered_competitors.nlargest(max_competitors, "competitor_score")
            competitor_domains = top_competitors["domain"].tolist()
            
            logger.info(f"   ✅ Discovered {len(competitor_domains)} competitors")
            for domain in competitor_domains[:5]:  # Show first 5
                logger.info(f"      - {domain}")
            
            return competitor_domains
            
        except Exception as e:
            logger.error(f"   ❌ SERP competitor discovery failed: {e}")
            return []
    
    def apply_early_filtering(self, keywords_df: pd.DataFrame):
        """Apply relevance filtering before enrichment"""
        logger.info("🔍 Applying early relevance filtering...")
        
        if keywords_df.empty or 'keyword' not in keywords_df.columns:
            return keywords_df
        
        # Filter by keyword patterns
        finance_patterns = [
            r'\b(mortgage|loan|lender|lending|finance|broker)\b',
            r'\b(private|bridge|hard money|alternative)\b',
            r'\b(canada|toronto|ontario|vancouver|montreal)\b'
        ]
        
        # Must contain at least one finance term and one qualifier
        pattern_mask = keywords_df['keyword'].str.contains(
            '|'.join(finance_patterns[:2]), 
            case=False, 
            regex=True,
            na=False
        )
        
        filtered_df = keywords_df[pattern_mask].copy()
        
        logger.info(f"   📊 Early filtering: {len(filtered_df)}/{len(keywords_df)} keywords retained")
        return filtered_df
    
    def _calculate_dynamic_limit(self, seed_count: int) -> int:
        """Calculate dynamic API limit based on seed count for optimal discovery"""
        # Get base limit from config
        base_keywords_per_seed = self.config.get("discovery_settings", {}).get("keywords_per_seed", 3000)
        
        if seed_count <= 0:
            return 1000  # Fallback for no seeds
        elif seed_count == 1:
            # For single seed, maximize discovery
            return base_keywords_per_seed
        elif seed_count == 2:
            # For two seeds, use 75% of base per seed
            return int(base_keywords_per_seed * 0.75)
        elif seed_count == 3:
            # For three seeds, use 60% of base per seed
            return int(base_keywords_per_seed * 0.6)
        else:
            # For more seeds (legacy), use conservative limit
            return 2000
    
    def _filter_finance_relevant(self, df: pd.DataFrame):
        """Filter trending keywords for finance relevance"""
        if df.empty or 'keyword' not in df.columns:
            return df
            
        finance_terms = [
            "mortgage", "loan", "lend", "credit", "bank", "finance", "debt", 
            "borrow", "payment", "rate", "interest", "refinance", "equity",
            "private", "bridge", "construction", "commercial", "residential",
            "approval", "qualification", "down payment", "amortization",
            "broker", "lender", "lending"
        ]
        
        pattern = "|".join([f"\\b{term}\\b" for term in finance_terms])
        mask = df['keyword'].str.contains(pattern, case=False, na=False, regex=True)
        
        return df[mask].copy()