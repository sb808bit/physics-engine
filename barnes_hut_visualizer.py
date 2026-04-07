#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import deque
import math
import random
import time

import pygame

from barnes_hut import (
    Bounds,
    Particle,
    QuadNode,
    advance_particles,
    barnes_hut_tree_and_accelerations,
    clone_particles,
    collect_tree_stats,
    exact_accelerations,
    make_disc_particles,
    position_rms_difference,
    rms_force_error,
    total_energy,
)


WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 960
TOP_MARGIN = 112
BOTTOM_MARGIN = 246
PANEL_GAP = 22
PANEL_PADDING = 26

BG = (7, 12, 20)
BG_2 = (11, 18, 30)
PANEL = (11, 18, 29)
PANEL_BORDER = (45, 60, 88)
GRID = (27, 38, 58)
TEXT = (237, 245, 255)
TEXT_SOFT = (168, 180, 201)
GOLD = (242, 201, 119)
AMBER = (217, 146, 87)
BLUE = (133, 197, 255)
RED = (239, 125, 124)
TEAL = (124, 211, 196)


def make_twin_cluster_particles(count: int, seed: int = 21) -> list[Particle]:
    rng = random.Random(seed)
    particles: list[Particle] = []
    half = max(8, count // 2)
    for side in (-1, 1):
        for _ in range(half):
            angle = rng.random() * math.tau
            radius = 7.0 * math.sqrt(rng.random())
            x = side * 12.0 + math.cos(angle) * radius
            y = math.sin(angle) * radius * 0.9
            swirl = 0.72 + rng.random() * 0.32
            drift = 0.22 * side
            vx = -math.sin(angle) * swirl + drift
            vy = math.cos(angle) * swirl
            particles.append(Particle(x=x, y=y, vx=vx, vy=vy, mass=0.7 + rng.random() * 1.4))
    return particles


def make_shear_particles(count: int, seed: int = 33) -> list[Particle]:
    rng = random.Random(seed)
    particles: list[Particle] = []
    for _ in range(count):
        x = rng.uniform(-20.0, 20.0)
        y = rng.uniform(-14.0, 14.0)
        vx = -0.045 * y + rng.uniform(-0.08, 0.08)
        vy = 0.03 * x + rng.uniform(-0.08, 0.08)
        particles.append(Particle(x=x, y=y, vx=vx, vy=vy, mass=0.5 + rng.random() * 1.1))
    return particles


SCENARIOS = [
    ("Disc Swirl", lambda: make_disc_particles(340, radius=18.0, seed=7)),
    ("Twin Cluster", lambda: make_twin_cluster_particles(480, seed=21)),
    ("Shear Field", lambda: make_shear_particles(720, seed=33)),
]


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def energy_drift_percent(current: float, baseline: float) -> float:
    if abs(baseline) < 1e-9:
        return 0.0
    return ((current - baseline) / abs(baseline)) * 100.0


def draw_round_rect(surface: pygame.Surface, rect: pygame.Rect, fill: tuple[int, int, int], border: tuple[int, int, int]) -> None:
    pygame.draw.rect(surface, fill, rect, border_radius=26)
    pygame.draw.rect(surface, border, rect, width=1, border_radius=26)


class BarnesHutLab:
    def __init__(self, scenario_index: int, theta: float):
        self.scenario_index = scenario_index
        self.theta = theta
        self.softening = 0.08
        self.dt = 1.0 / 120.0
        self.paused = False
        self.show_tree = True
        self.show_trails = True
        self.show_help = True
        self.frame_count = 0
        self.exact_force_ms = 0.0
        self.bh_force_ms = 0.0
        self.force_rms = 0.0
        self.position_rms = 0.0
        self.exact_energy = 0.0
        self.bh_energy = 0.0
        self.baseline_energy = 0.0
        self.tree_stats = collect_tree_stats(QuadNode(Bounds(0.0, 0.0, 1.0)))
        self.tree: QuadNode | None = None
        self.sample_indices: list[int] = []
        self.exact_trails: dict[int, deque[tuple[float, float]]] = {}
        self.bh_trails: dict[int, deque[tuple[float, float]]] = {}
        self.reset()

    @property
    def scenario_name(self) -> str:
        return SCENARIOS[self.scenario_index][0]

    def reset(self) -> None:
        particles = SCENARIOS[self.scenario_index][1]()
        self.exact_particles = clone_particles(particles)
        self.bh_particles = clone_particles(particles)
        self.baseline_energy = total_energy(particles, softening=self.softening)
        self.exact_energy = self.baseline_energy
        self.bh_energy = self.baseline_energy
        self.frame_count = 0
        self.exact_force_ms = 0.0
        self.bh_force_ms = 0.0
        self.force_rms = 0.0
        self.position_rms = 0.0
        self.tree = None
        self.tree_stats = collect_tree_stats(QuadNode(Bounds(0.0, 0.0, 1.0)))

        count = len(particles)
        stride = max(1, count // 8)
        self.sample_indices = list(range(0, count, stride))[:8]
        self.exact_trails = {index: deque(maxlen=42) for index in self.sample_indices}
        self.bh_trails = {index: deque(maxlen=42) for index in self.sample_indices}
        self._append_trails()

    def cycle_scenario(self, direction: int = 1) -> None:
        self.scenario_index = (self.scenario_index + direction) % len(SCENARIOS)
        self.reset()

    def nudge_theta(self, delta: float) -> None:
        self.theta = clamp(self.theta + delta, 0.25, 1.2)

    def _append_trails(self) -> None:
        for index in self.sample_indices:
            exact = self.exact_particles[index]
            approx = self.bh_particles[index]
            self.exact_trails[index].append((exact.x, exact.y))
            self.bh_trails[index].append((approx.x, approx.y))

    def step(self) -> None:
        if self.paused:
            return

        exact_start = time.perf_counter()
        exact_acc = exact_accelerations(self.exact_particles, softening=self.softening)
        advance_particles(self.exact_particles, exact_acc, self.dt)
        self.exact_force_ms = (time.perf_counter() - exact_start) * 1000.0

        bh_start = time.perf_counter()
        self.tree, bh_acc = barnes_hut_tree_and_accelerations(
            self.bh_particles,
            theta=self.theta,
            softening=self.softening,
        )
        advance_particles(self.bh_particles, bh_acc, self.dt)
        self.bh_force_ms = (time.perf_counter() - bh_start) * 1000.0
        self.tree_stats = collect_tree_stats(self.tree)

        self.frame_count += 1
        self._append_trails()

        if self.frame_count % 10 == 0:
            self.position_rms = position_rms_difference(self.exact_particles, self.bh_particles)
            self.exact_energy = total_energy(self.exact_particles, softening=self.softening)
            self.bh_energy = total_energy(self.bh_particles, softening=self.softening)

        if self.frame_count % 14 == 0:
            exact_on_bh = exact_accelerations(self.bh_particles, softening=self.softening)
            self.force_rms = rms_force_error(exact_on_bh, bh_acc)

    def render(self, surface: pygame.Surface, fonts: dict[str, pygame.font.Font]) -> None:
        surface.fill(BG)
        draw_background(surface)

        header = pygame.Rect(18, 18, WINDOW_WIDTH - 36, 76)
        draw_round_rect(surface, header, PANEL, PANEL_BORDER)
        left_panel = pygame.Rect(18, TOP_MARGIN, (WINDOW_WIDTH - 58) // 2, WINDOW_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN)
        right_panel = pygame.Rect(left_panel.right + PANEL_GAP, TOP_MARGIN, left_panel.width, left_panel.height)
        bottom = pygame.Rect(18, WINDOW_HEIGHT - BOTTOM_MARGIN + 18, WINDOW_WIDTH - 36, BOTTOM_MARGIN - 36)
        draw_round_rect(surface, left_panel, PANEL, PANEL_BORDER)
        draw_round_rect(surface, right_panel, PANEL, PANEL_BORDER)
        draw_round_rect(surface, bottom, PANEL, PANEL_BORDER)

        shared_extent = max(compute_extent(self.exact_particles), compute_extent(self.bh_particles))
        render_header(surface, header, fonts, self)
        render_world_panel(surface, left_panel, fonts, "Exact O(N²) Force Pass", "Direct pairwise acceleration on every frame.", self.exact_particles, self.exact_trails, None, shared_extent, self.show_trails)
        render_world_panel(surface, right_panel, fonts, "Barnes-Hut O(N log N) Approximation", "Grouped center-of-mass interactions with optional quadtree overlay.", self.bh_particles, self.bh_trails, self.tree if self.show_tree else None, shared_extent, self.show_trails)
        render_bottom_hud(surface, bottom, fonts, self)


def draw_background(surface: pygame.Surface) -> None:
    width, height = surface.get_size()
    glow = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255, 131, 120, 20), (int(width * 0.18), int(height * 0.18)), 240)
    pygame.draw.circle(glow, (242, 201, 119, 18), (int(width * 0.82), int(height * 0.22)), 180)
    pygame.draw.circle(glow, (133, 197, 255, 15), (int(width * 0.72), int(height * 0.78)), 220)
    surface.blit(glow, (0, 0))


def render_header(surface: pygame.Surface, rect: pygame.Rect, fonts: dict[str, pygame.font.Font], lab: BarnesHutLab) -> None:
    surface.blit(fonts["eyebrow"].render("Barnes-Hut Lab", True, GOLD), (rect.x + 24, rect.y + 16))
    surface.blit(fonts["title"].render("Exact vs Barnes-Hut Gravity", True, TEXT), (rect.x + 24, rect.y + 34))

    meta = [
        f"Scenario: {lab.scenario_name}",
        f"N = {len(lab.exact_particles)}",
        f"Theta = {lab.theta:.2f}",
    ]
    x = rect.right - 24
    for label in reversed(meta):
        pill = fonts["pill"].render(label, True, TEXT)
        box = pill.get_rect()
        box.width += 22
        box.height += 12
        box.top = rect.y + 18
        box.right = x
        pygame.draw.rect(surface, BG_2, box, border_radius=14)
        pygame.draw.rect(surface, PANEL_BORDER, box, width=1, border_radius=14)
        surface.blit(pill, (box.x + 11, box.y + 6))
        x = box.x - 10


def render_world_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    fonts: dict[str, pygame.font.Font],
    title: str,
    subtitle: str,
    particles: list[Particle],
    trails: dict[int, deque[tuple[float, float]]],
    tree: QuadNode | None,
    extent: float,
    show_trails: bool,
) -> None:
    surface.blit(fonts["section"].render(title, True, TEXT), (rect.x + 20, rect.y + 16))
    surface.blit(fonts["body"].render(subtitle, True, TEXT_SOFT), (rect.x + 20, rect.y + 46))

    view = pygame.Rect(rect.x + 18, rect.y + 80, rect.width - 36, rect.height - 98)
    pygame.draw.rect(surface, BG, view, border_radius=18)
    pygame.draw.rect(surface, PANEL_BORDER, view, width=1, border_radius=18)
    draw_world_grid(surface, view)

    if tree is not None:
        overlay = pygame.Surface((view.width, view.height), pygame.SRCALPHA)
        draw_tree_overlay(overlay, view, tree, extent)
        surface.blit(overlay, view.topleft)
    if show_trails:
        draw_trails(surface, view, trails, extent)
    draw_particles(surface, view, particles, extent)


