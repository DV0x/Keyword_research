"""
Step 5: Comprehensive competitor analysis pipeline
"""
import pandas as pd
import logging
from typing import Dict
from urllib.parse import urlparse
from pathlib import Path
from ..core.data_processor import normalize_series

logger = logging.getLogger(__name__)


def clean_domain_name(domain_input: str) -> str:
    """Extract clean domain name from various input formats"""
    if not domain_input:
        return ""
        
    if domain_input.startswith(('http://', 'https://')):
        parsed = urlparse(domain_input)
        return parsed.netloc.replace('www.', '')
    return domain_input.replace('www.', '')


class CompetitorAnalyzer:
    """Comprehensive competitive intelligence and gap analysis"""
    
    def __init__(self, api_client, config: dict):
        self.api_client = api_client
        self.config = config
    
    def analyze_competitors(self, enriched_keywords_df: pd.DataFrame, country_code: int, language_name: str) -> Dict:
        """
        Main competitor analysis function that orchestrates the complete competitive intelligence pipeline
        """
        logger.info("📋 Step 5: Comprehensive Competitor Analysis")
        logger.info("=" * 60)
        
        competitor_results = {
            "serp_competitors": pd.DataFrame(),
            "competitor_keywords": pd.DataFrame(),
            "gap_analysis": pd.DataFrame(),
            "domain_metrics": pd.DataFrame(),
            "top_competitors": []
        }
        
        try:
            # Phase 1: Identify SERP competitors using high-value keywords
            logger.info("🎯 Phase 1: SERP Competitor Discovery")
            
            # Select high-value keywords for competitor discovery
            high_value_keywords = []
            
            if "search_volume" in enriched_keywords_df.columns and "cpc" in enriched_keywords_df.columns:
                # Use volume and CPC criteria  
                high_value_df = enriched_keywords_df[
                    (enriched_keywords_df["search_volume"].fillna(0) > 100) & 
                    (enriched_keywords_df["cpc"].fillna(0) > 1.0)
                ].nlargest(200, "search_volume")
                high_value_keywords = high_value_df["keyword"].tolist()
            
            if not high_value_keywords:
                # Fallback to top volume keywords
                high_value_keywords = enriched_keywords_df.nlargest(200, "search_volume")["keyword"].tolist()
            
            logger.info(f"   🔍 Analyzing {len(high_value_keywords)} high-value keywords for competitors")
            
            # Find SERP competitors
            serp_competitors_df = self.api_client.serp_competitors(high_value_keywords, country_code, language_name)
            competitor_results["serp_competitors"] = serp_competitors_df
            
            if serp_competitors_df.empty:
                logger.warning("⚠️ No SERP competitors found. Skipping detailed competitor analysis.")
                return competitor_results
            
            # Phase 2: Filter and score competitors
            logger.info("🎯 Phase 2: Competitor Filtering & Scoring")
            
            # Clean competitor list
            exclude_domains = ["google.com", "youtube.com", "facebook.com", "amazon.com", "wikipedia.org", "linkedin.com"]
            your_domain = self.config["seed"].get("your_domain", "")
            
            if your_domain:
                exclude_domains.append(your_domain.lower())
                logger.info(f"   📝 Excluding your domain: {your_domain}")
            
            filtered_competitors = serp_competitors_df[
                ~serp_competitors_df.get("domain", pd.Series()).str.lower().isin(exclude_domains)
            ].copy()
            
            if filtered_competitors.empty:
                logger.warning("⚠️ No valid competitors after filtering")
                return competitor_results
            
            # Score competitors by multiple factors
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
            top_competitors = filtered_competitors.nlargest(15, "competitor_score")
            competitor_domains = top_competitors["domain"].tolist()
            competitor_results["top_competitors"] = competitor_domains
            
            logger.info(f"✅ Identified {len(competitor_domains)} top competitors:")
            for i, domain in enumerate(competitor_domains[:10], 1):
                score = top_competitors[top_competitors["domain"] == domain]["competitor_score"].iloc[0]
                logger.info(f"   {i:2d}. {domain} (score: {score:.3f})")
            
            # Phase 3: Extract competitor keywords (now with improved ranked_keywords method)
            logger.info("🎯 Phase 3: Competitor Keyword Extraction")
            
            comp_keyword_frames = []
            
            for i, domain in enumerate(competitor_domains[:10], 1):  # Limit to top 10 for API cost control
                logger.info(f"   📊 Analyzing competitor {i}/{min(10, len(competitor_domains))}: {domain}")
                
                # Clean domain name for API calls
                clean_domain = clean_domain_name(domain)
                logger.info(f"      🔧 Using cleaned domain: {clean_domain}")
                
                try:
                    # Get actual ranking keywords (what they rank for in organic search)
                    ranked_kw_df = self.api_client.ranked_keywords(clean_domain, country_code, language_name, limit=1000)
                    
                    if not ranked_kw_df.empty:
                        ranked_kw_df["competitor_domain"] = domain
                        ranked_kw_df["analysis_type"] = "ranked_keywords"
                        comp_keyword_frames.append(ranked_kw_df)
                        logger.info(f"      ✅ Extracted {len(ranked_kw_df)} ranking keywords from {domain}")
                        
                        # Log some sample keywords with ranking data for visibility
                        if 'keyword' in ranked_kw_df.columns:
                            logger.info(f"      📝 Top ranking keywords from {domain}:")
                            for idx, row in ranked_kw_df.head(3).iterrows():
                                keyword = row.get('keyword', 'N/A')
                                volume = row.get('keyword_search_volume', 'N/A')
                                rank = 'N/A'
                                
                                # Extract ranking position
                                serp_element = row.get('ranked_serp_element')
                                if isinstance(serp_element, dict):
                                    serp_item = serp_element.get('serp_item', {})
                                    rank = serp_item.get('rank_group', 'N/A')
                                
                                logger.info(f"         • '{keyword}' (rank: {rank}, volume: {volume})")
                    else:
                        logger.warning(f"      ⚠️ No ranking keywords found for {domain}")
                    
                    # Gap analysis (if your domain is specified)
                    if your_domain and i <= 5:  # Limit gap analysis to top 5 competitors
                        clean_your_domain = clean_domain_name(your_domain)
                        gap_df = self.api_client.domain_intersection(clean_your_domain, clean_domain, country_code, language_name)
                        
                        if not gap_df.empty:
                            gap_df["competitor_domain"] = domain
                            gap_df["analysis_type"] = "gap_analysis"
                            gap_df["is_gap_opportunity"] = True
                            comp_keyword_frames.append(gap_df)
                            logger.info(f"      ✅ Found {len(gap_df)} gap opportunities")
                    
                except Exception as e:
                    logger.error(f"      ❌ Failed to analyze {domain}: {e}")
                    continue
            
            # Phase 4: Consolidate competitor data
            if comp_keyword_frames:
                logger.info("🎯 Phase 4: Data Consolidation")
                
                competitor_keywords_df = pd.concat(comp_keyword_frames, ignore_index=True, sort=False)
                competitor_results["competitor_keywords"] = competitor_keywords_df
                
                # Add competitor frequency analysis
                if "keyword" in competitor_keywords_df.columns:
                    keyword_competitor_count = competitor_keywords_df.groupby("keyword")["competitor_domain"].nunique()
                    competitor_keywords_df = competitor_keywords_df.merge(
                        keyword_competitor_count.rename("competitor_frequency"),
                        left_on="keyword",
                        right_index=True,
                        how="left"
                    )
                    
                    # Separate gap analysis
                    gap_keywords = competitor_keywords_df[
                        competitor_keywords_df.get("is_gap_opportunity", False) == True
                    ]
                    competitor_results["gap_analysis"] = gap_keywords
                    
                    logger.info(f"✅ Consolidated {len(competitor_keywords_df):,} competitor keyword entries")
                    logger.info(f"   📊 Gap opportunities: {len(gap_keywords):,}")
                    logger.info(f"   📊 Multi-competitor keywords: {(keyword_competitor_count > 1).sum():,}")
                
            else:
                logger.warning("⚠️ No competitor keyword data collected")
            
            # Phase 5: Domain strength analysis
            logger.info("🎯 Phase 5: Domain Strength Analysis")
            
            domain_metrics_frames = []
            for domain in competitor_domains[:5]:  # Top 5 for detailed analysis
                try:
                    clean_domain = clean_domain_name(domain)
                    domain_overview = self.api_client.domain_rank_overview(clean_domain, country_code, language_name)
                    if not domain_overview.empty:
                        domain_overview["analyzed_domain"] = domain
                        domain_metrics_frames.append(domain_overview)
                        logger.info(f"   ✅ Got domain metrics for {domain}")
                except Exception as e:
                    logger.error(f"   ❌ Domain analysis failed for {domain}: {e}")
            
            if domain_metrics_frames:
                competitor_results["domain_metrics"] = pd.concat(domain_metrics_frames, ignore_index=True)
            
            logger.info("✅ Competitor analysis completed successfully!")
            
            # Summary statistics
            logger.info("📊 Competitor Analysis Summary:")
            logger.info(f"   • SERP competitors identified: {len(serp_competitors_df):,}")
            logger.info(f"   • Top competitors selected: {len(competitor_domains)}")
            logger.info(f"   • Competitor keywords collected: {len(competitor_results['competitor_keywords']):,}")
            logger.info(f"   • Gap opportunities found: {len(competitor_results['gap_analysis']):,}")
            logger.info(f"   • Domain metrics collected: {len(competitor_results['domain_metrics']):,}")
            
            return competitor_results
            
        except Exception as e:
            logger.error(f"❌ Competitor analysis failed: {e}")
            return competitor_results