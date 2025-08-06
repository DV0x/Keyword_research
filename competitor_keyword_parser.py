#!/usr/bin/env python3
"""
Competitor Keyword Parser for Bidding Optimization
Extracts actionable insights from competitor_keywords_v2.csv for PPC campaigns
"""

import pandas as pd
import json
import numpy as np
from datetime import datetime
import ast

def parse_competitor_keywords(input_file='data/competitor_keywords_v2.csv'):
    """
    Parse competitor keywords CSV and extract bidding-optimized data
    
    Args:
        input_file (str): Path to competitor keywords CSV file
        
    Returns:
        dict: Parsed data ready for campaign creation
    """
    print(f"🔍 Loading competitor keywords from {input_file}...")
    df = pd.read_csv(input_file)
    print(f"📊 Loaded {len(df):,} competitor keywords")
    
    # Extract key bidding metrics
    bidding_data = []
    
    for idx, row in df.iterrows():
        try:
            # Parse monthly searches for trend analysis
            monthly_searches = []
            if pd.notna(row['keyword_monthly_searches']):
                try:
                    monthly_data = ast.literal_eval(row['keyword_monthly_searches'])
                    monthly_searches = [item['search_volume'] for item in monthly_data]
                except:
                    monthly_searches = []
            
            # Parse search volume trend
            trend_data = {'monthly': 0, 'quarterly': 0, 'yearly': 0}
            if pd.notna(row['keyword_search_volume_trend']):
                try:
                    trend_data = ast.literal_eval(row['keyword_search_volume_trend'])
                except:
                    pass
            
            # Extract SERP position from ranked_serp_element
            serp_position = None
            estimated_traffic = 0
            try:
                serp_data = ast.literal_eval(row['ranked_serp_element'])
                if 'serp_item' in serp_data:
                    serp_position = serp_data['serp_item'].get('rank_absolute')
                    estimated_traffic = serp_data['serp_item'].get('etv', 0)
            except:
                pass
            
            keyword_data = {
                'keyword': row['keyword'],
                'competitor_domain': row['competitor_domain'],
                'search_volume': int(row['keyword_search_volume']) if pd.notna(row['keyword_search_volume']) else 0,
                'cpc': float(row['keyword_cpc']) if pd.notna(row['keyword_cpc']) else 0,
                'competition_level': row['keyword_competition_level'],
                'competition_score': float(row['keyword_competition']) if pd.notna(row['keyword_competition']) else 0,
                'low_bid': float(row['keyword_low_top_of_page_bid']) if pd.notna(row['keyword_low_top_of_page_bid']) else 0,
                'high_bid': float(row['keyword_high_top_of_page_bid']) if pd.notna(row['keyword_high_top_of_page_bid']) else 0,
                'difficulty': int(row.get('keyword_difficulty', 0)) if pd.notna(row.get('keyword_difficulty')) else 0,
                'serp_position': serp_position,
                'estimated_traffic': estimated_traffic,
                'monthly_searches': monthly_searches,
                'trend_monthly': trend_data.get('monthly', 0),
                'trend_quarterly': trend_data.get('quarterly', 0),
                'trend_yearly': trend_data.get('yearly', 0),
                'avg_monthly_volume': np.mean(monthly_searches) if monthly_searches else 0,
                'volume_stability': np.std(monthly_searches) if len(monthly_searches) > 1 else 0,
                'last_updated': row['keyword_last_updated_time']
            }
            
            bidding_data.append(keyword_data)
            
        except Exception as e:
            print(f"⚠️  Error parsing row {idx}: {e}")
            continue
    
    df_parsed = pd.DataFrame(bidding_data)
    
    # Generate bidding insights
    insights = generate_bidding_insights(df_parsed)
    
    # Export campaign-ready data
    export_campaign_data(df_parsed, insights)
    
    return {
        'data': df_parsed,
        'insights': insights,
        'total_keywords': len(df_parsed),
        'unique_competitors': df_parsed['competitor_domain'].nunique()
    }

def generate_bidding_insights(df):
    """Generate actionable bidding insights from parsed data"""
    
    insights = {
        'opportunity_analysis': {},
        'competitor_analysis': {},
        'bid_recommendations': {},
        'keyword_tiers': {}
    }
    
    # 1. Opportunity Analysis
    insights['opportunity_analysis'] = {
        'high_volume_low_competition': len(df[
            (df['search_volume'] >= 500) & 
            (df['competition_level'] == 'LOW')
        ]),
        'trending_up_keywords': len(df[df['trend_monthly'] > 20]),
        'stable_high_volume': len(df[
            (df['search_volume'] >= 1000) & 
            (df['volume_stability'] < 200)
        ]),
        'low_difficulty_high_traffic': len(df[
            (df['difficulty'] <= 20) & 
            (df['estimated_traffic'] >= 100)
        ])
    }
    
    # 2. Competitor Analysis
    competitor_stats = df.groupby('competitor_domain').agg({
        'keyword': 'count',
        'search_volume': 'sum',
        'estimated_traffic': 'sum',
        'cpc': 'mean',
        'serp_position': lambda x: (x <= 3).sum()  # Top 3 positions
    }).round(2)
    
    insights['competitor_analysis'] = {
        'top_competitors': competitor_stats.sort_values('estimated_traffic', ascending=False).head(10).to_dict(),
        'avg_keywords_per_competitor': competitor_stats['keyword'].mean(),
        'total_competitor_traffic': competitor_stats['estimated_traffic'].sum()
    }
    
    # 3. Bid Recommendations
    insights['bid_recommendations'] = {
        'easy_wins': df[
            (df['competition_level'] == 'LOW') & 
            (df['search_volume'] >= 100) &
            (df['cpc'] <= 5)
        ][['keyword', 'search_volume', 'cpc', 'low_bid', 'high_bid']].to_dict('records'),
        
        'high_value_targets': df[
            (df['search_volume'] >= 1000) & 
            (df['estimated_traffic'] >= 200) &
            (df['cpc'] <= 15)
        ][['keyword', 'search_volume', 'cpc', 'estimated_traffic', 'competitor_domain']].to_dict('records'),
        
        'trending_opportunities': df[
            (df['trend_monthly'] > 10) & 
            (df['search_volume'] >= 200)
        ][['keyword', 'search_volume', 'trend_monthly', 'cpc']].to_dict('records')
    }
    
    # 4. Keyword Tiers for Campaign Structure
    df['tier'] = pd.cut(
        df['search_volume'], 
        bins=[0, 100, 500, 2000, float('inf')],
        labels=['Tier_4_Long_tail', 'Tier_3_Medium', 'Tier_2_High', 'Tier_1_Premium']
    )
    
    tier_stats = df.groupby('tier').agg({
        'keyword': 'count',
        'search_volume': ['mean', 'sum'],
        'cpc': ['mean', 'median'],
        'competition_level': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'MEDIUM'
    }).round(2)
    
    insights['keyword_tiers'] = tier_stats.to_dict()
    
    return insights

