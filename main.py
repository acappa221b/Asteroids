

import sys
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, UI_FONT_SIZE, UI_SMALL_FONT_SIZE, UI_PADDING
from menu import MenuScreen
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
from player import Player
from perks import PerkType, Perk

def main():
    # ...existing code...
    font_large = pygame.font.Font(None, UI_FONT_SIZE)
    font_small = pygame.font.Font(None, UI_SMALL_FONT_SIZE)
    clock = pygame.time.Clock()
    menu = MenuScreen()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            action = menu.handle_input(event)
            if action == "NEW_GAME":
                result = run_game(screen, font_large, font_small, clock, debug_mode=False)
                if result == "QUIT":
                    pygame.quit()
                    sys.exit()
                break  # Exit inner loop to show menu again
            elif action == "DEBUG_MODE":
                result = run_game(screen, font_large, font_small, clock, debug_mode=True)
                if result == "QUIT":
                    pygame.quit()
                    sys.exit()
                break  # Exit inner loop to show menu again
            elif action == "EXIT":
                pygame.quit()
                sys.exit()
        # Draw menu
        menu.draw(screen)
        pygame.display.flip()
        clock.tick(60)

class PauseMenu:
    """Pause menu for both normal and debug mode"""
    def __init__(self):
        self.open = False
        self.selected_option = 0  # 0: Continue, 1: Exit Game
        self.options = ["CONTINUE", "EXIT GAME"]
        self.option_rects = []
    
    def handle_input(self, event):
        """Handle pause menu input"""
        if not self.open:
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Close pause menu
                self.open = False
                return "CONTINUE"
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.selected_option == 0:
                    self.open = False
                    return "CONTINUE"
                elif self.selected_option == 1:
                    return "EXIT_GAME"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(event.pos):
                    self.selected_option = i
                    if i == 0:
                        self.open = False
                        return "CONTINUE"
                    elif i == 1:
                        return "EXIT_GAME"
        
        return None
    
    def draw(self, screen, font_large, font_small):
        """Draw pause menu"""
        if not self.open:
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Title
        title = font_large.render("PAUSED", True, (255, 200, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title, title_rect)
        
        # Draw menu options
        menu_y = 300
        option_spacing = 100
        self.option_rects = []
        
        for i, option in enumerate(self.options):
            color = (0, 255, 100) if i == self.selected_option else (200, 200, 200)
            
            # Draw button background
            option_font = font_large
            text = option_font.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, menu_y + i * option_spacing))
            
            # Add padding to make buttons easier to click
            button_rect = text_rect.inflate(80, 30)
            self.option_rects.append(button_rect)
            
            # Draw button border if selected
            if i == self.selected_option:
                pygame.draw.rect(screen, color, button_rect, 3)
            
            screen.blit(text, text_rect)
        
        # Instructions
        instruction = font_small.render("Use W/↑ AND S/↓ to select | ENTER to confirm", True, (150, 150, 150))
        instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
        screen.blit(instruction, instruction_rect)


def draw_text(screen, text, font, color, pos):
    """Helper function to draw text"""
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)


def draw_hud(screen, player, game_state, font_large, font_small, debug_mode=False):
    """Draw the HUD with level, XP, perks, and score"""
    # Score display (top right)
    score_text = f"Score: {game_state.score}"
    draw_text(screen, score_text, font_large, (255, 100, 100), (SCREEN_WIDTH - 300, UI_PADDING))
    
    # Skip level/XP display in debug mode
    if debug_mode:
        return
    
    # Level and XP display
    level_text = f"Level: {player.level_system.current_level}/{player.level_system.MAX_LEVEL}"
    draw_text(screen, level_text, font_large, (255, 255, 0), (UI_PADDING, UI_PADDING))
    
    # XP bar
    xp_bar_width = 200
    xp_bar_height = 20
    xp_bar_x = UI_PADDING
    xp_bar_y = UI_PADDING + UI_FONT_SIZE + 10
    
    # Background
    pygame.draw.rect(screen, (100, 100, 100), (xp_bar_x, xp_bar_y, xp_bar_width, xp_bar_height))
    
    # Fill
    progress = player.level_system.get_progress_to_next_level()
    fill_width = int(xp_bar_width * progress)
    pygame.draw.rect(screen, (0, 255, 100), (xp_bar_x, xp_bar_y, fill_width, xp_bar_height))
    
    # Border
    pygame.draw.rect(screen, (255, 255, 255), (xp_bar_x, xp_bar_y, xp_bar_width, xp_bar_height), 2)
    
    # XP text
    xp_needed = player.level_system.get_xp_for_next_level()
    xp_text = f"XP: {player.level_system.current_xp} (+{xp_needed} to next)" if player.level_system.current_level < player.level_system.MAX_LEVEL else "MAX LEVEL"
    draw_text(screen, xp_text, font_small, (255, 255, 255), (xp_bar_x, xp_bar_y + xp_bar_height + 5))
    
    # Perks display
    perks_text = "Perks: " + ", ".join([p.name for p in player.perk_system.perks]) if player.perk_system.perks else "Perks: None"
    draw_text(screen, perks_text, font_small, (100, 200, 255), (UI_PADDING, SCREEN_HEIGHT - UI_PADDING - UI_SMALL_FONT_SIZE))


