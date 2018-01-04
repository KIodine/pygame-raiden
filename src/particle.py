import random
import math
import sys
from collections import deque
from functools import wraps
from operator import iadd, isub

import pygame

Vector2 = pygame.math.Vector2

WIDTH, HEIGHT = 1000, 680
FPS = 60
PPT = 15
GENERATED = 0
M_AMOUNT = 0
RUNNING = True
COUNTDOWN = 0
READY_TO_ACT = True
mess = pygame.sprite.Group()
pygame.init()
CLOCK = pygame.time.Clock()

'''NOTE:
    (1) Improve customability.
'''
# Kwargs checking.
def set_default_kw(default_kw):
    '''Decorator.'''
    def f_catcher(func):
        @wraps(func)
        def wrapper(*args, **kw):
            if any(k not in default_kw for k in kw.keys()):
                diff = set(kw.keys()) - set(default_kw.keys())
                raise KeyError(
                    "The following key(s) is not exist: "
                    "{k}".format(k=', '.join(diff))
                    )
            default_kw.update(kw)
            kw = default_kw
            return func(*args, **kw)
        return wrapper
    return f_catcher

# The default keyword parameter.
_UNIFORM = {
    'n': 15,
    'drag': 1.1,
    'g': 0,
    'group': mess,
    'color': (240, 200, 0),
    'r_mu': 0.25,
    'r_sigma': 0.09,
    'r_rate': 150,
    'r_base': 200
}

_NORMALVAR = {
    'n': 5,
    'drag': 0.3,
    'g': 0,
    'group': mess,
    'color': (240, 200, 0),
    'r_mu': 0.25,
    'r_sigma': 0.09,
    'r_rate': 150,
    'r_base': 200,
    'phi_mu': -90,
    'phi_sigma': 15
}

if __name__ == '__main__':
    pygame.init()
    pygame.display.init()
    pygame.display.set_caption("PARTICLES")
    screen = pygame.display.set_mode(
        (WIDTH, HEIGHT)
        )
    screen_rect = screen.get_rect()

# Add a 'color' option?
# Or add alpha channel.
class Particle(pygame.sprite.Sprite):
    # If an attr is defined outside (the raw space), any modification
    # in any instance will change the 'template' one.
    # Wierd.
    def __init__(
            self,
            *,
            init_s=None,
            init_v=None,
            init_a=None,
            drag=0,
            g=0,
            color=(195, 195, 0),
            base_life=0.9,
        ):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.surface.Surface(
            (2, 2), pygame.SRCALPHA, 32
            )
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect()
        # Adjusting.
        self.lifespan = (random.random()*base_life) * 1000 # 2s default.
        self.color = color

        self.max_dura = self.lifespan
        self.dead = False

        self.s = Vector2(0, 0)
        self.v = Vector2(0, 0)
        self.a = Vector2(0, 0)
        self.s += init_s if init_s else (0, 0)
        self.v += init_v if init_v else (0, 0)
        self.a += init_a if init_a else (0, 0)
        self.k = -drag
        self.g = Vector2(0, g)
        self.rect.center = self.s

    def update(self, h=None):
        if self.lifespan <= 0:
            self.dead = True
            return
        if not h:
            h = CLOCK.get_time()
        self.lifespan -= h
        h /= 1000
        self.v += (self.a + self.k * self.v + self.g) * h
        self.s += self.v * h

        self.rect.center = self.s

        alpha = int(255 * self.lifespan / self.max_dura)
        if alpha <= 0:
            alpha = 0
        self.image.fill((*self.color, alpha))
        return

def get_random_particle():
    pos = pygame.mouse.get_pos()
    rel = Vector2(pygame.mouse.get_rel())

    r = random.normalvariate(0.25, 0.09) * 150 + 200
    # Uniform spread.
    phi = random.random() * (2 * math.pi)

    # Determine the initial angle.
    phi = random.normalvariate(
        math.radians(-90), math.radians(25)
        )
    vx, vy = r * math.cos(phi), r * math.sin(phi)
    v = Vector2(vx, vy)
    drag = 1.1
    p = Particle(
        init_s=pos,
        init_v=v,
        drag=drag,
        g=120
    )
    return p

