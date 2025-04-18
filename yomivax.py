import pygame
import random
import sys
import os

# --- Settings ---
WIDTH = 1024
HEIGHT = 768
FPS = 60

# Game State
MENU = 0
GAME = 1
PAUSE = 2
GAME_OVER = 3


game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'img')
snd_folder = os.path.join(game_folder, 'snd')

#  (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (211, 47, 47)      
GREEN = (56, 142, 60)    
BLUE = (25, 118, 210)   
YELLOW = (251, 192, 45) 
PURPLE = (171, 71, 188)  

PLAYER_SPEED = 5
BULLET_SPEED = 10
ENEMY_SPEED = 1
ENEMY_SHOOT_DELAY = 1000 # Fire second

# Power-up  
POWERUP_SHIELD = 'shield'
POWERUP_DOUBLE_SHOT = 'double'
POWERUP_SPEED = 'speed'
POWERUP_LIFE = 'life'

# --- Pygame Start ---
pygame.init()
try:
    pygame.mixer.init()
    print("Sound start!")
except pygame.error:
    print("Sound error!")
    pygame.mixer.quit()
    pygame.mixer.init()
    print("Sound restart!")

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Yomivax Space War")
clock = pygame.time.Clock()
font_name = pygame.font.match_font('arial')

# Dummy 
class DummySound:
    def play(self):
        pass
    def set_volume(self, volume):
        pass


try:
    shoot_sound = pygame.mixer.Sound(os.path.join(snd_folder, 'laser.wav'))
    shoot_sound.set_volume(0.4)
except:
    
    shoot_sound = DummySound()

try:
    explosion_sound = pygame.mixer.Sound(os.path.join(snd_folder, 'explosion.wav'))
    explosion_sound.set_volume(0.3)
except:
    explosion_sound = DummySound()

try:
    power_up_sound = pygame.mixer.Sound(os.path.join(snd_folder, 'powerup.wav'))
    power_up_sound.set_volume(0.5)
except:
    power_up_sound = DummySound()


try:
    pygame.mixer.music.load(os.path.join(snd_folder, 'background.wav'))
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(loops=-1)
except:
    pass  


def draw_text(surf, text, size, x, y, color):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color) # True: anti-aliasing
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i # 
        img_rect.y = y
        surf.blit(img, img_rect)



