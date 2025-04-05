"""
Streamlit web interface for YouTube Cluster App
"""

import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from auth.oauth import authenticate
from data.fetch_subscriptions import fetch_all_subscriptions
from data.store import save_subscriptions, load_subscriptions, save_clusters, load_clusters
from clustering.vectorize import vectorize_channels, save_embeddings
from clustering.cluster import create_clusters, find_optimal_clusters
from clustering.visualize import generate_visualization
from interface.batch_actions import batch_subscribe, batch_unsubscribe

# Page configuration
st.set_page_config(
    page_title="YouTube Cluster App",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'youtube_client' not in st.session_state:
    st.session_state.youtube_client = None
if 'subscriptions' not in st.session_state:
    st.session_state.subscriptions = None
if 'embeddings' not in st.session_state:
    st.session_state.embeddings = None
if 'clusters' not in st.session_state:
    st.session_state.clusters = None


def authenticate_user():
    """Authenticate with YouTube API"""
    with st.spinner('Authenticating with YouTube...'):
        try:
            st.session_state.youtube_client = authenticate()
            st.session_state.authenticated = True
            st.success('Authentication successful!')
        except Exception as e:
            st.error(f'Authentication failed: {str(e)}')
            st.session_state.authenticated = False


def fetch_data():
    """Fetch subscription data from YouTube"""
    if not st.session_state.authenticated:
        st.warning('Please authenticate first')
        return
    
    with st.spinner('Fetching subscriptions from YouTube...'):
        try:
            subscriptions = fetch_all_subscriptions(st.session_state.youtube_client)
            st.session_state.subscriptions = subscriptions
            save_subscriptions(subscriptions)
            st.success(f'Successfully fetched {len(subscriptions)} subscriptions!')
        except Exception as e:
            st.error(f'Error fetching subscriptions: {str(e)}')


def load_data():
    """Load subscription data from file"""
    with st.spinner('Loading subscription data...'):
        try:
            subscriptions = load_subscriptions()
            if subscriptions:
                st.session_state.subscriptions = subscriptions
                st.success(f'Loaded {len(subscriptions)} subscriptions!')
            else:
                st.warning('No subscription data found. Please fetch subscriptions first.')
        except Exception as e:
            st.error(f'Error loading subscriptions: {str(e)}')


def create_channel_clusters():
    """Create clusters from subscription data"""
    if st.session_state.subscriptions is None:
        st.warning('Please load subscription data first')
        return
    
    with st.spinner('Vectorizing and clustering channels...'):
        try:
            # Get number of clusters from input
            n_clusters = st.session_state.get('n_clusters', 10)
            
            # Vectorize channels
            channels, embeddings = vectorize_channels(st.session_state.subscriptions)
            st.session_state.embeddings = embeddings
            save_embeddings(embeddings)
            
            # Create clusters
            clusters = create_clusters(embeddings, channels, n_clusters=n_clusters)
            st.session_state.clusters = clusters
            save_clusters(clusters)
            
            st.success(f'Successfully created {n_clusters} clusters!')
        except Exception as e:
            st.error(f'Error creating clusters: {str(e)}')


def visualize_clusters():
    """Visualize clusters in the app"""
    if st.session_state.clusters is None:
        st.warning('Please create clusters first')
        return
    
    clusters = st.session_state.clusters
    
    # Create visualization
    try:
        # Extract cluster information
        if 'channels' not in clusters:
            st.error("Cluster data does not contain channel information")
            return
        
        # Prepare data for scatter plot
        data = []
        colors = px.colors.qualitative.Plotly
        
        # Create a data trace for each cluster
        for cluster_label, channels in clusters['channels'].items():
            # Skip noise points (cluster -1) if present
            if cluster_label == '-1':
                marker_color = 'rgba(0, 0, 0, 0.1)'  # Transparent black for noise
                marker_size = 5
            else:
                # Assign color from the palette (cycle through if needed)
                color_idx = int(cluster_label) % len(colors)
                marker_color = colors[color_idx]
                marker_size = 8
            
            # Extract coordinates and labels
            x_coords = [channel.get('x', 0) for channel in channels]
            y_coords = [channel.get('y', 0) for channel in channels]
            titles = [channel.get('title', 'Unknown') for channel in channels]
            
            # Create hover text
            hover_texts = []
            for channel in channels:
                text = f"<b>{channel.get('title', 'Unknown')}</b><br>"
                text += f"Subscribers: {channel.get('subscriber_count', 'N/A')}<br>"
                text += f"Videos: {channel.get('video_count', 'N/A')}<br>"
                
                # Truncate description if too long
                desc = channel.get('description', '')
                if len(desc) > 100:
                    desc = desc[:97] + '...'
                text += f"Description: {desc}"
                
                hover_texts.append(text)
            
            # Create scatter trace for this cluster
            trace = go.Scatter(
                x=x_coords,
                y=y_coords,
                mode='markers',
                marker=dict(
                    size=marker_size,
                    color=marker_color,
                    line=dict(width=1, color='DarkSlateGrey')
                ),
                text=hover_texts,
                hoverinfo='text',
                name=f"Cluster {cluster_label}"
            )
            
            data.append(trace)
        
        # Create figure layout
        layout = go.Layout(
            title="YouTube Channel Clusters",
            hovermode='closest',
            xaxis=dict(title='Component 1'),
            yaxis=dict(title='Component 2'),
            showlegend=True,
            height=700
        )
        
        # Create and display figure
        fig = go.Figure(data=data, layout=layout)
        st.plotly_chart(fig, use_container_width=True)
        
        # Generate downloadable visualization
        viz_file = generate_visualization(clusters)
        if viz_file:
            with open(viz_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            st.download_button(
                label="Download Visualization",
                data=html_content,
                file_name="youtube_clusters.html",
                mime="text/html"
            )
    
    except Exception as e:
        st.error(f'Error visualizing clusters: {str(e)}')


def show_cluster_details():
    """Show detailed information about each cluster"""
    if st.session_state.clusters is None:
        st.warning('Please create clusters first')
        return
    
    clusters = st.session_state.clusters
    
    # Show cluster details in tabs
    if 'channels' in clusters:
        # Create tabs for each cluster
        cluster_tabs = st.tabs([f"Cluster {label}" for label in clusters['channels'].keys()])
        
        # Populate each tab with cluster information
        for i, (cluster_label, channels) in enumerate(clusters['channels'].items()):
            with cluster_tabs[i]:
                st.subheader(f"Cluster {cluster_label} - {len(channels)} channels")
                
                # Create dataframe from channels
                df = pd.DataFrame(channels)
                
                # Add interactive elements
                if st.checkbox(f"Show full data for Cluster {cluster_label}", key=f"show_data_{cluster_label}"):
                    st.dataframe(df)
                
                # Show top channels by subscriber count
                st.subheader("Top Channels by Subscribers")
                try:
                    # Convert subscriber_count to numeric
                    df['subscriber_count'] = pd.to_numeric(df['subscriber_count'], errors='coerce')
                    top_channels = df.nlargest(5, 'subscriber_count')
                    st.table(top_channels[['title', 'subscriber_count']])
                except:
                    st.write("Could not sort by subscriber count")
                
                # Word cloud option if wordcloud is installed
                try:
                    import matplotlib.pyplot as plt
                    from wordcloud import WordCloud
                    
                    # Create wordcloud from titles and descriptions
                    all_text = ' '.join([f"{ch.get('title', '')} {ch.get('description', '')}" for ch in channels])
                    if all_text.strip():
                        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_text)
                        
                        # Display wordcloud
                        plt.figure(figsize=(10, 5))
                        plt.imshow(wordcloud, interpolation='bilinear')
                        plt.axis('off')
                        st.pyplot(plt)
                except:
                    st.write("WordCloud visualization not available")


def main():
    """Main Streamlit application"""
    # Title and description
    st.title("📺 YouTube Channel Cluster App")
    st.markdown("""
    Organize your YouTube subscriptions into meaningful clusters based on content similarity.
    """)
    
    # Sidebar for actions
    with st.sidebar:
        st.header("Actions")
        
        # Authentication section
        st.subheader("Authentication")
        if not st.session_state.authenticated:
            auth_button = st.button("Authenticate with YouTube", key="auth_button")
            if auth_button:
                authenticate_user()
        else:
            st.success("✅ Authenticated")
            
            # Load/fetch data section
            st.subheader("Data")
            fetch_col, load_col = st.columns(2)
            with fetch_col:
                fetch_button = st.button("Fetch Subscriptions", key="fetch_button")
            with load_col:
                load_button = st.button("Load from File", key="load_button")
            
            if fetch_button:
                fetch_data()
            if load_button:
                load_data()
            
            # Clustering section
            if st.session_state.subscriptions is not None:
                st.subheader("Clustering")
                st.session_state.n_clusters = st.slider(
                    "Number of Clusters",
                    min_value=2,
                    max_value=30,
                    value=10,
                    step=1
                )
                cluster_button = st.button("Create Clusters", key="cluster_button")
                if cluster_button:
                    create_channel_clusters()
    
    # Main content
    if st.session_state.authenticated:
        # Subscription details tab
        if st.session_state.subscriptions is not None:
            tab1, tab2, tab3 = st.tabs(["Channel Overview", "Clusters", "Cluster Details"])
            
            with tab1:
                st.header("Channel Overview")
                st.write(f"You are subscribed to {len(st.session_state.subscriptions)} channels")
                
                # Display subscription table
                df = pd.DataFrame(st.session_state.subscriptions)
                if len(df) > 0:
                    # Convert columns to appropriate types
                    for col in ['subscriber_count', 'video_count', 'view_count']:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    # Show summary statistics
                    st.subheader("Channel Statistics")
                    stats_cols = st.columns(3)
                    with stats_cols[0]:
                        try:
                            total_subs = df['subscriber_count'].sum()
                            st.metric("Total Subscribers", f"{total_subs:,}")
                        except:
                            st.metric("Total Subscribers", "N/A")
                    
                    with stats_cols[1]:
                        try:
                            avg_subs = df['subscriber_count'].mean()
                            st.metric("Avg. Subscribers", f"{int(avg_subs):,}")
                        except:
                            st.metric("Avg. Subscribers", "N/A")
                    
                    with stats_cols[2]:
                        try:
                            total_videos = df['video_count'].sum()
                            st.metric("Total Videos", f"{total_videos:,}")
                        except:
                            st.metric("Total Videos", "N/A")
                    
                    # Show table of subscriptions
                    st.subheader("Your Subscriptions")
                    st.dataframe(df)
            
            with tab2:
                st.header("Channel Clusters")
                if st.session_state.clusters is not None:
                    visualize_clusters()
                else:
                    st.info("Create clusters from the sidebar to visualize them here")
            
            with tab3:
                st.header("Cluster Details")
                if st.session_state.clusters is not None:
                    show_cluster_details()
                else:
                    st.info("Create clusters from the sidebar to see detailed information")
        else:
            st.info("Please fetch or load subscription data from the sidebar")
    else:
        st.info("Please authenticate with YouTube from the sidebar to get started")
    
    # Footer
    st.markdown("---")
    st.caption("YouTube Cluster App | Made with ❤️ using Streamlit")


if __name__ == "__main__":
    main()
