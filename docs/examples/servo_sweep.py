from gpiozero import Servo
from gpiozero.tools import sin_values

servo = Servo(17)

servo.source = sin_values()
servo.source_delay = 0.1
