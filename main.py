#imports:
import sys
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, UI_FONT_SIZE, UI_SMALL_FONT_SIZE, UI_PADDING
from logger import log_state, log_event
from player import Player
from asteroidfield import AsteroidField
from asteroid import Asteroid
from shot import Shot
from perks import PerkType
from drone import Drone
from menu import MenuScreen
from highscores import HighscoreManager
import random



class GameState:
    """Manages game state including level-ups and perk selection"""
    def __init__(self):
        self.waiting_for_perk_selection = False
        self.available_perk_choices = []
        self.selected_perk_index = None
        self.score = 0  # Track player score


def draw_text(screen, text, font, color, pos):
    """Helper function to draw text"""
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)


def draw_hud(screen, player, game_state, font_large, font_small):
    """Draw the HUD with level, XP, perks, and score"""
    # Score display (top right)
    score_text = f"Score: {game_state.score}"
    draw_text(screen, score_text, font_large, (255, 100, 100), (SCREEN_WIDTH - 300, UI_PADDING))
    
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


def run_game(screen, font_large, font_small, clock):
    """Run the actual game loop"""
    dt = 0

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()

    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable,)
    Shot.containers = (shots, drawable, updatable)
    Player.containers = (updatable, drawable)
    
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2) #Player positioned at center of screen
    asteroid_field = AsteroidField(player)
    game_state = GameState()
    highscore_manager = HighscoreManager()
    
    game_over = False
    
    while True: # Main game loop
        log_state() # Log the current state for debugging
        
        for event in pygame.event.get(): # Event handling loop
            if event.type == pygame.QUIT: # Handle window close event
                return "QUIT"
            
            if not game_over:
                # Handle perk selection
                handle_perk_selection(game_state, player, asteroids, event)
            else:
                # Handle game over input
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    return "MENU"
        
        # Skip game logic if waiting for perk selection or game over
        if not game_over and not game_state.waiting_for_perk_selection:
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
                        shot.kill()
                        roid.split()
                        game_state.score += 10  # Award 10 points per asteroid
                        
                        # Award XP
                        if player.add_xp(1):  # Level up!
                            log_event(f"level_up_to_{player.level_system.current_level}")
                            game_state.waiting_for_perk_selection = True
                            game_state.available_perk_choices = player.perk_system.get_random_perks(2)

        
        screen.fill("black") #background color
       
        if not game_over:
            for draws in drawable:
                draws.draw(screen)
            
            # Draw HUD
            draw_hud(screen, player, game_state, font_large, font_small)
            
            # Draw perk selection UI if needed
            draw_perk_selection(screen, game_state, font_large, font_small)
        else:
            # Draw game over screen
            draw_game_over_screen(screen, game_state, player, font_large, font_small, highscore_manager)

        #refresh
        pygame.display.flip() # Update the full display surface to the screen
        dt = clock.tick(60) / 1000  # Limit to 60 FPS and get delta time in seconds


def main():
    print("Starting Blasteroids with pygame version: 2.6.1")
    print(f"Screen width: {SCREEN_WIDTH}\nScreen height: {SCREEN_HEIGHT}")

    pygame.init() # Initialize all imported pygame modules
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Set up the display
    pygame.display.set_caption("Blasteroids")
    
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
                    result = run_game(screen, font_large, font_small, clock)
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


