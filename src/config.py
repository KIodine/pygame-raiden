from collections import namedtuple

__doc__ = '''\
Game configurations.
Including common colors, window size, fonts and sound effects.\
'''

# Basic enviromental parameters.--------------------------------------

# Colors.
_colors = namedtuple(
    'Colors',
    [
        'black',
        'white',
        'red',
        'yellow',
        'green',
        'cyan',
        'blue',
        'purple'
        ]
    )

color = _colors(
    (0, 0, 0),
    (255, 255, 255),
    (255, 0, 0),
    (255, 255, 0),
    (0, 255, 0),
    (0, 255, 255),
    (0, 0, 255),
    (255, 0, 255)
    )

_gray_scale_floor = 150
_gray_scale_ceil = 215
gray_scale_range = [(i, i, i)
                    for i in range(_gray_scale_floor, _gray_scale_ceil + 1)
                    ]

_yellow_floor = 180
yellow_range = [(255, 255 - i, 0)
                for i in range(0, 256 - _yellow_floor)
                ]

rand_speed_floor = 5
rand_speed_ciel = 15

# Windows.
W_WIDTH = 1024
W_HEIGHT = 640
W_SIZE = (W_WIDTH, W_HEIGHT)
FPS = 30
default_bgcolor = (14, 52, 112)

# Texts.
title = "Interstellar simulator 2017"
font_msjh = 'fonts/msjh.ttf'

# Sounds.
play_bgm = True
firing_sound = 'music/beep1.ogg'
bgm = 'music/Diebuster OST- Escape Velocity.mp3'
volume_ratio = 0.25

# Game content.-------------------------------------------------------

_size = namedtuple('Size', ['S', 'M', 'L'])

meteor_counts = 512

pill_counts = 15
pill_lifetime = 10 # Seconds.
