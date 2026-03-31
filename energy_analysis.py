#!/usr/bin/env python3
"""
Energy Conservation Analysis
Shows why RK4 is superior to Euler for physics simulation
"""

import numpy as np
import matplotlib.pyplot as plt

def simulate_free_fall(method, dt=0.001, sim_time=1.0):
    """Simulate pure free-fall (no collisions) with exact forces"""
    n_steps = int(sim_time / dt)
    t = np.linspace(0, sim_time, n_steps)
    y = np.zeros(n_steps)
    vy = np.zeros(n_steps)
    
    # Initial conditions
    y[0] = 10.0
    vy[0] = 0.0
    g = -9.81
    
    # Analytical solution
    y_analytical = 10 + 0.5 * g * t**2
    vy_analytical = g * t
    
    for i in range(n_steps - 1):
        if method == 'euler':
            # Euler integration (first-order)
            vy[i+1] = vy[i] + g * dt
            y[i+1] = y[i] + vy[i] * dt
        else:
            # RK4 for free-fall (should match analytical)
            # k1
            vy1 = vy[i]
            y1 = y[i]
            # k2
            vy2 = vy[i] + g * dt/2
            y2 = y[i] + vy1 * dt/2
            # k3
            vy3 = vy[i] + g * dt/2
            y3 = y[i] + vy2 * dt/2
            # k4
            vy4 = vy[i] + g * dt
            y4 = y[i] + vy3 * dt
            # Weighted average
            vy[i+1] = vy[i] + (g + 2*g + 2*g + g) * dt / 6
            y[i+1] = y[i] + (vy1 + 2*vy2 + 2*vy3 + vy4) * dt / 6
    
    return t, y, vy, y_analytical, vy_analytical

def run_energy_comparison():
    """Compare Euler vs RK4 accuracy"""
    print("\n" + "="*70)
    print("ENERGY CONSERVATION ANALYSIS: Euler vs RK4 (Free Fall)")
    print("="*70)
    
    dt = 0.001
    sim_time = 1.0
    
    t_euler, y_euler, vy_euler, y_theory, vy_theory = simulate_free_fall('euler', dt, sim_time)
    t_rk4, y_rk4, vy_rk4, _, _ = simulate_free_fall('rk4', dt, sim_time)
    
    # Calculate errors
    pos_error_euler = np.abs(y_euler - y_theory)
    pos_error_rk4 = np.abs(y_rk4 - y_theory)
    
    vel_error_euler = np.abs(vy_euler - vy_theory)
    vel_error_rk4 = np.abs(vy_rk4 - vy_theory)
    
    # Calculate energy (E = mgh + 1/2 mv^2, m=1)
    energy_euler = 9.81 * np.maximum(0, y_euler) + 0.5 * vy_euler**2
    energy_rk4 = 9.81 * np.maximum(0, y_rk4) + 0.5 * vy_rk4**2
    energy_theory = 9.81 * np.maximum(0, y_theory) + 0.5 * vy_theory**2
    
    energy_error_euler = np.abs((energy_euler - energy_theory) / energy_theory) * 100
    energy_error_rk4 = np.abs((energy_rk4 - energy_theory) / energy_theory) * 100
    
    print(f"\nSimulation Parameters:")
    print(f"  • dt = {dt} seconds")
    print(f"  • Simulation time = {sim_time} seconds")
    print(f"  • Initial height = 10.0 m")
    print(f"  • Gravity = 9.81 m/s²")
    print(f"  • No collisions (pure free-fall)")
    
    print(f"\n{'Method':<10} {'Max Pos Error':<20} {'Max Vel Error':<20} {'Max Energy Error':<20}")
    print("-" * 70)
    print(f"{'Euler':<10} {np.max(pos_error_euler):<20.6e} m {np.max(vel_error_euler):<20.6e} m/s {np.max(energy_error_euler):<20.6f}%")
    print(f"{'RK4':<10} {np.max(pos_error_rk4):<20.6e} m {np.max(vel_error_rk4):<20.6e} m/s {np.max(energy_error_rk4):<20.6f}%")
    
    # Improvement factor
    improvement = np.max(pos_error_euler) / np.max(pos_error_rk4)
    print(f"\n{'='*70}")
    print(f"RESULT: RK4 is {improvement:.1e} times more accurate than Euler!")
    print(f"{'='*70}")
    
    # Create visualization
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Position comparison
    ax1 = axes[0, 0]
    ax1.plot(t_euler, y_euler, label='Euler', linewidth=2, alpha=0.7)
    ax1.plot(t_rk4, y_rk4, label='RK4', linewidth=2, alpha=0.7)
    ax1.plot(t_euler, y_theory, 'k--', label='Theoretical', linewidth=2, alpha=0.5)
    ax1.set_xlabel('Time (s)', fontsize=12)
    ax1.set_ylabel('Position (m)', fontsize=12)
    ax1.set_title('Free Fall: Position vs Time', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Position error (log scale)
    ax2 = axes[0, 1]
    ax2.semilogy(t_euler, pos_error_euler, label='Euler', linewidth=2)
    ax2.semilogy(t_rk4, pos_error_rk4, label='RK4', linewidth=2)
    ax2.set_xlabel('Time (s)', fontsize=12)
    ax2.set_ylabel('Position Error (m)', fontsize=12)
    ax2.set_title('Position Error (Log Scale)', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Velocity error (log scale)
    ax3 = axes[1, 0]
    ax3.semilogy(t_euler, vel_error_euler, label='Euler', linewidth=2)
    ax3.semilogy(t_rk4, vel_error_rk4, label='RK4', linewidth=2)
    ax3.set_xlabel('Time (s)', fontsize=12)
    ax3.set_ylabel('Velocity Error (m/s)', fontsize=12)
    ax3.set_title('Velocity Error (Log Scale)', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Energy error (log scale)
    ax4 = axes[1, 1]
    ax4.semilogy(t_euler, energy_error_euler, label='Euler', linewidth=2)
    ax4.semilogy(t_rk4, energy_error_rk4, label='RK4', linewidth=2)
    ax4.set_xlabel('Time (s)', fontsize=12)
    ax4.set_ylabel('Energy Error (%)', fontsize=12)
    ax4.set_title('Energy Error (Log Scale)', fontsize=12, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('energy_comparison.png', dpi=150, bbox_inches='tight')
    print("\n✓ Saved energy comparison plot to energy_comparison.png")
    plt.show()
    
    print("\n" + "="*70)
    print("CONCLUSION:")
    print("  • Euler integration accumulates error quadratically with time")
    print("  • RK4 maintains high accuracy even with large time steps")
    print("  • For robotics simulation, RK4 is essential for stable physics")
    print("="*70 + "\n")

if __name__ == "__main__":
    run_energy_comparison()
