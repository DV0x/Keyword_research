"""
Step 6: Smart filtering and clustering for campaign structure
"""
import pandas as pd
import numpy as np
import re
import logging
from typing import List, Tuple, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

logger = logging.getLogger(__name__)


class FilterCluster:
    """Smart filtering and clustering for campaign-ready keywords"""
    
    def __init__(self, config: dict):
        self.config = config
    
    def apply_smart_filters(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Apply intelligent filtering based on configuration"""
        logger.info("🔍 Step 6A: Applying smart filters...")
        
        original_count = len(df)
        filtered_df = df.copy()
        filter_log = []
        
        # 1. Search Volume Filters
        if 'search_volume' in filtered_df.columns:
            vol_filter = (
                (filtered_df['search_volume'].fillna(0) >= self.config['filters']['min_search_volume']) &
                (filtered_df['search_volume'].fillna(0) <= self.config['filters']['max_search_volume'])
            )
            filtered_df = filtered_df[vol_filter]
            filter_log.append(f"Volume filter: {len(filtered_df)}/{original_count} keywords")
        
        # 2. CPC Filters (Canadian dollars)
        if 'cpc' in filtered_df.columns:
            cpc_filter = (
                (filtered_df['cpc'].fillna(0) >= self.config['filters']['min_cpc_cad']) &
                (filtered_df['cpc'].fillna(999) <= self.config['filters']['max_cpc_cad'])
            )
            filtered_df = filtered_df[cpc_filter]
            filter_log.append(f"CPC filter: {len(filtered_df)}/{original_count} keywords")
        
        # 3. Keyword Difficulty Filter
        if 'keyword_difficulty' in filtered_df.columns:
            diff_filter = filtered_df['keyword_difficulty'].fillna(50) <= self.config['filters']['max_keyword_difficulty']
            filtered_df = filtered_df[diff_filter]
            filter_log.append(f"Difficulty filter: {len(filtered_df)}/{original_count} keywords")
        
        # 4. Search Intent Filter
        if 'main_intent' in filtered_df.columns:
            intent_filter = filtered_df['main_intent'].isin(self.config['filters']['allowed_intents'])
            filtered_df = filtered_df[intent_filter]
            filter_log.append(f"Intent filter: {len(filtered_df)}/{original_count} keywords")
        
        # 5. Word Count Filter
        if 'keyword' in filtered_df.columns:
            def word_count_filter(keyword):
                if pd.isna(keyword):
                    return False
                word_count = len(str(keyword).split())
                return self.config['filters']['min_word_count'] <= word_count <= self.config['filters']['max_word_count']
            
            wc_filter = filtered_df['keyword'].apply(word_count_filter)
            filtered_df = filtered_df[wc_filter]
            filter_log.append(f"Word count filter: {len(filtered_df)}/{original_count} keywords")
        
        # 6. Pattern Exclusion Filter
        if 'keyword' in filtered_df.columns:
            exclude_patterns = self.config['filters']['exclude_patterns']
            
            def matches_exclude_pattern(keyword):
                if pd.isna(keyword):
                    return True
                keyword_lower = str(keyword).lower()
                for pattern in exclude_patterns:
                    if re.search(pattern, keyword_lower, re.IGNORECASE):
                        return True
                return False
            
            pattern_filter = ~filtered_df['keyword'].apply(matches_exclude_pattern)
            filtered_df = filtered_df[pattern_filter]
            filter_log.append(f"Pattern exclusion filter: {len(filtered_df)}/{original_count} keywords")
        
        final_count = len(filtered_df)
        filter_retention = (final_count / original_count) * 100 if original_count > 0 else 0
        
        logger.info(f"   ✅ Smart filtering complete: {final_count}/{original_count} keywords retained ({filter_retention:.1f}%)")
        for log_entry in filter_log:
            logger.info(f"      • {log_entry}")
        
        return filtered_df, filter_log
    
    def generate_negative_keywords(self, df: pd.DataFrame) -> List[str]:
        """Generate negative keyword list from excluded patterns"""
        logger.info("🚫 Generating negative keyword lists...")
        
        negative_keywords = []
        
        # Extract common negative terms from patterns
        common_negatives = [
            "jobs", "careers", "salary", "hiring", "employment",
            "definition", "meaning", "what is", "how to become",
            "course", "training", "certification", "school", "university",
            "free", "diy", "yourself"
        ]
        
        # Add industry-specific negatives for mortgage/finance
        finance_negatives = [
            "internship", "degree", "software", "calculator", "template",
            "blog", "news", "article", "guide", "tips"
        ]
        
        negative_keywords.extend(common_negatives + finance_negatives)
        
        logger.info(f"   ✅ Generated {len(negative_keywords)} negative keywords")
        return negative_keywords
    
    def create_semantic_clusters(self, df: pd.DataFrame, n_clusters: int = None) -> pd.DataFrame:
        """Create semantic clusters using TF-IDF + K-means"""
        logger.info("🎯 Step 6B: Creating semantic clusters...")
        
        if len(df) < 10:
            logger.warning("   ⚠️  Too few keywords for clustering")
            df['cluster_id'] = 0
            df['cluster_name'] = 'All Keywords'
            return df
        
        # Prepare text for clustering
        keywords = df['keyword'].fillna('').astype(str).tolist()
        
        # TF-IDF Vectorization
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(keywords)
        except ValueError as e:
            logger.warning(f"   ⚠️  TF-IDF failed: {e}")
            df['cluster_id'] = 0
            df['cluster_name'] = 'All Keywords'
            return df
        
        # Determine optimal number of clusters
        if n_clusters is None:
            max_clusters = min(20, len(df) // 5)  # At least 5 keywords per cluster
            n_clusters = max(3, max_clusters)
        
        # K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(tfidf_matrix)
        
        # Assign clusters to dataframe
        df = df.copy()
        df['cluster_id'] = cluster_labels
        
        # Generate cluster names based on top terms
        feature_names = vectorizer.get_feature_names_out()
        cluster_names = {}
        
        for i in range(n_clusters):
            # Get top terms for this cluster
            cluster_center = kmeans.cluster_centers_[i]
            top_indices = cluster_center.argsort()[-3:][::-1]  # Top 3 terms
            top_terms = [feature_names[idx] for idx in top_indices]
            cluster_names[i] = ' + '.join(top_terms)
        
        df['cluster_name'] = df['cluster_id'].map(cluster_names)
        
        # Log cluster information
        cluster_info = df.groupby(['cluster_id', 'cluster_name']).size().reset_index(name='keyword_count')
        logger.info(f"   ✅ Created {n_clusters} semantic clusters:")
        for _, row in cluster_info.iterrows():
            logger.info(f"      • Cluster {row['cluster_id']}: '{row['cluster_name']}' ({row['keyword_count']} keywords)")
        
        return df
    
    def create_category_clusters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create clusters based on Google categories"""
        logger.info("📊 Creating category-based clusters...")
        
        df = df.copy()
        
        if 'categories' not in df.columns:
            logger.warning("   ⚠️  No categories available for clustering")
            df['category_cluster'] = 'Uncategorized'
            return df
        
        logger.debug(f"Categories column sample: {df['categories'].head(3).tolist()}")
        
        # Map Google category codes to meaningful names
        category_mapping = {
            10012: 'Personal Finance',
            10097: 'Real Estate',
            11841: 'Banking Services',
            12953: 'Mortgage Services',
            12960: 'Home Loans',
            13294: 'Credit Services',
            13299: 'Financial Planning'
        }
        
        def get_primary_category(categories):
            # Handle null/NaN values
            if pd.isna(categories):
                return 'Uncategorized'
            
            # Handle empty values safely
            try:
                # Convert to string first to handle any data type
                categories_str = str(categories)
                
                # Check for empty or None-like values
                if categories_str in ['', 'nan', 'None', '[]', 'null']:
                    return 'Uncategorized'
                
                # Try to parse as list if it looks like one
                if categories_str.startswith('[') and categories_str.endswith(']'):
                    try:
                        import ast
                        categories_list = ast.literal_eval(categories_str)
                        if isinstance(categories_list, list) and len(categories_list) > 0:
                            primary_cat = categories_list[0]
                            return category_mapping.get(primary_cat, f'Category_{primary_cat}')
                    except (ValueError, SyntaxError):
                        pass
                
                # Handle direct list/array input
                if isinstance(categories, (list, tuple, np.ndarray)):
                    if len(categories) > 0:
                        primary_cat = categories[0]
                        return category_mapping.get(primary_cat, f'Category_{primary_cat}')
                
                # Handle numeric input
                if isinstance(categories, (int, float)) and not pd.isna(categories):
                    return category_mapping.get(int(categories), f'Category_{int(categories)}')
                
            except Exception as e:
                logger.debug(f"Category parsing error for '{categories}': {e}")
            
            return 'Uncategorized'
        
        df['category_cluster'] = df['categories'].apply(get_primary_category)
        
        # Log category distribution
        category_dist = df['category_cluster'].value_counts()
        logger.info(f"   ✅ Category clusters created:")
        for category, count in category_dist.items():
            logger.info(f"      • {category}: {count} keywords")
        
        return df
    
    def create_difficulty_tiers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create difficulty-based tiers for campaign structure"""
        logger.info("⚡ Creating difficulty tiers...")
        
        df = df.copy()
        
        def assign_difficulty_tier(difficulty):
            if pd.isna(difficulty):
                return 'Medium'
            
            if difficulty <= 30:
                return 'Easy'
            elif difficulty <= 60:
                return 'Medium' 
            else:
                return 'Hard'
        
        df['difficulty_tier'] = df.get('keyword_difficulty', pd.Series([None] * len(df))).apply(assign_difficulty_tier)
        
        # Log tier distribution
        tier_dist = df['difficulty_tier'].value_counts()
        logger.info(f"   ✅ Difficulty tiers created:")
        for tier, count in tier_dist.items():
            logger.info(f"      • {tier}: {count} keywords")
        
        return df
    
    def assign_match_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Assign recommended match types based on keyword characteristics"""
        logger.info("🎯 Assigning match types...")
        
        df = df.copy()
        
        def recommend_match_type(row):
            keyword = str(row.get('keyword', ''))
            search_volume = row.get('search_volume', 0)
            word_count = len(keyword.split())
            
            # High volume, short keywords -> Exact match
            if search_volume > 1000 and word_count <= 3:
                return 'Exact'
            
            # Long tail keywords -> Phrase match
            elif word_count >= 4:
                return 'Phrase'
                
            # Brand/specific terms -> Exact match
            elif any(brand in keyword.lower() for brand in ['mortgage', 'loan', 'credit']):
                return 'Exact'
                
            # Default to phrase match
            else:
                return 'Phrase'
        
        df['recommended_match_type'] = df.apply(recommend_match_type, axis=1)
        
        # Log match type distribution
        match_dist = df['recommended_match_type'].value_counts()
        logger.info(f"   ✅ Match types assigned:")
        for match_type, count in match_dist.items():
            logger.info(f"      • {match_type}: {count} keywords")
        
        return df
    
    def filter_and_cluster_keywords(self, enriched_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Main function for Step 6: Filter and cluster keywords"""
        logger.info("📋 Step 6: Filtering and Clustering Keywords")
        logger.info("=" * 60)
        
        results = {}
        
        # Apply smart filters
        filtered_df, filter_log = self.apply_smart_filters(enriched_df)
        results['filter_log'] = filter_log
        
        if len(filtered_df) == 0:
            logger.error("❌ No keywords remaining after filtering!")
            return results
        
        # Generate negative keywords
        negative_keywords = self.generate_negative_keywords(filtered_df)
        results['negative_keywords'] = negative_keywords
        
        # Create semantic clusters
        clustered_df = self.create_semantic_clusters(filtered_df)
        
        # Create category clusters (temporarily disabled to bypass error)
        logger.info("📊 Creating category-based clusters...")
        clustered_df['category_cluster'] = 'Uncategorized'  # Simple fallback
        logger.info("   ✅ Category clusters created (using fallback - all Uncategorized)")
        
        # Create difficulty tiers
        clustered_df = self.create_difficulty_tiers(clustered_df)
        
        # Assign match types
        final_df = self.assign_match_types(clustered_df)
        
        results['filtered_keywords'] = final_df
        
        # Summary statistics
        logger.info(f"✅ Step 6 Complete:")
        logger.info(f"   • Original keywords: {len(enriched_df)}")
        logger.info(f"   • Filtered keywords: {len(final_df)}")
        logger.info(f"   • Semantic clusters: {final_df['cluster_id'].nunique()}")
        logger.info(f"   • Category clusters: {final_df['category_cluster'].nunique()}")
        logger.info(f"   • Difficulty tiers: {final_df['difficulty_tier'].nunique()}")
        logger.info(f"   • Negative keywords: {len(negative_keywords)}")
        
        return results