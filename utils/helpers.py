"""
Helper utilities for YouTube Cluster App
"""

import os
import re
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime


def ensure_dir(directory):
    """
    Create directory if it doesn't exist
    
    Args:
        directory: Directory path to create
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def format_subscriber_count(count: Optional[str]) -> str:
    """
    Format subscriber count for display
    
    Args:
        count: Subscriber count as string or None
        
    Returns:
        Formatted subscriber count
    """
    if count is None:
        return "N/A"
    
    try:
        # Convert to integer
        count_int = int(count)
        
        # Format based on magnitude
        if count_int >= 1_000_000:
            return f"{count_int/1_000_000:.1f}M"
        elif count_int >= 1_000:
            return f"{count_int/1_000:.1f}K"
        else:
            return str(count_int)
    except (ValueError, TypeError):
        return str(count)


def extract_topics_from_url(url: str) -> str:
    """
    Extract topic name from Freebase topic URL
    
    Args:
        url: Freebase topic URL
        
    Returns:
        Readable topic name
    """
    # Extract the last part of the URL
    topic = url.split('/')[-1]
    
    # Convert to readable format
    topic = topic.replace('_', ' ')
    
    return topic


def safe_api_call(func, *args, max_retries=3, **kwargs):
    """
    Safely make API calls with retries
    
    Args:
        func: Function to call
        *args: Positional arguments for func
        max_retries: Maximum number of retries
        **kwargs: Keyword arguments for func
        
    Returns:
        Function result
    """
    retries = 0
    last_error = None
    
    while retries < max_retries:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_error = e
            retries += 1
            
            # Wait longer between each retry
            time.sleep(2 ** retries)  # Exponential backoff
    
    # Raise the last error if all retries failed
    raise last_error


def save_json(data, filepath, pretty=True):
    """
    Save data to JSON file
    
    Args:
        data: Data to save
        filepath: File path to save to
        pretty: Whether to format the JSON nicely
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        if pretty:
            json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            json.dump(data, f, ensure_ascii=False)


def generate_timestamp():
    """
    Generate a timestamp string for filenames
    
    Returns:
        Timestamp string
    """
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def extract_channel_id_from_url(url: str) -> Optional[str]:
    """
    Extract channel ID from a YouTube URL
    
    Args:
        url: YouTube URL
        
    Returns:
        Channel ID if found, None otherwise
    """
    # Handle channel URLs
    channel_match = re.search(r'youtube\.com/channel/([^/\?&]+)', url)
    if channel_match:
        return channel_match.group(1)
    
    # Handle user URLs
    user_match = re.search(r'youtube\.com/user/([^/\?&]+)', url)
    if user_match:
        # Note: this returns the username, not the channel ID
        # Would need an API call to resolve to channel ID
        return None
    
    # Handle custom URLs
    custom_match = re.search(r'youtube\.com/c/([^/\?&]+)', url)
    if custom_match:
        # Note: this returns the custom name, not the channel ID
        # Would need an API call to resolve to channel ID
        return None
    
    return None
