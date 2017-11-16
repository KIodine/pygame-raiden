import sys
import os
import random
import math

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

DEV_MODE = True # Enable/disable DEV_MODE by 'F2' key.

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

rocket_dir = 'images/rocket02.png'
# The rocket projectile.
rocket = pygame.image.load(rocket_dir).convert_alpha()

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

    # Define Animation_core.

class Animation_core():
    '''Resolve single picture to animation list.'''
    def __init__(self,
                 *,
                 image=None,
                 w=70,
                 h=70,
                 col=1,
                 row=1
                 ):
        
        if image is None:
            self.image = pygame.Surface((w, h), pygame.SRCALPHA)
            self.rect = self.image.get_rect()
            self.image.fill((0, 0, 0, 0))
            pygame.draw.rect(self.image, (0, 255, 0, 255), (0, 0, w, h), 1)
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
        

    # End of Animation_core.

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

        Animation_core.__init__(
            self,
            image=image,
            w=w,
            h=h,
            col=col,
            row=row
            )

        self.rect.center = init_x, init_y

        self.move_x_rate = 6
        self.move_y_rate = 6

        now = pygame.time.get_ticks() # Get current time.

        self.fire_rate = 70
        self.last_fire = now

        # Set charge attr.
        self.current_charge = 0
        self.max_charge = 1000
        self.charge_value = 3
        self.charge_speed = 0.01 # second
        self.last_charge = now

        self.current_ult = 0
        self.max_ult = 2000
        self.ult_value = 3
        self.ult_speed = 0.01
        self.last_ult_charge = now

        # Set fps.
        self.fps = 24
        self.last_draw = now

    def actions(self, keypress):
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

        if keypress[pygame.K_KP8]:
            print("<Pressed 'KP8'>")

        if keypress[pygame.K_j]:
            ratio = self.current_charge/self.max_charge
            if ratio == 1:
                self.current_charge = 0
            pass

        if keypress[pygame.K_k]:
            ratio = self.current_ult/self.max_ult
            if ratio == 1:
                self.current_ult = 0
            pass

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
        if DEV_MODE:
            frame = pygame.draw.rect(
                screen,
                (0, 255, 0, 255),
                self.rect,
                1
                )
        
        elapsed_charge = current_time - self.last_charge
        if elapsed_charge > self.charge_speed * 1000\
           and self.current_charge < self.max_charge:
            self.last_charge = current_time
            self.current_charge += self.charge_value
            if self.current_charge > self.max_charge:
                self.current_charge = self.max_charge

        elapsed_ult_charge = current_time - self.last_ult_charge
        if elapsed_ult_charge > self.ult_speed * 1000\
           and self.current_ult < self.max_ult:
            self.last_ult_charge = current_time
            self.current_ult += self.ult_value
            if self.current_ult > self.max_ult:
                self.current_ult = self.max_ult
        
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

        Animation_core.__init__(
            self,
            image=image,
            w=w,
            h=h,
            col=col,
            row=row
            )

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
            
        if DEV_MODE:
            frame = pygame.draw.rect(
                screen,
                (0, 255, 0, 255),
                self.rect,
                1
                )


    # End of Animated_object.

    # Define Projectile.

class Projectile(pygame.sprite.Sprite):
    '''Simple linear projectile.'''
    def __init__(self,
                 *,
                 init_x=0,
                 init_y=0,
                 direct=-1,
                 speed=5,
                 image=None,
                 w=50,
                 h=50,
                 col=1,
                 row=1
                 ):
        
        super(Projectile, self).__init__()

        Animation_core.__init__(
            self,
            image=image,
            w=w,
            h=h,
            col=col,
            row=row
            )
        
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
            
        if DEV_MODE:
            pygame.draw.rect(
                    screen,
                    (255, 0, 0, 255),
                    self.rect,
                    1
                    )


    # End of Projectile.

    # Define Skill_panel.

class Skill_panel(pygame.sprite.Sprite):
    '''Skill charge instructor.'''
    def __init__(self,
                 *,
                 x_pos=0,
                 y_pos=0,
                 border_expand=25,
                 cur_resource='',
                 max_resource='',
                 image=None,
                 w=100,
                 h=100,
                 col=1,
                 row=1
                 ):

        if not (cur_resource or max_resource):
            raise ValueError("Cannot monitor empty resource name")

        self.cur_resource = cur_resource
        self.max_resource = max_resource
        
        super(Skill_panel, self).__init__()

        Animation_core.__init__(
            self,
            image=image,
            w=w,
            h=h,
            col=col,
            row=row
            )

        self.rect.topleft = x_pos, y_pos

        self.border_expand = border_expand

    def update(
        self,
        player: 'Player'
        ):
        current_val = getattr(player, self.cur_resource)
        max_val = getattr(player, self.max_resource)
        ratio = current_val/max_val
        outer_rect = self.rect.inflate(self.border_expand, self.border_expand)
        
        surf = pygame.Surface(outer_rect.size, pygame.SRCALPHA)
        surf_rect = outer_rect.copy()
        surf_rect.center = surf.get_rect().center
        arc_rect = surf_rect.inflate(-10, -10)
        
        arc_ratio = ratio * (2*math.pi)
##        print(f"<Panel, arc_ratio={arc_ratio}>")
        pygame.draw.arc(
            surf,
            (47, 89, 158, 190),
            arc_rect,
            (math.pi/2),
            (math.pi/2 + arc_ratio),
            15
            )
        if ratio == 1:
            c_center = outer_rect.center
            pygame.draw.circle(
                surf,
                (0, 255, 255, 190),
                surf_rect.center,
                int(outer_rect.width/2),
                3
                )
        screen.blit(surf, (outer_rect.topleft))


    # End of Skill panel.

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

    # Skill panel.
charge = Skill_panel(
    x_pos=screen_rect.w-180,
    y_pos=screen_rect.h-170,
    border_expand=100,
    cur_resource='current_ult',
    max_resource='max_ult',
    w=100,
    h=100
    )

charge2 = Skill_panel(
    x_pos=screen_rect.w-350,
    y_pos=screen_rect.h-110,
    border_expand=50,
    cur_resource='current_charge',
    max_resource='max_charge',
    w=75,
    h=75
    )

UI_group = pygame.sprite.Group()
UI_group.add(
    charge,
    charge2
    )

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

    # Global hotkey actions.
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            Run_flag = False
        elif event.type == pygame.KEYDOWN:
            key = event.key
            if key == pygame.K_ESCAPE:
                Run_flag = False
                print("<Exit by 'ESC' key>")
            if key == pygame.K_F2:
                DEV_MODE = not DEV_MODE
                print(f"<DEV_MODE={DEV_MODE}>")
            if key == pygame.K_F3:
                print("<Charge resource to max>")
                player.current_charge = player.max_charge
                player.current_ult = player.max_ult

    keypress = pygame.key.get_pressed()

    player.actions(keypress)

    # Game process.

    player_group.draw(screen)
    player_group.update(now)

    animated_object_group.draw(screen)
    animated_object_group.update(now)

    UI_group.draw(screen)
    UI_group.update(
        player
        )

##    print(player.current_charge, player.max_charge)

    # End of game process.

    # Debug frame.
    if DEV_MODE:
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

    pygame.display.flip() # Update screen.

# End of game loop.
pygame.quit()
sys.exit(0)
