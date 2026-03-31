#!/usr/bin/env python3
import pygame
import sys
import math
import random
from dataclasses import dataclass
from enum import Enum

class GravityDirection(Enum):
    DOWN = 0
    UP = 1
    LEFT = 2
    RIGHT = 3

@dataclass
class Ball:
    x: float
    y: float
    vx: float
    vy: float
    restitution: float
    radius: float
    color: tuple
    mass: float = 1.0

# Simulation parameters
WIDTH, HEIGHT = 1200, 700
GROUND_Y = HEIGHT - 50
GRAVITY_STRENGTH = 500.0
DT = 1/60.0

# Colors
BG_COLOR = (20, 20, 30)
GROUND_COLOR = (60, 60, 80)
TEXT_COLOR = (200, 200, 200)
SLIDER_COLOR = (100, 100, 150)
SLIDER_HANDLE = (200, 200, 250)

class Slider:
    def __init__(self, x, y, width, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, 10)
        self.handle_radius = 8
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.dragging = False
        
    def get_handle_x(self):
        t = (self.value - self.min_val) / (self.max_val - self.min_val)
        return self.rect.x + t * self.rect.width
        
    def update(self, mouse_x, mouse_y, mouse_pressed):
        handle_x = self.get_handle_x()
        handle_rect = pygame.Rect(handle_x - self.handle_radius, 
                                   self.rect.y - self.handle_radius,
                                   self.handle_radius * 2, 
                                   self.handle_radius * 2)
        
        if not self.dragging and mouse_pressed[0] and handle_rect.collidepoint(mouse_x, mouse_y):
            self.dragging = True
            
        if self.dragging:
            if not mouse_pressed[0]:
                self.dragging = False
            else:
                t = (mouse_x - self.rect.x) / self.rect.width
                t = max(0, min(1, t))
                self.value = self.min_val + t * (self.max_val - self.min_val)
                
    def draw(self, screen, font):
        pygame.draw.rect(screen, SLIDER_COLOR, self.rect)
        handle_x = self.get_handle_x()
        pygame.draw.circle(screen, SLIDER_HANDLE, (int(handle_x), self.rect.y + 5), self.handle_radius)
        
        label_text = font.render(f"{self.label}: {self.value:.1f}", True, TEXT_COLOR)
        screen.blit(label_text, (self.rect.x, self.rect.y - 25))

