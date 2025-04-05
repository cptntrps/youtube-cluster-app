#!/usr/bin/env python3
"""
Enhanced clustering script for YouTube channels
- Considers subscription relationships between channels
- Automatically names clusters by content category
"""

import os
import json
import numpy as np
from collections import Counter
from dotenv import load_dotenv
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
import requests
import re

# Import project modules
from auth.oauth import authenticate
from data.store import load_subscriptions, save_clusters
from clustering.vectorize import vectorize_channels, get_model
from clustering.cluster import create_clusters

# Topic mapping for automatic cluster naming
TOPIC_MAP = {
    "Music": ["music", "band", "song", "singer", "rapper", "artist", "piano", "guitar", "drum"],
    "Gaming": ["game", "gaming", "playthrough", "minecraft", "fortnite", "gamer", "xbox", "playstation", "nintendo"],
    "Technology": ["tech", "technology", "programming", "code", "developer", "computer", "software", "hardware"],
    "Science": ["science", "physics", "chemistry", "biology", "astronomy", "space", "experiment"],
    "Education": ["education", "learn", "school", "university", "college", "academic", "lecture", "course"],
    "Entertainment": ["entertainment", "funny", "comedy", "prank", "skit", "humor"],
    "News": ["news", "politics", "current events", "journalist", "report"],
    "Sports": ["sports", "football", "basketball", "soccer", "baseball", "nfl", "nba", "fitness"],
    "Art": ["art", "drawing", "painting", "animation", "design", "creative"],
    "Food": ["food", "cooking", "recipe", "chef", "baking", "cuisine", "restaurant"],
    "Fashion": ["fashion", "clothing", "style", "beauty", "makeup", "model"],
    "Travel": ["travel", "vlog", "adventure", "tourism", "explore", "destination"],
    "Automotive": ["car", "auto", "vehicle", "motorcycle", "racing", "engine"],
    "Finance": ["finance", "money", "investing", "stock", "crypto", "bitcoin", "business"],
    "DIY": ["diy", "craft", "how to", "tutorial", "woodworking", "maker", "build"],
    "Lifestyle": ["lifestyle", "minimalism", "productivity", "self-improvement", "motivation"],
    "History": ["history", "historical", "ancient", "medieval", "civilization", "war"]
}

# Add NumPy JSON encoder
class NumpyEncoder(json.JSONEncoder):
    """Special JSON encoder for NumPy types"""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

def fetch_channel_subscriptions(youtube_client, channel_id):
    """Fetch the subscriptions of a specific channel"""
    try:
        response = youtube_client.subscriptions().list(
            part="snippet",
            channelId=channel_id,
            maxResults=50
        ).execute()
        
        subscribed_to = []
        for item in response.get('items', []):
            subscribed_to.append(item['snippet']['resourceId']['channelId'])
            
        return subscribed_to
    except:
        # Some channels may have hidden their subscriptions
        return []

def build_subscription_graph(youtube_client, channels):
    """
    Build a graph of subscription relationships between channels
    Returns a dictionary mapping channel_id to list of channel_ids it subscribes to
    """
    print("Building subscription relationship graph...")
    subscription_graph = {}
    
    # Fetch subscriptions for each channel
    for i, channel in enumerate(channels):
        channel_id = channel.get('channel_id')
        if not channel_id:
            continue
            
        if i % 10 == 0:
            print(f"Processed {i}/{len(channels)} channels")
            
        subscribed_to = fetch_channel_subscriptions(youtube_client, channel_id)
        subscription_graph[channel_id] = subscribed_to
    
    return subscription_graph

def enhance_embeddings_with_relationships(embeddings, channels, subscription_graph, weight=0.3):
    """
    Enhance channel embeddings with subscription relationship data and engagement metrics
    Weight determines how much influence subscription relationships have (0.0-1.0)
    """
    print("Enhancing embeddings with subscription relationships and engagement metrics...")
    
    # Create a mapping from channel_id to embedding index
    channel_id_to_index = {channel.get('channel_id'): i for i, channel in enumerate(channels) if channel.get('channel_id')}
    
    # Create a copy of the original embeddings
    enhanced_embeddings = embeddings.copy()
    
    # Calculate engagement features
    engagement_features = np.zeros((len(channels), 4))  # 4 engagement metrics
    for i, channel in enumerate(channels):
        engagement_features[i] = [
            float(channel.get('avg_views_per_video', 0)),
            float(channel.get('avg_likes_per_video', 0)),
            float(channel.get('avg_comments_per_video', 0)),
            float(channel.get('engagement_rate', 0))
        ]
    
    # Normalize engagement features
    engagement_features = (engagement_features - engagement_features.mean(axis=0)) / (engagement_features.std(axis=0) + 1e-8)
    
    # Project engagement features to match embedding dimension using a simpler approach
    # Instead of PCA, we'll use a weighted combination of the original embeddings
    engagement_weights = np.mean(engagement_features, axis=1, keepdims=True)
    engagement_embeddings = embeddings * engagement_weights
    
    # Enhance embeddings based on subscription relationships and engagement
    for channel_id, subscribed_to in subscription_graph.items():
        if channel_id not in channel_id_to_index:
            continue
            
        channel_index = channel_id_to_index[channel_id]
        
        # Find embeddings of subscribed channels
        subscribed_embeddings = []
        subscribed_engagement = []
        for sub_id in subscribed_to:
            if sub_id in channel_id_to_index:
                sub_index = channel_id_to_index[sub_id]
                subscribed_embeddings.append(embeddings[sub_index])
                subscribed_engagement.append(engagement_embeddings[sub_index])
        
        # If this channel subscribes to others, enhance its embedding
        if subscribed_embeddings:
            # Calculate average embedding of subscribed channels
            avg_sub_embedding = np.mean(subscribed_embeddings, axis=0)
            
            # Calculate average engagement of subscribed channels
            avg_sub_engagement = np.mean(subscribed_engagement, axis=0)
            
            # Blend original with subscription relationship data and engagement
            enhanced_embeddings[channel_index] = (
                (1 - weight) * embeddings[channel_index] + 
                weight * 0.7 * avg_sub_embedding +
                weight * 0.3 * avg_sub_engagement
            )
    
    return enhanced_embeddings

