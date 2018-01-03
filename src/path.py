import math
import pygame
from pygame.math import Vector2
import logging

class path():
    
    def __init__(self,
            now=None, #目前座標
            final=None, #目標座標
            centre=None, #圓心 
            #以上三項參數均為 ( x,y )
            omega=None, #角速度為正是順時鐘，負為逆時鐘
            sprite123=None
        ):
        self.enabled = False
        return
        '''
        self.nowVec = Vector2(now - centre)
        self.finalVec = Vector2( final - centre)
        self.omega = omega
        self.sp123 = sprite123
        self.enable = True
        '''
        

    def NextCoor( self ):
        #if ( )
        tempVec = [int(x) for x in self.nowVec]
        if self.nowAngle >= self.finalAngle:
            self.enabled = False
            self.sp123.is_at_dest = True
            print("hi")
            return False
        print(tempVec, self.finalVec)
        self.nowVec.rotate_ip(self.omega)
        self.nowAngle += abs(self.omega)
        # Update the position vector and the rect.
        self.sp123.rect.center = self.centre+self.nowVec
        return True

    def ReDirect( self, now, final, centre, omega, sp123 ):
        self.nowVec = Vector2(now - centre)
        self.finalVec = Vector2( final - centre)
        self.centre = centre
        self.omega = omega
        self.sp123 = sp123
        self.enabled = True
        self.finalAngle = abs(self.finalVec.as_polar()[1] - self.nowVec.as_polar()[1])
        self.nowAngle = 0

        return