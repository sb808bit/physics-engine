#include "Integrator.h"

Vec2 Integrator::computeAcceleration(const RigidBody& body, const Vec2& forces) {
    return forces * body.inverseMass;
}

void Integrator::euler(RigidBody& body, const Vec2& forces, double dt) {
    Vec2 acceleration = computeAcceleration(body, forces);
    body.velocity += acceleration * dt;
    body.position += body.velocity * dt;
}

void Integrator::rk4(RigidBody& body, const Vec2& forces, double dt) {
    // Store initial state
    Vec2 initialPos = body.position;
    Vec2 initialVel = body.velocity;
    
    // k1: evaluate at start
    Vec2 a1 = computeAcceleration(body, forces);
    Vec2 v1 = body.velocity;
    
    // k2: evaluate at midpoint using k1
    Vec2 v2 = initialVel + a1 * (dt * 0.5);
    Vec2 p2 = initialPos + v1 * (dt * 0.5);
    RigidBody tempBody = body;
    tempBody.position = p2;
    tempBody.velocity = v2;
    Vec2 a2 = computeAcceleration(tempBody, forces);
    
    // k3: evaluate at midpoint using k2
    Vec2 v3 = initialVel + a2 * (dt * 0.5);
    Vec2 p3 = initialPos + v2 * (dt * 0.5);
    tempBody.position = p3;
    tempBody.velocity = v3;
    Vec2 a3 = computeAcceleration(tempBody, forces);
    
    // k4: evaluate at end using k3
    Vec2 v4 = initialVel + a3 * dt;
    Vec2 p4 = initialPos + v3 * dt;
    tempBody.position = p4;
    tempBody.velocity = v4;
    Vec2 a4 = computeAcceleration(tempBody, forces);
    
    // Weighted average of slopes
    Vec2 avgAccel = (a1 + a2 * 2.0 + a3 * 2.0 + a4) / 6.0;
    Vec2 avgVel = (v1 + v2 * 2.0 + v3 * 2.0 + v4) / 6.0;
    
    // Update
    body.velocity = initialVel + avgAccel * dt;
    body.position = initialPos + avgVel * dt;
}
