try:
    import pygame
    import random
    import math
    import bullet as blt
except:
    raise

class Hitbox(pygame.sprite.Sprite):

    def __init__(self,
                 screct,
                 rdyellow,
                 *,
                 x=None,
                 y=None,
                 w=None,
                 h=None,
                 color=None,
                 image=None,
                 enemy=False,
                 ratio=1,
                 frames=1,
                 ):
        super(Hitbox, self).__init__()
        self.isenemy = enemy
        self.ratio = ratio
        color = color or (0, 255, 0)
        if ( image == None ):
            w = w or 70
            h = h or 100
            
            self.image = pygame.Surface((w, h))
            self.image.fill(color)
            
        else:
            self.animation_list = []
            self.wholepic = image
            for i in range( int(image.get_rect().width/w) ):
                print( "i=" + str(i) + "w=" + str(w) + "h=" + str(h) )
                self.animation_list.append((i*w, 0, w, h))
            self.index = 0
            self.picrect = self.animation_list[self.index]
            self.image = self.wholepic.subsurface(self.picrect)
        
        self.image = pygame.transform.rotozoom( self.image, 0, ratio )
        self.rect = self.image.get_rect()
        
        self.rdyellow = rdyellow
        self.screct = screct
        
        self.rect.centery = y or self.screct.centery # Initial place aligned with screen.
        self.rect.centerx = x or self.screct.centerx
        
        self._dest_x = self.rect.centerx
        self._dest_y = self.rect.centery
        
        
        self._float_x = self.rect.centerx
        self._float_y = self.rect.centery

        self.move_v_rate = 15
        self.move_h_rate = 15

        self.move_dir = random.choice((1, -1)) # regulating move of sprite

        self.bullet_shift = 25

        self.fire_rate = 70 # ms
        self.last_fire = pygame.time.get_ticks()

##        self.fire_sfx = shooting_sfx
##        self.fire_sfx.set_volume(volume_ratio)

        self._last_setdest = pygame.time.get_ticks()

    def move(self, v):
        if v == 'W' and self.rect.top > self.screct.top:
            self.rect.move_ip(0, -self.move_v_rate)
        if v == 'S' and self.rect.bottom < self.screct.bottom:
            self.rect.move_ip(0, self.move_v_rate)
        if v == 'A' and self.rect.left > self.screct.left:
            self.rect.move_ip(-self.move_h_rate, 0)
        if v == 'D' and self.rect.right < self.screct.right:
            self.rect.move_ip(self.move_h_rate, 0)

    def _set_dest(self, x, y):
        self._dest_x = int(x)
        self._dest_y = int(y)
        return None

    def _nlmove(self):
        if self.rect.centerx != self._dest_x:
            delta_x = 0.1 * math.ceil(self._dest_x - self.rect.centerx)
            self.rect.centerx += int(delta_x)
##            print(delta_x)
        if self.rect.centery != self._dest_y:
            delta_y = 0.1 * math.ceil(self._dest_y - self.rect.centery)
            self.rect.centery += int(delta_y)
##            print(delta_y)

    def create_bullet(self, group):
        fire_now = pygame.time.get_ticks()
        elapsed_fire = fire_now - self.last_fire
        if not (elapsed_fire > self.fire_rate):
            # Fire rate limit.
            return None
        else:
            self.last_fire = fire_now
        
##        self.fire_sfx.stop()
        ctx = self.rect.centerx
        top = self.rect.top
        shift = self.bullet_shift
        bullet_obj = blt.Bullet(ctx, top - shift, self.rdyellow, self.isenemy)
        if self.isenemy is True:
            # Add random shift for bullet?
            bullet_obj = blt.Bullet(
                ctx, self.rect.bottom + shift, self.rdyellow, self.isenemy, direct='DOWN', size='L')
        group.add(bullet_obj)
##        self.fire_sfx.play()
        return None

    def update(self):
        if self.isenemy:
            self.index += 1
            if self.index > len(self.animation_list) - 1:
                self.index = 0
            self.picrect = self.animation_list[self.index]
            self.image = pygame.transform.rotozoom( self.wholepic.subsurface(self.picrect), 0, self.ratio )
            self._nlmove()
            elapsed_setdest = pygame.time.get_ticks() - self._last_setdest
            if elapsed_setdest > 2 * 1000:
                self._set_dest(
                    random.randint(
                        0 + self.rect.width, self.screct.right - self.rect.width
                        ),
                    random.randint(30, 90)
                    )
                print(self._dest_x, self._dest_y)
                self._last_setdest = pygame.time.get_ticks()
        
        if self.rect.left < self.screct.left or self.rect.right > self.screct.right:
            self.move_dir *= -1
        if self.move_dir > 0:
            self.rect.move_ip(self.move_h_rate, 0)
        if self.move_dir < 0:
            self.rect.move_ip(-self.move_h_rate, 0)
# End of 'Hitbox'.