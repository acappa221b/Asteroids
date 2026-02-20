#!/usr/bin/env python3
import pygame
pygame.init()

from constants import ASTEROID_MIN_RADIUS, ASTEROID_KINDS, SCREEN_WIDTH, SCREEN_HEIGHT
from asteroid import Asteroid
from asteroidfield import AsteroidField
from player import Player
from shot import Shot
from drone import Drone

# Setup like in run_game
asteroids = pygame.sprite.Group()
updatable = pygame.sprite.Group()
drawable = pygame.sprite.Group()
shots = pygame.sprite.Group()

Asteroid.containers = (asteroids, updatable, drawable)
AsteroidField.containers = (updatable,)
Shot.containers = (shots, drawable, updatable)
Player.containers = (updatable, drawable)
Drone.containers = (updatable, drawable)

# Create player and asteroid field with debug mode
player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
asteroid_field = AsteroidField(player, debug_mode=True)

print("Testing debug mode asteroid spawning...")

# Try to spawn an asteroid in debug mode
try:
    print(f"Asteroid field debug_mode: {asteroid_field.debug_mode}")
    print(f"Edges available: {len(asteroid_field.edges)}")
    
    # Simulate what happens when Ctrl is pressed
    import random
    edge = random.choice(asteroid_field.edges)
    speed = random.randint(40, 100)
    velocity = edge[0] * speed
    velocity = velocity.rotate(random.randint(-30, 30))
    position = edge[1](random.uniform(0, 1))
    
    print(f"Position: {position}, Velocity: {velocity}")
    
    # Call spawn
    result = asteroid_field.spawn(ASTEROID_MIN_RADIUS * ASTEROID_KINDS, position, velocity)
    
    print(f"Spawn successful!")
    print(f"Asteroid returned: {result}")
    print(f"Asteroids in group: {len(asteroids)}")
    print("TEST PASSED!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
