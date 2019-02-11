from gpiozero import Motor, Servo, TonalBuzzer
from gpiozero.tools import sin_values
from signal import pause

motor = Motor(2, 3)
servo = Servo(4)
buzzer = TonalBuzzer(5)

motor.source = sin_values()
servo.source = sin_values()
buzzer.source = sin_values()

pause()
