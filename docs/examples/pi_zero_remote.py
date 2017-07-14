from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory
from signal import pause

factory = PiGPIOFactory(host='raspberrypi.local')
led = LED(17, pin_factory=factory)

led.blink()

pause()
