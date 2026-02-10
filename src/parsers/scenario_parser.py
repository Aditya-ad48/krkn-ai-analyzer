import json
from pathlib import Path
import yaml
from typing import List, Tuple
from ..schema import Scenario, FitnessRecord

class ScenarioParser:
    """
    Parses best_scenarios.json and scenario YAML directories.
    """

    def parse_best_scenarios(self, json_path: Path) -> Tuple[List[Scenario], List[FitnessRecord]]:
        with open(json_path) as f:
            data = json.load(f)
        scenarios = []
        fitness = []
        for key, gen_items in data.items():
            if key.startswith("generation_"):
                gen_num = int(key.split("_")[1])
                for item in gen_items:
                    sid = item.get("scenario_id") or item.get("id") or f"gen{gen_num}_unknown"
                    sc = Scenario(
                        id=sid,
                        generation=gen_num,
                        scenario_type=item.get("scenario_type", "unknown"),
                        target=item.get("config", {}).get("pod_name") or item.get("config", {}).get("label_selector"),
                        raw_config=item.get("config", {}),
                        source_file=str(json_path)
                    )
                    scenarios.append(sc)
                    fitness.append(FitnessRecord(
                        generation=gen_num,
                        scenario_id=sid,
                        fitness_score=float(item.get("fitness_score", 1.0))
                    ))
        return scenarios, fitness

    def parse_generation_dir(self, yaml_root: Path) -> List[Scenario]:
        scenarios = []
        for gen_dir in yaml_root.glob("generation_*"):
            gen_num = int(gen_dir.name.split("_")[1]) if "generation_" in gen_dir.name else -1
            for f in gen_dir.glob("*.yaml"):
                with open(f) as fh:
                    doc = yaml.safe_load(fh)
                sid = doc.get("name") or f.stem
                sc = Scenario(
                    id=sid,
                    generation=gen_num,
                    scenario_type=doc.get("scenario_type", "pod-scenarios"),
                    target=doc.get("label_selector") or doc.get("namespace"),
                    raw_config=doc,
                    source_file=str(f)
                )
                scenarios.append(sc)
        return scenarios
