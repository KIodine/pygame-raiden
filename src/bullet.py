try:
    import pygame
    import config as cfg
except:
    raise
    
class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, rdyellow, isenemy, *, direct='UP', size='S'):
        super(Bullet, self).__init__()
        self.direct = direct
        bullet_size = {'S': (2, 16),
                       'M': (3, 20),
                       'L': (5, 26)}
        size = bullet_size[size]
        self.image = pygame.Surface(size)
        self.image.fill(rdyellow())
        self.rect = self.image.get_rect()

        self.rect.center = (x, y)

        self.projectspd = 20
        if isenemy:
            sound_file = cfg.enemy_firing_sound
        else:
            sound_file = cfg.firing_sound
        volume_ratio = cfg.volume_ratio
        shooting_sfx = pygame.mixer.Sound(sound_file)
        shooting_sfx.set_volume(volume_ratio)
        shooting_sfx.play()

    def update(self):
        if self.direct == 'UP':
            self.rect.centery -= self.projectspd
        if self.direct == 'DOWN':
            self.rect.centery += self.projectspd
# End of 'Bullet'.