def draw_perk_selection(screen, game_state, font_large, font_small):
    """Draw perk selection UI"""
    if not game_state.waiting_for_perk_selection:
        return
    
    # Semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Title
    title_text = "LEVEL UP! Choose a Perk:"
    title_surface = font_large.render(title_text, True, (255, 215, 0))
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
    screen.blit(title_surface, title_rect)
    
    # Perk buttons
    button_width = 400
    button_height = 80
    button_y_start = 250
    button_spacing = 150
    
    for i, perk_type in enumerate(game_state.available_perk_choices):
        perk_name = perk_type.value.replace('_', ' ').title()
        perk_obj = next((p for p in game_state.available_perk_choices if isinstance(p, PerkType)), None)
        
        # Get the actual Perk object for description
        from perks import Perk
        perk = Perk(perk_type)
        
        button_x = (SCREEN_WIDTH // 2) - (button_width // 2)
        button_y = button_y_start + (i * button_spacing)
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Highlight selected perk
        color = (255, 100, 0) if game_state.selected_perk_index == i else (200, 200, 200)
        pygame.draw.rect(screen, color, button_rect)
        pygame.draw.rect(screen, (255, 255, 255), button_rect, 3)
        
        # Perk name
        name_surface = font_large.render(perk.name, True, (0, 0, 0))
        name_rect = name_surface.get_rect(center=(button_x + button_width // 2, button_y + 20))
        screen.blit(name_surface, name_rect)
        
        # Perk description
        desc_surface = font_small.render(perk.description, True, (0, 0, 0))
        desc_rect = desc_surface.get_rect(center=(button_x + button_width // 2, button_y + 50))
        screen.blit(desc_surface, desc_rect)
        
        # Key hint
        key = str(i + 1)
        key_surface = font_small.render(f"Press {key}", True, (100, 100, 100))
        key_rect = key_surface.get_rect(center=(button_x + button_width // 2, button_y + 65))
        screen.blit(key_surface, key_rect)


class DebugPerkMenu:
    """Menu to activate/deactivate perks in debug mode"""
    def __init__(self):
        self.open = False
        self.button_rect = pygame.Rect(SCREEN_WIDTH - 250, 70, 230, 40)
        self.perk_buttons = []  # Store Perk button rects with their types
        self.active_perks = set()  # Track which perks are active
        self._create_perk_buttons()
    
    def _create_perk_buttons(self):
        """Create button rects for all available perks"""
        self.perk_buttons = []
        button_width = 200
        button_height = 50
        start_x = (SCREEN_WIDTH - button_width) // 2
        start_y = 150
        spacing = 60
        
        for i, perk_type in enumerate(PerkType):
            button_rect = pygame.Rect(start_x, start_y + (i * spacing), button_width, button_height)
            self.perk_buttons.append((button_rect, perk_type))
    
    def draw_button(self, screen, font):
        """Draw the open menu button"""
        pygame.draw.rect(screen, (100, 150, 255), self.button_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.button_rect, 2)
        text = font.render("TAB: Perk Menu", True, (0, 0, 0))
        text_rect = text.get_rect(center=self.button_rect.center)
        screen.blit(text, text_rect)
    
    def draw_menu(self, screen, font_large, font_small):
        """Draw the perk selection menu"""
        if not self.open:
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Title
        title = font_large.render("DEBUG: Toggle Perks (Click or Press Keys)", True, (0, 200, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title, title_rect)
        
        # Draw perk buttons
        for i, (button_rect, perk_type) in enumerate(self.perk_buttons):
            perk = Perk(perk_type)
            is_active = perk_type in self.active_perks
            
            # Color based on active state
            color = (0, 200, 50) if is_active else (150, 150, 150)
            pygame.draw.rect(screen, color, button_rect)
            pygame.draw.rect(screen, (255, 255, 255), button_rect, 2)
            
            # Perk name
            name_text = font_large.render(perk.name + (" ✓" if is_active else ""), True, (0, 0, 0))
            name_rect = name_text.get_rect(center=(button_rect.centerx, button_rect.y + 15))
            screen.blit(name_text, name_rect)
            
            # Key hint
            key = str(i + 1)
            key_text = font_small.render(f"Press {key}", True, (100, 100, 100))
            key_rect = key_text.get_rect(center=(button_rect.centerx, button_rect.y + 35))
            screen.blit(key_text, key_rect)
        
        # Close instruction
        close_text = font_small.render("Press TAB, ESC, or click outside to close", True, (150, 150, 150))
        close_rect = close_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        screen.blit(close_text, close_rect)
    
    def toggle_perk(self, perk_type: PerkType):
        """Toggle a perk on/off"""
        if perk_type in self.active_perks:
            self.active_perks.remove(perk_type)
        else:
            self.active_perks.add(perk_type)
    
    def button_clicked(self, pos):
        """Check if button was clicked"""
        return self.button_rect.collidepoint(pos)
    
    def get_perk_at_pos(self, pos):
        """Get perk type if clicked, None otherwise"""
        for button_rect, perk_type in self.perk_buttons:
            if button_rect.collidepoint(pos):
                return perk_type
        return None
    
    def apply_perks_to_player(self, player):
        """Apply all active perks to the player"""
        # Clear current perks
        player.perk_system.perks = []
        player.perk_system.available_perks = list(PerkType)
        
        # Add active perks
        for perk_type in self.active_perks:
            player.perk_system.add_perk(perk_type)
            # Special case: reset shield if it's active
            if perk_type == PerkType.SHIELD:
                player.reset_shield()


class DebugSpawnButton:
    """Button to spawn asteroids in debug mode"""
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH - 250, 20, 230, 40)
    
    def draw(self, screen, font):
        """Draw the button"""
        pygame.draw.rect(screen, (255, 100, 0), self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        text = font.render("Press CTRL to spawn asteroid", True, (0, 0, 0))
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)
    
    def is_clicked(self, pos):
        """Check if button was clicked"""
        return self.rect.collidepoint(pos)


def draw_game_over_screen(screen, game_state, player, font_large, font_small, highscore_manager):
    """Draw game over screen"""
    # Semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(220)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Game Over title
    title = font_large.render("GAME OVER", True, (255, 50, 50))
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
    screen.blit(title, title_rect)
    
    # Stats
    stats_y = 250
    score_text = font_small.render(f"Final Score: {game_state.score}", True, (255, 200, 100))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - 200, stats_y))
    
    level_text = font_small.render(f"Level Reached: {player.level_system.current_level}", True, (255, 200, 100))
    screen.blit(level_text, (SCREEN_WIDTH // 2 - 200, stats_y + 40))
    
    # Highscore check
    is_highscore = highscore_manager.is_highscore(game_state.score)
    if is_highscore:
        hs_text = font_small.render("★ NEW HIGHSCORE! ★", True, (255, 215, 0))
        screen.blit(hs_text, (SCREEN_WIDTH // 2 - 200, stats_y + 80))
    
    # Instructions
    instruction = font_small.render("Press SPACE to return to menu...", True, (150, 150, 150))
    instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
    screen.blit(instruction, instruction_rect)



def handle_perk_selection(game_state, player, asteroids, event):
    """Handle perk selection input"""
    if not game_state.waiting_for_perk_selection:
        return
    
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_1 and len(game_state.available_perk_choices) > 0:
            player.perk_system.add_perk(game_state.available_perk_choices[0])
            # Activate shield if it was selected
            if game_state.available_perk_choices[0] == PerkType.SHIELD:
                player.reset_shield()
            game_state.waiting_for_perk_selection = False
            game_state.available_perk_choices = []
        elif event.key == pygame.K_2 and len(game_state.available_perk_choices) > 1:
            player.perk_system.add_perk(game_state.available_perk_choices[1])
            # Activate shield if it was selected
            if game_state.available_perk_choices[1] == PerkType.SHIELD:
                player.reset_shield()
            game_state.waiting_for_perk_selection = False
            game_state.available_perk_choices = []


def run_game(screen, font_large, font_small, clock, debug_mode=False):
    """Run the actual game loop"""
    dt = 0

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    lasers = pygame.sprite.Group()

    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable,)
    Shot.containers = (shots, drawable, updatable)
    Player.containers = (updatable, drawable)
    
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2) #Player positioned at center of screen
    player.lasers_group = lasers  # Give player access to lasers group
    asteroid_field = AsteroidField(player, debug_mode=debug_mode)
    game_state = GameState()
    highscore_manager = HighscoreManager()
    
    # Debug mode spawn button and perk menu
    debug_button = DebugSpawnButton() if debug_mode else None
    debug_perk_menu = DebugPerkMenu() if debug_mode else None
    
    # Pause menu for both modes
    pause_menu = PauseMenu()
    
    game_over = False
    
    while True: # Main game loop
        log_state() # Log the current state for debugging
        
        for event in pygame.event.get(): # Event handling loop
            if event.type == pygame.QUIT: # Handle window close event
                return "QUIT"
            
            if not game_over:
                # Handle pause menu input
                if pause_menu.open:
                    action = pause_menu.handle_input(event)
                    if action == "CONTINUE":
                        # Menu closes on its own (pause_menu.open = False is set in handle_input)
                        pass
                    elif action == "EXIT_GAME":
                        # Save highscore before exiting
                        highscore_manager.add_score("Player", game_state.score, player.level_system.current_level)
                        return "MENU"
                    continue  # Skip other input handling when pause menu is open
                
                # Handle ESC to open pause menu
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if not (debug_mode and debug_perk_menu.open):
                        pause_menu.open = True
                        continue
                
                # Handle debug perk menu
                if debug_mode and debug_perk_menu:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_TAB:
                            debug_perk_menu.open = not debug_perk_menu.open
                        elif event.key == pygame.K_ESCAPE:
                            if debug_perk_menu.open:
                                debug_perk_menu.open = False
                        # Handle number keys (1-9) to toggle perks
                        elif 49 <= event.key <= 57:  # ASCII codes for 1-9
                            perk_index = event.key - 49
                            if debug_perk_menu.open and perk_index < len(debug_perk_menu.perk_buttons):
                                perk_type = debug_perk_menu.perk_buttons[perk_index][1]
                                debug_perk_menu.toggle_perk(perk_type)
                                debug_perk_menu.apply_perks_to_player(player)
                    
                    if event.type == pygame.MOUSEBUTTONDOWN and debug_perk_menu.open:
                        perk_type = debug_perk_menu.get_perk_at_pos(event.pos)
                        if perk_type:
                            debug_perk_menu.toggle_perk(perk_type)
                            debug_perk_menu.apply_perks_to_player(player)
                        elif not any(rect.collidepoint(event.pos) for rect, _ in debug_perk_menu.perk_buttons):
                            # Click outside menu to close
                            debug_perk_menu.open = False
                
                # Handle perk selection
                handle_perk_selection(game_state, player, asteroids, event)
                
                # Handle debug mode asteroid spawning
                if debug_mode and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                        # Spawn a single large asteroid at random position on edge
                        edge = random.choice(asteroid_field.edges)
                        speed = random.randint(40, 100)
                        velocity = edge[0] * speed
                        velocity = velocity.rotate(random.randint(-30, 30))
                        position = edge[1](random.uniform(0, 1))
                        asteroid_field.spawn(ASTEROID_MIN_RADIUS * ASTEROID_KINDS, position, velocity)
                
                # Handle debug button click (spawn button)
                if debug_mode and event.type == pygame.MOUSEBUTTONDOWN and debug_button:
                    if debug_button.is_clicked(event.pos):
                        edge = random.choice(asteroid_field.edges)
                        speed = random.randint(40, 100)
                        velocity = edge[0] * speed
                        velocity = velocity.rotate(random.randint(-30, 30))
                        position = edge[1](random.uniform(0, 1))
                        asteroid_field.spawn(ASTEROID_MIN_RADIUS * ASTEROID_KINDS, position, velocity)
                    # Handle perk menu button
                    elif debug_perk_menu and debug_perk_menu.button_clicked(event.pos):
                        debug_perk_menu.open = not debug_perk_menu.open
            else:
                # Handle game over input
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    return "MENU"
        
        # Skip game logic if waiting for perk selection, pause menu is open, or game over
        if not game_over and not game_state.waiting_for_perk_selection and not pause_menu.open:
            updatable.update(dt)

            for roid in asteroids:
                if roid.collides_with(player):
                    log_event("player_hit")
                    if player.take_damage():
                        log_event("game_over")
                        game_over = True
                        # Save the score
                        highscore_manager.add_score("Player", game_state.score, player.level_system.current_level)
                    else:
                        # Shield was active - reset field and teleport player to center
                        log_event("shield_hit")
                        # Clear all asteroids
                        for asteroid in asteroids:
                            asteroid.kill()
                        # Reset asteroid field spawn timer
                        asteroid_field.spawn_timer = 0
                        # Teleport player to center
                        player.position.x = SCREEN_WIDTH / 2
                        player.position.y = SCREEN_HEIGHT / 2
            
            for roid in asteroids:
                for shot in shots:
                    if roid.collides_with(shot):
                        log_event("asteroid_shot")
                        roid.split()
                        game_state.score += 10  # Award 10 points per asteroid
                        # Award XP
                        if player.add_xp(1):  # Level up!
                            log_event(f"level_up_to_{player.level_system.current_level}")
                            game_state.waiting_for_perk_selection = True
                            game_state.available_perk_choices = player.perk_system.get_random_perks(2)
                        # Piercing shot logic
                        if getattr(shot, 'piercing', False):
                            if not hasattr(shot, 'pierce_count'):
                                shot.pierce_count = 0
                            shot.pierce_count += 1
                            if shot.pierce_count >= 2:
                                shot.kill()
                        else:
                            shot.kill()
            
            # Laser collision detection
            for laser in list(lasers):
                if not laser.is_alive():
                    lasers.remove(laser)
                    continue
                for roid in asteroids:
                    if laser.check_collision(roid):
                        log_event("asteroid_laser")
                        roid.split()
                        game_state.score += 10  # Award 10 points per asteroid hit by laser

        
        screen.fill("black") #background color
       
        if not game_over:
            for draws in drawable:
                draws.draw(screen)
            
            # Draw lasers
            for laser in lasers:
                laser.draw(screen)
            
            # Draw HUD
            draw_hud(screen, player, game_state, font_large, font_small, debug_mode=debug_mode)
            
            # Draw perk selection UI if needed
            draw_perk_selection(screen, game_state, font_large, font_small)
            
            # Draw debug buttons and perk menu if in debug mode
            if debug_mode:
                debug_button.draw(screen, font_small)
                debug_perk_menu.draw_button(screen, font_small)
                debug_perk_menu.draw_menu(screen, font_large, font_small)
            
            # Draw pause menu
            pause_menu.draw(screen, font_large, font_small)
        else:
            # Draw game over screen
            draw_game_over_screen(screen, game_state, player, font_large, font_small, highscore_manager)

        #refresh
        pygame.display.flip() # Update the full display surface to the screen
        dt = clock.tick(60) / 1000  # Limit to 60 FPS and get delta time in seconds


def main():
    print("Starting Voidfall with pygame version: 2.6.1")
    print(f"Screen width: {SCREEN_WIDTH}\nScreen height: {SCREEN_HEIGHT}")

    pygame.init() # Initialize all imported pygame modules
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Set up the display
    pygame.display.set_caption("Voidfall")
    
    # Setup fonts
    font_large = pygame.font.Font(None, UI_FONT_SIZE)
    font_small = pygame.font.Font(None, UI_SMALL_FONT_SIZE)

    clock = pygame.time.Clock()
    
    # Create menu
    menu = MenuScreen()
    
    # Main loop
    while True:
        # Show menu
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                
                action = menu.handle_input(event)
                
                if action == "NEW_GAME":
                    result = run_game(screen, font_large, font_small, clock, debug_mode=False)
                    if result == "QUIT":
                        return
                    # result should be "MENU", loop back to menu
                    break  # Exit inner loop to show menu again
                elif action == "DEBUG_MODE":
                    result = run_game(screen, font_large, font_small, clock, debug_mode=True)
                    if result == "QUIT":
                        return
                    # result should be "MENU", loop back to menu
                    break  # Exit inner loop to show menu again
                elif action == "EXIT":
                    return
            
            # Draw menu
            menu.draw(screen)
            pygame.display.flip()
            clock.tick(60)




if __name__ == "__main__":
    main()


