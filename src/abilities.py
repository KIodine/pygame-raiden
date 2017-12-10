from collections import namedtuple

import pygame

import animation
import resource

# Notes.--------------------------------------------------------------
'''
    1.Add penetratable bullets.
    2.Add laser.(Added in main module, in 'Character'.)
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
            dmg=20,
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
        self.chargable = True
        self.cooldown = 12**-1 * 1000 # ms -> s

        # Just taking place for future.-------------------------------
        self.hit_count = 0
        self.hit_interval = 0.1
        self.hit_target = []
        self.combo = False
        self.combo_count = 0
        self.combo_max = 0
        self.spawn_time = now
        # ------------------------------------------------------------

        self.rect.center = init_x, init_y
        self.direct = int(direct/abs(direct))
        self.speed_y = speed

        self.float_y = init_y

        self.fps = 24
        self.last_draw = now

    def update(self, current_time):
        self.to_next_frame(current_time)
        self.float_y += (self.speed_y / 60) * self.direct
        self.rect.centery = int(self.float_y)
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
                collided.attrs[resource.HP].current_val -= proj.dmg
                # collided.Hp.current_val -= proj.dmg
                self._ult_feedback(proj.dmg)
                self.group.remove(proj)

                pos_x, pos_y = proj.rect.midtop
                flash_w, flash_h = flash.image.get_rect().size
                flash_pos = (pos_x - flash_w / 2), (pos_y - flash_h / 2)

                surface.blit(flash.image, flash_pos)
        return

    def _ult_feedback(self, val=0):
        # Not a good idea.
        shooter = self.shooter # Pass by reference.
        if shooter is None:
            return
        else:
            # if hasattr(shooter, 'ult'):
            #     shooter.ult.charge(val)
            # if resource.ULTIMATE in shooter.attrs:
            #     shooter.attrs[resource.ULTIMATE].charge(val)
            # or:
            res = shooter.attrs[resource.ULTIMATE]
            if res != resource.INVALID:
                # res.charge(val)
                res += val # Test OK.
        return
