"""
Channel text vectorization module
"""

import os
from typing import Dict, List, Any, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
import re


def get_model():
    """
    Get or initialize the text embedding model
    
    Returns:
        SentenceTransformer model instance
    """
    model_name = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    return SentenceTransformer(model_name)


def prepare_channel_text(channel: Dict[str, Any]) -> str:
    """
    Prepare channel data for vectorization by combining relevant text fields
    
    Args:
        channel: Channel data dictionary
        
    Returns:
        Combined text representation of the channel
    """
    # Combine channel title and description
    text = f"{channel.get('title', '')} - {channel.get('description', '')}"
    
    # Add topics if available
    if 'topics' in channel and channel['topics']:
        # Extract just the topic names from the URLs
        topics = []
        for topic_url in channel['topics']:
            # Extract the last part of the URL which is usually the topic name
            topic_name = topic_url.split('/')[-1].replace('_', ' ')
            topics.append(topic_name)
        
        # Add topics to text
        text += f" - Topics: {', '.join(topics)}"
    
    return text


def extract_metadata_features(channel: Dict) -> Dict:
    """
    Extract and normalize metadata features from a channel
    """
    features = {}
    
    # Normalize subscriber count
    sub_count = channel.get('subscriber_count', 0)
    features['subscriber_count'] = np.log1p(sub_count)  # Log transform for better scaling
    
    # Normalize video count
    video_count = channel.get('video_count', 0)
    features['video_count'] = np.log1p(video_count)
    
    # Calculate engagement metrics
    views = channel.get('view_count', 0)
    features['views_per_video'] = views / max(video_count, 1)
    
    # Extract keywords from description
    description = channel.get('description', '').lower()
    features['has_social_links'] = bool(re.search(r'(twitter|facebook|instagram|tiktok)', description))
    features['has_website'] = bool(re.search(r'(http|www)', description))
    
    return features


def vectorize_channels(channels: List[Dict]) -> Tuple[List[Dict], np.ndarray]:
    """
    Vectorize channel content and metadata
    Returns enhanced channel data and combined embeddings
    """
    print(f"Vectorizing {len(channels)} channels...")
    
    # Load the sentence transformer model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print(f"Using model with {model.get_sentence_embedding_dimension()}-dimensional embeddings")
    
    # Prepare text for embedding
    texts = []
    for channel in channels:
        # Combine title and description
        text = f"{channel.get('title', '')} {channel.get('description', '')}"
        texts.append(text)
    
    # Generate embeddings in batches
    batch_size = 32
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_embeddings = model.encode(batch, show_progress_bar=False)
        embeddings.append(batch_embeddings)
        print(f"Processed batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
    
    # Combine all embeddings
    content_embeddings = np.vstack(embeddings)
    
    # Extract metadata features
    metadata_features = []
    for channel in channels:
        features = extract_metadata_features(channel)
        metadata_features.append(list(features.values()))
    
    # Normalize metadata features
    metadata_features = np.array(metadata_features)
    metadata_features = (metadata_features - metadata_features.mean(axis=0)) / metadata_features.std(axis=0)
    
    # Combine content and metadata embeddings
    combined_embeddings = np.hstack([content_embeddings, metadata_features])
    
    # Update channel data with metadata features
    for i, channel in enumerate(channels):
        channel['metadata_features'] = metadata_features[i].tolist()
    
    return channels, combined_embeddings


def load_embeddings_from_file(filename):
    """
    Load pre-computed embeddings from file
    
    Args:
        filename: Path to the embeddings file
        
    Returns:
        numpy array of embeddings
    """
    return np.load(filename)


def save_embeddings(embeddings, filename=None):
    """
    Save embeddings to file
    
    Args:
        embeddings: numpy array of embeddings
        filename: Output filename (optional)
    """
    data_dir = os.getenv('DATA_DIR', './output')
    os.makedirs(data_dir, exist_ok=True)
    
    # Use default filename if none provided
    if filename is None:
        filename = f"{data_dir}/embeddings.npy"
    
    # Save to file
    np.save(filename, embeddings)
