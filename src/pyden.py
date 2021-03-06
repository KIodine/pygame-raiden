import sys
import os
import random
import math
from collections import namedtuple as _namedtuple

import pygame
import config as cfg

# Pyden 0.25.1

img_struct = _namedtuple(
        'Animation',
        [
            'image',
            'w',
            'h',
            'col',
            'row'
         ]
        )

# Temporary disabled.

<<<<<<< HEAD
try:
    import pygame
except:
    raise

try:
    import config as cfg
    import snowflake as snf
    import explode as exp
    import bullet as blt
    import die_explosion as d_exp
    import consumables as csb
    import hitbox as htb
except:
    raise
	

# Interstellar simulator 2017 ver. 0.11

rdgray = lambda: random.choice(cfg.gray_scale_range)
rdyellow = lambda: random.choice(cfg.yellow_range)
rdspeed = lambda: cfg.rand_speed_floor + cfg.rand_speed_ciel * random.random()
shftspeed = lambda: random.choice([1, -1]) * (3 * random.random())
rdsize = lambda: random.choices(
    [(1, i*5) for i in range(1, 3+1)], [70, 30, 10], k=1)
=======
##rdgray = lambda: random.choice(cfg.gray_scale_range)
##rdspeed = lambda: cfg.rand_speed_floor + cfg.rand_speed_ciel * random.random()
##shftspeed = lambda: random.choice([1, -1]) * (3 * random.random())
##rdsize = lambda: random.choices(
##    [(1, i*5) for i in range(1, 3+1)], [70, 30, 10], k=1
##    )
##rdyellow = lambda: random.choice(cfg.yellow_range)
>>>>>>> Architecture-Reconstruction

dice = lambda chn: True if chn > random.random() * 100 else False

# Set constants.

W_WIDTH = cfg.W_WIDTH
W_HEIGHT = cfg.W_HEIGHT
DEFAULT_COLOR = cfg.default_bgcolor
BLACK = cfg.color.black

FPS = 60

DEV_MODE = True

# Switch DEV_MODE by 'F2' key.
# Charge resource to full by 'F3' key.

# Init window.

pygame.init()
pygame.display.init()
pygame.display.set_caption("Interstellar")

screen = pygame.display.set_mode(cfg.W_SIZE, 0, 32)
screen.fill(cfg.color.black)

<<<<<<< HEAD
font = pygame.font.Font('fonts/msjh.ttf', 24)

screct = screen.get_rect()
rocket = pygame.image.load("images/rocket02.png").convert_alpha()
explode_image = 'images/explosion1.png'
explode = pygame.image.load(explode_image).convert_alpha()
ufo = pygame.image.load("../ufo.gif").convert_alpha()
# Use 'convert_alpha()' for images have alpha channel.

# It fails if the enviroment has no audio driver.
try:
    bullet_sound = "music/match0.wav"
    #sound_file = 'music/beep1.ogg' # Need to be replaced.
    #bgm = 'music/Diebuster OST- Escape Velocity.mp3'
    bgm = cfg.bgm
    dead_bgm = cfg.dead_bgm
    volume_ratio = cfg.volume_ratio

    pygame.mixer.music.load(bgm)
    pygame.mixer.music.set_volume(volume_ratio)
    pygame.mixer.music.play()
except:
    pass

#Initialize complete.-------------------------------------------------

def show_text(text, x, y):
    x, y = x, y
=======
screen_rect = screen.get_rect()

# Load resources.

    # Animations and images.

test_grid_dir = 'images/Checkered.png'
# The 'transparent' grid.
test_grid = pygame.image.load(test_grid_dir).convert_alpha()
test_grid_partial = test_grid.subsurface(screen_rect)

explode_dir = 'images/stone.png'
# A explosion animation named 'stone', uh...

ufo_dir = 'images/ufo.gif'

rocket_dir = 'images/rocket02.png'
# The rocket projectile.

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
>>>>>>> Architecture-Reconstruction
    if not isinstance(text, str):
        try:
            text = str(text)
        except:
            raise
    rendered_text = font.render(text, True, color)
    screen.blit(rendered_text, (x, y))
    
    return None

