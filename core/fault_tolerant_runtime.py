import time
import traceback
import threading
import numpy as np


class FaultTolerantScientificClusterRuntime:
    """
    Fault-tolerant scientific cluster runtime abstraction.

    Features:
    - Node health monitoring
    - Automatic failover
    - Retry logic
    - State checkpointing
    - Graceful degradation
    """

    def __init__(self, max_retries=3, retry_delay=1.0):
        self.nodes = {}
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.checkpoints = {}
        self.lock = threading.Lock()

    # --------------------------------------------------
    # NODE REGISTRY
    # --------------------------------------------------

    def register_node(self, node_id, health_score=1.0):
        with self.lock:
            self.nodes[node_id] = {
                "health": float(np.clip(health_score, 0, 1)),
                "failures": 0,
                "last_seen": time.time()
            }

    def update_health(self, node_id, health_score):
        with self.lock:
            if node_id in self.nodes:
                self.nodes[node_id]["health"] = float(
                    np.clip(health_score, 0, 1)
                )
                self.nodes[node_id]["last_seen"] = time.time()

    def remove_node(self, node_id):
        with self.lock:
            self.nodes.pop(node_id, None)

    # --------------------------------------------------
    # SCHEDULING
    # --------------------------------------------------

    def _select_best_node(self):
        if not self.nodes:
            return None

        # Prefer healthiest node with lowest failures
        sorted_nodes = sorted(
            self.nodes.items(),
            key=lambda x: (x[1]["health"], -x[1]["failures"]),
            reverse=True
        )

        return sorted_nodes[0][0]

    # --------------------------------------------------
    # CHECKPOINTING
    # --------------------------------------------------

    def save_checkpoint(self, task_id, state):
        self.checkpoints[task_id] = state

    def load_checkpoint(self, task_id):
        return self.checkpoints.get(task_id, None)

    # --------------------------------------------------
    # EXECUTION WITH FAILOVER
    # --------------------------------------------------

    def execute_task(self, task_id, kernel):

        retries = 0

        while retries <= self.max_retries:

            node_id = self._select_best_node()

            if node_id is None:
                print("No nodes available.")
                return None

            try:
                result = kernel.step()

                # Save checkpoint
                self.save_checkpoint(task_id, result)

                # Reset failure count
                self.nodes[node_id]["failures"] = 0

                return result

            except Exception as e:

                print(f"Node {node_id} failed:")
                traceback.print_exc()

                self.nodes[node_id]["failures"] += 1
                self.nodes[node_id]["health"] *= 0.8

                retries += 1
                time.sleep(self.retry_delay)

        print("Max retries exceeded.")
        return self.load_checkpoint(task_id)

    # --------------------------------------------------
    # CLUSTER DIAGNOSTICS
    # --------------------------------------------------

    def cluster_health_index(self):

        if not self.nodes:
            return 0.0

        return float(
            np.mean([n["health"] for n in self.nodes.values()])
        )

    def cluster_status_report(self):

        return {
            node_id: {
                "health": node["health"],
                "failures": node["failures"],
                "last_seen": node["last_seen"]
            }
            for node_id, node in self.nodes.items()
        }
