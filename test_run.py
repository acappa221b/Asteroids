#!/usr/bin/env python3
"""Test script to debug the game startup"""

import sys
import traceback

try:
    print("Starting imports...")
    import pygame
    print("✓ pygame imported")
    
    from constants import SCREEN_WIDTH, SCREEN_HEIGHT
    print("✓ constants imported")
    
    from player import Player
    print("✓ player imported")
    
    from perks import PerkType
    print("✓ perks imported")
    
    from shot import Shot
    print("✓ shot imported")
    
    from drone import Drone
    print("✓ drone imported")
    
    from asteroidfield import AsteroidField
    print("✓ asteroidfield imported")
    
    from asteroid import Asteroid  
    print("✓ asteroid imported")
    
    from menu import MenuScreen
    print("✓ menu imported")
    
    from highscores import HighscoreManager
    print("✓ highscores imported")
    
    from logger import log_state, log_event
    print("✓ logger imported")
    
    print("\n✓ All imports successful!")
    print("Game should be able to start normally.")
    
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {e}")
    traceback.print_exc()
    sys.exit(1)
