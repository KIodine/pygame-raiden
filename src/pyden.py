# Native.-------------------------------------------------------------
import sys
import os
import random
import math
import time
from collections import deque, namedtuple
# Third-party.--------------------------------------------------------
import pygame
# Custom.-------------------------------------------------------------
import config as cfg
import animation
import abilities
import resource

# Pyden 0.41.2

# Note: Seperate actions from player for further develope.
#   Add a 'Interface' class could be a solution, but clarify its structure
#   is more important.
# Note: Rename config module?

_zero = time.perf_counter() # Reference point.

dice = lambda chn: True if chn > random.random() * 100 else False

# Set constants.------------------------------------------------------

W_WIDTH = cfg.W_WIDTH
W_HEIGHT = cfg.W_HEIGHT
DEFAULT_COLOR = cfg.default_bgcolor
BLACK = cfg.color.black

FPS = 60

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

# Init custom modules.------------------------------------------------

abilities.init(screen)
assert abilities.is_initiated()

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

explode = animation.loader(
    image=explode_dir,
    w=50,
    h=50,
    col=1, # Full: 6. Shorter frames for better performance.
    row=5
    )

new_explode = animation.sequential_loader(
    image=explode_dir,
    w=50,
    h=50,
    col=1,
    row=5
)

ufo = animation.loader(
    image=ufo_dir,
    w=58,
    h=34,
    col=12
    )

