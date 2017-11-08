import sys
import os
import random
import time
import math

try:
    import pygame
except:
    raise

try:
    import config as cfg
    import snowflake as snf
except:
    raise
	

# Interstellar simulator 2017 ver. 0.11

rdgray = lambda: random.choice(cfg.gray_scale_range)
rdyellow = lambda: random.choice(cfg.yellow_range)
rdspeed = lambda: cfg.rand_speed_floor + cfg.rand_speed_ciel * random.random()
shftspeed = lambda: random.choice([1, -1]) * (3 * random.random())
rdsize = lambda: random.choices(
    [(1, i*5) for i in range(1, 3+1)], [70, 30, 10], k=1)

dice = lambda chn: True if chn > random.random() * 100 else False
print (rdsize)
#Simple functions set.------------------------------------------------

# Use random.gause(mu, sigma) to get normal dist?

W_WIDTH = cfg.W_WIDTH
W_HEIGHT = cfg.W_HEIGHT
DEFAULT_COLOR = cfg.default_bgcolor
BLACK = cfg.color.black

FLAKES = 512
FPS = cfg.FPS



sound_file = 'music/beep1.ogg' # Need to be replaced.
##bgm = 'music/Diebuster OST- Escape Velocity.mp3'
volume_ratio = 0.25

#Constants set.------------------------------------------------------

pygame.init()
pygame.display.init()
pygame.display.set_caption("Interstellar Simulator 2017")

screen = pygame.display.set_mode(cfg.W_SIZE, 0, 32)
screen.fill(cfg.color.black)

font = pygame.font.Font('fonts/msjh.ttf', 24)

screct = screen.get_rect()

explode_image = 'images/explosion1.png'
explode = pygame.image.load(explode_image).convert_alpha()
# Use 'convert_alpha()' for images have alpha channel.

# It fails if the enviroment has no audio driver.

##shooting_sfx = pygame.mixer.Sound(sound_file)
##shooting_sfx.set_volume(volume_ratio)

##pygame.mixer.music.load(bgm)
##pygame.mixer.music.set_volume(volume_ratio)

#Initialize complete.-------------------------------------------------

def show_text(text, x, y):
    x, y = x, y
    if not isinstance(text, str):
        try:
            text = str(text)
        except:
            raise
    text = font.render(text, True, (255, 255, 255))
    # Text is a 'pygame.Surface' object.
    t_rect = text.get_rect()
    screen.blit(text, (x, y))


class Explode(pygame.sprite.Sprite):

    def __init__(self, cx, cy):
        super(Explode, self).__init__()
        self.image = explode
        self.rect = self.image.get_rect()
        self.rect.center = (cx, cy)
        self.spawntime = pygame.time.get_ticks()
        self.lifetime = 0.07 * 1000

    def update(self):
        pass
# End of 'Explode'.



SNOWFLAKE_GROUP = pygame.sprite.Group()
for i in range(FLAKES):
    s = snf.SnowFlake(rdsize,rdgray,rdspeed,shftspeed,W_HEIGHT,W_WIDTH)
    s.rect.centerx = random.randrange(0, W_WIDTH)
    s.rect.centery = random.randrange(0, W_HEIGHT)
    SNOWFLAKE_GROUP.add(s)

# ---Create new class for enemy.---
# use pygame.trasform.rotozoom(Surface, angle, scale) to size-up image.

