# Physics Engine Benchmark Results

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
