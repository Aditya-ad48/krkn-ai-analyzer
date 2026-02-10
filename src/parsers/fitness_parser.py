import json
from pathlib import Path
from typing import List
from ..schema import FitnessRecord

class FitnessParser:
    """
    Simple parser for JSON fitness dumps if present.
    For krkn best_scenarios.json most parsing happens in scenario_parser,
    but this keeps fitness parsing isolated if a separate file exists.
    """
    def parse(self, json_path: Path) -> List[FitnessRecord]:
        with open(json_path) as f:
            data = json.load(f)
        records = []
        # Support two shapes: list of dicts or dict by generation
        if isinstance(data, list):
            for item in data:
                records.append(FitnessRecord(
                    generation=int(item.get("generation", -1)),
                    scenario_id=item.get("scenario_id", "unknown"),
                    fitness_score=float(item.get("fitness_score", 1.0))
                ))
        elif isinstance(data, dict):
            for key, items in data.items():
                if key.startswith("generation_"):
                    gen = int(key.split("_")[1])
                    for item in items:
                        records.append(FitnessRecord(
                            generation=gen,
                            scenario_id=item.get("scenario_id"),
                            fitness_score=float(item.get("fitness_score", 1.0))
                        ))
        return records
