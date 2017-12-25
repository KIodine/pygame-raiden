# Native.-------------------------------------------------------------
import sys
import os
import random
import math
import time
import copy
import weakref # Analyzing object lifespan.
import logging
from collections import deque, namedtuple
from enum import Enum
# Third-party.--------------------------------------------------------
import pygame
# Custom.-------------------------------------------------------------
import config as cfg
import animation
import abilities
import resource
import characters
import ui
import particle

# Pyden 0.42.5
'''Notes:
    1. Seperate actions from player for further develope.
        Add a 'Interface' class could be a solution, but clarify its structure
        is more important.
    2. (Suspended)Rename config module?
    3. The way to share 'AnimationHandler', passing reference when initialize
        related module?
    4. 'Character', 'Mob', 'MobHandle' and someother are coupled with
        'animation.AnimationHandle'(Note-3)
    5. (OK)Use custom identifier than seperate group?
'''

_zero = time.perf_counter() # Reference point.

logging.basicConfig(level=logging.WARNING)

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
if nfail != 0:
    if pygame.mixer.get_init() is None:
        logging.warning("pygame mixer initialization failed.")
    else:
        logging.warning("Pygame component initialization failed")
pygame.display.init()
pygame.display.set_caption("Interstellar")

screen = pygame.display.set_mode(cfg.W_SIZE, 0, 32) # RGBA
screen.fill(cfg.color.black)

screen_rect = screen.get_rect()

# Init containers.----------------------------------------------------

sprite_group = pygame.sprite.Group() # Universal.
projectile_group = pygame.sprite.Group() # Universal.

animated_object_group = pygame.sprite.Group()
HUD_group = pygame.sprite.Group()

ALL_GROUPS = list()
ALL_GROUPS.extend(
    [
        sprite_group,
        projectile_group,
        animated_object_group,
        HUD_group
    ]
)
# Identifier for camp.
CampID = characters.CampID
# Identifier for resource.
ResID = resource.ResID

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
        ResID.HP: resource.default_player_hp(),
        ResID.CHARGE: resource.default_player_charge(),
        ResID.ULTIMATE: resource.default_player_ultimate()
    }
)

