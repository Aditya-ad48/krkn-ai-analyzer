from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class HealthEvent(BaseModel):
    timestamp: str
    service: str
    url: Optional[str] = None
    status_code: Optional[int] = None
    latency_ms: Optional[float] = None
    healthy: bool = True
    error: Optional[str] = None