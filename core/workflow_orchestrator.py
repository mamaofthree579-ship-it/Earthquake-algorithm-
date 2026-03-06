import uuid
from datetime import datetime

class AutonomousWorkflowOrchestrator:

    def __init__(self, cluster, lineage_core):
        """
        :param cluster: ClusterOrchestrator instance
        :param lineage_core: LineageIntelligenceCore instance
        """
        self.cluster = cluster
        self.lineage_core = lineage_core
        self.workflow_registry = {}

    # --------------------------------------
    # Schedule a Research Task
    # --------------------------------------
    def schedule_task(self, engine_name, engine_method, df=None, parameters=None):
        """
        Schedule an autonomous simulation task.
        """
        task_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        if parameters is None:
            parameters = {}

        # Submit task to cluster
        payload = {
            "task_id": task_id,
            "engine": engine_name,
            "method": engine_method.__name__,
            "parameters": parameters,
            "dataset_rows": 0 if df is None else len(df),
            "timestamp": timestamp
        }

        job_id = self.cluster.submit_job(payload)

        # Record initial workflow state
        self.workflow_registry[task_id] = {
            "job_id": job_id,
            "status": "submitted",
            "engine": engine_name,
            "method": engine_method.__name__,
            "parameters": parameters,
            "dataset_rows": 0 if df is None else len(df),
            "timestamp": timestamp,
            "lineage_id": None,
            "result_preview": None
        }

        return task_id, job_id

    # --------------------------------------
    # Complete Task and Record Lineage
    # --------------------------------------
    def complete_task(self, task_id, df=None, parameters=None, result=None):
        """
        Mark a task as complete and store lineage.
        """
        if task_id not in self.workflow_registry:
            raise ValueError(f"Task {task_id} not found")

        if parameters is None:
            parameters = {}

        lineage_id = self.lineage_core.register_experiment(df, parameters, result)

        self.workflow_registry[task_id]["status"] = "completed"
        self.workflow_registry[task_id]["lineage_id"] = lineage_id
        self.workflow_registry[task_id]["result_preview"] = result

        return lineage_id

    # --------------------------------------
    # List Current Workflows
    # --------------------------------------
    def list_workflows(self):
        return self.workflow_registry
