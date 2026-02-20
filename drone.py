from circleshape import CircleShape
import pygame
from constants import LINE_WIDTH, PLAYER_RADIUS
from shot import Shot

class Drone(CircleShape):
    def __init__(self, player, asteroids_group):
        super().__init__(player.position.x, player.position.y, 8)
        self.player = player
        self.asteroids = asteroids_group
        self.angle = 0.0
        self.orbit_radius = PLAYER_RADIUS + 40
        self.angular_speed = 120  # degrees per second
        self.shoot_timer = 0.0
        self.shoot_interval = 2.0
        for group in self.containers:
            group.add(self)

    def draw(self, screen):
        pygame.draw.circle(screen, (200, 200, 255), self.position, self.radius, LINE_WIDTH)

    def update(self, dt):
        # orbit around player
        self.angle += self.angular_speed * dt
        offset = pygame.Vector2(self.orbit_radius, 0).rotate(self.angle)
        self.position = self.player.position + offset

        # shooting
        self.shoot_timer += dt
        if self.shoot_timer >= self.shoot_interval:
            self.shoot_timer = 0.0
            # find target asteroid: prioritize smaller radius then distance
            targets = sorted(self.asteroids, key=lambda a: (a.radius, self.position.distance_to(a.position)))
            if targets:
                target = targets[0]
                direction = (target.position - self.position)
                if direction.length() == 0:
                    return
                direction = direction.normalize()
                s = Shot(self.position.x, self.position.y, owner=self)
                s.velocity = direction * 300
                # Drone shots respect player's perks for piercing/ricochet
                s.piercing = self.player.perk_system.has_piercing()
                s.ricochet_remaining = 1 if self.player.perk_system.has_ricochet() else 0

