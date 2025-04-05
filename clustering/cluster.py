"""
Clustering module for YouTube channel embeddings
"""

import os
from typing import Dict, List, Any, Tuple
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import umap


def create_clusters(embeddings: np.ndarray, channels: List[Dict], n_clusters: int = 10) -> Dict:
    """
    Create clusters from channel embeddings using UMAP + DBSCAN
    Returns a dictionary with cluster assignments and metadata
    """
    # Reduce dimensionality with UMAP
    print("Reducing dimensionality with UMAP...")
    umap_reducer = umap.UMAP(
        n_neighbors=15,
        min_dist=0.1,
        n_components=2,
        metric='cosine'
    )
    reduced_embeddings = umap_reducer.fit_transform(embeddings)
    
    # Perform DBSCAN clustering
    print("Performing DBSCAN clustering...")
    clusterer = DBSCAN(
        eps=0.5,
        min_samples=5,
        metric='euclidean'
    )
    cluster_labels = clusterer.fit_predict(reduced_embeddings)
    
    # Calculate cluster metrics
    n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
    silhouette_avg = silhouette_score(reduced_embeddings, cluster_labels)
    print(f"Number of clusters: {n_clusters}")
    print(f"Silhouette Score: {silhouette_avg:.4f}")
    
    # Organize channels by cluster
    clusters = {
        'channels': {},
        'metadata': {
            'n_clusters': n_clusters,
            'silhouette_score': silhouette_avg,
            'reduced_embeddings': reduced_embeddings.tolist()
        }
    }
    
    # Group channels by cluster
    for i, label in enumerate(cluster_labels):
        cluster_key = str(label)
        if cluster_key not in clusters['channels']:
            clusters['channels'][cluster_key] = []
        clusters['channels'][cluster_key].append(channels[i])
    
    return clusters


def find_optimal_clusters(embeddings, max_clusters=20):
    """
    Find the optimal number of clusters using silhouette scores
    
    Args:
        embeddings: numpy array of embeddings
        max_clusters: Maximum number of clusters to try
        
    Returns:
        Dictionary with optimal number of clusters and scores
    """
    silhouette_scores = []
    k_values = range(2, min(max_clusters + 1, len(embeddings)))
    
    print("Finding optimal number of clusters...")
    
    for k in k_values:
        # Create KMeans with k clusters
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embeddings)
        
        # Calculate silhouette score
        score = silhouette_score(embeddings, labels)
        silhouette_scores.append(score)
        print(f"k={k}, silhouette={score:.4f}")
    
    # Find optimal k (highest silhouette score)
    optimal_k = list(k_values)[np.argmax(silhouette_scores)]
    
    return {
        'optimal_k': optimal_k,
        'scores': silhouette_scores,
        'k_values': list(k_values)
    }
