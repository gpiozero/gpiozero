import gpiozero
from gpiozero import TrafficHat
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

th_1 = TrafficHat()  # traffic hat using local pins
gpiozero.Device._set_pin_factory(PiGPIOFactory(host='192.168.1.3'))
th_2 = TrafficHat()  # traffic hat on 192.168.1.3 using remote pins
