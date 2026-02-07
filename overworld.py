import pygame
from settings import *
from sprite_loader import SpriteLoader

class OverworldPlayer(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        # Load and scale player sprites specifically for the overworld
        original_sprites = SpriteLoader.get_player_sprites()
        self.sprites = {}
        for key, img in original_sprites.items():
            w, h = img.get_size()
            self.sprites[key] = pygame.transform.scale(img, (int(w * 0.5), int(h * 0.5)))
            
        self.image = self.sprites['idle']
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(pos)
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 5

    def get_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

        if keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

    def update(self):
        self.get_input()
        self.pos += self.direction * self.speed
        self.rect.center = self.pos
        
        # Screen boundaries
        if self.rect.left < 0: 
            self.rect.left = 0
            self.pos.x = self.rect.centerx
        if self.rect.right > SCREEN_WIDTH: 
            self.rect.right = SCREEN_WIDTH
            self.pos.x = self.rect.centerx
        if self.rect.top < 0: 
            self.rect.top = 0
            self.pos.y = self.rect.centery
        if self.rect.bottom > SCREEN_HEIGHT: 
            self.rect.bottom = SCREEN_HEIGHT
            self.pos.y = self.rect.centery

class OverworldObstacle(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)

class OverworldNode(pygame.sprite.Sprite):
    def __init__(self, pos, boss_name):
        super().__init__()
        self.image = SpriteLoader.load_image(f"{ASSET_DIR}/Sprites/Tiles/Double/flag_red_a.png", 1.0)
        self.rect = self.image.get_rect(center=pos)
        self.boss_name = boss_name

class Overworld:
    def __init__(self, screen):
        self.screen = screen
        self.tile_size = 64
        
        # Assets
        self.grass_tile = SpriteLoader.load_image(f"{ASSET_DIR}/Sprites/Tiles/Default/terrain_grass_block_center.png", 0.5)
        self.path_tile = SpriteLoader.load_image(f"{ASSET_DIR}/Sprites/Tiles/Default/terrain_dirt_block_center.png", 0.5)
        self.water_tile = SpriteLoader.load_image(f"{ASSET_DIR}/Sprites/Tiles/Default/water_top.png", 0.5)
        self.rock_tile = SpriteLoader.load_image(f"{ASSET_DIR}/Sprites/Tiles/Default/rock.png", 0.5)
        self.tree_tile = SpriteLoader.load_image(f"{ASSET_DIR}/Sprites/Tiles/Default/hill_top.png", 0.5)
        self.house_tile = SpriteLoader.load_image(f"{ASSET_DIR}/Sprites/Tiles/Default/window.png", 0.8)

        self.player_group = pygame.sprite.GroupSingle()
        self.player = OverworldPlayer((SCREEN_WIDTH // 6, SCREEN_HEIGHT // 2)) # Start slightly further left
        self.player_group.add(self.player)
        
        self.obstacle_group = pygame.sprite.Group()
        self.path_group = pygame.sprite.Group()
        self.node_group = pygame.sprite.Group()
        
        self.create_map()

    def create_map(self):
        # A more 'Cuphead' island map
        # G: Grass, W: Water, T: Tree, R: Rock, H: House, B: Boss, P: Path
        map_data = [
            "WWWWWWWWWWWWWWWWWWWW",
            "WWWWWWWWWWWWWWWWWWWW",
            "WWGGPPTTGGGGGGGGGGWW",
            "WWGGPPGGGGTTTTGGGGWW",
            "WWGGPPGGGGTTTTGGGGWW",
            "WWGGPPRRRRPPGGGGGGWW",
            "WWGGPPPPPPPPGGGGGGWW",
            "WWGGGGGGHHPPGGGBGGWW",
            "WWWWWWGGHHPPGGGGGGWW",
            "WWWWWWWWWWWWWWWWWWWW",
            "WWWWWWWWWWWWWWWWWWWW",
        ]

        for row_index, row in enumerate(map_data):
            for col_index, tile in enumerate(row):
                x = col_index * self.tile_size
                y = row_index * self.tile_size
                
                if tile == 'W':
                    self.obstacle_group.add(OverworldObstacle((x, y), self.water_tile))
                elif tile == 'T':
                    self.obstacle_group.add(OverworldObstacle((x, y), self.tree_tile))
                elif tile == 'R':
                    self.obstacle_group.add(OverworldObstacle((x, y), self.rock_tile))
                elif tile == 'H':
                    self.obstacle_group.add(OverworldObstacle((x, y), self.house_tile))
                elif tile == 'P':
                    self.path_group.add(OverworldObstacle((x, y), self.path_tile)) # Use path tiles
                elif tile == 'B':
                    self.node_group.add(OverworldNode((x + self.tile_size//2, y + self.tile_size//2), "The Slime King"))

    def run(self):
        self.update()
        self.draw()
        
        # Check for encounter
        if pygame.sprite.spritecollide(self.player, self.node_group, False):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_x]:
                # Move player away slightly so it's not immediate loop if they return
                self.player.pos.x -= 20 
                return 'BATTLE'
        return 'OVERWORLD'

    def update(self):
        # Collision handling for the player
        old_pos = self.player.pos.copy()
        self.player_group.update()
        
        # Player is slowed down slightly if NOT on a path? Or just regular collisions
        if pygame.sprite.spritecollide(self.player, self.obstacle_group, False):
            self.player.pos = old_pos
            self.player.rect.center = self.player.pos

    def draw(self):
        # Fill background with grass
        for x in range(0, SCREEN_WIDTH, self.grass_tile.get_width()):
            for y in range(0, SCREEN_HEIGHT, self.grass_tile.get_height()):
                self.screen.blit(self.grass_tile, (x, y))
        
        self.path_group.draw(self.screen)
        self.obstacle_group.draw(self.screen)
        self.node_group.draw(self.screen)
        self.player_group.draw(self.screen)
        
        font = pygame.font.SysFont('Arial', 24, bold=True)
        text = font.render("Use Arrow Keys to move. Press X on Flag to Battle!", True, BLACK)
        self.screen.blit(text, (20, 20))
