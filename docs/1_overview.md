# YouTube Cluster App Overview

## Introduction
The YouTube Cluster App is a sophisticated tool for analyzing and clustering YouTube channels based on their content, engagement metrics, and subscription relationships. It uses advanced machine learning techniques to group similar channels and provide insights into content categories and audience engagement patterns.

## Tech Stack

### Core Technologies
- Python 3.12
- NumPy: Scientific computing and numerical operations
- scikit-learn: Machine learning algorithms and metrics
- sentence-transformers: Text embeddings and semantic analysis
- UMAP: Dimensionality reduction
- PyTorch: Deep learning framework (used by sentence-transformers)

### Data Management & API
- google-api-python-client: YouTube Data API v3 integration
- google-auth-oauthlib: OAuth 2.0 authentication
- python-dotenv: Environment variable management

### Visualization
- Plotly: Interactive data visualization
- Streamlit: Web interface (currently experiencing compatibility issues with Python 3.12)

### Development Tools
- Virtual Environment (venv): Dependency isolation
- Git: Version control

## Known Issues and Limitations

### 1. Streamlit Interface Issues
- RuntimeError: "no running event loop" in asyncio
- PyTorch path resolution errors with torch._classes
- Error: "Tried to instantiate class '__path__._path'" when running Streamlit
- General compatibility issues between Streamlit and Python 3.12

### 2. Alternative Access Methods
Instead of using Streamlit interface, use:
```bash
# Direct script execution
python enhanced_clustering.py

# View visualization in browser
xdg-open output/visualization.html
```

### 3. Current Workarounds
- Use the command-line interface instead of Streamlit
- Access visualizations directly through the browser
- Run clustering through the Python script interface 