new_ufo = animation.sequential_loader(
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

new_flash = animation.sequential_loader(
    image=flash_dir,
    w=15,
    h=15
)

# Functions.----------------------------------------------------------

def show_text(
        text: str,
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
        h=50,
        color=(0, 0, 0, 0)
    ) -> pygame.Surface:
    surface = pygame.Surface(
        (w, h),
        pygame.SRCALPHA
        )
    surface.fill(color)
    return surface

# Classes.------------------------------------------------------------

# Character.----------------------------------------------------------

class Character(
        pygame.sprite.Sprite,
        animation.NewCore
    ):
    '''Create player character for manipulation.'''
    def __init__(
            self,
            *,
            init_x=0,
            init_y=0,
            image=None
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

        self.fire_rate = 12
        self.last_fire = now

        # ------------------------------------------------------------
        self.Hp = resource.default_player_hp(
            init_time=now
        )
        self.Charge = resource.default_player_charge(
            init_time=now
        )
        self.ult = resource.default_player_ultimate(
            init_time=now
        )
        # ------------------------------------------------------------
        self._resource_list = [
            self.Charge,
            self.ult,
            self.Hp
            ]
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
            ratio = self.Charge.ratio
            if self.Charge.ratio == 1:
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
                        (255, 128, 0),
                        eff_bar
                        )
                    AnimationHandler.draw_single(
                        x=eff_bar.centerx,
                        y=eff_bar.top,
                        image=new_flash
                        )
                    hit.Hp.current_val -= 120
                    # Only when the skill hits enemy then energy consume.
                    self.Charge._to_zero()
                    self.ult.charge(120)
                else:
                    pass
                # ----------------------------------------------------

        if keypress[pygame.K_l]:
            # (Replaced)Cast ult.
            if self.ult.ratio == 1:
                self.ult._to_zero()

        # Ultimate.---------------------------------------------------
        if keypress[pygame.K_u] and not self.ult_active:
            if self.ult.ratio == 1:
                print("<Ultimate activated>")
                self.ult_active = True

        if keypress[pygame.K_u] \
           and self.ult_active \
           and (self.ult.ratio != 0):
            self._laser()
            self.ult.current_val -= 13
        else:
            if self.ult_active == True:
                self.ult_active = False
                print((
                    "<Ultimate deactiveted,"
                    " remaining energy: {u_ratio:.2f}%>".format(
                        u_ratio=self.ult.ratio * 100
                        )
                    ))
        # ------------------------------------------------------------
        return

    def move(self, keypress):
        '''Move player according to keypress, using WASD keys.'''
        rect = self.rect
        if keypress[pygame.K_w] and self.rect.top > screen_rect.top:
            rect.move_ip(0, -self.move_y_rate) # This is OK.
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
        image = abilities.default_bullet(color=cfg.color.yellow)
        x, y = self.rect.midtop
        bullet = abilities.Linear(
            init_x=x + b_shift(),
            init_y=y - 8,
            image=image,
            speed=18,
            dmg=22,
            shooter=self
        )
        projectile_group.add(bullet)
        return

    def _laser(self):
        bottom = self.rect.top - 8
        top = 0
        w = 20
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
                enemy.Hp.current_val -= 10
        for host_proj in hostile_projectile_group:
            if rect.colliderect(host_proj):
                hostile_projectile_group.remove(host_proj)
        return

    def update(self, current_time):
        '''Push character to next status.'''
        # Inheritate from 'animation.NewCore'.
        self.to_next_frame(current_time)
        for res in self._resource_list:
            res.recover(current_time)
        return

# Mob.----------------------------------------------------------------

class Mob(
        pygame.sprite.Sprite,
        animation.NewCore
    ):
    '''Create mob object that oppose to player.'''
    def __init__(
            self,
            *,
            init_x=0,
            init_y=0,
            image=None
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

        # ------------------------------------------------------------
        self.Hp = resource.default_enemy_hp(
            init_time=now
        )
        # ------------------------------------------------------------
        self._resource_list = [
            self.Hp
            ]

        # Overwriting params from 'NewCore'.--------------------------
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
        for res in self._resource_list:
            res.recover(current_time)
        self._draw_hpbar()

# Animated_object.----------------------------------------------------

class Animated_object(
        pygame.sprite.Sprite,
        animation.NewCore
    ):
    '''Building pure effect with image.'''
    def __init__(
            self,
            *,
            init_x=0,
            init_y=0,
            image=None
        ):
        master, frames = image
        pygame.sprite.Sprite.__init__(self)
        animation.NewCore.__init__(
            self,
            master=master,
            frames=frames
            )

        self.rect.center = init_x, init_y

        self.fps = 12
        self.last_draw = pygame.time.get_ticks()

    def update(self, current_time):
        self.to_next_frame(current_time)
        return

# Indicator.----------------------------------------------------------
# New HUD is planning.
# Still using old-type 'animation.Core'.
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
            resource_name='',
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
        self.resource = getattr(sprite, resource_name)
        self.sprite = sprite

        self.rect.topleft = x_pos, y_pos

        self.border_expand = border_expand
        self.arc_color = arc_color
        self.rim_color = rim_color

    def update(self):
        # Note: Redesign HUD for better performing.-------------------
        sprite = self.sprite
        res = self.resource
        current_val = res.current_val
        max_val = res.max_val
        ratio = res.ratio
        self.outer_rect = self.rect.inflate(
            self.border_expand, self.border_expand
            )
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
    image=new_ufo
    )

player_group = pygame.sprite.Group()
player_group.add(player)

enemy = Mob(
    init_x=screen_rect.centerx - 100,
    init_y=screen_rect.centery,
    image=new_ufo
    )

enemy_group = pygame.sprite.Group()
enemy_group.add(enemy)

projectile_group = pygame.sprite.Group()
hostile_projectile_group = pygame.sprite.Group()

animated_object_group = pygame.sprite.Group()

blank100 = animation.sequential_loader(w=100, h=100)

ult = Indicator(
    x_pos=screen_rect.w-180,
    y_pos=screen_rect.h-170,
    border_expand=80,
    resource_name='ult',
    sprite=player,
    image=blank100
    )

blank75 = animation.sequential_loader(w=75, h=75)

charge = Indicator(
    x_pos=screen_rect.w-350,
    y_pos=screen_rect.h-110,
    border_expand=50,
    resource_name='Charge',
    sprite=player,
    image=blank75
    )
blank80 = animation.sequential_loader(w=80, h=80)

HP_monitor = Indicator(
    x_pos=60,
    y_pos=515,
    border_expand=50,
    resource_name='Hp',
    arc_color=(25, 221, 0, 240),
    sprite=player,
    image=blank80
    )

HUD_group = pygame.sprite.Group()
HUD_group.add(
    HP_monitor,
    charge,
    ult
    )

# hitbox drawer.------------------------------------------------------

def draw_boxes():
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
            (0, 255, 0, 255),
            ui.outer_rect,
            2
            )
        pass
    return

