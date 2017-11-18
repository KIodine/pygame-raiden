import random
import math

import pygame

# Animation resolver.

class Animation_core():
    '''Resolve single picture to animation list.'''
    def __init__(self,
                 *,
                 image=None,
                 w=70,
                 h=70,
                 col=1,
                 row=1
                 ):
        
        if image is None:
            self.image = pygame.Surface((w, h), pygame.SRCALPHA)
            self.rect = self.image.get_rect()
            self.image.fill((0, 0, 0, 0))
            pygame.draw.rect(self.image, (0, 255, 0, 255), (0, 0, w, h), 1)
            self.index = None
        else:
            self.index = 0
            self.animation_list = []
            self.master_image = image
            for i in range(col):
                for j in range(row):
                    self.animation_list.append(
                        [i*w, j*h, w, h]
                        )
            self.rect = pygame.rect.Rect(0, 0, w, h)
            # Set a smaller collide rect for better player experience?
            ani_rect = self.animation_list[self.index]
            self.ani_len = len(self.animation_list)
            self.image = self.master_image.subsurface(ani_rect)
