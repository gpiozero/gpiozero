from gpiozero import PWMLED
from signal import pause

led = PWMLED(17)

led.pulse()

pause()
