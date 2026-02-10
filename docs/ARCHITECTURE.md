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
   `ExperimentResult` contract.

2. **Separation of concerns**  
   - Krkn-AI → experiment execution  
   - This project → analysis, insight, visualization

3. **Explainability over black-box AI**  
   LLM output is always grounded in numeric evidence and file-level citations.

4. **Incremental adoption**  
   Works with partial data (e.g., no health checks, no Prometheus metrics).

---

## High-Level Architecture

        ┌───────────────────┐
        │  Krkn-AI Results   │
        │ (JSON / CSV / YAML)│
        └─────────┬─────────┘
                  │
           KrknResultsLoader
                  │
        ┌─────────▼─────────┐
        │ Canonical Schema  │
        │ ExperimentResult  │
        └─────────┬─────────┘
                  │
    ┌─────────────┴─────────────┐
    │        Orchestrator        │
    │ (multi-agent coordinator) │
    └───────┬───────┬───────────┘
            │       │
 ┌──────────▼───┐ ┌─▼────────────┐
 │ FitnessAgent │ │ HealthAgent  │
 └──────────┬───┘ └───────┬──────┘
            │               │
     ┌──────▼─────┐   ┌─────▼──────┐
     │ SLO Agent  │   │ RootCause  │
     └────────────┘   │   Agent    │
                        (GROQ LLM)
                           │
                           ▼
                Evidence-backed insights

---

## Core Components

### 1. Loaders & Parsers
- Auto-detect Krkn-AI result structure
- Parse:
  - `best_scenarios.json`
  - `health_check_report.csv`
  - scenario YAMLs
  - Prometheus metric dumps
- Normalize everything into `ExperimentResult`

---

### 2. Multi-Agent Analysis

| Agent | Responsibility |
|------|----------------|
| FitnessAgent | Fitness evolution, convergence, plateaus |
| HealthAgent | Failure correlation, MTTR, cascade hints |
| SLOAgent | Threshold validation, severity classification |
| RootCauseAgent | LLM-assisted RCA with citations |

Agents operate independently and are orchestrated conditionally.

---

### 3. RAG / Historical Memory

Past experiments are embedded and stored in ChromaDB:
- Enables semantic comparison
- Detects recurring failure patterns
- Provides historical context to RCA

---

### 4. Visualization Layer

- Fitness evolution charts
- Failure correlation heatmaps
- Dependency network graphs
- Side-by-side experiment comparison
- Exportable reports

---

## Data Strategy

During development:
- Schema-accurate synthetic data is used for fast iteration.

For validation:
- Analyzer is tested against real Krkn-AI runs executed on a local cluster.

This ensures correctness without slowing development.

---

## Non-Goals

- Executing chaos experiments
- Modifying Krkn-AI core logic
- Replacing observability platforms

---

## Future Extensions

- Native LangGraph orchestration
- PDF / Markdown report export
- Prometheus live query integration
- UI plugin for Krkn dashboard

---

## Summary

This project acts as the **analysis and reasoning layer** for Krkn-AI,
bridging the gap between raw chaos output and actionable resilience insight.
