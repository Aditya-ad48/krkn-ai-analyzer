import os
from typing import Dict, Any, Optional
from ..schema import ExperimentResult

try:
    from langchain_groq import ChatGroq
except Exception:
    ChatGroq = None

class RootCauseAgent:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if ChatGroq is None:
            self.llm = None
        else:
            self.llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=self.api_key, temperature=0)

    def build_prompt(self, scenario, health_summary, fitness_summary, extra_context=""):
        prompt = [
            "You are an expert SRE. Analyze the following chaos experiment evidence and produce:",
            "1) A concise root-cause hypothesis with explicit citations like [file:line].",
            "2) A numeric summary (what dropped by how much, time windows).",
            "3) 3 practical remediation steps ranked by impact.",
            "",
            "SCENARIO:",
            str(scenario),
            "",
            "HEALTH_SUMMARY:",
            str(health_summary),
            "",
            "FITNESS_SUMMARY:",
            str(fitness_summary),
            "",
            "EXTRA_CONTEXT:",
            extra_context,
            "",
            "Be conservative. If evidence is missing, say so and list what you would need."
        ]
        return "\n".join(prompt)

    def analyze(self, experiment: ExperimentResult, health_summary: Dict = None, fitness_summary: Dict = None) -> Dict[str, Any]:
        """Single analyze method that handles both cases."""
        scenarios = getattr(experiment, 'scenarios', None)
        
        # No scenarios available
        if not scenarios or len(scenarios) == 0:
            health_events = experiment.health_events or []
            failed_services = set()
            for event in health_events:
                if not event.healthy:
                    failed_services.add(event.service)
            
            return {
                "hypothesis": f"Services affected: {', '.join(failed_services) if failed_services else 'None detected'}",
                "confidence": 0.7 if failed_services else 0.3,
                "affected_services": list(failed_services),
                "details": "No scenario injection data found.",
                "recommendations": [
                    "Review timeout configurations for affected services",
                    "Check circuit breaker settings",
                    "Add scenario.yaml with chaos injection details"
                ]
            }
        
        # Has scenarios - use LLM if available
        scenario = scenarios[0]
        health_summary = health_summary or {}
        fitness_summary = fitness_summary or {}
        
        prompt = self.build_prompt(scenario.model_dump(), health_summary, fitness_summary)
        
        if self.llm is None:
            return {
                "warning": "GROQ unavailable in dev environment",
                "prompt": prompt,
                "scenario_count": len(scenarios),
                "suggested_remediations": [
                    "Implement circuit breaker for critical dependency",
                    "Add retries with exponential backoff in health checks",
                    "Increase readiness/liveness probe sensitivity"
                ]
            }
        
        resp = self.llm.invoke(prompt)
        
        # Extract content from LLM response
        content = resp.content if hasattr(resp, 'content') else str(resp)
        
        # Parse the structured response
        return {
            "raw": content,
            "model": resp.response_metadata.get("model_name") if hasattr(resp, 'response_metadata') else None,
            "tokens_used": resp.usage_metadata.get("total_tokens") if hasattr(resp, 'usage_metadata') else None
        }
