#imports:
import sys
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from logger import log_state, log_event
from player import Player
from asteroidfield import AsteroidField
from asteroid import Asteroid
from shot import Shot
import random



def main():
    print("Starting Asteroids with pygame version: 2.6.1")
    print(f"Screen width: {SCREEN_WIDTH}\nScreen height: {SCREEN_HEIGHT}")

    pygame.init() # Initialize all imported pygame modules
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Set up the display

    clock = pygame.time.Clock()
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
    asteroid_field = AsteroidField()
    
    
    

    while True: # Main game loop
        log_state() # Log the current state for debugging
        for event in pygame.event.get(): # Event handling loop
            if event.type == pygame.QUIT: # Handle window close event
                return
        
        updatable.update(dt)

        for roid in asteroids:
            if roid.collides_with(player):
                log_event("player_hit")
                print("Game over!")
                sys.exit()
        
        for roid in asteroids:
            for shot in shots:
                if roid.collides_with(shot):
                    log_event("asteroid_shot")
                    shot.kill()
                    roid.split()

        
        screen.fill("black") #background color
       
        for draws in drawable:
            draws.draw(screen)
               
       
        #player.draw(screen) # Draw the player on the screen

        #refresh
        pygame.display.flip() # Update the full display surface to the screen
        dt = clock.tick(60) / 1000  # Limit to 60 FPS and get delta time in seconds




if __name__ == "__main__":
    main()
