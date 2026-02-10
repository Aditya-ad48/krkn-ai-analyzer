from typing import Dict, Any
import numpy as np
from ..schema import ExperimentResult

class FitnessAgent:
    """
    Analyzes fitness evolution and returns a compact summary dict.
    """

    def analyze(self, exp: ExperimentResult) -> Dict[str, Any]:
        # Aggregate best/avg/worst per generation
        gen_map = {}
        for f in exp.fitness:
            gen_map.setdefault(f.generation, []).append(f.fitness_score)

        results = {"per_generation": {}, "best_overall": None}
        best = (None, 1.0)  # (scenario_id, score)
        for gen, scores in gen_map.items():
            arr = np.array(scores)
            results["per_generation"][gen] = {
                "best": float(arr.min()),
                "avg": float(arr.mean()),
                "worst": float(arr.max()),
                "count": int(arr.size)
            }
            # find best scenario (lowest fitness)
            idx = arr.argmin()
            if arr.min() < best[1]:
                # naive: we don't track scenario_id here; front-end can match by generation+score
                best = (f"gen{gen}_best", float(arr.min()))
        results["best_overall"] = {"scenario_id": best[0], "fitness_score": best[1]}
        # detect plateau or fast drop using simple slope heuristics
        gens = sorted(results["per_generation"].keys())
        avgs = [results["per_generation"][g]["avg"] for g in gens]
        if len(avgs) >= 3:
            slope = (avgs[-1] - avgs[0]) / (len(avgs)-1)
            results["trend"] = "improving" if slope < 0 else ("degrading" if slope > 0 else "stable")
            results["slope"] = slope
        else:
            results["trend"] = "insufficient_data"
            results["slope"] = 0.0
        return results
