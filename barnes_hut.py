#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Iterable


G = 1.0


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    mass: float = 1.0


@dataclass
class Bounds:
    cx: float
    cy: float
    half_size: float

    def contains(self, particle: Particle) -> bool:
        return (
            self.cx - self.half_size <= particle.x <= self.cx + self.half_size
            and self.cy - self.half_size <= particle.y <= self.cy + self.half_size
        )


@dataclass
class TreeStats:
    node_count: int = 0
    internal_count: int = 0
    leaf_count: int = 0
    occupied_leaves: int = 0
    max_depth: int = 0


class QuadNode:
    def __init__(self, bounds: Bounds):
        self.bounds = bounds
        self.mass = 0.0
        self.com_x = 0.0
        self.com_y = 0.0
        self.particle: Particle | None = None
        self.children: list[QuadNode] | None = None

    def insert(self, particle: Particle) -> bool:
        if not self.bounds.contains(particle):
            return False

        previous_mass = self.mass
        self.mass += particle.mass
        if self.mass > 0:
            self.com_x = (self.com_x * previous_mass + particle.x * particle.mass) / self.mass
            self.com_y = (self.com_y * previous_mass + particle.y * particle.mass) / self.mass

        if self.children is None and self.particle is None:
            self.particle = particle
            return True

        if self.children is None:
            existing = self.particle
            self.particle = None
            self.subdivide()
            assert existing is not None
            self._insert_into_children(existing)

        return self._insert_into_children(particle)

    def subdivide(self) -> None:
        quarter = self.bounds.half_size * 0.5
        cx, cy = self.bounds.cx, self.bounds.cy
        self.children = [
            QuadNode(Bounds(cx - quarter, cy - quarter, quarter)),
            QuadNode(Bounds(cx + quarter, cy - quarter, quarter)),
            QuadNode(Bounds(cx - quarter, cy + quarter, quarter)),
            QuadNode(Bounds(cx + quarter, cy + quarter, quarter)),
        ]

    def _insert_into_children(self, particle: Particle) -> bool:
        assert self.children is not None
        for child in self.children:
            if child.insert(particle):
                return True
        return False


def compute_bounds(particles: Iterable[Particle]) -> Bounds:
    particles = list(particles)
    if not particles:
        return Bounds(0.0, 0.0, 1.0)
    min_x = min(p.x for p in particles)
    max_x = max(p.x for p in particles)
    min_y = min(p.y for p in particles)
    max_y = max(p.y for p in particles)
    size = max(max_x - min_x, max_y - min_y)
    half_size = max(size * 0.55, 1.0)
    return Bounds((min_x + max_x) * 0.5, (min_y + max_y) * 0.5, half_size)


def build_tree(particles: Iterable[Particle]) -> QuadNode:
    particles = list(particles)
    root = QuadNode(compute_bounds(particles))
    for particle in particles:
        root.insert(particle)
    return root


def barnes_hut_acceleration(
    particle: Particle,
    node: QuadNode,
    theta: float = 0.6,
    softening: float = 0.08,
) -> tuple[float, float]:
    if node.mass == 0:
        return 0.0, 0.0

    if node.children is None and node.particle is particle:
        return 0.0, 0.0

    dx = node.com_x - particle.x
    dy = node.com_y - particle.y
    dist_sq = dx * dx + dy * dy + softening * softening
    dist = math.sqrt(dist_sq)
    width = node.bounds.half_size * 2.0

    if node.children is None or width / max(dist, 1e-9) < theta:
        inv_dist_cubed = 1.0 / (dist_sq * dist)
        scale = G * node.mass * inv_dist_cubed
        return dx * scale, dy * scale

    ax = 0.0
    ay = 0.0
    assert node.children is not None
    for child in node.children:
        cx, cy = barnes_hut_acceleration(particle, child, theta=theta, softening=softening)
        ax += cx
        ay += cy
    return ax, ay


def exact_accelerations(particles: list[Particle], softening: float = 0.08) -> list[tuple[float, float]]:
    accelerations = []
    for index, particle in enumerate(particles):
        ax = 0.0
        ay = 0.0
        for other_index, other in enumerate(particles):
            if index == other_index:
                continue
            dx = other.x - particle.x
            dy = other.y - particle.y
            dist_sq = dx * dx + dy * dy + softening * softening
            dist = math.sqrt(dist_sq)
            inv_dist_cubed = 1.0 / (dist_sq * dist)
            scale = G * other.mass * inv_dist_cubed
            ax += dx * scale
            ay += dy * scale
        accelerations.append((ax, ay))
    return accelerations


