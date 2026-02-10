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

class EvidenceItem(BaseModel):
    """Single piece of evidence with citation"""
    file: str = Field(description="Source file name")
    line: Optional[str] = Field(None, description="Line number or section")
    detail: str = Field(description="What this evidence shows")

class RemediationStep(BaseModel):
    """Single actionable remediation"""
    step: str = Field(description="What to do")
    impact: str = Field(description="high, medium, or low")
    rationale: str = Field(description="Why this helps")

class StructuredRCA(BaseModel):
    """Structured Root Cause Analysis output"""
    hypothesis: str = Field(description="Root cause summary")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence 0-1")
    affected_components: List[str] = Field(description="Services/pods impacted")
    evidence: List[EvidenceItem] = Field(description="Supporting evidence with citations")
    remediations: List[RemediationStep] = Field(description="Ranked action items")
    missing_data: Optional[List[str]] = Field(None, description="What observability is missing")
