from itertools import cycle
from collections import deque
from gpiozero import LEDMultiCharDisplay
from signal import pause

display = LEDMultiCharDisplay(
    LEDCharDisplay(22, 23, 24, 25, 21, 20, 16, dp=12), 26, 19, 13, 6)

def scroller(message, chars=4):
    d = deque(maxlen=chars)
    for c in cycle(message):
        d.append(c)
        if len(d) == chars:
            yield ''.join(d)

display.source_delay = 0.2
display.source = scroller('GPIO 2ER0    ')
pause()
