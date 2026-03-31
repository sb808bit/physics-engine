#pragma once
#include "../core/RigidBody.h"
#include "../core/Vec2.h"

class Integrator {
public:
    // Euler integration (first-order)
    static void euler(RigidBody& body, const Vec2& forces, double dt);
    
    // Runge-Kutta 4 integration (fourth-order, more accurate)
    static void rk4(RigidBody& body, const Vec2& forces, double dt);
    
private:
    static Vec2 computeAcceleration(const RigidBody& body, const Vec2& forces);
};
