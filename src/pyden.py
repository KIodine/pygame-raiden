import pygame
import sys
import os
import random
import time

# Interstellar simulator 2017 v0.0.1

graystart = 150
graymax = 215
graylist = [(i, i, i) for i in range(graystart, graymax)]
rdgray = lambda: random.choice(graylist)

yellow_low = 180
yellowlist = [(255, 255 - i, 0) for i in range(256 - yellow_low)]
rdyellow = lambda: random.choice(yellowlist)

rds_upperlimit = 15
rds_lowerlimit = 5

rdspeed = lambda: rds_lowerlimit + rds_upperlimit * random.random()
shftspeed = lambda: random.choice([1, -1]) * (3 * random.random())
rdsize = lambda: random.choices(
    [(1, i*5) for i in range(1, 3+1)], [70, 30, 10], k=1)

dice = lambda chn: True if chn > random.random() * 100 else False

#Simple functions set.------------------------------------------------

# Use random.gause(mu, sigma) to get normal dist?

W_WIDTH = 1024
W_HEIGHT = 640
SCREEN_SIZE = (W_WIDTH, W_HEIGHT)
DEFAULT_COLOR = (14, 52, 112)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FLAKES = 512
FPS = 30



sound_file = 'music/beep1.ogg' # Need to be replaced.
bgm = 'music/Diebuster OST- Escape Velocity.mp3'
volume_ratio = 0.25

#Constants set.------------------------------------------------------

pygame.init()
pygame.display.init()
pygame.display.set_caption("Interstellar Simulator 2017")

screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
screen.fill(BLACK)

font = pygame.font.Font('fonts/msjh.ttf', 24)

screct = screen.get_rect()

shooting_sfx = pygame.mixer.Sound(sound_file)
shooting_sfx.set_volume(volume_ratio)

pygame.mixer.music.load(bgm)
pygame.mixer.music.set_volume(volume_ratio)

#Initialize complete.-------------------------------------------------

def show_text(text, x, y):
    x, y = x, y
    if not isinstance(text, str):
        try:
            text = str(text)
        except:
            raise
    text = font.render(text, True, (255, 255, 255))
    screen.blit(text, (x, y))
##    pygame.display.update()

class SnowFlake(pygame.sprite.Sprite):

    def __init__(self):
        super(SnowFlake, self).__init__()
##        self.image = pygame.Surface((2, 2))
        self.image = pygame.Surface(*rdsize())
##        self.image.fill(WHITE)
        self.image.fill(rdgray())
        self.rect = self.image.get_rect()
        self.drop_rate = rdspeed()

        self.shft_rate = shftspeed()

    def update(self):
        # Overrided method, defines how sprites act per 'cycle'.
        self.rect.centery += self.drop_rate
        # annouce: center y
        if self.rect.centery >= W_HEIGHT:
            # Boundary action.
            # Reset position when going outside of screen.
            self.rect.centerx = random.randrange(0, W_WIDTH)
            self.rect.centery = random.randrange(-20, -5)
            # Outside of upper limit.
            self.drop_rate = rdspeed()
            self.shft_rate = shftspeed()


SNOWFLAKE_GROUP = pygame.sprite.Group()
for i in range(FLAKES):
    s = SnowFlake()
    s.rect.centerx = random.randrange(0, W_WIDTH)
    s.rect.centery = random.randrange(0, W_HEIGHT)
    SNOWFLAKE_GROUP.add(s)


class Hitbox(pygame.sprite.Sprite):

    def __init__(self,
                 *,
                 x=None,
                 y=None,
                 w=None,
                 h=None,
                 color=None,
                 enemy=False
                 ):
        super(Hitbox, self).__init__()
        self.isenemy = enemy
        color = color or (0, 255, 0)
        w = w or 70
        h = h or 100
        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        
        self.rect.centery = y or screct.centery # Initial place aligned with screen.
        self.rect.centerx = x or screct.centerx

        self.move_v_rate = 15
        self.move_h_rate = 15

        self.move_dir = random.choice((1, -1)) # regulating move of sprite

        self.bullet_shift = 25

        self.fire_rate = 70 # ms
        self.last_fire = pygame.time.get_ticks()

        self.fire_sfx = shooting_sfx
        self.fire_sfx.set_volume(volume_ratio)

    def move(self, v):
        if v == 'W' and self.rect.top > screct.top:
            self.rect.move_ip(0, -self.move_v_rate)
        if v == 'S' and self.rect.bottom < screct.bottom:
            self.rect.move_ip(0, self.move_v_rate)
        if v == 'A' and self.rect.left > screct.left:
            self.rect.move_ip(-self.move_h_rate, 0)
        if v == 'D' and self.rect.right < screct.right:
            self.rect.move_ip(self.move_h_rate, 0)

    def create_bullet(self, group):
        fire_now = pygame.time.get_ticks()
        elapsed_fire = fire_now - self.last_fire
        if not (elapsed_fire > self.fire_rate):
            # Fire rate limit.
            return None
        else:
            self.last_fire = fire_now
        
        self.fire_sfx.stop()
        ctx = self.rect.centerx
        top = self.rect.top
        shift = self.bullet_shift
        bullet_obj = Bullet(ctx, top - shift)
        if self.isenemy is True:
            bullet_obj = Bullet(
                ctx, self.rect.bottom + shift, direct='DOWN', size='L')
        group.add(bullet_obj)
        self.fire_sfx.play()
        return None

    def update(self):
        if self.rect.left < screct.left or self.rect.right > screct.right:
            self.move_dir *= -1
        if self.move_dir > 0:
            self.rect.move_ip(self.move_h_rate, 0)
        if self.move_dir < 0:
            self.rect.move_ip(-self.move_h_rate, 0)
