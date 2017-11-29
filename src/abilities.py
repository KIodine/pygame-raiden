import math
from collections import namedtuple

import pygame


image_info = namedtuple(
    'Image_time',
    [
        'image',
        'spawn',
        'position'
        ]
    )


class Linear(pygame.sprite.Sprite):
    """Simple linear projectile.(progressing)"""

    def __init__(self,
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

        # Remove when finished.
        raise NotImplementedError("Progressing")

        animation.Core.__init__(
            self,
            image_struct=image
            )

        now = pygame.time.get_ticks()

        self.dmg = dmg
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

    def update(self):
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
        return


class BulletHandle():

    def __init__(self,
                 *,
                 shooter=None,
                 group=None,
                 target_group=None,
                 collide_coef=1,
                 surface=None,
                 on_hit=None
                 ):
        self.shooter=shooter
        self.group = group
        self.target_group = target_group
        self.collide_coef = collide_coef
        self.surface = surface
        self.surface_rect = surface.get_rect()
        
        self.on_hit = on_hit
        self._on_hit_list = []
        self._on_hit_interval = 0.015

    def refresh(self):
        flash = self.on_hit
        ratio = self.collide_coef
        now = pygame.time.get_ticks()
        
        self.group.update(now)
        self.group.draw(self.surface)

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

                self.surface.blit(flash.image, flash_pos)
        return

    def _ult_feedback(self, val=0):
        shooter = self.shooter # Pass by reference.
        if shooter is None:
            return
        else:
            if hasattr(shooter, 'Ult'):
                shooter.Ult.charge(val)
        return
