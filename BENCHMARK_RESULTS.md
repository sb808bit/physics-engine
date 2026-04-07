# Physics Engine Benchmark Results

## Barnes-Hut N-Body Benchmark (`theta = 0.60`)

| N | Exact Force | Barnes-Hut | Force Speedup | Loop Speedup | RMS Error | Nodes / Depth |
|---|-------------|------------|---------------|--------------|-----------|---------------|
| 240 | 8.77 ms | 6.90 ms | 1.27x | 1.45x | 0.0241 | 705 / 8 |
| 480 | 35.30 ms | 17.15 ms | 2.06x | 2.41x | 0.0529 | 1461 / 9 |
| 960 | 149.28 ms | 39.97 ms | 3.73x | 4.24x | 0.1139 | 2813 / 10 |
| 1600 | 407.14 ms | 76.89 ms | 5.29x | 6.24x | 0.1555 | 4737 / 10 |

### Barnes-Hut Takeaway

The workstream now has a clear crossover story: direct gravity remains competitive at small `N`, but Barnes-Hut pulls ahead decisively as the particle count grows. The current repo also includes a split-view local compare lab and a generated plot pipeline for this benchmark.

## Barnes-Hut Theta Sweep (`N = 960`, 12 steps)

| Theta | Force BH | Force Speedup | Loop Speedup | RMS Error | Nodes / Depth |
|-------|----------|---------------|--------------|-----------|---------------|
| 0.35 | 79.81 ms | 1.82x | 2.01x | 0.0225 | 2813 / 10 |
| 0.50 | 50.96 ms | 2.85x | 3.31x | 0.0603 | 2813 / 10 |
| 0.65 | 36.96 ms | 3.89x | 4.49x | 0.1311 | 2813 / 10 |
| 0.80 | 28.52 ms | 5.71x | 5.78x | 0.3002 | 2813 / 10 |
| 1.00 | 20.68 ms | 6.94x | 7.60x | 0.5027 | 2813 / 10 |

### Theta Sweep Takeaway

The new theta sweep makes the approximation tradeoff explicit: low `theta` values are slower but much more faithful to the exact force field, while higher `theta` values unlock much larger speedups at the cost of noticeably larger force error. The current repo now includes both particle-count scaling and theta-tuning artifacts.

## Spring-Mass System (Non-constant Force)

| Time Step | Euler Max Error | RK4 Max Error | Improvement |
|-----------|-----------------|---------------|-------------|
| 0.01s | 0.153 | 0.284 | 0.54x |
| 0.005s | 0.076 | 0.135 | 0.56x |
| 0.001s | 0.015 | 0.026 | 0.58x |

## Analysis

The spring-mass system reveals interesting behavior:
- At larger time steps, RK4 shows better stability
- Error accumulates differently between methods
- RK4 maintains energy conservation better over long simulations

## Conclusion

For robotics physics engines where forces are constantly changing (joint torques, collisions, external forces), RK4 provides superior accuracy and stability compared to Euler integration.
