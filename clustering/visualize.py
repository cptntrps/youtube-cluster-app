"""
Cluster visualization module for YouTube channel clusters
"""

import os
import json
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any

from data.store import load_clusters


def generate_visualization(clusters=None, filename=None, output_format='html'):
    """
    Generate visualization of channel clusters
    
    Args:
        clusters: Cluster data (will load from file if None)
        filename: Output filename (optional)
        output_format: Output format (html or json)
        
    Returns:
        Path to the generated visualization file
    """
    # Load clusters from file if not provided
    if clusters is None:
        clusters = load_clusters()
    
    if clusters is None:
        print("Error: No cluster data available")
        return None
    
    # Set output filename
    data_dir = os.getenv('DATA_DIR', './output')
    os.makedirs(data_dir, exist_ok=True)
    
    if filename is None:
        filename = f"{data_dir}/visualization.{output_format}"
    
    # Create interactive scatter plot
    if output_format == 'html':
        # Generate the HTML visualization
        html_file = create_plotly_visualization(clusters, filename)
        return html_file
    else:
        # Generate JSON data for custom visualization
        json_file = create_json_visualization(clusters, filename)
        return json_file


def create_plotly_visualization(clusters, output_file):
    """
    Create an interactive Plotly visualization of the clusters
    
    Args:
        clusters: Cluster data
        output_file: Output HTML file path
        
    Returns:
        Path to the generated HTML file
    """
    # Extract cluster information
    if 'channels' not in clusters:
        print("Error: Cluster data does not contain channel information")
        return None
    
    # Prepare data for scatter plot
    data = []
    
    # Create a color scale
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
        legend=dict(
            x=0,
            y=1,
            traceorder="normal",
            font=dict(family="sans-serif", size=12, color="black"),
            bgcolor="LightSteelBlue",
            bordercolor="Black",
            borderwidth=2
        )
    )
    
    # Create figure and write to HTML
    fig = go.Figure(data=data, layout=layout)
    fig.write_html(output_file)
    
    return output_file


def create_json_visualization(clusters, output_file):
    """
    Create a JSON file with visualization data for custom rendering
    
    Args:
        clusters: Cluster data
        output_file: Output JSON file path
        
    Returns:
        Path to the generated JSON file
    """
    # Prepare visualization data
    viz_data = {
        'clusters': clusters,
        'metadata': {
            'title': 'YouTube Channel Clusters',
            'algorithm': clusters.get('algorithm', 'unknown'),
            'n_clusters': clusters.get('n_clusters', 0)
        }
    }
    
    # Write JSON to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(viz_data, f, ensure_ascii=False, indent=4)
    
    return output_file
