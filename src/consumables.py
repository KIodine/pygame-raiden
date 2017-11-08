try:
    import pygame
    import random
    import config as cfg
except:
    raise

class Consumables(pygame.sprite.Sprite):

    def __init__(self, W_WIDTH):
        super(Consumables, self).__init__()
        
        size_list = [
            ['S', (7, 7)], ['M', (10, 10)], ['L', (14, 14)]
            ]
        score_dict = {
            'S': 1, 'M': 3, 'L': 7
            }
        
        size, vol = random.choice(size_list)
        self.image = pygame.Surface(vol)
        self.image.fill(cfg.color.white)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(0 + 15, W_WIDTH - 15), 15)
        self.score = score_dict[size]
        self.speed = 9
        self.direction = [random.choice((1, -1)), 1] # x, y direction
        self.lifetime = pygame.time.get_ticks() + 10 * 1000 # 10 seconds
    
    def update(self, screct):
        if self.rect.top < screct.top or self.rect.bottom > screct.bottom:
            self.direction[1] *= -1 # Switch direction
        if self.rect.left < screct.left or self.rect.right > screct.right:
            self.direction[0] *= -1
        self.rect.centerx += self.direction[0] * self.speed
        self.rect.centery += self.direction[1] * self.speed

        if self.lifetime - pygame.time.get_ticks() < 700:
            self.image.fill((255, 0, 0))
# End of 'Consumables'.