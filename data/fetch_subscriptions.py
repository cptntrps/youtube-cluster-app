"""
YouTube subscription fetching module
"""

import time
from typing import Dict, List, Any


def fetch_all_subscriptions(youtube_client) -> List[Dict[str, Any]]:
    """
    Fetches all subscriptions from the authenticated YouTube account
    
    Args:
        youtube_client: Authenticated YouTube API client
        
    Returns:
        List of subscription objects with channel info
    """
    subscriptions = []
    next_page_token = None
    
    print("Fetching subscriptions...")
    
    # Loop to handle pagination
    while True:
        # Get list of subscriptions
        request = youtube_client.subscriptions().list(
            part="snippet,contentDetails",
            mine=True,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        
        # Extract useful information
        for item in response['items']:
            channel_id = item['snippet']['resourceId']['channelId']
            
            # Extract relevant subscription data
            subscription_data = {
                'channel_id': channel_id,
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'published_at': item['snippet']['publishedAt'],
                'thumbnail': item['snippet']['thumbnails']['default']['url']
            }
            
            # Add to our list
            subscriptions.append(subscription_data)
        
        # Get channel details for each subscription
        subscriptions = enrich_with_channel_data(youtube_client, subscriptions)
        
        # Check if there are more pages
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
            
        # Respect YouTube API quota limits with a small delay
        time.sleep(0.5)
    
    return subscriptions


def enrich_with_channel_data(youtube_client, subscriptions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enriches subscription data with additional channel information
    
    Args:
        youtube_client: Authenticated YouTube API client
        subscriptions: List of subscription objects
        
    Returns:
        Enriched list of subscription objects
    """
    # Process channels in batches to minimize API calls
    batch_size = 50
    
    for i in range(0, len(subscriptions), batch_size):
        batch = subscriptions[i:i+batch_size]
        channel_ids = [sub['channel_id'] for sub in batch]
        
        # Request channel details
        channels_request = youtube_client.channels().list(
            part="snippet,statistics,topicDetails",
            id=",".join(channel_ids)
        )
        channels_response = channels_request.execute()
        
        # Map channel data to subscriptions
        channel_data = {item['id']: item for item in channels_response['items']}
        
        for sub in batch:
            channel_id = sub['channel_id']
            if channel_id in channel_data:
                channel = channel_data[channel_id]
                
                # Add statistics
                if 'statistics' in channel:
                    sub['subscriber_count'] = channel['statistics'].get('subscriberCount')
                    sub['video_count'] = channel['statistics'].get('videoCount')
                    sub['view_count'] = channel['statistics'].get('viewCount')
                
                # Add topics if available
                if 'topicDetails' in channel and 'topicCategories' in channel['topicDetails']:
                    sub['topics'] = channel['topicDetails']['topicCategories']
        
        # Respect YouTube API quota limits
        time.sleep(0.5)
    
    return subscriptions
