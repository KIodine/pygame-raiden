import os
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


class Core():
    '''
Takes 'img_struct', resolve into frame list.
Cannot use independent, must initialize explictly.
'''
    fps = 24
    played = False
    def __init__(
            self,
            *,
            image_struct=None,
        ):
        # Progessing: take 'img_struct' and resolve.
        # Unpack data.
        self.image_struct = image_struct
        image, w, h, col, row = image_struct

        if image is None:
            self.image = pygame.Surface((w, h), pygame.SRCALPHA)
            self.rect = self.image.get_rect()
            self.image.fill((0, 0, 0, 0))
            pygame.draw.rect(self.image, (0, 255, 0, 255), (0, 0, w, h), 1)
            self.index = None
        elif isinstance(image, pygame.Surface):
            self.index = 0
            self.animation_list = []
            self.master_image = image
            for i in range(row):
                for j in range(col):
                    self.animation_list.append(
                        [j*w, i*h, w, h]
                        )
            self.rect = pygame.rect.Rect(0, 0, w, h)
            # Set a smaller collide rect for better player experience?
            ani_rect = self.animation_list[self.index]
            self.ani_len = len(self.animation_list)
            self.image = self.master_image.subsurface(ani_rect)
        else:
            raise TypeError(
                f"Expecting 'image_struct' type, got {image}."
                )

    def to_next_frame(self, current_time):
        if self.index is not None:
            elapsed_time = current_time - self.last_draw
            if elapsed_time > self.fps**-1 * 1000:
                self.index += 1
                ani_rect = self.animation_list[self.index%self.ani_len]
                self.image = self.master_image.subsurface(ani_rect)
                self.last_draw = current_time
            if not self.played:
                if self.index >= (self.ani_len - 1):
                    self.played = True
        raise NotImplementedError
