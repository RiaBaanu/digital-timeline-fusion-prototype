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

from colorama import Fore, Style, init
init(autoreset=True)

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
    compute_ordering_accuracy
)

random.seed(42)


# =========================================================
# Synthetic Skew Injection
# =========================================================

def inject_skew(events, phone_skew=0, laptop_skew=0, noise_level=0):

    for e in events:
        if not e.ground_truth_timestamp:
            continue

        try:
            base = datetime.fromisoformat(e.ground_truth_timestamp)
        except:
            continue

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

        try:
            gt = datetime.fromisoformat(e.ground_truth_timestamp)
            ct = datetime.fromisoformat(str(e.corrected_timestamp))
        except:
            continue

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

    fused = fuse_events(corrected)

    residuals = compute_residual_skew(fused)

    clusters = cluster_events(fused, window_seconds=5)
    total_devices = len(set(e.device_id for e in fused))

    confidence_error_pairs = []

    for cluster in clusters:
        confidence = compute_cluster_confidence(cluster, residuals, total_devices)
        cid = str(uuid.uuid4())

        for e in cluster:
            e.confidence_score = confidence
            e.cluster_id = cid

            if e.ground_truth_timestamp and e.corrected_timestamp:
                try:
                    gt = datetime.fromisoformat(e.ground_truth_timestamp)
                    ct = datetime.fromisoformat(str(e.corrected_timestamp))
                    error = abs((ct - gt).total_seconds())
                    confidence_error_pairs.append((confidence, error))
                except:
                    pass

    mae_after = compute_timestamp_mae(fused)
    ordering = compute_ordering_accuracy(fused)

    return fused, mae_after, ordering, confidence_error_pairs


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

    print("\nScenario              Noise             MAE_After                Ordering")
    print("--------------------------------------------------------------------------------")

    results = []
    all_conf_err = []
    device_confidence = defaultdict(list)

    for name, ps, ls, noise in scenarios:

        fused, mae_a, ordering, conf_err = run_scenario(ps, ls, noise)

        all_conf_err.extend(conf_err)

        for e in fused:
            if e.confidence_score is not None:
                device_confidence[e.device_id].append(e.confidence_score)

        # ---- Colour MAE ----
        if mae_a is None:
            mae_display = "N/A"
        elif mae_a < 30:
            mae_display = Fore.GREEN + f"{mae_a:.2f}" + Style.RESET_ALL
        elif mae_a < 40:
            mae_display = Fore.YELLOW + f"{mae_a:.2f}" + Style.RESET_ALL
        else:
            mae_display = Fore.RED + f"{mae_a:.2f}" + Style.RESET_ALL

        # ---- Colour Ordering ----
        if ordering is None:
            ordering_display = "N/A"
        elif ordering >= 0.95:
            ordering_display = Fore.GREEN + f"{ordering:.4f}" + Style.RESET_ALL
        elif ordering >= 0.8:
            ordering_display = Fore.YELLOW + f"{ordering:.4f}" + Style.RESET_ALL
        else:
            ordering_display = Fore.RED + f"{ordering:.4f}" + Style.RESET_ALL

        print(f"{name:<12} {noise:<6} {mae_display:<12} {ordering_display}")

        results.append((noise, mae_a or 0, ordering or 0))

    noise_levels = [r[0] for r in results]
    mae_values = [r[1] for r in results]
    ordering_values = [r[2] for r in results]

    # =====================================================
    # MAE vs Noise
    # =====================================================

    mae_colors = ["green" if m < 30 else "orange" if m < 40 else "red" for m in mae_values]

    plt.figure()
    plt.scatter(noise_levels, mae_values, c=mae_colors, s=120)
    plt.plot(noise_levels, mae_values, linestyle="--", alpha=0.5)
    plt.xlabel("Noise Level")
    plt.ylabel("MAE After Correction (sec)")
    plt.title("MAE vs Noise (Performance Categorised)")
    plt.grid(True)
    plt.savefig("output/mae_vs_noise_colored.png")
    plt.close()

    # =====================================================
    # Ordering vs Noise
    # =====================================================

    ordering_colors = ["green" if a >= 0.95 else "orange" if a >= 0.8 else "red" for a in ordering_values]

    plt.figure()
    plt.scatter(noise_levels, ordering_values, c=ordering_colors, s=120)
    plt.plot(noise_levels, ordering_values, linestyle="--", alpha=0.5)
    plt.xlabel("Noise Level")
    plt.ylabel("Ordering Accuracy")
    plt.title("Ordering Accuracy vs Noise (Categorised)")
    plt.grid(True)
    plt.savefig("output/ordering_vs_noise_colored.png")
    plt.close()

    # =====================================================
    # Confidence vs Error
    # =====================================================

    if all_conf_err:
        conf_vals = [c for c, e in all_conf_err]
        err_vals = [e for c, e in all_conf_err]

        plt.figure()
        plt.scatter(conf_vals, err_vals, alpha=0.6)
        plt.xlabel("Confidence Score")
        plt.ylabel("Absolute Reconstruction Error (sec)")
        plt.title("Confidence vs Reconstruction Error")
        plt.grid(True)
        plt.savefig("output/confidence_vs_error.png")
        plt.close()

    # =====================================================
    # Average Confidence per Device
    # =====================================================

    avg_conf = {
        device: sum(vals) / len(vals)
        for device, vals in device_confidence.items()
        if vals
    }

    devices = list(avg_conf.keys())
    conf_values = list(avg_conf.values())

    colors = ["green" if v >= 0.8 else "orange" if v >= 0.6 else "red" for v in conf_values]

    plt.figure()
    plt.bar(devices, conf_values, color=colors)
    plt.xlabel("Device")
    plt.ylabel("Average Confidence Score")
    plt.title("Average Confidence per Device")
    plt.ylim(0, 1)
    plt.grid(axis="y", alpha=0.3)
    plt.savefig("output/avg_confidence_per_device.png")
    plt.close()

    print("\nExperiment completed successfully.\n")


if __name__ == "__main__":
    main()