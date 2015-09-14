from RPi import GPIO


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class InputDevice(object):
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(pin, GPIO.IN, GPIO.PUD_UP)

    def is_pressed(self):
        return GPIO.input(self.pin) == 0


class Button(InputDevice):
    pass
