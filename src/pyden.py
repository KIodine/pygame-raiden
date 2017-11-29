import sys
import os
import random
import math
import time

import pygame

import config as cfg
import animation
import abilities

# Pyden 0.33.2

# Note: Seperate hitbox frame drawing from every class.
# Note: Seperate actions of player for further develope.
# Note: Rename config module?

_zero = time.perf_counter() # Reference point.

dice = lambda chn: True if chn > random.random() * 100 else False

# Set constants.

W_WIDTH = cfg.W_WIDTH
W_HEIGHT = cfg.W_HEIGHT
DEFAULT_COLOR = cfg.default_bgcolor
BLACK = cfg.color.black

FPS = 60

DEV_MODE = True

# F2: Switch DEV_MODE.
# F3: Charge resource to full.

# Init window.

pygame.init()
pygame.display.init()
pygame.display.set_caption("Interstellar")

screen = pygame.display.set_mode(cfg.W_SIZE, 0, 32) # RGBA
screen.fill(cfg.color.black)

screen_rect = screen.get_rect()

# Load resources.

test_grid_dir = 'images/Checkered.png' # The 'transparent' grid.
test_grid = pygame.image.load(test_grid_dir).convert_alpha()
test_grid_partial = test_grid.subsurface(screen_rect)

explode_dir = 'images/stone.png'

ufo_dir = 'images/ufo.gif'

flash_dir = 'images/explosion1.png'

msjh_dir = 'fonts/msjh.ttf'
msjh_24 = pygame.font.Font(msjh_dir, 24)
msjh_16 = pygame.font.Font(msjh_dir, 16)

explode = animation.loader(
    image=explode_dir,
    w=50,
    h=50,
    col=1, # Full: 6. Shorter frames for better performance.
    row=5
    )

ufo = animation.loader(
    image=ufo_dir,
    w=58,
    h=34,
    col=12
    )

flash = animation.loader(
    image=flash_dir,
    w=15,
    h=15
    )

def show_text(text: str,
              x,
              y,
              font=msjh_16,
              color=cfg.color.white
              ):
    '''Display text on x, y.'''
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


