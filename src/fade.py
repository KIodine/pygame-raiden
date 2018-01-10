import pygame
import config as cfg
import time

class Fade():
    def __init__(self, screen, caption=None ):
        self.msjh = "fonts/msjh.ttf"
        self.cap_font = pygame.font.Font(self.msjh, 120)
        self.sub_font = pygame.font.Font(self.msjh, 24)
        self.FPS = 60
        if caption == None:
            self.cap = "Pyden 2017"
        else:
            self.cap = caption
        self.sub = "Studio EVER proudly present"
        self.screen = screen
        screen_rect = screen.get_rect()

        self.cap_x, self.cap_y = screen_rect.center
        self.sub_x, self.sub_y = self.cap_x, self.cap_y + 100

        self.clock = pygame.time.Clock()
        #self.FPS = cfg.FPS
        self.BLACK = cfg.color.black

    def show_cap(self, text, x, y, trans,
        font=None):
        if ( font==None):
            font = self.cap_font
        if not isinstance(text, str):
            try:
                text = str(text)
            except:
                raise
        text = font.render(text, True, (trans, trans, trans))
        text_x, text_y = text.get_size()
    ##    print('text_xy', text_x, text_y)
        self.screen.blit(text, (x - text_x / 2, y - text_y / 2))
        print(trans)

        return

    def fade(self):

        play_caption = True

        stay_interval = 1.5

        init_trans = 0
        fade_in_speed = 9
        fade_out_speed = 15

        # DO NOT TOUCH, this is the sign for animation controlling.
        fade_in_phase = True
        fade_out_phase = False


        if play_caption:
            trans = init_trans
            while fade_in_phase:
                self.clock.tick(self.FPS)
                self.show_cap( # Use functools.partial to shorten.
                    self.cap,
                    self.cap_x,
                    self.cap_y,
                    trans=trans)
                self.show_cap(
                    self.sub,
                    self.sub_x,
                    self.sub_y,
                    trans=trans,
                    font=self.sub_font
                    )
                trans += fade_in_speed
                if trans >= 255:
                    trans = 255
                    fade_in_phase = False
                    fade_out_phase = True
                pygame.display.flip()
                    
            time.sleep(stay_interval) # Pause gameplay.

            while fade_out_phase:
                self.clock.tick(self.FPS)
                self.show_cap(
                    self.cap,
                    self.cap_x,
                    self.cap_y,
                    trans=trans)
                self.show_cap(
                    self.sub,
                    self.sub_x,
                    self.sub_y,
                    trans=trans,
                    font=self.sub_font
                    )
                trans -= fade_out_speed
                if trans <= 0:
                    trans = 0
                    fade_out_phase = False
                pygame.display.flip()
            self.screen.fill(self.BLACK)
            pygame.display.flip()
            time.sleep(0.7)
            
            print("CAP SHOWN")