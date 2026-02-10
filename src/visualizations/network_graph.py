import networkx as nx
import plotly.graph_objects as go

def build_component_graph(scenarios, health_events):
    """
    Build dependency graph inferred from shared failure windows.
    """
    G = nx.Graph()

    for s in scenarios:
        if s.target:
            G.add_node(s.target, size=10)

    if health_events:
        by_time = {}
        for e in health_events:
            if e.status_code >= 400:
                by_time.setdefault(e.timestamp[:16], []).append(e.service)

        for services in by_time.values():
            for i in range(len(services)):
                for j in range(i + 1, len(services)):
                    G.add_edge(services[i], services[j])

    pos = nx.spring_layout(G, seed=42)
    edge_x, edge_y = [], []

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    node_x, node_y, labels = [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        labels.append(node)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(width=1, color="#aaa")
    ))
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=labels,
        textposition="bottom center",
        marker=dict(size=20, color="#ff6f61")
    ))

    fig.update_layout(
        title="Inferred Service Dependency Graph",
        showlegend=False,
        template="plotly_white"
    )
    return fig
