from typing import Dict, Any
from .agents.fitness_agent import FitnessAgent
from .agents.health_agent import HealthAgent
from .agents.slo_agent import SLOAgent
from .agents.root_cause_agent import RootCauseAgent
from .schema import ExperimentResult

class Orchestrator:
    """
    Coordinates the multi-agent analysis workflow.
    """

    def __init__(self):
        self.fitness_agent = FitnessAgent()
        self.health_agent = HealthAgent()
        self.slo_agent = SLOAgent()
        self.root_agent = RootCauseAgent()

    def analyze_experiment(self, exp: ExperimentResult) -> Dict[str, Any]:
        out = {}
        out["fitness"] = self.fitness_agent.analyze(exp)
        out["health"] = self.health_agent.analyze(exp)
        out["slo"] = self.slo_agent.analyze(exp)
        
        # Pass health and fitness summaries to root cause agent
        out["root_cause"] = self.root_agent.analyze(
            exp, 
            health_summary=out["health"], 
            fitness_summary=out["fitness"]
        )
        
        return out
