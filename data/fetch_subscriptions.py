"""
Enhanced YouTube subscription fetching module with additional data collection
"""

import time
from typing import Dict, List, Any
from datetime import datetime, timedelta


def fetch_all_subscriptions(youtube_client) -> List[Dict[str, Any]]:
    """
    Fetches all subscriptions from the authenticated YouTube account with enhanced data
    
    Args:
        youtube_client: Authenticated YouTube API client
        
    Returns:
        List of subscription objects with enriched channel info
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
                'thumbnail': item['snippet']['thumbnails']['default']['url'],
                'subscription_date': item['snippet']['publishedAt']  # When you subscribed
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
    Enriches subscription data with additional channel information including recent videos and engagement metrics
    
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
            part="snippet,statistics,topicDetails,brandingSettings,contentDetails",
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
                
                # Add branding settings
                if 'brandingSettings' in channel:
                    branding = channel['brandingSettings']
                    if 'channel' in branding:
                        sub['keywords'] = branding['channel'].get('keywords', '').split('|')
                        sub['country'] = branding['channel'].get('country', '')
                        sub['default_language'] = branding['channel'].get('defaultLanguage', '')
                
                # Fetch recent videos and engagement metrics
                sub.update(fetch_recent_videos_and_engagement(youtube_client, channel_id))
        
        # Respect YouTube API quota limits
        time.sleep(0.5)
    
    return subscriptions


def fetch_recent_videos_and_engagement(youtube_client, channel_id: str) -> Dict[str, Any]:
    """
    Fetches recent videos and engagement metrics for a channel
    
    Args:
        youtube_client: Authenticated YouTube API client
        channel_id: YouTube channel ID
        
    Returns:
        Dictionary containing recent video data and engagement metrics
    """
    try:
        # Get recent videos (last 10)
        videos_request = youtube_client.search().list(
            part="snippet",
            channelId=channel_id,
            order="date",
            type="video",
            maxResults=10
        )
        videos_response = videos_request.execute()
        
        recent_videos = []
        total_views = 0
        total_likes = 0
        total_comments = 0
        
        # Process each video
        for item in videos_response.get('items', []):
            video_id = item['id']['videoId']
            
            # Get video statistics
            video_request = youtube_client.videos().list(
                part="statistics,contentDetails",
                id=video_id
            )
            video_response = video_request.execute()
            
            if video_response['items']:
                video_data = video_response['items'][0]
                stats = video_data['statistics']
                
                video_info = {
                    'video_id': video_id,
                    'title': item['snippet']['title'],
                    'published_at': item['snippet']['publishedAt'],
                    'views': int(stats.get('viewCount', 0)),
                    'likes': int(stats.get('likeCount', 0)),
                    'comments': int(stats.get('commentCount', 0)),
                    'duration': video_data['contentDetails']['duration']
                }
                
                recent_videos.append(video_info)
                total_views += video_info['views']
                total_likes += video_info['likes']
                total_comments += video_info['comments']
        
        # Calculate engagement metrics
        engagement_metrics = {
            'recent_videos': recent_videos,
            'avg_views_per_video': total_views / len(recent_videos) if recent_videos else 0,
            'avg_likes_per_video': total_likes / len(recent_videos) if recent_videos else 0,
            'avg_comments_per_video': total_comments / len(recent_videos) if recent_videos else 0,
            'engagement_rate': (total_likes + total_comments) / total_views if total_views > 0 else 0
        }
        
        return engagement_metrics
        
    except Exception as e:
        print(f"Error fetching video data for channel {channel_id}: {str(e)}")
        return {
            'recent_videos': [],
            'avg_views_per_video': 0,
            'avg_likes_per_video': 0,
            'avg_comments_per_video': 0,
            'engagement_rate': 0
        }
