# Krkn-AI Analyzer – Architecture

## Overview

Krkn-AI Analyzer is an analysis and visualization layer built on top of
Krkn-AI chaos engineering results. While Krkn-AI focuses on *generating*
and *executing* chaos experiments, this project focuses on *interpreting*
their outcomes in a scalable, explainable, and operator-friendly way.

The system ingests native Krkn-AI result artifacts (JSON, CSV, YAML),
normalizes them into a canonical schema, and applies multi-agent analysis,
anomaly detection, historical comparison, and interactive visualization.

---

## Design Goals

1. **Schema-first design**  
   All inputs (synthetic or real) are normalized into a single
   `ExperimentResult` contract using Pydantic models.

2. **Separation of concerns**  
   - Krkn-AI → experiment execution  
   - This project → analysis, insight, visualization

3. **Explainability over black-box AI**  
   LLM output is always grounded in numeric evidence and file-level citations.
   Structured JSON output with Pydantic validation ensures consistency.

4. **Incremental adoption**  
   Works with partial data (e.g., no health checks, no Prometheus metrics).
   Graceful degradation when components are unavailable.

5. **Production-ready architecture**  
   Modular agents, extensible parsers, clear error handling.

---

## High-Level Architecture

```
        ┌───────────────────────────┐
        │    Krkn-AI Results        │
        │  (JSON / CSV / YAML)      │
        └─────────┬─────────────────┘
                  │
           ┌──────▼──────┐
           │ Auto-detect │
           │   Format    │
           └──────┬──────┘
                  │
        ┌─────────▼─────────────────┐
        │  KrknResultsLoader        │
        │  - ScenarioParser         │
        │  - HealthParser           │
        │  - FitnessParser          │
        └─────────┬─────────────────┘
                  │
        ┌─────────▼─────────────────┐
        │   Canonical Schema        │
        │   ExperimentResult        │
        │   (Pydantic Models)       │
        └─────────┬─────────────────┘
                  │
    ┌─────────────┴─────────────────┐
    │        Orchestrator            │
    │  (multi-agent coordinator)    │
    └───┬───────┬────────┬──────┬───┘
        │       │        │      │
 ┌──────▼───┐ ┌▼──────┐ ┌▼────┐ ┌▼──────────┐
 │ Fitness  │ │Health │ │ SLO │ │  Anomaly  │
 │  Agent   │ │ Agent │ │Agent│ │ Detector  │
 └──────┬───┘ └───┬───┘ └──┬──┘ └─────┬─────┘
        │         │        │          │
        └─────────┴────────┴──────────┘
                  │
        ┌─────────▼─────────────────┐
        │   Root Cause Agent        │
        │   (Groq LLM)              │
        │   - Structured output     │
        │   - Evidence citations    │
        │   - Ranked remediations   │
        └─────────┬─────────────────┘
                  │
        ┌─────────▼─────────────────┐
        │   Streamlit UI            │
        │   - Dashboard             │
        │   - AI Analysis           │
        │   - Comparison            │
        │   - Reports               │
        └───────────────────────────┘
```

---

## Core Components

### 1. Data Ingestion Layer

#### KrknResultsLoader
- **Purpose**: Auto-detect and load Krkn-AI experiment artifacts
- **Capabilities**:
  - Auto-detection of file formats (JSON, CSV, YAML)
  - Graceful handling of missing files
  - Raw file path tracking for provenance

#### Parsers
- **ScenarioParser**: Parses `best_scenarios.json` and per-generation YAML files
- **HealthParser**: Parses `health_check_report.csv` with NaN handling
- **FitnessParser**: Extracts fitness scores across generations

#### Schema (Pydantic Models)
```python
ExperimentResult
├── metadata: ExperimentMetadata
├── scenarios: List[Scenario]
├── fitness: List[FitnessRecord]
├── health_events: List[HealthEvent]
├── prometheus_metrics: Optional[List[Dict]]
└── raw_files: Dict[str, str]  # Provenance tracking
```

---

### 2. Multi-Agent Analysis Layer

