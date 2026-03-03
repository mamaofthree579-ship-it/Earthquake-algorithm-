import plotly.graph_objects as go

def render_global_map(lon, lat, magnitude):

    fig = go.Figure()

    fig.add_trace(go.Scattergeo(
        lon=lon,
        lat=lat,
        mode="markers",
        marker=dict(
            size=[max(m * 2, 2) for m in magnitude],
            color=magnitude,
            colorscale="Viridis"
        )
    ))

    fig.update_geos(projection_type="natural earth")

    return fig
