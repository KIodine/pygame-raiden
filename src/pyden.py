# Native.-------------------------------------------------------------
import sys
import os
import random
import math
import time
import copy
import weakref # Analyzing object lifespan.
from collections import deque, namedtuple
from enum import Enum
# Third-party.--------------------------------------------------------
import pygame
# Custom.-------------------------------------------------------------
import config as cfg
import animation
import abilities
import resource

# Pyden 0.42.3
'''Notes:
    1. Seperate actions from player for further develope.
        Add a 'Interface' class could be a solution, but clarify its structure
        is more important.
    2. Rename config module?
    3. The way to share 'AnimationHandler', passing reference when initialize
        related module?
    4. 'Character', 'Mob', 'MobHandle' and someother are coupled with
        'animation.AnimationHandle'(Note-3)
    5. Use custom identifier than seperate group?
'''

_zero = time.perf_counter() # Reference point.

dice = lambda chn: True if chn > random.random() * 100 else False

# Set constants.------------------------------------------------------

FPS = 60
W_WIDTH = cfg.W_WIDTH
W_HEIGHT = cfg.W_HEIGHT
DEFAULT_COLOR = cfg.default_bgcolor
BLACK = cfg.color.black

# Game constants and utilities.---------------------------------------

DEV_MODE = True
RUN_FLAG = True
PAUSE = False
KILL_COUNT = 0
clock = pygame.time.Clock()

# F2: Switch DEV_MODE.
# F3: Charge resource to full.
# F4: Damage player for 50 points.
# P: Pause game.

# Init pygame and display.--------------------------------------------

npass, nfail = pygame.init()
assert nfail == 0
pygame.display.init()
pygame.display.set_caption("Interstellar")

screen = pygame.display.set_mode(cfg.W_SIZE, 0, 32) # RGBA
screen.fill(cfg.color.black)

screen_rect = screen.get_rect()

# Init containers.----------------------------------------------------

player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
projectile_group = pygame.sprite.Group()
hostile_projectile_group = pygame.sprite.Group()
animated_object_group = pygame.sprite.Group()
HUD_group = pygame.sprite.Group()

ALL_GROUPS = list()
ALL_GROUPS.extend(
    [
        player_group,
        enemy_group,
        projectile_group,
        hostile_projectile_group,
        animated_object_group,
        HUD_group
    ]
)
# No actual effect right now.
class Camp(Enum):
    """Camp identifier."""
    PLAYER = 0
    ENEMY = 1
    NEUTRAL = 2

# Load resources.-----------------------------------------------------

if not os.path.exists('images'):
    # A vscode issue.
    try:
        os.chdir('src')
    except FileNotFoundError:
        raise

test_grid_dir = 'images/Checkered.png' # The 'transparent' grid.
test_grid = pygame.image.load(test_grid_dir).convert_alpha()
test_grid_partial = test_grid.subsurface(screen_rect)

msjh_dir = 'fonts/msjh.ttf'
msjh_24 = pygame.font.Font(msjh_dir, 24)
msjh_16 = pygame.font.Font(msjh_dir, 16)

explode_dir = 'images/stone.png'
ufo_dir = 'images/ufo.gif'
flash_dir = 'images/explosion1.png'

new_explode = animation.sequential_loader(
    image=explode_dir,
    w=50,
    h=50,
    col=1,
    row=5
)

new_ufo = animation.sequential_loader(
    image=ufo_dir,
    w=58,
    h=34,
    col=12
)

# The old-style loader, still using.
flash = animation.loader(
    image=flash_dir,
    w=15,
    h=15
    )

new_flash = animation.sequential_loader(
    image=flash_dir,
    w=15,
    h=15
)


# Init custom modules.------------------------------------------------

abilities.init(screen)
assert abilities.is_initiated()

