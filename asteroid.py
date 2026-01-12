from circleshape import CircleShape
import pygame
import constants
import random
from logger import log_event

class Asteroid(CircleShape):
    def __init__(self, x, y, radius): 
        super().__init__(x, y, radius)       
        self.color = (255, 255, 255)
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.position, self.radius, constants.LINE_WIDTH)


    def update(self, dt):
        self.position = self.position + self.velocity * dt

    def split(self):
        self.kill()
        if self.radius <= constants.ASTEROID_MIN_RADIUS:
            return
        else:
            log_event("asteroid_split")
            angle = random.uniform(20, 50)
            vec1 = self.velocity.rotate(angle)
            vec2 = self.velocity.rotate(-angle)
            new_radius = self.radius - constants.ASTEROID_MIN_RADIUS
            first_asteroid = Asteroid(self.position.x, self.position.y, new_radius)
            second_asteroid = Asteroid(self.position.x, self.position.y, new_radius)
            first_asteroid.velocity = vec1 * 1.2
            second_asteroid.velocity = vec2 * 1.2