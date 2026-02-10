# Krkn-AI Analyzer  
**Interactive Analysis, Visualization, and Root Cause Analysis for Chaos Experiments**

Krkn-AI Analyzer is a web-based analysis and visualization layer built on top of **Krkn-AI** chaos experiment outputs.  
It transforms raw experiment artifacts (JSON, CSV, YAML) into actionable insights using deterministic analysis, interactive visualizations, and optional LLM-powered Root Cause Analysis (RCA).

---

## Motivation

Krkn-AI produces rich experiment outputs such as:
- fitness scores across generations,
- health check results,
- SLO violations,
- chaos scenario configurations.

However, these artifacts are often difficult to interpret, compare, and reason about quickly.

This project addresses that gap by:
- normalizing Krkn-AI outputs,
- correlating failures across services,
- highlighting impactful chaos scenarios,
- generating human-readable and machine-parseable RCA reports.

---

## Key Features

- **Deterministic Analysis**
  - Fitness evolution across generations with trend detection
  - Best / worst scenario identification
  - SLO validation and violation detection
  - Health check correlation and cascade failure detection
  - MTTR (Mean Time To Recovery) estimation
  - ML-powered anomaly detection using Isolation Forest

- **Interactive Visualization**
  - Fitness evolution charts with best/avg/worst tracking
  - Health failure summaries and timeline analysis
  - Service dependency network graphs
  - Failure correlation heatmaps
  - Side-by-side experiment comparison
  - Exportable JSON reports

- **LLM-Powered Root Cause Analysis (Optional)**
  - Uses Groq (Llama 3.3 70B) for fast inference
  - Produces structured RCA with evidence citations and remediation steps
  - JSON schema validation with Pydantic
  - Graceful fallback when LLM is unavailable
  - Confidence scoring and missing data identification

- **Advanced Analytics**
  - Cascade failure detection with temporal correlation
  - Slow recovery detection and alerting
  - Service dependency graph visualization
  - Multi-generation fitness trend analysis

---

## Architecture Overview

```
Krkn-AI Outputs
├── best_scenarios.json
├── health_check_report.csv
├── scenario YAMLs
└── Prometheus metrics
          ↓
   Parsers & Loaders
   (ScenarioParser, HealthParser, FitnessParser)
          ↓
    Analysis Agents
┌─────────┴─────────┐
│  FitnessAgent     │ → Trend detection, convergence
│  HealthAgent      │ → MTTR, cascade hints
│  SLOAgent         │ → Threshold violations
│  AnomalyDetector  │ → ML-based outlier detection
└─────────┬─────────┘
          ↓
 Root Cause Agent (Groq LLM)
 - Structured JSON output
 - Evidence citations
 - Ranked remediations
          ↓
Streamlit UI + Exportable Reports
```

---

## Project Structure

```
krkn-ai-analyzer/
├── app/
│   ├── main.py                      # Entry point
│   └── pages/
│       ├── 1_📊_Dashboard.py        # Overview & metrics
│       ├── 2_🤖_AI_Analysis.py      # LLM-powered RCA
│       ├── 3_📈_Comparison.py       # Multi-experiment comparison
│       └── 4_📋_Reports.py          # JSON export
├── src/
│   ├── agents/
│   │   ├── fitness_agent.py         # Fitness evolution analysis
│   │   ├── health_agent.py          # Health correlation & MTTR
│   │   ├── slo_agent.py             # SLO validation
│   │   └── root_cause_agent.py      # LLM-powered RCA
│   ├── analytics/
│   │   └── anomaly_detection.py     # ML anomaly detection
│   ├── loaders/
│   │   └── krkn_loader.py           # Auto-detect experiment format
│   ├── parsers/
│   │   ├── scenario_parser.py       # Parse best_scenarios.json
│   │   ├── health_parser.py         # Parse health_check_report.csv
│   │   └── fitness_parser.py        # Parse fitness data
│   ├── visualizations/
│   │   ├── fitness_viz.py           # Fitness charts
│   │   ├── heatmap.py               # Correlation heatmaps
│   │   └── network_graph.py         # Service dependency graphs
│   ├── orchestrator.py              # Multi-agent coordinator
│   ├── schema.py                    # Pydantic data models
│   └── vector_store.py              # ChromaDB for experiment memory
├── data/
│   └── synthetic/
│       └── experiment_1/            # Synthetic test data
├── docs/
│   └── ARCHITECTURE.md              # Detailed architecture doc
├── requirements.txt
├── .env.example
└── README.md
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- pip
- Git

### Setup

```bash
git clone https://github.com/<your-username>/krkn-ai-analyzer.git
cd krkn-ai-analyzer

python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### Optional: Enable LLM-Based RCA

Create a `.env` file:

```
GROQ_API_KEY=your_api_key_here
```

Get your free API key at: https://console.groq.com/keys

If not set, the analyzer will use deterministic fallback logic with basic recommendations.

---

## Running the Application

```bash
streamlit run app/main.py
```

The app will open in your browser at `http://localhost:8501`

In the UI:

