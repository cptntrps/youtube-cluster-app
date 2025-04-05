"""
Channel text vectorization module
"""

import os
from typing import Dict, List, Any, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer


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


def vectorize_channels(channels: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], np.ndarray]:
    """
    Convert channel data to vector embeddings
    
    Args:
        channels: List of channel dictionaries
        
    Returns:
        Tuple of (channels with embeddings, embedding matrix)
    """
    # Initialize the embedding model
    model = get_model()
    print(f"Using model: {model.get_sentence_embedding_dimension()}-dimensional embeddings")
    
    # Prepare text for each channel
    texts = []
    for channel in channels:
        channel_text = prepare_channel_text(channel)
        texts.append(channel_text)
        
        # Store the prepared text for debugging
        channel['vectorized_text'] = channel_text
    
    # Convert texts to embeddings
    embeddings = model.encode(texts, show_progress_bar=True)
    
    # Add embeddings to channel data
    for i, channel in enumerate(channels):
        # We don't store the full embedding in the channel dict to keep it smaller
        # Just store the index for reference
        channel['embedding_index'] = i
    
    return channels, embeddings


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