def create_balls():
    balls = []
    for i in range(12):
        balls.append(Ball(
            x=random.uniform(80, WIDTH-80),
            y=random.uniform(80, GROUND_Y-80),
            vx=random.uniform(-200, 200),
            vy=random.uniform(-200, 0),
            restitution=random.uniform(0.6, 0.95),
            radius=random.uniform(8, 16),
            color=(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        ))
    
    balls.append(Ball(
        x=WIDTH//2, y=GROUND_Y-100,
        vx=150, vy=-300,
        restitution=0.98,
        radius=20,
        color=(255, 100, 100)
    ))
    return balls

def apply_gravity(ball, direction, strength, dt):
    if direction == GravityDirection.DOWN:
        ball.vy += strength * dt
    elif direction == GravityDirection.UP:
        ball.vy -= strength * dt
    elif direction == GravityDirection.LEFT:
        ball.vx -= strength * dt
    elif direction == GravityDirection.RIGHT:
        ball.vx += strength * dt

def check_bounds(ball, width, height, ground_y):
    if ball.y + ball.radius > ground_y:
        ball.y = ground_y - ball.radius
        ball.vy = -ball.vy * ball.restitution
        if abs(ball.vy) < 15:
            ball.vy = 0
    
    if ball.x - ball.radius < 0:
        ball.x = ball.radius
        ball.vx = -ball.vx * ball.restitution
    if ball.x + ball.radius > width:
        ball.x = width - ball.radius
        ball.vx = -ball.vx * ball.restitution
    
    if ball.y - ball.radius < 0:
        ball.y = ball.radius
        ball.vy = -ball.vy * ball.restitution

# Initialize
balls = create_balls()
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Physics Engine - Interactive Demo")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)
big_font = pygame.font.Font(None, 36)

gravity_slider = Slider(20, HEIGHT - 80, 300, 0, 1200, GRAVITY_STRENGTH, "Gravity Strength")
gravity_direction = GravityDirection.DOWN
direction_names = ["DOWN", "UP", "LEFT", "RIGHT"]

dragging_ball = None
drag_offset_x = 0
drag_offset_y = 0
drag_last_x = 0
drag_last_y = 0
throw_velocity = None

# Track window position via SDL
last_window_x = 0
last_window_y = 0
try:
    info = pygame.display.get_wm_info()
    if 'window' in info:
        import ctypes
        from ctypes import wintypes
        # macOS alternative - we'll track via mouse and window events differently
except:
    pass

# Alternative: track via mouse movement relative to screen
# We'll use a simpler approach: detect window movement by checking if the window 
# position changed using SDL's get window position (requires SDL2)
window_delta_x = 0
window_delta_y = 0
last_window_x, last_window_y = 0, 0
first_frame = True

running = True
while running:
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()
    
    # Track window movement - get position via SDL (works on all platforms)
    try:
        # Pygame doesn't have direct get_position, but we can use SDL's GetWindowPosition
        import pygame._sdl2 as sdl2
        win = sdl2.Window.from_display_module()
        current_window_x, current_window_y = win.position
    except:
        # Fallback: use a dummy value - window movement won't work
        current_window_x, current_window_y = 0, 0
    
    if not first_frame:
        window_delta_x = current_window_x - last_window_x
        window_delta_y = current_window_y - last_window_y
        
        if abs(window_delta_x) > 0 or abs(window_delta_y) > 0:
            # Apply impulse to balls based on window movement
            for ball in balls:
                if ball is not dragging_ball:
                    ball.vx += window_delta_x * 2.0
                    ball.vy += window_delta_y * 2.0
    
    last_window_x, last_window_y = current_window_x, current_window_y
    first_frame = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                balls.append(Ball(
                    x=random.uniform(50, WIDTH-50),
                    y=random.uniform(50, GROUND_Y-50),
                    vx=random.uniform(-200, 200),
                    vy=random.uniform(-200, 0),
                    restitution=random.uniform(0.5, 0.95),
                    radius=random.uniform(8, 16),
                    color=(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
                ))
            elif event.key == pygame.K_r:
                balls = create_balls()
            elif event.key == pygame.K_c:
                balls.clear()
            elif event.key == pygame.K_UP:
                gravity_slider.value = min(gravity_slider.max_val, gravity_slider.value + 20)
            elif event.key == pygame.K_DOWN:
                gravity_slider.value = max(gravity_slider.min_val, gravity_slider.value - 20)
            elif event.key == pygame.K_w:
                gravity_direction = GravityDirection.UP
            elif event.key == pygame.K_s:
                gravity_direction = GravityDirection.DOWN
            elif event.key == pygame.K_a:
                gravity_direction = GravityDirection.LEFT
            elif event.key == pygame.K_d:
                gravity_direction = GravityDirection.RIGHT
    
    GRAVITY_STRENGTH = gravity_slider.value
    
    # Mouse dragging with throw
    if mouse_pressed[0] and not gravity_slider.dragging:
        if dragging_ball is None:
            for ball in balls:
                dx = ball.x - mouse_x
                dy = ball.y - mouse_y
                if math.hypot(dx, dy) < ball.radius:
                    dragging_ball = ball
                    drag_offset_x = ball.x - mouse_x
                    drag_offset_y = ball.y - mouse_y
                    drag_last_x = mouse_x
                    drag_last_y = mouse_y
                    break
        else:
            mouse_dx = mouse_x - drag_last_x
            mouse_dy = mouse_y - drag_last_y
            drag_last_x = mouse_x
            drag_last_y = mouse_y
            
            dragging_ball.x = mouse_x + drag_offset_x
            dragging_ball.y = mouse_y + drag_offset_y
            dragging_ball.vx = 0
            dragging_ball.vy = 0
            
            throw_velocity = (mouse_dx / DT, mouse_dy / DT)
            
            if dragging_ball.x - dragging_ball.radius < 0:
                dragging_ball.x = dragging_ball.radius
            if dragging_ball.x + dragging_ball.radius > WIDTH:
                dragging_ball.x = WIDTH - dragging_ball.radius
            if dragging_ball.y - dragging_ball.radius < 0:
                dragging_ball.y = dragging_ball.radius
            if dragging_ball.y + dragging_ball.radius > GROUND_Y:
                dragging_ball.y = GROUND_Y - dragging_ball.radius
    else:
        if dragging_ball is not None and throw_velocity is not None:
            dragging_ball.vx = throw_velocity[0]
            dragging_ball.vy = throw_velocity[1]
        dragging_ball = None
        throw_velocity = None
    
    gravity_slider.update(mouse_x, mouse_y, mouse_pressed)
    
    # Physics update
    for ball in balls:
        if ball is dragging_ball:
            continue
        
        apply_gravity(ball, gravity_direction, GRAVITY_STRENGTH, DT)
        ball.x += ball.vx * DT
        ball.y += ball.vy * DT
        check_bounds(ball, WIDTH, HEIGHT, GROUND_Y)
    
    # Sphere-sphere collisions
    for i in range(len(balls)):
        if balls[i] is dragging_ball:
            continue
        for j in range(i+1, len(balls)):
            if balls[j] is dragging_ball:
                continue
            a = balls[i]
            b = balls[j]
            dx = a.x - b.x
            dy = a.y - b.y
            dist = math.hypot(dx, dy)
            min_dist = a.radius + b.radius
            
            if dist < min_dist:
                overlap = min_dist - dist
                angle = math.atan2(dy, dx)
                nx = math.cos(angle)
                ny = math.sin(angle)
                
                a.x += nx * overlap * 0.5
                a.y += ny * overlap * 0.5
                b.x -= nx * overlap * 0.5
                b.y -= ny * overlap * 0.5
                
                vrelx = a.vx - b.vx
                vrely = a.vy - b.vy
                dot = vrelx * nx + vrely * ny
                e = (a.restitution + b.restitution) / 2
                
                if dot < 0:
                    imp = (1 + e) * dot / 2
                    a.vx -= imp * nx
                    a.vy -= imp * ny
                    b.vx += imp * nx
                    b.vy += imp * ny
    
    # Draw
    screen.fill(BG_COLOR)
    pygame.draw.rect(screen, GROUND_COLOR, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    
    for ball in balls:
        pygame.draw.circle(screen, ball.color, (int(ball.x), int(ball.y)), int(ball.radius))
        if ball is dragging_ball:
            pygame.draw.circle(screen, (255, 255, 255), (int(ball.x), int(ball.y)), int(ball.radius) + 4, 3)
        elif ball.restitution > 0.95:
            pygame.draw.circle(screen, (255, 255, 255), (int(ball.x), int(ball.y)), int(ball.radius) + 2, 2)
    
    gravity_slider.draw(screen, font)
    
    dir_text = big_font.render(f"Gravity: {direction_names[gravity_direction.value]}", True, (150, 200, 255))
    screen.blit(dir_text, (WIDTH // 2 - 100, HEIGHT - 60))
    
    info_lines = [
        f"Balls: {len(balls)}",
        "SPACE: Add ball | R: Reset | C: Clear all",
        "WASD: Change gravity direction",
        "Drag window to shake balls!",
        "Click and drag balls to throw them"
    ]
    for i, line in enumerate(info_lines):
        text = font.render(line, True, TEXT_COLOR)
        screen.blit(text, (WIDTH - 380, 10 + i * 22))
    
    if dragging_ball and throw_velocity:
        vel_text = font.render(f"Throw: ({throw_velocity[0]:.0f}, {throw_velocity[1]:.0f})", True, (255, 200, 100))
        screen.blit(vel_text, (mouse_x + 20, mouse_y - 20))
    
    if abs(window_delta_x) > 2 or abs(window_delta_y) > 2:
        move_text = font.render("WINDOW MOVING!", True, (255, 100, 100))
        screen.blit(move_text, (WIDTH // 2 - 60, 50))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
