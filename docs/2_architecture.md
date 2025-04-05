# System Architecture

## Directory Structure
```
youtube-cluster-app/
├── auth/                 # Authentication handling
│   ├── oauth.py         # YouTube API authentication
│   └── credentials/     # API credentials storage
├── clustering/           # Core clustering functionality
│   ├── vectorize.py     # Channel vectorization
│   ├── cluster.py       # Clustering algorithms
│   └── visualize.py     # Visualization generation
├── data/                # Data management
│   ├── store.py         # Data persistence
│   └── fetch_subscriptions.py  # Data collection
├── interface/           # Web interface (currently limited)
│   └── streamlit_app.py # Streamlit application
├── output/              # Generated files
│   ├── clusters.json    # Clustering results
│   ├── enhanced_clusters.json  # Enhanced clustering results
│   └── visualization.html # Interactive visualizations
├── utils/               # Utility functions
└── docs/               # Documentation
```

## Core Components

### 1. Data Collection (data/fetch_subscriptions.py)
- YouTube Data API v3 integration
- Batch processing with quota management
- Error handling and retry logic
- Data validation and normalization
- Subscription relationship mapping

### 2. Channel Vectorization (clustering/vectorize.py)
- Sentence transformer model: 384-dimensional embeddings
- Text preprocessing and cleaning
- Feature extraction:
  * Channel metadata
  * Engagement metrics
  * Topic categorization
  * Subscription relationships
- Dimensionality reduction using UMAP

### 3. Clustering Engine (clustering/cluster.py)
- Multi-stage clustering process
- Automatic parameter optimization
- Metrics:
  * Silhouette score
  * Inertia
  * Cluster stability
- DBSCAN implementation for density-based clustering

### 4. Visualization (clustering/visualize.py)
- Interactive Plotly-based visualization
- UMAP dimensionality reduction
- Feature importance visualization
- Cluster relationship mapping
- Direct HTML output for browser viewing

### 5. Authentication (auth/oauth.py)
- OAuth 2.0 implementation
- Token management
- Credential storage
- API quota tracking

### 6. Data Storage (data/store.py)
- JSON-based data persistence
- CSV export capabilities
- Cache management
- Data versioning

## Component Interactions

### Data Flow
1. Authentication → Data Collection
2. Data Collection → Storage
3. Storage → Vectorization
4. Vectorization → Clustering
5. Clustering → Visualization

### Error Handling
- API quota management
- Network timeout recovery
- Data validation
- Process recovery

## Access Methods

### Command Line Interface
```bash
# Main clustering script
python enhanced_clustering.py

# View results
xdg-open output/visualization.html
```

### Alternative Web Interface
Note: Currently experiencing compatibility issues with Python 3.12
```bash
# Not recommended due to known issues
python -m streamlit run interface/streamlit_app.py
``` 