ENEMY_ATTRS = resource.RES_DICT(
    {
        ResID.HP: resource.default_enemy_hp()
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
            camp=None,
            enemy=None
        ):
        master, frames = image
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
        self.enemy = enemy
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
            # particle --------------------------------------------- #
            # particle.spawn_normalvar(
            #     self.rect.midtop,
            #     (0, 0),
            #     5,
            #     1.1,
            #     0
            # )
            # particle --------------------------------------------- #
            self.create_bullet(projectile_group)
            return

        if keypress[pygame.K_k] and not self.ult_active:
            # Cast charged skill.
            self.railgun()
            return

        if keypress[pygame.K_u] and not self.ult_active:
            if self.attrs[ResID.ULTIMATE].ratio == 1:
                print("<Ultimate activated>")
                self.ult_active = True
            else:
                print(
                    "<Insufficient energy: {}>".format(
                        self.attrs[ResID.ULTIMATE].ratio
                    )
                )

        if keypress[pygame.K_u] \
           and self.ult_active \
           and (self.attrs[ResID.ULTIMATE].ratio != 0):
            self.laser()
            self.attrs[ResID.ULTIMATE] -= 13
        else:
            if self.ult_active == True:
                self.ult_active = False
                print((
                    "<Ultimate deactiveted,"
                    " remaining energy: {u_ratio:.2f}%>".format(
                        u_ratio=self.attrs[ResID.ULTIMATE].ratio * 100
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

    def create_bullet(self, projectile_group):
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
            camp=self.camp,
            shooter=self
        )
        projectile_group.add(bullet)
        # self.gcd += bullet.cooldown
        return

    def laser(self):
        # Test.
        particle.spawn_normalvar(
                self.rect.midtop,
                (0, 0),
                5,
                0.3,
                0
            )
        # Test.
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
        # Test filter.------------------------------------------------
        # CID filter in '_laser'.
        enemies = [
            sprite for sprite in sprite_group
            if sprite.camp == CampID.ENEMY
        ]
        host_ps = [
            projectile for projectile in projectile_group
            if projectile.camp == CampID.ENEMY
        ]
        # ------------------------------------------------------------
        for enemy in enemies:
            if rect.colliderect(enemy.rect):
                enemy.attrs[ResID.HP] -= 10
                # Test.
                particle.spawn_normalvar(
                    enemy.rect.midbottom,
                    (0, 0),
                    9,
                    1.1,
                    0
                )
                # Test.
        for host_proj in host_ps:
            if rect.colliderect(host_proj):
                projectile_group.remove(host_proj)
        return

    def railgun(self):
        ratio = self.attrs[ResID.CHARGE].ratio
        if ratio != 1:
            return
        else:
            rect = self.rect
            w = 5
            h = rect.top
            x = rect.centerx - w / 2
            y = 0
            check_rect = pygame.Rect(
                (x, y), (w, h)
                )
            # CID filter in 'railgun'.
            collide_list = [
                sprite for sprite in sprite_group
                if check_rect.colliderect(sprite.rect)
                if sprite.camp == CampID.ENEMY
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
                hit.attrs[ResID.HP] -= 120
                # Only when the skill hits enemy then energy consume.
                self.attrs[ResID.CHARGE]._to_zero()
                self.attrs[ResID.ULTIMATE] += 120

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
        # Spring move test.-------------------------------------------
        self.float_v = 0.0
        self.float_s = 0.0
        self.dest_x, self.dest_y = self.rect.center
        self.is_at_dest = True
        self.dist_to_dest = 0.0
        self.direct_v = pygame.math.Vector2(0, 0)
        self.float_center = pygame.math.Vector2(0, 0)
        self.base_v = pygame.math.Vector2(0, 0)
        # Lock mechanism.
        self.until_next_move = 0.0
        self.ready_to_move = True
        # Spring move test.-------------------------------------------
        now = pygame.time.get_ticks() # Get current time.

        self.until_next_fire = 0
        self.ready_to_fire = True

        self.attrs = attrs

        self.camp = camp
        # Overwriting params from 'NewCore'.--------------------------
        self.fps = 24
        self.last_draw = now

    def draw_hpbar(self):
        hp_ratio = int(self.attrs[ResID.HP].ratio * 100)
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
        rd_next = lambda: random.randint(500, 1300)
        if self.ready_to_fire:
            self.ready_to_fire = False
            self.until_next_fire += rd_next()
        else:
            return
        image = abilities.default_bullet(color=(255, 150, 0))
        x, y = self.rect.midbottom
        bullet = abilities.Linear(
            init_x=x+b_shift(),
            init_y=y+8,
            direct=1,
            camp=self.camp,
            image=image,
        )
        projectile_group.add(bullet)
        return

    def set_dest(self, x, y):
        if not self.is_at_dest or not self.ready_to_move:
            return
        logging.debug(
            f"<sprite({hex(id(self))}) has set its dest to ({x}, {y})>"
            f"<Current: {self.rect.center}>"
            )
        self.base_v = pygame.math.Vector2(self.rect.center)
        self.float_center = self.base_v
        self.dest_x, self.dest_y = int(x), int(y)
        self.dest_s = pygame.math.Vector2(
            self.dest_x, self.dest_y
        )
        self.dist_to_dest = math.hypot(
            (x - self.rect.centerx),
            (y - self.rect.centery)
        )
        self.is_at_dest = False
        self.ready_to_move = False
        self.direct_v = pygame.math.Vector2(self.dest_x, self.dest_y) - \
            self.base_v
        self.direct_v = self.direct_v.normalize() # Get the direction vector.
        return

    def spring_move(self):
        if self.is_at_dest:
            return
        # This is not a correct answer.
        dest_x, dest_y = self.dest_x, self.dest_y
        # Consts.--------------------------------------------------- #
        pd = 0.03
        td = 0.5
        freq = 0.7
        epsilon = 2
        # Consts.--------------------------------------------------- #
        vector_now = pygame.math.Vector2(self.rect.center)
        t = clock.get_time()/1000
        # Use 'Vector2'? How?
        def spring(
                x, v, xt,
                zeta, omega, h
            ):
            """Damped spring move."""
            f = 1.0 + 2.0 * h * zeta * omega
            oo = omega * omega
            hoo = h * oo
            hhoo = h * hoo
            detInv = 1.0 / (f + hhoo)
            detX = f * x + h * v + hhoo * xt
            detV = v + hoo * (xt - x)
            x = detX * detInv
            v = detV * detInv
            return x, v

        def omega(f):
            """Translate frequency to angular velocity."""
            o = 2 * math.pi * f
            return o

        def zeta(pd, td, o):
            """Return damping ratio according to params."""
            k = math.log(pd) / (-o * td)
            return k

        # New mechanism. ------------------------------------------- #
        z = zeta(pd, td, omega(freq))
        s_next, v_next = spring(
            self.float_s, self.float_v, self.dist_to_dest,
            z, omega(freq), t
        )
        # Problem(OK)
        # print("Before", self.float_center, end='; ')
        self.float_center = self.base_v + (s_next * self.direct_v)
        # print("After", self.float_center)
        # Problem(OK)
        self.rect.center = self.float_center
        # NOTE!:
        #   Calibrate 'float_s' and 'float_v' after it reaches destination!
        #   Otherwise it causes sudden movement at the start of next move!
        self.float_s = s_next
        self.float_v = v_next

        # New mechanism. ------------------------------------------- #

        # Judge.---------------------------------------------------- #
        at_dest_x_fuzzy = abs(self.rect.centerx - self.dest_x) <= epsilon
        at_dest_y_fuzzy = abs(self.rect.centery - self.dest_y) <= epsilon

        if at_dest_x_fuzzy and at_dest_y_fuzzy:
            logging.debug(f"<sprite({hex(id(self))}) is at its destnation.>")
            self.is_at_dest = True
            self.base_v = pygame.math.Vector2(self.rect.center)
            # Reset params.
            self.float_s = 0.0
            self.float_v = 0.0
            self.direction = pygame.math.Vector2(0, 0)
            # Set until next move.
            self.until_next_move = random.randint(4000, 6000)
            print(f"Until next move: {self.until_next_move/1000}")
        # Judge.---------------------------------------------------- #
        return None

    def update(self, current_time):
        self.to_next_frame(current_time)
        self.spring_move()
        dt = clock.get_time()
        for res in self.attrs.values():
            res.recover(current_time)

        if not self.ready_to_fire:
            # Relative mode.
            self.until_next_fire -= dt
            if self.until_next_fire <= 0:
                self.until_next_fire = 0
                self.ready_to_fire = True

        if not self.ready_to_move and self.is_at_dest:
            self.until_next_move -= dt
            if self.until_next_move <= 0:
                self.until_next_move = 0
                self.ready_to_move = True

        self.draw_hpbar()

# Skill handler.------------------------------------------------------

# Instances.----------------------------------------------------------

player = Character(
    init_x=screen_rect.centerx,
    init_y=screen_rect.centery + 100,
    image=new_ufo,
    attrs=PLAYER_ATTRS,
    camp=CampID.PLAYER,
    enemy=CampID.ENEMY
    )

sprite_group.add(player)

# hitbox drawer.------------------------------------------------------

def draw_boxes():
    '''Drawing outline of rects.'''
    for sprite in sprite_group:
        if sprite.camp == CampID.PLAYER:
            fcolor = (0, 255, 0)
        elif sprite.camp == CampID.ENEMY:
            fcolor = (255, 0, 0)
        frame = pygame.draw.rect(
            screen,
            fcolor,
            sprite.rect,
            1
        )
    for proj in projectile_group:
        if proj.camp == CampID.PLAYER:
            fcolor = (0, 255, 0)
        elif proj.camp == CampID.ENEMY:
            fcolor = (255, 0, 0)
        frame = pygame.draw.rect(
            screen,
            fcolor,
            proj.rect.inflate(2, 2),
            1
            )
    for eff in animated_object_group:
        frame = pygame.draw.rect(
            screen,
            (0, 255, 0),
            eff.rect,
            1
            )
    for ui in HUD_group:
        frame = pygame.draw.rect(
            screen,
            (0, 255, 0),
            ui.outer_rect,
            2
            )
        pass
    return

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
            (6) CampID
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
        if self.group is None:
            return
        reset_next_spawn = lambda: current_time + self.spawn_interval
        # The absolute spawntime, maybe relative spawntime is better?
        current_time = pygame.time.get_ticks()

        self.clear_deadbody(current_time)
        self.attack_random()
        self.move_sprite()

        group = [
            sprite for sprite in self.group
            if sprite.camp == self.camp
        ]

        if len(group) < self.max_amount:
            if current_time > self.next_spawn:
                self.spawn_random_pos()
                self.next_spawn = reset_next_spawn() # Reset.
        else:
            self.next_spawn = reset_next_spawn()
        return

    def spawn_random_pos(self):
        """Spawn a mob at random place without overlap the others."""
        safe_x_pos = lambda: random.randint(100, screen_rect.w-100)
        safe_y_pos = lambda: random.randint(100, screen_rect.h/2)
        enemy = Mob(
            init_x=safe_x_pos(),
            init_y=safe_y_pos(),
            image=new_ufo,
            attrs=copy.deepcopy(ENEMY_ATTRS),
            camp=self.camp
            )
        while True:
            # Try until the new sprite's rect does not overlap the existings.
            if not pygame.sprite.spritecollide(
                    enemy,
                    self.group,
                    False
                ):
                AnimationHandler.draw_multi_effects(
                    x=enemy.rect.centerx,
                    y=enemy.rect.centery,
                    num=12,
                    interval=0.05,
                    image=new_flash,
                    fps=6
                )
                break
            else:
                if DEV_MODE:
                    print("<Collide detected, rearrange position.>")
                enemy.rect.center = safe_x_pos(), safe_y_pos()
        self.group.add(enemy)
        return

    def clear_deadbody(self, current_time):
        '''Clear hostile that 'Hp' less/equal than zero.'''
        global KILL_COUNT # Be aware!
        # CID filter in '_clear_deadbody'
        group = [
            sprite for sprite in self.group
            if sprite.camp == self.camp
        ]
        for hostile in group:
            if hostile.attrs[ResID.HP].current_val <= 0:
                self.group.remove(hostile)
                KILL_COUNT += 1 # Global variable.
                x, y = hostile.rect.center
                self.animation_handler.draw_multi_effects(
                    x=x,
                    y=y,
                    image=new_explode
                    )
                particle.spawn_uniform(
                    hostile.rect.center,
                    (0, 0),
                    15,
                    1.1,
                    0
                )
                pass
            pass
        return

    def attack_random(self):
        '''Attack with n percent of chance.'''
        # Filter sprite by CIDfilter.------------------------------- #
        cid_group = characters.CIDfilter(self.group, self.camp)
        ready_group = [
            sprite for sprite in cid_group
            if sprite.ready_to_fire
            ]
        member_count = len(ready_group)
        k = member_count if member_count < 5 else 5
        for hostile in random.choices(ready_group, k=k):
            hostile.attack(projectile_group)
        return

    def move_sprite(self):
        safe_x_pos = lambda: random.randint(100, screen_rect.w-100)
        safe_y_pos = lambda: random.randint(100, screen_rect.h/2)
        cid_group = characters.CIDfilter(self.group, self.camp)
        ready_group = [
            sprite for sprite in cid_group
            if sprite.is_at_dest is True
        ]
        member_count = len(ready_group)
        k = member_count if member_count < 5 else 5
        for sprite in random.choices(ready_group, k=k):
            sprite.set_dest(safe_x_pos(), safe_y_pos())
            # Seems not suit?
            # Splitting x and y is not right, treat as 'distance',
            # then split into x and y vector.
        return

# Init handlers.------------------------------------------------------

AnimationHandler = animation.AnimationHandle(
    group=animated_object_group,
    surface=screen
    )

player_bullets = abilities.BulletHandle(
    shooter=player,
    camp=CampID.PLAYER,
    proj_group=projectile_group,
    sprite_group=sprite_group,
    target_camp=CampID.ENEMY,
    collide_coef=1.2,
    on_hit=flash
    )

enemy_bullets = abilities.BulletHandle(
    proj_group=projectile_group, # projectile_group
    camp=CampID.ENEMY,
    sprite_group=sprite_group,
    target_camp=CampID.PLAYER,
    collide_coef=0.7,
    on_hit=flash
    )

MobHandler = MobHandle(
    group=sprite_group, # sprite_group
    animation_handler=AnimationHandler,
    max_amount=17,
    camp=CampID.ENEMY
    )

# Elapsed time during initialization.
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

            if key == pygame.K_F2:
                # Enable/disable develope mode.
                DEV_MODE = not DEV_MODE
                print(f"<DEV_MODE={DEV_MODE}>")

            if key == pygame.K_F3:
                print("<Charge resource to max>")
                for sprite in sprite_group:
                    for res in sprite.attrs.values():
                        res._to_max()

            if key == pygame.K_F4:
                player.attrs[ResID.HP] -= 50

            if key == pygame.K_p:
                PAUSE = not PAUSE
                print("<PAUSE>")
                while PAUSE:
                    event = pygame.event.wait()
                    if event.type == pygame.KEYDOWN\
                       and event.key == pygame.K_p:
                        PAUSE = not PAUSE
                        print("<ACTION>")
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
                player.attrs[ResID.HP],
                170,
                490,
                color=cfg.color.black
                )
            pass
        return

    def enemy_info():
        enemies = [
            sprite for sprite in sprite_group
            if sprite.camp == CampID.ENEMY
        ]
        for enemy in enemies:
            x, y = enemy.rect.bottomright
            show_text(
                enemy.float_center,
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


    # Update duplicate.-----------------------------------------------
    player_bullets.refresh()
    enemy_bullets.refresh()

    projectile_group.update(now)
    projectile_group.draw(screen)
    # ----------------------------------------------------------------

    # Transfer to handler?
    player.actions(keypress)

    sprite_group.update(now)
    sprite_group.draw(screen)
    MobHandler.refresh()
    
    # Test Vector2. ------------------------------------------------ #
    # Nothing, just testing the 'pygame.math.Vector2' module.
    # Confirmed that 'Vector2' object can use as tuple(or iterable) as well.
    mouse_posv = pygame.math.Vector2(
        pygame.mouse.get_pos()
    )
    mouse_vector = pygame.math.Vector2(
        pygame.mouse.get_rel()
    )
    pygame.draw.line(
        screen, (200, 255, 0),
        mouse_posv, (mouse_posv + mouse_vector),
        1
    )
    # -------------------------------------------------------------- #

    # Testing New UI.----------------------------------------------- #
    # Note: The params and layout is not polished yet!
    # Debug, aligning.
    if DEV_MODE:
        pygame.draw.line(
            screen, (128, 255, 0),
            (player.rect.centerx - 250, player.rect.centery),
            (player.rect.centerx + 250, player.rect.centery),
            1
        )
        pygame.draw.arc(
            screen, (128, 255, 0),
            player.rect.inflate(400, 400),
            math.radians(180), math.radians(360),
            1
        )
        # The arc seems not drawing the 'final step'.
    # Debug -------------------------------------------------------- #
    # Use UIIntegrater to simplify drawing?
    ui.expand_arc(
        player,
        ResID.HP,
        screen,
        radius=150,
        ind_color=(0, 255, 255),
        rim_width=4
    )

    ui.expand_arc(
        player,
        ResID.CHARGE,
        screen,
        radius=175,
        base_angle=math.radians(210),
        expand_angle=math.radians(25),
        rim_color=(47, 89, 158),
        ind_color=(0, 255, 255),
        gap=math.radians(2.5)
    )

    ui.expand_arc(
        player,
        ResID.ULTIMATE,
        screen,
        radius=175,
        base_angle=math.radians(300),
        expand_angle=math.radians(50),
        rim_color=(255, 175, 63),
        ind_color=(0, 255, 255),
        gap=math.radians(2.5)
    )

    if player.attrs[ResID.ULTIMATE].ratio == 1:
        arrow_color = (0, 255, 255)
    else:
        arrow_color = (255, 255, 0)
    ui.arrow_to(
        screen,
        player.rect.center,
        270,
        30,
        color=arrow_color
    )
    # Not useful, just for experiment.
    ui.sight_index(
        player,
        sprite_group,
        CampID.ENEMY,
        screen
    )
    # Testing new ui------------------------------------------------ #

    # Test particle effects ---------------------------------------- #
    for part in particle.mess:
        if not (0 < part.rect.centerx < screen_rect.w)\
        or part.rect.centery > screen_rect.h:
            particle.mess.remove(part)
        if part.dead:
            particle.mess.remove(part)

    particle.mess.update(clock.get_time())
    particle.mess.draw(screen)
    # Test particle effects ---------------------------------------- #

    AnimationHandler.refresh()

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
