import math
from functools import wraps

import pygame

from resource import ResID
from characters import CIDfilter

# Resource indicators, including:
#   (1) HP
#   (2) CHARGE
#   (3) ULT

# ------------------------------------------------------------------ #
# NOTE: All angles in this module uses 'radians' as unit!----------- #
# EXCEPT: 'arrow_to'(Due to some coordinate issue)------------------ #
# ------------------------------------------------------------------ #

# TODO:
#   (1) Apply 'default_keyword' decorator to functions had **kw.

Vector2 = pygame.math.Vector2

_DEFAULT_EXPAND = {
    'radius': 100,
    'rim_color': (0, 255, 0),
    'ind_color': (255, 0, 0),
    'base_angle': math.radians(270),
    'expand_angle': math.radians(60),
    'rim_width': 3,
    'ind_width': 2,
    'c_index_color': (175, 175, 175),
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

_DEFAULT_ARROW = {
    'color': (255, 255, 0),
    'expand': 10, # Degree.
    'length': 20,
    'pass': None,
}

_DEFAULT_SIGHT = {
    'pass': None
}

def default_keyword(default_kw):
    '''Set the default keyword dict to the decorated function.'''
    def func_catcher(func):
        @wraps(func)
        def wrapper(*args, **kw):
            '''Modify kwargs then put back.'''
            for k, v in default_kw.items():
                # Add check a key is available in default keyword or not.
                if k not in kw:
                    kw[k] = v
            return func(*args, **kw)
        return wrapper
    return func_catcher

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

def arrow_to(
        surface,
        point,
        angle: 'degree',
        distance,
        **kw
    ):
    '''Draw an isosceles triangle by determine its point, top, angle, and side.'''
    for k, v in _DEFAULT_ARROW.items():
        if k not in kw:
            kw[k] = v
    angle = 360 - angle
    vertices = list()
    point = Vector2(point)
    top = Vector2()
    top.from_polar((distance, angle))
    # The pygame surface coord is upside down.
    pin_point = point + top
    vertices.append(pin_point)
    vertex_cw = Vector2()
    vertex_cw.from_polar(
        (kw['length'], angle-kw['expand'])
        )
    vertices.append(pin_point+vertex_cw)
    vertex_ccw = Vector2()
    vertex_ccw.from_polar(
        (kw['length'], angle+kw['expand'])
    )
    vertices.append(pin_point+vertex_ccw)
    pygame.draw.polygon(
        surface,
        kw['color'],
        vertices,
        0 # Fill.
    )
    return

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
    ratio = sprite.attrs[res_id].ratio
    if ratio == ResID.INVALID:
        ratio = 1
    expand_angle = kw['expand_angle'] * ratio
    clockwise_border = kw['base_angle'] - expand_angle
    countercw_border = kw['base_angle'] + expand_angle + math.radians(5) * ratio
    # Add 5 degrees for correction.
    pygame.draw.arc(
        surface,
        kw['rim_color'],
        frame,
        clockwise_border,
        countercw_border,
        kw['rim_width']
    )
    # The left poing and right point is not horizontal?------------- #
    if sprite.attrs[res_id].ratio == 1:
        pass
    else:
        kw['ind_color'] = (200, 0, 0)
    # -------------------------------------------------------------- #
    cw_max_angle = kw['base_angle'] - kw['expand_angle']
    ccw_max_angle = kw['base_angle'] + kw['expand_angle'] + math.radians(5)
    # Add 5 degrees for correction.
    cw_st, cw_ed = centered_pol2rect(
        framex, framey,
        L/2 - kw['rim_width'],
        L/2 + kw['rim_width'],
        cw_max_angle - kw['gap']
    )
    ccw_st, ccw_ed = centered_pol2rect(
        framex, framey,
        L/2 - kw['rim_width'],
        L/2 + kw['rim_width'],
        ccw_max_angle + kw['gap']
    )
    baseline_st, baseline_ed = centered_pol2rect(
        framex, framey,
        L/2 - 1.7*kw['rim_width'],
        L/2 + 1.7*kw['rim_width'],
        kw['base_angle']
    )
    # The center index line.
    pygame.draw.line(
        surface, kw['c_index_color'],
        baseline_st, baseline_ed,
        kw['ind_width']
    )
    for start, end in ((cw_st, cw_ed), (ccw_st, ccw_ed)):
        pygame.draw.line(
            surface, kw['ind_color'],
            start, end,
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

def sight_index(
        sprite,
        group,
        target_camp,
        surface,
        **kw
    ):
    '''Indicate the nearest enemy on the virtual ballistic.'''
    '''
        If there is enemy on the line, draw indication image on
        the bottom of the nearest enemy.
        If not, no drawing is applied.
    '''
    # Let this function takes the pattern, decides the pattern by 'partial'?
    selected = [sprite for sprite in CIDfilter(group, target_camp)]
    if not selected:
        return
    f = lambda other: abs(other.rect.bottom - sprite.rect.top)
    hitbox = pygame.Rect(
        (0, 0), 
        (3, sprite.rect.top)
    )
    hitbox.midbottom = sprite.rect.midtop
    collided = list()
    for select in selected:
        if hitbox.colliderect(select.rect.inflate(30, 30)):
            # Use 'inflate' method to make it more sensitive.
            collided.append(select)
    if not collided:
        x, y = sprite.rect.midtop
        y -= 30
        color = (0, 200, 0)
    else:
        collided.sort(key=f)
        x, y = sprite.rect.centerx, collided[0].rect.bottom
        color = (255, 15, 0)
    # Draw pattern ------------------------------------------------- #
    # This is replacable.
    arrow_to(
        surface,
        (x, y),
        270,
        5,
        color=color
    )
    # -------------------------------------------------------------- #
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