def animation_loader(
    image: pygame.Surface=None,
    w=70,
    h=70,
    col=1,
    row=1
    ) -> img_struct:
    '''\
Resolve or packs necessary info into 'img_struct' container.\
'''
    # 'isinstance' can test both native and custom classes.
    if image is not None:
        if isinstance(image, pygame.Surface):
            pass
        elif os.path.exists(image):
            # if it's not 'pygame.Surface', but a available path then:
            image = pygame.image.load(image).convert_alpha()
        else:
            raise TypeError(f"Cannot resolve {image}")
    struct = img_struct(
        image=image,
        w=w,
        h=h,
        col=col,
        row=row
        )
    return struct

# Load resource
explode = animation_loader(
    image=explode_dir,
    w=50,
    h=50,
    col=6,
    row=5
    )

ufo = animation_loader(
    image=ufo_dir,
    w=58,
    h=34,
    col=12
    )

def transparent_image(
    w=50,
    h=50
    ) -> pygame.Surface:
    surface = pygame.Surface(
        (w, h),
        pygame.SRCALPHA
        )
    surface.fill(
        (0, 0, 0, 0)
        )
    return surface

class Animation_core():
    '''Takes 'img_struct', resolve it into frame list.'''
    def __init__(self,
                 *,
                 image_struct=None,
                 ):
        # Progessing: take 'img_struct' and resolve.
        # Unpack data.
        image, w, h, col, row = image_struct
        
        if image is None:
            self.image = pygame.Surface((w, h), pygame.SRCALPHA)
            self.rect = self.image.get_rect()
            self.image.fill((0, 0, 0, 0))
            pygame.draw.rect(self.image, (0, 255, 0, 255), (0, 0, w, h), 1)
            self.index = None
        elif isinstance(image, pygame.Surface):
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
        else:
            raise TypeError(
                f"Expecting 'image_struct' type, got{image}"
                )

class resource():
    '''Resource container.'''
    __slots__ = [   # Fixed data structure.
        'name',
        'current_val',
        'max_val',
        'charge_val',
        'charge_speed',
        'last_charge',
        'delay',
        'delay_time',
        'last_val'
        ]
    def __init__(self,
                 *,
                 name='NONE',
                 init_val=100,
                 max_val=100,
                 charge_val=1,
                 charge_speed=0.1,
                 init_time=0,
                 delay=False,
                 delay_time=1
                 ):
        self.name = name
        self.current_val = init_val
        self.max_val = max_val
        self.charge_val = charge_val
        self.charge_speed=charge_speed
        self.last_charge = init_time
        
        self.delay = delay
        self.delay_time = delay_time
        self.last_val = init_val

    def __repr__(self):
        s = "<{name}: {current_val}/{max_val} ({ratio:.1f}%)>"
        return s.format(
            name=self.name,
            max_val=int(self.max_val),
            current_val=int(self.current_val),
            ratio=self.ratio*100
            )

    def recover(self, current_time):
        '''Recover resource over time.'''
        # The main method.
        def is_available():
            permission = False
            # Short-circuit, if 'delay' is 'False', it won't eval the rear code.
            if self.delay and self.last_val != self.current_val:
                self.last_charge = current_time
                # Reset last charge time(this is important).
                self.last_charge += self.delay_time * 1000
                self.last_val = self.current_val
                
            elapsed_time = current_time - self.last_charge
            if elapsed_time > self.charge_speed * 1000\
               and self.current_val < self.max_val:
                permission = True
                
            return permission
        
        if is_available():
            self.last_charge = current_time
            self.current_val += self.charge_val
            if self.current_val > self.max_val:
                self.current_val = self.max_val
            self.last_val = self.current_val
        # Limit the minimum val to zero.
        if self.current_val < 0: self.current_val = 0

    def zero(self):
        '''Reduce resource to zero.'''
        self.current_val = 0

    def _to_max(self):
        '''Charge resource to its maximum value.'''
        self.current_val = self.max_val

    @property
    def ratio(self):
        c_val = self.current_val
        if c_val < 0: c_val = 0
        return c_val/self.max_val

# Interactive objects.

    # Define Charactor.

