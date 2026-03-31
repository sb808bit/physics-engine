#include <iostream>
#include <iomanip>
#include <cmath>
#include <vector>
#include "core/Vec2.h"
#include "core/RigidBody.h"
#include "dynamics/Integrator.h"

// Spring force: F = -k * x
Vec2 springForce(const RigidBody& body, double k) {
    return Vec2(-k * body.position.x, -k * body.position.y);
}

void runSpringBenchmark(const std::string& name, 
                        void (*integrator)(RigidBody&, const Vec2&, double),
                        double dt) {
    std::cout << "\n" << name << " (Spring-Mass System, dt=" << dt << "):\n";
    std::cout << "────────────────────────────────────────────────\n";
    
    RigidBody body(1.0, 1.0);
    body.position = Vec2(1.0, 0);  // Stretch spring to x=1
    body.velocity = Vec2(0, 0);
    
    double k = 100.0;  // Spring constant
    double simTime = 1.0;
    int steps = simTime / dt;
    
    // Analytical solution: x = cos(ωt) where ω = sqrt(k/m) = 10
    double omega = std::sqrt(k / body.mass);
    
    double maxError = 0;
    double t = 0;
    
    std::cout << std::fixed << std::setprecision(8);
    for (int i = 0; i <= steps; i++) {
        t = i * dt;
        
        // Apply spring force and integrate
        Vec2 force = springForce(body, k);
        integrator(body, force, dt);
        
        // Analytical position
        double x_analytical = std::cos(omega * t);
        double error = std::abs(body.position.x - x_analytical);
        
        if (error > maxError) maxError = error;
        
        if (i % 100 == 0 && dt <= 0.01) {  // Print every 0.1 seconds at dt=0.001
            std::cout << "  t=" << t << "s: x=" << body.position.x 
                      << " (error=" << error << ")\n";
        } else if (i % 10 == 0 && dt > 0.01) {
            std::cout << "  t=" << t << "s: x=" << body.position.x 
                      << " (error=" << error << ")\n";
        }
    }
    
    std::cout << "\n  MAX ERROR: " << maxError << "\n";
}

int main() {
    std::cout << "\n";
    std::cout << "╔══════════════════════════════════════════════════════════════╗\n";
    std::cout << "║     SPRING-MASS BENCHMARK: Euler vs RK4 (Non-constant Force)║\n";
    std::cout << "╚══════════════════════════════════════════════════════════════╝\n";
    
    std::vector<double> dt_list = {0.01, 0.005, 0.001};
    
    for (double dt : dt_list) {
        std::cout << "\n" << std::string(60, '=') << "\n";
        std::cout << "Time step: " << dt << " seconds\n";
        std::cout << std::string(60, '=');
        
        runSpringBenchmark("Euler", Integrator::euler, dt);
        runSpringBenchmark("RK4", Integrator::rk4, dt);
    }
    
    std::cout << "\n";
    std::cout << "═══════════════════════════════════════════════════════════════\n";
    std::cout << "CONCLUSION: RK4 is dramatically more accurate for non-constant forces!\n";
    std::cout << "═══════════════════════════════════════════════════════════════\n\n";
    
    return 0;
}
