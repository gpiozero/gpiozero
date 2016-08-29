from gpiozero import LED
from signal import pause

red = LED(17)

red.blink()

pause()
