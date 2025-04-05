# Usage Guide

## Installation

### 1. Environment Setup
```bash
# Clone the repository
git clone [repository-url]
cd youtube-cluster-app

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

### 2. Dependencies
```bash
# Install required packages
pip install -r requirements.txt
```

### 3. Configuration
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
# Required variables:
# - YOUTUBE_API_KEY
# - CLIENT_ID
# - CLIENT_SECRET
```

## Running the Application

### 1. Command Line Interface (Recommended)
```bash
# Activate virtual environment if not already active
source venv/bin/activate

# Run clustering
python enhanced_clustering.py

# View results
xdg-open output/visualization.html
```

### 2. Web Interface (Currently Limited)
Note: The Streamlit interface is currently experiencing compatibility issues with Python 3.12

Known Issues:
- RuntimeError: "no running event loop"
- PyTorch path resolution errors
- Error with torch._classes path

Alternative Access Methods:
```bash
# Not recommended due to known issues
python -m streamlit run interface/streamlit_app.py
```

## Data Collection

### 1. Initial Setup
- Ensure YouTube API credentials are configured
- Check API quota limits (default: 10,000 units/day)
- Verify authentication tokens

### 2. Fetching Subscriptions
```bash
# Fetch new subscription data
python cluster_subscriptions.py
```

### 3. Updating Data
- Regular updates recommended (weekly/monthly)
- Monitor API quota usage
- Cache frequently accessed data

## Clustering Configuration

### 1. Basic Settings
```python
# Default parameters
n_clusters = 7  # Number of clusters
subscription_weight = 0.3  # Subscription relationship weight
```

### 2. Advanced Options
```bash
# Custom clustering parameters
python enhanced_clustering.py --clusters 10 --weight 0.4
```

### 3. Batch Processing
```bash
# Process in smaller batches
python enhanced_clustering.py --batch-size 50
```

## Visualization

### 1. Interactive Plot
- Open `output/visualization.html` in a web browser
- Features:
  * Zoom and pan
  * Hover information
  * Cluster selection
  * Channel details

### 2. Export Options
- HTML interactive plot
- JSON cluster data
- CSV channel data

## Troubleshooting

### 1. Common Issues

#### API Errors
- Check API quota in Google Cloud Console
- Verify API credentials
- Monitor rate limits

#### Authentication Issues
- Refresh OAuth tokens
- Check credential permissions
- Verify API access

#### Processing Errors
- Monitor memory usage
- Check disk space
- Verify input data format

### 2. Error Messages

#### Streamlit Interface
```
RuntimeError: no running event loop
```
- Use command-line interface instead
- Access visualization directly through browser

#### PyTorch Errors
```
RuntimeError: Tried to instantiate class '__path__._path'
```
- Known issue with Python 3.12
- Use command-line interface

### 3. Performance Issues
- Reduce batch size
- Monitor memory usage
- Clean cache regularly

## Best Practices

### 1. Data Management
- Regular backups
- Version control
- Data validation

### 2. API Usage
- Monitor quotas
- Implement caching
- Use batch processing

### 3. Updates
- Check for updates regularly
- Test in development environment
- Maintain documentation 