#!/usr/bin/env python3
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import time

from barnes_hut import (
    barnes_hut_tree_and_accelerations,
    collect_tree_stats,
    exact_accelerations,
    leapfrog_step,
    make_disc_particles,
    rms_force_error,
)

REPO_ROOT = Path(__file__).resolve().parent
DOCS_DIR = REPO_ROOT / "docs"


def benchmark_force_pass(particles, theta):
    start = time.perf_counter()
    tree, approx = barnes_hut_tree_and_accelerations(particles, theta=theta)
    approx_time = time.perf_counter() - start
    stats = collect_tree_stats(tree)

    start = time.perf_counter()
    exact = exact_accelerations(particles)
    exact_time = time.perf_counter() - start

    return {
        "approx_time": approx_time,
        "exact_time": exact_time,
        "speedup": exact_time / max(approx_time, 1e-9),
        "rms_error": rms_force_error(exact, approx),
        "node_count": stats.node_count,
        "max_depth": stats.max_depth,
        "occupied_leaves": stats.occupied_leaves,
    }


def benchmark_step_loop(count, steps, theta, seed):
    exact_particles = make_disc_particles(count, seed=seed)
    approx_particles = deepcopy(exact_particles)

    start = time.perf_counter()
    for _ in range(steps):
        leapfrog_step(exact_particles, 1 / 90.0, method="exact")
    exact_runtime = time.perf_counter() - start

    start = time.perf_counter()
    for _ in range(steps):
        leapfrog_step(approx_particles, 1 / 90.0, method="barnes-hut", theta=theta)
    approx_runtime = time.perf_counter() - start

    return {
        "exact_runtime": exact_runtime,
        "approx_runtime": approx_runtime,
        "speedup": exact_runtime / max(approx_runtime, 1e-9),
    }


def format_row(columns):
    return " | ".join(str(column).ljust(width) for column, width in columns)


def main():
    parser = argparse.ArgumentParser(description="Benchmark Barnes-Hut against direct O(N^2) gravity.")
    parser.add_argument("--theta", type=float, default=0.6, help="Barnes-Hut opening angle")
    parser.add_argument("--steps", type=int, default=30, help="Integration steps for loop benchmark")
    parser.add_argument("--seed", type=int, default=7, help="Random seed")
    parser.add_argument("--counts", type=int, nargs="+", default=[250, 500, 1000, 2000], help="Particle counts")
    parser.add_argument("--write-summary", action="store_true", help="Write a benchmark snapshot into docs/")
    parser.add_argument("--json-out", type=Path, default=None, help="Optional JSON output path")
    args = parser.parse_args()

    print("\nBarnes-Hut Benchmark")
    print("====================")
    print(f"Theta: {args.theta:.2f}")
    print(f"Step benchmark length: {args.steps} steps")
    print("")

    headers = [
        ("N", 6),
        ("Force exact (ms)", 18),
        ("Force BH (ms)", 16),
        ("Force speedup", 16),
        ("RMS accel err", 16),
        ("Nodes/depth", 16),
        ("Loop speedup", 14),
    ]
    print(format_row(headers))
    print("-" * 116)

    results = []
    for count in args.counts:
        particles = make_disc_particles(count, seed=args.seed + count)
        force_result = benchmark_force_pass(particles, theta=args.theta)
        loop_result = benchmark_step_loop(count, args.steps, args.theta, seed=args.seed + count)
        results.append((count, force_result, loop_result))

        row = [
            (count, 6),
            (f"{force_result['exact_time'] * 1000:0.2f}", 18),
            (f"{force_result['approx_time'] * 1000:0.2f}", 16),
            (f"{force_result['speedup']:0.2f}x", 16),
            (f"{force_result['rms_error']:0.4f}", 16),
            (f"{force_result['node_count']}/{force_result['max_depth']}", 16),
            (f"{loop_result['speedup']:0.2f}x", 14),
        ]
        print(format_row(row))

    best = max(results, key=lambda entry: entry[2]["speedup"])
    print("")
    print(
        f"Best observed loop speedup: {best[2]['speedup']:0.2f}x at N={best[0]} with theta={args.theta:.2f}."
    )
    print("Use smaller theta values for more accuracy and larger values for more aggressive approximation.")

    if args.write_summary:
        artifact = DOCS_DIR / "barnes_hut_latest.txt"
        artifact.parent.mkdir(exist_ok=True)
        lines = [
            "Barnes-Hut Benchmark Snapshot",
            f"Theta: {args.theta:.2f}",
            f"Steps: {args.steps}",
            "",
        ]
        for count, force_result, loop_result in results:
            lines.append(
                f"N={count}: force speedup {force_result['speedup']:0.2f}x, "
                f"loop speedup {loop_result['speedup']:0.2f}x, "
                f"RMS accel error {force_result['rms_error']:0.4f}, "
                f"nodes/depth {force_result['node_count']}/{force_result['max_depth']}"
            )
        artifact.write_text("\n".join(lines) + "\n")
        print(f"Saved summary to {artifact}")

    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "theta": args.theta,
            "steps": args.steps,
            "counts": args.counts,
            "results": [
                {
                    "count": count,
                    "force": force_result,
                    "loop": loop_result,
                }
                for count, force_result, loop_result in results
            ],
        }
        args.json_out.write_text(json.dumps(payload, indent=2) + "\n")
        print(f"Saved JSON to {args.json_out}")


if __name__ == "__main__":
    main()
