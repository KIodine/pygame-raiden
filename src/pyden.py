import sys
import os
import random

import pygame
import config as cfg

# Pyden 0.15.1 alpha

rdgray = lambda: random.choice(cfg.gray_scale_range)
rdspeed = lambda: cfg.rand_speed_floor + cfg.rand_speed_ciel * random.random()
shftspeed = lambda: random.choice([1, -1]) * (3 * random.random())
rdsize = lambda: random.choices(
    [(1, i*5) for i in range(1, 3+1)], [70, 30, 10], k=1
    )
rdyellow = lambda: random.choice(cfg.yellow_range)

dice = lambda chn: True if chn > random.random() * 100 else False

# Set constants.

W_WIDTH = cfg.W_WIDTH
W_HEIGHT = cfg.W_HEIGHT
DEFAULT_COLOR = cfg.default_bgcolor
BLACK = cfg.color.black

FPS = 60

# Init window.

pygame.init()
pygame.display.init()
pygame.display.set_caption("Interstellar")

screen = pygame.display.set_mode(cfg.W_SIZE, 0, 32)
screen.fill(cfg.color.black)

screen_rect = screen.get_rect()

# Load resources.

    # Animations and images.

test_grid_dir = 'images/Checkered.png'
# The 'transparent' grid.
test_grid = pygame.image.load(test_grid_dir).convert_alpha()
test_grid_partial = test_grid.subsurface(screen_rect)

explode_dir = 'images/stone.png'
# A explosion animation named 'stone', uh...
explode = pygame.image.load(explode_dir).convert_alpha()

ufo_dir = 'images/ufo.gif'
# The ufo.
ufo = pygame.image.load(ufo_dir).convert_alpha()

    # Fonts.
msjh_dir = 'fonts/msjh.ttf'
msjh_24 = pygame.font.Font(msjh_dir, 24)
msjh_16 = pygame.font.Font(msjh_dir, 16)

# Define simple functions.

def show_text(text: str,
              x,
              y,
              font=msjh_16,
              color=cfg.color.white
              ):
    '''\
Display text on x, y.\
'''
    if not isinstance(text, str):
        try:
            text = str(text)
        except:
            raise
    rendered_text = font.render(text, True, color)
    screen.blit(rendered_text, (x, y))
    
    return None

# Interactive objects.

    # Define Charactor.

class Character(pygame.sprite.Sprite):

    def __init__(self,
                 *,
                 init_x=0,
                 init_y=0,
                 image=None,
                 w=70,
                 h=70,
                 col=1,
                 row=1
                 ):
        '''\
If given a image, set 'w' and 'h' to the unit size of image,
'col' and 'row' for frames.\
'''
        # Must be explictly.
        super(Character, self).__init__()
        
        if image is None:
            self.image = pygame.Surface((w, h), pygame.SRCALPHA)
            self.rect = self.image.get_rect()
            self.image.fill((0, 0, 0, 0))
            pygame.draw.rect(screen, (0, 255, 0, 255), (0, 0, w, h), 1)
            self.index = None
        else:
            self.index = 0
            self.animation_list = []
            self.master_image = image
            for i in range(col):
                for j in range(row):
                    self.animation_list.append(
                        [i*w, j*h, w, h]
                        )
            self.rect = pygame.rect.Rect(0, 0, w, h)
            # Set a smaller collide rect for better player experience?
            ani_rect = self.animation_list[self.index]
            self.ani_len = len(self.animation_list)
            self.image = self.master_image.subsurface(ani_rect)

        self.rect.center = init_x, init_y

        self.move_x_rate = 6
        self.move_y_rate = 6

        self.fire_rate = 70
        self.last_fire = pygame.time.get_ticks()

        self.fps = 24
        self.last_draw = pygame.time.get_ticks()

    def move(self, keypress):
        # Move: W A S D.
        # Note: May integrated with other actions and rename as 'actions'.
        if keypress[pygame.K_w] and self.rect.top > screen_rect.top:
            self.rect.move_ip(0, -self.move_y_rate)
        if keypress[pygame.K_s] and self.rect.bottom < screen_rect.bottom:
            self.rect.move_ip(0, self.move_y_rate)
        if keypress[pygame.K_a] and self.rect.left > screen_rect.left:
            self.rect.move_ip(-self.move_x_rate, 0)
        if keypress[pygame.K_d] and self.rect.right < screen_rect.right:
            self.rect.move_ip(self.move_x_rate, 0)

        if keypress[pygame.K_KP4]:
            print("<Pressed 'KP4'>")

    def _create_bullet(self):
        # Not finished yet.
        pass

    def update(self, current_time):
        if self.index is not None:
            elapsed_time = current_time - self.last_draw
            if elapsed_time > self.fps**-1 * 1000:
                self.index += 1
                ani_rect = self.animation_list[self.index%self.ani_len]
                self.image = self.master_image.subsurface(ani_rect)
                self.last_draw = current_time
        # Draw hitbox frame.
        frame = pygame.draw.rect(
            screen,
            (0, 255, 0, 255),
            self.rect,
            1
            )
        
    # End of Character.

    # Define Animated_object

