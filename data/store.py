"""
Data storage module for YouTube Cluster App
"""

import os
import json
import csv
from datetime import datetime
from typing import Dict, List, Any


def save_subscriptions(subscriptions: List[Dict[str, Any]], format='csv'):
    """
    Save subscription data to file
    
    Args:
        subscriptions: List of subscription data
        format: Output format (csv or json)
    """
    # Create output directory if it doesn't exist
    data_dir = os.getenv('DATA_DIR', './output')
    os.makedirs(data_dir, exist_ok=True)
    
    # Add timestamp to filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format == 'csv':
        # Save as CSV
        filename = f"{data_dir}/subscriptions.csv"
        latest_filename = f"{data_dir}/subscriptions_{timestamp}.csv"
        
        if subscriptions:
            # Get fieldnames from first subscription
            fieldnames = list(subscriptions[0].keys())
            
            # Write to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for subscription in subscriptions:
                    writer.writerow(subscription)
            
            # Also save timestamped version
            with open(latest_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for subscription in subscriptions:
                    writer.writerow(subscription)
    else:
        # Save as JSON
        filename = f"{data_dir}/subscriptions.json"
        latest_filename = f"{data_dir}/subscriptions_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(subscriptions, f, ensure_ascii=False, indent=4)
        
        with open(latest_filename, 'w', encoding='utf-8') as f:
            json.dump(subscriptions, f, ensure_ascii=False, indent=4)


def load_subscriptions(format='csv') -> List[Dict[str, Any]]:
    """
    Load subscription data from file
    
    Args:
        format: Input format (csv or json)
        
    Returns:
        List of subscription data
    """
    data_dir = os.getenv('DATA_DIR', './output')
    
    if format == 'csv':
        filename = f"{data_dir}/subscriptions.csv"
        
        if not os.path.exists(filename):
            print(f"Error: Subscription file {filename} not found")
            return []
        
        subscriptions = []
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                subscriptions.append(row)
        
        return subscriptions
    else:
        filename = f"{data_dir}/subscriptions.json"
        
        if not os.path.exists(filename):
            print(f"Error: Subscription file {filename} not found")
            return []
        
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)


def save_clusters(clusters, filename=None):
    """
    Save cluster data to file
    
    Args:
        clusters: Cluster data
        filename: Output filename (optional)
    """
    data_dir = os.getenv('DATA_DIR', './output')
    os.makedirs(data_dir, exist_ok=True)
    
    # Use default filename if none provided
    if filename is None:
        filename = f"{data_dir}/clusters.json"
    
    # Add timestamp version
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    timestamp_filename = f"{data_dir}/clusters_{timestamp}.json"
    
    # Save to file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(clusters, f, ensure_ascii=False, indent=4)
    
    # Save timestamped version
    with open(timestamp_filename, 'w', encoding='utf-8') as f:
        json.dump(clusters, f, ensure_ascii=False, indent=4)


def load_clusters(filename=None):
    """
    Load cluster data from file
    
    Args:
        filename: Input filename (optional)
        
    Returns:
        Cluster data
    """
    data_dir = os.getenv('DATA_DIR', './output')
    
    # Use default filename if none provided
    if filename is None:
        filename = f"{data_dir}/clusters.json"
    
    if not os.path.exists(filename):
        print(f"Error: Cluster file {filename} not found")
        return None
    
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)