class Character(pygame.sprite.Sprite):
    
    def __init__(self,
                 *,
                 init_x=0,
                 init_y=0,
                 image=None
                 ):
        '''\
If given a image, set 'w' and 'h' to the unit size of image,
'col' and 'row' for frames.\
'''
        # Must be explictly.
        super(Character, self).__init__()

        Animation_core.__init__(
            self,
            image_struct=image
            )

        self.rect.center = init_x, init_y

        self.move_x_rate = 6
        self.move_y_rate = 6

        now = pygame.time.get_ticks() # Get current time.

        self.fire_rate = 12
        self.last_fire = now

        # Set charge attr.
        self.Charge = resource(
            name='Charge',
            init_val=0,
            max_val=1000,
            charge_val=3,
            charge_speed=0.01,
            init_time=now
            )

        self.Ult = resource(
            name='Ultimate',
            init_val=0,
            max_val=2000,
            charge_val=3,
            charge_speed=0.01,
            init_time=now
            )

<<<<<<< HEAD
=======
        self.Hp = resource(
            name='Health',
            init_val=100,
            max_val=100,
            charge_val=0.6,
            charge_speed=0.02,
            init_time=now,
            delay=True,
            delay_time=2
            )

        self._resource_list = [
            self.Charge,
            self.Ult,
            self.Hp
            ]

        # Set fps.
        self.fps = 24
        self.last_draw = now

    def actions(self, keypress):
        # Move: W A S D.
        # Normal attack: 'j'
        # Charged attack: 'k'
        # Ult: 'l'(L)
        if keypress[pygame.K_w] and self.rect.top > screen_rect.top:
            self.rect.move_ip(0, -self.move_y_rate)
        if keypress[pygame.K_s] and self.rect.bottom < screen_rect.bottom:
            self.rect.move_ip(0, self.move_y_rate)
        if keypress[pygame.K_a] and self.rect.left > screen_rect.left:
            self.rect.move_ip(-self.move_x_rate, 0)
        if keypress[pygame.K_d] and self.rect.right < screen_rect.right:
            self.rect.move_ip(self.move_x_rate, 0)

        if keypress[pygame.K_KP8]: # Test.
            print("<Pressed 'KP8'>")


        if keypress[pygame.K_j]:
            # Cast normal attack.
            self._create_bullet(projectile_group)

        if keypress[pygame.K_k]:
            # Cast charged skill.
            ratio = self.Charge.ratio
            if self.Charge.ratio == 1:
                self.Charge.zero()

        if keypress[pygame.K_l]:
            # Cast ult.
            if self.Ult.ratio == 1:
                self.Ult.zero()

    def _create_bullet(self, projectile_group):
        now = pygame.time.get_ticks()
        b_shift = lambda: random.randint(-2, 2)
        if now - self.last_fire > self.fire_rate**-1 * 1000:
            self.last_fire = now
            pass
        else:
            return
        # Default bullet for test.
        image = pygame.Surface(
            (5, 15)
            )
        image.fill(
            (255, 255, 0) # yellow.
            )
        x, y = self.rect.midtop
        w, h = image.get_rect().size
        img = animation_loader(
            image=image,
            w=w,
            h=h
            )
        bullet = Projectile(
            init_x=x+b_shift(),
            init_y=y-8,
            image=img
            )
        projectile_group.add(bullet)
        

    def update(self, current_time):
        # Is there a way to seperate?
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
            

        for res in self._resource_list:
            res.recover(current_time)


    # End of Character.

    # Define Mob.

