# Digital Timeline Fusion – Backend Prototype

This project implements the backend logic for a **multi-device digital timeline fusion system**.
The goal is to ingest events from different sources, normalise timestamps, detect clock skew,
and produce a single fused chronological timeline with provenance and confidence information.

This repository focuses on **correctness, reproducibility, and forensic-style integrity**
rather than UI development.

---

## Current Features

- Parsing of IoT-style CSV event logs
- Timestamp normalisation to UTC
- Handling of missing and malformed timestamps (events are retained and flagged)
- Detection of overlapping events across devices
- Median-based clock skew estimation
- Clock skew correction
- Fusion of events into a single chronological timeline
- Provenance tracking (source file, row number, SHA-256 hash)
- Basic evaluation metrics (timestamp MAE and ordering accuracy)
- Synthetic data support for controlled testing

---

## Project Structure

data/
db/
parsers/        # Data source parsers (IoT, extensible)
pipeline/       # Core fusion pipeline logic
scripts/
tests/
