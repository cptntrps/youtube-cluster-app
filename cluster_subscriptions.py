#!/usr/bin/env python3
"""
Simple script to cluster YouTube subscriptions without Streamlit
"""

import os
from dotenv import load_dotenv

# Import project modules
from auth.oauth import authenticate
from data.store import load_subscriptions
from clustering.vectorize import vectorize_channels
from clustering.cluster import create_clusters
from clustering.visualize import generate_visualization

def main():
    """Main execution function"""
    # Load environment variables
    load_dotenv()
    
    print("========= YouTube Cluster App - CLI Version =========")
    
    # Authentication is already done, so we can load subscriptions
    print("Loading saved subscriptions...")
    subscriptions = load_subscriptions()
    print(f"Loaded {len(subscriptions)} subscriptions")
    
    # Number of clusters
    n_clusters = int(input("How many clusters do you want to create? [10]: ") or "10")
    
    # Vectorize channels
    print(f"Vectorizing {len(subscriptions)} channels...")
    channels, embeddings = vectorize_channels(subscriptions)
    
    # Create clusters
    print(f"Creating {n_clusters} clusters...")
    clusters = create_clusters(embeddings, channels, n_clusters=n_clusters)
    
    # Generate and save visualization
    print("Generating visualization...")
    viz_file = generate_visualization(clusters)
    print(f"Visualization saved to: {viz_file}")
    print("You can open this HTML file in your browser to view the cluster visualization.")
    
    print("Clustering complete!")

if __name__ == "__main__":
    main() 