class Mob(pygame.sprite.Sprite):
    '''This class is yet to be done.'''
    def __init__(self,
                 *,
                 init_x=0,
                 init_y=0,
                 image=None
                 ):
        super(Mob, self).__init__()

        Animation_core.__init__(
            self,
            image_struct=image
            )

        self.rect.center = init_x, init_y

        self.move_x_rate = 6
        self.move_y_rate = 6

        now = pygame.time.get_ticks() # Get current time.

        self.fire_rate = 1
        self.last_fire = now

        self.Hp = resource(
            name='Hp',
            charge_val=1, # Will not recover over time.
            delay=True,
            delay_time=1.5
            )

        self._resource_list = [
            self.Hp
            ]

        # Set fps.
        self.fps = 24
        self.last_draw = now

    def _draw_hpbar(self):
        hp_ratio = int(100 * self.Hp.ratio)
        bar = pygame.rect.Rect(
            0, 0, hp_ratio, 6
            )
        x, y = self.rect.midtop
        bar.center = x, (y - 10)
        pygame.draw.rect(
            screen,
            cfg.color.green,
            bar,
            0 # fill
            )

    def attack(self, projectile_group):
        now = pygame.time.get_ticks()
        b_shift = lambda: random.randint(-2, 2)
        if now - self.last_fire > self.fire_rate**-1 * 1000:
            self.last_fire = now
            pass
        else:
            return
        # Default bullet for test.
        image = pygame.Surface(
            (5, 15)
            )
        image.fill(
            (255, 150, 0)
            )
        x, y = self.rect.midbottom
        w, h = image.get_rect().size
        img = animation_loader(
            image=image,
            w=w,
            h=h
            )
        bullet = Projectile(
            init_x=x+b_shift(),
            init_y=y+8,
            direct=1,
            image=img
            )
        projectile_group.add(bullet)

    def update(self, current_time):
        if self.index is not None:
            elapsed_time = current_time - self.last_draw
            if elapsed_time > self.fps**-1 * 1000:
                self.index += 1
                ani_rect = self.animation_list[self.index%self.ani_len]
                self.image = self.master_image.subsurface(ani_rect)
                self.last_draw = current_time
                
        for res in self._resource_list:
            res.recover(current_time)

        self._draw_hpbar()
        
        # Draw hitbox frame.
        if DEV_MODE:
            frame = pygame.draw.rect(
                screen,
                (255, 0, 0, 255), # red for enemy.
                self.rect,
                1
                )
            x, y = self.rect.bottomright
            show_text(
                self.Hp,
                x,
                y,
                color=cfg.color.black
                )


    # End of Mob.

    # Define Animated_object

class Animated_object(pygame.sprite.Sprite):

    def __init__(self,
                 *,
                 init_x=0,
                 init_y=0,
                 image=None
                 ):
>>>>>>> Architecture-Reconstruction

        super(Animated_object, self).__init__()

        Animation_core.__init__(
            self,
            image_struct=image
            )

<<<<<<< HEAD
psuedo_player = htb.Hitbox(screct, rdyellow, w=46, h=200, image=rocket, ratio=0.5)
=======
        self.rect.center = init_x, init_y
>>>>>>> Architecture-Reconstruction

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

<<<<<<< HEAD
enemy = htb.Hitbox(screct, rdyellow, y=60, w=58, image = ufo, h=34, color=(221, 0, 48), enemy=True, ratio=2)
=======
    # Define Projectile.
>>>>>>> Architecture-Reconstruction

class Projectile(pygame.sprite.Sprite):
    '''\
Simple linear projectile.
Minus direct for upward, positive direct for downward.\
'''
    def __init__(self,
                 *,
                 init_x=0,
                 init_y=0,
                 direct=-1,
                 speed=10,
                 dmg=10,
                 image=None
                 ):
        
        super(Projectile, self).__init__()

        Animation_core.__init__(
            self,
            image_struct=image
            )

        now = pygame.time.get_ticks()

        self.dmg = dmg
        
        self.rect.center = init_x, init_y
        self.direct = direct
        self.y_speed = speed
        self.move_rate = 0.1
        self.last_move = now

        self.fps = 12
        self.last_draw = now
        
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
        if current_time - self.last_move > self.move_rate:
            self.rect.centery += self.y_speed * self.direct
            self.last_move = current_time
            
        if DEV_MODE:
            pygame.draw.rect(
                    screen,
                    (255, 0, 0, 255),
                    self.rect.inflate(2, 2),
                    1
                    )


    # End of Projectile.

    # Define bullet type.

def bullet_creator(btype: str):
    # Working on it.
    pass

    # End of bullet type.

    # Define Skill_panel.

