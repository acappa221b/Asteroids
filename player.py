from circleshape import CircleShape
from constants import PLAYER_RADIUS, PLAYER_TURN_SPEED, PLAYER_SPEED, PLAYER_SHOOT_SPEED, PLAYER_SHOOT_COOLDOWN_SECONDS
import pygame
from shot import Shot

class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.color = (0, 255, 0)  # Green color
        self.speed = 5
        self.health = 100
        self.rotation = 0
        self.timer = 0
        for group in self.containers:
            group.add(self)

    # in the Player class
    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]
    
    def rotate(self,dt):
        self.rotation += PLAYER_TURN_SPEED * dt
    
    def move(self, dt):
        unit_vector = pygame.Vector2(0, 1)
        rotated_vector = unit_vector.rotate(self.rotation)
        rotated_with_speed_vector = rotated_vector * PLAYER_SPEED * dt
        self.position += rotated_with_speed_vector
    
    def update(self, dt):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            #print("A pressed, dt=", dt)
            self.rotate(-dt)
        if keys[pygame.K_d]:
            #print("D pressed, dt=", dt)
            self.rotate(dt)
        if keys[pygame.K_w]:
            #print("W pressed, dt=", dt)
            self.move(dt)
        if keys[pygame.K_s]:
            #print("S pressed, dt=", dt)
            self.move(-dt)
        
        self.timer -= dt
        if self.timer < 0:
            self.timer = 0
        if keys[pygame.K_SPACE]:
            self.shoot()

    
    def shoot(self):
        direction = pygame.Vector2(0, 1)
        direction = direction.rotate(self.rotation)
        direction = direction * PLAYER_SHOOT_SPEED 
        if self.timer > 0:
            return
        else:
            self.timer = PLAYER_SHOOT_COOLDOWN_SECONDS
            shot = Shot(self.position.x, self.position.y)
            shot.velocity = direction
        
        