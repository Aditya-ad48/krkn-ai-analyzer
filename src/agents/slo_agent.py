from typing import Dict, Any, List
from ..schema import ExperimentResult

class SLOAgent:
    """
    Validates experiment results against SLO thresholds.
    """
    
    def __init__(self, error_rate_threshold: float = 0.01, latency_p99_threshold: float = 500.0):
        self.error_rate_threshold = error_rate_threshold
        self.latency_p99_threshold = latency_p99_threshold

    def analyze(self, exp: ExperimentResult) -> Dict[str, Any]:
        """Analyze experiment against SLO thresholds."""
        violations: List[Dict[str, Any]] = []
        
        health_events = exp.health_events or []
        
        if not health_events:
            return {
                "violations": [],
                "error_rate": 0.0,
                "status": "no_data"
            }
        
        # Calculate error rate
        total = len(health_events)
        failures = sum(1 for e in health_events if not e.healthy)
        error_rate = failures / total if total > 0 else 0.0
        
        if error_rate > self.error_rate_threshold:
            violations.append({
                "type": "error_rate",
                "error_rate": error_rate,
                "threshold": self.error_rate_threshold
            })
        
        # Calculate latency stats if available
        latencies = [e.latency_ms for e in health_events if e.latency_ms is not None]
        latency_p99 = None
        if latencies:
            latencies_sorted = sorted(latencies)
            p99_idx = int(len(latencies_sorted) * 0.99)
            latency_p99 = latencies_sorted[min(p99_idx, len(latencies_sorted) - 1)]
            
            if latency_p99 > self.latency_p99_threshold:
                violations.append({
                    "type": "latency_p99",
                    "latency_p99": latency_p99,
                    "threshold": self.latency_p99_threshold
                })
        
        return {
            "violations": violations,
            "error_rate": error_rate,
            "latency_p99": latency_p99,
            "status": "violated" if violations else "passed"
        }
