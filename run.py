import sys
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, UI_FONT_SIZE, UI_SMALL_FONT_SIZE, UI_PADDING
from logger import log_state, log_event
from player2 import Player
from asteroidfield import AsteroidField
from asteroid import Asteroid
from shot_new import Shot
from perks2 import PerkType
from menu import MenuScreen
from highscores import HighscoreManager
from drone import Drone
import random

class GameState:
    def __init__(self):
        self.waiting_for_perk_selection = False
        self.available_perk_choices = []
        self.selected_perk_index = None
        self.score = 0


def draw_text(screen, text, font, color, pos):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)


def handle_perk_selection(game_state, player, asteroids, event):
    if not game_state.waiting_for_perk_selection:
        return
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_1 and len(game_state.available_perk_choices) > 0:
            chosen = game_state.available_perk_choices[0]
            player.perk_system.add_perk(chosen)
            if chosen == PerkType.SHIELD:
                player.reset_shield()
            if chosen == PerkType.DRONE:
                # create drone orbiting player
                d = Drone(player, asteroids)
                player.drone = d
            game_state.waiting_for_perk_selection = False
            game_state.available_perk_choices = []
        elif event.key == pygame.K_2 and len(game_state.available_perk_choices) > 1:
            chosen = game_state.available_perk_choices[1]
            player.perk_system.add_perk(chosen)
            if chosen == PerkType.SHIELD:
                player.reset_shield()
            if chosen == PerkType.DRONE:
                d = Drone(player, asteroids)
                player.drone = d
            game_state.waiting_for_perk_selection = False
            game_state.available_perk_choices = []


def draw_hud(screen, player, game_state, font_large, font_small):
    score_text = f"Score: {game_state.score}"
    draw_text(screen, score_text, font_large, (255, 100, 100), (SCREEN_WIDTH - 300, UI_PADDING))
    level_text = f"Level: {player.level_system.current_level}/{player.level_system.MAX_LEVEL}"
    draw_text(screen, level_text, font_large, (255, 255, 0), (UI_PADDING, UI_PADDING))
    xp_bar_width = 200
    xp_bar_height = 20
    xp_bar_x = UI_PADDING
    xp_bar_y = UI_PADDING + UI_FONT_SIZE + 10
    pygame.draw.rect(screen, (100, 100, 100), (xp_bar_x, xp_bar_y, xp_bar_width, xp_bar_height))
    progress = player.level_system.get_progress_to_next_level()
    fill_width = int(xp_bar_width * progress)
    pygame.draw.rect(screen, (0, 255, 100), (xp_bar_x, xp_bar_y, fill_width, xp_bar_height))
    pygame.draw.rect(screen, (255, 255, 255), (xp_bar_x, xp_bar_y, xp_bar_width, xp_bar_height), 2)