def export_campaign_data(df, insights):
    """Export campaign-ready data files"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    # 1. Bidding-optimized keyword list
    campaign_keywords = df[[
        'keyword', 'search_volume', 'cpc', 'competition_level', 
        'low_bid', 'high_bid', 'difficulty', 'estimated_traffic',
        'trend_monthly', 'competitor_domain'
    ]].copy()
    
    # Add suggested bid ranges
    campaign_keywords['suggested_min_bid'] = campaign_keywords['low_bid'] * 0.8
    campaign_keywords['suggested_max_bid'] = campaign_keywords['high_bid'] * 1.2
    campaign_keywords['bid_strategy'] = campaign_keywords.apply(lambda row: 
        'Conservative' if row['competition_level'] == 'HIGH' else
        'Aggressive' if row['trend_monthly'] > 20 else 'Standard', axis=1
    )
    
    # Export main campaign file
    output_file = f'data/campaign_ready_keywords_{timestamp}.csv'
    campaign_keywords.to_csv(output_file, index=False)
    print(f"📄 Exported campaign keywords: {output_file}")
    
    # 2. Easy wins (low competition, good volume)
    easy_wins = df[
        (df['competition_level'] == 'LOW') & 
        (df['search_volume'] >= 50) &
        (df['cpc'] <= 8)
    ][['keyword', 'search_volume', 'cpc', 'low_bid', 'high_bid', 'competitor_domain']]
    
    easy_wins_file = f'data/easy_wins_keywords_{timestamp}.csv'
    easy_wins.to_csv(easy_wins_file, index=False)
    print(f"🎯 Exported easy wins: {easy_wins_file} ({len(easy_wins)} keywords)")
    
    # 3. High-value targets (premium keywords)
    high_value = df[
        (df['search_volume'] >= 500) & 
        (df['estimated_traffic'] >= 100)
    ][['keyword', 'search_volume', 'cpc', 'estimated_traffic', 'difficulty', 'competitor_domain']]
    
    high_value_file = f'data/high_value_targets_{timestamp}.csv'
    high_value.to_csv(high_value_file, index=False)
    print(f"💎 Exported high-value targets: {high_value_file} ({len(high_value)} keywords)")
    
    # 4. Trending keywords
    trending = df[df['trend_monthly'] > 5][
        ['keyword', 'search_volume', 'trend_monthly', 'cpc', 'competitor_domain']
    ].sort_values('trend_monthly', ascending=False)
    
    trending_file = f'data/trending_keywords_{timestamp}.csv'
    trending.to_csv(trending_file, index=False)
    print(f"📈 Exported trending keywords: {trending_file} ({len(trending)} keywords)")
    
    # 5. Export insights summary
    insights_file = f'data/bidding_insights_{timestamp}.json'
    with open(insights_file, 'w') as f:
        json.dump(insights, f, indent=2, default=str)
    print(f"📊 Exported bidding insights: {insights_file}")
    
    return {
        'campaign_keywords': output_file,
        'easy_wins': easy_wins_file,
        'high_value': high_value_file,
        'trending': trending_file,
        'insights': insights_file
    }

def main():
    """Main execution function"""
    print("🚀 Starting Competitor Keyword Parser for Bidding Optimization")
    print("=" * 60)
    
    try:
        result = parse_competitor_keywords()
        
        print("\n📈 PARSING COMPLETE")
        print("=" * 40)
        print(f"✅ Total keywords processed: {result['total_keywords']:,}")
        print(f"🏢 Unique competitors analyzed: {result['unique_competitors']}")
        
        # Display key opportunities
        opportunities = result['insights']['opportunity_analysis']
        print(f"\n🎯 KEY OPPORTUNITIES:")
        print(f"   • High volume, low competition: {opportunities['high_volume_low_competition']} keywords")
        print(f"   • Trending up (>20% growth): {opportunities['trending_up_keywords']} keywords")  
        print(f"   • Low difficulty, high traffic: {opportunities['low_difficulty_high_traffic']} keywords")
        
        # Display top competitors
        print(f"\n🏆 TOP COMPETITORS BY TRAFFIC:")
        top_comps = result['insights']['competitor_analysis']['top_competitors']
        for domain, stats in list(top_comps.items())[:5]:
            traffic = stats.get('estimated_traffic', 0)
            keywords = stats.get('keyword', 0)
            print(f"   • {domain}: {traffic:,.0f} traffic from {keywords} keywords")
            
        print(f"\n💡 Check the exported files in data/ directory for campaign-ready keywords!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()