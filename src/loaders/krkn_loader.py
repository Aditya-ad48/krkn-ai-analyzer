import json
import yaml
import csv
from pathlib import Path
from typing import Optional, Dict, Any
from ..parsers.scenario_parser import ScenarioParser
from ..parsers.health_parser import HealthParser
from ..parsers.fitness_parser import FitnessParser
from ..schema import ExperimentResult, ExperimentMetadata

class KrknResultsLoader:
    """
    Auto-detects a directory containing Krkn-AI output (or synthetic)
    and returns a canonical ExperimentResult.
    """

    def __init__(self, base_dir: str):
        self.base = Path(base_dir)
        self.scenario_parser = ScenarioParser()
        self.health_parser = HealthParser()
        self.fitness_parser = FitnessParser()

    def auto_detect_format(self) -> Dict[str, bool]:
        found = {
            "best_scenarios.json": (self.base / "best_scenarios.json").exists(),
            "health_check_report.csv": (self.base / "health_check_report.csv").exists(),
            "yaml_dirs": any(p.is_dir() for p in (self.base / "yaml").glob("*")) if (self.base / "yaml").exists() else False,
            "prometheus": (self.base / "prometheus_metrics.json").exists()
        }
        return found

    def load(self) -> ExperimentResult:
        md = ExperimentMetadata(experiment_id=self.base.name)
        result = ExperimentResult(metadata=md, raw_files={})
        # Best scenarios
        bs = self.base / "best_scenarios.json"
        if bs.exists():
            result.raw_files["best_scenarios.json"] = str(bs)
            result.scenarios, result.fitness = self.scenario_parser.parse_best_scenarios(bs)
        # Health checks
        hc = self.base / "health_check_report.csv"
        if hc.exists():
            result.raw_files["health_check_report.csv"] = str(hc)
            result.health_events = self.health_parser.parse(hc)
        # Prometheus
        prom = self.base / "prometheus_metrics.json"
        if prom.exists():
            result.raw_files["prometheus_metrics.json"] = str(prom)
            with open(prom) as f:
                result.prometheus_metrics = json.load(f)
        # Also parse per-scenario YAMLs if present
        yaml_root = self.base / "yaml"
        if yaml_root.exists():
            scenario_list = self.scenario_parser.parse_generation_dir(yaml_root)
            # merge unique scenarios
            existing_ids = {s.id for s in result.scenarios}
            for s in scenario_list:
                if s.id not in existing_ids:
                    result.scenarios.append(s)
        return result
