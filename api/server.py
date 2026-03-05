from fastapi import FastAPI
from core.cluster_orchestrator import ClusterOrchestrator
from experiments.example_experiment import run_experiment

app = FastAPI()

cluster = ClusterOrchestrator()

@app.post("/submit_job")
def submit_job():

    params = {"x": 5, "y": 10}

    job_id = cluster.submit_job(run_experiment, params)

    return {"job_id": job_id}

@app.get("/job_status/{job_id}")
def job_status(job_id: str):

    status = cluster.job_status(job_id)

    return {"status": status}

@app.get("/artifacts")
def artifacts():

    return cluster.ledger.list_artifacts()
