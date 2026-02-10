from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class Scenario(BaseModel):
    id: str
    generation: int
    scenario_type: str
    target: Optional[str] = None
    raw_config: Dict[str, Any] = {}
    source_file: Optional[str] = None

class FitnessRecord(BaseModel):
    generation: int
    scenario_id: str
    fitness_score: float

class HealthEvent(BaseModel):
    timestamp: str
    service: str
    url: Optional[str]
    status_code: int
    latency_ms: Optional[int]
    error: Optional[str] = None

class ExperimentMetadata(BaseModel):
    experiment_id: str
    created_at: Optional[str] = None
    duration_seconds: Optional[int] = None
    notes: Optional[str] = None

class ExperimentResult(BaseModel):
    metadata: ExperimentMetadata
    scenarios: List[Scenario] = []
    fitness: List[FitnessRecord] = []
    health_events: List[HealthEvent] = []
    prometheus_metrics: Optional[List[Dict[str, Any]]] = None
    raw_files: Optional[Dict[str, str]] = None
