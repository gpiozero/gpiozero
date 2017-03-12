from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOPin
from signal import pause

led = LED(PiGPIOPin(17, host='raspberrypi.local'))

led.blink()

pause()
