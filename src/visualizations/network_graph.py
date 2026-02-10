import plotly.graph_objects as go
import networkx as nx
from typing import List, Dict, Any
import pandas as pd

class ServiceDependencyGraph:
    """Build interactive network graphs from health events"""
    
    def build_graph_from_cascades(self, health_events: List[Dict], cascades: List[Dict]) -> go.Figure:
        """Create network graph showing service dependencies"""
        
        # Build directed graph
        G = nx.DiGraph()
        
        # Add all services as nodes
        services = set(e['service'] for e in health_events)
        for service in services:
            G.add_node(service)
        
        # Add edges based on cascade patterns
        edge_weights = {}
        for cascade in cascades:
            services_in_cascade = cascade['services']
            # Assume first service failure triggers others
            if len(services_in_cascade) > 1:
                source = services_in_cascade[0]
                for target in services_in_cascade[1:]:
                    edge = (source, target)
                    edge_weights[edge] = edge_weights.get(edge, 0) + 1
        
        for (source, target), weight in edge_weights.items():
            G.add_edge(source, target, weight=weight)
        
        # Calculate failure counts for node sizing
        df = pd.DataFrame(health_events)
        failure_counts = df[df['status_code'] >= 400].groupby('service').size().to_dict()
        
        # Layout
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Create edge traces
        edge_trace = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            weight = G[edge[0]][edge[1]]['weight']
            
            edge_trace.append(
                go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=weight * 2, color='#888'),
                    hoverinfo='none',
                    showlegend=False
                )
            )
        
        # Create node trace
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        node_color = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            failures = failure_counts.get(node, 0)
            node_text.append(f"{node}<br>Failures: {failures}")
            node_size.append(max(20, failures * 5))
            node_color.append(failures)
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            text=[node for node in G.nodes()],
            textposition="top center",
            hovertext=node_text,
            hoverinfo='text',
            marker=dict(
                size=node_size,
                color=node_color,
                colorscale='YlOrRd',
                showscale=True,
                colorbar=dict(
                    title="Failures",
                    thickness=15,
                    len=0.7
                ),
                line=dict(width=2, color='white')
            ),
            showlegend=False
        )
        
        # Create figure
        fig = go.Figure(data=edge_trace + [node_trace])
        
        fig.update_layout(
            title="Service Dependency Graph (Based on Cascade Failures)",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(0,0,0,0)',
            height=500
        )
        
        return fig