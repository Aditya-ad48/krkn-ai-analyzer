import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict

def create_failure_correlation_heatmap(health_events: List[Dict]) -> go.Figure:
    """Create heatmap showing which services fail together"""
    
    if not health_events:
        return None
    
    df = pd.DataFrame(health_events)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['failed'] = (df['status_code'] >= 400).astype(int)
    
    # Create time buckets
    df['time_bucket'] = df['timestamp'].dt.floor('30s')
    
    # Pivot: rows=time, cols=service, values=failure(0/1)
    pivot = df.pivot_table(
        index='time_bucket',
        columns='service',
        values='failed',
        aggfunc='max',
        fill_value=0
    )
    
    if len(pivot.columns) < 2:
        return None
    
    # Calculate correlation
    corr_matrix = pivot.corr()
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdYlGn_r',
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title="Service Failure Correlation Matrix",
        xaxis_title="Service",
        yaxis_title="Service",
        height=400
    )
    
    return fig