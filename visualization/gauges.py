import plotly.graph_objects as go

def render_gauge(value, title="Metric"):

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title}
    ))

    return fig
