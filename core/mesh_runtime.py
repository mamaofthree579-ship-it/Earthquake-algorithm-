import queue
import threading

class ComputeMesh:

    def __init__(self, nodes=4):

        self.nodes = nodes
        self.task_queue = queue.Queue()

        for i in range(nodes):

            t = threading.Thread(target=self.worker_loop)
            t.daemon = True
            t.start()

    def worker_loop(self):

        while True:

            func, params = self.task_queue.get()

            try:
                func(**params)
            finally:
                self.task_queue.task_done()

    def submit(self, func, params):

        self.task_queue.put((func, params))
