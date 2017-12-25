import random
import math
import sys
from collections import deque
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

if __name__ == '__main__':
    pygame.init()
    pygame.display.init()
    pygame.display.set_caption("PARTICLES")
    screen = pygame.display.set_mode(
        (WIDTH, HEIGHT)
        )
    screen_rect = screen.get_rect()

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
            g=0
        ):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.surface.Surface((2, 2))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect()
        # Adjusting.
        self.lifespan = (random.random()*0.9) * 1000 # 2s default.

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

        color = int(255 * self.lifespan / self.max_dura)
        if color <= 0: color = 0
        self.image.fill((color, color, 0))
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
        group=mess
    ):
    part = Particle(
        init_s=s,
        init_v=v,
        drag=drag,
        g=g
    )
    group.add(part)
    return None

def spawn_uniform(
        s,
        v,
        n,
        drag,
        g,
        group=mess
    ):
    s = Vector2(s)
    for _ in range(n):
        v = Vector2(0, 0)
        # Method to spawn.
        r = random.normalvariate(0.25, 0.09) * 150 + 200
        phi = random.random() * 360
        # Method to spawn.
        v.from_polar((r, phi))
        spawn_single(
            s,
            v,
            drag,
            g,
            group
        )
    return None

def spawn_normalvar(
        s,
        v,
        n,
        drag,
        g,
        group=mess
    ):
    s = Vector2(s)
    for _ in range(n):
        v = Vector2(0, 0)
        # Method to spawn.
        r = random.normalvariate(0.25, 0.09) * 150 + 200
        phi = random.normalvariate(-90, 15)
        # Method to spawn.
        v.from_polar((r, phi))
        spawn_single(
            s,
            v,
            drag,
            g,
            group
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
                PPT,
                1.1,
                120,
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