def draw_perk_selection(screen, game_state, font_large, font_small):
    if not game_state.waiting_for_perk_selection:
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    title_text = "LEVEL UP! Choose a Perk:"
    title_surface = font_large.render(title_text, True, (255, 215, 0))
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
    screen.blit(title_surface, title_rect)
    button_width = 400
    button_height = 80
    button_y_start = 250
    button_spacing = 150
    from perks2 import Perk
    for i, perk_type in enumerate(game_state.available_perk_choices):
        perk = Perk(perk_type)
        button_x = (SCREEN_WIDTH // 2) - (button_width // 2)
        button_y = button_y_start + (i * button_spacing)
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        color = (255, 100, 0) if game_state.selected_perk_index == i else (200, 200, 200)
        pygame.draw.rect(screen, color, button_rect)
        pygame.draw.rect(screen, (255, 255, 255), button_rect, 3)
        name_surface = font_large.render(perk.name, True, (0, 0, 0))
        name_rect = name_surface.get_rect(center=(button_x + button_width // 2, button_y + 20))
        screen.blit(name_surface, name_rect)
        desc_surface = font_small.render(perk.description, True, (0, 0, 0))
        desc_rect = desc_surface.get_rect(center=(button_x + button_width // 2, button_y + 50))
        screen.blit(desc_surface, desc_rect)
        key = str(i + 1)
        key_surface = font_small.render(f"Press {key}", True, (100, 100, 100))
        key_rect = key_surface.get_rect(center=(button_x + button_width // 2, button_y + 65))
        screen.blit(key_surface, key_rect)


def draw_laser(screen, player):
    # draw a beam from player forward
    direction = pygame.Vector2(0, 1).rotate(player.rotation)
    start = player.position
    length = max(SCREEN_WIDTH, SCREEN_HEIGHT) * 1.5
    end = start + direction * length
    pygame.draw.line(screen, (255, 50, 50), start, end, 4)


def line_intersects_circle(p1, p2, circle_pos, circle_r):
    # check distance from circle center to segment
    d = p2 - p1
    f = p1 - circle_pos
    a = d.dot(d)
    b = 2 * f.dot(d)
    c = f.dot(f) - circle_r * circle_r
    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return False
    discriminant = discriminant ** 0.5
    t1 = (-b - discriminant) / (2 * a)
    t2 = (-b + discriminant) / (2 * a)
    if (0 <= t1 <= 1) or (0 <= t2 <= 1):
        return True
    return False


def run_game(screen, font_large, font_small, clock):
    dt = 0
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()

    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable,)
    Shot.containers = (shots, drawable, updatable)
    Player.containers = (updatable, drawable)
    Drone.containers = (updatable, drawable)

    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    asteroid_field = AsteroidField(player)
    game_state = GameState()
    highscore_manager = HighscoreManager()
    
    game_over = False

    while True:
        log_state()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if not game_over:
                handle_perk_selection(game_state, player, asteroids, event)
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    return "MENU"
        if not game_over and not game_state.waiting_for_perk_selection:
            updatable.update(dt)
            # handle collisions
            for roid in list(asteroids):
                # laser collisions
                if player.laser_timer > 0 and player.perk_system.has_laser():
                    p1 = player.position
                    p2 = player.position + pygame.Vector2(0,1).rotate(player.rotation) * max(SCREEN_WIDTH, SCREEN_HEIGHT) * 1.5
                    if line_intersects_circle(p1, p2, roid.position, roid.radius):
                        roid.split()
                        game_state.score += 10
                        if player.add_xp(1):
                            game_state.waiting_for_perk_selection = True
                            game_state.available_perk_choices = player.perk_system.get_random_perks(2)
                        continue
                if roid.collides_with(player):
                    log_event("player_hit")
                    if player.take_damage():
                        log_event("game_over")
                        game_over = True
                        highscore_manager.add_score("Player", game_state.score, player.level_system.current_level)
                    else:
                        log_event("shield_hit")
                        for asteroid in list(asteroids):
                            asteroid.kill()
                        asteroid_field.spawn_timer = 0
                        player.position.x = SCREEN_WIDTH / 2
                        player.position.y = SCREEN_HEIGHT / 2
                for shot in list(shots):
                    if roid.collides_with(shot):
                        log_event("asteroid_shot")
                        # apply hit
                        roid.split()
                        game_state.score += 10
                        if player.add_xp(1):
                            game_state.waiting_for_perk_selection = True
                            game_state.available_perk_choices = player.perk_system.get_random_perks(2)
                        # shot behavior: piercing or ricochet
                        if getattr(shot, 'piercing', False):
                            pass
                        elif getattr(shot, 'ricochet_remaining', 0) > 0:
                            shot.ricochet_remaining -= 1
                            # Calculate ricochet direction: from collision point (shot.position) away from asteroid center (roid.position)
                            ricochet_dir = (shot.position - roid.position).normalize()
                            new_shot = Shot(shot.position.x, shot.position.y, owner=shot.owner)
                            new_shot.velocity = ricochet_dir * shot.velocity.length()
                            new_shot.ricochet_remaining = shot.ricochet_remaining
                            new_shot.piercing = shot.piercing
                            new_shot.pierce_count = getattr(shot, 'pierce_count', 0)
                            shots.add(new_shot)
                            shot.kill()
                        else:
                            shot.kill()
        screen.fill("black")
        if not game_over:
            for draws in drawable:
                draws.draw(screen)
            # draw laser if active
            if player.laser_timer > 0 and player.perk_system.has_laser():
                draw_laser(screen, player)
            draw_hud(screen, player, game_state, font_large, font_small)
            draw_perk_selection(screen, game_state, font_large, font_small)
        else:
            # game over screen
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(220)
            overlay.fill((0,0,0))
            screen.blit(overlay, (0,0))
            title = font_large.render("GAME OVER", True, (255,50,50))
            screen.blit(title, (SCREEN_WIDTH//2 - 150, 100))
            stats_y = 250
            score_text = font_small.render(f"Final Score: {game_state.score}", True, (255,200,100))
            screen.blit(score_text, (SCREEN_WIDTH//2 - 200, stats_y))
            level_text = font_small.render(f"Level Reached: {player.level_system.current_level}", True, (255,200,100))
            screen.blit(level_text, (SCREEN_WIDTH//2 - 200, stats_y + 40))
            is_highscore = highscore_manager.is_highscore(game_state.score)
            if is_highscore:
                hs_text = font_small.render("★ NEW HIGHSCORE! ★", True, (255,215,0))
                screen.blit(hs_text, (SCREEN_WIDTH//2 - 200, stats_y + 80))
            instruction = font_small.render("Press SPACE to return to menu...", True, (150,150,150))
            screen.blit(instruction, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT - 60))
        pygame.display.flip()
        dt = clock.tick(60) / 1000


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Blast Asteroids")
    font_large = pygame.font.Font(None, UI_FONT_SIZE)
    font_small = pygame.font.Font(None, UI_SMALL_FONT_SIZE)
    clock = pygame.time.Clock()
    menu = MenuScreen()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            action = menu.handle_input(event)
            if action == "NEW_GAME":
                result = run_game(screen, font_large, font_small, clock)
                if result == "QUIT":
                    return
                break
            elif action == "EXIT":
                return
        menu.draw(screen)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