def draw_world_grid(surface: pygame.Surface, rect: pygame.Rect) -> None:
    for index in range(1, 8):
        x = rect.x + rect.width * index / 8.0
        y = rect.y + rect.height * index / 8.0
        pygame.draw.line(surface, GRID, (x, rect.y + 10), (x, rect.bottom - 10), 1)
        pygame.draw.line(surface, GRID, (rect.x + 10, y), (rect.right - 10, y), 1)


def compute_extent(particles: list[Particle]) -> float:
    if not particles:
        return 20.0
    max_axis = max(max(abs(p.x), abs(p.y)) for p in particles)
    return max(18.0, max_axis * 1.2 + 2.0)


def world_to_screen(rect: pygame.Rect, extent: float, x: float, y: float) -> tuple[float, float]:
    scale = min(rect.width, rect.height) / (extent * 2.0)
    sx = rect.centerx + x * scale
    sy = rect.centery - y * scale
    return sx, sy


def draw_tree_overlay(overlay: pygame.Surface, rect: pygame.Rect, node: QuadNode, extent: float, depth: int = 0) -> None:
    color = (
        min(255, 74 + depth * 10),
        min(255, 92 + depth * 6),
        min(255, 130 + depth * 4),
    )
    alpha = max(24, 76 - depth * 8)
    node_rect = pygame.Rect(0, 0, 1, 1)
    left = node.bounds.cx - node.bounds.half_size
    right = node.bounds.cx + node.bounds.half_size
    top = node.bounds.cy + node.bounds.half_size
    bottom = node.bounds.cy - node.bounds.half_size
    sx0, sy0 = world_to_screen(rect, extent, left, top)
    sx1, sy1 = world_to_screen(rect, extent, right, bottom)
    node_rect.x = int(min(sx0, sx1) - rect.x)
    node_rect.y = int(min(sy0, sy1) - rect.y)
    node_rect.width = max(1, int(abs(sx1 - sx0)))
    node_rect.height = max(1, int(abs(sy1 - sy0)))
    pygame.draw.rect(overlay, (*color, alpha), node_rect, width=1, border_radius=4)
    if node.children is not None:
        for child in node.children:
            draw_tree_overlay(overlay, rect, child, extent, depth + 1)