class Hitbox(pygame.sprite.Sprite):

    def __init__(self,
                 *,
                 x=None,
                 y=None,
                 w=None,
                 h=None,
                 color=None,
                 image=None,
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
        
        self._dest_x = self.rect.centerx
        self._dest_y = self.rect.centery
        
        self._float_x = self.rect.centerx
        self._float_y = self.rect.centery

        self.move_v_rate = 15
        self.move_h_rate = 15

        self.move_dir = random.choice((1, -1)) # regulating move of sprite

        self.bullet_shift = 25

        self.fire_rate = 70 # ms
        self.last_fire = pygame.time.get_ticks()

##        self.fire_sfx = shooting_sfx
##        self.fire_sfx.set_volume(volume_ratio)

        self._last_setdest = pygame.time.get_ticks()

    def move(self, v):
        if v == 'W' and self.rect.top > screct.top:
            self.rect.move_ip(0, -self.move_v_rate)
        if v == 'S' and self.rect.bottom < screct.bottom:
            self.rect.move_ip(0, self.move_v_rate)
        if v == 'A' and self.rect.left > screct.left:
            self.rect.move_ip(-self.move_h_rate, 0)
        if v == 'D' and self.rect.right < screct.right:
            self.rect.move_ip(self.move_h_rate, 0)

    def _set_dest(self, x, y):
        self._dest_x = int(x)
        self._dest_y = int(y)
        return None

    def _nlmove(self):
        if self.rect.centerx != self._dest_x:
            delta_x = 0.1 * math.ceil(self._dest_x - self.rect.centerx)
            self.rect.centerx += int(delta_x)
##            print(delta_x)
        if self.rect.centery != self._dest_y:
            delta_y = 0.1 * math.ceil(self._dest_y - self.rect.centery)
            self.rect.centery += int(delta_y)
##            print(delta_y)

    def create_bullet(self, group):
        fire_now = pygame.time.get_ticks()
        elapsed_fire = fire_now - self.last_fire
        if not (elapsed_fire > self.fire_rate):
            # Fire rate limit.
            return None
        else:
            self.last_fire = fire_now
        
##        self.fire_sfx.stop()
        ctx = self.rect.centerx
        top = self.rect.top
        shift = self.bullet_shift
        bullet_obj = Bullet(ctx, top - shift)
        if self.isenemy is True:
            # Add random shift for bullet?
            bullet_obj = Bullet(
                ctx, self.rect.bottom + shift, direct='DOWN', size='L')
        group.add(bullet_obj)
##        self.fire_sfx.play()
        return None

    def update(self):
        if self.isenemy:
            self._nlmove()
            elapsed_setdest = pygame.time.get_ticks() - self._last_setdest
            if elapsed_setdest > 2 * 1000:
                self._set_dest(
                    random.randint(
                        0 + self.rect.width, screct.right - self.rect.width
                        ),
                    random.randint(30, 90)
                    )
                print(self._dest_x, self._dest_y)
                self._last_setdest = pygame.time.get_ticks()
        
        if self.rect.left < screct.left or self.rect.right > screct.right:
            self.move_dir *= -1
        if self.move_dir > 0:
            self.rect.move_ip(self.move_h_rate, 0)
        if self.move_dir < 0:
            self.rect.move_ip(-self.move_h_rate, 0)
# End of 'Hitbox'.

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
# End of 'Bullet'.

class Consumables(pygame.sprite.Sprite):

    def __init__(self):
        super(Consumables, self).__init__()
        
        size_list = [
            ['S', (7, 7)], ['M', (10, 10)], ['L', (14, 14)]
            ]
        score_dict = {
            'S': 1, 'M': 3, 'L': 7
            }
        
        size, vol = random.choice(size_list)
        self.image = pygame.Surface(vol)
        self.image.fill(cfg.color.white)
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
# End of 'Consumables'.

class Die_Explosion(pygame.sprite.Sprite):
    
    def __init__(self, cx, cy):
        super(Die_Explosion, self).__init__()
        self.center = cx, cy
        self.image = None
        self.subrect = 0, 0, 50, 50
        self.master_image = pygame.image.load("images/stone.png").convert_alpha()
        self.animation_list = []
        for y in range(4):
            for x in range(5):
                self.animation_list.append((x*50, y*50, 50, 50))
        self.index = 0
        self.spawntime = pygame.time.get_ticks()
        
        self.zero = self.spawntime
        self.stay_interval = 300 # ms.

        self.ended = False
        
    def update(self, current_time):
        rect = self.animation_list[self.index]
        self.index += 1
        if self.index > len(self.animation_list) - 1:
            self.zero = self.zero or current_time
            self.index = 0
            if (current_time - self.zero) > self.stay_interval:
                self.ended = True
        
        self.image = self.master_image.subsurface(rect)
        self.rect = self.image.get_rect()
        self.rect.center = self.center
#End of 'Die_Explosion'

#---------------------------------------------------------------------

psuedo_player = Hitbox(w=50, h=50)

player_atk = 25

player_group = pygame.sprite.Group()
player_group.add(psuedo_player)

# Use specialized class for enemy.

enemy = Hitbox(y=60, w=170, h=15, color=(221, 0, 48), enemy=True)

enemy_group = pygame.sprite.Group()
enemy_group.add(enemy)

bullet_group = pygame.sprite.Group()
enemy_bullet_group = pygame.sprite.Group()

Explode_group = pygame.sprite.Group()

pill = Consumables()

pill_group = pygame.sprite.Group()
pill_group.add(pill)

# Die_Explosion_Group

die_explosion_group = pygame.sprite.Group()
last_spawn = 0

# Game loop area.

CLOCK = pygame.time.Clock()
RUN_FLAG = True
DIE_FLAG = False  # Check if player is alive or not

#---------------------------------------------------------------------

##pygame.mixer.music.play(-1, 0.0)

#---------------------------------------------------------------------
'''Fade in and fade out.'''

msjh = 'fonts/msjh.ttf'
cap_font = pygame.font.Font(msjh, 120)
sub_font = pygame.font.Font(msjh, 24)
cap = "Pyden 2017"
sub = "Studio EVER proudly present"

screen_rect = screen.get_rect()

cap_x, cap_y = screen_rect.center
sub_x, sub_y = cap_x, cap_y + 100

clock = pygame.time.Clock()

def show_cap(text, x, y, trans, font=cap_font):
    if not isinstance(text, str):
        try:
            text = str(text)
        except:
            raise
    text = font.render(text, True, (trans, trans, trans))
    text_x, text_y = text.get_size()
##    print('text_xy', text_x, text_y)
    screen.blit(text, (x - text_x / 2, y - text_y / 2))
    print(trans)

play_caption = True

stay_interval = 1.5

init_trans = 0
fade_in_speed = 9
fade_out_speed = 15

# DO NOT TOUCH, this is the sign for animation controlling.
fade_in_phase = True
fade_out_phase = False


if play_caption:
    trans = init_trans
    while fade_in_phase:
        clock.tick(FPS)
        show_cap( # Use functools.partial to shorten.
            cap,
            cap_x,
            cap_y,
            trans=trans)
        show_cap(
            sub,
            sub_x,
            sub_y,
            trans=trans,
            font=sub_font
            )
        trans += fade_in_speed
        if trans >= 255:
            trans = 255
            fade_in_phase = False
            fade_out_phase = True
        pygame.display.flip()
            
    time.sleep(stay_interval) # Pause gameplay.

    while fade_out_phase:
        clock.tick(FPS)
        show_cap(
            cap,
            cap_x,
            cap_y,
            trans=trans)
        show_cap(
            sub,
            sub_x,
            sub_y,
            trans=trans,
            font=sub_font
            )
        trans -= fade_out_speed
        if trans <= 0:
            trans = 0
            fade_out_phase = False
        pygame.display.flip()
    screen.fill(BLACK)
    pygame.display.flip()
    time.sleep(0.7)
    
    print("CAP SHOWN")

#---------------------------------------------------------------------

hits = 0
e_hits = 0
score = 0

enemy_hp = 1000
enemy_max_hp = 1000

player_dead = False
enemy_dead = False

while RUN_FLAG:
    CLOCK.tick(FPS)
    
    # Init screen color.
    # ---Put scrolling background here---
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUN_FLAG = False
        elif event.type == pygame.KEYDOWN:
##            print('KEYDOWN event detected:', event.key)
            if event.key == pygame.K_ESCAPE:
                show_text("Exit by user",
                          screct.centerx - 6*11,
                          screct.centery + 55)
                RUN_FLAG = False
                print("Exit by esc key.")

    # Player activities logics.
    # Avaliable to control if player is alive
    if not DIE_FLAG:
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
    if not DIE_FLAG:
        pill_group.update()
        pill_group.draw(screen)

    # Draw player on screen.
    player_group.draw(screen)
    
    # Draw Enemies on screen

    for enemy in enemy_group:
        if dice(10):
            # Has 10% of chance spawn a bullet per tick.
            enemy.create_bullet(enemy_bullet_group)
    if not DIE_FLAG:
        enemy_group.update()
    enemy_group.draw(screen)

    # Player's dead. EXPLOSION!!
    if DIE_FLAG:
        
        if player_dead:
            target_rect = psuedo_player.rect
            end_messege = "You're DEAD"
        if enemy_dead:
            target_rect = enemy.rect
            end_messege = "VICTORY!"
        
        exp_spawn_interval = pygame.time.get_ticks() - last_spawn
        if len(die_explosion_group) <= 5 and exp_spawn_interval > 200: # ms.
            random_x = target_rect.centerx + random.randint(-25, 25)
            random_y = target_rect.centery + random.randint(-25, 25)
            die_exp = Die_Explosion(random_x, random_y)
            die_explosion_group.add(die_exp)
            last_spawn = pygame.time.get_ticks()
        
        for die_exp in die_explosion_group:
            if die_exp.ended:
                die_explosion_group.remove(die_exp)

##        die_explosion_group.add(die_explosion1)
        die_explosion_group.update(pygame.time.get_ticks())
        die_explosion_group.draw(screen)
        show_text(end_messege,
                  screct.centerx - 6*11,
                  screct.centery - 12)
        current_die_time = pygame.time.get_ticks()
        if current_die_time - pre_die_time >= 5000:
            RUN_FLAG = False
    
    # Projectile logics.
    # Player:
    if not DIE_FLAG:
        bullet_group.draw(screen)
        bullet_group.update()
    if not DIE_FLAG:
        pre_die_time = pygame.time.get_ticks()
    for bullet in bullet_group:
        if not screct.colliderect(bullet.rect):
            # Remove bullets that out of screen.
            bullet_group.remove(bullet)
        for spr in pygame.sprite.spritecollide(bullet, enemy_group, False):
            # Insert on-hit-animation here. -> Done.
            
            colcenterx = (spr.rect.centerx + bullet.rect.centerx)/2
            colcentery = (spr.rect.centery + bullet.rect.centery)/2
            print(colcenterx, colcentery)
            
            Explode_group.add(
                Explode(
                    *bullet.rect.center))
            bullet_group.remove(bullet)
            hits += 1
            enemy_hp -= player_atk
                
            if enemy_hp <= 0:
##                show_text("Victory!",
##                          screct.centerx - 6*11,
##                          screct.centery + 16)
                print("Exit by victory.")
                DIE_FLAG = True
                enemy_dead = True

    # Enemy:
    if not DIE_FLAG:
        enemy_bullet_group.draw(screen)
        enemy_bullet_group.update()
    for ebullet in enemy_bullet_group:
        if not screct.colliderect(ebullet.rect):
            # Remove bullets that out of screen.
            enemy_bullet_group.remove(ebullet)
        for espr in  pygame.sprite.spritecollide(ebullet, player_group, False):
            # Insert on-hit-animation here. -> Done.
            
            colcenterx = (espr.rect.centerx + ebullet.rect.centerx)/2
            colcentery = (espr.rect.centery + ebullet.rect.centery)/2
            cldx, cldy = ebullet.rect.midtop
            print(colcenterx, colcentery)
            
            Explode_group.add(
                Explode(
                    *ebullet.rect.center))
            enemy_bullet_group.remove(ebullet)
            e_hits += 1

            if e_hits >= 5:
                if not DIE_FLAG:
                    pre_die_time = pygame.time.get_ticks()
                DIE_FLAG = True
                player_dead = True
                
    if not DIE_FLAG:
        Explode_group.draw(screen)
        Explode_group.update()
    for e in Explode_group:
        explode_elapsed = pygame.time.get_ticks() - e.spawntime
        if explode_elapsed > e.lifetime:
            Explode_group.remove(e)

    # ---Insert player life instructor here.---

    # Print elapsed time (ms) on screen
    elapsed_time = '{:.3f} seconds'.format(
        pygame.time.get_ticks() / 1000
        )
    show_text(elapsed_time, 5, 0)
    show_text(f'hits: {hits}', 5, screct.bottom - 30)
    show_text(f'score: {score}', 5, 30 + 5)
    show_text(f'Enemy_hits: {e_hits}', screct.right - 350, screct.bottom - 30)

    # Enemy life intruction.

    ratio = int(600*(enemy_hp/enemy_max_hp))
    if ratio < 0: ratio = 0
    ehp_s = pygame.Surface((ratio, 20))
    ehp_rect = ehp_s.get_rect(
        center=(screct.centerx, 15))
    ehp_s.fill((0, 240, 0))
    screen.blit(ehp_s, ehp_rect)
    print(enemy_hp)
    pygame.display.update(ehp_rect)
    
    # Refresh screen.
    pygame.display.flip()

#End Game loop--------------------------------------------------------

pygame.display.flip()

#time.sleep(0.5)
pygame.event.clear() # Clear event queue avoid getting unused events.

while True:
    event = pygame.event.wait()
    if event.type == pygame.KEYDOWN:
        # Quit by press any key.
        break

pygame.quit()
sys.exit()