class Resource():
    '''Resource container and manager.'''
    # Fixed data structure.
    __slots__ = [
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
            self._over_charge_check()
            self.last_val = self.current_val
        # Limit the minimum val to zero.
        if self.current_val < 0: self.current_val = 0

    def charge(self, val=0):
        '''Charge resource with 'val'.'''
        if self.ratio < 1:
            self.current_val += val
            self._over_charge_check()

    def _to_zero(self):
        '''Reduce resource to zero.'''
        self.current_val = 0

    def _to_max(self):
        '''Charge resource to its maximum value.'''
        self.current_val = self.max_val

    def _over_charge_check(self):
        '''If current_val exceeds max_val, set it to max_val.'''
        if self.current_val > self.max_val:
            self.current_val = self.max_val

        return None

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

        animation.Core.__init__(
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
        self.Charge = Resource(
            name='Charge',
            init_val=0,
            max_val=1000,
            charge_val=3,
            charge_speed=0.01,
            init_time=now
            )

        self.Ult = Resource(
            name='Ultimate',
            init_val=0,
            max_val=2000,
            charge_val=3,
            charge_speed=0.1,
            init_time=now
            )

        self.Hp = Resource(
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

        self.move(keypress)

        if keypress[pygame.K_j]:
            # Cast normal attack.
            self._create_bullet(projectile_group)

        if keypress[pygame.K_k]:
            # Cast charged skill.
            ratio = self.Charge.ratio
            if self.Charge.ratio == 1:
                self.Charge._to_zero()

        if keypress[pygame.K_l]:
            # Cast ult.
            if self.Ult.ratio == 1:
                self.Ult._to_zero()
        return

    def move(self, keypress):
        '''Move player according to keypress, using WASD keys.'''
        if keypress[pygame.K_w] and self.rect.top > screen_rect.top:
            self.rect.move_ip(0, -self.move_y_rate)
        if keypress[pygame.K_s] and self.rect.bottom < screen_rect.bottom:
            self.rect.move_ip(0, self.move_y_rate)
        if keypress[pygame.K_a] and self.rect.left > screen_rect.left:
            self.rect.move_ip(-self.move_x_rate, 0)
        if keypress[pygame.K_d] and self.rect.right < screen_rect.right:
            self.rect.move_ip(self.move_x_rate, 0)
        return
    
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
        img = animation.loader(
            image=image,
            w=w,
            h=h
            )
        bullet = Projectile(
            init_x=x+b_shift(),
            init_y=y-8,
            image=img,
            speed=18,
            dmg=20,
            shooter=self
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
    '''Create mob object that oppose to player.'''
    def __init__(self,
                 *,
                 init_x=0,
                 init_y=0,
                 image=None
                 ):
        super(Mob, self).__init__()

        animation.Core.__init__(
            self,
            image_struct=image
            )

        self.rect.center = init_x, init_y

        self.move_x_rate = 6
        self.move_y_rate = 6

        now = pygame.time.get_ticks() # Get current time.

        self.fire_rate = 1
        self.last_fire = now

        self.Hp = Resource(
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
        img = animation.loader(
            image=image,
            w=w,
            h=h
            )
        bullet = Projectile(
            init_x=x+b_shift(),
            init_y=y+8,
            direct=1,
            image=img,
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

        super(Animated_object, self).__init__()

        animation.Core.__init__(
            self,
            image_struct=image
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
                 shooter=None,
                 image=None
                 ):
        
        super(Projectile, self).__init__()

        animation.Core.__init__(
            self,
            image_struct=image
            )

        now = pygame.time.get_ticks()

        self.dmg = dmg
        self.shooter = shooter
        
        self.rect.center = init_x, init_y
        self.direct = direct
        self.y_speed = speed
        self.move_rate = 0.1
        self.last_move = now

        self.fps = 12
        self.last_draw = now

    def _drain(self):
        if self.shooter is not None:
            self.shooter.Ult.charge(self.dmg * 1)
        
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

class Penetratable(pygame.sprite.Sprite):
    pass

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

        animation.Core.__init__(
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

animated_object_group = pygame.sprite.Group()

    # Skill panel.

blank100 = animation.loader(w=100, h=100)

charge = Skill_panel(
    x_pos=screen_rect.w-180,
    y_pos=screen_rect.h-170,
    border_expand=80,
    resource_name='Ult',
    image=blank100
    )

blank75 = animation.loader(w=75, h=75)

charge2 = Skill_panel(
    x_pos=screen_rect.w-350,
    y_pos=screen_rect.h-110,
    border_expand=50,
    resource_name='Charge',
    image=blank75
    )

blank80 = animation.loader(w=80, h=80)

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
            m_pos_y-26,
            color=cfg.color.black
            )
        show_text(
            clock.get_fps(),
            0,
            33,
            color=cfg.color.purple
            )
        show_text(
            pygame.time.get_ticks(),
            0,
            66,
            color=cfg.color.red
            )


class PositionControll():
    '''\
    Providing position control by preset route.
    '''
    def __init__(self):
        raise NotImplementedError("This class is yet being implemented.")


class AnimationHandle():
    '''Not implemented.'''
    def __init__(self):
        raise NotImplementedError("Not implemented yet.")


class MobHandle():

    def __init__(self,
                 *,
                 current_time,
                 enemy_group=None,
                 spawn_interval=1,
                 max_amount=10
                 ):
        
        self.next_spawn = current_time + spawn_interval * 1000
        self.enemy_group = enemy_group
        self.spawn_interval = spawn_interval * 1000
        self.max_amount = max_amount

    def refresh(self):
        # Psuedo code:
        # if there is space for spawn, wait for 'spawn_interval':
        #   spawn_enemy()
        #   if spawned, set 'next_spawn' as 'current_time' + 'spawn_interval'
        # if there is no space for spawn, set 'next_spawn' as
        #   'current_time' + 'spawn_interval'

        current_time = pygame.time.get_ticks()
        
        reset_next_spawn = lambda: current_time + self.spawn_interval
        
        if self.enemy_group is None:
            return
        self._clear_deadbody(current_time)
        self._attack_random(5)
        
        if len(self.enemy_group) < self.max_amount:
            if current_time > self.next_spawn:
                self._spawn_random_pos()
                self.next_spawn = reset_next_spawn() # Reset.
        else:
            self.next_spawn = reset_next_spawn()
    
    def _spawn_random_pos(self):
        
        # Add check(Psuedo code):
        #   if enemy.rect collides existing enemy:
        #     retry
        safe_x_pos = lambda: random.randint(100, screen_rect.w-100)
        safe_y_pos = lambda: random.randint(100, screen_rect.h/2)
        
        enemy = Mob(
            init_x=safe_x_pos(),
            init_y=safe_y_pos(),
            image=ufo
            )
        while True:
            if not pygame.sprite.spritecollide(
                enemy,
                self.enemy_group,
                False
                ):
                break
            else:
                if DEV_MODE:
                    print("<Collide detected, rearrange position.>")
                enemy.rect.center = safe_x_pos(), safe_y_pos()
                
        self.enemy_group.add(enemy)

    def _clear_deadbody(self, current_time):
        '''Clear hostile that 'Hp' less/equal than zero.'''
        # Clear deadbody and play explosion.
        for hostile in self.enemy_group:
            if hostile.Hp.current_val <= 0:
                self.enemy_group.remove(hostile)

                global KILL_COUNT # Not a good choice.
                KILL_COUNT += 1
                
                
                # Dead animation.
                # Target: random shift, with spawn interval.(other handle?)
                x, y = hostile.rect.center
                animated_object_group.add(
                    Animated_object(
                        init_x=x,
                        init_y=y,
                        image=explode
                        )
                    )

    def _attack_random(self, chance):
        '''Attack with n percent of chance.'''
        for hostile in self.enemy_group:
            if dice(chance):
                hostile.attack(hostile_projectile_group)
                # Play shooting sound here.


MobHandler = MobHandle(
    current_time=pygame.time.get_ticks(),
    enemy_group=enemy_group,
    )

player_bullets = abilities.BulletHandle(
    shooter=player,
    group=projectile_group,
    target_group=enemy_group,
    collide_coef=1.2,
    surface=screen,
    on_hit=flash
    )

enemy_bullets = abilities.BulletHandle(
    group=hostile_projectile_group,
    target_group=player_group,
    collide_coef=0.7,
    surface=screen,
    on_hit=flash
    )

# Elapsed time.
_elapsed_time = time.perf_counter() - _zero

print(
    "Time spent during initiate: {:.3f} ms".format(
        _elapsed_time * 1000
        )
    )


# Init game loop.

clock = pygame.time.Clock()

# Game contants.

Run_flag = True
PAUSE = False
KILL_COUNT = 0

# Start game loop.

    # Main phase.
while Run_flag:
    clock.tick(FPS)
    now = pygame.time.get_ticks()
    
    if DEV_MODE:
        screen.blit(test_grid_partial, (0, 0))
    else:
        screen.fill(BLACK)
        
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
                print("<PAUSE>")
                while PAUSE:
                    event = pygame.event.wait()
                    if event.type == pygame.KEYDOWN\
                       and event.key == pygame.K_p:
                        PAUSE = not PAUSE
                        print("<ACTION>")
                        pass
                    pass
                pass
        else:
            pass
    
    DEV_INFO(DEV_MODE)

    keypress = pygame.key.get_pressed()

    player.actions(keypress)

    # Game process.

    player_group.update(now)
    player_group.draw(screen)

    enemy_group.update(now) # Transfer to 'MobHandle'?
    enemy_group.draw(screen)
    
    MobHandler.refresh()

    player_bullets.refresh()
    enemy_bullets.refresh()

    # Animation handle.
    for ani in animated_object_group:
        if ani.index >= ani.ani_len - 1:
            animated_object_group.remove(ani)
    animated_object_group.update(now)
    animated_object_group.draw(screen)

    UI_group.draw(screen)
    UI_group.update(
        player
        )

    if DEV_MODE:
        color = cfg.color.black
    else:
        color = cfg.color.white
    show_text(
        f"KILLED: {KILL_COUNT}",
        400,
        550,
        color=color
        )

    # End of game process.

    pygame.display.flip() # Update screen.

# End of game loop.
pygame.quit()
sys.exit(0)