class Skill_panel(pygame.sprite.Sprite):
    '''Skill charge instructor.'''
    def __init__(self,
                 *,
                 x_pos=0,
                 y_pos=0,
                 border_expand=25,
                 arc_color=(47, 89, 158, 190),
                 rim_color=(0, 255, 255, 215),
                 resource_name='',
                 image=None
                 ):

        self.resource_name = resource_name
        
        super(Skill_panel, self).__init__()

        Animation_core.__init__(
            self,
            image_struct=image
            )

        self.rect.topleft = x_pos, y_pos

        self.border_expand = border_expand
        self.arc_color = arc_color
        self.rim_color = rim_color

    def update(
        self,
        player: Character
        ):
        
        res = getattr(player, self.resource_name) 
        current_val = res.current_val
        max_val = res.max_val
        
        ratio = res.ratio
        outer_rect = self.rect.inflate(self.border_expand, self.border_expand)
        
        surf = pygame.Surface(outer_rect.size, pygame.SRCALPHA)
        surf_rect = outer_rect.copy()
        surf_rect.center = surf.get_rect().center
        arc_rect = surf_rect.inflate(-10, -10)
        
        arc_ratio = ratio * (2*math.pi)
        # 'arc' takes 'radius' as param.
        # Variable arc indicates resource percentage.
        pygame.draw.arc(
            surf,
            self.arc_color,
            arc_rect,
            (math.pi/2),
            (math.pi/2 + arc_ratio),
            15
            )
        if ratio == 1:
            # Outer rim indicates resource is full.
            c_center = outer_rect.center
            pygame.draw.circle(
                surf,
                self.rim_color,
                surf_rect.center,
                int(outer_rect.width/2),
                3
                )
        screen.blit(surf, (outer_rect.topleft))
        if DEV_MODE:
            pygame.draw.rect(
                screen,
                (0, 255, 0, 255),
                outer_rect,
                2
                )


    # End of Skill panel.

# End of interactive objects.

# Init objects.

    # Player object.
player = Character(
    init_x=screen_rect.centerx,
    init_y=screen_rect.centery + 100,
    image=ufo
    )

player_group = pygame.sprite.Group()
player_group.add(player)

enemy = Mob(
    init_x=screen_rect.centerx-100,
    init_y=screen_rect.centery,
    image=ufo
    )

enemy_group = pygame.sprite.Group()
enemy_group.add(enemy)

    # projectile objects.
projectile_group = pygame.sprite.Group()
hostile_projectile_group = pygame.sprite.Group()

    # Animated objects.
explode_animation = Animated_object(
    init_x=screen_rect.centerx,
    init_y=screen_rect.centery-150,
    image=explode
    )

animated_object_group = pygame.sprite.Group()
animated_object_group.add(explode_animation)

    # Skill panel.

blank100 = animation_loader(w=100, h=100)

charge = Skill_panel(
    x_pos=screen_rect.w-180,
    y_pos=screen_rect.h-170,
    border_expand=80,
    resource_name='Ult',
    image=blank100
    )

blank75 = animation_loader(w=75, h=75)

charge2 = Skill_panel(
    x_pos=screen_rect.w-350,
    y_pos=screen_rect.h-110,
    border_expand=50,
    resource_name='Charge',
    image=blank75
    )

blank80 = animation_loader(w=80, h=80)

HP_monitor = Skill_panel(
    x_pos=60,
    y_pos=515,
    border_expand=50,
    resource_name='Hp',
    arc_color=(25, 221, 0, 240),
    image=blank80
    )

UI_group = pygame.sprite.Group()
UI_group.add(
    charge,
    charge2,
    HP_monitor
    )

# Define Handlers.

def DEV_INFO(flag=DEV_MODE):
    '''\
Catches 'player' and 'event' param in global and show.\
'''
    if flag:
        # Show character rect infos.
        if 'player' in globals():
            show_text(
                player.rect,
                player.rect.right,
                player.rect.bottom,
                color=cfg.color.black
                )
            show_text(
            player.Hp,
            170,
            490,
            color=cfg.color.black
            )
            # Show key infos.
        if 'event' in globals():
            show_text(
                event,
                0,
                0,
                color=cfg.color.black
                )
        m_pos_x, m_pos_y = pygame.mouse.get_pos()
        show_text(
            f'<{m_pos_x}, {m_pos_y}>',
            m_pos_x,
            m_pos_y,
            color=cfg.color.black
            )
        show_text(
            clock.get_fps(),
            0,
            33,
            color=cfg.color.purple
            )
    

