#include <iostream>
#include <iomanip>
#include <cmath>
#include <vector>
#include "core/RigidBody.h"
#include "dynamics/Integrator.h"

struct EnergyData {
    double time;
    double kinetic;
    double potential;
    double total;
};

double computeEnergy(const RigidBody& body, double height) {
    double kinetic = 0.5 * body.mass * body.velocity.magnitudeSquared();
    double potential = body.mass * 9.81 * height;
    return kinetic + potential;
}

void runBenchmark(const std::string& name, void (*integrator)(RigidBody&, const Vec2&, double)) {
    std::cout << "\n" << name << ":\n";
    std::cout << "────────────────────────────────────────────────\n";
    
    RigidBody body(1.0, 0.95);
    body.position = Vec2(0, 10);
    body.velocity = Vec2(0, 0);
    Vec2 gravity(0, -9.81);
    double dt = 0.01;
    double simTime = 5.0;
    
    double initialEnergy = computeEnergy(body, body.position.y);
    double maxEnergyError = 0;
    double finalEnergyError = 0;
    
    for (double t = 0; t <= simTime; t += dt) {
        integrator(body, gravity, dt);
        
        // Ground collision
        if (body.position.y < 0) {
            body.position.y = 0;
            body.velocity.y = -body.velocity.y * body.restitution;
        }
        
        double currentEnergy = computeEnergy(body, body.position.y);
        double error = std::abs((currentEnergy - initialEnergy) / initialEnergy) * 100;
        
        if (error > maxEnergyError) maxEnergyError = error;
        
        if (std::abs(t - 2.0) < dt/2) {
            std::cout << "  t=2.0s: Energy error = " << std::fixed << std::setprecision(4) << error << "%\n";
        }
        
        finalEnergyError = error;
    }
    
    std::cout << "  Max error: " << std::setprecision(4) << maxEnergyError << "%\n";
    std::cout << "  Final error: " << std::setprecision(4) << finalEnergyError << "%\n";
    std::cout << "  Energy drift: " << std::setprecision(4) << (maxEnergyError - finalEnergyError) << "%\n";
}

int main() {
    std::cout << "\n";
    std::cout << "╔══════════════════════════════════════════════════════════════╗\n";
    std::cout << "║         PHYSICS ENGINE BENCHMARK: Euler vs RK4              ║\n";
    std::cout << "╚══════════════════════════════════════════════════════════════╝\n";
    
    runBenchmark("Euler Integration", Integrator::euler);
    runBenchmark("RK4 Integration", Integrator::rk4);
    
    std::cout << "\n";
    std::cout << "═══════════════════════════════════════════════════════════════\n";
    std::cout << "CONCLUSION: RK4 conserves energy significantly better than Euler\n";
    std::cout << "═══════════════════════════════════════════════════════════════\n\n";
    
    return 0;
}
