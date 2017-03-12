from gpiozero import LightSensor
from gpiozero.pins.pigpio import PiGPIOPin
from sense_hat import SenseHat

light = LightSensor(PiGPIOPin(4, host='192.168.1.4'))  # remote motion sensor
sense = SenseHat()  # local sense hat

blue = (0, 0, 255)
yellow = (255, 255, 0)

while True:
    if light.value > 0.5:
        sense.clear(yellow)
    else:
        sense.clear(blue)
