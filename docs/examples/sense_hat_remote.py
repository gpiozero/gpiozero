from gpiozero import MotionSensor
from gpiozero.pins.pigpio import PiGPIOFactory
from sense_hat import SenseHat

remote_factory = PiGPIOFactory(host='192.198.1.4')
pir = MotionSensor(4, pin_factory=remote_factory)  # remote motion sensor
sense = SenseHat()  # local sense hat

while True:
    pir.wait_for_motion()
    sense.show_message(sense.temperature)
