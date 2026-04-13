"""
Digital Timeline Fusion – Experimental Evaluation
-------------------------------------------------
Evaluates robustness of the fusion system under
varying noise and skew conditions.
"""

import os
import uuid
import random
from copy import deepcopy
from datetime import datetime, timedelta
from collections import defaultdict

import matplotlib.pyplot as plt

from parsers.iot_parser import IoTCSVParser
from pipeline.event_builder import build_canonical_event
from pipeline.skew_detector import (
    detect_overlapping_events,
    calculate_median_skew,
    apply_clock_skew
)
from pipeline.event_clustering import cluster_events
from pipeline.confidence_model import compute_cluster_confidence
from pipeline.fusion_engine import fuse_events
from pipeline.evaluation import (
    compute_timestamp_mae,
    compute_weighted_ordering_accuracy
)

random.seed(42)


# =========================================================
# Synthetic Skew Injection
# =========================================================

def inject_skew(events, phone_skew=0, laptop_skew=0, noise_level=0):

    for e in events:
        if not e.ground_truth_timestamp:
            continue

        base = datetime.fromisoformat(e.ground_truth_timestamp)

        if e.device_id == "Phone01":
            skew = phone_skew

        elif e.device_id == "Laptop01":
            skew = laptop_skew

        elif e.device_id == "Laptop02":
            try:
                num = int(e.event_type.split("_")[1])
            except:
                num = 1
            skew = laptop_skew + (num ** 2) * 3

        else:
            skew = 0

        noise = random.uniform(-noise_level, noise_level)

        # Simulate skewed device timestamp
        e.corrected_timestamp = (
            base + timedelta(seconds=skew + noise)
        ).isoformat()

    return events


# =========================================================
# Residual Skew
# =========================================================

def compute_residual_skew(events):

    errors = defaultdict(list)

    for e in events:
        if not e.ground_truth_timestamp or not e.corrected_timestamp:
            continue

        gt = datetime.fromisoformat(e.ground_truth_timestamp)
        ct = datetime.fromisoformat(e.corrected_timestamp)

        errors[e.device_id].append((ct - gt).total_seconds())

    return {
        d: round(sum(v) / len(v), 2)
        for d, v in errors.items()
        if v
    }


# =========================================================
# Single Scenario Execution
# =========================================================

def run_scenario(phone_skew, laptop_skew, noise):

    parsers = [
        IoTCSVParser("data/synthetic/iot_camera01.csv"),
        IoTCSVParser("data/synthetic/iot_phone01_skewed.csv"),
        IoTCSVParser("data/synthetic/iot_laptop01_skewed.csv"),
        IoTCSVParser("data/synthetic/iot_laptop02_skewed.csv"),
    ]

    raw = []
    for p in parsers:
        raw.extend(p.parse())

    events = [build_canonical_event(r) for r in raw]

    events = inject_skew(deepcopy(events), phone_skew, laptop_skew, noise)

    overlaps = detect_overlapping_events(events, reference_device="Camera01")
    skew = calculate_median_skew(overlaps, reference_device="Camera01")
    corrected = apply_clock_skew(events, skew, reference_device="Camera01")

    fused = fuse_events(corrected, confidence_weighted=True)

    residuals = compute_residual_skew(fused)

    clusters = cluster_events(fused, window_seconds=5)
    total_devices = len(set(e.device_id for e in fused))

    for cluster in clusters:
        confidence = compute_cluster_confidence(cluster, residuals, total_devices)
        cid = str(uuid.uuid4())

        for e in cluster:
            e.confidence_score = confidence
            e.cluster_id = cid

    mae_after = compute_timestamp_mae(fused)
    ordering = compute_weighted_ordering_accuracy(fused)

    return fused, mae_after, ordering


# =========================================================
# Main Experiment
# =========================================================

def main():

    scenarios = [
        ("Low", 60, 90, 5),
        ("Medium", 60, 90, 15),
        ("High", 60, 90, 30),
    ]

    os.makedirs("output", exist_ok=True)

    print("\nScenario     Noise   MAE_After   Ordering")
    print("---------------------------------------------------")

    results = []

    for name, ps, ls, noise in scenarios:

        fused, mae_a, ordering = run_scenario(ps, ls, noise)

        mae_display = f"{mae_a:.2f}" if mae_a is not None else "N/A"
        ordering_display = f"{ordering:.4f}" if ordering is not None else "N/A"

        print(f"{name:<12}{noise:<8}{mae_display:<12}{ordering_display}")

        results.append((noise, mae_a or 0, ordering or 0))

    # =====================================================
    # Plot: MAE vs Noise
    # =====================================================

    noise_levels = [r[0] for r in results]
    mae_values = [r[1] for r in results]
    ordering_values = [r[2] for r in results]

    plt.figure()
    plt.plot(noise_levels, mae_values, marker="o")
    plt.xlabel("Noise Level")
    plt.ylabel("MAE After Correction (sec)")
    plt.title("MAE vs Noise")
    plt.grid(True)
    plt.savefig("output/mae_vs_noise.png")
    plt.close()

    # =====================================================
    # Plot: Ordering vs Noise
    # =====================================================

    plt.figure()
    plt.plot(noise_levels, ordering_values, marker="o")
    plt.xlabel("Noise Level")
    plt.ylabel("Weighted Ordering Accuracy")
    plt.title("Ordering Accuracy vs Noise")
    plt.grid(True)
    plt.savefig("output/ordering_vs_noise.png")
    plt.close()

    print("\nExperiment completed successfully.\n")


if __name__ == "__main__":
    main()
