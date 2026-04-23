Digital Timeline Fusion – Backend Prototype

This repository implements the backend reconstruction engine for a multi-device digital timeline fusion system.
The objective is to ingest heterogeneous device logs (e.g., camera, phone, laptop), normalise timestamps, detect and correct inter-device clock skew, and reconstruct a unified chronological timeline enriched with provenance and confidence metadata.
This implementation prioritises deterministic processing, reproducibility, and forensic-style traceability, rather than user interface development.

##################################################################################################################################################################

System Workflow

The reconstruction pipeline executes in clearly separated stages:
1. Log Parsing
Device-specific CSV logs are parsed into structured RawEvent objects with SHA-256 provenance hashing.
2. Canonical Event Construction
Events are transformed into a unified internal representation.
3. Timestamp Normalisation
Heterogeneous timestamps are converted to ISO 8601 UTC format with structured validation.
4. Clock Skew Detection
Overlapping events are analysed to estimate inter-device temporal offsets.
5. Median-Based Skew Correction
Robust median-based correction is applied to align device timelines.
6. Event Fusion & Clustering
Corrected events are merged into a unified chronological timeline and grouped into clusters.
7. Composite Confidence Scoring
Events are assigned confidence values based on temporal consistency, skew reliability, and cluster completeness.
8. Experimental Evaluation Framework
Reconstruction robustness is evaluated under controlled noise and skew scenarios.

##################################################################################################################################################################

Core Features

-Parsing of IoT-style CSV event logs
-Deterministic timestamp normalisation to UTC
-Structured handling of malformed and missing timestamps (events retained and flagged)
-Overlap-based inter-device skew detection
-Robust median-based skew estimation
-Temporal alignment and correction
-Chronological event fusion
-Sliding-window clustering
-Composite confidence modelling with exponential penalisation
-Provenance tracking (source file, row index, SHA-256 hash)
-Multi-scenario synthetic noise evaluation (low, medium, high distortion)
-Confidence vs reconstruction error correlation analysis

##################################################################################################################################################################

Evaluation Metrics

Reconstruction performance is evaluated using:
-Mean Absolute Error (MAE) before and after skew correction
-Chronological ordering accuracy
-Device-level ordering stability
-Confidence-based reliability correlation
-Multi-scenario statistical comparison

The evaluation framework enables controlled robustness testing under increasing temporal distortion.

##################################################################################################################################################################

Repository Structure
parsers/      # Log ingestion and parsing modules
pipeline/     # Deterministic reconstruction logic
scripts/      # Execution and experimentation entry points
tests/        # Unit tests for modular validation
data/         # Synthetic and test datasets
output/       # Generated evaluation results

This modular separation enforces isolation of concerns and supports maintainability.

##################################################################################################################################################################

Setup & Execution

Requirements
-Python 3.10+
-pip

Install dependencies:
pip install -r requirements.txt

Run full experimental evaluation:
python -m scripts.run_experiments

Run full pipeline on default dataset:
python -m scripts.run_pipeline

Execute unit tests:

pytest
Reproducibility

The system is fully deterministic.
Given identical input logs and configuration, the pipeline produces identical outputs across executions.

Synthetic datasets are included to allow controlled replication of experimental scenarios.
