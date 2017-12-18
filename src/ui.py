import math

import pygame

from resource import ResID

# Resource indicators, including:
#   (1) HP
#   (2) CHARGE
#   (3) ULT

# ------------------------------------------------------------------ #
# NOTE: All angles in this module uses 'radians' as unit!----------- #
# ------------------------------------------------------------------ #

_DEFAULT_EXPAND = {
    'radius': 100,
    'rim_color': (0, 255, 0),
    'ind_color': (255, 0, 0),
    'base_angle': math.radians(270),
    'expand_angle': math.radians(60),
    'rim_width': 3,
    'ind_width': 2,
    'gap': math.radians(5) # The diff of angle between arc and index.
}

_DEFAULT_FULL = {
    'radius': 150,
    'rim_color': (0, 255, 0),
    'ind_color': (255, 0, 0),
    'base_angle': math.radians(0),
    'rim_width': 5,
    'ind_width': 1,
    'gap': 5 # the radius diff between inner and outer rim.
}

_DEFAULT_BAR = {
    'width': 100,
    'height': 6,
    'shift': 10,
    'color': (0, 255, 0)
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

def centered_pol2rect(
        cx,
        cy,
        init_r,
        end_r,
        phi
    ):
    st_x, st_y = pol2rect(init_r, phi)
    st_x = cx + st_x
    st_y = cy - st_y

    ed_x, ed_y = pol2rect(end_r, phi)
    ed_x = cx + ed_x
    ed_y = cy - ed_y

    return (st_x, st_y), (ed_x, ed_y)

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
    countercw_border = kw['base_angle'] + expand_angle + math.radians(5)
    # The pygame.draw.arc 
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
        pass
    else:
        kw['ind_color'] = (200, 0, 0)
    # -------------------------------------------------------------- #
    cw_st, cw_ed = centered_pol2rect(
        framex, framey,
        L/2 - kw['rim_width'],
        L/2 + kw['rim_width'],
        clockwise_border - kw['gap']
    )
    ccw_st, ccw_ed = centered_pol2rect(
        framex, framey,
        L/2 - kw['rim_width'],
        L/2 + kw['rim_width'],
        countercw_border + kw['gap']
    )
    for start, end in ((cw_st, cw_ed), (ccw_st, ccw_ed)):
        pygame.draw.line(
            surface, kw['ind_color'],
            start,
            end,
            kw['ind_width']
        )
    # -------------------------------------------------------------- #
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

def expand_bar(
        sprite,
        res_id,
        surface,
        **kw
    ):
    '''Draw expanding bar that hovers on the top of sprite.'''
    for k, v in _DEFAULT_BAR.items():
        if k not in kw:
            kw[k] = v
    ratio = int(sprite.attrs[res_id].ratio * 100)
    bar_x, bar_y = sprite.rect.center
    bar = pygame.rect.Rect(
        0, 0, ratio, kw['width']
    )
    bar.center = bar_x, (bar_y - kw['shift'])
    pygame.draw.rect(
        surface,
        kw['color'],
        bar,
        0 # fill.
    )
    return

'''
    Note:
        A class holds all ui drawing?

class Holder():
    ui_list = list()

    def __init__(
            self,
            *,
            sprite, # or group, CID
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
