from typing import Dict, Any
import pandas as pd
from ..schema import ExperimentResult

class HealthAgent:
    """
    Correlates health events to produce MTTR, failure counts, and cascade hints.
    """

    def analyze(self, exp: ExperimentResult) -> Dict[str, Any]:
        if not exp.health_events:
            return {"error": "no_health_data"}
        df = pd.DataFrame([e.dict() for e in exp.health_events])
        summary = {}
        # Failure counts by service
        fail_df = df[df["status_code"] >= 400]
        counts = fail_df.groupby("service").size().to_dict()
        summary["failure_counts"] = counts
        # Simple MTTR per service: compute contiguous failure windows (naive)
        mttr = {}
        for svc, group in df.groupby("service"):
            service_fail = group[group["status_code"] >= 400]
            if service_fail.empty:
                mttr[svc] = 0.0
                continue
            # assume timestamp strings parseable by pandas
            times = pd.to_datetime(service_fail["timestamp"])
            durations = (times.max() - times.min()).total_seconds()
            mttr[svc] = durations
        summary["mttr_seconds"] = mttr
        # Simple cascade hint: services that fail within the same time bucket
        df["ts"] = pd.to_datetime(df["timestamp"]).dt.floor("30s")
        buckets = df[df["status_code"] >= 400].groupby("ts")["service"].unique().apply(list).to_dict()
        cascades = [v for v in buckets.values() if len(v) > 1]
        summary["cascade_samples"] = cascades[:10]
        return summary
