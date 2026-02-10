import pandas as pd
import plotly.graph_objects as go

def fitness_evolution_chart(fitness_records):
    """
    Plot best / avg / worst fitness per generation.
    """
    if not fitness_records:
        return None

    df = pd.DataFrame([f.dict() for f in fitness_records])
    grouped = df.groupby("generation")["fitness_score"]

    summary = grouped.agg(["min", "mean", "max"]).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=summary["generation"], y=summary["min"],
        name="Best (Lowest)", mode="lines+markers"
    ))
    fig.add_trace(go.Scatter(
        x=summary["generation"], y=summary["mean"],
        name="Average", mode="lines+markers"
    ))
    fig.add_trace(go.Scatter(
        x=summary["generation"], y=summary["max"],
        name="Worst (Highest)", mode="lines+markers"
    ))

    fig.update_layout(
        title="Fitness Evolution Across Generations",
        xaxis_title="Generation",
        yaxis_title="Fitness Score",
        template="plotly_white"
    )
    return fig
