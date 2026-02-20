from circleshape import CircleShape
import pygame
from constants import SHOT_RADIUS, LINE_WIDTH, SCREEN_WIDTH, SCREEN_HEIGHT

class Shot(CircleShape):
    def __init__(self, x, y, owner=None):
        super().__init__(x, y, SHOT_RADIUS)
        self.width_multiplier = 1.0
        self.piercing = False
        self.pierce_count = 0  # Number of targets pierced
        self.ricochet_remaining = 0
        self.owner = owner
        self.velocity = pygame.Vector2(0, 0)  # Ensure velocity is always present

    def draw(self, screen):
        draw_radius = int(self.radius * self.width_multiplier)
        pygame.draw.circle(screen, "white", self.position, draw_radius, LINE_WIDTH)

    def update(self, dt):
        self.position += self.velocity * dt
        # Kill if off-screen
        if (
            self.position.x < -50
            or self.position.x > SCREEN_WIDTH + 50
            or self.position.y < -50
            or self.position.y > SCREEN_HEIGHT + 50
        ):
            self.kill()

