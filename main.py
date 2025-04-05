#!/usr/bin/env python3
"""
YouTube Cluster App - Main Entry Point
"""

import os
import argparse
from dotenv import load_dotenv

# Import project modules
from auth.oauth import authenticate
from data.fetch_subscriptions import fetch_all_subscriptions
from data.store import save_subscriptions, load_subscriptions
from clustering.vectorize import vectorize_channels
from clustering.cluster import create_clusters
from clustering.visualize import generate_visualization

def main():
    """Main execution function"""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='YouTube Cluster App')
    parser.add_argument('--fetch', action='store_true', help='Fetch subscriptions from YouTube')
    parser.add_argument('--cluster', action='store_true', help='Generate clusters')
    parser.add_argument('--visualize', action='store_true', help='Generate visualization')
    parser.add_argument('--n-clusters', type=int, default=int(os.getenv('DEFAULT_NUM_CLUSTERS', 10)),
                        help='Number of clusters to generate')
    args = parser.parse_args()
    
    # Authentication
    youtube = authenticate()
    
    if args.fetch:
        print("Fetching subscriptions...")
        subscriptions = fetch_all_subscriptions(youtube)
        save_subscriptions(subscriptions)
        print(f"Saved {len(subscriptions)} subscriptions")
    
    if args.cluster or args.visualize:
        subscriptions = load_subscriptions()
        
        if args.cluster:
            print(f"Vectorizing {len(subscriptions)} channels...")
            vectors = vectorize_channels(subscriptions)
            
            print(f"Creating {args.n_clusters} clusters...")
            clusters = create_clusters(vectors, n_clusters=args.n_clusters)
            
            # Save results
            save_clusters(clusters)
            print(f"Saved cluster data to {os.getenv('DATA_DIR', './output')}/clusters.json")
        
        if args.visualize:
            print("Generating visualization...")
            generate_visualization()
            print("Visualization saved to output directory")
    
    if not (args.fetch or args.cluster or args.visualize):
        print("No actions specified. Use --help to see available options.")
        print("Alternatively, run 'streamlit run interface/streamlit_app.py' to start the GUI.")

if __name__ == "__main__":
    main()