# Functions.----------------------------------------------------------
# Add a 'show_multiline' function?
def show_text(
        text: str,
        x=0,
        y=0,
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

# Classes.------------------------------------------------------------

# Character.----------------------------------------------------------

PLAYER_ATTRS = resource.RES_DICT(
    {
        resource.HP: resource.default_player_hp(),
        resource.CHARGE: resource.default_player_charge(),
        resource.ULTIMATE: resource.default_player_ultimate()
    }
)


ENEMY_ATTRS = resource.RES_DICT(
    {
        resource.HP: resource.default_enemy_hp()
    }
)

class Character(
        pygame.sprite.Sprite,
        animation.NewCore
    ):
    '''Create player character for manipulation.'''
    '''Dependencies.(which are not passed by params or inheritance.)
        Depends on:
            (1) enemy_group
            (2) AnimationHandler
            (3) abilities
            (4) projectile_group
            (5) hostile_projectile_group
            (6) screen
    '''
    def __init__(
            self,
            *,
            init_x=0,
            init_y=0,
            image=None,
            attrs=None, # Add a 'camp' param to identify its group?
            camp=None
        ):
        # Must be explictly.
        master, frames = image
        # Due to the need of initial params, initialize parent explictly.
        pygame.sprite.Sprite.__init__(self)
        animation.NewCore.__init__(
            self,
            master=master,
            frames=frames
            )
        now = pygame.time.get_ticks()

        self.rect.center = init_x, init_y

        self.move_x_rate = 6
        self.move_y_rate = 6
        # Test for more generic way to limit firerate.
        self.gcd = 0 # A player is permitted to fire if gcd <= 0.

        self.fire_rate = 12
        self.last_fire = now
        # New attr mechanism.-----------------------------------------
        self.attrs = copy.deepcopy(attrs) # Avoid reference to the object.
        # ------------------------------------------------------------
        self.camp = camp
        # Overwritting attrs from 'NewCore'---------------------------
        self.fps = 24
        self.last_draw = now
        # ------------------------------------------------------------
        self.ult_active = False

    def actions(self, keypress):
        # Move: W A S D.
        # Normal attack: 'j'
        # Charged attack: 'k'
        # Ult: 'l'(L)

        self.move(keypress)

        if keypress[pygame.K_j] and not self.ult_active:
            # Cast normal attack.
            self._create_bullet(projectile_group)

        if keypress[pygame.K_k] and not self.ult_active:
            # Cast charged skill.
            ratio = self.attrs[resource.CHARGE].ratio
            if ratio == 1:
                # ----------------------------------------------------
                # Issue: The beam stays too short on screen.
                rect = self.rect
                w = 5
                h = rect.top
                x = rect.centerx - w / 2
                y = 0
                check_rect = pygame.Rect(
                    (x, y), (w, h)
                    )
                collide_list = [
                    sprite for sprite in enemy_group
                    if check_rect.colliderect(sprite.rect)
                    ]
                if collide_list:
                    collide_list.sort(
                        key=lambda sprite: sprite.rect.centery - rect.centery,
                        reverse=True
                        )
                    hit = collide_list[0]
                    top = hit.rect.bottom
                    eff_bar = pygame.Rect(
                        (x, top), (w, h - top)
                        )
                    pygame.draw.rect(
                        screen,
                        (255, 255, 0),
                        eff_bar
                        )
                    AnimationHandler.draw_single(
                        x=eff_bar.centerx,
                        y=eff_bar.top,
                        image=new_flash
                        )
                    hit.attrs[resource.HP] -= 120
                    # Only when the skill hits enemy then energy consume.
                    self.attrs[resource.CHARGE]._to_zero()
                    self.attrs[resource.ULTIMATE] += 120
                else:
                    pass
                # ----------------------------------------------------

        # Ultimate.---------------------------------------------------
        # The lock mechanism.
        if keypress[pygame.K_u] and not self.ult_active:
            if self.attrs[resource.ULTIMATE].ratio == 1:
                print("<Ultimate activated>")
                self.ult_active = True
            else:
                print(
                    "<Insufficient energy: {}>".format(
                        self.attrs[resource.HP].ratio
                    )
                )

        if keypress[pygame.K_u] \
           and self.ult_active \
           and (self.attrs[resource.ULTIMATE].ratio != 0):
            self._laser()
            self.attrs[resource.ULTIMATE] -= 13
        else:
            if self.ult_active == True:
                self.ult_active = False
                print((
                    "<Ultimate deactiveted,"
                    " remaining energy: {u_ratio:.2f}%>".format(
                        u_ratio=self.attrs[resource.ULTIMATE].ratio * 100
                        )
                    ))
        # ------------------------------------------------------------
        return

    def move(self, keypress):
        '''Move player according to keypress, using WASD keys.'''
        rect = self.rect
        if keypress[pygame.K_w] and self.rect.top > screen_rect.top:
            rect.move_ip(0, -self.move_y_rate)
        if keypress[pygame.K_s] and self.rect.bottom < screen_rect.bottom:
            self.rect.move_ip(0, self.move_y_rate)
        if keypress[pygame.K_a] and self.rect.left > screen_rect.left:
            self.rect.move_ip(-self.move_x_rate, 0)
        if keypress[pygame.K_d] and self.rect.right < screen_rect.right:
            self.rect.move_ip(self.move_x_rate, 0)
        return

    def _create_bullet(self, projectile_group):
        # Use identifier instead of group??
        # if self.gcd >= 0:
        #     return
        now = pygame.time.get_ticks()
        b_shift = lambda: random.randint(-2, 2)

        if now - self.last_fire > self.fire_rate**-1 * 1000:
            self.last_fire = now
        else:
            return
        image = abilities.default_bullet(color=cfg.color.yellow)
        x, y = self.rect.midtop
        bullet = abilities.Linear(
            init_x=x + b_shift(),
            init_y=y - 8,
            image=image,
            speed=1050,
            dmg=22,
            shooter=self
        )
        projectile_group.add(bullet)
        # self.gcd += bullet.cooldown
        return

    def _laser(self):
        bottom = self.rect.top - 8
        top = 0
        w = 14
        h = self.rect.top - 8
        rect = pygame.Rect(
            (self.rect.centerx - w/2, 0),
            (w, h)
            )
        pygame.draw.rect(
            screen,
            (0, 255, 0),
            rect
            )
        for enemy in enemy_group:
            if rect.colliderect(enemy.rect):
                enemy.attrs[resource.HP] -= 10
        for host_proj in hostile_projectile_group:
            if rect.colliderect(host_proj):
                hostile_projectile_group.remove(host_proj)
        return

    def update(self, current_time):
        '''Push character to next status.'''
        # Inheritate from 'animation.NewCore'.
        self.to_next_frame(current_time)
        # New firerate limit mechanism.-------------------------------
        self.gcd -= clock.get_rawtime()
        if self.gcd < 0:
            self.gcd = 0
        # ------------------------------------------------------------
        for res in self.attrs.values():
            res.recover(current_time)
        return

# Mob.----------------------------------------------------------------

class Mob(
        pygame.sprite.Sprite,
        animation.NewCore
    ):
    '''Create mob object that oppose to player.'''
    '''Dependencies
        Depends on:
            (1) screen
            (2) abilities
            (3) projectile_group(hostile_project_group)
    '''
    def __init__(
            self,
            *,
            init_x=0,
            init_y=0,
            image=None,
            attrs=None,
            camp=None
        ):
        master, frames = image
        pygame.sprite.Sprite.__init__(self)
        animation.NewCore.__init__(
            self,
            master=master,
            frames=frames
            )

        self.rect.center = init_x, init_y

        self.move_x_rate = 6
        self.move_y_rate = 6

        now = pygame.time.get_ticks() # Get current time.

        self.fire_rate = 1
        self.last_fire = now
        # New attr.---------------------------------------------------
        self.attrs = attrs
        # ------------------------------------------------------------
        self.camp = camp
        # Overwriting params from 'NewCore'.--------------------------
        self.fps = 24
        self.last_draw = now

    def _draw_hpbar(self):
        hp_ratio = int(self.attrs[resource.HP].ratio * 100)
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
        return

    def attack(self, projectile_group):
        now = pygame.time.get_ticks()
        b_shift = lambda: random.randint(-2, 2)
        if now - self.last_fire > self.fire_rate**-1 * 1000:
            self.last_fire = now
            pass
        else:
            return
        image = abilities.default_bullet(color=(255, 150, 0))
        x, y = self.rect.midbottom
        bullet = abilities.Linear(
            init_x=x+b_shift(),
            init_y=y+8,
            direct=1,
            image=image,
        )
        projectile_group.add(bullet)
        return

    def update(self, current_time):
        self.to_next_frame(current_time)
        for res in self.attrs.values():
            res.recover(current_time)
        self._draw_hpbar()

# Skill handler.------------------------------------------------------
'''Psuedo code:

def normalfire(?):
    Dependency:
        bullet handler
        shooter
        *AnimationHandler
    create a bullet
    add to projectile_group
    add gcd

def railgun(?):
    Dependency:
        enemy sprite group
        shooter
        *AnimationHandler
    check the nearest hostile sprite
    draw a beam that ends at the sprite
    damage sprite once
    consume energy(in sprite)
    add gcd

def laserbeam(?):
    Dependency:
        enemy sprite group
        hostile projectile group
        shoooter
        *AnimationHandler
    draw a beam
    attack all hostile sprites
    destroy all hostile bullets
    damage once per tick
    consume energe
    add gcd

Every skill has:
    its function.
    cooldown -> add to 'until_next_fire'(or 'gcd')?
        *We use energy mechanism here, so cooldown could be None or 0,
         this could add to 'global cooldown'(gcd).

How to access:
    Store them in a dict.
        -> What about the params and resource they need?

class SkillHandler():

    def __init__(
            self,
            *,
            sprite=None,
            projectile_handler=None,
            animation_handler=None,
            clock=None
        ):
        self.sprite = sprite
        self.projectile_handler = projectile_handler
        self.clock = clock

    def keyevent(self, keypress):
        React to specific keypress.
    or:
    def __call__(self, keypress):
        React ot specific keypress.


Using of SkillHandler:
    Skillhandler = SkillHandler(...)
    character = Character(...)
    player = PlayerInterface(
        player=character,
        skill=Skillhandler
    )
    player.keyevents(keypress)
        # Calls the skill handler and move.


class PlayerInterface():
    
    def __init__(
            self,
            *,
            sprite=None,
            skill=None
        ):
        self.sprite = sprite
        self.skill = None

    def keyevents(self, keypress):
        self.sprite.move(keypress)
        self.skill.keyevents(keypress)


'''

# Indicator.----------------------------------------------------------
# New HUD is planning.
class Indicator(
        pygame.sprite.Sprite,
        animation.NewCore
    ):
    '''Skill charge instructor.'''
    def __init__(
            self,
            *,
            x_pos=0,
            y_pos=0,
            border_expand=25,
            arc_color=(47, 89, 158, 190),
            rim_color=(0, 255, 255, 215),
            sprite=None,
            resource_name='', # Will be resource flag and change to 'resource_flag'.
            image=None
        ):
        if not sprite:
            raise ValueError("No sprite being monitoring.")
        master, frames = image
        pygame.sprite.Sprite.__init__(self)
        animation.NewCore.__init__(
            self,
            master=master,
            frames=frames
            )
        self.resource = sprite.attrs[resource_name]
        self.sprite = sprite

        self.rect.topleft = x_pos, y_pos
        self.border_expand = border_expand
        self.outer_rect = self.rect.inflate(
            self.border_expand, self.border_expand
            )
        self.arc_color = arc_color
        self.rim_color = rim_color

    def update(self):
        # Note: Redesign HUD for better performing.-------------------
        sprite = self.sprite
        res = self.resource
        current_val = res.current_val
        max_val = res.max_val
        ratio = res.ratio
        surf = pygame.Surface(self.outer_rect.size, pygame.SRCALPHA)
        surf_rect = self.outer_rect.copy()
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
            c_center = self.outer_rect.center
            pygame.draw.circle(
                surf,
                self.rim_color,
                surf_rect.center,
                int(self.outer_rect.width/2),
                3
                )
        screen.blit(surf, (self.outer_rect.topleft))

# Instances.----------------------------------------------------------

player = Character(
    init_x=screen_rect.centerx,
    init_y=screen_rect.centery + 100,
    image=new_ufo,
    attrs=PLAYER_ATTRS,
    camp=Camp.PLAYER
    )
player_group.add(player)
# TEST.---------------------------------------------------------------
# Temporary disabled.
# TEST_ENEMY = Mob(
#     init_x=screen_rect.w / 2,
#     init_y=screen_rect.h / 2,
#     image=new_ufo,
#     attrs=copy.deepcopy(ENEMY_ATTRS)
# )
# tracker = weakref.finalize(
#     TEST_ENEMY,
#     print,
#     "<Test subject has been collected.>"
#     )

# enemy_group.add(TEST_ENEMY)
# TEST.---------------------------------------------------------------
blank100 = animation.sequential_loader(w=100, h=100)

ult = Indicator(
    x_pos=screen_rect.w-180,
    y_pos=screen_rect.h-170,
    border_expand=80,
    resource_name=resource.ULTIMATE, # resource.ULTIMATE
    sprite=player,
    image=blank100
    )

blank75 = animation.sequential_loader(w=75, h=75)

charge = Indicator(
    x_pos=screen_rect.w-350,
    y_pos=screen_rect.h-110,
    border_expand=50,
    resource_name=resource.CHARGE, # resource.CHARGE
    sprite=player,
    image=blank75
    )
blank80 = animation.sequential_loader(w=80, h=80)

HP_monitor = Indicator(
    x_pos=60,
    y_pos=515,
    border_expand=50,
    resource_name=resource.HP, # resource.HP
    arc_color=(25, 221, 0, 240),
    sprite=player,
    image=blank80
    )

HUD_group.add(
    HP_monitor,
    charge,
    ult
    )

# hitbox drawer.------------------------------------------------------

def draw_boxes():
    '''Drawing outline of rects.'''
    for player in player_group:
        frame = pygame.draw.rect(
            screen,
            (0, 255, 0),
            player.rect,
            1
            )
        pass
    for enemy in enemy_group:
        frame = pygame.draw.rect(
            screen,
            (255, 0, 0), # red for enemy.
            enemy.rect,
            1
            )
        pass
    for host_proj in hostile_projectile_group:
        frame = pygame.draw.rect(
            screen,
            (255, 0, 0),
            host_proj.rect.inflate(2, 2),
            1
            )
        pass
    for proj in projectile_group:
        frame = pygame.draw.rect(
            screen,
            (255, 0, 0),
            proj.rect.inflate(2, 2),
            1
            )
        pass
    for eff in animated_object_group:
        frame = pygame.draw.rect(
            screen,
            (0, 255, 0),
            eff.rect,
            1
            )
        pass
    for ui in HUD_group:
        frame = pygame.draw.rect(
            screen,
            (0, 255, 0),
            ui.outer_rect,
            2
            )
        pass
    return

# Handlers.-----------------------------------------------------------

# MobHandle.----------------------------------------------------------

class MobHandle():
    '''Managing group logics of Mob.'''
    '''Dependencies
        Depends on:
            (1) screen
            (2) Mob(class)
            (3) ENEMY_ATTRS
            (4) AnimationHandler
            (5) dice
            (6) Camp
    '''
    def __init__(
            self,
            *,
            group=None,
            animation_handler=None,
            spawn_interval=1,
            max_amount=10,
            camp=None
        ):
        now = pygame.time.get_ticks()
        self.group = group
        self.animation_handler = animation_handler
        self.next_spawn = now + spawn_interval * 1000
        self.spawn_interval = spawn_interval * 1000
        self.max_amount = max_amount
        self.camp = camp

    def refresh(self):
        # Psuedo code:
        # if there is space for spawn, wait for 'spawn_interval':
        #   spawn_enemy()
        #   if spawned, set 'next_spawn' as 'current_time' + 'spawn_interval'
        # if there is no space for spawn, set 'next_spawn' as
        #   'current_time' + 'spawn_interval'
        if self.group is None:
            return
        reset_next_spawn = lambda: current_time + self.spawn_interval
        # The absolute spawntime, maybe relative spawntime is better?
        current_time = pygame.time.get_ticks()

        self.group.update(current_time)
        self.group.draw(screen)

        self._clear_deadbody(current_time)
        self._attack_random(5)

        if len(self.group) < self.max_amount:
            if current_time > self.next_spawn:
                self._spawn_random_pos()
                self.next_spawn = reset_next_spawn() # Reset.
        else:
            self.next_spawn = reset_next_spawn()
        return

    def _spawn_random_pos(self):
        safe_x_pos = lambda: random.randint(100, screen_rect.w-100)
        safe_y_pos = lambda: random.randint(100, screen_rect.h/2)
        enemy = Mob(
            init_x=safe_x_pos(),
            init_y=safe_y_pos(),
            image=new_ufo,
            attrs=copy.deepcopy(ENEMY_ATTRS),
            camp=self.camp
            )
        # Tracking object lifespan.-----------------------------------
        weakref.finalize(
            enemy,
            print,
            f"<Enemy({id(enemy)}) spawn by handler has been collected.>"
            )
        # ------------------------------------------------------------
        while True:
            # Try until the new sprite's rect does not overlap the existings.
            if not pygame.sprite.spritecollide(
                    enemy,
                    self.group,
                    False
                ):
                break
            else:
                if DEV_MODE:
                    print("<Collide detected, rearrange position.>")
                enemy.rect.center = safe_x_pos(), safe_y_pos()
        self.group.add(enemy)
        return

    def _clear_deadbody(self, current_time):
        '''Clear hostile that 'Hp' less/equal than zero.'''
        global KILL_COUNT # Be aware!
        for hostile in self.group:
            if hostile.attrs[resource.HP].current_val <= 0:
                # Override '__le__' method?
                self.group.remove(hostile)
                KILL_COUNT += 1 # Global variable.
                x, y = hostile.rect.center
                self.animation_handler.draw_multi_effects(
                    x=x,
                    y=y,
                    image=new_explode
                    )
                pass
            pass
        return

    def _attack_random(self, chance):
        '''Attack with n percent of chance.'''
        for hostile in self.group:
            # Replace by a relative timer?
            # ex: a dict with sprite-'until_next_fire' or attr 'until_next_fire'?
            if dice(chance):
                hostile.attack(hostile_projectile_group)
                # Play shooting sound here.

# Init handlers.------------------------------------------------------

AnimationHandler = animation.AnimationHandle(
    group=animated_object_group,
    surface=screen
    )

player_bullets = abilities.BulletHandle(
    shooter=player,
    group=projectile_group,
    target_group=enemy_group,
    collide_coef=1.2,
    on_hit=flash
    )

enemy_bullets = abilities.BulletHandle(
    group=hostile_projectile_group,
    target_group=player_group,
    collide_coef=0.7,
    on_hit=flash
    )

MobHandler = MobHandle(
    group=enemy_group,
    animation_handler=AnimationHandler,
    max_amount=17,
    camp=Camp.ENEMY
    )

# Elapsed time.
_elapsed_time = time.perf_counter() - _zero
print(
    "Time spent during initiate: {:.3f} ms".format(
        _elapsed_time * 1000
        )
    )

# hotkey_actions.-----------------------------------------------------
# Not a elegant way.
def hotkey_actions(events):
    global DEV_MODE
    global PAUSE
    global RUN_FLAG

    for event in events:
        if event.type == pygame.QUIT:
            # The 'X' button on righttop corner.
            RUN_FLAG = False
        elif event.type == pygame.KEYDOWN:
            key = event.key

            if key == pygame.K_ESCAPE:
                RUN_FLAG = False
                print("<Exit by 'ESC' key>")
                pass

            if key == pygame.K_F2:
                # Enable/disable develope mode.
                DEV_MODE = not DEV_MODE
                print(f"<DEV_MODE={DEV_MODE}>")
                pass

            if key == pygame.K_F3:
                print("<Charge resource to max>")
                for p_res in player.attrs.values():
                    p_res._to_max()
                for e in enemy_group:
                    for e_res in e.attrs.values():
                        e_res._to_max()
                # for p_res in player._resource_list:
                #     p_res._to_max()
                # for e in enemy_group:
                #     for e_res in e._resource_list:
                #         e_res._to_max()
                #         pass
                #     pass
                pass

            if key == pygame.K_F4:
                # player.Hp.current_val -= 50
                player.attrs[resource.HP].current_val -= 50
                pass

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
        pass
    return

# dev_info.-----------------------------------------------------------
# Not a elegant way.
def dev_info(events):
    '''Catches 'player' and 'event' param in global and show.'''
    def event_info():
        # If there is no event in 'events', for-loop will end immediatly,
        # but 'event' is not changed and will remain its last result.
        if 'event' in globals():
            show_text(
                event,
                0,
                0,
                color=cfg.color.black
                )
            pass
        return

    def player_info():
        # Display character rect infos.
        if 'player' in globals():
            show_text(
                player.rect,
                player.rect.right,
                player.rect.bottom,
                color=cfg.color.black
                )
            show_text(
                player.attrs[resource.HP],
                170,
                490,
                color=cfg.color.black
                )
            pass
        return

    def enemy_info():
        for enemy in enemy_group:
            x, y = enemy.rect.bottomright
            show_text(
                enemy.attrs[resource.HP],
                x,
                y,
                color=cfg.color.black
                )
            pass
        return

    def game_info():
        # Display misc infos.
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
        return

    if DEV_MODE:
        event_info()
        player_info()
        enemy_info()
        game_info()
        pass
    return

# Main phase.---------------------------------------------------------
while RUN_FLAG:
    clock.tick(FPS)
    now = pygame.time.get_ticks()
    # Background.-----------------------
    if DEV_MODE:
        screen.blit(test_grid_partial, (0, 0))
    else:
        screen.fill(BLACK)
    #-----------------------------------

    events = pygame.event.get()
    # Little trick to preserve last result of 'event'.
    for event in events:
        pass
    # Action and info.------------------
    hotkey_actions(events)
    dev_info(events)
    #-----------------------------------
    keypress = pygame.key.get_pressed()

    MobHandler.refresh()
    player_bullets.refresh()
    enemy_bullets.refresh()

    # Transfer to handler?
    player.actions(keypress)
    player_group.update(now)
    player_group.draw(screen)

    AnimationHandler.refresh()

    HUD_group.draw(screen)
    HUD_group.update()

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
    if DEV_MODE:
        draw_boxes()

    pygame.display.flip()
    # End of game process.--------------------------------------------
    pass
# End of game loop.---------------------------------------------------

if __name__ == '__main__':
    pygame.quit()
    sys.exit(0)
