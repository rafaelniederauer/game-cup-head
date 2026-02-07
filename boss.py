import pygame
import random
import math
from settings import *
from sprite_loader import SpriteLoader

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, boss_type='slime'):
        super().__init__()
        self.boss_type = boss_type
        self.all_sprites = SpriteLoader.get_boss_sprites(boss_type)
        self.phase = 'intro'
        self.state = 'idle'
        self.sprites = self.all_sprites['intro']
        self.image = self.sprites['idle']
        self.rect = self.image.get_rect(center=(x, y))
        
        self.health = 100
        self.max_health = 100
        self.attack_timer = 0
        self.shoot_timer = 0
        
        # Base settings based on boss type
        if self.boss_type == 'bee':
            self.shoot_cooldown = 45 # Fast shooting
        elif self.boss_type == 'ladybug':
            self.shoot_cooldown = 150 # Slow shooting (block shots)
        else: # slime or default
            self.shoot_cooldown = 120
            
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

        # Phase logic depends on boss type
        if self.phase == 'intro':
            self.move_intro()
        elif self.phase == 'phase1':
            self.move_phase1()
        elif self.phase == 'phase2':
            self.move_phase2()

    def move_intro(self):
        # Default intro movement: Horizontal jumping (used by Slime and Ladybug)
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

        if self.boss_type == 'bee':
            # Bee intro is faster and doesn't jump as much
            self.velocity_y = 0
            self.rect.centery = SCREEN_HEIGHT // 2
            self.rect.x += self.direction_x * 10 # Speed boost for bee intro

    def move_phase1(self):
        if self.boss_type == 'bee':
            # Figure-eight hovering
            t = pygame.time.get_ticks() * 0.002
            self.rect.centerx = SCREEN_WIDTH // 2 + math.cos(t) * 300
            self.rect.centery = SCREEN_HEIGHT // 3 + math.sin(t * 2) * 100
        elif self.boss_type == 'ladybug':
            # Ground patrol: Horizontal walking
            self.rect.x += self.direction_x * 7
            self.rect.bottom = SCREEN_HEIGHT - 50
            if self.rect.left <= 50 or self.rect.right >= SCREEN_WIDTH - 50:
                self.direction_x *= -1
        else: # Slime or default
            # Phase 1 Slime: Stays still (original used sine wave and horizontal movement)
            # We just ensure it's at a good height
            self.rect.bottom = SCREEN_HEIGHT - 50

    def move_phase2(self):
        if self.boss_type == 'ladybug':
            # Ceiling hang: Move to top and strafe
            if self.rect.top > 50:
                self.rect.y -= 5
            else:
                self.rect.x += self.direction_x * 8
                if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
                    self.direction_x *= -1
        elif self.boss_type == 'bee':
            # Tight Orbit: Strafe back and forth with vertical sine wave
            self.rect.x += self.direction_x * 12
            self.rect.y = 150 + math.sin(pygame.time.get_ticks() * 0.01) * 50
            if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
                self.direction_x *= -1
        else: # Slime or default
            # Fly at the top (original behavior)
            if self.rect.top > 50:
                self.rect.y -= 5
            else:
                self.rect.x += self.direction_x * 10
                if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
                    self.direction_x *= -1

    def get_attack_settings(self):
        """Returns a list of bullet parameters (bullet_type, scale, speed, angle_offset)"""
        settings = []
        
        if self.boss_type == 'ladybug':
            if self.phase == 'phase2':
                # Dropping block shots from ceiling
                settings.append(('brick', 1.5, 10, 90)) # Shoot downwards
            else:
                # Standard ground block shot
                settings.append(('brick', 1.5, 6, 0))
        elif self.boss_type == 'bee':
            if self.phase == 'phase2':
                # Burst of stingers, but slower (was speed 15)
                settings.append(('brick', 0.4, 8, -10))
                settings.append(('brick', 0.4, 8, 0))
                settings.append(('brick', 0.4, 8, 10))
            else:
                # Standard stinger, but slower (was speed 15)
                settings.append(('brick', 0.4, 10, 0))
        else: # slime
            # Revert Phase 2 speed to Phase 1 speed (8)
            settings.append(('brick', 0.5, 8, 0))
                
        return settings

    def transition_to_phase(self, new_phase):
        self.phase = new_phase
        self.sprites = self.all_sprites[new_phase]
        self.health = 100 # Reset health for new phase
        if new_phase == 'phase2':
            if self.boss_type == 'bee':
                self.shoot_cooldown = 100 # Slower shooting in Phase 2 (was 30)
            elif self.boss_type == 'ladybug':
                self.shoot_cooldown = 100
            else:
                self.shoot_cooldown = 60 # Faster shooting in phase 2 for slime
        
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