def find_optimal_clusters(embeddings, max_clusters=15):
    """
    Find the optimal number of clusters using the elbow method and silhouette analysis
    """
    from sklearn.metrics import silhouette_score
    from sklearn.cluster import KMeans
    
    print("Finding optimal number of clusters...")
    
    # Calculate inertia (within-cluster sum of squares) for different numbers of clusters
    inertias = []
    silhouette_scores = []
    
    for k in range(2, max_clusters + 1):
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(embeddings)
        inertias.append(kmeans.inertia_)
        
        # Calculate silhouette score
        score = silhouette_score(embeddings, kmeans.labels_)
        silhouette_scores.append(score)
        print(f"Clusters: {k}, Silhouette Score: {score:.3f}")
    
    # Find the elbow point using the second derivative
    inertias = np.array(inertias)
    diffs = np.diff(inertias)
    diffs2 = np.diff(diffs)
    elbow_idx = np.argmax(diffs2) + 2
    
    # Find the number of clusters with the highest silhouette score
    best_silhouette_idx = np.argmax(silhouette_scores) + 2
    
    # Choose the number of clusters that balances the elbow point and silhouette score
    optimal_clusters = min(elbow_idx, best_silhouette_idx)
    print(f"Optimal number of clusters: {optimal_clusters}")
    
    return optimal_clusters

def find_optimal_weight(embeddings, channels, subscription_graph):
    """
    Find the optimal weight for subscription relationships using silhouette analysis
    """
    print("Finding optimal subscription relationship weight...")
    
    weights = np.linspace(0.1, 0.5, 5)  # Test weights from 0.1 to 0.5
    best_score = -1
    best_weight = 0.3
    
    for weight in weights:
        # Enhance embeddings with current weight
        enhanced = enhance_embeddings_with_relationships(embeddings, channels, subscription_graph, weight=weight)
        
        # Create clusters and calculate silhouette score
        clusters = create_clusters(enhanced, channels, n_clusters=7)  # Use 7 clusters for consistency
        score = clusters.get('silhouette_score', -1)
        
        print(f"Weight: {weight:.2f}, Silhouette Score: {score:.3f}")
        
        if score > best_score:
            best_score = score
            best_weight = weight
    
    print(f"Optimal weight: {best_weight:.2f}")
    return best_weight

