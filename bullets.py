import pygame
import math
from settings import *
from sprite_loader import SpriteLoader

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, scale=0.7):
        super().__init__()
        self.image = SpriteLoader.get_projectile_sprite('fireball', scale) 
        # Rotate based on direction
        angle = math.degrees(math.atan2(-direction.y, direction.x))
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = 12

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        
        if not (0 <= self.rect.x <= SCREEN_WIDTH and 0 <= self.rect.y <= SCREEN_HEIGHT):
            self.kill()

class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, bullet_type='brick', scale=0.5, speed=8, angle_offset=0):
        super().__init__()
        self.image = SpriteLoader.get_projectile_sprite(bullet_type, scale)
        
        # Calculate direction to target
        direction = pygame.math.Vector2(target_x - x, target_y - y)
        if direction.length() > 0:
            self.direction = direction.normalize()
        else:
            self.direction = pygame.math.Vector2(-1, 0)
        
        # Apply angle offset for spread shots
        if angle_offset != 0:
            self.direction = self.direction.rotate(angle_offset)

        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.centerx += self.direction.x * self.speed
        self.rect.centery += self.direction.y * self.speed
        
        if not (-100 <= self.rect.centerx <= SCREEN_WIDTH + 100 and -100 <= self.rect.centery <= SCREEN_HEIGHT + 100):
            self.kill()
