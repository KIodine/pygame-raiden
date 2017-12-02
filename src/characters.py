import functools

import pygame

import animation
import abilities

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

#---------------------------------------------------------------------

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
        pass

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
        return

    def charge(self, val=0):
        '''Charge resource with 'val'.'''
        if self.ratio < 1:
            self.current_val += val
            self._over_charge_check()
            pass
        return

    @property
    def ratio(self):
        c_val = self.current_val
        if c_val < 0: c_val = 0
        return c_val/self.max_val

    def _to_zero(self):
        '''Reduce resource to zero.'''
        self.current_val = 0
        return

    def _to_max(self):
        '''Charge resource to its maximum value.'''
        self.current_val = self.max_val
        return

    def _over_charge_check(self):
        '''If current_val exceeds max_val, set it to max_val.'''
        if self.current_val > self.max_val:
            self.current_val = self.max_val
        return

# Character.----------------------------------------------------------
class Character(pygame.sprite.Sprite):
    '''Create player.'''
    def __init__(self,
                 *,
                 init_x=0,
                 init_y=0,
                 image=None
                 ):
        
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
            charge_val=7.5,
            charge_speed=0.06,
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
        # Maybe fire_rate should tranfer to ability itself.
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

    def update(self, current_time):
        # Is there a way to seperate?
        if self.index is not None:
            elapsed_time = current_time - self.last_draw
            if elapsed_time > self.fps**-1 * 1000:
                self.index += 1
                ani_rect = self.animation_list[self.index%self.ani_len]
                self.image = self.master_image.subsurface(ani_rect)
                self.last_draw = current_time
        # Seperate frame refresh logic to animation.Core

        for res in self._resource_list:
            res.recover(current_time)


# Interface for indirect control.-------------------------------------

class Interface():
    '''Progressing'''
    def __init__(self,
                 *,
                 sprite,
                 bullet_group
                 ):
        '''Should take sprite.'''
        raise NotImplementedError
        self.sprite = sprite
        self.bullet_group = bullet_group
        self.action_dict = dict()
        
    def set_action(self,
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


# Mob.----------------------------------------------------------------

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
            charge_val=1, # if charge_val is zero, will not recover over time.
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
        pass


class MobHandle():

    def __init__(self,
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
            image=ufo
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
                pass
            pass
        return

    def _attack_random(self, chance):
        '''Attack with n percent of chance.'''
        for hostile in self.group:
            if dice(chance):
                hostile.attack(hostile_projectile_group)
                # Play shooting sound here.
