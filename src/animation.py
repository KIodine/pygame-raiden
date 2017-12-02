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
    image: pygame.Surface=None,
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


class Core():
    '''
Takes 'img_struct', resolve into frame list.
Cannot use independent, must initialize explictly.
'''
    fps = 24
    played = False
    def __init__(self,
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
