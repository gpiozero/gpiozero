from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOPin
from time import sleep

led_1 = LED(17)  # local pin
led_2 = LED(PiGPIOPin(17, host='192.168.1.3'))  # remote pin on one pi
led_3 = LED(PiGPIOPin(17, host='192.168.1.4'))  # remote pin on another pi

while True:
    led_1.on()
    led_2.off()
    led_3.on()
    sleep(1)
    led_1.off()
    led_2.on()
    led_3.off()
    sleep(1)
