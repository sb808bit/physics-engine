#include "CollisionDetector.h"
#include <cmath>

bool CollisionDetector::checkCollision(const RigidBody& a, const RigidBody& b, Contact& contact) {
    // Simple sphere-sphere collision (circle-circle in 2D)
    Vec2 delta = b.position - a.position;
    double distance = delta.magnitude();
    double minDistance = 0.5; // Assuming radius = 0.5 for both balls
    
    if (distance < minDistance) {
        // Collision detected
        contact.bodyA = const_cast<RigidBody*>(&a);
        contact.bodyB = const_cast<RigidBody*>(&b);
        contact.normal = delta.normalized();
        contact.penetration = minDistance - distance;
        contact.restitution = (a.restitution + b.restitution) / 2.0;
        return true;
    }
    return false;
}

void CollisionDetector::resolveCollision(Contact& contact, double /*dt*/) {
    RigidBody* a = contact.bodyA;
    RigidBody* b = contact.bodyB;
    
    // Relative velocity
    Vec2 relativeVel = b->velocity - a->velocity;
    double velAlongNormal = relativeVel.dot(contact.normal);
    
    // Don't resolve if moving apart
    if (velAlongNormal > 0) return;
    
    // Calculate impulse scalar
    double e = contact.restitution;
    double invMassSum = a->inverseMass + b->inverseMass;
    if (invMassSum == 0) return;
    
    double j = -(1 + e) * velAlongNormal / invMassSum;
    Vec2 impulse = contact.normal * j;
    
    // Apply impulse
    a->velocity -= impulse * a->inverseMass;
    b->velocity += impulse * b->inverseMass;
    
    // Position correction to prevent sinking
    double correction = contact.penetration / (invMassSum * 2.0);
    Vec2 correctionVec = contact.normal * correction;
    a->position -= correctionVec * a->inverseMass;
    b->position += correctionVec * b->inverseMass;
}

void CollisionDetector::detectAndResolve(std::vector<RigidBody>& bodies, double dt) {
    // Check all pairs
    for (size_t i = 0; i < bodies.size(); i++) {
        for (size_t j = i + 1; j < bodies.size(); j++) {
            Contact contact;
            if (checkCollision(bodies[i], bodies[j], contact)) {
                resolveCollision(contact, dt);
            }
        }
    }
}
