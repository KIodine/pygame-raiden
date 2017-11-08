try:
    import pygame
except:
    raise

class Explode(pygame.sprite.Sprite):

    def __init__(self, cx, cy, image):
        super(Explode, self).__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (cx, cy)
        self.spawntime = pygame.time.get_ticks()
        self.lifetime = 0.07 * 1000

    def update(self):
        pass
# End of 'Explode'.