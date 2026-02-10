import os
import json
from typing import Dict, Any, List, Optional  # ← ADD Optional here!
from pydantic import BaseModel, Field
from ..schema import ExperimentResult

# ===== STRUCTURED OUTPUT SCHEMAS =====
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

# ===== GROQ INTEGRATION =====
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
            try:
                self.llm = ChatGroq(
                    model="llama-3.3-70b-versatile", 
                    api_key=self.api_key, 
                    temperature=0,
                    model_kwargs={"response_format": {"type": "json_object"}}
                )
            except Exception as e:
                print(f"Warning: Could not initialize GROQ LLM: {e}")
                self.llm = None

    def build_structured_prompt(self, scenario, health_summary, fitness_summary):
        """Build prompt that forces JSON schema output"""
        schema_example = {
            "hypothesis": "Cart service experienced cascading failures due to insufficient memory allocation under load",
            "confidence": 0.85,
            "affected_components": ["cart", "checkout"],
            "evidence": [
                {
                    "file": "best_scenarios.json",
                    "line": "generation_1.scenario_1_0",
                    "detail": "Fitness dropped 48% (0.82 → 0.34) when kill_count increased to 2"
                },
                {
                    "file": "health_check_report.csv",
                    "line": "rows 15-23",
                    "detail": "Cart service had 8 consecutive 503 failures during chaos injection"
                }
            ],
            "remediations": [
                {
                    "step": "Implement circuit breaker between cart and checkout services",
                    "impact": "high",
                    "rationale": "Prevents cascade failures when cart is degraded"
                },
                {
                    "step": "Increase cart pod memory limit from 128Mi to 256Mi",
                    "impact": "medium",
                    "rationale": "Current limit may cause OOM under concurrent requests"
                },
                {
                    "step": "Add exponential backoff retry logic to health checks",
                    "impact": "medium",
                    "rationale": "Reduces false positives during transient failures"
                }
            ],
            "missing_data": [
                "Pod resource utilization metrics (CPU/memory)",
                "Network latency between cart and checkout services",
                "Application-level error logs"
            ]
        }

        prompt = f"""You are an expert Site Reliability Engineer analyzing a Kubernetes chaos experiment.

**EXPERIMENT SCENARIO:**
```json
{json.dumps(scenario, indent=2)}
```

**HEALTH CHECK SUMMARY:**
```json
{json.dumps(health_summary, indent=2)}
```

**FITNESS EVOLUTION SUMMARY:**
```json
{json.dumps(fitness_summary, indent=2)}
```

Your task: Analyze this chaos experiment and return a JSON object matching this EXACT schema:
```json
{json.dumps(schema_example, indent=2)}
```

**CRITICAL REQUIREMENTS:**

1. **hypothesis**: Write 1-2 sentence root cause summary explaining WHY the system degraded
2. **confidence**: Numeric value 0.0-1.0 based on evidence strength (be conservative!)
3. **affected_components**: List specific service/pod names from the data
4. **evidence**: MUST cite actual files/lines from the experiment data (e.g., "best_scenarios.json generation_1")
5. **remediations**: Provide 2-4 actionable steps ranked by impact (high/medium/low)
6. **missing_data**: List what observability signals would strengthen your hypothesis

**ANALYSIS RULES:**
- Be conservative with confidence scores (weak evidence = lower confidence)
- Only cite evidence that actually exists in the provided data
- Remediations must be specific and actionable, not generic advice
- If data is insufficient, note what's missing in "missing_data"

Return ONLY the JSON object. No markdown formatting, no code blocks, no additional text."""

        return prompt

    def analyze(self, experiment: ExperimentResult, health_summary: Dict = None, fitness_summary: Dict = None) -> Dict[str, Any]:
        """Analyze with structured output"""
        scenarios = getattr(experiment, 'scenarios', None)
        health_summary = health_summary or {}
        fitness_summary = fitness_summary or {}
        
        # ===== FALLBACK WHEN NO LLM OR NO SCENARIOS =====
        if not scenarios or len(scenarios) == 0 or self.llm is None:
            health_events = experiment.health_events or []
            failed_services = set()
            failure_details = {}
            
            for event in health_events:
                if event.status_code >= 400:  # Failed health check
                    failed_services.add(event.service)
                    if event.service not in failure_details:
                        failure_details[event.service] = []
                    failure_details[event.service].append({
                        "timestamp": event.timestamp,
                        "status": event.status_code,
                        "error": event.error
                    })
            
            # Build deterministic fallback
            evidence_list = []
            if failure_details:
                for svc, failures in failure_details.items():
                    evidence_list.append({
                        "file": "health_check_report.csv",
                        "line": f"{svc} failures",
                        "detail": f"{len(failures)} health check failures detected"
                    })
            
            return {
                "structured": True,
                "fallback": True,
                "hypothesis": f"Health degradation detected in: {', '.join(failed_services) if failed_services else 'No failures'}",
                "confidence": 0.5,
                "affected_components": list(failed_services),
                "evidence": evidence_list,
                "remediations": [
                    {
                        "step": "Enable GROQ_API_KEY environment variable for AI-powered analysis",
                        "impact": "high",
                        "rationale": "Current analysis is deterministic-only without LLM insights"
                    },
                    {
                        "step": "Add scenario YAML files to experiment directory",
                        "impact": "medium",
                        "rationale": "Scenario details needed for deeper root cause analysis"
                    }
                ],
                "missing_data": ["Chaos scenario injection details", "LLM-powered inference", "Prometheus metrics"]
            }
        
        # ===== LLM-POWERED ANALYSIS =====
        scenario = scenarios[0].dict() if hasattr(scenarios[0], 'dict') else scenarios[0]
        
        prompt = self.build_structured_prompt(scenario, health_summary, fitness_summary)
        
        try:
            # Get LLM response
            resp = self.llm.invoke(prompt)
            content = resp.content if hasattr(resp, 'content') else str(resp)
            
            # Parse JSON response
            parsed = json.loads(content)
            
            # Validate with Pydantic
            validated = StructuredRCA(**parsed)
            
            return {
                "structured": True,
                "fallback": False,
                **validated.dict(),
                "metadata": {
                    "model": resp.response_metadata.get("model_name") if hasattr(resp, 'response_metadata') else "llama-3.3-70b-versatile",
                    "tokens": resp.usage_metadata.get("total_tokens") if hasattr(resp, 'usage_metadata') else None
                }
            }
            
        except json.JSONDecodeError as e:
            return {
                "structured": False,
                "error": f"LLM returned invalid JSON: {str(e)}",
                "raw": content[:500],  # First 500 chars for debugging
                "hypothesis": "LLM parsing error - using fallback",
                "confidence": 0.3,
                "affected_components": [],
                "evidence": [],
                "remediations": [
                    {
                        "step": "Check GROQ API response format - may need to adjust model parameters",
                        "impact": "high",
                        "rationale": "LLM did not return valid JSON"
                    }
                ]
            }
        except Exception as e:
            return {
                "structured": False,
                "error": f"Analysis failed: {str(e)}",
                "hypothesis": "Error during analysis",
                "confidence": 0.0,
                "affected_components": [],
                "evidence": [],
                "remediations": [
                    {
                        "step": f"Debug error: {str(e)}",
                        "impact": "high",
                        "rationale": "Unexpected error in root cause agent"
                    }
                ]
            }