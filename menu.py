import pygame
import sys
from settings import *

class Menu:
    def __init__(self, screen, player_data):
        self.screen = screen
        self.font_title = pygame.font.SysFont('Arial', 64, bold=True)
        self.font_item = pygame.font.SysFont('Arial', 32, bold=True)
        self.font_desc = pygame.font.SysFont('Arial', 20)
        
        self.player_data = player_data # Reference to global_player_data
        
        # All possible power-up definitions (for display)
        self.power_defs = {
            'hp': {'name': 'Extra Heart', 'desc': 'Adds +1 HP when equipped'},
            'speed': {'name': 'Fast Shot', 'desc': 'Doubles your fire rate'},
            'wide': {'name': 'Wide Shot', 'desc': 'Your projectiles are much larger'},
            'dash': {'name': 'Smoke Dash', 'desc': 'Better dash with faster cooldown'}
        }
        
        # Only list powers the player owns
        self.owned_power_ids = player_data['powers']
        self.selected_index = 0
        
        self.bg_color = (30, 40, 50) # Dark blueish gray

    def handle_events(self):
        action = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m or event.key == pygame.K_ESCAPE or event.key == pygame.K_z:
                    action = 'OVERWORLD'
                
                if action is None and self.owned_power_ids:
                    if event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.owned_power_ids)
                    if event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.owned_power_ids)
                    if event.key == pygame.K_x:
                        self.toggle_equip()
        return action

    def toggle_equip(self):
        power_id = self.owned_power_ids[self.selected_index]
        if power_id in self.player_data['equipped_powers']:
            self.player_data['equipped_powers'].remove(power_id)
            print(f"Unequipped {power_id}")
        else:
            # For simplicity, let's allow equipping everything, or limit to 2?
            # User said "equip what you want", so let's allow all.
            self.player_data['equipped_powers'].append(power_id)
            print(f"Equipped {power_id}")

    def draw(self):
        self.screen.fill(self.bg_color)
        
        # Title
        title_surf = self.font_title.render("EQUIPMENT", True, PINK)
        self.screen.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, 50))
        
        if not self.owned_power_ids:
            empty_surf = self.font_item.render("Inventory is Empty! Go to the shop.", True, WHITE)
            self.screen.blit(empty_surf, (SCREEN_WIDTH//2 - empty_surf.get_width()//2, SCREEN_HEIGHT//2))
        else:
            # Items list
            start_y = 200
            for i, power_id in enumerate(self.owned_power_ids):
                color = WHITE
                if i == self.selected_index:
                    color = YELLOW
                    pygame.draw.rect(self.screen, (50, 60, 70), (100, start_y + i*100 - 10, SCREEN_WIDTH - 200, 80), border_radius=10)
                    pygame.draw.rect(self.screen, YELLOW, (100, start_y + i*100 - 10, SCREEN_WIDTH - 200, 80), 3, border_radius=10)
                
                # Check if equipped
                status_text = "[ EQUIPPED ]" if power_id in self.player_data['equipped_powers'] else "[ UNEQUIPPED ]"
                status_color = GREEN if power_id in self.player_data['equipped_powers'] else RED
                
                p_def = self.power_defs.get(power_id, {'name': power_id, 'desc': ''})
                
                # Name
                name_surf = self.font_item.render(p_def['name'], True, color)
                self.screen.blit(name_surf, (150, start_y + i*100))
                
                # Description
                desc_surf = self.font_desc.render(p_def['desc'], True, WHITE)
                self.screen.blit(desc_surf, (150, start_y + i*100 + 40))
                
                # Status
                stat_surf = self.font_item.render(status_text, True, status_color)
                self.screen.blit(stat_surf, (SCREEN_WIDTH - 350, start_y + i*100 + 10))

        # Instructions
        instr_surf = self.font_desc.render("Arrows to Select | X to Equip/Unequip | M to Close", True, WHITE)
        self.screen.blit(instr_surf, (SCREEN_WIDTH//2 - instr_surf.get_width()//2, SCREEN_HEIGHT - 50))

        pygame.display.flip()
