import pygame

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PINK = (255, 182, 193)

# Physics
GRAVITY = 0.8
PLAYER_JUMP_SPEED = -16
PLAYER_MOVE_SPEED = 7
PLAYER_DASH_SPEED = 20
PLAYER_DASH_DURATION = 15  # frames

# Asset Paths
ASSET_DIR = "/Users/rafael/Library/Mobile Documents/com~apple~CloudDocs/Docs/Second Brain/Projects/cuphead_game/kenney_new-platformer-pack-1"
SPRITE_DIR = f"{ASSET_DIR}/Sprites"
PLAYER_SPRITE_PATH = f"{SPRITE_DIR}/Characters/Default"
BOSS_SPRITE_PATH = f"{SPRITE_DIR}/Enemies/Default"
