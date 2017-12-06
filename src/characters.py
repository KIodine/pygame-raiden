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
