import pygame
from settings import *
from sprite_loader import SpriteLoader

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.sprites = SpriteLoader.get_player_sprites()
        self.image = self.sprites['idle']
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # Movement
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = PLAYER_MOVE_SPEED
        self.gravity = GRAVITY
        self.jump_speed = PLAYER_JUMP_SPEED
        
        # State
        self.facing_right = True
        self.on_ground = False
        self.is_ducking = False
        self.hp = 3
        self.invincible = False
        self.invinc_timer = 0
        
        # Dash
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_cooldown = 0
        
        # Shooting
        self.shoot_cooldown = 0
        
        # Animation
        self.state = 'idle'
        self.frame_index = 0
        self.animation_speed = 0.15

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_DOWN] and self.on_ground:
            self.is_ducking = True
            self.direction.x = 0 # Can't move while ducking
        else:
            self.is_ducking = False

        if not self.is_ducking:
            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.facing_right = True
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.facing_right = False
            else:
                self.direction.x = 0

        if keys[pygame.K_SPACE] and self.on_ground and not self.is_ducking:  # Space for Jump
            self.jump()

            
        if keys[pygame.K_c] and not self.is_dashing and self.dash_cooldown == 0:  # C for Dash
            self.start_dash()

    def start_dash(self):
        self.is_dashing = True
        self.dash_timer = PLAYER_DASH_DURATION
        self.dash_cooldown = 30 # half second approx
        self.direction.y = 0 # No gravity during dash

    def handle_dash(self):
        if self.is_dashing:
            self.direction.x = 1 if self.facing_right else -1
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.is_dashing = False
        
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1

    def get_shoot_direction(self):
        keys = pygame.key.get_pressed()
        dir_vec = pygame.math.Vector2(0, 0)
        
        if keys[pygame.K_RIGHT]: dir_vec.x = 1
        elif keys[pygame.K_LEFT]: dir_vec.x = -1
        
        if keys[pygame.K_UP]: dir_vec.y = -1
        elif keys[pygame.K_DOWN]: dir_vec.y = 1
        
        # Default to facing direction if no movement key held
        if dir_vec.length() == 0:
            dir_vec.x = 1 if self.facing_right else -1
            
        return dir_vec.normalize()

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def jump(self):
        self.direction.y = self.jump_speed
        self.on_ground = False

    def animate(self):
        # Animation logic
        if self.is_dashing:
            self.image = self.sprites['jump']
        elif not self.on_ground:
            self.image = self.sprites['jump']
        elif self.is_ducking:
            self.image = self.sprites['duck']
        elif self.direction.x != 0:
            self.state = 'walk'
            self.frame_index += self.animation_speed
            if self.frame_index >= 2: self.frame_index = 0
            img_key = 'walk_a' if self.frame_index < 1 else 'walk_b'
            self.image = self.sprites[img_key]
        else:
            self.state = 'idle'
            self.image = self.sprites['idle']

        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

        # Flash effect when invincible
        if self.invincible and (pygame.time.get_ticks() // 100) % 2 == 0:
            self.image = self.image.copy()
            self.image.fill((255, 255, 255, 150), special_flags=pygame.BLEND_RGBA_MULT)


    def take_damage(self):
        if not self.invincible and not self.is_dashing:
            self.hp -= 1
            self.invincible = True
            self.invinc_timer = 60 # 1 second

    def update(self):
        if self.invinc_timer > 0:
            self.invinc_timer -= 1
            if self.invinc_timer == 0:
                self.invincible = False

        self.get_input()
        self.handle_dash()
        
        if not self.is_dashing:
            self.rect.x += self.direction.x * self.speed
            self.apply_gravity()
        else:
            self.rect.x += self.direction.x * PLAYER_DASH_SPEED
        
        # Screen Boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
            self.direction.y = 0
        
        # Floor collision (simple)
        if self.rect.bottom >= SCREEN_HEIGHT - 50:
            self.rect.bottom = SCREEN_HEIGHT - 50
            self.direction.y = 0
            self.on_ground = True
        
        self.animate()
