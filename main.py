import pygame
import sys
from settings import *
from sprite_loader import SpriteLoader
from player import Player, Ghost
from boss import Boss
from bullets import Bullet, BossBullet
from overworld import OverworldPlayer, OverworldNode, Island1, Island2

class Battle:
    def __init__(self, screen, boss_type='slime'):
        self.screen = screen
        self.clock = pygame.time.Clock()
        
        # Sprite Groups
        self.player_group = pygame.sprite.GroupSingle()
        self.player = Player(100, SCREEN_HEIGHT - 150)
        self.player_group.add(self.player)

        self.boss_group = pygame.sprite.GroupSingle()
        self.boss = Boss(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 200, boss_type)
        self.boss_group.add(self.boss)

        self.bullets = pygame.sprite.Group()
        self.boss_bullets = pygame.sprite.Group()
        self.ghost_group = pygame.sprite.Group()
        self.game_state = 'PLAYING' # PLAYING, KNOCKOUT, GAMEOVER
        
        # Shooting
        self.shoot_timer = 0
        self.shoot_cooldown = 15 # default frames

        # Background
        self.background = SpriteLoader.get_background()

    def handle_events(self):
        action = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.game_state == 'PLAYING':
                    # Check for shoot
                    if event.key == pygame.K_x and self.shoot_timer >= self.shoot_cooldown:
                        self.shoot()
                        self.shoot_timer = 0
                if event.key == pygame.K_r and (self.game_state in ['GAMEOVER', 'KNOCKOUT']): # R to restart
                    action = 'RESTART'
                if event.key == pygame.K_m and self.game_state == 'GAMEOVER': # M to Equip
                    action = 'MENU'
                if event.key == pygame.K_ESCAPE: # Back to overworld
                    action = 'OVERWORLD'
        
        if action:
            return action
        keys = pygame.key.get_pressed()
        if keys[pygame.K_x] and self.game_state == 'PLAYING':
            # Adjust cooldown if player has speed power
            cooldown = self.shoot_cooldown
            if 'speed' in self.player.powers:
                cooldown = 8 # Much faster
                
            if self.shoot_timer >= cooldown:
                self.shoot()
                self.shoot_timer = 0
                
        return None

    def shoot(self):
        direction = self.player.get_shoot_direction()
        scale = 0.7
        if 'wide' in self.player.powers:
            scale = 1.2
        bullet = Bullet(self.player.rect.centerx, self.player.rect.centery, direction, scale)
        self.bullets.add(bullet)

    def boss_shoot(self):
        if self.boss.alive() and self.game_state == 'PLAYING' and self.boss.phase != 'intro':
            attack_settings = self.boss.get_attack_settings()
            for b_type, scale, speed, angle in attack_settings:
                bullet = BossBullet(
                    self.boss.rect.centerx, 
                    self.boss.rect.centery, 
                    self.player.rect.centerx, 
                    self.player.rect.centery,
                    bullet_type=b_type,
                    scale=scale,
                    speed=speed,
                    angle_offset=angle
                )
                self.boss_bullets.add(bullet)

    def update(self):
        if self.game_state == 'KNOCKOUT':
            self.boss_group.update()
            return

        if self.player.hp <= 0:
            if self.game_state == 'PLAYING':
                self.game_state = 'GAMEOVER'
                self.ghost_group.add(Ghost(self.player.rect.center))
                self.player.kill()
            self.ghost_group.update()
            return

        self.shoot_timer += 1
        self.player_group.update()
        self.boss_group.update()
        self.bullets.update()
        self.boss_bullets.update()

        # Check for boss defeat
        if self.boss.health <= 0 and self.boss.phase == 'phase2':
            self.game_state = 'KNOCKOUT'
            self.boss.trigger_death()
            return

        # Boss shooting logic
        self.boss.shoot_timer += 1
        if self.boss.shoot_timer >= self.boss.shoot_cooldown:
            self.boss_shoot()
            self.boss.shoot_timer = 0

        # Player Bullets -> Boss
        hits = pygame.sprite.spritecollide(self.boss, self.bullets, True)
        if self.boss.alive():
            for hit in hits:
                self.boss.take_damage(5)

        # Boss Bullets -> Player
        if pygame.sprite.spritecollide(self.player, self.boss_bullets, True):
            self.player.take_damage()

        # Boss Touch -> Player
        if pygame.sprite.spritecollide(self.player, self.boss_group, False):
            self.player.take_damage()

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        pygame.draw.rect(self.screen, GREEN, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
        
        self.player_group.draw(self.screen)
        self.boss_group.draw(self.screen)
        self.bullets.draw(self.screen)
        self.boss_bullets.draw(self.screen)
        self.ghost_group.draw(self.screen)
        
        if self.game_state == 'PLAYING':
            self.draw_player_hp()
        
        if self.game_state == 'KNOCKOUT':
            font = pygame.font.SysFont('Arial', 100, bold=True)
            win_text = font.render("KNOCKOUT!", True, RED)
            self.screen.blit(win_text, (SCREEN_WIDTH//2 - win_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            font_small = pygame.font.SysFont('Arial', 36)
            restart_text = font_small.render("Press R to return to Map", True, BLACK)
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
        
        if self.game_state == 'GAMEOVER':
            self.draw_death_screen()

        pygame.display.flip()

    def draw_death_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        font_big = pygame.font.SysFont('Arial', 100, bold=True)
        died_text = font_big.render("YOU DIED", True, RED)
        self.screen.blit(died_text, (SCREEN_WIDTH//2 - died_text.get_width()//2, 100))
        
        # Progress bar logic
        phase_map = {'intro': 0, 'phase1': 1, 'phase2': 2}
        base_progress = phase_map.get(self.boss.phase, 0) / 3.0
        phase_percent = (100 - self.boss.health) / 100.0 / 3.0
        total_progress = base_progress + phase_percent

        bar_w, bar_h = 600, 40
        bar_x = (SCREEN_WIDTH - bar_w) // 2
        bar_y = SCREEN_HEIGHT // 2
        pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(self.screen, (200, 0, 0), (bar_x, bar_y, int(bar_w * total_progress), bar_h))
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 4)

        # Markers & Labels
        font_small = pygame.font.SysFont('Arial', 24, bold=True)
        markers = [("Intro", 0), ("Phase 1", 1/3), ("Phase 2", 2/3), ("Finish", 1.0)]
        for label, pos in markers:
            mx = bar_x + int(bar_w * pos)
            pygame.draw.line(self.screen, WHITE, (mx, bar_y), (mx, bar_y + bar_h), 2)
            lbl = font_small.render(label, True, WHITE)
            self.screen.blit(lbl, (mx - lbl.get_width()//2, bar_y + bar_h + 10))

        # Progress Indicator (Yellow Circle)
        indicator_x = bar_x + int(bar_w * total_progress)
        pygame.draw.circle(self.screen, (255, 255, 0), (indicator_x, bar_y + bar_h//2), 15)

        restart_font = pygame.font.SysFont('Arial', 36)
        restart_text = restart_font.render("Press R to return to Map | M to Equip", True, WHITE)
        self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT - 100))

    def draw_player_hp(self):
        font = pygame.font.SysFont('Arial', 32, bold=True)
        hp_text = f"HP. {max(0, self.player.hp)}"
        color = YELLOW if self.player.hp > 1 else RED
        shadow = font.render(hp_text, True, BLACK)
        text = font.render(hp_text, True, color)
        self.screen.blit(shadow, (22, SCREEN_HEIGHT - 48))
        self.screen.blit(text, (20, SCREEN_HEIGHT - 50))

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Cuphead Kenney Edition")
        self.clock = pygame.time.Clock()
        
        # Persistent Global State
        self.global_player_data = {
            'coins': 10,
            'max_hp_base': 3,
            'powers': [], # Owned powers
            'equipped_powers': [], # Active powers
            'defeated_bosses': [], # List of boss names/types defeated
            'has_key': False, # Golden key to Island 2
            'is_portal_unlocked': False, # Whether the door is open
            'current_island': 1 # Track which island we're on
        }
        
        self.state = 'OVERWORLD'
        self.overworld = Island1(
            self.screen, 
            self.global_player_data['defeated_bosses'],
            self.global_player_data['has_key'],
            self.global_player_data['is_portal_unlocked']
        )
        self.battle = None
        self.shop = None
        self.menu = None

    def run(self):
        while True:
            if self.state == 'OVERWORLD':
                events = pygame.event.get()
                node_type, node_name = self.overworld.run(events)
                if node_type == 'BATTLE':
                    self.battle = Battle(self.screen, node_name)
                    # Sync persistent data to battle player
                    self.battle.player.coins = self.global_player_data['coins']
                    
                    # Calculate HP: Base + 1 for each 'hp' power equipped
                    extra_hp = self.global_player_data['equipped_powers'].count('hp')
                    self.battle.player.max_hp = self.global_player_data['max_hp_base'] + extra_hp
                    self.battle.player.hp = self.battle.player.max_hp
                    
                    # Only sync EQUIPPED powers to the battle player
                    self.battle.player.powers = self.global_player_data['equipped_powers']
                    self.state = 'BATTLE'
                elif node_type == 'PORTAL':
                    if self.global_player_data['has_key']:
                        if not self.global_player_data['is_portal_unlocked']:
                            # Step 1: Unlock
                            self.global_player_data['is_portal_unlocked'] = True
                            # Refresh overworld to show open door
                            self.overworld = Island1(
                                self.screen, 
                                self.global_player_data['defeated_bosses'],
                                self.global_player_data['has_key'],
                                self.global_player_data['is_portal_unlocked']
                            )
                        else:
                            # Step 2: Enter
                            self.global_player_data['current_island'] = 2
                            self.state = 'ISLAND2'
                            self.overworld = Island2(self.screen, self.global_player_data['defeated_bosses'])
                elif node_type == 'SHOP':
                    from shop import Shop
                    self.shop = Shop(self.screen)
                    self.shop.coins = self.global_player_data['coins']
                    self.shop.owned_powers = self.global_player_data['powers']
                    self.state = 'SHOP'
                
                # Overworld event loop
                for event in events:
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_m:
                            from menu import Menu
                            self.menu = Menu(self.screen, self.global_player_data)
                            self.state = 'MENU'
                
                pygame.display.flip()

            elif self.state == 'BATTLE':
                action = self.battle.handle_events()
                if action == 'RESTART' or action == 'OVERWORLD':
                    if self.battle.game_state == 'KNOCKOUT':
                        self.global_player_data['coins'] += 5
                        # Record boss as defeated
                        if self.battle.boss.boss_type not in self.global_player_data['defeated_bosses']:
                            self.global_player_data['defeated_bosses'].append(self.battle.boss.boss_type)
                        
                        # Check for all bosses defeated to award key
                        if len(self.global_player_data['defeated_bosses']) == 3:
                            self.global_player_data['has_key'] = True
                    
                    self.state = 'OVERWORLD'
                    # Re-instantiate overworld to reflect changes (flag colors & portal)
                    if self.global_player_data['current_island'] == 1:
                        self.overworld = Island1(
                            self.screen, 
                            self.global_player_data['defeated_bosses'],
                            self.global_player_data['has_key'],
                            self.global_player_data['is_portal_unlocked']
                        )
                    else:
                        self.overworld = Island2(self.screen, self.global_player_data['defeated_bosses'])
                    self.battle = None 
                elif action == 'MENU':
                    from menu import Menu
                    self.menu = Menu(self.screen, self.global_player_data)
                    self.state = 'MENU'
                    self.battle = None # Clear battle since we're switching
                else:
                    self.battle.update()
                    self.battle.draw()

            elif self.state == 'SHOP':
                action = self.shop.handle_events()
                if action == 'OVERWORLD':
                    self.global_player_data['coins'] = self.shop.coins
                    # Just add bought items to owned powers
                    for power_id in self.shop.purchased_items:
                        if power_id not in self.global_player_data['powers'] or power_id == 'hp':
                            self.global_player_data['powers'].append(power_id)
                    
                    self.state = 'OVERWORLD'
                    self.shop = None
                else:
                    self.shop.draw()

            elif self.state == 'MENU':
                action = self.menu.handle_events()
                if action == 'OVERWORLD':
                    self.state = 'OVERWORLD'
                    self.menu = None
                else:
                    self.menu.draw()

            elif self.state == 'ISLAND2':
                events = pygame.event.get()
                action = self.overworld.run(events) # It can return 'OVERWORLD' or node interactions
                
                for event in events:
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r: # R to return to World Map 1
                            self.global_player_data['current_island'] = 1
                            self.state = 'OVERWORLD'
                            self.overworld = Island1(
                                self.screen, 
                                self.global_player_data['defeated_bosses'],
                                self.global_player_data['has_key'],
                                self.global_player_data['is_portal_unlocked']
                            )

            self.clock.tick(FPS)

    def draw_island2_screen(self):
        self.screen.fill((30, 30, 60)) # Deep blue
        font_big = pygame.font.SysFont('Arial', 80, bold=True)
        island_text = font_big.render("WELCOME TO ISLAND 2!", True, YELLOW)
        self.screen.blit(island_text, (SCREEN_WIDTH//2 - island_text.get_width()//2, 200))
        
        font_small = pygame.font.SysFont('Arial', 32)
        info_text = font_small.render("More bosses and challenges await...", True, WHITE)
        self.screen.blit(info_text, (SCREEN_WIDTH//2 - info_text.get_width()//2, 350))
        
        hint_text = font_small.render("Press R to return to Map", True, WHITE)
        self.screen.blit(hint_text, (SCREEN_WIDTH//2 - hint_text.get_width()//2, SCREEN_HEIGHT - 100))
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
