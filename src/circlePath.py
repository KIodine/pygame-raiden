import math
import pygame
from pygame.math import Vector2

class CirclePath():
    
    def __init__(self,
            now, 
            final,
            centre, #這三項參數均為Points ( x,y )
            #self.clockwise = 0#0為順時針,1為逆時針,若未給值預設為0
            angle_speed,
            sprite123
        ):
        
        self.nowVec = Vector2(now - centre)
        self.finalVec = Vector2( final - centre)
        self.angle_speed = angle_speed
        self.sp123 = sprite123

    def NextCoor( self,now ):
        #if ( )
        self.sp123.direction.rotate_ip(self.sp123.angle_speed)
        self.sp123.angle += self.sp123.angle_speed
        self.sp123.image = pygame.transform.rotate(self.sp123.original_image, -self.sp123.angle)
        self.sp123.rect = self.sp123.image.get_rect(midtop=self.sp123.rect.midtop)
        # Update the position vector and the rect.
        self.sp123.position += self.sp123.direction * self.sp123.speed
        self.sp123.rect.center = self.sp123.position

