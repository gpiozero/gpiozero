from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOPin
from time import sleep

led_1 = LED(PiGPIOPin(17, host='192.168.1.3'))
led_2 = LED(PiGPIOPin(17, host='192.168.1.4'))

while True:
    led_1.on()
    led_2.off()
    sleep(1)
    led_1.off()
    led_2.on()
    sleep(1)
