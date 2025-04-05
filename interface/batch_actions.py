"""
Batch actions module for YouTube subscriptions
"""

import time
from typing import List, Dict, Any


def batch_subscribe(youtube_client, channel_ids: List[str]) -> Dict[str, Any]:
    """
    Subscribe to multiple channels at once
    
    Args:
        youtube_client: Authenticated YouTube API client
        channel_ids: List of channel IDs to subscribe to
        
    Returns:
        Dictionary with results
    """
    results = {
        'success': [],
        'failed': [],
        'total': len(channel_ids),
        'success_count': 0,
        'failed_count': 0
    }
    
    for channel_id in channel_ids:
        try:
            # Create subscription resource
            subscription_body = {
                'snippet': {
                    'resourceId': {
                        'kind': 'youtube#channel',
                        'channelId': channel_id
                    }
                }
            }
            
            # Execute API request
            request = youtube_client.subscriptions().insert(
                part='snippet',
                body=subscription_body
            )
            response = request.execute()
            
            # Record success
            results['success'].append({
                'channel_id': channel_id,
                'title': response['snippet']['title'] if 'snippet' in response else 'Unknown'
            })
            results['success_count'] += 1
            
            # Respect API quota limits
            time.sleep(0.5)
        
        except Exception as e:
            # Record failure
            results['failed'].append({
                'channel_id': channel_id,
                'error': str(e)
            })
            results['failed_count'] += 1
    
    return results


def batch_unsubscribe(youtube_client, subscription_ids: List[str]) -> Dict[str, Any]:
    """
    Unsubscribe from multiple channels at once
    
    Args:
        youtube_client: Authenticated YouTube API client
        subscription_ids: List of subscription IDs to remove
        
    Returns:
        Dictionary with results
    """
    results = {
        'success': [],
        'failed': [],
        'total': len(subscription_ids),
        'success_count': 0,
        'failed_count': 0
    }
    
    for subscription_id in subscription_ids:
        try:
            # Execute API request
            request = youtube_client.subscriptions().delete(id=subscription_id)
            request.execute()
            
            # Record success
            results['success'].append({
                'subscription_id': subscription_id
            })
            results['success_count'] += 1
            
            # Respect API quota limits
            time.sleep(0.5)
        
        except Exception as e:
            # Record failure
            results['failed'].append({
                'subscription_id': subscription_id,
                'error': str(e)
            })
            results['failed_count'] += 1
    
    return results


def find_subscription_id(youtube_client, channel_id: str) -> str:
    """
    Find subscription ID for a channel
    
    Args:
        youtube_client: Authenticated YouTube API client
        channel_id: Channel ID to find subscription for
        
    Returns:
        Subscription ID if found, None otherwise
    """
    request = youtube_client.subscriptions().list(
        part="snippet",
        mine=True,
        maxResults=50,
        forChannelId=channel_id
    )
    response = request.execute()
    
    if 'items' in response and len(response['items']) > 0:
        return response['items'][0]['id']
    
    return None


def batch_channel_action(youtube_client, channel_ids: List[str], action: str,
                         source_cluster: str = None) -> Dict[str, Any]:
    """
    Perform batch actions on channels
    
    Args:
        youtube_client: Authenticated YouTube API client
        channel_ids: List of channel IDs to act on
        action: Action to perform ('subscribe', 'unsubscribe')
        source_cluster: Cluster ID these channels belong to (optional)
        
    Returns:
        Dictionary with results
    """
    if action.lower() == 'subscribe':
        return batch_subscribe(youtube_client, channel_ids)
    
    elif action.lower() == 'unsubscribe':
        # First get subscription IDs for the channels
        subscription_ids = []
        for channel_id in channel_ids:
            subscription_id = find_subscription_id(youtube_client, channel_id)
            if subscription_id:
                subscription_ids.append(subscription_id)
        
        return batch_unsubscribe(youtube_client, subscription_ids)
    
    else:
        return {
            'error': f"Unsupported action: {action}",
            'supported_actions': ['subscribe', 'unsubscribe']
        }
