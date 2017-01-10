from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOPin
from time import sleep

led = LED(PiGPIOPin(17, host='192.168.1.3'))

while True:
    led.on()
    sleep(1)
    led.off()
    sleep(1)
