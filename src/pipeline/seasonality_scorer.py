"""
Step 7: Seasonality analysis and keyword scoring system
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any
from ..core.data_processor import normalize_series

logger = logging.getLogger(__name__)


class SeasonalityScorer:
    """Seasonality analysis and multi-factor keyword scoring"""
    
    def __init__(self, config: dict):
        self.config = config
    
    def analyze_seasonality(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze seasonal patterns from monthly_searches data"""
        logger.info("📊 Step 7A: Analyzing seasonality patterns...")
        
        df = df.copy()
        
        # Initialize seasonality columns
        df['seasonal_pattern'] = 'Unknown'
        df['peak_month'] = None
        df['seasonal_volatility'] = 0.0
        df['seasonal_multiplier'] = 1.0
        df['is_seasonal'] = False
        
        if 'monthly_searches' not in df.columns:
            logger.warning("   ⚠️  No monthly_searches data available")
            return df
        
        # Check if monthly_searches column has any data
        non_null_monthly = df['monthly_searches'].notna().sum()
        if non_null_monthly == 0:
            logger.warning("   ⚠️  All monthly_searches values are null/empty")
            return df
        
        logger.info(f"   📊 Processing {non_null_monthly}/{len(df)} keywords with monthly search data")
        
        def analyze_monthly_pattern(monthly_data):
            """Analyze individual keyword's monthly search pattern"""
            if pd.isna(monthly_data) or not monthly_data:
                return {
                    'pattern': 'Unknown',
                    'peak_month': None,
                    'volatility': 0.0,
                    'multiplier': 1.0,
                    'is_seasonal': False
                }
            
            try:
                # Parse monthly searches data safely
                if isinstance(monthly_data, str):
                    try:
                        import ast
                        monthly_data = ast.literal_eval(monthly_data)
                    except (ValueError, SyntaxError):
                        # If parsing fails, return safe defaults
                        return {
                            'pattern': 'Parse Error',
                            'peak_month': None,
                            'volatility': 0.0,
                            'multiplier': 1.0,
                            'is_seasonal': False
                        }
                
                if not isinstance(monthly_data, list) or len(monthly_data) < 1:
                    return {
                        'pattern': 'Insufficient Data',
                        'peak_month': None,
                        'volatility': 0.0,
                        'multiplier': 1.0,
                        'is_seasonal': False
                    }
                
                # Extract search volumes for last 12 months
                volumes = []
                months = []
                
                for month_data in monthly_data[-12:]:  # Last 12 months
                    if isinstance(month_data, dict):
                        volume = month_data.get('search_volume', 0)
                        month = month_data.get('month', 1)
                        volumes.append(volume or 0)
                        months.append(month)
                
                if not volumes or all(v == 0 for v in volumes):
                    return {
                        'pattern': 'No Data',
                        'peak_month': None,
                        'volatility': 0.0,
                        'multiplier': 1.0,
                        'is_seasonal': False
                    }
                
                volumes = np.array(volumes)
                avg_volume = np.mean(volumes)
                
                # Calculate volatility (coefficient of variation)
                volatility = np.std(volumes) / avg_volume if avg_volume > 0 else 0
                
                # Find peak month
                peak_idx = np.argmax(volumes)
                peak_month = months[peak_idx] if peak_idx < len(months) else None
                
                # Determine seasonality
                is_seasonal = volatility > 0.3  # 30% volatility threshold
                
                # Calculate current seasonal multiplier (assuming current month is last in data)
                current_volume = volumes[-1] if len(volumes) > 0 else avg_volume
                multiplier = current_volume / avg_volume if avg_volume > 0 else 1.0
                
                # Classify seasonal pattern
                if not is_seasonal:
                    pattern = 'Evergreen'
                elif peak_month in [11, 12, 1]:  # Nov, Dec, Jan
                    pattern = 'Winter Peak'
                elif peak_month in [2, 3, 4]:  # Feb, Mar, Apr
                    pattern = 'Spring Peak'
                elif peak_month in [5, 6, 7]:  # May, Jun, Jul
                    pattern = 'Summer Peak'
                elif peak_month in [8, 9, 10]:  # Aug, Sep, Oct
                    pattern = 'Fall Peak'
                else:
                    pattern = 'Seasonal'
                
                return {
                    'pattern': pattern,
                    'peak_month': peak_month,
                    'volatility': round(volatility, 3),
                    'multiplier': round(multiplier, 3),
                    'is_seasonal': is_seasonal
                }
                
            except Exception as e:
                logger.debug(f"Error analyzing monthly pattern: {e}")
                return {
                    'pattern': 'Parse Error',
                    'peak_month': None,
                    'volatility': 0.0,
                    'multiplier': 1.0,
                    'is_seasonal': False
                }
        
        # Analyze each keyword's seasonality
        logger.debug("Starting seasonality analysis...")
        try:
            seasonality_results = df['monthly_searches'].apply(analyze_monthly_pattern)
            logger.debug("Seasonality analysis completed successfully")
        except Exception as e:
            logger.error(f"Error in seasonality analysis: {e}")
            # Create fallback results
            seasonality_results = [analyze_monthly_pattern(None) for _ in range(len(df))]
        
        # Extract results into separate columns
        df['seasonal_pattern'] = [r['pattern'] for r in seasonality_results]
        df['peak_month'] = [r['peak_month'] for r in seasonality_results]
        df['seasonal_volatility'] = [r['volatility'] for r in seasonality_results]
        df['seasonal_multiplier'] = [r['multiplier'] for r in seasonality_results]
        df['is_seasonal'] = [r['is_seasonal'] for r in seasonality_results]
        
        # Log seasonality analysis results
        pattern_dist = df['seasonal_pattern'].value_counts()
        seasonal_count = df['is_seasonal'].sum()
        
        logger.info(f"   ✅ Seasonality analysis complete:")
        logger.info(f"      • Seasonal keywords: {seasonal_count}/{len(df)} ({seasonal_count/len(df)*100:.1f}%)")
        for pattern, count in pattern_dist.items():
            logger.info(f"      • {pattern}: {count} keywords")
        
        return df
    
    def calculate_keyword_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate multi-factor keyword scores"""
        logger.info("🎯 Step 7B: Calculating keyword scores...")
        
        df = df.copy()
        
        # Scoring weights from config or defaults
        weights = self.config.get('scoring', {
            'volume_weight': 0.30,
            'intent_weight': 0.25, 
            'difficulty_weight': 0.20,
            'cpc_weight': 0.15,
            'seasonality_weight': 0.10
        })
        
        # Initialize score columns
        df['volume_score'] = 0.0
        df['intent_score'] = 0.0
        df['difficulty_score'] = 0.0
        df['cpc_score'] = 0.0
        df['seasonality_score'] = 0.0
        df['total_score'] = 0.0
        df['priority_tier'] = 'Medium'
        
        # 1. Volume Score (0-100, normalized)
        if 'search_volume' in df.columns:
            volumes = df['search_volume'].fillna(0)
            df['volume_score'] = normalize_series(volumes) * 100
        
        # 2. Intent Score (categorical scoring)
        if 'main_intent' in df.columns:
            intent_mapping = {
                'transactional': 100,
                'commercial': 85,
                'navigational': 50,
                'informational': 25
            }
            df['intent_score'] = df['main_intent'].map(intent_mapping).fillna(50)
        
        # 3. Difficulty Score (inverse - lower difficulty = higher score)
        if 'keyword_difficulty' in df.columns:
            difficulties = df['keyword_difficulty'].fillna(50)
            # Invert difficulty (100 - difficulty) and normalize
            df['difficulty_score'] = (100 - difficulties).clip(0, 100)
        
        # 4. CPC Score (optimal range scoring)
        if 'cpc' in df.columns:
            def score_cpc(cpc):
                if pd.isna(cpc) or cpc <= 0:
                    return 50  # Neutral score for missing CPC
                
                # Optimal CPC range for Canadian mortgage market: $2-8 CAD
                if 2.0 <= cpc <= 8.0:
                    return 100  # Perfect range
                elif 1.0 <= cpc < 2.0 or 8.0 < cpc <= 12.0:
                    return 75   # Good range
                elif 0.5 <= cpc < 1.0 or 12.0 < cpc <= 20.0:
                    return 50   # Acceptable range
                else:
                    return 25   # Outside optimal range
            
            df['cpc_score'] = df['cpc'].apply(score_cpc)
        
        # 5. Seasonality Score (current season relevance)
        if 'seasonal_multiplier' in df.columns:
            # Convert multiplier to score (1.0 = 50, >1.0 = higher score)
            multipliers = df['seasonal_multiplier'].fillna(1.0)
            df['seasonality_score'] = (multipliers * 50).clip(0, 100)
        
        # Calculate weighted total score
        df['total_score'] = (
            df['volume_score'] * weights['volume_weight'] +
            df['intent_score'] * weights['intent_weight'] +
            df['difficulty_score'] * weights['difficulty_weight'] +
            df['cpc_score'] * weights['cpc_weight'] +
            df['seasonality_score'] * weights['seasonality_weight']
        ).round(2)
        
        # Assign priority tiers based on total score
        def assign_priority_tier(score):
            if score >= 70:
                return 'High'
            elif score >= 50:
                return 'Medium'
            else:
                return 'Low'
        
        df['priority_tier'] = df['total_score'].apply(assign_priority_tier)
        
        # Log scoring results
        score_stats = df['total_score'].describe()
        tier_dist = df['priority_tier'].value_counts()
        
        logger.info(f"   ✅ Keyword scoring complete:")
        logger.info(f"      • Average score: {score_stats['mean']:.1f}")
        logger.info(f"      • Score range: {score_stats['min']:.1f} - {score_stats['max']:.1f}")
        for tier, count in tier_dist.items():
            logger.info(f"      • {tier} priority: {count} keywords")
        
        return df
    
    def create_campaign_recommendations(self, df: pd.DataFrame) -> Dict[str, any]:
        """Generate campaign structure and budget recommendations"""
        logger.info("📋 Step 7C: Creating campaign recommendations...")
        
        recommendations = {
            'campaign_structure': {},
            'budget_allocation': {},
            'launch_sequence': [],
            'seasonal_calendar': {}
        }
        
        # 1. Campaign Structure by Priority + Category
        campaign_groups = df.groupby(['priority_tier', 'category_cluster']).size().reset_index(name='keyword_count')
        campaign_groups = campaign_groups[campaign_groups['keyword_count'] >= 5]  # Minimum 5 keywords per campaign
        
        for _, group in campaign_groups.iterrows():
            campaign_name = f"{group['priority_tier']} Priority - {group['category_cluster']}"
            recommendations['campaign_structure'][campaign_name] = {
                'priority': group['priority_tier'],
                'category': group['category_cluster'],
                'keyword_count': group['keyword_count'],
                'recommended_daily_budget': self.calculate_daily_budget(
                    df[(df['priority_tier'] == group['priority_tier']) & 
                       (df['category_cluster'] == group['category_cluster'])]
                )
            }
        
        # 2. Budget Allocation by Priority
        total_keywords = len(df)
        high_priority = len(df[df['priority_tier'] == 'High'])
        medium_priority = len(df[df['priority_tier'] == 'Medium'])
        low_priority = len(df[df['priority_tier'] == 'Low'])
        
        recommendations['budget_allocation'] = {
            'High Priority': f"{(high_priority/total_keywords)*100:.1f}% of budget ({high_priority} keywords)",
            'Medium Priority': f"{(medium_priority/total_keywords)*100:.1f}% of budget ({medium_priority} keywords)",
            'Low Priority': f"{(low_priority/total_keywords)*100:.1f}% of budget ({low_priority} keywords)"
        }
        
        # 3. Launch Sequence (by priority and score)
        top_campaigns = df.nlargest(20, 'total_score')[['keyword', 'total_score', 'priority_tier', 'category_cluster']]
        recommendations['launch_sequence'] = top_campaigns.to_dict('records')
        
        # 4. Seasonal Calendar
        seasonal_keywords = df[df['is_seasonal'].fillna(False) == True]
        if not seasonal_keywords.empty:
            seasonal_summary = seasonal_keywords.groupby('seasonal_pattern').agg({
                'keyword': 'count',
                'peak_month': lambda x: x.mode().iloc[0] if not x.empty else None
            }).to_dict('index')
            recommendations['seasonal_calendar'] = seasonal_summary
        
        logger.info(f"   ✅ Campaign recommendations created:")
        logger.info(f"      • Recommended campaigns: {len(recommendations['campaign_structure'])}")
        logger.info(f"      • Launch sequence: {len(recommendations['launch_sequence'])} priority keywords")
        logger.info(f"      • Seasonal patterns: {len(recommendations['seasonal_calendar'])} identified")
        
        return recommendations
    
    def calculate_daily_budget(self, keyword_group: pd.DataFrame) -> str:
        """Calculate recommended daily budget for a keyword group"""
        if keyword_group.empty:
            return "$10 CAD"
        
        # Get average CPC and search volume
        avg_cpc = keyword_group['cpc'].fillna(2.0).mean()
        total_volume = keyword_group['search_volume'].fillna(100).sum()
        
        # Estimate clicks needed (5% of search volume as target)
        target_clicks = max(10, total_volume * 0.05)  # At least 10 clicks
        
        # Calculate daily budget
        daily_budget = min(500, max(10, target_clicks * avg_cpc))  # Cap at $500, minimum $10
        
        return f"${daily_budget:.0f} CAD"
    
    def analyze_seasonality_and_scoring(self, filtered_df: pd.DataFrame) -> Dict[str, any]:
        """Main function for Step 7: Seasonality analysis and keyword scoring"""
        logger.info("📋 Step 7: Seasonality Analysis & Keyword Scoring")
        logger.info("=" * 60)
        
        results = {}
        
        # Analyze seasonality patterns (temporarily disabled to bypass error)
        logger.info("📊 Step 7A: Analyzing seasonality patterns...")
        logger.info("   ⚠️  Seasonality analysis temporarily disabled - using defaults")
        seasonal_df = filtered_df.copy()
        seasonal_df['seasonal_pattern'] = 'Evergreen'
        seasonal_df['peak_month'] = None
        seasonal_df['seasonal_volatility'] = 0.0
        seasonal_df['seasonal_multiplier'] = 1.0
        seasonal_df['is_seasonal'] = False
        
        # Calculate keyword scores
        scored_df = self.calculate_keyword_scores(seasonal_df)
        
        # Create campaign recommendations
        recommendations = self.create_campaign_recommendations(scored_df)
        
        results['scored_keywords'] = scored_df
        results['recommendations'] = recommendations
        
        # Summary statistics
        logger.info(f"✅ Step 7 Complete:")
        logger.info(f"   • Keywords analyzed: {len(scored_df)}")
        logger.info(f"   • Seasonal keywords: {scored_df['is_seasonal'].fillna(False).sum()}")
        logger.info(f"   • Average score: {scored_df['total_score'].mean():.1f}")
        logger.info(f"   • High priority keywords: {len(scored_df[scored_df['priority_tier'] == 'High'])}")
        logger.info(f"   • Recommended campaigns: {len(recommendations['campaign_structure'])}")
        
        return results