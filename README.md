# YouTube Cluster App

A tool to organize your YouTube subscriptions using clustering algorithms.

## Features

- OAuth authentication with Google/YouTube
- Fetch and manage your YouTube subscriptions
- Cluster channels based on content similarity
- Interactive visualization of clusters
- Batch actions for subscription management
- Export/import capabilities

## Setup

1. Create a `.env` file based on `.env.example`
2. Install requirements: `pip install -r requirements.txt`
3. Run the app: `streamlit run interface/streamlit_app.py`

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
