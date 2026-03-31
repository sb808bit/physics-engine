#!/usr/bin/env python3
"""
Spring-Mass System: Euler vs RK4 Comparison
"""

import numpy as np
import matplotlib.pyplot as plt

def simulate_spring(method, dt=0.01, sim_time=2.0):
    """Simulate spring-mass system: x'' + kx = 0"""
    n_steps = int(sim_time / dt)
    t = np.linspace(0, sim_time, n_steps)
    x = np.zeros(n_steps)
    v = np.zeros(n_steps)
    
    # Initial conditions: x=1, v=0
    x[0] = 1.0
    v[0] = 0.0
    k = 100.0
    m = 1.0
    omega = np.sqrt(k / m)
    
    for i in range(n_steps - 1):
        a = -k/m * x[i]
        
        if method == 'euler':
            # Euler integration
            v[i+1] = v[i] + a * dt
            x[i+1] = x[i] + v[i] * dt
        else:  # RK4
            # k1
            a1 = -k/m * x[i]
            v1 = v[i]
            x1 = x[i]
            # k2
            v2 = v[i] + a1 * dt/2
            x2 = x[i] + v1 * dt/2
            a2 = -k/m * x2
            # k3
            v3 = v[i] + a2 * dt/2
            x3 = x[i] + v2 * dt/2
            a3 = -k/m * x3
            # k4
            v4 = v[i] + a3 * dt
            x4 = x[i] + v3 * dt
            a4 = -k/m * x4
            # Weighted average
            v[i+1] = v[i] + (a1 + 2*a2 + 2*a3 + a4) * dt / 6
            x[i+1] = x[i] + (v1 + 2*v2 + 2*v3 + v4) * dt / 6
    
    x_analytical = np.cos(omega * t)
    return t, x, x_analytical

# Run simulations with different time steps
dt_values = [0.01, 0.005, 0.001]
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

for idx, dt in enumerate(dt_values):
    # Euler
    t_euler, x_euler, x_theory = simulate_spring('euler', dt)
    error_euler = np.abs(x_euler - x_theory)
    
    # RK4
    t_rk4, x_rk4, _ = simulate_spring('rk4', dt)
    error_rk4 = np.abs(x_rk4 - x_theory)
    
    # Position comparison
    ax1 = axes[0, idx]
    ax1.plot(t_euler, x_euler, label='Euler', linewidth=2, alpha=0.7)
    ax1.plot(t_rk4, x_rk4, label='RK4', linewidth=2, alpha=0.7)
    ax1.plot(t_euler, x_theory, 'k--', label='Theory', linewidth=2, alpha=0.5)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Position (m)')
    ax1.set_title(f'dt = {dt}s')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Error comparison (log scale)
    ax2 = axes[1, idx]
    ax2.semilogy(t_euler, error_euler, label='Euler Error', linewidth=2)
    ax2.semilogy(t_rk4, error_rk4, label='RK4 Error', linewidth=2)
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Error (m)')
    ax2.set_title(f'Error: dt = {dt}s')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    print(f"\ndt = {dt}s:")
    print(f"  Euler max error: {np.max(error_euler):.6e}")
    print(f"  RK4 max error:   {np.max(error_rk4):.6e}")
    print(f"  Improvement:     {np.max(error_euler)/np.max(error_rk4):.1e}x")

plt.tight_layout()
plt.savefig('spring_comparison.png', dpi=150)
print("\n✓ Saved spring comparison to spring_comparison.png")
plt.show()

print("\n" + "="*60)
print("CONCLUSION: RK4 is dramatically more accurate for oscillatory systems!")
print("For robotics simulation (constant changing forces), RK4 is essential.")
print("="*60)