class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        self.original_image = pygame.image.load(os.path.join(img_folder, 'player_ship.png')).convert_alpha()
       
        self.original_image = pygame.transform.scale(self.original_image, (50, 50))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.lives = 3
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.power_level = 1
        self.power_timer = pygame.time.get_ticks()
        self.shield = False
        self.shield_timer = pygame.time.get_ticks()
        self.speed_boost = False
        self.speed_timer = pygame.time.get_ticks()

    def update(self):
        
        self.image = self.original_image.copy()  
        if self.shield:
            
            surf = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            pygame.draw.circle(surf, (100, 181, 246, 128), (self.rect.width//2, self.rect.height//2), 
                             max(self.rect.width, self.rect.height)//2, 3)
            self.image.blit(surf, (0,0))
        
        
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        current_speed = PLAYER_SPEED * 1.5 if self.speed_boost else PLAYER_SPEED
        if keystate[pygame.K_LEFT] or keystate[pygame.K_a]:
            self.speedx = -current_speed
        if keystate[pygame.K_RIGHT] or keystate[pygame.K_d]:
            self.speedx = current_speed
        self.rect.x += self.speedx
        
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

      
        now = pygame.time.get_ticks()
        if self.power_level > 1 and now - self.power_timer > 10000:
            self.power_level = 1
        if self.shield and now - self.shield_timer > 8000:
            self.shield = False
        if self.speed_boost and now - self.speed_timer > 5000:
            self.speed_boost = False

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            shoot_sound.play()
            
            if self.power_level == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                player_bullets.add(bullet)
            elif self.power_level >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                player_bullets.add(bullet1)
                player_bullets.add(bullet2)

    def powerup(self, type):
        power_up_sound.play()
        if type == POWERUP_SHIELD:
            self.shield = True
            self.shield_timer = pygame.time.get_ticks()
        elif type == POWERUP_DOUBLE_SHOT:
            self.power_level = 2
            self.power_timer = pygame.time.get_ticks()
        elif type == POWERUP_SPEED:
            self.speed_boost = True
            self.speed_timer = pygame.time.get_ticks()
        elif type == POWERUP_LIFE:
            if self.lives < 3:  
                self.lives += 1

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type=1):
        pygame.sprite.Sprite.__init__(self)
      
        try:
            if enemy_type == 1:
                self.original_image = pygame.image.load(os.path.join(img_folder, 'enemy1.png')).convert_alpha()
            elif enemy_type == 2:
                self.original_image = pygame.image.load(os.path.join(img_folder, 'enemy2.png')).convert_alpha()
            elif enemy_type == 3:
                self.original_image = pygame.image.load(os.path.join(img_folder, 'enemy3.png')).convert_alpha()
       
            self.original_image = pygame.transform.scale(self.original_image, (60, 60))
            self.image = self.original_image
        except:
          
            self.image = pygame.Surface((30, 30))
            self.image.fill(RED)
            pygame.draw.circle(self.image, YELLOW, (15, 15), 10)
            self.image.set_colorkey(RED)
            
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speedx = ENEMY_SPEED
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = random.randint(2000, 5000)

    def update(self):
        self.rect.x += self.speedx
        if self.rect.right > WIDTH or self.rect.left < 0:
            for enemy in enemies:
                enemy.speedx *= -1
                enemy.rect.y += 10

      
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            self.shoot()
            self.shoot_delay = random.randint(2000, 5000)

    def shoot(self):
        bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
        all_sprites.add(bullet)
        enemy_bullets.add(bullet)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((4, 10))
        self.image.fill(PURPLE) 
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -BULLET_SPEED

    def update(self):
        self.rect.y += self.speedy
      
        if self.rect.bottom < 0:
            self.kill() 

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((4, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speedy = BULLET_SPEED / 2  
    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

class Powerup(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice([POWERUP_SHIELD, POWERUP_DOUBLE_SHOT, POWERUP_SPEED, POWERUP_LIFE])
        
        try:
            
            if self.type == POWERUP_SHIELD:
                self.original_image = pygame.image.load(os.path.join(img_folder, 'shield_powerup.png')).convert_alpha()
            elif self.type == POWERUP_DOUBLE_SHOT:
                self.original_image = pygame.image.load(os.path.join(img_folder, 'doubleshot_powerup.png')).convert_alpha()
            elif self.type == POWERUP_SPEED:
                self.original_image = pygame.image.load(os.path.join(img_folder, 'speed_powerup.png')).convert_alpha()
            else:  
                self.original_image = pygame.image.load(os.path.join(img_folder, 'life_powerup.png')).convert_alpha()
            
           
            self.image = pygame.transform.scale(self.original_image, (40, 40))
            self.original_image = self.image 
        except:
          
            self.image = pygame.Surface((20, 20)) 
            self.image.fill(BLACK)
            self.image.set_colorkey(BLACK)
            
            if self.type == POWERUP_SHIELD:
                
                pygame.draw.circle(self.image, BLUE, (10, 10), 8, 2)
            elif self.type == POWERUP_DOUBLE_SHOT:
                
                pygame.draw.line(self.image, PURPLE, (6, 4), (6, 16), 2)
                pygame.draw.line(self.image, PURPLE, (14, 4), (14, 16), 2)
            elif self.type == POWERUP_SPEED:
                
                pygame.draw.polygon(self.image, GREEN, [(4, 10), (12, 4), (12, 7), (16, 7), (16, 13), (12, 13), (12, 16)])
            else:  # POWERUP_LIFE
                
                pygame.draw.polygon(self.image, RED, [(10, 4), (4, 10), (10, 16), (16, 10)])
            
            self.original_image = self.image.copy()  
        
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3
        
       
        self.alpha = 255
        self.alpha_change = -5
        
    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()
            
       
        self.alpha += self.alpha_change
        if self.alpha <= 100:
            self.alpha_change = 5
        elif self.alpha >= 255:
            self.alpha_change = -5
        
        try:
            
            self.image = self.original_image.copy()
            self.image.set_alpha(self.alpha)
        except:
         
            self.image.set_alpha(self.alpha)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = pygame.Surface((size, size))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.frame_rate = 50
        self.last_update = pygame.time.get_ticks()
        self.frame_speed = 75  

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_speed:
            self.last_update = now
            self.frame += 1
            if self.frame >= 8: 
                self.kill()
            else:
                center = self.rect.center
                self.image = pygame.Surface((self.size, self.size))
                self.image.fill(RED)
                self.image.set_alpha(255 - (self.frame * 30))  
                self.rect = self.image.get_rect()
                self.rect.center = center

# --- Game return ---
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
explosions = pygame.sprite.Group()
powerups = pygame.sprite.Group()

level = 1 
score = 0
game_state = MENU

def show_menu():
    screen.fill(BLACK)
    # Stars
    for _ in range(50):
        pygame.draw.circle(screen, WHITE, (random.randint(0, WIDTH), random.randint(0, HEIGHT)), 1)
    
    draw_text(screen, "YOMIVAX SPACE WAR", 64, WIDTH / 2, HEIGHT / 4, BLUE)
    draw_text(screen, "Your ship took a lot of damage!", 22, WIDTH / 2, HEIGHT / 2, WHITE)
    draw_text(screen, "Return to the space station", 22, WIDTH / 2, HEIGHT / 2 + 40, WHITE)
    draw_text(screen, "", 22, WIDTH / 2, HEIGHT / 2 + 80, WHITE)
    draw_text(screen, "", 36, WIDTH / 2, HEIGHT * 3/4, YELLOW)

def show_pause():
    s = pygame.Surface((WIDTH, HEIGHT))
    s.set_alpha(128)
    s.fill(BLACK)
    screen.blit(s, (0,0))
    draw_text(screen, "PAUSE", 64, WIDTH / 2, HEIGHT / 4, WHITE)
    draw_text(screen, "Press P to continue", 22, WIDTH / 2, HEIGHT / 2, WHITE)
    draw_text(screen, "Press ESC to exit", 22, WIDTH / 2, HEIGHT / 2 + 40, WHITE)

def new_game():
    global all_sprites, player, enemies, player_bullets, enemy_bullets, explosions, powerups
    global score, game_state, level  
    
    
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    explosions = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    
   
    player = Player()
    all_sprites.add(player)
    
   
    for row in range(4):
        for col in range(8):
            enemy_type = row % 3 + 1
            enemy = Enemy(col * 60 + 50, row * 40 + 50, enemy_type)
            enemy.speedx = ENEMY_SPEED * (1 + level * 0.1)  
            all_sprites.add(enemy)
            enemies.add(enemy)
    
   
    score = 0
    level = 1
    game_state = GAME


game_state = MENU
new_game()
running = True

while running:
    clock.tick(FPS)
    
   
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == GAME:
                    game_state = PAUSE
                else:
                    running = False
            elif event.key == pygame.K_p:
                if game_state == GAME:
                    game_state = PAUSE
                elif game_state == PAUSE:
                    game_state = GAME
            elif event.key == pygame.K_SPACE:
                if game_state == MENU:
                    new_game()
                elif game_state == GAME:
                    player.shoot()
                elif game_state == GAME_OVER:
                    game_state = MENU
    
 
    if game_state == GAME:
        all_sprites.update()
        
        
        hits = pygame.sprite.groupcollide(enemies, player_bullets, True, True)
        for hit in hits:
            score += 10 * level
            explosion_sound.play()
            expl = Explosion(hit.rect.center, 30)
            all_sprites.add(expl)
            explosions.add(expl)
            
            if random.random() < 0.1:
                pow = Powerup(hit.rect.center)
                all_sprites.add(pow)
                powerups.add(pow)
        
        hits = pygame.sprite.spritecollide(player, powerups, True)
        for hit in hits:
            player.powerup(hit.type)
        
        if not player.shield:
            hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
            if hits:
                explosion_sound.play()
                expl = Explosion(player.rect.center, 40)
                all_sprites.add(expl)
                explosions.add(expl)
                player.lives -= 1
                if player.lives <= 0:
                    game_state = GAME_OVER
        
        for enemy in enemies:
            if enemy.rect.bottom > HEIGHT - 50:
                game_state = GAME_OVER
                break
        
      
        if len(enemies) == 0:
            level += 1
            for row in range(4):
                for col in range(8):
                    enemy_type = row % 3 + 1
                    enemy = Enemy(col * 60 + 50, row * 40 + 50, enemy_type)
                    enemy.speedx = ENEMY_SPEED * (1 + level * 0.1)  
                    all_sprites.add(enemy)
                    enemies.add(enemy)
    
   
    screen.fill(BLACK)
    
    
    for _ in range(50):
        pygame.draw.circle(screen, WHITE, (random.randint(0, WIDTH), random.randint(0, HEIGHT)), 1)
    
    if game_state == MENU:
        show_menu()
    elif game_state == GAME:
        all_sprites.draw(screen)
        
       
        draw_text(screen, f"Score: {score}", 24, WIDTH / 2, 10, WHITE)
        draw_text(screen, f"Level: {level}", 24, WIDTH / 2, 40, YELLOW)
        player_mini_img = pygame.transform.scale(player.image, (15, 10))
        player_mini_img.set_colorkey(BLACK)
        draw_lives(screen, WIDTH - 100, 15, player.lives, player_mini_img)
        
       
        if player.shield:
            draw_text(screen, "Shield", 16, 70, 10, BLUE)
        if player.power_level > 1:
            draw_text(screen, "Double Shot", 16, 70, 30, PURPLE)
        if player.speed_boost:
            draw_text(screen, "Speed Boost", 16, 70, 50, GREEN)
    elif game_state == PAUSE:
        all_sprites.draw(screen)
        show_pause()
    elif game_state == GAME_OVER:
        all_sprites.draw(screen)
        draw_text(screen, "GAME OVER!", 64, WIDTH / 2, HEIGHT / 4, RED)
        draw_text(screen, f"Final Score: {score}", 36, WIDTH / 2, HEIGHT / 2, WHITE)
        draw_text(screen, f"Level: {level}", 36, WIDTH / 2, HEIGHT / 2 + 50, YELLOW)
        draw_text(screen, "PRESS SPACE", 22, WIDTH / 2, HEIGHT * 3/4, WHITE)
        draw_text(screen, "Press ESC to exit", 22, WIDTH / 2, HEIGHT * 3/4 + 40, WHITE)
    
    pygame.display.flip()

pygame.quit()
sys.exit()