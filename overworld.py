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
    def __init__(self, pos, name, type='BATTLE', is_completed=False, has_key=False, is_portal_unlocked=False):
        super().__init__()
        if type == 'BATTLE':
            flag_color = 'green' if is_completed else 'red'
            self.image = SpriteLoader.load_image(f"{ASSET_DIR}/Sprites/Tiles/Double/flag_{flag_color}_a.png", 0.3)
        elif type == 'PORTAL':
            # Portal state: only open if BOTH has_key and is_portal_unlocked are True
            door_state = 'open' if (has_key and is_portal_unlocked) else 'closed'
            self.image = SpriteLoader.load_image(f"{ASSET_DIR}/Sprites/Tiles/Double/door_{door_state}_top.png", 0.5)
        else: # Shop
            self.image = SpriteLoader.load_image(f"{ASSET_DIR}/Sprites/Tiles/Double/door_closed_top.png", 0.5)
        self.rect = self.image.get_rect(center=pos)
        self.name = name
        self.type = type

class Island1:
    def __init__(self, screen, defeated_bosses=None, has_key=False, is_portal_unlocked=False):
        self.screen = screen
        self.tile_size = 64
        self.defeated_bosses = defeated_bosses if defeated_bosses is not None else []
        self.has_key = has_key
        self.is_portal_unlocked = is_portal_unlocked
        
        # Assets
        self.key_image = SpriteLoader.load_image(f"{ASSET_DIR}/Sprites/Tiles/Default/key_yellow.png", 0.5)
        self.grass_tile = SpriteLoader.load_image(f"{ASSET_DIR}/Sprites/Tiles/Default/terrain_grass_block_center.png", 0.5)
        self.path_tile = SpriteLoader.load_image(f"{ASSET_DIR}/Sprites/Tiles/Default/terrain_dirt_block_center.png", 0.5)
        self.water_tile = SpriteLoader.load_image(f"{ASSET_DIR}/Sprites/Tiles/Default/water_top.png", 0.5)
        self.rock_tile = SpriteLoader.load_image(f"{ASSET_DIR}/Sprites/Tiles/Default/rock.png", 0.5)
        self.tree_tile = SpriteLoader.load_image(f"{ASSET_DIR}/Sprites/Tiles/Default/hill_top.png", 0.5)
        self.house_tile = SpriteLoader.load_image(f"{ASSET_DIR}/Sprites/Tiles/Default/window.png", 0.8)

        self.player_group = pygame.sprite.GroupSingle()
        self.player = OverworldPlayer((SCREEN_WIDTH // 6, SCREEN_HEIGHT // 2)) 
        self.player_group.add(self.player)
        
        self.obstacle_group = pygame.sprite.Group()
        self.path_group = pygame.sprite.Group()
        self.node_group = pygame.sprite.Group()
        
        self.create_map()

    def create_map(self):
        # G: Grass, W: Water, T: Tree, R: Rock, H: House, B: Boss, P: Path, S: Shop, K: Bee, L: Ladybug, O: Portal
        map_data = [
            "WWWWGGGGGGGGGGGGGGWW",
            "WWSGPPTTGGGGGGGGGGWW",
            "WWGGPPGGGGTTTTGGGGWW",
            "WWGGPPGGGGTTTTGGGGWW",
            "WWGGPPRRRRPPGGGGGGWW",
            "WWGGPPPPPPPPGGGGGGWW",
            "WWGGGGGGHHPPGGGBGGWW",
            "WWKWGGGGHHPPGGGGGGWW",
            "WWGGWWGGGGPPPPGGGGWW",
            "WWGGWWGGGGPPPPGOGGWW", # Added Portal 'O'
            "WWWWWWGGLLGGGGGGGGWW",
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
                    self.path_group.add(OverworldObstacle((x, y), self.path_tile)) 
                elif tile == 'B':
                    is_completed = "slime" in self.defeated_bosses
                    self.node_group.add(OverworldNode((x + self.tile_size//2, y + self.tile_size//2), "slime", 'BATTLE', is_completed))
                elif tile == 'K':
                    is_completed = "bee" in self.defeated_bosses
                    self.node_group.add(OverworldNode((x + self.tile_size//2, y + self.tile_size//2), "bee", 'BATTLE', is_completed))
                elif tile == 'L':
                    is_completed = "ladybug" in self.defeated_bosses
                    self.node_group.add(OverworldNode((x + self.tile_size//2, y + self.tile_size//2), "ladybug", 'BATTLE', is_completed))
                elif tile == 'S':
                    self.node_group.add(OverworldNode((x + self.tile_size//2, y + self.tile_size//2), "Porkind's Emporium", 'SHOP'))
                elif tile == 'O':
                    # Portal to Island 2
                    self.node_group.add(OverworldNode(
                        (x + self.tile_size//2, y + self.tile_size//2), 
                        "Portal to Island 2", 
                        'PORTAL', 
                        has_key=self.has_key,
                        is_portal_unlocked=self.is_portal_unlocked
                    ))

    def run(self, events):
        self.update()
        self.draw()
        
        # Check for encounter
        hits = pygame.sprite.spritecollide(self.player, self.node_group, False)
        if hits:
            node = hits[0]
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_x:
                    # Move player away slightly
                    self.player.pos.x -= 20 
                    return (node.type, node.name)
        return ('OVERWORLD', None)

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
        text = font.render("Use Arrow Keys to move. Press X on Node to interact!", True, BLACK)
        self.screen.blit(text, (20, 20))

        # HUD for Key
        if self.has_key:
            self.screen.blit(self.key_image, (SCREEN_WIDTH - 80, 20))
            key_text = font.render("Golden Key", True, YELLOW)
            self.screen.blit(key_text, (SCREEN_WIDTH - key_text.get_width() - 85, 25))

class Island2:
    def __init__(self, screen, defeated_bosses=None):
        self.screen = screen
        self.tile_size = 64
        self.defeated_bosses = defeated_bosses if defeated_bosses is not None else []
        
        # Assets (Using different colors for Island 2)
        self.grass_tile = SpriteLoader.load_image(f"{ASSET_DIR}/Sprites/Tiles/Default/terrain_grass_center.png", 0.5)
        # Tint grass slightly for Island 2 feel if possible, or just use different variant
        self.path_tile = SpriteLoader.load_image(f"{ASSET_DIR}/Sprites/Tiles/Default/terrain_dirt_center.png", 0.5)
        self.water_tile = SpriteLoader.load_image(f"{ASSET_DIR}/Sprites/Tiles/Default/lava_top.png", 0.5) # Lava instead of water!
        
        self.player_group = pygame.sprite.GroupSingle()
        self.player = OverworldPlayer((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)) 
        self.player_group.add(self.player)
        
        self.obstacle_group = pygame.sprite.Group()
        self.path_group = pygame.sprite.Group()
        self.node_group = pygame.sprite.Group()
        
        self.create_map()

    def create_map(self):
        # A different layout for Island 2
        map_data = [
            "LLLLLLLLLLLLLLLLLLLL",
            "LLGGGGPPPPGGGGGGGGLL",
            "LLGGGGPPPPGGGGGGGGLL",
            "LLGGPPPPGGGGGGGGGGLL",
            "LLGGPPPPGGGGGGGGGGLL",
            "LLGGPPGGGGTTGGGGGGLL",
            "LLGGPPGGGGTTGGGGGGLL",
            "LLGGPPPPGGGGGGGGGGLL",
            "LLGGGGPPPPGGGGGGGGLL",
            "LLGGGGGGPPPPGGGGGGLL",
            "LLGGGGGGGGPPGGGGGGLL",
            "LLLLLLLLLLLLLLLLLLLL",
        ]
        # L as Lava (water_tile)

        for row_index, row in enumerate(map_data):
            for col_index, tile in enumerate(row):
                x = col_index * self.tile_size
                y = row_index * self.tile_size
                
                if tile == 'L':
                    self.obstacle_group.add(OverworldObstacle((x, y), self.water_tile))
                elif tile == 'G':
                    pass # Handled by background draw
                elif tile == 'P':
                    self.path_group.add(OverworldObstacle((x, y), self.path_tile)) 

    def run(self, events):
        self.update()
        self.draw()
        return ('OVERWORLD', None)

    def update(self):
        old_pos = self.player.pos.copy()
        self.player_group.update()
        if pygame.sprite.spritecollide(self.player, self.obstacle_group, False):
            self.player.pos = old_pos
            self.player.rect.center = self.player.pos

    def draw(self):
        for x in range(0, SCREEN_WIDTH, self.grass_tile.get_width()):
            for y in range(0, SCREEN_HEIGHT, self.grass_tile.get_height()):
                self.screen.blit(self.grass_tile, (x, y))
        
        self.path_group.draw(self.screen)
        self.obstacle_group.draw(self.screen)
        self.player_group.draw(self.screen)
        
        font = pygame.font.SysFont('Arial', 24, bold=True)
        text = font.render("WELCOME TO ISLAND 2! (More bosses coming soon)", True, YELLOW)
        self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 50))
        
        hint = font.render("Press R to return to World Map", True, WHITE)
        self.screen.blit(hint, (20, SCREEN_HEIGHT - 40))
