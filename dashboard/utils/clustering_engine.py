"""Keyword clustering algorithms and utilities"""
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
import networkx as nx
from typing import Tuple, Optional

def prepare_text_features(keywords: pd.Series) -> Tuple[np.ndarray, TfidfVectorizer]:
    """Convert keywords to TF-IDF features"""
    # Adjust parameters based on dataset size
    n_keywords = len(keywords)
    min_df = max(1, min(2, n_keywords // 5)) if n_keywords < 20 else 2
    max_features = min(100, n_keywords * 10) if n_keywords < 50 else 100
    
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, 3),
        stop_words='english',
        min_df=min_df
    )
    tfidf_matrix = vectorizer.fit_transform(keywords.fillna(''))
    return tfidf_matrix, vectorizer

def calculate_similarity_matrix(tfidf_matrix: np.ndarray) -> np.ndarray:
    """Calculate cosine similarity between all keywords"""
    return cosine_similarity(tfidf_matrix)

def perform_kmeans_clustering(
    tfidf_matrix: np.ndarray, 
    n_clusters: Optional[int] = None,
    max_clusters: int = 20
) -> np.ndarray:
    """Perform K-means clustering with automatic cluster detection"""
    if n_clusters is None:
        # Automatically determine optimal clusters using elbow method
        n_samples = tfidf_matrix.shape[0]
        n_clusters = min(max_clusters, max(3, n_samples // 10))
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(tfidf_matrix)
    return clusters

def perform_hierarchical_clustering(
    similarity_matrix: np.ndarray,
    n_clusters: Optional[int] = None,
    threshold: float = 0.5
) -> np.ndarray:
    """Perform hierarchical clustering"""
    if n_clusters is None:
        n_clusters = None  # Let algorithm decide based on threshold
    
    clustering = AgglomerativeClustering(
        n_clusters=n_clusters,
        affinity='precomputed',
        linkage='average',
        distance_threshold=threshold if n_clusters is None else None
    )
    
    # Convert similarity to distance
    distance_matrix = 1 - similarity_matrix
    clusters = clustering.fit_predict(distance_matrix)
    return clusters

def create_cluster_network(
    df: pd.DataFrame,
    similarity_matrix: np.ndarray,
    threshold: float = 0.3,
    keyword_col: str = 'keyword'
) -> nx.Graph:
    """Create network graph for visualization"""
    G = nx.Graph()
    
    # Reset index to ensure proper alignment
    df_reset = df.reset_index(drop=True)
    
    # Add nodes using sequential indices
    for i, row in df_reset.iterrows():
        G.add_node(
            i,
            keyword=row.get(keyword_col, f'keyword_{i}'),
            cluster=row.get('cluster', 0),
            volume=row.get('search_volume', 0),
            cpc=row.get('cpc', 0),
            difficulty=row.get('keyword_difficulty', 50)
        )
    
    # Add edges for similar keywords
    n_keywords = len(df_reset)
    for i in range(n_keywords):
        for j in range(i + 1, n_keywords):
            if similarity_matrix[i, j] > threshold:
                G.add_edge(i, j, weight=similarity_matrix[i, j])
    
    return G

def get_cluster_summaries(df: pd.DataFrame, keyword_col: str = 'keyword') -> pd.DataFrame:
    """Generate summary statistics for each cluster"""
    if 'cluster' not in df.columns:
        return pd.DataFrame()
    
    # Build aggregation dict based on available columns
    agg_dict = {keyword_col: 'count'}
    if 'search_volume' in df.columns:
        agg_dict['search_volume'] = ['sum', 'mean']
    if 'cpc' in df.columns:
        agg_dict['cpc'] = 'mean'
    if 'keyword_difficulty' in df.columns:
        agg_dict['keyword_difficulty'] = 'mean'
    
    summaries = df.groupby('cluster').agg(agg_dict).round(2)
    
    # Build column names
    col_names = ['Keywords']
    if 'search_volume' in df.columns:
        col_names.extend(['Total Volume', 'Avg Volume'])
    if 'cpc' in df.columns:
        col_names.append('Avg CPC')
    if 'keyword_difficulty' in df.columns:
        col_names.append('Avg Difficulty')
    
    summaries.columns = col_names
    
    # Sort by total volume if available, otherwise by keyword count
    sort_col = 'Total Volume' if 'Total Volume' in summaries.columns else 'Keywords'
    summaries = summaries.sort_values(sort_col, ascending=False)
    
    # Add cluster names based on top keywords
    cluster_names = {}
    for cluster_id in df['cluster'].unique():
        cluster_keywords = df[df['cluster'] == cluster_id][keyword_col].head(3)
        # Find common terms
        common_terms = find_common_terms(cluster_keywords)
        cluster_names[cluster_id] = common_terms or f"Cluster {cluster_id}"
    
    summaries['Cluster Name'] = summaries.index.map(cluster_names)
    return summaries

def find_common_terms(keywords: pd.Series) -> str:
    """Find common terms in a group of keywords"""
    if len(keywords) == 0:
        return ""
    
    # Split all keywords into words
    all_words = []
    for keyword in keywords:
        all_words.extend(keyword.lower().split())
    
    # Find most common word
    from collections import Counter
    word_counts = Counter(all_words)
    
    # Filter out stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
    filtered_counts = {w: c for w, c in word_counts.items() if w not in stop_words}
    
    if filtered_counts:
        most_common = max(filtered_counts, key=filtered_counts.get)
        return most_common.title()
    return "General"

def reduce_dimensions_for_viz(tfidf_matrix: np.ndarray, n_components: int = 2) -> np.ndarray:
    """Reduce dimensions for 2D/3D visualization"""
    pca = PCA(n_components=n_components, random_state=42)
    reduced = pca.fit_transform(tfidf_matrix.toarray())
    return reduced