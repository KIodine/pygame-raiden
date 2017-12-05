import functools

import pygame

import animation
import abilities
import resource

# WARNING=============================================================
# This module is still progressing,
# ====================================================================

raise NotImplementedError("This module is still progressing.")

# Note.---------------------------------------------------------------
'''
    1.Reconstruct 'Character' and 'Mob', add interface between handle and them.
'''
# Note.---------------------------------------------------------------

surface = None
surface_rect = None
_initiated = False

def init(screen):
    """Pass necessary objects into module."""
    global surface
    global surface_rect
    global _initiated

    surface = screen
    surface_rect = screen.get_rect()
    _initiated = True

def is_initiated() -> bool:
    '''Return True if module is successfully initialized.'''
    return _initiated

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

# Interface for indirect control.-------------------------------------

class Interface():
    '''Progressing'''
    def __init__(
            self,
            *,
            sprite,
            bullet_group
        ):
        '''Should take sprite.'''
        raise NotImplementedError
        self.sprite = sprite
        self.bullet_group = bullet_group
        self.action_dict = dict()
        
    def set_action(
            self,
            *,
            key,
            ability
        ):
        '''Set action.'''
        raise NotImplementedError
        # Psuedo code:
        # takes 'pygame.K_*' and 'abilities'.
        # use functools.partial to pass default params.
        # Note: Partial params should storage in a seperate module.
        temp_ability = functools.partial(
            ability,
            direct=-1,
            speed=18,
            dmg=22,
            shooter=self.sprite,
            image=abilities.default_bullet()
            )
        self.action_dict.update(
            {key: temp_ability}
            )
        return

    def attack(self, keypress):
        '''Define attack.'''
        raise NotImplementedError
        # Psuedo code:
        # Check if sprite is 'ready to fire'.
        # Call abilities.Linear create bullet.
        b_shift = lambda: random.randint(-2, 2)
        x, y = self.sprite.rect.midtop
        y -= 8
        for key, ability in self.action_dict.items():
            if keypress[key]:
                self.bullet_group.add(
                    ability(
                        init_x=x+b_shift(),
                        init_y=y
                        )
                    )
                # Psuedo code:
                # self.sprite.next_fire = now + ability.cooldown
                break
        return

    def move(self, keypress):
        '''Define move.'''
        raise NotImplementedError
        rect = self.sprite.rect
        if keypress[pygame.K_w] and rect.top > screen_rect.top:
            rect.move_ip(0, -self.move_y_rate)
        if keypress[pygame.K_s] and rect.bottom < screen_rect.bottom:
            rect.move_ip(0, self.move_y_rate)
        if keypress[pygame.K_a] and rect.left > screen_rect.left:
            rect.move_ip(-self.move_x_rate, 0)
        if keypress[pygame.K_d] and rect.right < screen_rect.right:
            rect.move_ip(self.move_x_rate, 0)
        return

    def foo(self):
        '''bar.'''
        raise NotImplementedError
