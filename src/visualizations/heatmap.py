import pandas as pd
import plotly.express as px

def failure_correlation_heatmap(health_events):
    """
    Heatmap showing which services fail together.
    """
    if not health_events:
        return None

    df = pd.DataFrame([e.dict() for e in health_events])
    df = df[df["status_code"] >= 400]

    if df.empty:
        return None

    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.floor("30s")
    matrix = (
        df.groupby(["timestamp", "service"])
        .size()
        .unstack(fill_value=0)
    )

    corr = matrix.corr()

    fig = px.imshow(
        corr,
        text_auto=True,
        title="Service Failure Correlation Heatmap",
        color_continuous_scale="Reds"
    )
    return fig
