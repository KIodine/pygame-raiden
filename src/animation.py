import os
import random
from collections import namedtuple

import pygame

img_struct = namedtuple(
    'Animation',
    [
        'image',
        'w',
        'h',
        'col',
        'row'
        ]
    )

def loader(
        image=None,
        w=70,
        h=70,
        col=1,
        row=1
    ) -> img_struct:
    '''\
Resolve and pack necessary info into 'img_struct' container.\
'''
    # 'isinstance' can test both native and custom classes.
    if image is not None:
        if isinstance(image, pygame.Surface):
            pass
        elif os.path.exists(image):
            # if it's not 'pygame.Surface', but a available path then:
            image = pygame.image.load(image).convert_alpha()
        else:
            raise TypeError(f"Cannot resolve {image}")
    struct = img_struct(
        image=image,
        w=w,
        h=h,
        col=col,
        row=row
        )
    return struct

def sequential_loader(
        image=None,
        *,
        init_x=0,
        init_y=0,
        w=50,
        h=50,
        col=1,
        row=1
    ) -> tuple:
    '''Takes Surface object, return master_image and resolved tuple of image.'''
    # Resolve logics is the same as 'Core'.
    # Return master_image and subsurfaces tuple.
    if image is None:
         # Draw a green frame and return.
        surf = pygame.Surface(
            (w, h),
            pygame.SRCALPHA,
            32
        )
        pygame.draw.rect(
            surf,
            (0, 255, 0),
            (0, 0, w, h),
            1
        )
        return image, tuple([surf])
    elif isinstance(image, pygame.Surface):
        pass
    elif os.path.exists(image) and os.path.isfile(image):
        image = pygame.image.load(image).convert_alpha()
    master_image = image
    animation_list = []
    for i in range(row):
        for j in range(col):
            frame = pygame.Rect(
                (init_x + (j * w), init_y + (i * h)),
                (w, h)
                )
            animation_list.append(
                master_image.subsurface(frame)
                )
    return master_image, tuple(animation_list)

class NewCore():
    '''New animation player, takes result from 'sequential loader'.'''
    fps = 24
    def __init__(
            self,
            *,
            master=None,
            frames=None
        ):
        # pygame.Surface.subsurface returns a surface reference to its parent,
        # so aborting the parent could cause unexpected error.
        # Keep it in the instance may help.
        self.master = master
        self.frames = frames
        self.frame_length = len(frames)
        self.index = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.last_draw = pygame.time.get_ticks()

    def to_next_frame(self, current_time):
        """Push frame to its next if elapsed time exceeds frame interval."""
        elapsed_time = current_time - self.last_draw
        if elapsed_time > self.fps**-1 * 1000:
            # If elapsed time greater than the reciprocal of frame rate,
            # add index inplace.
            self.index += 1
            self.image = self.frames[self.index % self.frame_length]
            self.last_draw = current_time
        return

    @property
    def played(self):
        """Return how many times the animation played."""
        frame_length = self.frame_length
        if frame_length == 1:
            # If it is a single-frame image, let it stay at least one frame.
            frame_length += 1
        count = self.index // (frame_length - 1)
        return count


class AnimatedObject(
        pygame.sprite.Sprite,
        NewCore
    ):
    '''Building pure effect with image.'''
    def __init__(
            self,
            *,
            init_x=0,
            init_y=0,
            image=None,
            fps=None
        ):
        master, frames = image
        pygame.sprite.Sprite.__init__(self)
        NewCore.__init__(
            self,
            master=master,
            frames=frames
            )

        self.rect.center = init_x, init_y
        if fps:
            self.fps = fps
        self.last_draw = pygame.time.get_ticks()

    def update(self, current_time):
        self.to_next_frame(current_time)
        return


class AnimationHandle():
    '''Handle effects.'''
    def __init__(
            self,
            *,
            group=None,
            surface=None
        ):
        if group is None:
            raise ValueError("No group is referenced.")
        if surface is None:
            raise ValueError("No surface is referenced.")
        self.group = group
        self.surface = surface
        self.draw_queue = list()
        self.draw_multi_delay = 0.1 * 1000
        self.last_draw_multi = pygame.time.get_ticks()
        self.timestamped = namedtuple(
            'Stamped_Frame',
            [
                'timestamp',
                'frame'
                ]
            )

    def draw_single(
            self,
            *,
            x=0,
            y=0,
            image=None,
            fps=None
        ):
        eff = AnimatedObject(
            init_x=x,
            init_y=y,
            image=image,
            fps=fps
            )
        self.group.add(eff)
        return

    def draw_multi_effects(
            self,
            *,
            x=0,
            y=0,
            diff=16,
            num=5,
            interval=0.08,
            image=None,
            fps=None
        ):
        if image is None:
            return
        now = pygame.time.get_ticks()
        diff_pos = lambda: random.randint(-diff, diff)
        self.draw_multi_delay = interval * 1000
        for i in range(num):
            eff = AnimatedObject(
                init_x=x+diff_pos(),
                init_y=y+diff_pos(),
                image=image,
                fps=fps
                )
            pair = self.timestamped(
                now + interval * 1000 * i, eff
                )
            self.draw_queue.append(pair)
            # Sort draw order when inserting new effects.
        self.draw_queue.sort(
            key=lambda x: x.timestamp
            )
        return

    def refresh(self):
        now = pygame.time.get_ticks()
        for ani in self.group:
            # Clean animations that had played once.
            if ani.played >= 1:
                self.group.remove(ani)
        if len(self.draw_queue) != 0:
            # Maybe not a good style?
            if self.draw_queue[0].timestamp < now:
                self.group.add(self.draw_queue.pop(0).frame)
        # ------------------------------
        self.group.update(now)
        self.group.draw(self.surface)
        # ------------------------------
        return