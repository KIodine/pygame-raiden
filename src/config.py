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

rdgray = lambda: random.choice(gray_scale_range)
rdspeed = lambda: rand_speed_floor + rand_speed_ciel * random.random()
shftspeed = lambda: random.choice([1, -1]) * (3 * random.random())
rdsize = lambda: random.choices(
    [(1, i*5) for i in range(1, 3+1)], [70, 30, 10], k=1
    )
rdyellow = lambda: random.choice(yellow_range)

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
firing_sound = "music/match0.wav"
enemy_firing_sound = "music/badswap.wav"

bgm = "music/tetrisb.mid"
dead_bgm = "music/Trap-music.mp3"

volume_ratio = 0.25

# Game content.-------------------------------------------------------

_size = namedtuple('Size', ['S', 'M', 'L'])

meteor_counts = 512

pill_counts = 15
pill_lifetime = 10 # Seconds.
