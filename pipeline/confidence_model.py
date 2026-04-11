"""
Composite Confidence Model
--------------------------
Computes unified confidence score for clustered events
based on temporal consistency, skew reliability,
and cluster completeness.
"""

import math
import statistics
import numpy as np


def compute_cluster_confidence(cluster, residuals, total_devices):
    """
    Compute composite confidence score (0–1) for an event cluster.

    Parameters:
        cluster (list): List of CanonicalEvent objects.
        residuals (dict): Device skew residuals {device_id: seconds}.
        total_devices (int): Total number of devices in dataset.

    Returns:
        float: Rounded confidence score between 0 and 1.
    """

    # ------------------------------------------
    # 1. Temporal Consistency
    # ------------------------------------------
    timestamps = []

    for e in cluster:
        if e.corrected_timestamp:
            try:
                dt = np.datetime64(e.corrected_timestamp)
                seconds = float(dt.astype("datetime64[s]").astype("int64"))
                timestamps.append(seconds)
            except Exception:
                continue

    if len(timestamps) > 1:
        temporal_std = float(np.std(timestamps))
    else:
        temporal_std = 0.0

    # Exponential decay (strong separation effect)
    temporal_quality = math.exp(-temporal_std / 20)


    # ------------------------------------------
    # 2. Cluster Completeness
    # ------------------------------------------
    cluster_size = len(cluster)

    if total_devices > 0:
        cluster_size_factor = cluster_size / total_devices
        size_penalty = 1 - abs(total_devices - cluster_size) / total_devices
    else:
        cluster_size_factor = 0.0
        size_penalty = 0.0


    # ------------------------------------------
    # 3. Skew Reliability
    # ------------------------------------------
    device_skews = [
        abs(residuals.get(e.device_id, 0))
        for e in cluster
    ]

    avg_skew = statistics.mean(device_skews) if device_skews else 0.0

    # Exponential penalty for skew instability
    skew_quality = math.exp(-avg_skew / 30)


    # ------------------------------------------
    # 4. Composite Score
    # ------------------------------------------
    composite_confidence = (
        0.40 * temporal_quality +
        0.35 * skew_quality +
        0.15 * cluster_size_factor +
        0.10 * size_penalty
    )

    # Clamp to [0, 1]
    composite_confidence = max(0.0, min(1.0, composite_confidence))

    return round(composite_confidence, 2)