#!/usr/bin/env python3
"""
Physics Engine Visualization
Plots trajectories from simulation output
"""

import matplotlib.pyplot as plt
import numpy as np
import sys
import re

def parse_simulation_data(filename):
    """Parse simulation output to extract trajectories"""
    trajectories = {}
    
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        print("Run the simulation first: ./physics_engine > sim_output.txt")
        return None
    
    for line in lines:
        # Look for ball data lines
        if 'Ball' in line and 'pos(' in line:
            # Extract ball number
            ball_match = re.search(r'Ball\s+(\d+)', line)
            if not ball_match:
                continue
            
            ball_id = int(ball_match.group(1))
            
            # Extract position coordinates
            pos_match = re.search(r'pos\(([-\d.]+),\s*([-\d.]+)\)', line)
            if not pos_match:
                continue
            
            x = float(pos_match.group(1))
            y = float(pos_match.group(2))
            
            # Initialize trajectory for this ball if needed
            if ball_id not in trajectories:
                trajectories[ball_id] = {'x': [], 'y': []}
            
            trajectories[ball_id]['x'].append(x)
            trajectories[ball_id]['y'].append(y)
    
    return trajectories

def plot_trajectories(trajectories):
    """Plot all ball trajectories"""
    if not trajectories:
        print("No trajectory data found in file.")
        return
    
    plt.figure(figsize=(14, 8))
    
    # Use a colormap for different balls
    colors = plt.cm.tab20(np.linspace(0, 1, len(trajectories)))
    
    for i, (ball_id, traj) in enumerate(sorted(trajectories.items())):
        # Special marker for ball 99
        if ball_id == 99:
            marker = '★'
            color = 'red'
            linewidth = 3
            markersize = 8
            label = f'Ball {ball_id} (High Bounce)'
        else:
            marker = 'o'
            color = colors[i % len(colors)]
            linewidth = 2
            markersize = 4
            label = f'Ball {ball_id}'
        
        plt.plot(traj['x'], traj['y'], 
                label=label, 
                color=color,
                marker=marker, 
                markersize=markersize,
                linewidth=linewidth,
                alpha=0.7,
                markevery=max(1, len(traj['x']) // 20))  # Plot markers sparingly
    
    plt.xlabel('X Position (m)', fontsize=12, fontweight='bold')
    plt.ylabel('Y Position (m)', fontsize=12, fontweight='bold')
    plt.title('Physics Engine: Ball Trajectories (RK4 Integration)', 
              fontsize=14, fontweight='bold')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.axhline(y=0, color='black', linestyle='-', linewidth=2, alpha=0.5, label='Ground')
    plt.xlim(-12, 12)
    plt.ylim(-0.5, 8)
    
    plt.tight_layout()
    plt.savefig('trajectories.png', dpi=150, bbox_inches='tight')
    print("\n✓ Saved trajectory plot to trajectories.png")
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 visualize.py sim_output.txt")
        sys.exit(1)
    
    trajectories = parse_simulation_data(sys.argv[1])
    plot_trajectories(trajectories)
