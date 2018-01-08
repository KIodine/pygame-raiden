from collections import namedtuple

import pygame

import animation
import resource
from characters import CampID

# Notes.--------------------------------------------------------------
'''
    1. Add penetratable bullets.
    2. Add laser.(Added in main module, in 'Character'.)
    3. Depends outer object:
        (1) screen(from pygame.display.set_mode(...))
        (2) animation_handler(possible)
'''
#--------------------------------------------------------------------
ResID = resource.ResID

surface = None
_initiated = False

image_info = namedtuple(
    'Image_time',
    [
        'image',
        'spawn',
        'position'
        ]
    )

# Init.---------------------------------------------------------------
def init(screen):
    """Pass necessary objects into module."""
    global surface
    global _initiated
    # To modify variables, use 'global' keyword.

    surface = screen
    _initiated = True
    return None

def is_initiated() -> bool:
    '''Return True if module is successfully initialized.'''
    return _initiated
# Init.---------------------------------------------------------------

def _check_init(func):
    '''Decorator checks module is initialized or not.'''
    def wrapper(*args, **kwargs):
        '''Takes params.'''
        if not is_initiated():
            raise RuntimeError("Module is not initiated.")
        else:
            pass
        return func(*args, **kwargs)
    return wrapper

def default_bullet(
        size=(5, 15),
        color=(255, 255, 0)
    ):
    """Create default bullet image."""
    image = pygame.Surface(size)
    image.fill(color) # yellow.
    w, h = image.get_rect().size
    image = animation.sequential_loader(
        image=image,
        w=w,
        h=h
        )
    return image


class Hitscan(
        pygame.sprite.Sprite,
        animation.NewCore
    ):
    pass


class Continuous(
        pygame.sprite.Sprite,
        animation.NewCore
    ):
    pass


class Linear(
        pygame.sprite.Sprite,
        animation.NewCore
    ):
    """Simple linear projectile.
    'speed' is px/s.
    """
    @_check_init
    def __init__(
            self,
            *,
            init_x=0,
            init_y=0,
            direct=-1,
            speed=420, # px per second.
            dmg=20, # Add a 'target camp' param?
            camp=None,
            shooter=None,
            image=None
        ):
        master, frames = image
        pygame.sprite.Sprite.__init__(self)
        animation.NewCore.__init__(
            self,
            master=master,
            frames=frames
            )

        now = pygame.time.get_ticks()

        self.dmg = dmg
        self.shooter = shooter
        self.camp = camp
        self.chargable = True
        self.cooldown = 12**-1 * 1000 # ms -> s

        self.rect.center = init_x, init_y
        self.direct = int(direct/abs(direct))
        self.speed_y = speed # Change to relative time?
        self.float_y = init_y

        self.fps = 24
        self.last_draw = now

    def update(self, current_time):
        self.to_next_frame(current_time)
        self.float_y += (self.speed_y / 60) * self.direct
        self.rect.centery = int(self.float_y)
        return

'''Note
    Q: If use identifier, how bullet hits?
        A1: If a bullet meets a sprite that has different camp or target camp,
            attack it; If so, we have to set target camp of a bullet when it's
            been create.
        A2: (pass)
'''
class BulletHandle():
    """Manage general actions of projectiles."""
    @_check_init
    def __init__(
            self,
            *,
            shooter=None,
            camp=None,
            proj_group=None,
            sprite_group=None,
            target_camp=None, # change to 'target_camp'?
            collide_coef=1,
            on_hit=None
        ):
        self.shooter = shooter
        self.camp = camp
        self.proj_group = proj_group
        self.sprite_group = sprite_group
        self.target_camp = target_camp
        self.collide_coef = collide_coef
        self.surface_rect = surface.get_rect()
        self.on_hit = on_hit

    def refresh(self):
        flash = self.on_hit
        ratio = self.collide_coef
        now = pygame.time.get_ticks()

        target_group = [
            sprite for sprite in self.sprite_group
            if sprite.camp == self.target_camp
        ]
        bullets = [
            proj for proj in self.proj_group
            if proj.camp == self.camp
        ]

        for proj in bullets:
            if not self.surface_rect.contains(proj.rect):
                self.proj_group.remove(proj)
                continue
            collides = pygame.sprite.spritecollide(
                proj,
                target_group,
                False,
                collided=pygame.sprite.collide_rect_ratio(ratio)
                )
            for collided in collides:
                collided.attrs[ResID.HP] -= proj.dmg
                self.ult_feedback(proj.dmg)
                self.proj_group.remove(proj)

                pos_x, pos_y = proj.rect.midtop
                flash_w, flash_h = flash.image.get_rect().size
                flash_pos = (pos_x - flash_w / 2), (pos_y - flash_h / 2)

                surface.blit(flash.image, flash_pos)
        return

    def ult_feedback(self, val=0):
        shooter = self.shooter # Pass by reference.
        if shooter is None:
            return
        else:
            res = shooter.attrs[ResID.ULTIMATE]
            if res != ResID.INVALID:
                res += val # Test OK.
        return
