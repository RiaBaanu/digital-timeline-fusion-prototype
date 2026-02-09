import matplotlib
matplotlib.use("Agg")  # non-GUI backend

import matplotlib.pyplot as plt


def plot_confidence_scores(skew_results, output_path):
    """
    Plot confidence scores per device and save as an image.

    Args:
        skew_results: dict returned by calculate_median_skew()
        output_path: path to save PNG file
    """
    devices = []
    confidences = []

    for device_id, data in skew_results.items():
        devices.append(device_id)
        confidences.append(data["confidence"])

    plt.figure(figsize=(6, 4))
    plt.bar(devices, confidences)
    plt.ylim(0, 1)
    plt.xlabel("Device")
    plt.ylabel("Confidence Score")
    plt.title("Clock Skew Correction Confidence per Device")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
