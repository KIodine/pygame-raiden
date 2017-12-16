import functools
from enum import Enum

import pygame

import animation
import abilities
import resource

# WARNING=============================================================
# This module is still progressing,
# ====================================================================

# Note.---------------------------------------------------------------
'''
    1.Reconstruct 'Character' and 'Mob', add interface between handle and them.
'''
# Note.---------------------------------------------------------------

class SID(Enum):
    """Skill identifier."""
    RAILGUN = 0
    LASER = 1

class CampID(Enum):
    """CampID identifier."""
    PLAYER = 0
    ENEMY = 1
    NEUTRAL = 2

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

def CIDfilter(group, CID):
    '''Return sprites that match the assigned CID.'''
    f = lambda sprite: True if sprite.camp == CID else False
    filtered = [
        sprite for sprite in filter(f, group)
    ]
    return filtered

# Character.----------------------------------------------------------

class PlayerInterface():

    def __init__(
            self,
            *,
            sprite=None,

            skills=None,
            animation_handler=None
        ):
        raise NotImplementedError
        self.sprite = sprite
        self.skills = skills
        self.animation_handler = animation_handler

    def keyact(self, keypress):
        self.sprite.move(keypress)
        self.skills.cast(keypress)


class Skills():

    def __init__(
            self,
            *,
            sprite=None,
            skill_list=None,
            projectile_handler=None,
            group=None # sprite_group
        ):
        raise NotImplementedError
        self.sprite = sprite
        self.skill_list = skill_list
        self.projectile_handler = projectile_handler
        self.camp = sprite.camp
        self.group = group
    
    def cast(self, keypress):
        if keypress[pygame.K_j]:
            self.projectile_handler.create_basic()
        elif keypress[pygame.K_k]:
            self.skill_list[SID.RAILGUN]()
        elif keypress[pygame.K_u]:
            self.skill_list[SID.LASER]()

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
            hostile_camp=None,
            skill=None
        ):
        self.sprite = sprite
        self.skill = None
        self.hostile_camp = hostile_camp

    def keyevents(self, keypress):
        self.sprite.move(keypress)
        self.skill.keyevents(keypress)


'''