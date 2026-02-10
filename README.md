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
  - Fitness evolution across generations
  - Best / worst scenario identification
  - SLO validation and violation detection
  - Health check correlation and cascade detection
  - MTTR estimation

- **Interactive Visualization**
  - Fitness evolution charts
  - Health failure summaries
  - Side-by-side experiment comparison
  - Exportable JSON reports

- **LLM-Powered Root Cause Analysis (Optional)**
  - Uses Groq for fast inference
  - Produces structured RCA with evidence and remediation steps
  - Graceful fallback when LLM is unavailable

- **RAG-Ready Architecture**
  - Experiment memory via ChromaDB
  - Enables historical comparison and semantic search (extensible)

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
          ↓
    Analysis Agents
(Fitness | Health | SLO | Anomaly)
          ↓
 Root Cause Agent (Groq, optional)
          ↓
Streamlit UI + Exportable Reports
```

---

## Project Structure

```
krkn-ai-analyzer/
├── app/
│   ├── main.py
│   └── pages/
│       ├── 1_📊_Dashboard.py
│       ├── 2_🤖_AI_Analysis.py
│       ├── 3_📈_Comparison.py
│       └── 4_📋_Reports.py
├── src/
│   ├── agents/
│   ├── analytics/
│   ├── loaders/
│   ├── parsers/
│   ├── visualizations/
│   └── orchestrator.py
├── data/
│   └── synthetic/
│       └── experiment_1/
├── requirements.txt
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
source .venv/bin/activate

pip install -r requirements.txt
```

### Optional: Enable LLM-Based RCA

Create a `.env` file:

```
GROQ_API_KEY=your_api_key_here
```

If not set, the analyzer will still work using deterministic fallback logic.

---

## Running the Application

```bash
streamlit run app/main.py
```

In the UI:

* Enter experiment path:
  ```
  data/synthetic/experiment_1
  ```
* Click **Load & Analyze**

---

## Input Data Format

Expected experiment folder structure:

```
experiment_x/
├── best_scenarios.json
├── health_check_report.csv
├── config.yaml
├── prometheus_metrics.json
└── yaml/
    └── generation_0/
        └── scenario_0_0.yaml
```

---

## Root Cause Analysis (LLM)

When enabled, the Root Cause Agent:

* consumes worst-performing scenario metadata,
* correlates health failures and SLO violations,
* returns **structured JSON output** including:
  * root cause summary,
  * impacted components,
  * evidence,
  * ranked remediation steps,
  * missing observability signals.

The LLM is used **only for explanation**, not for metric computation.

---

## Testing & Validation

* Synthetic experiment data included for immediate testing
* Designed to work with real Krkn-AI outputs without modification
* Clear separation between parsing, analysis, and presentation layers

---

## Design Principles

* Deterministic-first analysis
* LLM as an optional reasoning layer
* Explicit data provenance
* Graceful degradation
* Production-oriented structure

---

## Future Improvements

* Typed Pydantic schemas for all LLM outputs
* Dependency graph visualization
* PDF report export
* CI pipeline and Docker support
* Deeper Prometheus metric correlation

---

## License

Apache License 2.0

---

## Acknowledgements

* Built to complement **Krkn-AI** chaos experiments
* LLM inference powered by **Groq**