##        print('MOVE', self.move_dir)


class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, *, direct='UP', size='S'):
        super(Bullet, self).__init__()
        self.direct = direct
        bullet_size = {'S': (2, 16),
                       'M': (3, 20),
                       'L': (5, 26)}
        size = bullet_size[size]
        self.image = pygame.Surface(size)
        self.image.fill(rdyellow())
        self.rect = self.image.get_rect()

        self.rect.center = (x, y)

        self.projectspd = 20

    def update(self):
        if self.direct == 'UP':
            self.rect.centery -= self.projectspd
        if self.direct == 'DOWN':
            self.rect.centery += self.projectspd


class Consumables(pygame.sprite.Sprite):

    def __init__(self):
        super(Consumables, self).__init__()
        
        size_list = [
            ['S', (7, 7)], ['M', (15, 15)], ['L', (19, 19)]
            ]
        score_dict = {
            'S': 1, 'M': 3, 'L': 7
            }
        
        size, vol = random.choice(size_list)
        self.image = pygame.Surface(vol)
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(0 + 15, W_WIDTH - 15), 15)
        self.score = score_dict[size]
        self.speed = 9
        self.direction = [random.choice((1, -1)), 1] # x, y direction
        self.lifetime = pygame.time.get_ticks() + 10 * 1000 # 10 seconds
    
    def update(self):
        if self.rect.top < screct.top or self.rect.bottom > screct.bottom:
            self.direction[1] *= -1 # Switch direction
        if self.rect.left < screct.left or self.rect.right > screct.right:
            self.direction[0] *= -1
        self.rect.centerx += self.direction[0] * self.speed
        self.rect.centery += self.direction[1] * self.speed

        if self.lifetime - pygame.time.get_ticks() < 700:
            self.image.fill((255, 0, 0))


#---------------------------------------------------------------------

psuedo_player = Hitbox(w=50, h=50)

player_group = pygame.sprite.Group()
player_group.add(psuedo_player)


enemy = Hitbox(y=60, w=170, h=15, color=(221, 0, 48), enemy=True)

enemy_group = pygame.sprite.Group()
enemy_group.add(enemy)

bullet_group = pygame.sprite.Group()
enemy_bullet_group = pygame.sprite.Group()

pill = Consumables()

pill_group = pygame.sprite.Group()
pill_group.add(pill)

# Game loop area.

CLOCK = pygame.time.Clock()
RUN_FLAG = True

#---------------------------------------------------------------------

pygame.mixer.music.play(-1, 0.0)

hits = 0
e_hits = 0
score = 0

while RUN_FLAG:
    CLOCK.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUN_FLAG = False
        elif event.type == pygame.KEYDOWN:
            print('KEYDOWN event detected:', event.key)
            if event.key == pygame.K_ESCAPE:
                RUN_FLAG = False
                print("Exit by esc key.")

    # Player activities logics.
    keyboard = pygame.key.get_pressed()
    if keyboard[pygame.K_w]:
        psuedo_player.move('W')
    if keyboard[pygame.K_s]:
        psuedo_player.move('S')
    if keyboard[pygame.K_a]:
        psuedo_player.move('A')
    if keyboard[pygame.K_d]:
        psuedo_player.move('D')
    if keyboard[pygame.K_j]:
        psuedo_player.create_bullet(bullet_group)

    # Init screen color.
    screen.fill(BLACK)

    # Background logics.
    SNOWFLAKE_GROUP.draw(screen)
    SNOWFLAKE_GROUP.update()

    # Draw pills
    if len(pill_group) <= 15:
        if dice(5):
            # Spawn pills at 5% chance of each frame.
            pill = Consumables()
            pill_group.add(pill)
    for p in pill_group:
        if p.lifetime < pygame.time.get_ticks():
            pill_group.remove(p)
        if pygame.sprite.spritecollideany(p, player_group):
            score += p.score
            pill_group.remove(p)
        
    pill_group.update()
    pill_group.draw(screen)

    # Draw player on screen.
    player_group.draw(screen)

    # Draw Enemies on screen

    for enemy in enemy_group:
        if dice(10):
            enemy.create_bullet(enemy_bullet_group)
    
    enemy_group.update()
    enemy_group.draw(screen)

    # Projectile logics.
    bullet_group.draw(screen)
    bullet_group.update()
    for bullet in bullet_group:
        if not screct.colliderect(bullet.rect):
            # Remove bullets that out of screen.
            bullet_group.remove(bullet)
        if pygame.sprite.spritecollideany(bullet, enemy_group):
            bullet_group.remove(bullet)
            hits += 1

    enemy_bullet_group.draw(screen)
    enemy_bullet_group.update()
    for ebullet in enemy_bullet_group:
        if not screct.colliderect(ebullet.rect):
            # Remove bullets that out of screen.
            enemy_bullet_group.remove(ebullet)
        if pygame.sprite.spritecollideany(ebullet, player_group):
            enemy_bullet_group.remove(ebullet)
            e_hits += 1

    # Print elapsed time (ms) on screen
    elapsed_time = '{:.3f} seconds'.format(
        pygame.time.get_ticks() / 1000
        )
    show_text(elapsed_time, 5, 0)
    show_text(f'hits: {hits}', 5, screct.bottom - 30)
    show_text(f'score: {score}', 5, 30 + 5)
    show_text(f'Enemy_hits: {e_hits}', screct.right - 350, screct.bottom - 30)

    # Refresh screen.
    pygame.display.flip()

pygame.quit()
sys.exit()
