import uuid
from datetime import datetime
import numpy as np


class AutonomousScientificCivilizationKernel:

    def __init__(self, orchestrator, governance_layer, lineage_core):

        self.orchestrator = orchestrator
        self.governance_layer = governance_layer
        self.lineage_core = lineage_core

        self.cycle_history = []

    # -------------------------------------------------
    # Hypothesis Generator
    # -------------------------------------------------

    def generate_hypothesis(self):

        hypothesis = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "type": "harmonic_resonance_variation",
            "parameters": {
                "t": int(np.random.randint(0, 365))
            }
        }

        return hypothesis

    # -------------------------------------------------
    # Execute Research Cycle
    # -------------------------------------------------

    def run_cycle(self, engine, df):

        hypothesis = self.generate_hypothesis()

        task_id, job_id = self.orchestrator.schedule_task(
            engine_name="HarmonicPredictionEngine",
            engine_method=engine.predict_risk,
            df=df,
            parameters=hypothesis["parameters"]
        )

        t = hypothesis["parameters"]["t"]
        result = {"hazard_index": engine.predict_risk(t)}

        lineage_id = self.orchestrator.complete_task(
            task_id,
            df=df,
            parameters=hypothesis["parameters"],
            result=result
        )

        governance = self.governance_layer.evaluate_governance(
            df,
            result
        )

        record = {
            "cycle_id": hypothesis["id"],
            "job_id": job_id,
            "lineage_id": lineage_id,
            "parameters": hypothesis["parameters"],
            "result": result,
            "governance_index": governance["governance_index"]
        }

        self.cycle_history.append(record)

        return record

    # -------------------------------------------------
    # Rank Scientific Cycles
    # -------------------------------------------------

    def rank_cycles(self):

        ranked = sorted(
            self.cycle_history,
            key=lambda x: x["governance_index"],
            reverse=True
        )

        return ranked

    # -------------------------------------------------
    # Civilization Status
    # -------------------------------------------------

    def civilization_status(self):

        return {
            "total_cycles": len(self.cycle_history),
            "top_cycles": self.rank_cycles()[:3]
        }
