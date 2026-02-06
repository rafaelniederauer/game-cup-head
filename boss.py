import pygame
import random
import math
from settings import *
from sprite_loader import SpriteLoader

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.all_sprites = SpriteLoader.get_boss_sprites()
        self.phase = 'intro'
        self.state = 'idle'
        self.sprites = self.all_sprites['intro']
        self.image = self.sprites['idle']
        self.rect = self.image.get_rect(center=(x, y))
        
        self.health = 100
        self.max_health = 100
        self.attack_timer = 0
        self.shoot_timer = 0
        self.shoot_cooldown = 120 # every 2 seconds
        self.frame_index = 0
        self.animation_speed = 0.1
        self.death_timer = 180 # 3 seconds death animation
        self.intro_timer = 120 # 2 seconds intro
        self.direction_x = -1 # Start moving left
        self.velocity_y = 0
        self.jump_speed = -28
        self.gravity = 0.8

    def animate(self):
        if self.state == 'dying':
            self.image = self.sprites.get('death', self.sprites['idle'])
            if (pygame.time.get_ticks() // 100) % 2 == 0:
                self.image = pygame.transform.flip(self.image, True, False)
            return

        self.frame_index += self.animation_speed
        if self.frame_index >= 2: self.frame_index = 0
        img_key = 'walk_a' if self.frame_index < 1 else 'walk_b'
        self.image = self.sprites[img_key]

    def update(self):
        self.animate()
        
        if self.state == 'dying':
            self.death_timer -= 1
            if self.death_timer <= 0:
                self.kill()
            return

        if self.phase == 'intro':
            # Horizontal movement
            self.rect.x += self.direction_x * 5
            if self.rect.left <= 0:
                self.rect.left = 0
                self.direction_x = 1
            elif self.rect.right >= SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH
                self.direction_x = -1
            
            # Vertical movement (Jumping)
            self.velocity_y += self.gravity
            self.rect.y += self.velocity_y
            
            if self.rect.bottom >= SCREEN_HEIGHT - 50:
                self.rect.bottom = SCREEN_HEIGHT - 50
                self.velocity_y = self.jump_speed
            return

        if self.phase == 'phase2':
            # Move to top first
            if self.rect.top > 50:
                self.rect.y -= 5
            else:
                # Strafe at the top
                self.rect.x += self.direction_x * 10
                if self.rect.left <= 0:
                    self.rect.left = 0
                    self.direction_x = 1
                elif self.rect.right >= SCREEN_WIDTH:
                    self.rect.right = SCREEN_WIDTH
                    self.direction_x = -1
            return

        # Phase 1 logic
        self.rect.y += math.sin(pygame.time.get_ticks() * 0.005) * 2

    def transition_to_phase(self, new_phase):
        self.phase = new_phase
        self.sprites = self.all_sprites[new_phase]
        self.health = 100 # Reset health for new phase
        if new_phase == 'phase2':
            self.shoot_cooldown = 60 # Faster shooting in phase 2
        
    def trigger_death(self):
        self.state = 'dying'

    def take_damage(self, amount):
        if self.state != 'dying':
            self.health -= amount
            if self.health <= 0:
                if self.phase == 'intro':
                    self.transition_to_phase('phase1')
                elif self.phase == 'phase1':
                    self.transition_to_phase('phase2')
                else:
                    self.health = 0 # Final death will be caught by main.py
