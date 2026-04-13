# Digital Timeline Fusion – Backend Prototype

This project implements the backend logic for a **multi-device digital timeline fusion system**.

The goal is to ingest events from multiple heterogeneous devices (e.g., camera, phone, laptop), 
normalise timestamps, detect and correct clock skew, and produce a single fused chronological 
timeline with provenance and confidence information.

This repository focuses on **correctness, reproducibility, and forensic-style integrity** 
rather than UI development.

---

## System Workflow

The pipeline operates in the following stages:

1. **Log Parsing** – Device-specific CSV logs are parsed into structured records.
2. **Canonical Event Construction** – Events are normalized into a unified format.
3. **Clock Skew Detection** – Overlapping events are used to estimate inter-device skew.
4. **Skew Correction** – Median-based correction is applied to align device timelines.
5. **Event Fusion** – Corrected events are merged into a unified chronological sequence.
6. **Clustering & Confidence Scoring** – Events are grouped and assigned a composite confidence score.
7. **Evaluation Framework** – Reconstruction accuracy is measured under multiple noise scenarios.

---

## Current Features

- Parsing of IoT-style CSV event logs
- Timestamp normalisation to UTC
- Handling of missing and malformed timestamps (events retained and flagged)
- Detection of overlapping events across devices
- Median-based clock skew estimation
- Clock skew correction
- Fusion of events into a single chronological timeline
- Event clustering and composite confidence scoring
- Provenance tracking (source file, row number, SHA-256 hash)
- Multi-scenario experimental evaluation (low, medium, high noise)
- Statistical reporting (mean and standard deviation across scenarios)
- Confidence vs reconstruction error correlation analysis
- Synthetic data support for controlled testing

---

## Evaluation Metrics

The system evaluates reconstruction performance using:

- Mean Absolute Error (MAE) before and after skew correction
- Chronological ordering accuracy
- Confidence-based tie-breaking accuracy
- Device-level ordering accuracy
- Statistical summary across multiple experimental scenarios
- Correlation between confidence scores and reconstruction error

---

## Running Experiments

To execute the experimental evaluation pipeline:

```bash
python -m scripts.run_experiments
