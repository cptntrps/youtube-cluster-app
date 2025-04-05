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

# NumPy JSON encoder
class NumpyEncoder(json.JSONEncoder):
    """Special JSON encoder for NumPy types"""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)


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
        
        # Get cluster name if available, otherwise use cluster number
        if 'cluster_names' in clusters and cluster_label in clusters['cluster_names']:
            cluster_name = clusters['cluster_names'][cluster_label]
        else:
            cluster_name = f"Cluster {cluster_label}"
        
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
            name=cluster_name
        )
        
        data.append(trace)
    
    # Create figure layout
    layout = go.Layout(
        title="YouTube Channel Clusters by Category",
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
    Create an interactive visualization of the clusters
    """
    # Prepare the data for visualization
    viz_data = {
        'nodes': [],
        'links': [],
        'clusters': {},
        'metadata': clusters.get('metadata', {})
    }
    
    # Add nodes (channels) with enhanced metadata
    for cluster_id, channels in clusters['channels'].items():
        cluster_name = clusters.get('cluster_names', {}).get(cluster_id, f'Cluster {cluster_id}')
        viz_data['clusters'][cluster_id] = {
            'name': cluster_name,
            'size': len(channels)
        }
        
        for channel in channels:
            node = {
                'id': channel['channel_id'],
                'title': channel['title'],
                'cluster': cluster_id,
                'cluster_name': cluster_name,
                'x': channel.get('x', 0),
                'y': channel.get('y', 0),
                'metadata': {
                    'subscriber_count': channel.get('subscriber_count', 0),
                    'video_count': channel.get('video_count', 0),
                    'views_per_video': channel.get('metadata_features', [0])[2],
                    'has_social_links': channel.get('metadata_features', [0])[3],
                    'has_website': channel.get('metadata_features', [0])[4]
                }
            }
            viz_data['nodes'].append(node)
    
    # Create the HTML template with enhanced visualization
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>YouTube Channel Clusters</title>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
            #visualization { width: 100%; height: 800px; }
            .node { cursor: pointer; }
            .node:hover { stroke: #000; stroke-width: 2px; }
            .tooltip { position: absolute; padding: 10px; background: rgba(0,0,0,0.8); color: white; border-radius: 5px; }
            .controls { margin-bottom: 20px; }
            .cluster-info { margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="controls">
            <h2>YouTube Channel Clusters</h2>
            <div>
                <label>Cluster Size: </label>
                <input type="range" id="sizeScale" min="1" max="10" value="5">
            </div>
            <div>
                <label>Show Labels: </label>
                <input type="checkbox" id="showLabels" checked>
            </div>
        </div>
        <div id="visualization"></div>
        <div class="cluster-info" id="clusterInfo"></div>
        <script>
            const data = %s;
            
            // Set up the visualization
            const width = window.innerWidth - 40;
            const height = 800;
            const padding = 50;
            
            const svg = d3.select('#visualization')
                .append('svg')
                .attr('width', width)
                .attr('height', height);
            
            // Create scales
            const xScale = d3.scaleLinear()
                .domain(d3.extent(data.nodes, d => d.x))
                .range([padding, width - padding]);
                
            const yScale = d3.scaleLinear()
                .domain(d3.extent(data.nodes, d => d.y))
                .range([height - padding, padding]);
                
            const colorScale = d3.scaleOrdinal()
                .domain(Object.keys(data.clusters))
                .range(d3.schemeCategory10);
                
            const sizeScale = d3.scaleLinear()
                .domain([0, d3.max(data.nodes, d => d.metadata.subscriber_count)])
                .range([5, 20]);
            
            // Create tooltip
            const tooltip = d3.select('body')
                .append('div')
                .attr('class', 'tooltip')
                .style('opacity', 0);
            
            // Draw nodes
            const nodes = svg.selectAll('.node')
                .data(data.nodes)
                .enter()
                .append('circle')
                .attr('class', 'node')
                .attr('cx', d => xScale(d.x))
                .attr('cy', d => yScale(d.y))
                .attr('r', d => sizeScale(d.metadata.subscriber_count))
                .style('fill', d => colorScale(d.cluster))
                .on('mouseover', function(event, d) {
                    tooltip.transition()
                        .duration(200)
                        .style('opacity', .9);
                    tooltip.html(`
                        <strong>${d.title}</strong><br/>
                        Cluster: ${d.cluster_name}<br/>
                        Subscribers: ${d.metadata.subscriber_count.toLocaleString()}<br/>
                        Videos: ${d.metadata.video_count.toLocaleString()}<br/>
                        Views/Video: ${d.metadata.views_per_video.toLocaleString()}
                    `)
                        .style('left', (event.pageX + 10) + 'px')
                        .style('top', (event.pageY - 28) + 'px');
                })
                .on('mouseout', function() {
                    tooltip.transition()
                        .duration(500)
                        .style('opacity', 0);
                });
            
            // Add labels if enabled
            function updateLabels() {
                const labels = svg.selectAll('.label')
                    .data(data.nodes)
                    .join('text')
                    .attr('class', 'label')
                    .attr('x', d => xScale(d.x))
                    .attr('y', d => yScale(d.y))
                    .attr('text-anchor', 'middle')
                    .attr('dy', -10)
                    .style('display', d3.select('#showLabels').property('checked') ? 'block' : 'none')
                    .text(d => d.title);
            }
            
            // Update cluster info
            function updateClusterInfo() {
                const info = d3.select('#clusterInfo');
                info.html('');
                
                Object.entries(data.clusters).forEach(([id, cluster]) => {
                    info.append('div')
                        .html(`
                            <h3>${cluster.name}</h3>
                            <p>Size: ${cluster.size} channels</p>
                        `);
                });
            }
            
            // Handle controls
            d3.select('#sizeScale').on('input', function() {
                const scale = +this.value;
                nodes.attr('r', d => sizeScale(d.metadata.subscriber_count) * scale);
            });
            
            d3.select('#showLabels').on('change', updateLabels);
            
            // Initial updates
            updateLabels();
            updateClusterInfo();
        </script>
    </body>
    </html>
    """ % json.dumps(viz_data, cls=NumpyEncoder)
    
    # Save the visualization
    output_dir = os.getenv('DATA_DIR', './output')
    output_path = os.path.join(output_dir, output_file)
    
    with open(output_path, 'w') as f:
        f.write(html_template)
    
    return output_path
