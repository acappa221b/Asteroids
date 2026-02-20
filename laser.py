import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Laser(pygame.sprite.Sprite):
    """Laser beam fired by player when LASER_BEAM perk is active"""
    
    def __init__(self, player_pos, direction, owner=None):
        super().__init__()
        self.player_pos = pygame.Vector2(player_pos)
        self.direction = pygame.Vector2(direction).normalize()
        self.owner = owner
        
        # Laser timing
        self.active_time = 0.0  # Time laser has been active
        self.max_active_time = 1.0  # Laser fires for 1 second
        self.min_width = 2
        self.max_width = 4  # Double the min width
        
        # Calculate endpoint (ray from player to edge of screen)
        self._update_endpoint()
    
    def _update_endpoint(self):
        """Calculate where the laser extends to (edge of screen)"""
        # Start from player position
        # Find the farthest point in the direction vector that's still on screen
        
        max_distance = 0
        
        # Check which edge we'll hit first
        if self.direction.x > 0:
            # Moving right
            dist_x = (SCREEN_WIDTH - self.player_pos.x) / self.direction.x
            max_distance = dist_x
        elif self.direction.x < 0:
            # Moving left
            dist_x = self.player_pos.x / abs(self.direction.x)
            max_distance = dist_x
        else:
            max_distance = float('inf')
        
        if self.direction.y > 0:
            # Moving down
            dist_y = (SCREEN_HEIGHT - self.player_pos.y) / self.direction.y
            max_distance = min(max_distance, dist_y) if max_distance != float('inf') else dist_y
        elif self.direction.y < 0:
            # Moving up
            dist_y = self.player_pos.y / abs(self.direction.y)
            max_distance = min(max_distance, dist_y) if max_distance != float('inf') else dist_y
        
        # Clamp to reasonable distance
        if max_distance == float('inf'):
            max_distance = 1000
        
        self.endpoint = self.player_pos + self.direction * max_distance
    
    def update(self, dt):
        """Update laser state and follow player direction if owner exists"""
        self.active_time += dt
        if self.owner is not None:
            # Update position and direction to match player
            self.player_pos = pygame.Vector2(self.owner.position)
            # Player's direction is always (0, 1) rotated by self.owner.rotation
            self.direction = pygame.Vector2(0, 1).rotate(self.owner.rotation).normalize()
            self._update_endpoint()
    
    def is_alive(self):
        """Check if laser is still active"""
        return self.active_time < self.max_active_time
    
    def get_width(self):
        """Get current width of laser based on active time (grows from min to max over 1 second)"""
        progress = self.active_time / self.max_active_time  # 0 to 1
        return self.min_width + (self.max_width - self.min_width) * progress
    
    def draw(self, screen):
        """Draw the laser as a line"""
        if self.is_alive():
            width = int(self.get_width())
            color = (0, 200, 255)  # Cyan color
            pygame.draw.line(screen, color, self.player_pos, self.endpoint, width)
    
    def check_collision(self, sprite):
        """Check if laser hits an asteroid/sprite"""
        if not self.is_alive():
            return False
        
        # Simple point-to-line distance check
        # Vector from laser start to sprite
        to_sprite = sprite.position - self.player_pos
        
        # Project onto laser direction
        projection = to_sprite.dot(self.direction)
        
        # Check if projection is within laser bounds
        if projection < 0 or projection > self.player_pos.distance_to(self.endpoint):
            return False
        
        # Closest point on laser to sprite
        closest_point = self.player_pos + self.direction * projection
        
        # Check distance from sprite center to laser line
        distance = sprite.position.distance_to(closest_point)
        
        return distance <= sprite.radius
