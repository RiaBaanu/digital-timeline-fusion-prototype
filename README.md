Digital Timeline Fusion – Backend Prototype
-------------------------------------------

This repository implements the backend reconstruction engine for a multi-device digital timeline fusion system.
The objective is to ingest heterogeneous device logs (e.g., camera, phone, laptop), normalise timestamps, detect and correct inter-device clock skew, and reconstruct a unified chronological timeline enriched with provenance and confidence metadata.
This implementation prioritises deterministic processing, reproducibility, and forensic-style traceability, rather than user interface development.

-------------------------------------------

**System Workflow**

The reconstruction pipeline executes in clearly separated stages:
1. Log Parsing</br>
Device-specific CSV logs are parsed into structured RawEvent objects with SHA-256 provenance hashing.
2. Canonical Event Construction</br>
Events are transformed into a unified internal representation.
3. Timestamp Normalisation</br>
Heterogeneous timestamps are converted to ISO 8601 UTC format with structured validation.
4. Clock Skew Detection</br>
Overlapping events are analysed to estimate inter-device temporal offsets.
5. Median-Based Skew Correction</br>
Robust median-based correction is applied to align device timelines.
6. Event Fusion & Clustering</br>
Corrected events are merged into a unified chronological timeline and grouped into clusters.
7. Composite Confidence Scoring</br>
Events are assigned confidence values based on temporal consistency, skew reliability, and cluster completeness.
8. Experimental Evaluation Framework</br>
Reconstruction robustness is evaluated under controlled noise and skew scenarios.

-------------------------------------------

**Core Features**

* Parsing of IoT-style CSV event logs</br>
* Deterministic timestamp normalisation to UTC</br>
* Structured handling of malformed and missing timestamps (events retained and flagged)</br>
* Overlap-based inter-device skew detection</br>
* Robust median-based skew estimation</br>
* Temporal alignment and correction</br>
* Chronological event fusion</br>
* Sliding-window clustering</br>
* Composite confidence modelling with exponential penalisation</br>
* Provenance tracking (source file, row index, SHA-256 hash)</br>
* Multi-scenario synthetic noise evaluation (low, medium, high distortion)</br>
* Confidence vs reconstruction error correlation analysis</br>

-------------------------------------------

**Evaluation Metrics**

Reconstruction performance is evaluated using:</br>
* Mean Absolute Error (MAE) before and after skew correction</br>
* Chronological ordering accuracy</br>
* -Device-level ordering stability</br>
* Confidence-based reliability correlation</br>
* Multi-scenario statistical comparison</br>

The evaluation framework enables controlled robustness testing under increasing temporal distortion.

-------------------------------------------

**Repository Structure**

* parsers/      # Log ingestion and parsing modules</br>
* pipeline/     # Deterministic reconstruction logic</br>
* scripts/      # Execution and experimentation entry points</br>
* tests/        # Unit tests for modular validation</br>
* data/         # Synthetic and test datasets</br>
* output/       # Generated evaluation results</br>

This modular separation enforces isolation of concerns and supports maintainability.

-------------------------------------------

**Setup & Execution**

Requirements</br>
* Python 3.10+</br>
* pip</br>

Install dependencies:</br>
<i>pip install -r requirements.txt</i></br>

Run full experimental evaluation:</br>
<i>python -m scripts.run_experiments</i></br>

Run full pipeline on default dataset:</br>
<i>python -m scripts.run_pipeline</i></br>

Execute unit tests:</br>
<i>pytest</i>

-------------------------------------------

**Reproducibility**

The system is fully deterministic.</br>
Given identical input logs and configuration, the pipeline produces identical outputs across executions.</br>
Synthetic datasets are included to allow controlled replication of experimental scenarios.