class Animated_object(pygame.sprite.Sprite):

    def __init__(self,
                 *,
                 init_x=0,
                 init_y=0,
                 image=None,
                 w=0,
                 h=0,
                 col=1,
                 row=1
                 ):

        super(Animated_object, self).__init__()
        
        if image is None:
            self.image = pygame.Surface(
                (50, 50),
                pygame.SRCALPHA
                )
            self.image.fill((0, 0, 0, 0))
            pygame.draw.rect(screen, (0, 255, 0, 255), (0, 0, w, h), 1)
            self.rect = self.image.get_rect()
            self.index = None
        else:
            self.index = 0
            self.animation_list = []
            self.master_image = image
            for i in range(col):
                for j in range(row):
                    self.animation_list.append(
                        [i*w, j*h, w, h]
                        )
            self.rect = pygame.rect.Rect(0, 0, w, h)
            # Set a smaller collide rect for better player experience?
            ani_rect = self.animation_list[self.index]
##            print(self.master_image.get_rect())
            self.ani_len = len(self.animation_list)
            self.image = self.master_image.subsurface(ani_rect)

        self.rect.center = init_x, init_y

        self.fps = 12
        self.last_draw = pygame.time.get_ticks()

    def update(self, current_time):
        if self.index is not None:
            elapsed_time = current_time - self.last_draw
            if elapsed_time > self.fps**-1 * 1000:
                self.index += 1
                ani_rect = self.animation_list[self.index%self.ani_len]
                self.image = self.master_image.subsurface(ani_rect)
                self.last_draw = current_time
        else:
            pygame.draw.rect(
                screen,
                (0, 255, 0, 255),
                self.rect,
                1
                )
            
        # Draw hitbox frame.
        frame = pygame.draw.rect(
            screen,
            (0, 255, 0, 255),
            self.rect,
            1
            )


    # End of Animated_object.
    
# End of interactive objects.

# Init objects.

    # Player object.
player = Character(
    init_x=screen_rect.centerx,
    init_y=screen_rect.centery + 100,
    image=ufo,
    w=58,
    h=34,
    col=12
    )

player_group = pygame.sprite.Group()
player_group.add(player)

    # Animated objects.
explode_animation = Animated_object(
    init_x=screen_rect.centerx,
    init_y=screen_rect.centery-150,
    image=explode,
    w=50,
    h=50,
    col=6,
    row=5
    )

animated_object_group = pygame.sprite.Group()
animated_object_group.add(explode_animation)

# Init game loop.

clock = pygame.time.Clock()
Run_flag = True

# Start game loop.

    # Main phase.
while Run_flag:
    clock.tick(FPS)
    now = pygame.time.get_ticks()
    screen.fill(BLACK)
    screen.blit(test_grid_partial, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Run_flag = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                Run_flag = False
                print("<Exit by 'ESC' key>")

    keypress = pygame.key.get_pressed()

    player.move(keypress)

    # Game process.

    player_group.draw(screen)
    player_group.update(now)

    animated_object_group.draw(screen)
    animated_object_group.update(now)

    # End of game process.

    # Debug frame.

        # Show character rect infos.
    show_text(
        player.rect,
        player.rect.right,
        player.rect.bottom,
        color=cfg.color.black
        )
    
        # Show key infos.
    show_text(
        event,
        0,
        0,
        color=cfg.color.black
        )

    # End of debug frame.

    pygame.display.flip()

# End of game loop.
pygame.quit()
sys.exit(0)
