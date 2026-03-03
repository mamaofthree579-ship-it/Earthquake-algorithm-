import numpy as np


class ScientificClusterOrchestrator:
    """
    Research workload orchestration abstraction.

    Responsibilities:
    - Node registry management
    - Compute node selection
    - Simulation workload delegation
    - Health-weighted scheduling proxy
    """

    def __init__(self):
        self.node_registry = {}

    # --------------------------------------
    # Node Management
    # --------------------------------------

    def register_node(self, node_id: str, health_score: float):
        """
        Register or update node health status.

        Parameters
        ----------
        node_id : str
            Unique compute node identifier

        health_score : float
            Node operational health proxy (0-1)
        """

        self.node_registry[node_id] = np.clip(health_score, 0.0, 1.0)

    def remove_node(self, node_id: str):
        """Remove node from federation registry."""
        if node_id in self.node_registry:
            del self.node_registry[node_id]

    # --------------------------------------
    # Scheduling Logic
    # --------------------------------------

    def schedule_node(self):
        """
        Select compute node using health-weighted priority.

        Returns
        -------
        Selected node identifier or None if registry empty.
        """

        if not self.node_registry:
            return None

        # Select highest health node
        return max(
            self.node_registry.items(),
            key=lambda x: x[1]
        )[0]

    # --------------------------------------
    # Workload Execution Proxy
    # --------------------------------------

    def execute_kernel_step(self, kernel):
        """
        Execute one simulation kernel cycle.

        Parameters
        ----------
        kernel : object
            Expected to implement `step()` method.

        Returns
        -------
        Simulation field state or None
        """

        node = self.schedule_node()

        if node is None:
            return None

        if hasattr(kernel, "step"):
            return kernel.step()

        return None

    # --------------------------------------
    # Cluster Diagnostics
    # --------------------------------------

    def cluster_health_index(self):
        """
        Compute aggregate cluster health metric.
        """

        if not self.node_registry:
            return 0.0

        return float(
            np.mean(list(self.node_registry.values()))
        )
