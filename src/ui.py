import math

import pygame

from resource import ResID

# Resource indicators, including:
#   (1) HP
#   (2) CHARGE
#   (3) ULT


_DEFAULT_EXPAND = {
    'radius': 100,
    'rim_color': (0, 255, 0),
    'ind_color': (255, 0, 0),
    'base_angle': math.radians(270),
    'expand_angle': math.radians(60),
    'rim_width': 3,
    'ind_width': 2,
    'gap': math.radians(5)
}

_DEFAULT_FULL = {
    'radius': 150,
    'rim_color': (0, 255, 0),
    'ind_color': (255, 0, 0),
    'base_angle': math.radians(0),
    'rim_width': 5,
    'ind_width': 1,
    'gap': 5
}

def pol2rect(r, phi):
    '''Convert polar to rectangle.'''
    x = r * math.cos(phi)
    y = r * math.sin(phi)
    return x, y

def rect2pol(x, y):
    '''Convert rectangle to polar.'''
    r = math.hypot(x, y)
    phi = math.atan2(y, x)
    return r, phi

def expand_arc(
        sprite,
        res_id,
        surface,
        **kw
    ):
    '''Draw expandable arc as resource instruction.'''
    for k, v in _DEFAULT_EXPAND.items():
        # If a kwarg is not assigned, a value in default setting will take
        # its place.
        if k not in kw:
            kw[k] = v
    base_rect = sprite.rect
    L = kw['radius']
    frame = pygame.Rect(0, 0, L, L)
    frame.center = base_rect.center
    framex, framey = frame.center
    ratio = sprite.attrs[res_id]
    if ratio == ResID.INVALID:
        ratio = 1
    expand_angle = kw['expand_angle'] * sprite.attrs[res_id].ratio
    clockwise_border = kw['base_angle'] - expand_angle
    countercw_border = kw['base_angle'] + expand_angle
    pygame.draw.arc(
        surface,
        kw['rim_color'],
        frame,
        clockwise_border,
        countercw_border,
        kw['rim_width']
    )
    # The left poing and right point is not horizontal?
    if sprite.attrs[res_id].ratio == 1:
        sposx, sposy = pol2rect(
            L/2 - kw['rim_width'],
            clockwise_border - kw['gap']
        )
        eposx, eposy = pol2rect(
            L/2 + kw['rim_width'],
            clockwise_border - kw['gap']
        )
        pygame.draw.line(
            surface,
            kw['ind_color'],
            (framex + int(sposx), framey - int(sposy)),
            (framex + int(eposx), framey - int(eposy)),
            kw['ind_width']
        )
        pygame.draw.line(
            surface,
            kw['ind_color'],
            (framex - int(sposx), framey - int(sposy)),
            (framex - int(eposx), framey - int(eposy))
        )
    return None

def full_rim(
        sprite,
        res_id,
        surface,
        **kw
    ):
    '''Draw full circle as resource instructor.'''
    for k, v in _DEFAULT_FULL.items():
        # If a kwarg is not assigned, a value in default setting will take
        # its place.
        if k not in kw:
            kw[k] = v
    base_rect = sprite.rect
    L = kw['radius']
    base = kw['base_angle']
    frame = pygame.Rect(0, 0, L, L)
    frame.center = base_rect.center
    ratio = sprite.attrs[res_id].ratio
    if ratio == ResID.INVALID:
        ratio = 1
    arc_end = (2 * math.pi) * ratio + base
    pygame.draw.arc(
        surface,
        kw['rim_color'],
        frame,
        base,
        arc_end,
        kw['rim_width']
    )
    if ratio == 1:
        # Outer rim indicates resource is full.
        pygame.draw.circle(
            surface,
            kw['ind_color'],
            frame.center,
            int(frame.width/2 + kw['gap']),
            2
            )
    return None

def expand_bar():
    '''Draw expanding bar that hovers on the top of sprite.'''
    raise NotImplementedError

'''
    Note:
        A class holds all ui drawing?

class Holder():
    ui_list = list()

    def __init__(
            self,
            *,
            sprite,
            surface
        ):
        self.sprite = sprite
        self.surface = surface

    def set_ui(
            self,
            func,
            res_id,
            **kw
        ):
        ui_list.append(
            partial(func, res_id, **kw) # Correct?
        )

    def draw():
        for gear in self.ui_list:
            gear()

'''
