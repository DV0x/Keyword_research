#!/usr/bin/env python3
"""
Google Ads Keyword Parser
Agency-ready workflow to turn ranked_keywords CSV into bidding-ready data

Based on the simple, repeatable recipe for processing huge competitor keyword exports.
Run this script and get a clean, sortable sheet of keywords ready for Google Ads.
"""

import pandas as pd
import ast
import json
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

def parse_for_google_ads(raw_file="data/competitor_keywords_v2.csv"):
    """
    Convert competitor keywords CSV to Google Ads ready format
    Following the 7-step agency workflow
    """
    
    print("🚀 GOOGLE ADS KEYWORD PARSER")
    print("=" * 50)
    
    # Step 1 — Load the file & pick the useful columns
    print(f"📂 Loading {raw_file}...")
    RAW = Path(raw_file)
    df = pd.read_csv(RAW, engine="python")  # engine=python tolerates commas in JSON
    
    print(f"📊 Loaded {len(df):,} rows from {RAW}")
    
    # Choose ONLY the columns you care about
    cols = [
        "keyword",                              # query
        "keyword_search_volume",                # last-month volume
        "keyword_cpc",                          # avg CPC
        "keyword_competition",                  # 0-100 index
        "keyword_low_top_of_page_bid",          # low-range bid
        "keyword_high_top_of_page_bid",         # high-range bid
        "keyword_search_intent_info",           # intent JSON
        "keyword_last_updated_time",            # when volume/CPC were refreshed
        "ranked_serp_element"                   # blob that holds competitor rank + timestamp
    ]
    df = df[cols]
    print(f"✅ Selected {len(cols)} essential columns")
    
    # Step 2 — Flatten the two JSON blobs
    print("🔍 Extracting intent and competitor ranking data...")
    
    # Intent
    df["intent"] = df["keyword_search_intent_info"].apply(
        lambda s: ast.literal_eval(s)["main_intent"] if pd.notna(s) else "unknown"
    )
    
    # Competitor rank & rank timestamp
    serp = df["ranked_serp_element"].apply(ast.literal_eval)
    df["competitor_rank"] = serp.map(lambda j: j["serp_item"]["rank_absolute"])
    df["rank_date"] = pd.to_datetime(
        serp.map(lambda j: j["last_updated_time"]), errors="coerce"
    )
    
    print(f"Intent distribution: {df['intent'].value_counts().to_dict()}")
    
    # Drop the original JSON columns
    df.drop(columns=["keyword_search_intent_info","ranked_serp_element"], inplace=True)
    print(f"🗑️  Dropped JSON columns, now have {len(df.columns)} columns")
    
    # Step 3 — Light cleanup
    print("🧹 Cleaning numeric data...")
    
    # Numeric cast
    num_cols = ["keyword_search_volume","keyword_cpc","keyword_competition",
                "keyword_low_top_of_page_bid","keyword_high_top_of_page_bid"]
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce")
    
    # Fix volumes if they look tiny (older exports store 8.3 instead of 830)
    if df["keyword_search_volume"].max() < 50:
        df["keyword_search_volume"] = (df["keyword_search_volume"] * 100).round(0)
        print("📈 Fixed volume scaling (multiplied by 100)")
    else:
        print(f"📊 Volume range looks good: {df['keyword_search_volume'].min():.0f} - {df['keyword_search_volume'].max():.0f}")
    
    # Step 4 — Drop obvious junk
    print("🗑️  Removing junk keywords...")
    
    junk = ["calculator","meaning","definition","job","salary"]
    before_count = len(df)
    mask = ~df["keyword"].str.contains("|".join(junk), case=False, na=False)
    df = df[mask]
    removed = before_count - len(df)
    print(f"Removed {removed:,} junk keywords ({removed/before_count*100:.1f}%)")
    print(f"✅ Clean dataset: {len(df):,} keywords remaining")
    
    # Step 5 — Keep only *fresh* rows
    print("🕒 Filtering for fresh data...")
    
    now = datetime.now()
    df["kw_date"] = pd.to_datetime(df["keyword_last_updated_time"], errors="coerce", utc=True)
    df["rank_date"] = pd.to_datetime(df["rank_date"], utc=True)
    
    # Convert now to timezone-aware for comparison
    now_utc = pd.Timestamp(now, tz='UTC')
    
    before_fresh = len(df)
    df = df[
        (df.kw_date >= now_utc - timedelta(days=90)) &     # metrics ≤ 3 months old
        (df.rank_date >= now_utc - timedelta(days=30))     # ranking snapshot ≤ 1 month old
    ]
    removed_stale = before_fresh - len(df)
    print(f"Removed {removed_stale:,} stale rows (metrics >90 days or ranks >30 days)")
    print(f"✅ Fresh dataset: {len(df):,} keywords with recent data")
    
    # Step 6 — Rename to friendly headers & reorder
    print("📝 Renaming columns for Google Ads...")
    
    df = df.rename(columns={
        "keyword_search_volume":"vol",
        "keyword_cpc":"cpc",
        "keyword_competition":"competition",
        "keyword_low_top_of_page_bid":"low_bid",
        "keyword_high_top_of_page_bid":"high_bid"
    })[[
        "keyword","vol","cpc","competition","low_bid","high_bid",
        "intent","competitor_rank","kw_date","rank_date"
    ]]
    
    print("✅ Renamed columns for Google Ads readiness")
    
    # Step 7 — Export for bidding / sorting
    print("💾 Exporting bidding-ready file...")
    
    timestamp = datetime.now().strftime("%Y-%m-%d")
    OUT = Path(f"bidding_ready_{timestamp}.csv")
    
    # Sort by volume (desc) and competitor rank (asc) for easy bidding prioritization
    df_sorted = df.sort_values(["vol","competitor_rank"], ascending=[False,True])
    df_sorted.to_csv(OUT, index=False)
    
    print(f"✅ Saved {OUT.resolve()} with {len(df):,} rows")
    print(f"🎯 Ready for Google Ads import!")
    
    # Show summary
    print("\n📊 FINAL DATASET SUMMARY")
    print("=" * 50)
    print(f"Total keywords: {len(df):,}")
    print(f"Volume range: {df['vol'].min():.0f} - {df['vol'].max():.0f}")
    print(f"CPC range: ${df['cpc'].min():.2f} - ${df['cpc'].max():.2f}")
    print(f"Intent breakdown: {df['intent'].value_counts().to_dict()}")
    
    print("\n🎯 TOP 10 HIGHEST VOLUME KEYWORDS:")
    print(df_sorted[['keyword', 'vol', 'cpc', 'intent', 'competitor_rank']].head(10).to_string(index=False))
    
    print(f"\n💡 BIDDING TIPS:")
    print(f"• Focus on 'commercial' and 'transactional' intent keywords first")
    print(f"• Initial Max CPC = CPC × 1.2")
    print(f"• Keywords with vol ≥ 20 deserve their own ad groups") 
    print(f"• Competition > 70 = crowded auction, check landing page quality")
    print(f"• Stay near low_bid while testing, scale to high_bid if profitable")
    
    return df_sorted, OUT

def main():
    """Main execution"""
    try:
        df, output_file = parse_for_google_ads()
        print(f"\n🎉 SUCCESS! Check {output_file} for your Google Ads ready keywords.")
        return True
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    main()