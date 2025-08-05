"""
Step 4: Keyword enrichment with comprehensive metrics and difficulty scores
"""
import pandas as pd
import logging
from tqdm import tqdm
from ..core.data_processor import parse_existing_keyword_data, batch_iterator

logger = logging.getLogger(__name__)


class KeywordEnricher:
    """Enrich keywords with comprehensive metrics and difficulty scores"""
    
    def __init__(self, api_client):
        self.api_client = api_client
    
    def enrich_keywords(self, seed_keywords_df: pd.DataFrame, country_code: int, language_name: str) -> pd.DataFrame:
        """Enrich keywords with comprehensive metrics and difficulty scores"""
        logger.info("📋 Step 4: Enriching keywords with comprehensive metrics...")
        
        # First, parse existing data from the CSV
        enriched_df = parse_existing_keyword_data(seed_keywords_df)
        
        # Sort by search volume and take top keywords for additional enrichment
        # Focus on top 1000 keywords for additional API calls to manage costs
        if "search_volume" in enriched_df.columns:
            top_keywords = enriched_df.nlargest(1000, "search_volume")["keyword"].tolist()
        else:
            top_keywords = enriched_df["keyword"].tolist()[:1000]
        
        if not top_keywords:
            logger.warning("No keywords found to enrich")
            return enriched_df
        
        # Step 4.1: Get difficulty scores for keywords without them (most important missing data)
        keywords_without_difficulty = enriched_df[
            enriched_df["keyword_difficulty"].isna() | (enriched_df["keyword_difficulty"] == 0)
        ]["keyword"].tolist()
        
        if keywords_without_difficulty:
            logger.info(f"🔍 Getting difficulty scores for {len(keywords_without_difficulty)} keywords...")
            difficulty_results = []
            
            try:
                for batch in tqdm(list(batch_iterator(keywords_without_difficulty, 1000)), desc="Difficulty scores"):
                    try:
                        diff_df = self.api_client.bulk_keyword_difficulty(batch, country_code, language_name)
                        if not diff_df.empty:
                            difficulty_results.append(diff_df)
                            logger.info(f"   ✅ Processed difficulty batch of {len(batch)} keywords")
                        else:
                            logger.warning(f"   ⚠️ Empty difficulty response for batch of {len(batch)} keywords")
                    except Exception as e:
                        logger.error(f"   ❌ Difficulty batch failed: {e}")
                        continue
                
                # Merge difficulty data
                if difficulty_results:
                    diff_df = pd.concat(difficulty_results, ignore_index=True)
                    logger.info(f"📊 Difficulty data collected for {len(diff_df)} keywords")
                    
                    # Update difficulty scores
                    enriched_df = enriched_df.merge(
                        diff_df[["keyword", "keyword_difficulty"]],
                        on="keyword",
                        how="left",
                        suffixes=("", "_new")
                    )
                    
                    # Fill missing difficulty scores
                    enriched_df["keyword_difficulty"] = enriched_df["keyword_difficulty"].fillna(
                        enriched_df["keyword_difficulty_new"]
                    )
                    enriched_df.drop(columns=["keyword_difficulty_new"], inplace=True, errors='ignore')
                    logger.info(f"   ✅ Difficulty scores updated successfully")
                else:
                    logger.warning("   ⚠️ No difficulty data collected")
                    
            except Exception as e:
                logger.error(f"❌ Keyword difficulty enrichment failed: {e}")
        else:
            logger.info("✅ All keywords already have difficulty scores")
        
        # Step 4.2: Calculate enrichment statistics
        total_keywords = len(enriched_df)
        keywords_with_difficulty = enriched_df["keyword_difficulty"].notna().sum()
        keywords_with_cpc = enriched_df["cpc"].notna().sum() if "cpc" in enriched_df.columns else 0
        keywords_with_volume = enriched_df["search_volume"].notna().sum() if "search_volume" in enriched_df.columns else 0
        
        keywords_with_volume_positive = (enriched_df["search_volume"] > 0).sum() if "search_volume" in enriched_df.columns else 0
        keywords_with_intent = enriched_df["main_intent"].notna().sum() if "main_intent" in enriched_df.columns else 0
        
        logger.info("📊 Final Enrichment Summary:")
        logger.info(f"   • Total keywords: {total_keywords:,}")
        logger.info(f"   • With search volume > 0: {keywords_with_volume_positive:,} ({keywords_with_volume_positive/total_keywords*100:.1f}%)")
        logger.info(f"   • With CPC data: {keywords_with_cpc:,} ({keywords_with_cpc/total_keywords*100:.1f}%)")
        logger.info(f"   • With difficulty scores: {keywords_with_difficulty:,} ({keywords_with_difficulty/total_keywords*100:.1f}%)")
        logger.info(f"   • With search intent: {keywords_with_intent:,} ({keywords_with_intent/total_keywords*100:.1f}%)")
        
        # Show intent distribution
        if "main_intent" in enriched_df.columns:
            intent_counts = enriched_df["main_intent"].value_counts()
            logger.info("📊 Search Intent Distribution:")
            for intent, count in intent_counts.head(5).items():
                logger.info(f"   • {intent}: {count:,} keywords ({count/total_keywords*100:.1f}%)")
        
        logger.info("✅ Keyword enrichment completed!")
        return enriched_df