# Handlers.-----------------------------------------------------------

class AnimationHandle():
    '''Handle effects.'''
    def __init__(
            self,
            *,
            group=None,
        ):
        self.group = group
        self.draw_queue = list()
        self.draw_multi_delay = 0.1 * 1000
        self.last_draw_multi = pygame.time.get_ticks()
        self.timestamped = namedtuple(
            'Stamped_Frame',
            [
                'timestamp',
                'frame'
                ]
            )

    def draw_single(
            self,
            *,
            x=0,
            y=0,
            image=None
        ):
        eff = Animated_object(
            init_x=x,
            init_y=y,
            image=image
            )
        self.group.add(eff)
        return

    def draw_multi_effects(
            self,
            *,
            x=0,
            y=0,
            image=None,
            diff=16,
            num=5,
            interval=0.08
        ):
        if image is None:
            return
        now = pygame.time.get_ticks()
        diff_pos = lambda: random.randint(-diff, diff)
        self.draw_multi_delay = interval * 1000
        for i in range(num):
            eff = Animated_object(
                init_x=x+diff_pos(),
                init_y=y+diff_pos(),
                image=image
                )
            pair = self.timestamped(
                now + interval * 1000 * i, eff
                )
            self.draw_queue.append(pair)
            # Sort draw order when inserting new effects.
            self.draw_queue.sort(
                key=lambda x: x.timestamp
                )
        return

    def refresh(self):
        now = pygame.time.get_ticks()
        for ani in self.group:
            # Clear animations that had played once.
            if ani.played >= 1:
                self.group.remove(ani)
        if len(self.draw_queue) != 0:
            if self.draw_queue[0].timestamp < now:
                self.group.add(self.draw_queue.pop(0).frame)
        self.group.update(now)
        self.group.draw(screen)
        return

# MobHandle.----------------------------------------------------------

class MobHandle():
    '''Managing group logics of Mob.'''
    def __init__(
            self,
            *,
            group=None,
            spawn_interval=1,
            max_amount=10
        ):
        now = pygame.time.get_ticks()

        self.next_spawn = now + spawn_interval * 1000
        self.group = group
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

        self.group.update(current_time)
        self.group.draw(screen)

        reset_next_spawn = lambda: current_time + self.spawn_interval

        if self.group is None:
            return
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
        # Add check(Psuedo code):
        #   if enemy.rect collides existing enemy:
        #     retry
        safe_x_pos = lambda: random.randint(100, screen_rect.w-100)
        safe_y_pos = lambda: random.randint(100, screen_rect.h/2)

        enemy = Mob(
            init_x=safe_x_pos(),
            init_y=safe_y_pos(),
            image=new_ufo
            )
        while True:
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
        # Clear deadbody and play explosion.
        global KILL_COUNT

        for hostile in self.group:
            if hostile.Hp.current_val <= 0:
                self.group.remove(hostile)

                 # Not a good choice.
                KILL_COUNT += 1

                x, y = hostile.rect.center
                # Test.-------------------------------------
                # Bad coupling, need to solve.
                # Solved @ 171203.
                AnimationHandler.draw_multi_effects(
                    x=x,
                    y=y,
                    image=new_explode
                    )
                # Test.-------------------------------------
                pass
            pass
        return

    def _attack_random(self, chance):
        '''Attack with n percent of chance.'''
        for hostile in self.group:
            if dice(chance):
                hostile.attack(hostile_projectile_group)
                # Play shooting sound here.

# Instance.-----------------------------------------------------------

# Transfer to seperate module?
AnimationHandler = AnimationHandle(
    group=animated_object_group
    )

MobHandler = MobHandle(
    group=enemy_group,
    max_amount=17
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
                for p_res in player._resource_list:
                    p_res._to_max()
                for e in enemy_group:
                    for e_res in e._resource_list:
                        e_res._to_max()
                        pass
                    pass
                pass

            if key == pygame.K_F4:
                player.Hp.current_val -= 50
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
    '''\
Catches 'player' and 'event' param in global and show.\
'''
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
                player.Hp,
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
                enemy.Hp,
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