class MobHandle():

    def __init__(self,
                 *,
                 current_time,
                 enemy_group=None,
                 spawn_interval=2,
                 max_amount=5
                 ):
        self.last_spawn = current_time
        self.enemy_group = enemy_group
        self.spawn_interval = spawn_interval * 1000
        self.max_amount = max_amount

    def __call__(self, current_time):
        if self.enemy_group is None:
            return
        for hostile in self.enemy_group:
            if hostile.Hp.current_val == 0:
                enemy_group.remove(hostile)
                self.last_spawn = current_time
        if len(enemy_group) < self.max_amount:
            elapsed_time = current_time - self.last_spawn
            if elapsed_time > self.spawn_interval:
                self._spawn_random_pos()
                self.last_spawn = current_time # Reset.

    def _spawn_random_pos(self):
        enemy = Mob(
                    init_x=random.randint(100, screen_rect.w-100),
                    init_y=random.randint(100, screen_rect.h/2),
                    image=ufo
                    )
        self.enemy_group.add(enemy)

MobHandler = MobHandle(
    current_time=pygame.time.get_ticks(),
    enemy_group=enemy_group,
    )

# Init game loop.

clock = pygame.time.Clock()
Run_flag = True
PAUSE = False

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
                # Enable/disable develope mode.
                DEV_MODE = not DEV_MODE
                print(f"<DEV_MODE={DEV_MODE}>")
                
            if key == pygame.K_F3:
                print("<Charge resource to max>")
                for p_res in player._resource_list:
                    p_res._to_max()
                for e in enemy_group:
                    for e_res in e._resource_list:
                        e_res._to_max()
                        
            if key == pygame.K_F4:
                player.Hp.current_val -= 50

            if key == pygame.K_p:
                PAUSE = not PAUSE
                while PAUSE:
                    event = pygame.event.wait()
                    if event.type == pygame.KEYDOWN\
                       and event.key == pygame.K_p:
                        PAUSE = not PAUSE
        else:
            pass
    
    DEV_INFO(DEV_MODE)
                
    for e in enemy_group:
        if dice(5):
            e.attack(hostile_projectile_group)

    keypress = pygame.key.get_pressed()

    player.actions(keypress)

    # Game process.

    player_group.update(now)
    player_group.draw(screen)

    enemy_group.update(now)
    enemy_group.draw(screen)
    
<<<<<<< HEAD
    # Player's dead. EXPLOSION!!
    if DIE_FLAG:
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(dead_bgm)
            pygame.mixer.music.set_volume(volume_ratio*8)
            pygame.mixer.music.play(0)
        except:
            pass
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
            die_exp = d_exp.Die_Explosion(random_x, random_y)
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
                exp.Explode(
                    *bullet.rect.center, explode))
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
=======
    MobHandler(now)

    projectile_group.update(now)
    projectile_group.draw(screen)
    for proj in projectile_group:
        if not screen_rect.contains(proj.rect):
            projectile_group.remove(proj)
>>>>>>> Architecture-Reconstruction
            
        collides = pygame.sprite.spritecollide(
            proj,
            enemy_group,
            False
            )
        for collided in collides:
            collided.Hp.current_val -= proj.dmg
            projectile_group.remove(proj)
    # The above and below chunk can be combined into a for-loop.
    hostile_projectile_group.update(now)
    hostile_projectile_group.draw(screen)
    for host_proj in hostile_projectile_group:
        if not screen_rect.contains(host_proj):
            hostile_projectile_group.remove(host_proj)

        collides = pygame.sprite.spritecollide(
            host_proj,
            player_group,
            False
            )
        for collided in collides:
            collided.Hp.current_val -= host_proj.dmg
            hostile_projectile_group.remove(host_proj)

    animated_object_group.update(now)
    animated_object_group.draw(screen)

    UI_group.draw(screen)
    UI_group.update(
        player
        )

    # End of game process.

    pygame.display.flip() # Update screen.

# End of game loop.
pygame.quit()
sys.exit(0)