| Agent | Responsibility | Key Outputs |
|------|----------------|-------------|
| **FitnessAgent** | Fitness evolution, convergence, plateaus | Best/avg/worst per generation, trend detection, slope analysis |
| **HealthAgent** | Failure correlation, MTTR, cascade hints | Failure counts by service, MTTR in seconds, cascade patterns |
| **SLOAgent** | Threshold validation, severity classification | Violations list, error rate, P99 latency, pass/fail status |
| **AnomalyDetector** | ML-based outlier detection | Fitness anomalies (Isolation Forest), cascade failures, slow recovery alerts |
| **RootCauseAgent** | LLM-assisted RCA with citations | Structured hypothesis, confidence score, evidence, remediations |

#### Agent Orchestration
The `Orchestrator` class:
- Coordinates sequential execution of agents
- Passes intermediate results between agents
- Handles agent failures gracefully
- Aggregates outputs into unified analysis dict

---

### 3. Root Cause Agent (LLM)

#### Design Philosophy
- **LLM as reasoning layer, not data source**
- **Structured output enforced via JSON schema**
- **Evidence must cite actual experiment files/lines**
- **Confidence scoring based on evidence quality**

#### Architecture
```python
RootCauseAgent
├── __init__: Initialize Groq LLM client
├── build_structured_prompt: Generate JSON schema-enforced prompt
└── analyze: 
    ├── Check for scenarios & LLM availability
    ├── Build prompt with evidence
    ├── Invoke LLM with JSON response format
    ├── Parse & validate with Pydantic (StructuredRCA)
    └── Return structured output or fallback
```

#### Output Schema (Pydantic)
```python
StructuredRCA
├── hypothesis: str              # 1-2 sentence root cause
├── confidence: float (0.0-1.0)  # Evidence-based confidence
├── affected_components: List[str]
├── evidence: List[EvidenceItem]
│   ├── file: str               # Source file name
│   ├── line: Optional[str]     # Line number/section
│   └── detail: str             # What this shows
├── remediations: List[RemediationStep]
│   ├── step: str               # Action item
│   ├── impact: str             # high/medium/low
│   └── rationale: str          # Why this helps
└── missing_data: Optional[List[str]]  # Observability gaps
```

#### Fallback Behavior
When LLM unavailable or scenarios missing:
- Deterministic analysis of health events
- Generic remediation recommendations
- Clear indication of fallback mode
- Suggestions to enable full functionality

---

### 4. Analytics Layer

#### Anomaly Detection (ML)
**Isolation Forest** for fitness anomaly detection:
- Features: [generation, fitness_score]
- Contamination: 0.15 (15% expected anomalies)
- Outputs: Anomaly indices, scores, generations

**Cascade Failure Detection**:
- Time-window correlation (30-second buckets)
- Concurrent failure identification
- Service correlation matrix

**Slow Recovery Detection**:
- Failure window tracking per service
- Threshold-based alerting (default: 60s)
- Severity classification (warning/critical)

---

### 5. Visualization Layer

#### Components
- **fitness_viz.py**: Best/avg/worst evolution charts
- **heatmap.py**: Service failure correlation matrices
- **network_graph.py**: Service dependency graphs with cascade edges

#### Technologies
- **Plotly**: Interactive charts with zoom/hover
- **NetworkX**: Graph layout algorithms
- **Pandas**: Data aggregation and transformation

---

### 6. User Interface (Streamlit)

#### Page Structure
```
Main Page (app/main.py)
├── Experiment loader
├── Auto-detect format
└── Trigger analysis

Dashboard (1_📊_Dashboard.py)
├── Experiment metadata
├── Fitness evolution chart
├── Health timeline
├── Anomaly detection results
└── Service dependency graph

AI Analysis (2_🤖_AI_Analysis.py)
├── Structured RCA display
├── Evidence citations
├── Ranked remediations
├── Agent output tabs
└── Export functionality

Comparison (3_📈_Comparison.py)
├── Side-by-side metrics
├── Dual fitness evolution
├── Winner analysis
└── Detailed comparison table

Reports (4_📋_Reports.py)
└── JSON export with metadata
```

---

## Data Flow

