from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOPin
from gpiozero.tools import all_values
from signal import pause

led = LED(17)
button_1 = Button(PiGPIOPin(17, host='192.168.1.3'))
button_2 = Button(PiGPIOPin(17, host='192.168.1.4'))

led.source = all_values(button_1.values, button_2.values)

pause()
