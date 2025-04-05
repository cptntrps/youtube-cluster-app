# YouTube Cluster App

A sophisticated tool for analyzing and clustering YouTube channels based on their content, engagement metrics, and subscription relationships. This application uses advanced machine learning techniques to group similar channels and provide insights into content categories and audience engagement patterns.

## Features

- **Channel Analysis**: Extract and analyze channel metadata, engagement metrics, and content
- **Advanced Clustering**: Group similar channels using machine learning algorithms
- **Visualization**: Interactive visualizations of channel clusters and relationships
- **Subscription Graph**: Analyze subscription relationships between channels
- **Content Categorization**: Automatically detect and categorize channel content

## Tech Stack

- Python 3.12
- NumPy & scikit-learn for machine learning
- sentence-transformers for text embeddings
- UMAP for dimensionality reduction
- Plotly for interactive visualizations
- YouTube Data API v3 for data collection

## Documentation

Comprehensive documentation is available in the `docs/` directory:

1. [Overview](docs/1_overview.md) - Introduction and tech stack
2. [Architecture](docs/2_architecture.md) - System design and components
3. [Algorithms](docs/3_algorithms.md) - Technical details of methods used
4. [Usage](docs/4_usage.md) - Installation and usage instructions
5. [API](docs/5_api.md) - API documentation
6. [Contributing](docs/6_contributing.md) - Guidelines for contributors

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/youtube-cluster-app.git
cd youtube-cluster-app

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your YouTube API credentials:
```
YOUTUBE_API_KEY=your_api_key
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
```

## Usage

### Command Line Interface (Recommended)

```bash
# Run clustering
python enhanced_clustering.py

# View results
xdg-open output/visualization.html
```

### Web Interface (Currently Limited)

Note: The Streamlit interface is currently experiencing compatibility issues with Python 3.12.

```bash
# Not recommended due to known issues
python -m streamlit run interface/streamlit_app.py
```

## Known Issues

- Streamlit interface has compatibility issues with Python 3.12
- PyTorch path resolution errors with torch._classes
- RuntimeError: "no running event loop" in asyncio

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Please read [CONTRIBUTING.md](docs/6_contributing.md) for details on our code of conduct and the process for submitting pull requests.

## Project Structure

```
youtube-cluster-app/
├── README.md
├── requirements.txt
├── .env.example
├── main.py
├── auth/
│   └── oauth.py       # YouTube API authentication
├── data/
│   ├── fetch_subscriptions.py  # Data collection
│   └── store.py                # Data persistence
├── clustering/
│   ├── vectorize.py  # Text to vector conversion
│   ├── cluster.py    # Clustering algorithms
│   └── visualize.py  # Visualization tools
├── interface/
│   ├── streamlit_app.py   # Web interface
│   └── batch_actions.py   # Bulk operations
├── utils/
│   └── helpers.py     # Shared utilities
├── output/            # Generated data
└── docker/            # Containerization
```

## Development

See the GitHub project board for current tasks and progress.
