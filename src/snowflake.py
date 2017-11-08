try:
    import pygame
    import random
except:
    raise

class SnowFlake(pygame.sprite.Sprite):

    def __init__(self, rdsize, rdgray, rdspeed, shftspeed, W_HEIGHT,W_WIDTH):
        super(SnowFlake, self).__init__()
        self.image = pygame.Surface(*rdsize())
        self.image.fill(rdgray())
        self.rect = self.image.get_rect()
        self.rdspeed = rdspeed
        self.shftspeed = shftspeed
        self.drop_rate = self.rdspeed()
        self.shft_rate = shftspeed()
        self.W_HEIGHT = W_HEIGHT
        self.W_WIDTH = W_WIDTH
    def update(self):
        self.rect.centery += self.drop_rate
        if self.rect.centery >= self.W_HEIGHT:
            # Boundary action.
            # Reset position when going outside of screen.
            self.rect.centerx = random.randrange(0, self.W_WIDTH)
            self.rect.centery = random.randrange(-20, -5)
            # Outside of upper limit.
            self.drop_rate = self.rdspeed()
            self.shft_rate = self.shftspeed()
# End of 'SnowFlake'.