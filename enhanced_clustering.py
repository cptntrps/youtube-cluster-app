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
    Enhance channel embeddings with subscription relationship data
    Weight determines how much influence subscription relationships have (0.0-1.0)
    """
    print("Enhancing embeddings with subscription relationships...")
    
    # Create a mapping from channel_id to embedding index
    channel_id_to_index = {channel.get('channel_id'): i for i, channel in enumerate(channels) if channel.get('channel_id')}
    
    # Create a copy of the original embeddings
    enhanced_embeddings = embeddings.copy()
    
    # Enhance embeddings based on subscription relationships
    for channel_id, subscribed_to in subscription_graph.items():
        if channel_id not in channel_id_to_index:
            continue
            
        channel_index = channel_id_to_index[channel_id]
        
        # Find embeddings of subscribed channels
        subscribed_embeddings = []
        for sub_id in subscribed_to:
            if sub_id in channel_id_to_index:
                sub_index = channel_id_to_index[sub_id]
                subscribed_embeddings.append(embeddings[sub_index])
        
        # If this channel subscribes to others, enhance its embedding
        if subscribed_embeddings:
            # Calculate average embedding of subscribed channels
            avg_sub_embedding = np.mean(subscribed_embeddings, axis=0)
            
            # Blend original with subscription relationship data
            enhanced_embeddings[channel_index] = (1 - weight) * embeddings[channel_index] + weight * avg_sub_embedding
    
    return enhanced_embeddings

def name_clusters(clusters, channels):
    """
    Automatically name clusters based on channel content
    """
    print("Naming clusters based on content categories...")
    
    # Ensure channels are grouped by cluster
    if 'channels' not in clusters:
        print("No channel data in clusters, cannot name clusters")
        return clusters
        
    # For each cluster, analyze all text and determine the most likely category
    for cluster_label, cluster_channels in clusters['channels'].items():
        # Collect all text from channels in this cluster
        all_text = " ".join([
            f"{ch.get('title', '')} {ch.get('description', '')}" 
            for ch in cluster_channels
        ]).lower()
        
        # Count occurrences of category keywords
        category_scores = {}
        for category, keywords in TOPIC_MAP.items():
            score = sum(all_text.count(keyword.lower()) for keyword in keywords)
            category_scores[category] = score
            
        # Find the most common categories
        top_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Generate cluster name based on top categories
        if top_categories and top_categories[0][1] > 0:
            # Use the top category if it has a significant score
            primary_category = top_categories[0][0]
            
            # Add a secondary category if it's also significant
            if len(top_categories) > 1 and top_categories[1][1] > top_categories[0][1] * 0.7:
                cluster_name = f"{primary_category} & {top_categories[1][0]}"
            else:
                cluster_name = primary_category
        else:
            # Fallback if no clear category is found
            cluster_name = f"Cluster {cluster_label}"
            
        # Add the name to the cluster data
        clusters.setdefault('cluster_names', {})[cluster_label] = cluster_name
    
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
    
    # Get number of clusters with robust input handling
    n_clusters = int(clean_input("How many clusters do you want to create? [10]: "))
    
    # Get subscription weight with robust input handling
    subscription_weight = float(clean_input("Enter weight for subscription relationships (0.0-1.0) [0.3]: ", "0.3"))
    
    # Vectorize channels
    print(f"Vectorizing {len(channels)} channels...")
    channels, embeddings = vectorize_channels(channels)
    
    # Build subscription graph
    subscription_graph = build_subscription_graph(youtube, channels)
    
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