def draw_particles(surface: pygame.Surface, rect: pygame.Rect, particles: list[Particle], extent: float) -> None:
    for particle in particles:
        speed = math.hypot(particle.vx, particle.vy)
        radius = 1.8 + clamp(speed * 0.75, 0.0, 2.2)
        sx, sy = world_to_screen(rect, extent, particle.x, particle.y)
        color = (
            int(clamp(110 + speed * 52, 0, 255)),
            int(clamp(150 + speed * 38, 0, 255)),
            int(clamp(200 + speed * 22, 0, 255)),
        )
        pygame.draw.circle(surface, color, (int(sx), int(sy)), int(radius))


def draw_trails(surface: pygame.Surface, rect: pygame.Rect, trails: dict[int, deque[tuple[float, float]]], extent: float) -> None:
    for trail in trails.values():
        if len(trail) < 2:
            continue
        points = [world_to_screen(rect, extent, x, y) for x, y in trail]
        for index in range(1, len(points)):
            alpha = int(24 + (index / len(points)) * 90)
            overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            x0, y0 = points[index - 1]
            x1, y1 = points[index]
            pygame.draw.line(
                overlay,
                (242, 201, 119, alpha),
                (x0 - rect.x, y0 - rect.y),
                (x1 - rect.x, y1 - rect.y),
                2,
            )
            surface.blit(overlay, rect.topleft)


