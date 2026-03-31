# Physics Engine

A high-performance rigid-body physics simulator built in C++ for robotics simulation and numerical methods exploration.

## Features

### Current Implementation
- Rigid Body Dynamics (mass, position, velocity, forces)
- 2D Vector Mathematics library
- Euler Integration with configurable timesteps
- Gravity forces
- Ground collision detection with restitution (bouncing)
- CMake build system
- Clean terminal output with status indicators

### In Development
- Runge-Kutta 4 Integration (higher accuracy)
- Sphere-Sphere collision detection
- Multiple object simulation
- Python visualization

## Quick Start

### Build with CMake:

```bash
git clone https://github.com/sb808bit/physics-engine.git
cd physics-engine
mkdir build && cd build
cmake ..
make
./physics_engine
```

### Or compile directly:

```bash
cd src
g++ -std=c++17 -I. main.cpp core/RigidBody.cpp -o demo
./demo
```

## Why This Matters for Robotics

This project demonstrates the core concepts used in robotics physics engines like MuJoCo, Drake, and Bullet:
- Rigid body dynamics for robot arms and manipulators
- Collision detection for obstacle avoidance
- Numerical integration for stable simulation
- Contact resolution for realistic interactions

## Skills Demonstrated

- C++17 development with object-oriented design
- Numerical methods (Euler integration)
- Physics simulation (Newtonian mechanics, collisions)
- CMake build systems and Git version control

## Author

Supash Bhat
UC Berkeley - Physics, Astrophysics, Music
GitHub: sb808bit

## Python Interactive Demo

For the full interactive experience with all features, run the Python version:

```bash
git clone https://github.com/supashbhat/physics-engine.git
cd physics-engine
pip install pygame
python3 visualize_realtime.py
```

**Features in Python version:**
- ✅ Click and drag to throw balls with velocity
- ✅ Real-time gravity slider
- ✅ WASD gravity direction control
- ✅ **Window shake inertia** — drag the window to shake all balls
- ✅ Energy display with trails
- ✅ SPACE to add balls, R to reset, C to clear
- ✅ Toggle between energy and controls display