def name_clusters(clusters, channels):
    """
    Automatically name clusters based on channel content and engagement metrics
    with improved thresholds and category detection
    """
    print("Naming clusters based on content categories and engagement patterns...")
    
    # Ensure channels are grouped by cluster
    if 'channels' not in clusters:
        print("No channel data in clusters, cannot name clusters")
        return clusters
        
    # Calculate global engagement statistics for better thresholding
    all_engagement_rates = []
    for cluster_channels in clusters['channels'].values():
        for ch in cluster_channels:
            if 'engagement_rate' in ch:
                all_engagement_rates.append(float(ch.get('engagement_rate', 0)))
    
    if all_engagement_rates:
        # Calculate engagement thresholds using percentiles
        engagement_thresholds = {
            'high': np.percentile(all_engagement_rates, 75),
            'medium': np.percentile(all_engagement_rates, 50),
            'low': np.percentile(all_engagement_rates, 25)
        }
    else:
        engagement_thresholds = {'high': 0.1, 'medium': 0.05, 'low': 0.01}
    
    # For each cluster, analyze all text and determine the most likely category
    for cluster_label, cluster_channels in clusters['channels'].items():
        # Collect all text and keywords from channels in this cluster
        all_text = []
        all_keywords = []
        
        for ch in cluster_channels:
            # Combine title, description and keywords
            channel_text = f"{ch.get('title', '')} {ch.get('description', '')}"
            all_text.append(channel_text.lower())
            
            # Add keywords if available
            if 'keywords' in ch:
                all_keywords.extend([k.lower() for k in ch['keywords']])
        
        # Join all text
        combined_text = " ".join(all_text)
        
        # Calculate average engagement metrics for the cluster
        engagement_rates = [float(ch.get('engagement_rate', 0)) for ch in cluster_channels]
        avg_engagement = np.mean(engagement_rates) if engagement_rates else 0
        
        # Count occurrences of category keywords with boosted weights for keywords
        category_scores = {}
        for category, keywords in TOPIC_MAP.items():
            # Score from text content
            text_score = sum(combined_text.count(keyword.lower()) for keyword in keywords)
            
            # Score from channel keywords (weighted higher)
            keyword_score = sum(all_keywords.count(keyword.lower()) * 2 for keyword in keywords)
            
            # Combined score
            category_scores[category] = text_score + keyword_score
            
        # Find the most common categories
        top_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Generate cluster name based on top categories and engagement
        if top_categories and top_categories[0][1] > 0:
            # Use the top category
            primary_category = top_categories[0][0]
            
            # Add a secondary category if it's also significant
            if len(top_categories) > 1 and top_categories[1][1] > top_categories[0][1] * 0.6:
                cluster_name = f"{primary_category} & {top_categories[1][0]}"
            else:
                cluster_name = primary_category
                
            # Add engagement level indicator based on percentile thresholds
            if avg_engagement >= engagement_thresholds['high']:
                cluster_name += " (High Engagement)"
            elif avg_engagement >= engagement_thresholds['medium']:
                cluster_name += " (Medium Engagement)"
            else:
                cluster_name += " (Low Engagement)"
        else:
            # Fallback if no clear category is found
            cluster_name = f"Cluster {cluster_label}"
            
        # Add the name to the cluster data
        clusters.setdefault('cluster_names', {})[cluster_label] = cluster_name
        
        # Add additional metadata about the cluster
        clusters.setdefault('cluster_metadata', {})[cluster_label] = {
            'avg_engagement': avg_engagement,
            'size': len(cluster_channels),
            'top_categories': [cat for cat, _ in top_categories[:3]],
            'engagement_level': 'High' if avg_engagement >= engagement_thresholds['high'] else 
                              'Medium' if avg_engagement >= engagement_thresholds['medium'] else 'Low'
        }
    
    return clusters

def clean_input(prompt, default="10"):
    """Clean user input by removing ANSI escape sequences and whitespace."""
    user_input = input(prompt)
    # Remove ANSI escape sequences and whitespace
    cleaned_input = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', user_input).strip()
    return cleaned_input or default

def main():
    """Main execution function"""
    # Load environment variables
    load_dotenv()
    
    print("========= Enhanced YouTube Cluster App =========")
    
    # Authenticate
    youtube = authenticate()
    
    # Load existing subscriptions
    print("Loading saved subscriptions...")
    channels = load_subscriptions()
    print(f"Loaded {len(channels)} subscriptions")
    
    # Vectorize channels
    print(f"Vectorizing {len(channels)} channels...")
    channels, embeddings = vectorize_channels(channels)
    
    # Build subscription graph
    subscription_graph = build_subscription_graph(youtube, channels)
    
    # Find optimal number of clusters and weight
    n_clusters = find_optimal_clusters(embeddings)
    subscription_weight = find_optimal_weight(embeddings, channels, subscription_graph)
    
    # Enhance embeddings with subscription relationships
    enhanced_embeddings = enhance_embeddings_with_relationships(
        embeddings, channels, subscription_graph, weight=subscription_weight
    )
    
    # Create clusters with enhanced embeddings
    print(f"Creating {n_clusters} clusters...")
    clusters = create_clusters(enhanced_embeddings, channels, n_clusters=n_clusters)
    
    # Name clusters by category
    clusters = name_clusters(clusters, channels)
    
    # Save enhanced clusters
    enhanced_clusters_file = os.path.join(os.getenv('DATA_DIR', './output'), 'enhanced_clusters.json')
    with open(enhanced_clusters_file, 'w') as f:
        json.dump(clusters, f, cls=NumpyEncoder)
    
    print(f"Enhanced clusters saved to: {enhanced_clusters_file}")
    
    # Print cluster categories
    print("\nCluster Categories:")
    # Convert all cluster labels to strings for consistent sorting
    cluster_items = [(str(k), v) for k, v in clusters['cluster_names'].items()]
    for cluster_label, cluster_name in sorted(cluster_items, key=lambda x: int(x[0]) if x[0].isdigit() else float('-inf')):
        print(f"Cluster {cluster_label}: {cluster_name}")
    
    # Generate and save visualization using the visualize module
    from clustering.visualize import generate_visualization
    print("\nGenerating visualization...")
    viz_file = generate_visualization(clusters, filename='enhanced_visualization.html')
    print(f"Visualization saved to: {viz_file}")
    print("Opening visualization in browser...")
    
    # Open visualization in browser
    try:
        import webbrowser
        webbrowser.open(viz_file)
    except:
        print("Please open the visualization file manually in your browser")
    
    print("Enhanced clustering complete!")

if __name__ == "__main__":
    main() 