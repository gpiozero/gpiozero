from gpiozero import LED
from signal import pause

led = LED(17)
led.source = [1, 0, 1, 1, 1, 0, 0, 1, 0, 1]

pause()
