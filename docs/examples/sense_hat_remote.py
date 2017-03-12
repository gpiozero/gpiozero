from gpiozero import MotionSensor
from gpiozero.pins.pigpio import PiGPIOPin
from sense_hat import SenseHat

pir = MotionSensor(PiGPIOPin(4, host='192.168.1.4'))  # remote motion sensor
sense = SenseHat()  # local sense hat

while True:
    pir.wait_for_motion()
    sense.show_message(sense.temperature)
