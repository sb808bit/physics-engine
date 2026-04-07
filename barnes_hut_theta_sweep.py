#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from barnes_hut import make_disc_particles
from barnes_hut_benchmark import benchmark_force_pass, benchmark_step_loop, format_row

REPO_ROOT = Path(__file__).resolve().parent
DOCS_DIR = REPO_ROOT / "docs"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sweep Barnes-Hut theta values to compare speed and approximation error."
    )
    parser.add_argument("--count", type=int, default=960, help="Particle count to benchmark")
    parser.add_argument(
        "--thetas",
        type=float,
        nargs="+",
        default=[0.35, 0.50, 0.65, 0.80, 1.00],
        help="Theta values to evaluate",
    )
    parser.add_argument("--steps", type=int, default=12, help="Integration steps for loop benchmark")
    parser.add_argument("--seed", type=int, default=7, help="Random seed base")
    parser.add_argument("--write-summary", action="store_true", help="Write a theta sweep snapshot into docs/")
    parser.add_argument("--json-out", type=Path, default=None, help="Optional JSON output path")
    args = parser.parse_args()

    print("\nBarnes-Hut Theta Sweep")
    print("======================")
    print(f"Particle count: {args.count}")
    print(f"Step benchmark length: {args.steps} steps")
    print("")

    headers = [
        ("Theta", 10),
        ("Force BH (ms)", 16),
        ("Force speedup", 16),
        ("Loop speedup", 14),
        ("RMS accel err", 16),
        ("Nodes/depth", 16),
    ]
    print(format_row(headers))
    print("-" * 92)

    results = []
    particles = make_disc_particles(args.count, seed=args.seed + args.count)
    for theta in args.thetas:
        force_result = benchmark_force_pass(particles, theta=theta)
        loop_result = benchmark_step_loop(args.count, args.steps, theta, seed=args.seed + args.count)
        results.append({"theta": theta, "force": force_result, "loop": loop_result})
        row = [
            (f"{theta:0.2f}", 10),
            (f"{force_result['approx_time'] * 1000:0.2f}", 16),
            (f"{force_result['speedup']:0.2f}x", 16),
            (f"{loop_result['speedup']:0.2f}x", 14),
            (f"{force_result['rms_error']:0.4f}", 16),
            (f"{force_result['node_count']}/{force_result['max_depth']}", 16),
        ]
        print(format_row(row))

    fastest = max(results, key=lambda entry: entry["loop"]["speedup"])
    most_accurate = min(results, key=lambda entry: entry["force"]["rms_error"])
    print("")
    print(
        f"Fastest tested theta: {fastest['theta']:0.2f} "
        f"({fastest['loop']['speedup']:0.2f}x loop speedup)."
    )
    print(
        f"Most accurate tested theta: {most_accurate['theta']:0.2f} "
        f"(RMS accel error {most_accurate['force']['rms_error']:0.4f})."
    )

    if args.write_summary:
        artifact = DOCS_DIR / "barnes_hut_theta_sweep.txt"
        artifact.parent.mkdir(exist_ok=True)
        lines = [
            "Barnes-Hut Theta Sweep",
            f"Particle count: {args.count}",
            f"Steps: {args.steps}",
            "",
        ]
        for entry in results:
            lines.append(
                f"theta={entry['theta']:0.2f}: "
                f"force speedup {entry['force']['speedup']:0.2f}x, "
                f"loop speedup {entry['loop']['speedup']:0.2f}x, "
                f"RMS accel error {entry['force']['rms_error']:0.4f}, "
                f"nodes/depth {entry['force']['node_count']}/{entry['force']['max_depth']}"
            )
        artifact.write_text("\n".join(lines) + "\n")
        print(f"Saved summary to {artifact}")

    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "count": args.count,
            "steps": args.steps,
            "thetas": args.thetas,
            "results": results,
        }
        args.json_out.write_text(json.dumps(payload, indent=2) + "\n")
        print(f"Saved JSON to {args.json_out}")


if __name__ == "__main__":
    main()
