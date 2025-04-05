"""
Clustering module for YouTube channel embeddings
"""

import os
from typing import Dict, List, Any, Tuple
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA


def create_clusters(embeddings, channels=None, n_clusters=10, algorithm='kmeans'):
    """
    Cluster the channel embeddings
    
    Args:
        embeddings: numpy array of embeddings
        channels: List of channel data (optional)
        n_clusters: Number of clusters to create
        algorithm: Clustering algorithm to use ('kmeans' or 'dbscan')
        
    Returns:
        Dictionary with cluster model, labels, and metadata
    """
    # Select clustering algorithm
    if algorithm.lower() == 'dbscan':
        # DBSCAN automatically determines the number of clusters
        cluster_model = DBSCAN(eps=0.5, min_samples=5)
    else:
        # KMeans with specified number of clusters
        cluster_model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    
    # Fit the model to the embeddings
    cluster_model.fit(embeddings)
    
    # Get cluster labels
    if algorithm.lower() == 'dbscan':
        labels = cluster_model.labels_
        # Count the number of clusters (excluding noise points labeled as -1)
        n_clusters_found = len(set(labels)) - (1 if -1 in labels else 0)
        print(f"DBSCAN found {n_clusters_found} clusters")
    else:
        labels = cluster_model.labels_
        centers = cluster_model.cluster_centers_
    
    # Calculate silhouette score if more than one cluster
    if len(set(labels)) > 1 and min(labels) >= 0:
        silhouette = silhouette_score(embeddings, labels)
        print(f"Silhouette score: {silhouette:.4f}")
    else:
        silhouette = None
        print("Skipping silhouette score calculation (not enough clusters)")
    
    # Create cluster output
    clusters = {
        'algorithm': algorithm,
        'n_clusters': n_clusters if algorithm.lower() != 'dbscan' else n_clusters_found,
        'silhouette_score': silhouette,
        'labels': labels.tolist()
    }
    
    # Add dimensionality reduction for visualization
    if embeddings.shape[1] > 2:
        # Use PCA to reduce to 2D
        pca = PCA(n_components=2)
        reduced_data = pca.fit_transform(embeddings)
        
        # Add reduced coordinates
        clusters['reduced_data'] = reduced_data.tolist()
        clusters['explained_variance'] = pca.explained_variance_ratio_.tolist()
    
    # Add channel data to clusters if provided
    if channels:
        # Group channels by cluster
        cluster_channels = {}
        for i, channel in enumerate(channels):
            cluster_label = str(labels[i])  # Convert to string for JSON compatibility
            
            if cluster_label not in cluster_channels:
                cluster_channels[cluster_label] = []
            
            # Add channel to its cluster
            cluster_channels[cluster_label].append({
                'channel_id': channel.get('channel_id'),
                'title': channel.get('title'),
                'description': channel.get('description'),
                'subscriber_count': channel.get('subscriber_count'),
                'video_count': channel.get('video_count'),
                
                # Add 2D coordinates for visualization
                'x': float(reduced_data[i][0]) if embeddings.shape[1] > 2 else float(embeddings[i][0]),
                'y': float(reduced_data[i][1]) if embeddings.shape[1] > 2 else float(embeddings[i][1])
            })
        
        clusters['channels'] = cluster_channels
    
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
