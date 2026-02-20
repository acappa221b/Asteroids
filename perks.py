import random
from enum import Enum

class PerkType(Enum):
    DOUBLE_SHOT = "double_shot"
    WIDER_SHOT = "wider_shot"
    MACHINE_GUN = "machine_gun"
    SHIELD = "shield"
    SPEEDSTER = "speedster"
    LASER_BEAM = "laser_beam"
    PIERCING_SHOTS = "piercing_shots"
    RICOCHET = "ricochet"
    DRONE = "drone"

class Perk:
    def __init__(self, perk_type: PerkType):
        self.perk_type = perk_type
        self.name = self._get_name()
        self.description = self._get_description()
    
    def _get_name(self):
        names = {
            PerkType.DOUBLE_SHOT: "Double Shot",
            PerkType.WIDER_SHOT: "Wider Shot",
            PerkType.MACHINE_GUN: "Machine Gun",
            PerkType.SHIELD: "Shield",
            PerkType.SPEEDSTER: "Speedster",
            PerkType.LASER_BEAM: "Laser Beam",
            PerkType.PIERCING_SHOTS: "Piercing Shots",
            PerkType.RICOCHET: "Ricochet",
            PerkType.DRONE: "Drone",
        }
        return names[self.perk_type]
    
    def _get_description(self):
        descriptions = {
            PerkType.DOUBLE_SHOT: "Ship shoots 2 parallel shots",
            PerkType.WIDER_SHOT: "Doubles the width of shots",
            PerkType.MACHINE_GUN: "Fires twice as fast (reduced cooldown)",
            PerkType.SHIELD: "Protects from 1 hit, visible shield",
            PerkType.SPEEDSTER: "Ship flies 1.5x faster",
            PerkType.LASER_BEAM: "Fires a forward beam (1s on / 3s off)",
            PerkType.PIERCING_SHOTS: "Shots pierce the first target hit",
            PerkType.RICOCHET: "Bullets ricochet once",
            PerkType.DRONE: "Spawns a drone that orbits and shoots",
        }
        return descriptions[self.perk_type]

class PerkSystem:
    ALL_PERKS = list(PerkType)
    
    def __init__(self):
        self.perks = []
        self.available_perks = self.ALL_PERKS.copy()
    
    def add_perk(self, perk_type: PerkType):
        """Add a perk and remove it from available perks"""
        if perk_type in self.available_perks:
            self.perks.append(Perk(perk_type))
            self.available_perks.remove(perk_type)
            return True
        return False
    
    def get_random_perks(self, count=2):
        """Get random perks that haven't been selected yet"""
        if len(self.available_perks) == 0:
            return []
        return random.sample(self.available_perks, min(count, len(self.available_perks)))
    
    def has_perk(self, perk_type: PerkType):
        """Check if player has a specific perk"""
        return any(p.perk_type == perk_type for p in self.perks)
    
    def get_shot_width_multiplier(self):
        """Get shot width multiplier based on perks"""
        multiplier = 1.0
        if self.has_perk(PerkType.WIDER_SHOT):
            multiplier *= 2.0
        return multiplier
    
    def get_shot_speed_multiplier(self):
        """Backward-compatible: returns multiplier for shot speed (unused)
        """
        return 1.0
    
    def get_shot_cooldown_multiplier(self):
        """Return multiplier to apply to cooldown (MACHINE_GUN halves cooldown)"""
        multiplier = 1.0
        if self.has_perk(PerkType.MACHINE_GUN):
            multiplier *= 0.5
        return multiplier
    
    def get_player_speed_multiplier(self):
        """Get player speed multiplier based on perks"""
        multiplier = 1.0
        if self.has_perk(PerkType.SPEEDSTER):
            multiplier *= 1.5
        return multiplier
    
    def should_shoot_double(self):
        """Check if player has double shot perk"""
        return self.has_perk(PerkType.DOUBLE_SHOT)
    
    def has_shield(self):
        """Check if player has shield perk"""
        return self.has_perk(PerkType.SHIELD)
    
    def has_laser(self):
        return self.has_perk(PerkType.LASER_BEAM)
    
    def has_piercing(self):
        return self.has_perk(PerkType.PIERCING_SHOTS)
    
    def has_ricochet(self):
        return self.has_perk(PerkType.RICOCHET)
    
    def has_drone(self):
        return self.has_perk(PerkType.DRONE)

    def remove_perk(self, perk_type: PerkType):
        """Remove a perk (for debug/toggle) and make it available again"""
        removed = False
        for p in list(self.perks):
            if p.perk_type == perk_type:
                try:
                    self.perks.remove(p)
                except ValueError:
                    pass
                removed = True
        if removed and perk_type not in self.available_perks:
            self.available_perks.append(perk_type)
        return removed

    def toggle_perk(self, perk_type: PerkType):
        """Toggle a perk on/off for debug purposes"""
        if self.has_perk(perk_type):
            return self.remove_perk(perk_type)
        # add even if previously removed (debug convenience)
        if perk_type in self.available_perks:
            return self.add_perk(perk_type)
        self.perks.append(Perk(perk_type))
        return True

class LevelSystem:
    MAX_LEVEL = 20
    BASE_XP_FOR_LEVEL_2 = 50  # Level 12 requires 50 XP
    XP_INCREMENT = 50  # Each subsequent level costs 50 more XP
    
    def __init__(self):
        self.current_level = 1
        self.current_xp = 0
        self.xp_thresholds = self._calculate_xp_thresholds()
    
    def _calculate_xp_thresholds(self):
        """Calculate cumulative XP needed for each level"""
        thresholds = {1: 0}  # Level 1 starts at 0 XP
        cumulative_xp = 0
        
        for level in range(2, self.MAX_LEVEL + 1):
            xp_needed = self.BASE_XP_FOR_LEVEL_2 + (level - 2) * self.XP_INCREMENT
            cumulative_xp += xp_needed
            thresholds[level] = cumulative_xp
        
        return thresholds
    
    def add_xp(self, amount):
        """Add XP and return True if leveled up"""
        self.current_xp += amount
        
        if self.current_level < self.MAX_LEVEL:
            next_level_threshold = self.xp_thresholds.get(self.current_level + 1, float('inf'))
            if self.current_xp >= next_level_threshold:
                self.current_level += 1
                return True
        return False
    
    def get_xp_for_next_level(self):
        """Get XP needed to reach next level"""
        if self.current_level >= self.MAX_LEVEL:
            return 0
        return self.xp_thresholds.get(self.current_level + 1, float('inf')) - self.current_xp
    
    def get_progress_to_next_level(self):
        """Get progress percentage to next level (0.0 to 1.0)"""
        if self.current_level >= self.MAX_LEVEL:
            return 1.0
        
        current_threshold = self.xp_thresholds.get(self.current_level, 0)
        next_threshold = self.xp_thresholds.get(self.current_level + 1, float('inf'))
        
        if next_threshold == float('inf'):
            return 1.0
        
        xp_in_level = self.current_xp - current_threshold
        xp_needed = next_threshold - current_threshold
        
        return min(1.0, xp_in_level / xp_needed) if xp_needed > 0 else 1.0
