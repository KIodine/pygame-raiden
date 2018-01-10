import pygame
import config as cfg
import time

def Fade( screen, FPS, BLACK , cap=None):
    msjh = 'fonts/msjh.ttf'
    cap_font = pygame.font.Font(msjh, 120)
    sub_font = pygame.font.Font(msjh, 24)
    if cap==None:
        cap = "Pyden 2017"
    sub = "Studio EVER proudly present"

    screen_rect = screen.get_rect()

    cap_x, cap_y = screen_rect.center
    sub_x, sub_y = cap_x, cap_y + 100

    clock = pygame.time.Clock()

    def show_cap(text, x, y, trans, font=cap_font):
        if not isinstance(text, str):
            try:
                text = str(text)
            except:
                raise
        text = font.render(text, True, (trans, trans, trans))
        text_x, text_y = text.get_size()
    ##    print('text_xy', text_x, text_y)
        screen.blit(text, (x - text_x / 2, y - text_y / 2))
        print(trans)

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
            clock.tick(FPS)
            show_cap( # Use functools.partial to shorten.
                cap,
                cap_x,
                cap_y,
                trans=trans)
            show_cap(
                sub,
                sub_x,
                sub_y,
                trans=trans,
                font=sub_font
                )
            trans += fade_in_speed
            if trans >= 255:
                trans = 255
                fade_in_phase = False
                fade_out_phase = True
            pygame.display.flip()
                
        time.sleep(stay_interval) # Pause gameplay.

        while fade_out_phase:
            clock.tick(FPS)
            show_cap(
                cap,
                cap_x,
                cap_y,
                trans=trans)
            show_cap(
                sub,
                sub_x,
                sub_y,
                trans=trans,
                font=sub_font
                )
            trans -= fade_out_speed
            if trans <= 0:
                trans = 0
                fade_out_phase = False
            pygame.display.flip()
        screen.fill(BLACK)
        pygame.display.flip()
        time.sleep(0.7)
        
        print("CAP SHOWN")