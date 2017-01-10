from gpiozero import LED
from gpiozero.pins.rpigpio import RPiGPIOPin
from time import sleep

led_1 = LED(RPiGPIOPin(17))  # local pin
led_2 = LED(17)  # remote pin

while True:
    led_1.on()
    led_2.off()
    sleep(1)
    led_1.off()
    led_2.on()
    sleep(1)
