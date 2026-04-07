#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot Barnes-Hut theta sweep JSON output.")
    parser.add_argument("input", type=Path, help="Path to theta sweep JSON output")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/barnes_hut_theta_sweep.png"),
        help="Destination PNG path",
    )
    args = parser.parse_args()

    data = json.loads(args.input.read_text())
    thetas = [entry["theta"] for entry in data["results"]]
    force_speedups = [entry["force"]["speedup"] for entry in data["results"]]
    loop_speedups = [entry["loop"]["speedup"] for entry in data["results"]]
    rms_errors = [entry["force"]["rms_error"] for entry in data["results"]]

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

    axes[0].plot(thetas, force_speedups, marker="o", color="#f2c879", linewidth=2.2)
    axes[0].set_title("Force Speedup vs Theta")
    axes[0].set_xlabel("Theta")
    axes[0].set_ylabel("Force speedup")

    axes[1].plot(thetas, loop_speedups, marker="o", color="#80c6ff", linewidth=2.2)
    axes[1].set_title("Loop Speedup vs Theta")
    axes[1].set_xlabel("Theta")
    axes[1].set_ylabel("Loop speedup")

    axes[2].plot(thetas, rms_errors, marker="o", color="#ff8f86", linewidth=2.2)
    axes[2].set_title("Force Error vs Theta")
    axes[2].set_xlabel("Theta")
    axes[2].set_ylabel("RMS acceleration error")

    fig.suptitle(
        f"Barnes-Hut Theta Sweep (N = {data['count']}, steps = {data['steps']})",
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
