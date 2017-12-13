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
