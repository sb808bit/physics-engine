#pragma once
#include <vector>
#include "../core/RigidBody.h"
#include "../core/Vec2.h"

struct Contact {
    RigidBody* bodyA;
    RigidBody* bodyB;
    Vec2 normal;
    double penetration;
    double restitution;
};

class CollisionDetector {
public:
    static void detectAndResolve(std::vector<RigidBody>& bodies, double dt);
    
private:
    static bool checkCollision(const RigidBody& a, const RigidBody& b, Contact& contact);
    static void resolveCollision(Contact& contact, double dt);
};
