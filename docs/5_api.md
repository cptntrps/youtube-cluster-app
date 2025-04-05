# API Documentation

## Data Structures

### 1. Channel Object
```json
{
  "channel_id": "UC...",
  "title": "Channel Name",
  "description": "Channel description text",
  "published_at": "2020-01-01T00:00:00Z",
  "thumbnail": "https://...",
  "subscriber_count": 1000000,
  "video_count": 500,
  "view_count": 50000000,
  "topics": [
    "https://en.wikipedia.org/wiki/Technology",
    "https://en.wikipedia.org/wiki/Education"
  ],
  "metadata_features": [1.2, 0.8, 0.5, ...],
  "cluster": 1,
  "cluster_name": "Technology Education"
}
```

### 2. Cluster Object
```json
{
  "cluster_id": 1,
  "name": "Technology Education",
  "size": 25,
  "centroid": [1.2, 0.8, 0.5, ...],
  "channels": ["UC...", "UC..."],
  "topics": ["Technology", "Education"],
  "avg_subscribers": 1000000,
  "avg_views": 50000000
}
```

### 3. Subscription Graph
```json
{
  "nodes": [
    {
      "id": "UC...",
      "weight": 1.0,
      "features": [...]
    }
  ],
  "edges": [
    {
      "source": "UC...",
      "target": "UC...",
      "weight": 0.5
    }
  ]
}
```

## YouTube Data API Integration

### 1. Channel Information
```python
GET https://www.googleapis.com/youtube/v3/channels
```
Parameters:
- `part`: snippet,statistics,topicDetails
- `id`: Channel ID
- `key`: API key

Response:
```json
{
  "items": [{
    "id": "UC...",
    "snippet": {...},
    "statistics": {...},
    "topicDetails": {...}
  }]
}
```

### 2. Subscriptions
```python
GET https://www.googleapis.com/youtube/v3/subscriptions
```
Parameters:
- `part`: snippet
- `channelId`: Source channel ID
- `maxResults`: Results per page (default: 50)
- `pageToken`: Next page token
- `key`: API key

Response:
```json
{
  "items": [{
    "snippet": {
      "resourceId": {
        "channelId": "UC..."
      }
    }
  }],
  "nextPageToken": "..."
}
```

## Internal APIs

### 1. Channel Vectorization

#### Generate Channel Embedding
```python
def generate_channel_embedding(
    channel_data: dict,
    model: SentenceTransformer
) -> np.ndarray:
    """
    Generate text embedding for channel data.
    
    Args:
        channel_data (dict): Channel information
        model (SentenceTransformer): Embedding model
        
    Returns:
        np.ndarray: Channel embedding vector
    """
```

#### Generate Engagement Features
```python
def generate_engagement_features(
    channel_data: dict
) -> np.ndarray:
    """
    Generate engagement metrics vector.
    
    Args:
        channel_data (dict): Channel statistics
        
    Returns:
        np.ndarray: Engagement features vector
    """
```

### 2. Clustering Engine

#### Create Clusters
```python
def create_clusters(
    embeddings: np.ndarray,
    n_clusters: int = 7,
    min_samples: int = 5
) -> Tuple[np.ndarray, DBSCAN]:
    """
    Create channel clusters using DBSCAN.
    
    Args:
        embeddings (np.ndarray): Channel embeddings
        n_clusters (int): Target number of clusters
        min_samples (int): Minimum samples per cluster
        
    Returns:
        Tuple[np.ndarray, DBSCAN]: Cluster labels and model
    """
```

#### Name Clusters
```python
def name_clusters(
    clusters: List[dict],
    channels: List[dict]
) -> List[str]:
    """
    Generate descriptive names for clusters.
    
    Args:
        clusters (List[dict]): Cluster information
        channels (List[dict]): Channel data
        
    Returns:
        List[str]: Cluster names
    """
```

### 3. Visualization

#### Generate Plot
```python
def generate_plot(
    embeddings: np.ndarray,
    labels: np.ndarray,
    channels: List[dict]
) -> go.Figure:
    """
    Generate interactive plot.
    
    Args:
        embeddings (np.ndarray): Channel embeddings
        labels (np.ndarray): Cluster labels
        channels (List[dict]): Channel data
        
    Returns:
        go.Figure: Plotly figure object
    """
```

## Error Handling

### 1. API Errors
```python
class YouTubeAPIError(Exception):
    """YouTube API related errors."""
    pass

class QuotaExceededError(YouTubeAPIError):
    """API quota exceeded."""
    pass

class AuthenticationError(YouTubeAPIError):
    """Authentication failed."""
    pass
```

### 2. Processing Errors
```python
class ProcessingError(Exception):
    """Data processing errors."""
    pass

class EmbeddingError(ProcessingError):
    """Embedding generation failed."""
    pass

class ClusteringError(ProcessingError):
    """Clustering process failed."""
    pass
```

## Configuration

### 1. Environment Variables
```bash
YOUTUBE_API_KEY=your_api_key
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
```

### 2. Application Settings
```python
# Clustering parameters
CLUSTERING_PARAMS = {
    'n_clusters': 7,
    'min_samples': 5,
    'eps': 0.5
}

# Feature weights
FEATURE_WEIGHTS = {
    'text_embedding': 0.4,
    'engagement': 0.3,
    'subscription': 0.3
}

# API settings
API_SETTINGS = {
    'max_retries': 3,
    'timeout': 30,
    'batch_size': 50
}
``` 