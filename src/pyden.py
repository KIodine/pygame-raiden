import sys
import os
import random
import math

import pygame
import config as cfg
import animation as ani

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

DEV_MODE = True

# Switch DEV_MODE by 'F2' key.
# Charge resource to full by 'F3' key.

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
        # Delayed recovery is yet being implemented.
        
        def is_available():
            permission = False
            
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

        ani.Animation_core.__init__(
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
        bullet = Projectile(
            init_x=x+b_shift(),
            init_y=y-8,
            image=image,
            w=w,
            h=h
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
                 image=None,
                 w=70,
                 h=70,
                 col=1,
                 row=1
                 ):
        super(Mob, self).__init__()

        ani.Animation_core.__init__(
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

        self.fire_rate = 12
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
        bullet = Projectile(
            init_x=x+b_shift(),
            init_y=y+8,
            direct=1,
            image=image,
            w=w,
            h=h
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
                 image=None,
                 w=0,
                 h=0,
                 col=1,
                 row=1
                 ):

        super(Animated_object, self).__init__()

        ani.Animation_core.__init__(
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
                 image=None,
                 w=50,
                 h=50,
                 col=1,
                 row=1
                 ):
        
        super(Projectile, self).__init__()

        ani.Animation_core.__init__(
            self,
            image=image,
            w=w,
            h=h,
            col=col,
            row=row
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
                    self.rect,
                    1
                    )


    # End of Projectile.

    # Define bullet type.

def bullet_creator(btype: str):
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
                 resource_name='',
                 image=None,
                 w=100,
                 h=100,
                 col=1,
                 row=1
                 ):

        self.resource_name = resource_name
        
        super(Skill_panel, self).__init__()

        ani.Animation_core.__init__(
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
    image=ufo,
    w=58,
    h=34,
    col=12
    )

player_group = pygame.sprite.Group()
player_group.add(player)

enemy = Mob(
    init_x=screen_rect.centerx-100,
    init_y=screen_rect.centery,
    image=ufo,
    w=58,
    h=34,
    col=12
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
    resource_name='Ult',
    w=100,
    h=100
    )

charge2 = Skill_panel(
    x_pos=screen_rect.w-350,
    y_pos=screen_rect.h-110,
    border_expand=50,
    resource_name='Charge',
    w=75,
    h=75
    )

HP_monitor = Skill_panel(
    x_pos=60,
    y_pos=515,
    border_expand=50,
    resource_name='Hp',
    w=80,
    h=80
    )

UI_group = pygame.sprite.Group()
UI_group.add(
    charge,
    charge2,
    HP_monitor
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
                
    if dice(5):
        enemy.attack(hostile_projectile_group)

    keypress = pygame.key.get_pressed()

    player.actions(keypress)

    # Game process.

    player_group.draw(screen)
    player_group.update(now)

    enemy_group.draw(screen)
    enemy_group.update(now)

    projectile_group.draw(screen)
    projectile_group.update(now)
    for proj in projectile_group:
        if not screen_rect.contains(proj.rect):
            projectile_group.remove(proj)
            
        collides = pygame.sprite.spritecollide(
            proj,
            enemy_group,
            False
            )
        for collided in collides:
            collided.Hp.current_val -= proj.dmg
            projectile_group.remove(proj)

    hostile_projectile_group.draw(screen)
    hostile_projectile_group.update(now)
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

    animated_object_group.draw(screen)
    animated_object_group.update(now)

    UI_group.draw(screen)
    UI_group.update(
        player
        )

##    print(player.current_charge, player.max_charge)

    # End of game process.

    # System info frame.
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
        m_pos_x, m_pos_y = pygame.mouse.get_pos()
        show_text(
            f'<{m_pos_x}, {m_pos_y}>',
            m_pos_x,
            m_pos_y,
            color=cfg.color.black
            )
        show_text(
            player.Hp,
            170,
            490,
            color=cfg.color.black
            )
        show_text(
            clock.get_fps(),
            0,
            33,
            color=cfg.color.purple
            )

    # End of debug frame.

    pygame.display.flip() # Update screen.

# End of game loop.
pygame.quit()
sys.exit(0)