def render_bottom_hud(surface: pygame.Surface, rect: pygame.Rect, fonts: dict[str, pygame.font.Font], lab: BarnesHutLab) -> None:
    surface.blit(fonts["eyebrow"].render("Comparison + Controls", True, GOLD), (rect.x + 24, rect.y + 14))

    left = pygame.Rect(rect.x + 20, rect.y + 44, rect.width * 0.33 - 26, rect.height - 62)
    mid = pygame.Rect(left.right + 16, left.y, rect.width * 0.31 - 22, left.height)
    right = pygame.Rect(mid.right + 16, left.y, rect.right - 20 - (mid.right + 16), left.height)

    for panel in (left, mid, right):
        pygame.draw.rect(surface, BG, panel, border_radius=18)
        pygame.draw.rect(surface, PANEL_BORDER, panel, width=1, border_radius=18)

    render_metrics_block(surface, left, fonts, lab)
    render_drift_block(surface, mid, fonts, lab)
    render_controls_block(surface, right, fonts)


def render_metrics_block(surface: pygame.Surface, rect: pygame.Rect, fonts: dict[str, pygame.font.Font], lab: BarnesHutLab) -> None:
    surface.blit(fonts["section"].render("Live Metrics", True, TEXT), (rect.x + 16, rect.y + 14))
    rows = [
        ("Exact force pass", f"{lab.exact_force_ms:0.2f} ms"),
        ("Barnes-Hut pass", f"{lab.bh_force_ms:0.2f} ms"),
        ("Loop speedup", f"{lab.exact_force_ms / max(lab.bh_force_ms, 1e-6):0.2f}x"),
        ("Force RMS error", f"{lab.force_rms:0.4f}"),
        ("Position divergence", f"{lab.position_rms:0.3f}"),
    ]
    render_key_value_rows(surface, rect, fonts, rows, start_y=48)


def render_drift_block(surface: pygame.Surface, rect: pygame.Rect, fonts: dict[str, pygame.font.Font], lab: BarnesHutLab) -> None:
    surface.blit(fonts["section"].render("Tree + Energy", True, TEXT), (rect.x + 16, rect.y + 14))
    rows = [
        ("Nodes / depth", f"{lab.tree_stats.node_count} / {lab.tree_stats.max_depth}"),
        ("Occupied leaves", f"{lab.tree_stats.occupied_leaves}"),
        ("Exact drift", f"{energy_drift_percent(lab.exact_energy, lab.baseline_energy):+0.2f}%"),
        ("Barnes-Hut drift", f"{energy_drift_percent(lab.bh_energy, lab.baseline_energy):+0.2f}%"),
        ("Quadtree overlay", "On" if lab.show_tree else "Off"),
    ]
    render_key_value_rows(surface, rect, fonts, rows, start_y=48)