def spawn_single(
        s,
        v,
        drag,
        g,
        group=mess,
        color=(210, 210, 0)
    ):
    part = Particle(
        init_s=s,
        init_v=v,
        drag=drag,
        g=g,
        color=color
    )
    group.add(part)
    return None

# Set 'drag', 'g', 'group' as kwargs.
@set_default_kw(_UNIFORM)
def spawn_uniform(
        s,
        v,
        **kw
    ):
    s = Vector2(s)
    for _ in range(kw['n']):
        v = Vector2(v)
        # Method to spawn.
        r = random.normalvariate(
            kw['r_mu'], 
            kw['r_sigma']
            ) * kw['r_rate'] + kw['r_base']
        phi = random.random() * 360
        # Method to spawn.
        v.from_polar((r, phi))
        spawn_single(
            s,
            v,
            kw['drag'],
            kw['g'],
            kw['group'],
            kw['color']
        )
    return None

# Set 'drag', 'g', 'group' as kwargs.
@set_default_kw(_NORMALVAR)
def spawn_normalvar(
        s,
        v,
        **kw
    ):
    s = Vector2(s)
    for _ in range(kw['n']):
        v = Vector2(0, 0)
        # Method to spawn.
        r = random.normalvariate(
            kw['r_mu'],
            kw['r_sigma']) * kw['r_rate'] + kw['r_base']
        phi = random.normalvariate(kw['phi_mu'], kw['phi_sigma'])
        # Method to spawn.
        v.from_polar((r, phi))
        spawn_single(
            s,
            v,
            kw['drag'],
            kw['g'],
            kw['group'],
            kw['color']
        )
    return None

def expel_particles(
        radius=200,
        mode='expel'
    ):
    global COUNTDOWN
    global READY_TO_ACT
    if not READY_TO_ACT:
        return
    center = Vector2(pygame.mouse.get_pos())
    radius = radius
    READY_TO_ACT = not READY_TO_ACT
    COUNTDOWN += 0.3 * 1000
    for part in mess:
        distance = part.s.distance_to(center)
        if distance < radius:
            if mode == 'expel':
                isub(
                    part.v,
                    (center - part.s) * (1 - (distance / radius)) * 10
                )
            if mode == 'attract':
                iadd(
                    part.v,
                    (center - part.s) * (1 - (distance / radius)) * 10
                )
    return

def keyact(key):
    global RUNNING
    if key == pygame.K_ESCAPE:
        RUNNING = False
    return

def mouseact(pressed):
    # Progressing.
    global GENERATED
    L, M, R = pressed
    if L:
        pass
    if M:
        expel_particles(mode='attract')
    if R:
        expel_particles(mode='expel')
    return

# Test block.
if __name__ == '__main__':
    while RUNNING:
        CLOCK.tick(FPS)
        screen.fill((0, 0, 0))
        events = pygame.event.get()
        for event in events:
            etype = event.type
            if etype == pygame.QUIT:
                RUNNING = False
            elif etype == pygame.KEYDOWN:
                keyact(event.key)
            elif etype == pygame.MOUSEBUTTONDOWN:
                pressed = pygame.mouse.get_pressed()
                mouseact(pressed)

        pressed = pygame.mouse.get_pressed()
        L, _, _ = pressed
        if L:
            # for i in range(PPT):
                # GENERATED += 1
                # mess.add(get_random_particle())
            spawn_normalvar(
                pygame.mouse.get_pos(),
                (0, 0),
                n=PPT,
                drag=1.1,
                g=120,
                group=mess
            )

        for particle in mess:
            if not (0 < particle.rect.centerx < screen_rect.w)\
            or particle.rect.centery > screen_rect.h:
                mess.remove(particle)
            if particle.dead:
                mess.remove(particle)

        mess.update()
        mess.draw(screen)

        if not READY_TO_ACT:
            COUNTDOWN -= CLOCK.get_time()
            if COUNTDOWN <= 0:
                READY_TO_ACT = True
        ...
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)
