import math
from collections import namedtuple

import pygame

import animation

# Notes.--------------------------------------------------------------
'''
    1.Add penetratable bullets.
    2.Add laser.
'''
#--------------------------------------------------------------------

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
    image = animation.loader(
        image=image,
        w=w,
        h=h
        )
    return image


class Penetratable(pygame.sprite.Sprite):
    pass


class Linear(pygame.sprite.Sprite):
    """Simple linear projectile.(progressing)"""
    @_check_init
    def __init__(
            self,
            *,
            init_x=0,
            init_y=0,
            direct=-1,
            speed=10,
            dmg=20,
            shooter=None,
            image=None
        ):
        super(Linear, self).__init__()

        animation.Core.__init__(
            self,
            image_struct=image
            )

        now = pygame.time.get_ticks()

        self.dmg = dmg
        self.cooldown = 12**-1 * 1000
        self.chargable = True
        self.shooter = shooter

        # Just taking place for future.
        self.hit_count = 0
        self.hit_interval = 0.1
        self.hit_target = []
        self.combo = False
        self.combo_count = 0
        self.combo_max = 0
        self.spawn_time = now

        self.rect.center = init_x, init_y
        self.direct = direct
        self.speed_y = speed
        self.move_rate = 0.1
        self.last_move = now

        self.fps = 24
        self.last_draw = now
        pass

    def update(self, current_time):
        if self.index is not None:
            elapsed_time = current_time - self.last_draw
            if elapsed_time > self.fps**-1 * 1000:
                self.index += 1
                ani_rect = self.animation_list[self.index % self.ani_len]
                self.image = self.master_image.subsurface(ani_rect)
                self.last_draw = current_time
                pass
            pass
        else:
            pygame.draw.rect(
                surface,
                (0, 255, 0, 255),
                self.rect,
                1
                )
            pass
        
        if current_time - self.last_move > self.move_rate:
            self.rect.centery += self.speed_y * self.direct
            self.last_move = current_time
            pass
        return


class BulletHandle():
    """Manage general actions of projectiles."""
    @_check_init
    def __init__(
            self,
            *,
            shooter=None,
            group=None,
            target_group=None,
            collide_coef=1,
            on_hit=None
        ):
        self.shooter = shooter
        self.group = group
        self.target_group = target_group
        self.collide_coef = collide_coef
        self.surface_rect = surface.get_rect()

        self.on_hit = on_hit
        self._on_hit_list = []
        self._on_hit_interval = 0.015

    def refresh(self):
        flash = self.on_hit
        ratio = self.collide_coef
        now = pygame.time.get_ticks()

        self.group.update(now)
        self.group.draw(surface)

        for proj in self.group:
            if not self.surface_rect.contains(proj.rect):
                self.group.remove(proj)

            collides = pygame.sprite.spritecollide(
                proj,
                self.target_group,
                False,
                collided=pygame.sprite.collide_rect_ratio(ratio)
                )
            for collided in collides:
                collided.Hp.current_val -= proj.dmg
                self._ult_feedback(proj.dmg)
                self.group.remove(proj)

                pos_x, pos_y = proj.rect.midtop
                flash_w, flash_h = flash.image.get_rect().size
                flash_pos = (pos_x - flash_w / 2), (pos_y - flash_h / 2)

                surface.blit(flash.image, flash_pos)
        return

    def _ult_feedback(self, val=0):
        shooter = self.shooter # Pass by reference.
        if shooter is None:
            return
        else:
            if hasattr(shooter, 'ult'):
                shooter.ult.charge(val)
                # shooter.Ult.charge(val)
        return
