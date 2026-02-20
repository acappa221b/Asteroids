from circleshape import CircleShape
from constants import PLAYER_RADIUS, PLAYER_TURN_SPEED, PLAYER_SPEED, PLAYER_SHOOT_SPEED, PLAYER_SHOOT_COOLDOWN_SECONDS
import pygame
from shot import Shot
from laser import Laser
from perks import PerkSystem, LevelSystem, PerkType

class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.color = (0, 255, 0)  # Green color
        self.speed = 5
        self.health = 100
        self.rotation = 0
        self.timer = 0
        self.perk_system = PerkSystem()
        self.level_system = LevelSystem()
        self.shield_health = 0  # 0 means no shield, 1 means shield is active
        self.laser_cooldown = 0.0
        self.laser_timer = 0.0
        self.drone = None
        self.lasers_group = None  # Reference to lasers sprite group, set by game
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
    
    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt
    
    def move(self, dt):
        unit_vector = pygame.Vector2(0, 1)
        rotated_vector = unit_vector.rotate(self.rotation)
        speed_multiplier = self.perk_system.get_player_speed_multiplier()
        rotated_with_speed_vector = rotated_vector * PLAYER_SPEED * speed_multiplier * dt
        self.position += rotated_with_speed_vector
    
    def update(self, dt):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-dt)
        
        # timers
        self.timer = max(0.0, self.timer - dt)
        self.laser_cooldown = max(0.0, self.laser_cooldown - dt)
        self.laser_timer = max(0.0, self.laser_timer - dt)

        if keys[pygame.K_SPACE]:
            self.shoot()

    def shoot(self):
        # Laser activation takes precedence
        if self.perk_system.has_laser():
            if self.laser_timer <= 0 and self.laser_cooldown <= 0:
                # Create laser and add to group
                if self.lasers_group is not None:
                    direction = pygame.Vector2(0, 1).rotate(self.rotation)
                    laser = Laser(self.position, direction, owner=self)
                    self.lasers_group.add(laser)
                # Set timers: 1 second active, then 3 second cooldown
                self.laser_timer = 1.0
                self.laser_cooldown = 3.0
                return
        # Normal shooting
        if self.timer > 0:
            return
        cooldown_mult = self.perk_system.get_shot_cooldown_multiplier()
        self.timer = PLAYER_SHOOT_COOLDOWN_SECONDS * cooldown_mult

        direction = pygame.Vector2(0, 1).rotate(self.rotation)
        direction = direction * PLAYER_SHOOT_SPEED
        width_multiplier = self.perk_system.get_shot_width_multiplier()

        if self.perk_system.should_shoot_double():
            offset = pygame.Vector2(0, 1).rotate(self.rotation + 90) * 10
            shot1 = Shot(self.position.x + offset.x, self.position.y + offset.y, owner=self)
            shot1.velocity = direction
            shot1.width_multiplier = width_multiplier
            shot1.piercing = self.perk_system.has_piercing()
            shot1.ricochet_remaining = 1 if self.perk_system.has_ricochet() else 0

            shot2 = Shot(self.position.x - offset.x, self.position.y - offset.y, owner=self)
            shot2.velocity = direction
            shot2.width_multiplier = width_multiplier
            shot2.piercing = self.perk_system.has_piercing()
            shot2.ricochet_remaining = 1 if self.perk_system.has_ricochet() else 0
        else:
            shot = Shot(self.position.x, self.position.y, owner=self)
            shot.velocity = direction
            shot.width_multiplier = width_multiplier
            shot.piercing = self.perk_system.has_piercing()
            shot.ricochet_remaining = 1 if self.perk_system.has_ricochet() else 0
    
    def add_xp(self, amount):
        return self.level_system.add_xp(amount)
    
    def take_damage(self):
        if self.perk_system.has_shield() and self.shield_health > 0:
            self.shield_health = 0
            self.perk_system.perks = [p for p in self.perk_system.perks if p.perk_type != PerkType.SHIELD]
            return False
        return True
    
    def reset_shield(self):
        if self.perk_system.has_shield():
            self.shield_health = 1
    
    def draw(self, screen):
        points = self.triangle()
        pygame.draw.polygon(screen, self.color, points)
        if self.shield_health > 0:
            pygame.draw.circle(screen, (0, 150, 255), self.position, self.radius + 10, 2)
        # Laser drawing handled by main loop

