import numpy as np
import uuid


class MetaResearchAgent:

    def __init__(self, engine, memory_graph):

        self.engine = engine
        self.memory_graph = memory_graph

    # -------------------------------------------------
    # Generate Hypothesis Parameters
    # -------------------------------------------------

    def generate_hypothesis(self):

        return {
            "t": int(np.random.randint(0, 365))
        }

    # -------------------------------------------------
    # Execute Research Trial
    # -------------------------------------------------

    def run_trial(self):

        params = self.generate_hypothesis()

        score = self.engine.predict_risk(params["t"])

        node_id = self.memory_graph.add_experiment(
            params,
            {"hazard_index": score},
            governance_score=score
        )

        return {
            "agent_id": str(uuid.uuid4()),
            "parameters": params,
            "score": score,
            "node_id": node_id
        }


# =====================================================
# Meta OS Kernel
# =====================================================

class MetaOSKernel:

    def __init__(
        self,
        harmonic_engine,
        memory_graph,
        agent_count=4
    ):

        self.harmonic_engine = harmonic_engine
        self.memory_graph = memory_graph

        self.agents = [
            MetaResearchAgent(
                harmonic_engine,
                memory_graph
            )
            for _ in range(agent_count)
        ]

        self.convergence_history = []

    # -------------------------------------------------
    # Run Discovery Cycle
    # -------------------------------------------------

    def run_discovery_cycle(self, iterations=5):

        cycle_results = []

        for _ in range(iterations):

            agent_scores = []

            for agent in self.agents:

                trial = agent.run_trial()
                agent_scores.append(trial["score"])

                cycle_results.append(trial)

            # Convergence metric
            convergence_metric = float(
                1.0 / (1.0 + np.std(agent_scores))
            )

            self.convergence_history.append(convergence_metric)

        return {
            "cycle_results": cycle_results,
            "convergence_score": float(
                np.mean(self.convergence_history)
            ),
            "agents_active": len(self.agents)
        }

    # -------------------------------------------------
    # Kernel Status
    # -------------------------------------------------

    def status(self):

        return {
            "agents": len(self.agents),
            "cycles_run": len(self.convergence_history),
            "last_convergence": self.convergence_history[-1]
            if self.convergence_history else 0.0
        }
