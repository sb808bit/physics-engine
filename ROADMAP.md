# Physics Engine Roadmap

This roadmap tracks the project from rigid-body simulation and integrator benchmarking toward richer interaction, many-body scaling, and more unified simulation surfaces.

## Current Foundation

Already in place:

- Euler and RK4 integration
- Multi-body rigid-body simulation
- Ground and circle-circle collision handling
- Energy and spring benchmark scripts
- Real-time Python sandbox with live controls
- Browser-connected 2D and 3D demo surfaces

## Active Workstreams

### 1. Barnes-Hut and many-body scaling

Current status: active local compare lab + scaling/theta benchmark pipeline

- 2D Barnes-Hut quadtree implementation
- Exact-force baseline for correctness checks
- Benchmark script for force-pass timing and RMS acceleration error
- Plot generation for benchmark artifacts
- Theta sweep for speed-vs-error tuning
- Side-by-side local compare lab with quadtree overlay and divergence tracking

Next steps:

- Add a browser-facing N-body surface instead of local tooling alone
- Scale benchmarks to larger particle counts
- Compare multiple particle distributions beyond the disc swirl baseline
- Connect many-body work to a public-facing simulation demo

### 2. Simulation UX

Current status: strong local foundation plus Barnes-Hut compare tooling

- Scene presets
- Live gravity, time-scale, and trail controls
- Pause / step controls
- Help overlay and HUD
- Energy-history sparkline

Next steps:

- Guided scenes that teach specific numerical ideas
- More scenario-driven presets
- Tighter alignment between local and browser-facing demos

### 3. Engine depth

Current status: rigid-body and collision fundamentals are in place

Next steps:

- More collision shapes beyond circles
- Springs, joints, and mechanism systems
- Clearer separation between engine logic and presentation layers
- Stronger benchmark coverage across parameter regimes

## Longer-Term Direction

- Unify the simulation story across C++, Python, and web surfaces
- Make the portfolio demos feel like real educational and research tools
- Expand from rigid-body interaction into larger-scale gravitational and algorithmic simulations
- Keep the project useful both as a sandbox and as a serious benchmark-oriented physics repo
