try:
    import pygame
except:
    raise

class Die_Explosion(pygame.sprite.Sprite):
    
    def __init__(self, cx, cy):
        super(Die_Explosion, self).__init__()
        self.center = cx, cy
        self.image = None
        self.subrect = 0, 0, 50, 50
        self.master_image = pygame.image.load("images/stone.png").convert_alpha()
        self.animation_list = []
        for y in range(4):
            for x in range(5):
                self.animation_list.append((x*50, y*50, 50, 50))
        self.index = 0
        self.spawntime = pygame.time.get_ticks()
        
        self.zero = self.spawntime
        self.stay_interval = 300 # ms.

        self.ended = False
        
    def update(self, current_time):
        rect = self.animation_list[self.index]
        self.index += 1
        if self.index > len(self.animation_list) - 1:
            self.zero = self.zero or current_time
            self.index = 0
            if (current_time - self.zero) > self.stay_interval:
                self.ended = True
        
        self.image = self.master_image.subsurface(rect)
        self.rect = self.image.get_rect()
        self.rect.center = self.center
#End of 'Die_Explosion'