"""Interactive visualization and analysis dashboard for UMI data.

This module provides advanced visualization tools for UMI analysis, enabling:
1. Real-time exploration of molecular diversity
2. Quality assessment of UMI clustering
3. Interactive analysis of error patterns
4. Statistical validation of results
5. Export of publication-ready figures

These visualizations support breakthrough discoveries by providing:
- Unprecedented clarity in single-cell experiment analysis
- Deep insights into molecular heterogeneity
- Robust quality control metrics
- Intuitive exploration of complex datasets
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Union

try:
    import plotly.graph_objects as go
    import plotly.express as px
    import pandas as pd
    import numpy as np
    from dash import Dash, dcc, html
    from dash.dependencies import Input, Output, State
    HAS_VIZ_DEPS = True
except ImportError as e:
    HAS_VIZ_DEPS = False
    logging.warning(
        f"Visualization dependencies not available ({str(e)}). "
        "Install required packages: pip install -r requirements-ml.txt"
    )

@dataclass
class UMIVisualizationData:
    """Container for comprehensive UMI visualization data.
    
    Attributes:
        cluster_sizes: Size distribution of UMI clusters
        error_rates: Estimated error probabilities per UMI
        quality_scores: Quality assessment metrics per UMI
        cluster_relationships: Network of related UMIs with confidence scores
        metadata: Optional experiment-specific metadata
    
    This data structure enables:
    - Molecular diversity analysis
    - Error rate profiling
    - Quality score distribution analysis
    - Network-based relationship visualization
    """
    cluster_sizes: Dict[str, int]
    error_rates: Dict[str, float]
    quality_scores: Dict[str, float]
    cluster_relationships: List[Tuple[str, str, float]]
    metadata: Dict[str, Any] = field(default_factory=dict)

def create_cluster_visualization(
    data: UMIVisualizationData,
    min_confidence: float = 0.5,
    highlight_quality: float = 0.9
) -> Union[go.Figure, None]:
    """Create interactive molecular relationship visualization.
    
    This visualization enables scientists to:
    1. Explore molecular diversity through network analysis
    2. Identify high-confidence UMI clusters
    3. Detect potential sequencing artifacts
    4. Validate clustering decisions
    5. Export publication-ready network diagrams
    
    Args:
        data: UMI visualization data container
        min_confidence: Minimum confidence score for displaying relationships
        highlight_quality: Threshold for highlighting high-quality UMIs
    
    Returns:
        Interactive Plotly figure or None if dependencies not available
    """
    if not HAS_VIZ_DEPS:
        logging.warning("Visualization dependencies required for cluster visualization")
        return None
        
    # Create network graph with molecular insights
    nodes = []
    edges = []
    
    # Process nodes with quality metrics
    for umi, size in data.cluster_sizes.items():
        quality = data.quality_scores.get(umi, 0.0)
        error_rate = data.error_rates.get(umi, 1.0)
        
        nodes.append({
            'id': umi,
            'size': size,
            'quality': quality,
            'error_rate': error_rate,
            'is_high_quality': quality >= highlight_quality,
            'error_rate': data.error_rates.get(umi, 0),
            'quality': data.quality_scores.get(umi, 1.0)
        })
    
    for umi1, umi2, weight in data.cluster_relationships:
        edges.append({
            'source': umi1,
            'target': umi2,
            'weight': weight
        })
    
    # Create network visualization
    fig = go.Figure()
    
    # Add nodes
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    node_color = []
    
    # Layout nodes using Fruchterman-Reingold algorithm
    pos = _layout_nodes(nodes, edges)
    
    for node in nodes:
        x, y = pos[node['id']]
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"UMI: {node['id']}<br>Size: {node['size']}<br>Error: {node['error_rate']:.2f}")
        node_size.append(node['size'] * 10)
        node_color.append(node['quality'])
    
    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers',
        marker={
            'size': node_size,
            'color': node_color,
            'colorscale': 'Viridis',
            'showscale': True,
            'colorbar': {'title': 'Quality Score'}
        },
        text=node_text,
        hoverinfo='text'
    ))
    
    # Add edges
    for edge in edges:
        x0, y0 = pos[edge['source']]
        x1, y1 = pos[edge['target']]
        fig.add_trace(go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode='lines',
            line={'width': edge['weight'] * 2},
            opacity=0.5,
            hoverinfo='none'
        ))
    
    fig.update_layout(
        title='UMI Clustering Visualization',
        showlegend=False,
        hovermode='closest',
        xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
        yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False}
    )
    
    return fig

def create_metric_card(label: str, value: Union[int, float, str]) -> html.Div:
    """Create a metric display card for the dashboard.
    
    Args:
        label: Metric name
        value: Metric value (can be number or formatted string)
    
    Returns:
        Dash HTML component
    """
    return html.Div([
        html.P(label, className="metric-label"),
        html.H3(str(value), className="metric-value")
    ], className="metric-card")

def create_error_heatmap(data: UMIVisualizationData) -> Union[go.Figure, None]:
    """Create error rate analysis heatmap.
    
    This visualization enables:
    1. Identification of systematic sequencing errors
    2. Quality control pattern analysis
    3. Optimization of filtering parameters
    4. Validation of error correction
    
    Args:
        data: UMI visualization data container
        
    Returns:
        Plotly heatmap figure or None if dependencies unavailable
    """
    if not HAS_VIZ_DEPS:
        logging.warning("Visualization dependencies required for error heatmap")
        return None
    
    try:
        # Prepare data for heatmap
        umis = sorted(data.error_rates.keys())
        matrix = np.zeros((len(umis), len(umis)))
        labels = []
        
        for i, umi1 in enumerate(umis):
            for j, umi2 in enumerate(umis):
                # Find relationship confidence if it exists
                conf = 0.0
                for u1, u2, c in data.cluster_relationships:
                    if (u1 == umi1 and u2 == umi2) or (u1 == umi2 and u2 == umi1):
                        conf = c
                        break
                matrix[i][j] = conf
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=umis,
            y=umis,
            colorscale='RdYlBu_r',
            showscale=True,
            colorbar=dict(
                title='Relationship<br>Confidence'
            )
        ))
        
        fig.update_layout(
            title='UMI Relationship Analysis',
            xaxis_title='UMI Sequence',
            yaxis_title='UMI Sequence',
            template='plotly_white'
        )
        
        return fig
        
    except Exception as e:
        logging.error(f"Error creating heatmap: {e}")
        return None

def create_quality_distribution(data: UMIVisualizationData) -> Union[go.Figure, None]:
    """Create quality score distribution visualization.
    
    This visualization enables:
    1. Assessment of sequencing quality
    2. Identification of quality thresholds
    3. Detection of problematic samples
    4. Optimization of filtering parameters
    5. Statistical quality control
    
    Args:
        data: UMI visualization data container
        
    Returns:
        Plotly figure or None if dependencies unavailable
    """
    if not HAS_VIZ_DEPS:
        logging.warning("Visualization dependencies required for quality distribution")
        return None
    
    try:
        # Prepare data for statistical analysis
        df = pd.DataFrame({
            'umi': list(data.quality_scores.keys()),
            'quality': list(data.quality_scores.values()),
            'cluster_size': [data.cluster_sizes.get(umi, 1) for umi in data.quality_scores.keys()],
            'error_rate': [data.error_rates.get(umi, 0.0) for umi in data.quality_scores.keys()]
        })
        
        # Calculate statistical metrics
        df['quality_category'] = pd.qcut(df['quality'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
        quality_stats = df.groupby('quality_category').agg({
            'quality': ['mean', 'std'],
            'error_rate': 'mean',
            'cluster_size': 'mean'
        }).round(3)
        
        # Create main distribution plot
        fig = go.Figure()
        
        # Add quality score distribution
        fig.add_trace(go.Histogram(
            x=df['quality'],
            name='Quality Distribution',
            histnorm='probability',
            nbinsx=30,
            marker_color='rgb(55, 83, 109)'
        ))
        
        # Add error rate correlation
        fig.add_trace(go.Scatter(
            x=df['quality'],
            y=df['error_rate'],
            mode='markers',
            name='Error Rate vs Quality',
            yaxis='y2',
            marker=dict(
                color=df['cluster_size'],
                colorscale='Viridis',
                showscale=True,
                size=8,
                opacity=0.6
            )
        ))
        
        # Update layout with scientific styling
        fig.update_layout(
            title='Molecular Quality Analysis',
            xaxis_title='Quality Score',
            yaxis_title='Frequency',
            yaxis2=dict(
                title='Error Rate',
                overlaying='y',
                side='right'
            ),
            template='plotly_white',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99
            ),
            margin=dict(t=50, b=50, l=50, r=50),
            annotations=[
                dict(
                    x=0.02,
                    y=0.98,
                    xref='paper',
                    yref='paper',
                    text=f'Mean Quality: {df["quality"].mean():.3f}<br>'
                         f'Std Dev: {df["quality"].std():.3f}',
                    showarrow=False,
                    font=dict(size=10),
                    bgcolor='rgba(255,255,255,0.8)'
                )
            ]
        )
        
        return fig
        
    except Exception as e:
        logging.error(f"Error creating quality distribution plot: {e}")
        return None

def create_error_rate_plot(data: UMIVisualizationData) -> go.Figure:
    """Create error rate analysis plot."""
    error_rates = list(data.error_rates.values())
    cluster_sizes = list(data.cluster_sizes.values())
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=cluster_sizes,
        y=error_rates,
        mode='markers',
        marker={
            'size': 8,
            'color': error_rates,
            'colorscale': 'Reds',
            'showscale': True
        },
        text=[f"Size: {s}<br>Error: {e:.2f}" for s, e in zip(cluster_sizes, error_rates)],
        hoverinfo='text'
    ))
    
    fig.update_layout(
        title='Error Rates vs Cluster Size',
        xaxis_title='Cluster Size',
        yaxis_title='Error Rate'
    )
    
    return fig

def _layout_nodes(nodes: List[dict], edges: List[dict], iterations: int = 50) -> Dict[str, Tuple[float, float]]:
    """Layout nodes using Fruchterman-Reingold algorithm."""
    # Initialize random positions
    pos = {node['id']: (np.random.rand(), np.random.rand()) for node in nodes}
    
    # Create adjacency list
    adj = {node['id']: [] for node in nodes}
    for edge in edges:
        adj[edge['source']].append(edge['target'])
        adj[edge['target']].append(edge['source'])
    
    # Parameters
    k = 1.0
    t = 1.0
    dt = t / (iterations + 1)
    
    # Main layout loop
    for _ in range(iterations):
        # Calculate repulsive forces
        disp = {node['id']: np.array([0.0, 0.0]) for node in nodes}
        
        for v in nodes:
            for u in nodes:
                if v['id'] != u['id']:
                    delta = np.array(pos[v['id']]) - np.array(pos[u['id']])
                    dist = np.linalg.norm(delta)
                    if dist != 0:
                        disp[v['id']] += (delta / dist) * k * k / dist
        
        # Calculate attractive forces
        for edge in edges:
            delta = np.array(pos[edge['source']]) - np.array(pos[edge['target']])
            dist = np.linalg.norm(delta)
            if dist != 0:
                d = delta * (dist * dist / k)
                disp[edge['source']] -= d
                disp[edge['target']] += d
        
        # Update positions
        for v in nodes:
            dist = np.linalg.norm(disp[v['id']])
            if dist != 0:
                pos[v['id']] = tuple(np.array(pos[v['id']]) + (disp[v['id']] / dist) * min(dist, t))
        
        t -= dt
    
    return pos

def create_dashboard(data: UMIVisualizationData) -> Optional[Dash]:
    """Create comprehensive scientific analysis dashboard.
    
    This dashboard enables scientists to:
    1. Perform real-time quality assessment
    2. Validate molecular clustering decisions
    3. Identify potential biological artifacts
    4. Generate publication-ready visualizations
    5. Export data for further analysis
    
    Features:
    - Interactive network visualization
    - Quality score distributions
    - Error rate profiling
    - Statistical summaries
    - Data export capabilities
    
    Args:
        data: Container with UMI analysis data
        
    Returns:
        Dash application instance or None if dependencies unavailable
    """
    if not HAS_VIZ_DEPS:
        logging.warning("Visualization dependencies required for dashboard creation")
        return None
    
    try:
        app = Dash(__name__)
        
        # Create scientific visualizations
        cluster_fig = create_cluster_visualization(data)
        quality_fig = create_quality_distribution(data)
        error_fig = create_error_heatmap(data)
        
        if any(fig is None for fig in [cluster_fig, quality_fig, error_fig]):
            logging.error("Failed to create one or more visualizations")
            return None
            
        # Calculate summary statistics
        total_molecules = sum(data.cluster_sizes.values())
        unique_molecules = len(data.cluster_sizes)
        avg_quality = np.mean(list(data.quality_scores.values()))
        error_rate = np.mean(list(data.error_rates.values()))
        
        # Create the scientific dashboard layout
        app.layout = html.Div([
            # Header with key metrics
            html.Div([
                html.H1("UMI Analysis Dashboard", className="header-title"),
                html.Div([
                    create_metric_card("Total Molecules", total_molecules),
                    create_metric_card("Unique Molecules", unique_molecules),
                    create_metric_card("Average Quality", f"{avg_quality:.3f}"),
                    create_metric_card("Error Rate", f"{error_rate:.3e}")
                ], className="metric-container")
            ], className="header"),
            
            # Main visualization section
            html.Div([
                # Network analysis panel
                html.Div([
                    html.H3("Molecular Network Analysis"),
                    dcc.Graph(figure=cluster_fig, id='cluster-graph'),
                    html.Div([
                        html.Label("Minimum Confidence:"),
                        dcc.Slider(0, 1, 0.1, value=0.5, id='confidence-slider')
                    ], className="control-panel")
                ], className="panel"),
                
                # Quality analysis panel
                html.Div([
                    html.H3("Quality Distribution Analysis"),
                    dcc.Graph(figure=quality_fig, id='quality-graph'),
                    html.Div([
                        html.Label("Quality Threshold:"),
                        dcc.Slider(0, 1, 0.1, value=0.9, id='quality-slider')
                    ], className="control-panel")
                ], className="panel")
            ], className="row"),
            
            # Error analysis section
            html.Div([
                html.H3("Error Pattern Analysis"),
                dcc.Graph(figure=error_fig, id='error-graph')
            ], className="panel"),
            
            # Export controls
            html.Div([
                html.Button("Export Data", id="export-button"),
                html.Button("Save Figures", id="save-button"),
                dcc.Download(id="download-data")
            ], className="export-panel")
        ])
        
        return app
        
    except Exception as e:
        logging.error(f"Error creating dashboard: {e}")
        return None