import pygame
import sys
from settings import *
from sprite_loader import SpriteLoader
from player import Player, Ghost
from boss import Boss
from bullets import Bullet, BossBullet
from overworld import Overworld

class Battle:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        
        # Sprite Groups
        self.player_group = pygame.sprite.GroupSingle()
        self.player = Player(100, SCREEN_HEIGHT - 150)
        self.player_group.add(self.player)

        self.boss_group = pygame.sprite.GroupSingle()
        self.boss = Boss(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 200)
        self.boss_group.add(self.boss)

        self.bullets = pygame.sprite.Group()
        self.boss_bullets = pygame.sprite.Group()
        self.ghost_group = pygame.sprite.Group()
        self.game_state = 'PLAYING' # PLAYING, KNOCKOUT, GAMEOVER

        # Background
        self.background = SpriteLoader.get_background()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.game_state == 'PLAYING':
                    if event.key == pygame.K_x:  # X for Shoot
                        self.shoot()
                if event.key == pygame.K_r and (self.game_state in ['GAMEOVER', 'KNOCKOUT']): # R to restart
                    return 'RESTART'
                if event.key == pygame.K_ESCAPE: # Back to overworld
                    return 'OVERWORLD'
        return None

    def shoot(self):
        direction = self.player.get_shoot_direction()
        bullet = Bullet(self.player.rect.centerx, self.player.rect.centery, direction)
        self.bullets.add(bullet)

    def boss_shoot(self):
        if self.boss.alive() and self.game_state == 'PLAYING' and self.boss.phase != 'intro':
            bullet = BossBullet(self.boss.rect.centerx, self.boss.rect.centery, self.player.rect.centerx, self.player.rect.centery)
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
        restart_text = restart_font.render("Press R to return to Map", True, WHITE)
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
        self.state = 'OVERWORLD'
        self.overworld = Overworld(self.screen)
        self.battle = None

    def run(self):
        while True:
            if self.state == 'OVERWORLD':
                result = self.overworld.run()
                if result == 'BATTLE':
                    self.battle = Battle(self.screen)
                    self.state = 'BATTLE'
                
                # Overworld event loop
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                
                pygame.display.flip()

            elif self.state == 'BATTLE':
                action = self.battle.handle_events()
                if action == 'RESTART' or action == 'OVERWORLD':
                    self.state = 'OVERWORLD'
                    self.battle = None # Clear battle state
                else:
                    self.battle.update()
                    self.battle.draw()

            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
