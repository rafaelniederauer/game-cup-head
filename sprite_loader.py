import pygame
import os
from settings import *

class SpriteLoader:
    @staticmethod
    def load_image(path, scale=1.0):
        image = pygame.image.load(path).convert_alpha()
        if scale != 1.0:
            width = int(image.get_width() * scale)
            height = int(image.get_height() * scale)
            image = pygame.transform.scale(image, (width, height))
        return image

    @staticmethod
    def get_player_sprites():
        # Using character_pink as Cuphead proxy
        base_path = f"{PLAYER_SPRITE_PATH}/character_pink_"
        states = {
            'idle': SpriteLoader.load_image(f"{base_path}idle.png", 1.0),
            'walk_a': SpriteLoader.load_image(f"{base_path}walk_a.png", 1.0),
            'walk_b': SpriteLoader.load_image(f"{base_path}walk_b.png", 1.0),
            'jump': SpriteLoader.load_image(f"{base_path}jump.png", 1.0),
            'duck': SpriteLoader.load_image(f"{base_path}duck.png", 1.0),
            'hit': SpriteLoader.load_image(f"{base_path}hit.png", 1.0),
        }

        return states

    @staticmethod
    def get_boss_sprites(boss_type='slime'):
        if boss_type == 'bee':
            base = f"{BOSS_SPRITE_PATH}/bee_"
            states = {
                'idle': SpriteLoader.load_image(f"{base}rest.png", 5),
                'walk_a': SpriteLoader.load_image(f"{base}a.png", 5),
                'walk_b': SpriteLoader.load_image(f"{base}b.png", 5),
            }
            return {'intro': states, 'phase1': states, 'phase2': states}
            
        elif boss_type == 'ladybug':
            base = f"{BOSS_SPRITE_PATH}/ladybug_"
            states = {
                'idle': SpriteLoader.load_image(f"{base}rest.png", 5),
                'walk_a': SpriteLoader.load_image(f"{base}walk_a.png", 5),
                'walk_b': SpriteLoader.load_image(f"{base}walk_b.png", 5),
                'death': SpriteLoader.load_image(f"{base}fly.png", 5),
            }
            return {'intro': states, 'phase1': states, 'phase2': states}

        # Default Slime King
        # Phase 0: Intro (Slime Spike)
        intro_base = f"{ASSET_DIR}/Sprites/Enemies/Double/slime_spike_"
        intro_states = {
            'idle': SpriteLoader.load_image(f"{intro_base}rest.png", 2.5),
            'walk_a': SpriteLoader.load_image(f"{intro_base}walk_a.png", 2.5),
            'walk_b': SpriteLoader.load_image(f"{intro_base}walk_b.png", 2.5),
        }

        # Phase 1: Normal Slime
        phase1_base = f"{BOSS_SPRITE_PATH}/slime_normal_"
        phase1_states = {
            'idle': SpriteLoader.load_image(f"{phase1_base}rest.png", 5),
            'walk_a': SpriteLoader.load_image(f"{phase1_base}walk_a.png", 5),
            'walk_b': SpriteLoader.load_image(f"{phase1_base}walk_b.png", 5),
            'death': SpriteLoader.load_image(f"{phase1_base}flat.png", 5),
        }

        # Phase 2: Fire Slime
        phase2_base = f"{BOSS_SPRITE_PATH}/slime_fire_"
        phase2_states = {
            'idle': SpriteLoader.load_image(f"{phase2_base}rest.png", 5),
            'walk_a': SpriteLoader.load_image(f"{phase2_base}walk_a.png", 5),
            'walk_b': SpriteLoader.load_image(f"{phase2_base}walk_b.png", 5),
            'death': SpriteLoader.load_image(f"{phase2_base}flat.png", 5),
        }

        return {
            'intro': intro_states,
            'phase1': phase1_states,
            'phase2': phase2_states
        }

    @staticmethod
    def get_background():
        path = f"{SPRITE_DIR}/Backgrounds/Default/background_color_hills.png"
        image = pygame.image.load(path).convert()
        image = pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        return image

    @staticmethod
    def get_projectile_sprite(projectile_type='fireball', scale=1.0):
        if projectile_type == 'brick':
            path = f"{SPRITE_DIR}/Tiles/Double/brick_brown.png"
        else:
            path = f"{SPRITE_DIR}/Tiles/Default/fireball.png"
        return SpriteLoader.load_image(path, scale)
