#include <iostream>
#include <iomanip>
#include <vector>
#include <cmath>
#include <random>
#include "core/Vec2.h"
#include "core/RigidBody.h"
#include "dynamics/Integrator.h"

struct Ball {
    RigidBody body;
    Vec2 color;  // Just for visual variety in output
    int id;
};

int main() {
    std::cout << "\n";
    std::cout << "╔══════════════════════════════════════════════════════════════════╗\n";
    std::cout << "║     ADVANCED PHYSICS ENGINE - RK4 INTEGRATION & MULTI-BODY      ║\n";
    std::cout << "╚══════════════════════════════════════════════════════════════════╝\n";
    std::cout << "\n";
    
    // Simulation parameters
    Vec2 gravity(0, -9.81);
    double groundY = 0.0;
    double dt = 0.01;
    double simTime = 3.0;
    
    // Create multiple balls with different properties
    std::vector<Ball> balls;
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> posDist(1.0, 8.0);
    std::uniform_real_distribution<> velDist(-3.0, 3.0);
    std::uniform_real_distribution<> restitutionDist(0.6, 0.95);
    
    for (int i = 0; i < 8; i++) {
        Ball ball;
        double restitution = restitutionDist(gen);
        ball.body = RigidBody(1.0, restitution);
        ball.body.position = Vec2(posDist(gen) - 4.0, posDist(gen));
        ball.body.velocity = Vec2(velDist(gen), 0);
        ball.id = i + 1;
        balls.push_back(ball);
    }
    
    // Add one special high-bounce ball
    Ball specialBall;
    specialBall.body = RigidBody(1.0, 0.95);
    specialBall.body.position = Vec2(0, 6);
    specialBall.body.velocity = Vec2(2, 0);
    specialBall.id = 99;
    balls.push_back(specialBall);
    
    std::cout << "SIMULATION PARAMETERS:\n";
    std::cout << "  • Gravity: 9.81 m/s²\n";
    std::cout << "  • Time step: " << dt << " seconds\n";
    std::cout << "  • Total objects: " << balls.size() << "\n";
    std::cout << "  • Integration method: Runge-Kutta 4\n";
    std::cout << "  • Features: Ground collision, restitution, multi-body\n";
    std::cout << "\n";
    std::cout << "Press Enter to start simulation...";
    std::cin.get();
    
    std::cout << "\n";
    std::cout << "RUNNING SIMULATION...\n";
    std::cout << "═══════════════════════════════════════════════════════════════════\n\n";
    
    // Track bounce counts
    std::vector<int> bounceCounts(balls.size(), 0);
    std::vector<bool> wasInAir(balls.size(), true);
    
    // Main simulation loop
    int frameCount = 0;
    for (double t = 0; t <= simTime; t += dt) {
        // Update each ball
        for (size_t i = 0; i < balls.size(); i++) {
            Ball& ball = balls[i];
            
            // Apply gravity and integrate using RK4
            Integrator::rk4(ball.body, gravity, dt);
            
            // Ground collision
            if (ball.body.position.y < groundY) {
                ball.body.position.y = groundY;
                ball.body.velocity.y = -ball.body.velocity.y * ball.body.restitution;
                
                if (wasInAir[i]) {
                    bounceCounts[i]++;
                    wasInAir[i] = false;
                }
                
                // Stop very small bounces
                if (std::abs(ball.body.velocity.y) < 0.2) {
                    ball.body.velocity.y = 0;
                }
            } else {
                wasInAir[i] = true;
            }
        }
        
        // Print every 0.2 seconds
        if (frameCount % 20 == 0) {
            std::cout << "t = " << std::fixed << std::setprecision(2) << t << "s\n";
            std::cout << "───────────────────────────────────────────────────────────\n";
            
            for (const auto& ball : balls) {
                std::string marker = (ball.id == 99) ? "★ " : "  ";
                std::cout << marker << "Ball " << std::setw(2) << ball.id << ": "
                          << "pos(" << std::setw(5) << std::setprecision(2) << ball.body.position.x
                          << ", " << std::setw(5) << ball.body.position.y << ")  "
                          << "vel(" << std::setw(5) << ball.body.velocity.x
                          << ", " << std::setw(5) << ball.body.velocity.y << ")";
                
                if (ball.body.position.y < 0.05 && std::abs(ball.body.velocity.y) < 0.3) {
                    std::cout << "  [RESTING]";
                } else if (ball.body.position.y < 0.1) {
                    std::cout << "  [BOUNCE]";
                }
                std::cout << "\n";
            }
            std::cout << "\n";
        }
        frameCount++;
    }
    
    // Final summary
    std::cout << "\n";
    std::cout << "═══════════════════════════════════════════════════════════════════\n";
    std::cout << "SIMULATION COMPLETE\n";
    std::cout << "═══════════════════════════════════════════════════════════════════\n";
    std::cout << "\nBounce Statistics:\n";
    for (size_t i = 0; i < balls.size(); i++) {
        std::string marker = (balls[i].id == 99) ? "★ " : "  ";
        std::cout << marker << "Ball " << std::setw(2) << balls[i].id << ": "
                  << bounceCounts[i] << " bounces  |  Restitution: " 
                  << balls[i].body.restitution << "\n";
    }
    std::cout << "\n";
    
    return 0;
}
