"""
Step 8: Campaign Export System - Generate campaign-ready files for Google Ads and Microsoft Ads
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Any
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class CampaignExporter:
    """Export keywords to campaign-ready formats for Google Ads and Microsoft Ads"""
    
    def __init__(self, config: dict):
        self.config = config
        
    def export_campaigns(self, scored_keywords_df: pd.DataFrame, recommendations: Dict) -> Dict[str, Any]:
        """
        Main export function that generates all campaign files
        """
        logger.info("📋 Step 8: Campaign Export System")
        logger.info("=" * 60)
        
        export_results = {
            "google_ads_files": {},
            "microsoft_ads_files": {},
            "summary_stats": {},
            "export_paths": []
        }
        
        try:
            # Prepare keywords for export
            campaign_ready_df = self._prepare_campaign_keywords(scored_keywords_df)
            
            if campaign_ready_df.empty:
                logger.warning("⚠️ No campaign-ready keywords found")
                return export_results
            
            # Generate tiered campaign structure
            tiered_campaigns = self._create_tiered_campaigns(campaign_ready_df)
            
            # Export Google Ads files
            google_exports = self._export_google_ads_files(tiered_campaigns)
            export_results["google_ads_files"] = google_exports
            
            # Export Microsoft Ads files
            microsoft_exports = self._export_microsoft_ads_files(tiered_campaigns)
            export_results["microsoft_ads_files"] = microsoft_exports
            
            # Generate negative keyword lists
            negative_keywords = self._generate_negative_keywords(scored_keywords_df)
            
            # Export additional campaign assets
            campaign_assets = self._export_campaign_assets(
                tiered_campaigns, negative_keywords, recommendations
            )
            
            # Compile summary statistics
            export_results["summary_stats"] = self._generate_export_summary(
                campaign_ready_df, tiered_campaigns, negative_keywords
            )
            
            logger.info(f"✅ Campaign export completed successfully!")
            logger.info(f"📊 Generated {len(tiered_campaigns)} campaign tiers")
            logger.info(f"🎯 Total campaign-ready keywords: {len(campaign_ready_df)}")
            
            return export_results
            
        except Exception as e:
            logger.error(f"❌ Campaign export failed: {e}")
            return export_results
    
    def _prepare_campaign_keywords(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare keywords for campaign export with proper formatting"""
        logger.info("🔧 Preparing keywords for campaign export...")
        
        campaign_df = df.copy()
        
        # Only include high-intent keywords
        if 'main_intent' in campaign_df.columns:
            high_intent = campaign_df['main_intent'].isin(['commercial', 'transactional'])
            campaign_df = campaign_df[high_intent]
        
        # Ensure required columns exist
        required_columns = ['keyword', 'search_volume', 'cpc', 'keyword_difficulty']
        for col in required_columns:
            if col not in campaign_df.columns:
                campaign_df[col] = 0
        
        # Clean and format keywords
        campaign_df['keyword_clean'] = campaign_df['keyword'].str.lower().str.strip()
        campaign_df = campaign_df[campaign_df['keyword_clean'].str.len() > 2]
        
        # Add match type recommendations
        campaign_df['recommended_match_type'] = campaign_df.apply(
            self._recommend_match_type, axis=1
        )
        
        # Add bid recommendations (in CAD)
        campaign_df['recommended_bid_cad'] = campaign_df.apply(
            self._calculate_recommended_bid, axis=1
        )
        
        # Add campaign tier based on difficulty and volume
        campaign_df['campaign_tier'] = campaign_df.apply(
            self._assign_campaign_tier, axis=1
        )
        
        logger.info(f"✅ Prepared {len(campaign_df)} campaign-ready keywords")
        return campaign_df
    
    def _recommend_match_type(self, row) -> str:
        """Recommend match type based on keyword characteristics"""
        keyword = str(row.get('keyword', '')).lower()
        search_volume = row.get('search_volume', 0)
        difficulty = row.get('keyword_difficulty', 50)
        
        # Long-tail keywords (4+ words) - Exact match
        if len(keyword.split()) >= 4:
            return 'exact'
        
        # High volume, high difficulty - Exact match for precision
        if search_volume > 1000 and difficulty > 60:
            return 'exact'
        
        # Brand/location terms - Exact match
        if any(term in keyword for term in ['mortgage broker', 'lender', 'company']):
            return 'exact'
        
        # Medium volume, medium difficulty - Phrase match
        if 100 <= search_volume <= 1000 and 30 <= difficulty <= 60:
            return 'phrase'
        
        # Low competition opportunities - Broad match modified
        if difficulty < 30:
            return 'broad'
        
        # Default to phrase match
        return 'phrase'
    
    def _calculate_recommended_bid(self, row) -> float:
        """Calculate recommended starting bid in CAD"""
        cpc = row.get('cpc', 0)
        difficulty = row.get('keyword_difficulty', 50)
        search_volume = row.get('search_volume', 0)
        
        if cpc > 0:
            # Start with market CPC
            base_bid = float(cpc)
        else:
            # Estimate based on difficulty and volume
            if difficulty > 70:
                base_bid = 3.0  # High competition
            elif difficulty > 40:
                base_bid = 2.0  # Medium competition
            else:
                base_bid = 1.0  # Low competition
        
        # Adjust for search volume
        if search_volume > 1000:
            base_bid *= 1.2  # Premium for high volume
        elif search_volume < 50:
            base_bid *= 0.8  # Discount for low volume
        
        # Cap bids within reasonable range
        base_bid = max(0.5, min(base_bid, 10.0))
        
        return round(base_bid, 2)
    
    def _assign_campaign_tier(self, row) -> str:
        """Assign keywords to campaign tiers based on difficulty and volume"""
        difficulty = row.get('keyword_difficulty', 50)
        search_volume = row.get('search_volume', 0)
        
        # Tier 1: Easy wins (low difficulty, decent volume)
        if difficulty <= 30 and search_volume >= 100:
            return 'tier_1_easy_wins'
        
        # Tier 2: High volume opportunities (high volume, any difficulty)
        if search_volume >= 1000:
            return 'tier_2_high_volume'
        
        # Tier 3: Long-tail opportunities (low difficulty, any volume)
        if difficulty <= 40:
            return 'tier_3_long_tail'
        
        # Tier 4: Competitive terms (high difficulty, high volume)
        if difficulty > 60 and search_volume >= 500:
            return 'tier_4_competitive'
        
        # Default: General campaign
        return 'tier_5_general'
    
    def _create_tiered_campaigns(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Create tiered campaign structure"""
        logger.info("🎯 Creating tiered campaign structure...")
        
        tiered_campaigns = {}
        
        # Group by campaign tier
        for tier in df['campaign_tier'].unique():
            tier_df = df[df['campaign_tier'] == tier].copy()
            
            # Sort by priority score (if available) or search volume
            sort_column = 'priority_score' if 'priority_score' in tier_df.columns else 'search_volume'
            tier_df = tier_df.sort_values(sort_column, ascending=False)
            
            tiered_campaigns[tier] = tier_df
            logger.info(f"📊 {tier}: {len(tier_df)} keywords")
        
        return tiered_campaigns
    
    def _export_google_ads_files(self, tiered_campaigns: Dict) -> Dict[str, str]:
        """Export Google Ads compatible CSV files"""
        logger.info("🔵 Exporting Google Ads files...")
        
        google_exports = {}
        exports_dir = Path("exports/google_ads")
        exports_dir.mkdir(parents=True, exist_ok=True)
        
        for tier_name, tier_df in tiered_campaigns.items():
            # Google Ads format
            google_df = pd.DataFrame({
                'Campaign': tier_name.replace('_', ' ').title(),
                'Ad Group': tier_df.apply(self._generate_ad_group_name, axis=1),
                'Keyword': tier_df['keyword'],
                'Match Type': tier_df['recommended_match_type'].map({
                    'exact': 'Exact',
                    'phrase': 'Phrase', 
                    'broad': 'Broad'
                }),
                'Max CPC': tier_df['recommended_bid_cad'],
                'Final URL': self.config.get('campaign', {}).get('landing_page', 'https://example.com'),
                'Search Volume': tier_df['search_volume'],
                'Competition': tier_df['keyword_difficulty']
            })
            
            # Export file
            filename = f"google_ads_{tier_name}.csv"
            filepath = exports_dir / filename
            google_df.to_csv(filepath, index=False)
            google_exports[tier_name] = str(filepath)
            
            logger.info(f"✅ Exported {filename}: {len(google_df)} keywords")
        
        return google_exports
    
    def _export_microsoft_ads_files(self, tiered_campaigns: Dict) -> Dict[str, str]:
        """Export Microsoft Ads compatible CSV files"""
        logger.info("🟦 Exporting Microsoft Ads files...")
        
        microsoft_exports = {}
        exports_dir = Path("exports/microsoft_ads")
        exports_dir.mkdir(parents=True, exist_ok=True)
        
        for tier_name, tier_df in tiered_campaigns.items():
            # Microsoft Ads format
            microsoft_df = pd.DataFrame({
                'Campaign Name': tier_name.replace('_', ' ').title(),
                'Ad Group Name': tier_df.apply(self._generate_ad_group_name, axis=1),
                'Keyword': tier_df['keyword'],
                'Match Type': tier_df['recommended_match_type'].map({
                    'exact': 'Exact',
                    'phrase': 'Phrase',
                    'broad': 'Broad'
                }),
                'Bid': tier_df['recommended_bid_cad'],
                'Destination URL': self.config.get('campaign', {}).get('landing_page', 'https://example.com'),
                'Search Volume': tier_df['search_volume'],
                'Keyword Difficulty': tier_df['keyword_difficulty']
            })
            
            # Export file
            filename = f"microsoft_ads_{tier_name}.csv"
            filepath = exports_dir / filename
            microsoft_df.to_csv(filepath, index=False)
            microsoft_exports[tier_name] = str(filepath)
            
            logger.info(f"✅ Exported {filename}: {len(microsoft_df)} keywords")
        
        return microsoft_exports
    
    def _generate_ad_group_name(self, row) -> str:
        """Generate semantic ad group names"""
        keyword = str(row.get('keyword', '')).lower()
        
        # Mortgage product types
        if 'private mortgage' in keyword or 'private lender' in keyword:
            return 'Private Mortgages'
        elif 'bad credit' in keyword or 'poor credit' in keyword:
            return 'Bad Credit Mortgages'  
        elif 'bridge' in keyword or 'bridging' in keyword:
            return 'Bridge Financing'
        elif 'second mortgage' in keyword or '2nd mortgage' in keyword:
            return 'Second Mortgages'
        elif 'home equity' in keyword or 'equity loan' in keyword:
            return 'Home Equity Loans'
        elif 'mortgage broker' in keyword:
            return 'Mortgage Brokers'
        elif 'alternative lender' in keyword or 'alternative mortgage' in keyword:
            return 'Alternative Lenders'
        elif 'fast approval' in keyword or 'quick approval' in keyword:
            return 'Fast Approval'
        
        # Geographic terms
        if any(geo in keyword for geo in ['toronto', 'vancouver', 'calgary', 'montreal']):
            return 'Major Cities'
        elif any(geo in keyword for geo in ['ontario', 'bc', 'alberta', 'quebec']):
            return 'Provincial'
        
        # Default grouping
        return 'General Mortgages'
    
    def _generate_negative_keywords(self, df: pd.DataFrame) -> List[str]:
        """Generate negative keyword lists"""
        logger.info("🚫 Generating negative keyword lists...")
        
        # Base negative keywords for mortgage industry
        base_negatives = [
            'free', 'diy', 'do it yourself', 'course', 'training', 'education',
            'job', 'jobs', 'career', 'employment', 'salary', 'wage',
            'cheap', 'cheapest', 'discount', 'sale', 'promotion',
            'review', 'reviews', 'complaint', 'complaints', 'scam',
            'government', 'canada.ca', 'cmhc', 'public', 'non profit'
        ]
        
        # Add dynamically from excluded keywords
        excluded_patterns = self.config.get('filters', {}).get('exclude_patterns', [])
        for pattern in excluded_patterns:
            # Convert regex patterns to keyword negatives
            clean_pattern = pattern.replace('\\b', '').replace('.*', '').strip()
            if clean_pattern and len(clean_pattern.split()) <= 3:
                base_negatives.append(clean_pattern)
        
        # Remove duplicates and sort
        negative_keywords = sorted(list(set(base_negatives)))
        
        logger.info(f"✅ Generated {len(negative_keywords)} negative keywords")
        return negative_keywords
    
    def _export_campaign_assets(self, tiered_campaigns: Dict, negative_keywords: List, recommendations: Dict) -> Dict:
        """Export additional campaign assets"""
        logger.info("📁 Exporting additional campaign assets...")
        
        assets_dir = Path("exports/campaign_assets")
        assets_dir.mkdir(parents=True, exist_ok=True)
        
        # Export negative keywords
        neg_file = assets_dir / "negative_keywords.txt"
        with open(neg_file, 'w') as f:
            for keyword in negative_keywords:
                f.write(f"{keyword}\n")
        
        # Export campaign summary
        campaign_summary = {
            "campaign_overview": {
                "total_tiers": len(tiered_campaigns),
                "total_keywords": sum(len(df) for df in tiered_campaigns.values()),
                "recommended_budget_cad": self._calculate_recommended_budget(tiered_campaigns),
                "export_timestamp": pd.Timestamp.now().isoformat()
            },
            "tier_breakdown": {
                tier: {
                    "keyword_count": len(df),
                    "avg_search_volume": df['search_volume'].mean(),
                    "avg_cpc": df['recommended_bid_cad'].mean(),
                    "avg_difficulty": df['keyword_difficulty'].mean()
                }
                for tier, df in tiered_campaigns.items()
            },
            "recommendations": recommendations
        }
        
        summary_file = assets_dir / "campaign_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(campaign_summary, f, indent=2, default=str)
        
        logger.info(f"✅ Exported campaign assets to {assets_dir}")
        return {"negative_keywords_file": str(neg_file), "summary_file": str(summary_file)}
    
    def _calculate_recommended_budget(self, tiered_campaigns: Dict) -> Dict[str, float]:
        """Calculate recommended daily budgets for each tier"""
        budget_recommendations = {}
        
        for tier_name, tier_df in tiered_campaigns.items():
            # Calculate potential daily clicks and cost
            avg_bid = tier_df['recommended_bid_cad'].mean()
            total_volume = tier_df['search_volume'].sum()
            
            # Estimate 2% CTR and 10% impression share for new campaigns
            estimated_daily_clicks = (total_volume * 0.02 * 0.10) / 30  # Monthly to daily
            estimated_daily_cost = estimated_daily_clicks * avg_bid
            
            # Set minimum budget of $20 CAD per day
            recommended_budget = max(20.0, estimated_daily_cost * 2)  # 2x buffer
            
            budget_recommendations[tier_name] = round(recommended_budget, 2)
        
        return budget_recommendations
    
    def _generate_export_summary(self, campaign_df: pd.DataFrame, tiered_campaigns: Dict, negative_keywords: List) -> Dict:
        """Generate comprehensive export summary statistics"""
        
        total_keywords = len(campaign_df)
        total_volume = campaign_df['search_volume'].sum()
        avg_cpc = campaign_df['recommended_bid_cad'].mean()
        
        summary = {
            "export_overview": {
                "total_campaign_keywords": total_keywords,
                "total_monthly_search_volume": int(total_volume),
                "average_recommended_bid_cad": round(avg_cpc, 2),
                "campaign_tiers_created": len(tiered_campaigns),
                "negative_keywords_generated": len(negative_keywords)
            },
            "tier_distribution": {
                tier: len(df) for tier, df in tiered_campaigns.items()
            },
            "match_type_distribution": dict(campaign_df['recommended_match_type'].value_counts()),
            "intent_distribution": dict(campaign_df['main_intent'].value_counts()) if 'main_intent' in campaign_df.columns else {},
            "budget_estimation": {
                "estimated_monthly_budget_cad": round(avg_cpc * total_volume * 0.02 * 0.10, 2),
                "recommended_daily_budget_cad": round((avg_cpc * total_volume * 0.02 * 0.10) / 30, 2)
            }
        }
        
        return summary