def barnes_hut_tree_and_accelerations(
    particles: list[Particle],
    theta: float = 0.6,
    softening: float = 0.08,
) -> tuple[QuadNode, list[tuple[float, float]]]:
    tree = build_tree(particles)
    accelerations = [barnes_hut_acceleration(p, tree, theta=theta, softening=softening) for p in particles]
    return tree, accelerations


def barnes_hut_accelerations(
    particles: list[Particle],
    theta: float = 0.6,
    softening: float = 0.08,
) -> list[tuple[float, float]]:
    _, accelerations = barnes_hut_tree_and_accelerations(particles, theta=theta, softening=softening)
    return accelerations


def advance_particles(particles: list[Particle], accelerations: list[tuple[float, float]], dt: float) -> None:
    for particle, (ax, ay) in zip(particles, accelerations):
        particle.vx += ax * dt
        particle.vy += ay * dt
        particle.x += particle.vx * dt
        particle.y += particle.vy * dt


def leapfrog_step(
    particles: list[Particle],
    dt: float,
    method: str = "barnes-hut",
    theta: float = 0.6,
    softening: float = 0.08,
) -> None:
    accelerations = (
        barnes_hut_accelerations(particles, theta=theta, softening=softening)
        if method == "barnes-hut"
        else exact_accelerations(particles, softening=softening)
    )
    advance_particles(particles, accelerations, dt)


def make_disc_particles(count: int, radius: float = 24.0, seed: int = 7) -> list[Particle]:
    rng = random.Random(seed)
    particles: list[Particle] = []
    for _ in range(count):
        angle = rng.random() * math.tau
        radial = radius * math.sqrt(rng.random())
        x = math.cos(angle) * radial
        y = math.sin(angle) * radial
        tangential = 0.65 + rng.random() * 0.45
        vx = -math.sin(angle) * tangential
        vy = math.cos(angle) * tangential
        particles.append(Particle(x=x, y=y, vx=vx, vy=vy, mass=0.5 + rng.random() * 2.0))
    return particles


def rms_force_error(exact: list[tuple[float, float]], approx: list[tuple[float, float]]) -> float:
    total = 0.0
    count = 0
    for (ex, ey), (ax, ay) in zip(exact, approx):
        dx = ex - ax
        dy = ey - ay
        total += dx * dx + dy * dy
        count += 1
    return math.sqrt(total / max(count, 1))


def position_rms_difference(left: list[Particle], right: list[Particle]) -> float:
    total = 0.0
    count = 0
    for a, b in zip(left, right):
        dx = a.x - b.x
        dy = a.y - b.y
        total += dx * dx + dy * dy
        count += 1
    return math.sqrt(total / max(count, 1))


def total_energy(particles: list[Particle], softening: float = 0.08) -> float:
    kinetic = sum(0.5 * particle.mass * (particle.vx * particle.vx + particle.vy * particle.vy) for particle in particles)
    potential = 0.0
    for index, particle in enumerate(particles):
        for other in particles[index + 1:]:
            dx = other.x - particle.x
            dy = other.y - particle.y
            distance = math.sqrt(dx * dx + dy * dy + softening * softening)
            potential -= G * particle.mass * other.mass / distance
    return kinetic + potential


def clone_particles(particles: Iterable[Particle]) -> list[Particle]:
    return [Particle(p.x, p.y, p.vx, p.vy, p.mass) for p in particles]


def collect_tree_stats(node: QuadNode, depth: int = 0) -> TreeStats:
    stats = TreeStats(node_count=1, max_depth=depth)

    if node.children is None:
        stats.leaf_count = 1
        if node.particle is not None:
            stats.occupied_leaves = 1
        return stats

    stats.internal_count = 1
    assert node.children is not None
    for child in node.children:
        child_stats = collect_tree_stats(child, depth + 1)
        stats.node_count += child_stats.node_count
        stats.internal_count += child_stats.internal_count
        stats.leaf_count += child_stats.leaf_count
        stats.occupied_leaves += child_stats.occupied_leaves
        stats.max_depth = max(stats.max_depth, child_stats.max_depth)
    return stats
