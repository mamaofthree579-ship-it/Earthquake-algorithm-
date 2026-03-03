import plotly.graph_objects as go
import numpy as np

def render_geo_map(df):

    fig = go.Figure()

    if df.empty:
        return fig

    df["marker_size"] = np.clip(df["magnitude"] * 2, 2, 20)

    fig.add_trace(go.Scattergeo(
        lon=df["longitude"].tolist(),
        lat=df["latitude"].tolist(),
        mode="markers",
        marker=dict(
            size=df["marker_size"].tolist(),
            color=df["magnitude"].tolist(),
            colorscale="Viridis"
        )
    ))

    fig.update_geos(projection_type="natural earth")

    return fig
