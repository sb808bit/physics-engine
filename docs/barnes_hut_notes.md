# Barnes-Hut Notes

This workstream extends the physics engine from local rigid-body interaction into many-body gravity and scaling.

## Why Barnes-Hut

Direct gravity between `N` bodies is `O(N^2)`. That is fine for dozens or a few hundred particles, but it becomes expensive quickly. Barnes-Hut reduces the force pass by grouping distant regions of mass and approximating them with a single center-of-mass interaction, leading to roughly `O(N log N)` behavior.

## Current Implementation

- 2D quadtree with recursive subdivision
- Center-of-mass aggregation at each node
- Barnes-Hut force traversal with configurable `theta`
- Direct exact-force baseline for comparison
- Leapfrog-style stepping for simple multi-step timing comparisons
- Benchmark script that compares:
  - exact vs Barnes-Hut force-pass time
  - approximate vs exact integration-loop runtime
  - RMS acceleration error
  - tree size and depth
- Theta sweep script that compares:
  - speedup versus opening angle
  - RMS error versus opening angle
  - approximation tuning at a fixed particle field
- Plot generator that turns the latest JSON benchmark output into a shareable PNG
- Split-view local compare lab (`barnes_hut_visualizer.py`) that renders:
  - exact `O(N^2)` stepping on the left
  - Barnes-Hut on the right
  - quadtree overlay on demand
  - position divergence, force error, and energy drift stats

## What To Look For

- smaller `theta` values improve accuracy but reduce speedup
- larger `theta` values improve speed but increase approximation error
- the useful range is where timing improves materially while force error remains interpretable
- divergence between the exact and Barnes-Hut particle fields should stay understandable rather than exploding immediately
- tree node count and depth help explain why performance changes with particle distribution, not only particle count

## Current Snapshot

Using `theta = 0.60` and the current first-pass benchmark:

- `N = 240` -> loop speedup `1.45x`
- `N = 480` -> loop speedup `2.41x`
- `N = 960` -> loop speedup `4.24x`
- `N = 1600` -> loop speedup `6.24x`

The exact crossover will still depend on particle distribution and implementation details, but the overall curve is now strong enough to show the intended scaling story.

Using the current `N = 960` theta sweep:

- `theta = 0.35` -> loop speedup `2.01x`, RMS accel error `0.0225`
- `theta = 0.50` -> loop speedup `3.31x`, RMS accel error `0.0603`
- `theta = 0.65` -> loop speedup `4.49x`, RMS accel error `0.1311`
- `theta = 0.80` -> loop speedup `5.78x`, RMS accel error `0.3002`
- `theta = 1.00` -> loop speedup `7.60x`, RMS accel error `0.5027`

That makes the tradeoff legible: larger `theta` values are dramatically faster, but they also widen the approximation error fast enough that the choice should be treated as a tunable design parameter, not just a free speed boost.

## Compare Lab Controls

- `1 / 2 / 3` switch scenario
- `[` / `]` adjust `theta`
- `Q` toggles the quadtree overlay
- `T` toggles sample trails
- `Space` pauses the sim
- `S` advances one simulation step while paused
- `R` resets the current scenario

## Next Steps

- add a browser-facing N-body surface rather than only the local compare lab
- benchmark larger particle counts and multiple particle distributions
- connect the Barnes-Hut work to a future public demo surface
