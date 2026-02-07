import pygame
import sys
from settings import *
from sprite_loader import SpriteLoader

class Shop:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont('Arial', 64, bold=True)
        self.font_item = pygame.font.SysFont('Arial', 32, bold=True)
        self.font_desc = pygame.font.SysFont('Arial', 20)
        
        # Shop Items
        self.items = [
            {'name': 'Extra Heart', 'price': 3, 'desc': 'Gives you +1 max HP', 'id': 'hp'},
            {'name': 'Fast Shot', 'price': 3, 'desc': 'Increase your fire rate', 'id': 'speed'},
            {'name': 'Wide Shot', 'price': 4, 'desc': 'Shoots a larger projectile', 'id': 'wide'},
            {'name': 'Smoke Dash', 'price': 5, 'desc': 'Invincibility during dash is longer', 'id': 'dash'},
        ]
        self.selected_index = 0
        
        # Assets for the shop
        self.bg_color = (40, 30, 20) # Dark wooden brown
        self.coin_sprite = SpriteLoader.load_image(f"{ASSET_DIR}/Sprites/Tiles/Double/coin_gold.png", 1.0)
        
        # Game State
        self.coins = 10 
        self.owned_powers = [] # Powers already owned by player
        self.purchased_items = [] # IDs of items bought in this session

    def handle_events(self):
        action = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_z:
                    action = 'OVERWORLD'
                if action is None:
                    if event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.items)
                    if event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.items)
                    if event.key == pygame.K_x:
                        self.buy_item()
        return action

    def buy_item(self):
        item = self.items[self.selected_index]
        if self.coins >= item['price']:
            # Non-stackable check
            is_owned = item['id'] in self.owned_powers or item['id'] in self.purchased_items
            if item['id'] != 'hp' and is_owned:
                print("Already owned!")
                return
                
            self.coins -= item['price']
            self.purchased_items.append(item['id'])
            print(f"Purchased {item['name']}!")
        else:
            print("Not enough coins!")

    def draw(self):
        self.screen.fill(self.bg_color)
        
        # Title
        title_surf = self.font_title.render("PORKIND'S EMPORIUM", True, YELLOW)
        self.screen.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, 50))
        
        # Coins
        self.screen.blit(self.coin_sprite, (50, 50))
        coin_text = self.font_item.render(f"x {self.coins}", True, WHITE)
        self.screen.blit(coin_text, (110, 60))

        # Items list
        start_y = 200
        for i, item in enumerate(self.items):
            color = WHITE
            if i == self.selected_index:
                color = YELLOW
                pygame.draw.rect(self.screen, (60, 50, 40), (100, start_y + i*100 - 10, SCREEN_WIDTH - 200, 80), border_radius=10)
                pygame.draw.rect(self.screen, YELLOW, (100, start_y + i*100 - 10, SCREEN_WIDTH - 200, 80), 3, border_radius=10)
            
            # Item Name
            name_surf = self.font_item.render(item['name'], True, color)
            self.screen.blit(name_surf, (150, start_y + i*100))
            
            # Description
            desc_surf = self.font_desc.render(item['desc'], True, WHITE)
            self.screen.blit(desc_surf, (150, start_y + i*100 + 40))
            
            # Price
            price_surf = self.font_item.render(f"{item['price']}", True, YELLOW)
            self.screen.blit(price_surf, (SCREEN_WIDTH - 200, start_y + i*100 + 10))
            self.screen.blit(self.coin_sprite, (SCREEN_WIDTH - 250, start_y + i*100 + 5))

        # Instructions
        instr_surf = self.font_desc.render("Arrows to Select | X to Buy | ESC to Leave", True, WHITE)
        self.screen.blit(instr_surf, (SCREEN_WIDTH//2 - instr_surf.get_width()//2, SCREEN_HEIGHT - 50))

        pygame.display.flip()