### Analysis Workflow
```
1. User selects experiment directory
2. KrknResultsLoader auto-detects files
3. Parsers normalize to ExperimentResult
4. Orchestrator executes agents sequentially:
   a. FitnessAgent → trend analysis
   b. HealthAgent → MTTR & cascades
   c. SLOAgent → violation detection
   d. AnomalyDetector → ML outliers
   e. RootCauseAgent → LLM reasoning
5. Results stored in st.session_state
6. UI pages render analysis
7. User exports JSON report
```

---

## Error Handling

### Graceful Degradation Strategy
- **Missing files**: Skip optional components (e.g., Prometheus)
- **NaN values**: Clean with pandas `isna()` checks
- **LLM failures**: Use deterministic fallback
- **Invalid JSON**: Return error with raw response excerpt
- **Import errors**: Conditionally import optional dependencies

### Validation
- Pydantic models validate all data at parse time
- Schema mismatches caught early with clear error messages
- File existence checks before parsing

---

## Extensibility

### Adding New Agents
1. Create agent class in `src/agents/`
2. Implement `analyze(exp: ExperimentResult) -> Dict[str, Any]`
3. Register in `Orchestrator.__init__`
4. Add to orchestrator workflow

### Adding New Parsers
1. Create parser class in `src/parsers/`
2. Implement `parse(file_path: Path) -> List[Model]`
3. Register in `KrknResultsLoader.load()`

### Adding New Visualizations
1. Create viz function in `src/visualizations/`
2. Return Plotly `go.Figure`
3. Call from Streamlit page with `st.plotly_chart()`

---

## Performance Considerations

### Optimization Strategies
- **Lazy loading**: Only parse files when needed
- **Caching**: Streamlit `@st.cache_data` for expensive operations
- **Batch processing**: Group similar operations (e.g., all parsers run together)
- **Async LLM calls**: Use `langchain` async for future parallelization

### Scalability
- Current design handles experiments with:
  - 100+ scenarios
  - 10,000+ health events
  - 10+ generations
- For larger datasets, consider:
  - Sampling strategies
  - Database backend (replace in-memory)
  - Distributed processing

---

## Security Considerations

- **API Keys**: Stored in `.env`, never committed to git
- **Input validation**: All user inputs validated via Pydantic
- **File path sanitization**: Pathlib prevents directory traversal
- **LLM prompt injection**: Structured JSON output limits injection vectors

---

## Testing Strategy

### Current Coverage
- Synthetic data for unit testing
- Manual testing with real Krkn-AI outputs
- Schema validation via Pydantic

### Future Testing
- Unit tests for each agent
- Integration tests for full workflow
- Property-based testing for parsers
- LLM output validation tests

---

## Deployment

### Local Development
```bash
streamlit run app/main.py
```

### Production Deployment
```bash
# Using Streamlit Cloud
streamlit run app/main.py --server.port 8501

# Using Docker
docker build -t krkn-analyzer .
docker run -p 8501:8501 krkn-analyzer
```

---

## Future Architecture Enhancements

### Planned Improvements
1. **LangGraph Integration**: Replace Orchestrator with LangGraph for:
   - Conditional agent execution
   - Parallel agent execution
   - Agent communication protocols

2. **RAG Enhancement**: Extend ChromaDB usage for:
   - Historical experiment search
   - Pattern recognition across experiments
   - Auto-remediation suggestions

3. **Real-time Analysis**: Stream processing for:
   - Live experiment monitoring
   - Progressive analysis updates
   - Alert generation

4. **Plugin System**:
   - Custom agent registration
   - Third-party visualization plugins
   - External integrations (Slack, PagerDuty)

---

## Non-Goals

- Executing chaos experiments (use Krkn-AI)
- Modifying Krkn-AI core logic
- Replacing observability platforms (Prometheus, Grafana)
- General-purpose chaos engineering framework

---

## Summary

Krkn-AI Analyzer acts as the **analysis and reasoning layer** for Krkn-AI,
bridging the gap between raw chaos output and actionable resilience insight.

The architecture prioritizes:
- **Explainability**: Every insight traceable to source data
- **Modularity**: Agents operate independently
- **Extensibility**: Easy to add new capabilities
- **Robustness**: Graceful handling of missing data/services
- **Production-readiness**: Clear error handling, validation, security

This design enables rapid iteration while maintaining a path to production deployment and CNCF-quality standards.