def render_controls_block(surface: pygame.Surface, rect: pygame.Rect, fonts: dict[str, pygame.font.Font]) -> None:
    surface.blit(fonts["section"].render("Keys", True, TEXT), (rect.x + 16, rect.y + 14))
    lines = [
        "1 / 2 / 3  switch scenario",
        "[ / ]      decrease / increase theta",
        "Q          toggle quadtree overlay",
        "T          toggle sample trails",
        "H          toggle this help card",
        "Space      pause / resume",
        "S          single simulation step",
        "R          reset current scenario",
    ]
    for index, line in enumerate(lines):
        surface.blit(fonts["body"].render(line, True, TEXT_SOFT), (rect.x + 16, rect.y + 46 + index * 22))


def render_key_value_rows(surface: pygame.Surface, rect: pygame.Rect, fonts: dict[str, pygame.font.Font], rows, start_y: int) -> None:
    for index, (label, value) in enumerate(rows):
        y = rect.y + start_y + index * 22
        surface.blit(fonts["body"].render(label, True, TEXT_SOFT), (rect.x + 16, y))
        value_surface = fonts["body"].render(value, True, TEXT)
        surface.blit(value_surface, (rect.right - 16 - value_surface.get_width(), y))


def build_fonts() -> dict[str, pygame.font.Font]:
    return {
        "eyebrow": pygame.font.SysFont("SF Pro Display", 16, bold=True),
        "title": pygame.font.SysFont("SF Pro Display", 34, bold=True),
        "section": pygame.font.SysFont("SF Pro Display", 22, bold=True),
        "body": pygame.font.SysFont("SF Pro Text", 18),
        "pill": pygame.font.SysFont("SF Pro Text", 15, bold=True),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactive exact-vs-Barnes-Hut N-body lab.")
    parser.add_argument("--theta", type=float, default=0.6, help="Initial Barnes-Hut theta")
    parser.add_argument("--scenario", type=int, default=1, help="Scenario index: 1 disc, 2 twin cluster, 3 shear field")
    args = parser.parse_args()

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Barnes-Hut Lab")
    clock = pygame.time.Clock()
    fonts = build_fonts()
    lab = BarnesHutLab(max(0, min(len(SCENARIOS) - 1, args.scenario - 1)), args.theta)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    lab.paused = not lab.paused
                elif event.key == pygame.K_q:
                    lab.show_tree = not lab.show_tree
                elif event.key == pygame.K_t:
                    lab.show_trails = not lab.show_trails
                    if not lab.show_trails:
                        for trail in lab.exact_trails.values():
                            trail.clear()
                        for trail in lab.bh_trails.values():
                            trail.clear()
                        lab._append_trails()
                elif event.key == pygame.K_h:
                    lab.show_help = not lab.show_help
                elif event.key == pygame.K_r:
                    lab.reset()
                elif event.key == pygame.K_s:
                    lab.step()
                elif event.key == pygame.K_LEFTBRACKET:
                    lab.nudge_theta(-0.05)
                elif event.key == pygame.K_RIGHTBRACKET:
                    lab.nudge_theta(0.05)
                elif event.key == pygame.K_1:
                    lab.scenario_index = 0
                    lab.reset()
                elif event.key == pygame.K_2:
                    lab.scenario_index = 1
                    lab.reset()
                elif event.key == pygame.K_3:
                    lab.scenario_index = 2
                    lab.reset()

        lab.step()
        lab.render(screen, fonts)
        if not lab.show_help:
            mask = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(mask, (7, 12, 20, 180), pygame.Rect(18, WINDOW_HEIGHT - BOTTOM_MARGIN + 18, WINDOW_WIDTH - 36, BOTTOM_MARGIN - 36), border_radius=26)
            screen.blit(mask, (0, 0))
            screen.blit(fonts["body"].render("Press H to show controls.", True, TEXT_SOFT), (42, WINDOW_HEIGHT - 108))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
