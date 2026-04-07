#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot Barnes-Hut benchmark JSON output.")
    parser.add_argument("input", type=Path, help="Path to benchmark JSON output")
    parser.add_argument("--output", type=Path, default=Path("docs/barnes_hut_benchmark.png"), help="Destination PNG path")
    args = parser.parse_args()

    data = json.loads(args.input.read_text())
    counts = [entry["count"] for entry in data["results"]]
    force_speedups = [entry["force"]["speedup"] for entry in data["results"]]
    loop_speedups = [entry["loop"]["speedup"] for entry in data["results"]]
    rms_errors = [entry["force"]["rms_error"] for entry in data["results"]]
    node_counts = [entry["force"]["node_count"] for entry in data["results"]]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    fig.patch.set_facecolor("#0b1220")

    for ax in axes:
        ax.set_facecolor("#111a2b")
        ax.grid(color="#25324a", alpha=0.55, linewidth=0.8)
        ax.tick_params(colors="#dfe8f5")
        for spine in ax.spines.values():
            spine.set_color("#2f405d")
        ax.title.set_color("#eef4ff")
        ax.xaxis.label.set_color("#c6d3e6")
        ax.yaxis.label.set_color("#c6d3e6")

    axes[0].plot(counts, force_speedups, marker="o", color="#f2c879", linewidth=2.2, label="Force speedup")
    axes[0].plot(counts, loop_speedups, marker="o", color="#80c6ff", linewidth=2.2, label="Loop speedup")
    axes[0].set_title("Speedup vs Particle Count")
    axes[0].set_xlabel("Particle count")
    axes[0].set_ylabel("Speedup")
    axes[0].legend(facecolor="#162235", edgecolor="#2f405d", labelcolor="#edf5ff")

    axes[1].plot(counts, rms_errors, marker="o", color="#ff8f86", linewidth=2.2)
    axes[1].set_title("Force Error vs Particle Count")
    axes[1].set_xlabel("Particle count")
    axes[1].set_ylabel("RMS acceleration error")

    axes[2].plot(counts, node_counts, marker="o", color="#f5d89d", linewidth=2.2)
    axes[2].set_title("Tree Size vs Particle Count")
    axes[2].set_xlabel("Particle count")
    axes[2].set_ylabel("Barnes-Hut nodes")

    fig.suptitle(
        f"Barnes-Hut Benchmark (theta = {data['theta']:.2f}, steps = {data['steps']})",
        color="#eef4ff",
        fontsize=14,
        fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=180, facecolor=fig.get_facecolor(), bbox_inches="tight")
    print(f"Saved plot to {args.output}")


if __name__ == "__main__":
    main()
