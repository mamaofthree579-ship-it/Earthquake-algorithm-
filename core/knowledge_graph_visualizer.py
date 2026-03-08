import plotly.graph_objects as go


class KnowledgeGraphVisualizer:

    def __init__(self, memory_graph):
        self.memory_graph = memory_graph

    def build_graph_figure(self):

        nodes = list(self.memory_graph.nodes.values())
        edges = self.memory_graph.edges

        if not nodes:
            return None

        node_ids = [n["id"] for n in nodes]

        # Simple circular layout positioning
        n = len(node_ids)
        angles = [i * 2 * 3.14159 / max(n, 1) for i in range(n)]

        positions = {
            node_ids[i]: (
                float(0.5 + 0.4 * __import__("math").cos(angles[i])),
                float(0.5 + 0.4 * __import__("math").sin(angles[i]))
            )
            for i in range(n)
        }

        fig = go.Figure()

        # Draw edges
        for edge in edges:
            if edge["from"] in positions and edge["to"] in positions:

                x0, y0 = positions[edge["from"]]
                x1, y1 = positions[edge["to"]]

                fig.add_trace(go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode="lines",
                    line=dict(width=1),
                    hoverinfo="none"
                ))

        # Draw nodes
        for node in nodes:

            x, y = positions[node["id"]]

            fig.add_trace(go.Scatter(
                x=[x],
                y=[y],
                mode="markers+text",
                marker=dict(size=12),
                text=[str(node["id"][:6])],
                textposition="top center",
                hovertext=str(node["parameters"]),
                name="experiment_node"
            ))

        fig.update_layout(
            showlegend=False,
            height=600
        )

        return fig
