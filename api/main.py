from fastapi import FastAPI
from core.cluster_orchestrator import ClusterOrchestrator
from core.task_scheduler import TaskScheduler
from core.mesh_runtime import MeshRuntime
from governance.ethics_kernel import EthicsKernel

app = FastAPI()

orchestrator = ClusterOrchestrator()
scheduler = TaskScheduler(orchestrator)
runtime = MeshRuntime(orchestrator)
ethics = EthicsKernel()

@app.post("/register_node")
def register_node(node_id: str):
    orchestrator.register_node(node_id)
    return {"status": "registered"}

@app.post("/submit_job")
def submit_job():
    def sample_compute():
        return {"value": 42}

    payload = {"compute": sample_compute}

    approved, message = ethics.validate(payload)
    if not approved:
        return {"error": message}

    job_id = orchestrator.submit_job(payload)
    scheduler.schedule()
    runtime.execute(job_id)

    return orchestrator.jobs[job_id]