* Enter experiment path:
  ```
  data/synthetic/experiment_1
  ```
* Click **Load & Analyze**
* Navigate through the sidebar pages:
  - 📊 Dashboard: Overview metrics and visualizations
  - 🤖 AI Analysis: LLM-powered root cause analysis
  - 📈 Comparison: Compare multiple experiments
  - 📋 Reports: Export JSON reports

---

## Input Data Format

Expected experiment folder structure:

```
experiment_x/
├── best_scenarios.json          # Fitness scores per generation
├── health_check_report.csv      # Health check results
├── config.yaml                  # (Optional) Experiment metadata
├── prometheus_metrics.json      # (Optional) Prometheus data
└── yaml/
    └── generation_0/
        └── scenario_0_0.yaml    # Scenario configurations
```

### Sample Data Files

**best_scenarios.json:**
```json
{
  "generation_0": [
    {
      "scenario_id": "scenario_0_0",
      "fitness_score": 0.82,
      "scenario_type": "pod_delete",
      "config": {"kill_count": 1}
    }
  ]
}
```

**health_check_report.csv:**
```csv
timestamp,service,url,status_code,latency_ms,healthy,error
2024-01-01T10:00:00Z,cart,http://cart:8080/health,200,45,true,
2024-01-01T10:00:30Z,checkout,http://checkout:8080/health,503,120,false,Connection timeout
```

---

## Root Cause Analysis (LLM)

When enabled with `GROQ_API_KEY`, the Root Cause Agent:

* Analyzes worst-performing scenarios
* Correlates health failures and SLO violations
* Returns **structured JSON output** including:
  * **hypothesis**: Root cause summary with confidence score
  * **affected_components**: List of impacted services
  * **evidence**: File/line citations from experiment data
  * **remediations**: Ranked action items (high/medium/low impact)
  * **missing_data**: Observability gaps identified

### Example RCA Output

```json
{
  "hypothesis": "Cart service cascading failure due to insufficient memory under load",
  "confidence": 0.85,
  "affected_components": ["cart", "checkout"],
  "evidence": [
    {
      "file": "best_scenarios.json",
      "line": "generation_1.scenario_1_0",
      "detail": "Fitness dropped 48% when kill_count increased to 2"
    }
  ],
  "remediations": [
    {
      "step": "Implement circuit breaker between cart and checkout",
      "impact": "high",
      "rationale": "Prevents cascade failures when cart is degraded"
    }
  ]
}
```

The LLM is used **only for explanation**, not for metric computation.

---

## Advanced Features

### ML-Powered Anomaly Detection

- **Fitness Anomalies**: Isolation Forest detects unusual fitness drops
- **Cascade Failures**: Temporal correlation analysis identifies services that fail together
- **Slow Recovery Detection**: Alerts on services with MTTR > threshold

### Service Dependency Graphs

Interactive network visualization showing:
- Service failure relationships
- Cascade patterns
- Node sizing based on failure counts

### Multi-Experiment Comparison

Side-by-side analysis including:
- Fitness evolution comparison
- Failure count deltas
- SLO status comparison
- Winner analysis across metrics

---

## Testing & Validation

* Synthetic experiment data included in `data/synthetic/experiment_1/` for immediate testing
* Designed to work with real Krkn-AI outputs without modification
* Clear separation between parsing, analysis, and presentation layers
* Graceful handling of missing data (partial experiments)

---

## Design Principles

* **Deterministic-first analysis**: Core metrics computed without AI
* **LLM as optional reasoning layer**: Adds context, not critical path
* **Explicit data provenance**: All insights cite source files/lines
* **Graceful degradation**: Works with partial data, missing API keys
* **Production-oriented structure**: Modular agents, extensible parsers

---

## Troubleshooting

### Common Issues

**"No module named 'src'"**
- Ensure you're running from project root: `streamlit run app/main.py`
- Check that virtual environment is activated

**"GROQ_API_KEY not found"**
- Create `.env` file with your API key
- Or run without LLM (deterministic fallback will be used)

**"Experiment path not found"**
- Verify the path exists: `ls data/synthetic/experiment_1`
- Check file permissions

**Pydantic validation errors**
- Ensure CSV/JSON files match expected schema
- Check for NaN values in numeric fields

---

## Future Improvements

* Typed Pydantic schemas for all LLM outputs ✅ (Implemented)
* Dependency graph visualization ✅ (Implemented)
* PDF report export
* CI/CD pipeline with GitHub Actions
* Docker support
* Deeper Prometheus metric correlation
* Real-time streaming analysis
* LangGraph orchestration
* Plugin system for custom agents

---

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

---

## License

Apache License 2.0

---

## Acknowledgements

* Built to complement **Krkn-AI** chaos experiments
* LLM inference powered by **Groq** (Llama 3.3 70B)
* Visualization built with **Plotly** and **Streamlit**
* ML anomaly detection using **scikit-learn**

---

## Contact

For questions or support:
- Open an issue on GitHub
- Reach out via CNCF Slack

---

**Ready to analyze chaos experiments? Run `streamlit run app/main.py` and get started!** 🚀