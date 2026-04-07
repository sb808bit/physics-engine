# Physics Engine

Physics Engine is a computational physics sandbox built around rigid-body simulation, numerical integration, and interactive visualization. It combines a C++ core with Python and browser-facing surfaces so the same physical ideas can be explored through benchmarks, local sandboxes, and public demos.

The project started as a way to compare integrators and collision handling in a more tangible setting. It now also includes a Barnes-Hut workstream for many-body gravity, scaling experiments, and approximation-quality analysis.

## Highlights

- C++ rigid-body core with Euler and RK4 integration
- Multi-body simulation with circle-circle and ground collision handling
- Benchmark tooling for energy drift and spring-system behavior
- Polished real-time Python sandbox with scene presets, pause/step controls, and live energy feedback
- Browser-facing 2D and 3D demo surfaces connected to the portfolio
- Barnes-Hut exact-vs-approximation compare lab with quadtree overlay, divergence tracking, and generated scaling/theta benchmark plots

## Quick Start

### Build the C++ engine

```bash
git clone https://github.com/supashbhat/physics-engine.git
cd physics-engine
cmake -S . -B build
cmake --build build
./build/physics_engine
```

### Run the real-time sandbox

```bash
pip install pygame
python3 visualize_realtime.py
```

### Run the analysis scripts

```bash
pip install numpy matplotlib
python3 energy_analysis.py
python3 spring_visualize.py
```

### Run the Barnes-Hut benchmark

```bash
python3 barnes_hut_benchmark.py --counts 240 480 960 1600 --theta 0.6 --write-summary --json-out docs/barnes_hut_latest.json
python3 barnes_hut_plot.py docs/barnes_hut_latest.json --output docs/barnes_hut_benchmark.png
```

### Run the Barnes-Hut theta sweep

```bash
python3 barnes_hut_theta_sweep.py --count 960 --steps 12 --thetas 0.35 0.50 0.65 0.80 1.00 --write-summary --json-out docs/barnes_hut_theta_sweep.json
python3 barnes_hut_theta_plot.py docs/barnes_hut_theta_sweep.json --output docs/barnes_hut_theta_sweep.png
```

### Run the Barnes-Hut compare lab

```bash
pip install pygame
python3 barnes_hut_visualizer.py
```

This launches a split-view local surface with exact `O(N^2)` gravity on the left and Barnes-Hut on the right.

## Main Components

### C++ core

- `RigidBody`, `Vec2`, and collision primitives
- Euler and RK4 integrators for direct numerical comparison
- Terminal-native simulation loop for fast iteration
- Benchmark programs that make the integrator tradeoff explicit

### Python sandbox

`visualize_realtime.py` is the most polished local surface in the repository.

- Drag-and-throw interaction
- Scene presets: `Random`, `Cascade`, `Orbit`
- Live gravity, time-scale, and trail controls
- Pause / step workflow
- HUD, help overlay, and energy-history display
- Atmospheric styling so the sandbox reads like a tool instead of a debug window

### Browser demos

- [2D demo](https://supashbhat.github.io/2d-physics.html)
- [3D demo](https://supashbhat.github.io/3d-physics.html)
- [Physics project page](https://supashbhat.github.io/physics-engine.html)

### Barnes-Hut workstream

The Barnes-Hut additions live in:

- `barnes_hut.py`
- `barnes_hut_benchmark.py`
- `barnes_hut_plot.py`
- `barnes_hut_theta_sweep.py`
- `barnes_hut_theta_plot.py`
- `barnes_hut_visualizer.py`
- `docs/barnes_hut_notes.md`
- `docs/barnes_hut_latest.txt`
- `docs/barnes_hut_latest.json`
- `docs/barnes_hut_benchmark.png`
- `docs/barnes_hut_theta_sweep.txt`
- `docs/barnes_hut_theta_sweep.json`
- `docs/barnes_hut_theta_sweep.png`

This part of the repo is focused on scaling from small-body interaction toward large gravitational systems through spatial partitioning, center-of-mass approximation, timing/error tradeoff analysis, and direct visual comparison against the exact solver.

## Sandbox Controls

### Keyboard

- `W A S D` - redirect gravity
- `1 2 3` - switch scene preset
- `Space` - spawn one ball
- `B` - spawn a burst
- `R` - reset the current preset
- `C` - clear the scene
- `P` - pause / resume
- `.` - step one frame while paused
- `T` - toggle trails
- `H` - toggle HUD
- `I` - toggle help overlay

### Mouse

- Drag a ball to reposition and throw it
- Drag the window itself to inject a subtle global impulse

## Repository Map

- `src/` - C++ engine core, collisions, and benchmarks
- `visualize_realtime.py` - polished Pygame sandbox
- `visualize.py` - trajectory plotting
- `energy_analysis.py` - free-fall energy comparison
- `spring_visualize.py` - spring benchmark visualization
- `barnes_hut.py` - Barnes-Hut quadtree, exact gravity baseline, and stepping helpers
- `barnes_hut_benchmark.py` - timing/error comparison script for many-body gravity
- `barnes_hut_plot.py` - plot generation for benchmark JSON output
- `barnes_hut_theta_sweep.py` - theta-vs-speed/error sweep for approximation tuning
- `barnes_hut_theta_plot.py` - plot generation for theta sweep JSON output
- `barnes_hut_visualizer.py` - split-view local compare lab for exact vs Barnes-Hut stepping
- `docs/barnes_hut_notes.md` - Barnes-Hut implementation notes and next steps
- `docs/barnes_hut_benchmark.png` - current benchmark figure
- `docs/barnes_hut_theta_sweep.png` - current theta sweep figure
- `ROADMAP.md` - project direction and future milestones

## Why This Project Exists

The aim is to make computational physics feel both rigorous and explorable: numerical methods that can be benchmarked seriously, but also interacted with directly. That same idea carries across the browser demos, the Python sandbox, and the newer Barnes-Hut scaling work.

## Roadmap

Current directions include:

- Barnes-Hut browser-facing visualization, larger `N` benchmarking, and broader particle distributions
- Broader collision and constraint systems
- More unified architecture between the C++ core and interactive surfaces
- Stronger browser-facing demos tied into the portfolio

More detail is available in [ROADMAP.md](ROADMAP.md).
