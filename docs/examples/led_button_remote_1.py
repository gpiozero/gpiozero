from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOPin
from signal import pause

button = Button(2)
led = LED(PiGPIOPin(17, host='192.168.1.3'))

led.source = button.values

pause()
