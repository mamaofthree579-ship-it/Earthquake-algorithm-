import time
import queue
import threading
import numpy as np
from concurrent.futures import ThreadPoolExecutor


class DistributedScientificComputeMesh:
    """
    Distributed scientific compute mesh runtime.

    Features:
    - Multi-worker execution
    - Health-aware scheduling
    - Task queue system
    - Checkpoint storage
    - Graceful worker degradation
    """

    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        self.task_queue = queue.Queue()
        self.nodes = {}
        self.checkpoints = {}
        self.lock = threading.Lock()
        self.running = False

    # --------------------------------------------------
    # NODE REGISTRATION
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

    # --------------------------------------------------
    # TASK MANAGEMENT
    # --------------------------------------------------

    def submit_task(self, task_id, kernel):

        self.task_queue.put((task_id, kernel))

    def save_checkpoint(self, task_id, state):

        self.checkpoints[task_id] = state

    def load_checkpoint(self, task_id):

        return self.checkpoints.get(task_id, None)

    # --------------------------------------------------
    # SCHEDULING
    # --------------------------------------------------

    def _select_node(self):

        if not self.nodes:
            return None

        return max(
            self.nodes.items(),
            key=lambda x: x[1]["health"]
        )[0]

    def _execute(self, task_id, kernel):

        node_id = self._select_node()

        if node_id is None:
            return None

        try:
            result = kernel.step()

            self.save_checkpoint(task_id, result)

            with self.lock:
                self.nodes[node_id]["failures"] = 0

            return result

        except Exception:

            with self.lock:
                self.nodes[node_id]["failures"] += 1
                self.nodes[node_id]["health"] *= 0.8

            return self.load_checkpoint(task_id)

    # --------------------------------------------------
    # RUNTIME LOOP
    # --------------------------------------------------

    def start(self):

        if self.running:
            return

        self.running = True

        def worker_loop():
            while self.running:
                try:
                    task_id, kernel = self.task_queue.get(timeout=1)
                    self.executor.submit(self._execute, task_id, kernel)
                except queue.Empty:
                    continue

        self.runtime_thread = threading.Thread(target=worker_loop)
        self.runtime_thread.daemon = True
        self.runtime_thread.start()

    def stop(self):

        self.running = False
        self.executor.shutdown(wait=True)

    # --------------------------------------------------
    # DIAGNOSTICS
    # --------------------------------------------------

    def cluster_health_index(self):

        if not self.nodes:
            return 0.0

        return float(
            np.mean([n["health"] for n in self.nodes.values()])
        )

    def status_report(self):

        return {
            node_id: {
                "health": node["health"],
                "failures": node["failures"],
                "last_seen": node["last_seen"]
            }
            for node_id, node in self.nodes.items()
        }
